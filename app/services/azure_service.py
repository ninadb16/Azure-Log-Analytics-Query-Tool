# app/services/azure_service.py (UPDATED API VERSIONS and URLs)

import logging
import requests
from typing import Dict, List, Any
import urllib.parse
from app.config import (
    AppConfig, 
    AZURE_ARM_RESOURCE_AUTH, # <-- NEW AUTH RESOURCE
    AZURE_ARM_BASE_URL, 
    ARM_SUBSCRIPTION_API_VERSION,
    ARM_WORKSPACE_API_VERSION,
    AZURE_LOG_ANALYTICS_RESOURCE, 
    AZURE_LOG_ANALYTICS_AUTH_RESOURCE 
)
from app.auth.token_cache import AzureTokenCache

log = logging.getLogger(__name__)

class AzureService:
    def __init__(self, config: AppConfig, token_cache: AzureTokenCache):
        self.config = config
        self.token_cache = token_cache
        self.ARM_RESOURCE_AUTH = AZURE_ARM_RESOURCE_AUTH 
        self.ARM_BASE_URL = AZURE_ARM_BASE_URL     
        self.LA_RESOURCE = AZURE_LOG_ANALYTICS_RESOURCE
        self.LA_AUTH_RESOURCE = AZURE_LOG_ANALYTICS_AUTH_RESOURCE 

    def _get_auth_headers(self, resource_url: str) -> Dict[str, str]:
        """Gets the access token for the specified resource (AUTH URI) and formats it for HTTP headers."""
        token = self.token_cache.get_token(resource_url)
        return {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _fetch_all_subscription_ids(self) -> List[str]:
        """
        Fetches all accessible subscription IDs using the Azure Resource Manager API.
        """
        log.info("Starting discovery of all accessible subscription IDs.")
        
        # AUTH CALL: Use the ARM AUTH Resource Identifier
        arm_headers = self._get_auth_headers(self.ARM_RESOURCE_AUTH) 
        
        # API CALL: Use the ARM Base URL and user-specified API version
        # URL construction: https://management.azure.com/subscriptions?...
        subs_url = f"{self.ARM_BASE_URL}/subscriptions?api-version={ARM_SUBSCRIPTION_API_VERSION}" 
        subscription_ids = []

        try:
            response = requests.get(subs_url, headers=arm_headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for sub in data.get('value', []):
                subscription_ids.append(sub['subscriptionId'])
                
            log.info(f"Found {len(subscription_ids)} accessible subscriptions.")
            return subscription_ids

        except requests.exceptions.RequestException as e:
            log.error(f"Error fetching subscription IDs: {e}", exc_info=True)
            raise RuntimeError(f"Failed to fetch subscription IDs: {e}")

    
    def discover_all_workspaces(self) -> List[Dict[str, str]]:
        """
        Iterates through all subscription IDs to find all Log Analytics Workspaces 
        and fetches their name, resource group, subscription, and Customer ID.
        """
        subscription_ids = self._fetch_all_subscription_ids()
        
        # AUTH CALL: Use the ARM AUTH Resource Identifier for token
        arm_headers = self._get_auth_headers(self.ARM_RESOURCE_AUTH)
        
        workspaces_list = []
        arm_base = self.ARM_BASE_URL 
        
        log.info("Starting iterative Log Analytics Workspace discovery per subscription.")

        for sub_id in subscription_ids:
            # API CALL: Use the ARM Base URL and user-specified API version
            list_workspaces_url = (
                f"{arm_base}/subscriptions/{sub_id}/"
                f"providers/Microsoft.OperationalInsights/workspaces?api-version={ARM_WORKSPACE_API_VERSION}"
            )
            
            log.info(f"Fetching workspaces in subscription: {sub_id}")
            
            try:
                response = requests.get(list_workspaces_url, headers=arm_headers, timeout=20)
                response.raise_for_status()
                data = response.json()
                
                for workspace in data.get('value', []):
                    ws_id = workspace.get('id')
                    ws_name = workspace.get('name')
                    customer_id = workspace.get('properties', {}).get('customerId')
                    
                    if ws_id and ws_name and customer_id:
                        try:
                            rg_name = ws_id.split('/resourceGroups/')[1].split('/')[0]
                        except IndexError:
                            rg_name = "N/A (Error Parsing ID)"
                            
                        workspaces_list.append({
                            "name": ws_name,
                            "resource_group": rg_name,
                            "subscription_id": sub_id,
                            "workspace_id": customer_id
                        })
                        
                log.info(f"Found {len(data.get('value', []))} workspaces in {sub_id}")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    log.warning(f"Permission denied (403) to list workspaces in subscription {sub_id}. Skipping.")
                else:
                    log.error(f"Failed to list workspaces for subscription {sub_id}: {e}", exc_info=False)
            except Exception as e:
                log.error(f"Unexpected error while processing subscription {sub_id}: {e}", exc_info=True)
                
        if not workspaces_list:
            log.warning("No Log Analytics Workspaces found across all accessible subscriptions.")
        else:
            log.info(f"Successfully discovered {len(workspaces_list)} total workspaces.")
            
        return workspaces_list


    def run_query(self, workspace_id: str, query: str, start: str, end: str) -> Dict[str, Any]:
        """Runs a Kusto query against the specified Log Analytics workspace."""
        log.info(f"Running query on workspace {workspace_id}")
        
        # AUTH CALL: Use the correct LA AUTH RESOURCE
        la_headers = self._get_auth_headers(self.LA_AUTH_RESOURCE)
        
        query_url = f"{self.LA_RESOURCE}v1/workspaces/{workspace_id}/query"
        
        query_body = {
            "query": query,
            "timespan": f"{start}/{end}" 
        }

        try:
            response = requests.post(query_url, headers=la_headers, json=query_body, timeout=60)
            response.raise_for_status()
            results = response.json()
            
            if not results.get('tables'):
                return {'results': [], 'columns': []}

            table = results['tables'][0]
            columns = [col['name'] for col in table['columns']]
            
            rows = []
            for row_values in table.get('rows', []):
                rows.append(dict(zip(columns, row_values)))
            
            return {
                'results': rows, 
                'columns': columns
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                log.error(f"Log Analytics Query Error (400): {e.response.text}")
                error_detail = e.response.json().get('error', {}).get('message', 'Bad query or request.')
                raise ValueError(f"Query Failed (KQL/Syntax): {error_detail}")
            log.error(f"Log Analytics API HTTP Error: {e}", exc_info=True)
            raise RuntimeError(f"Log Analytics API failed: {e}")
        except Exception as e:
            log.error(f"Unexpected error during query: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred during query execution: {e}")

# app/config.py (REVISED to assign all needed attributes)

from typing import Dict, Any
from query import QUERY_TEMPLATES
# --- Module-Level Constants (Used for definition, but accessed via instance) ---
AZURE_ARM_RESOURCE_AUTH = "https://management.azure.com/" 
AZURE_ARM_BASE_URL = "https://management.azure.com" 
ARM_SUBSCRIPTION_API_VERSION = "2022-12-01"
ARM_WORKSPACE_API_VERSION = "2022-10-01"
AZURE_LOG_ANALYTICS_RESOURCE = "https://api.loganalytics.azure.com/"
AZURE_LOG_ANALYTICS_AUTH_RESOURCE = "https://api.loganalytics.io"


class AppConfig:
    def __init__(self):
        # ⚠️ FIX: Assign ALL required module-level constants as instance attributes
        self.AZURE_ARM_RESOURCE_AUTH = AZURE_ARM_RESOURCE_AUTH
        self.AZURE_ARM_BASE_URL = AZURE_ARM_BASE_URL
        self.ARM_SUBSCRIPTION_API_VERSION = ARM_SUBSCRIPTION_API_VERSION
        self.ARM_WORKSPACE_API_VERSION = ARM_WORKSPACE_API_VERSION
        self.AZURE_LOG_ANALYTICS_RESOURCE = AZURE_LOG_ANALYTICS_RESOURCE
        self.AZURE_LOG_ANALYTICS_AUTH_RESOURCE = AZURE_LOG_ANALYTICS_AUTH_RESOURCE
        
        # Predefined KQL Queries
        self.PREDEFINED_QUERIES: Dict[str, str] = QUERY_TEMPLATES
        #{
#            "query_1_errors_last_day": "AzureActivity | where Level == 'Error' | limit 100",
#            "query_2_heartbeats_summary": "Heartbeat | summarize LastHeartbeat = max(TimeGenerated) by Computer, ResourceId, _ResourceId | order by LastHeartbeat desc | limit 50",
#            "query_3_all_security_events": "SecurityEvent | where EventID == 4624 or EventID == 4625 | limit 50",
#            "AppRequests": "AppRequests| take 10"
 #               list(QUERYTEMPLATES.keys())
 #       }
        
        # Scopes (already instance attributes)
        self.ARM_SCOPE = f"{self.AZURE_ARM_RESOURCE_AUTH}.default" 
        self.LA_SCOPE = f"{self.AZURE_LOG_ANALYTICS_AUTH_RESOURCE}/.default" 

# --- Load Function ---
def load_config() -> AppConfig:
    """Instantiates and returns the application configuration."""
    return AppConfig()

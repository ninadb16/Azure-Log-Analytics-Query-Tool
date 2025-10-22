import logging
from typing import Dict
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta
from app.config import AppConfig
# No need to import module-level constants, AppConfig handles it.

log = logging.getLogger(__name__)

class AzureTokenCache:
    def __init__(self, config: AppConfig):
        self.config = config
        self.credential = DefaultAzureCredential()
        self.cache: Dict[str, AccessToken] = {}
        
        # ⚠️ FIX: Access the new instance attributes from the config object
        self.resource_to_scope = {
            # Map AUTH Resource Identifier to its corresponding full SCOPE
            config.AZURE_ARM_RESOURCE_AUTH: config.ARM_SCOPE, 
            config.AZURE_LOG_ANALYTICS_AUTH_RESOURCE: config.LA_SCOPE
        }

    def get_token(self, resource_url: str) -> AccessToken:
        # ... (rest of the method logic is now correct)
        
        scope = self.resource_to_scope.get(resource_url)
        if not scope:
            raise ValueError(f"Unknown resource identifier provided: {resource_url}")
        
        # Check cache validity
        cached_token = self.cache.get(scope)
        if cached_token and cached_token.expires_on > int((datetime.now() + timedelta(minutes=5)).timestamp()):
            log.info(f"Using cached token for scope: {scope}")
            return cached_token

        # Acquire new token
        log.info(f"Acquiring new token for scope: {scope}")
        try:
            # We pass the full scope (list of scopes) to DefaultAzureCredential
            token = self.credential.get_token(scope)
            self.cache[scope] = token
            log.info(f"Token acquired. Expires on: {datetime.fromtimestamp(token.expires_on)}")
            return token
        except Exception as e:
            log.error(f"Failed to acquire Azure AD token for scope {scope}: {e}", exc_info=True)
            raise RuntimeError(f"Authentication failed: {e}")

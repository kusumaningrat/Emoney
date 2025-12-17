from pydantic_settings import BaseSettings
from typing import Optional, List, Union, Any, Dict
import secrets
from functools import lru_cache
from enum import Enum


class Environment(str, Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Service Orchestrator"
    API_VERSION: str = "v1"
    DEBUG: bool = True
    
    # Environment
    ENVIRONMENT: Environment = Environment.DEV
    
    # Security
    API_KEY: Optional[str] = None
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # CORS - Accept string and convert it internally
    ALLOWED_ORIGINS: str = "*"
    
    # Service settings
    DEFAULT_SERVICE_TIMEOUT: float = 5.0  # seconds
    SCAN_RESULT_RETENTION_DAYS: int = 30  # Keep scan results for 30 days
    
    # Service URLs with environment variable overrides
    # Client Service
    CLIENT_URL_DEV: str = "http://client-service:4642"
    CLIENT_URL_STAGE: str = "https://client.stage.wealthbox-integration.example.com"
    CLIENT_URL_PROD: str = "https://client.wealthbox-integration.example.com"
    
    # Opportunity Service
    OPPORTUNITY_URL_DEV: str = "http://opportunity-service:4644"
    OPPORTUNITY_URL_STAGE: str = "https://opportunity.stage.wealthbox-integration.example.com"
    OPPORTUNITY_URL_PROD: str = "https://opportunity.wealthbox-integration.example.com"
    
    # Identity Service
    IDENTITY_URL_DEV: str = "http://identity-service:4641"
    IDENTITY_URL_STAGE: str = "https://identity.stage.wealthbox-integration.example.com"
    IDENTITY_URL_PROD: str = "https://identity.wealthbox-integration.example.com"
    
    # Activity Service
    ACTIVITY_URL_DEV: str = "http://activity-service:4643"
    ACTIVITY_URL_STAGE: str = "https://activity.stage.wealthbox-integration.example.com"
    ACTIVITY_URL_PROD: str = "https://activity.wealthbox-integration.example.com"
    
    # Auth Service
    AUTH_URL_DEV: str = "http://auth-service:4645"
    AUTH_URL_STAGE: str = "https://auth.stage.wealthbox-integration.example.com"
    AUTH_URL_PROD: str = "https://auth.wealthbox-integration.example.com"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def cors_origins(self) -> List[str]:
        """
        Parse ALLOWED_ORIGINS to get a list of allowed origins.
        
        Returns:
            List[str]: List of allowed origins
        """
        # If it's just "*", return that as a list
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
            
        # Otherwise, split by comma
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def service_urls(self) -> Dict[str, str]:
        """
        Get the service URLs for the current environment.
        
        Returns:
            Dict[str, str]: Dictionary mapping service keys to URLs
        """
        env_suffix = self.ENVIRONMENT.value.upper()
        
        return {
            "client": getattr(self, f"CLIENT_URL_{env_suffix}"),
            "opportunity": getattr(self, f"OPPORTUNITY_URL_{env_suffix}"),
            "identity": getattr(self, f"IDENTITY_URL_{env_suffix}"),
            "activity": getattr(self, f"ACTIVITY_URL_{env_suffix}"),
            "auth": getattr(self, f"AUTH_URL_{env_suffix}")
        }
    
    def get_service_url(self, service_key: str) -> Optional[str]:
        """
        Get URL for a specific service in the current environment.
        
        Args:
            service_key (str): Service key (client, opportunity, identity, activity, auth)
            
        Returns:
            str: Service URL or None if not found
        """
        return self.service_urls.get(service_key)
    
    def get_scan_endpoint(self, service_key: str) -> Optional[str]:
        """
        Get the scan API endpoint for a service.
        
        Args:
            service_key (str): Service key
            
        Returns:
            str: Scan API endpoint URL
        """
        service_url = self.get_service_url(service_key)
        if not service_url:
            return None
        
        return f"{service_url}/api/{self.API_VERSION}/scan/start"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching for efficiency.
    
    Returns:
        Settings: Application settings
    """
    return Settings()
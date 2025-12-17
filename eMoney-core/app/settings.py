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
    APP_NAME: str = "EMoney Service Orchestrator"
    API_VERSION: str = "v1"
    DEBUG: bool = True
    
    # Environment
    ENVIRONMENT: Environment = Environment.DEV
    
    # Security
    API_KEY: Optional[str] = None
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./emoney.db"
    
    # CORS - Accept string and convert it internally
    ALLOWED_ORIGINS: str = "*"
    
    # Service settings - Enhanced for EMoney
    DEFAULT_SERVICE_TIMEOUT: float = 30.0  # Increased for EMoney APIs
    SCAN_RESULT_RETENTION_DAYS: int = 30  # Keep scan results for 30 days
    MAX_RETRY_ATTEMPTS: int = 3  # EMoney API retry attempts
    RATE_LIMIT_RETRY_AFTER: int = 60  # Rate limit retry delay
    
    # EMoney Service URLs with environment variable overrides
    # Account Service
    EMONEY_ACCOUNT_URL_DEV: str = "http://emoney-account-service:4650"
    EMONEY_ACCOUNT_URL_STAGE: str = "https://account.stage.emoney-integration.example.com"
    EMONEY_ACCOUNT_URL_PROD: str = "https://account.emoney-integration.example.com"
    
    # Client Service
    EMONEY_CLIENT_URL_DEV: str = "http://emoney-client-service:4651"
    EMONEY_CLIENT_URL_STAGE: str = "https://client.stage.emoney-integration.example.com"
    EMONEY_CLIENT_URL_PROD: str = "https://client.emoney-integration.example.com"
    
    # Financial Planning Service
    EMONEY_FINANCIAL_PLANNING_URL_DEV: str = "http://emoney-planning-service:4652"
    EMONEY_FINANCIAL_PLANNING_URL_STAGE: str = "https://planning.stage.emoney-integration.example.com"
    EMONEY_FINANCIAL_PLANNING_URL_PROD: str = "https://planning.emoney-integration.example.com"
    
    # Identity Service
    EMONEY_IDENTITY_URL_DEV: str = "http://emoney-identity-service:4653"
    EMONEY_IDENTITY_URL_STAGE: str = "https://identity.stage.emoney-integration.example.com"
    EMONEY_IDENTITY_URL_PROD: str = "https://identity.emoney-integration.example.com"
    
    # EMoney Authentication Settings
    EMONEY_DEFAULT_API_KEY: str = "emoney-api-key-67890"
    EMONEY_DEFAULT_CLIENT_ID: str = "emoney-client-id-12345"
    EMONEY_DEFAULT_FIRM_ID: str = "firm-12345"
    EMONEY_DEFAULT_SCOPE: str = "API"
    EMONEY_JWT_EXPIRY_HOURS: int = 24  # JWT token expiry
    
    # EMoney Batch Processing Settings
    EMONEY_DEFAULT_BATCH_SIZE: int = 100
    EMONEY_MAX_BATCH_SIZE: int = 1000
    EMONEY_PAGINATION_LIMIT: int = 100
    
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
        Get the EMoney service URLs for the current environment.
        
        Returns:
            Dict[str, str]: Dictionary mapping service keys to URLs
        """
        env_suffix = self.ENVIRONMENT.value.upper()
        
        return {
            "account": getattr(self, f"EMONEY_ACCOUNT_URL_{env_suffix}"),
            "client": getattr(self, f"EMONEY_CLIENT_URL_{env_suffix}"),
            "financial_planning": getattr(self, f"EMONEY_FINANCIAL_PLANNING_URL_{env_suffix}"),
            "identity": getattr(self, f"EMONEY_IDENTITY_URL_{env_suffix}")
        }
    
    def get_service_url(self, service_key: str) -> Optional[str]:
        """
        Get URL for a specific EMoney service in the current environment.
        
        Args:
            service_key (str): Service key (account, client, financial_planning, identity)
            
        Returns:
            str: Service URL or None if not found
        """
        return self.service_urls.get(service_key)
    
    def get_scan_endpoint(self, service_key: str) -> Optional[str]:
        """
        Get the scan API endpoint for an EMoney service.
        
        Args:
            service_key (str): Service key
            
        Returns:
            str: Scan API endpoint URL
        """
        service_url = self.get_service_url(service_key)
        if not service_url:
            return None
        
        return f"{service_url}/api/{self.API_VERSION}/scan/start"
    
    @property
    def emoney_auth_config(self) -> Dict[str, str]:
        """
        Get default EMoney authentication configuration.
        
        Returns:
            Dict[str, str]: Default auth config
        """
        return {
            "api_key": self.EMONEY_DEFAULT_API_KEY,
            "client_id": self.EMONEY_DEFAULT_CLIENT_ID,
            "firm_id": self.EMONEY_DEFAULT_FIRM_ID,
            "scope": self.EMONEY_DEFAULT_SCOPE
        }
    
    def get_emoney_auth_config(self, jwt_token: Optional[str] = None) -> Dict[str, str]:
        """
        Get EMoney authentication configuration with optional JWT token.
        
        Args:
            jwt_token (str, optional): JWT token to include
            
        Returns:
            Dict[str, str]: Auth config with JWT token if provided
        """
        config = self.emoney_auth_config.copy()
        if jwt_token:
            config["jwt_token"] = jwt_token
        return config
    
    @property 
    def emoney_filter_defaults(self) -> Dict[str, Any]:
        """
        Get default EMoney filter configuration.
        
        Returns:
            Dict[str, Any]: Default filter config
        """
        return {
            "dateRange": {
                "startDate": "2025-01-01",
                "endDate": "2025-12-31"
            },
            "batchSize": self.EMONEY_DEFAULT_BATCH_SIZE,
            "includeInactive": False
        }
    
    def get_service_config(self, service_key: str) -> Dict[str, Any]:
        """
        Get complete configuration for a specific EMoney service.
        
        Args:
            service_key (str): Service key
            
        Returns:
            Dict[str, Any]: Service configuration
        """
        return {
            "service_key": service_key,
            "url": self.get_service_url(service_key),
            "scan_endpoint": self.get_scan_endpoint(service_key),
            "timeout": self.DEFAULT_SERVICE_TIMEOUT,
            "max_retries": self.MAX_RETRY_ATTEMPTS,
            "auth_config": self.emoney_auth_config,
            "filter_defaults": self.emoney_filter_defaults
        }
    
    def get_all_service_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration for all EMoney services.
        
        Returns:
            Dict[str, Dict[str, Any]]: All service configurations
        """
        services = ["account", "client", "financial_planning", "identity"]
        return {
            service_key: self.get_service_config(service_key)
            for service_key in services
        }
    
    def validate_service_key(self, service_key: str) -> bool:
        """
        Validate if a service key is supported.
        
        Args:
            service_key (str): Service key to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return service_key in ["account", "client", "financial_planning", "identity"]
    
    @property
    def supported_service_keys(self) -> List[str]:
        """
        Get list of supported EMoney service keys.
        
        Returns:
            List[str]: Supported service keys
        """
        return ["account", "client", "financial_planning", "identity"]


@lru_cache()
def get_settings() -> Settings:
    """
    Get EMoney application settings with caching for efficiency.
    
    Returns:
        Settings: EMoney application settings
    """
    return Settings()
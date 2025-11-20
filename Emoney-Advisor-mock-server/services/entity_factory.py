# services/entity_factory.py - Entity Service Factory

from sqlalchemy.orm import Session
from typing import Union, Any

# Import all service classes
from services.identity import (
    UserService, OfficeService, RoleService, PermissionService, 
    SharingRuleService, LogonService
)
from services.client import (
    ClientService, HouseholdService, SpouseService, 
    ContactService, RelationshipService
)
from services.financial import (
    FinancialPlanService, GoalService, ScenarioService, 
    CashFlowService, NetWorthService
)
from services.account import AccountService, AccountTypeService
from services.asset import AssetService, AssetClassService, LiabilityService


class EntityServiceFactory:
    """
    Factory class for creating service instances based on entity type.
    
    This factory provides a centralized way to get the appropriate service
    instance for different entity types across all versions of the eMoney
    Mock Server API.
    """
    
    # Service mapping for all entity types
    _service_mapping = {
        # V1 - Identity & Access Management
        "user": UserService,
        "office": OfficeService,
        "role": RoleService,
        "permission": PermissionService,
        "sharing_rule": SharingRuleService,
        "logon": LogonService,
        
        # V2 - Client & Household Management
        "client": ClientService,
        "household": HouseholdService,
        "spouse": SpouseService,
        "contact": ContactService,
        "relationship": RelationshipService,
        
        # V3 - Financial Planning Core
        "financial_plan": FinancialPlanService,
        "goal": GoalService,
        "scenario": ScenarioService,
        "cash_flow": CashFlowService,
        "net_worth": NetWorthService,
        
        # V4 - Account & Asset Management
        "account": AccountService,
        "account_type": AccountTypeService,
        "asset": AssetService,
        "asset_class": AssetClassService,
        "liability": LiabilityService
    }
    
    @classmethod
    def get_service(cls, entity_type: str, db: Session) -> Any:
        """
        Get a service instance for the specified entity type.
        
        Args:
            entity_type: The type of entity (e.g., 'user', 'client', 'account')
            db: Database session
            
        Returns:
            Service instance for the specified entity type
            
        Raises:
            ValueError: If the entity type is not supported
            
        Example:
            ```python
            # Get user service
            user_service = EntityServiceFactory.get_service("user", db)
            users = user_service.get_all(db)
            
            # Get client service
            client_service = EntityServiceFactory.get_service("client", db)
            client = client_service.get_by_id(db, "C12345")
            ```
        """
        if entity_type not in cls._service_mapping:
            available_types = list(cls._service_mapping.keys())
            raise ValueError(
                f"Unsupported entity type: {entity_type}. "
                f"Available types: {', '.join(available_types)}"
            )
        
        service_class = cls._service_mapping[entity_type]
        return service_class()
    
    @classmethod
    def get_available_entities(cls) -> dict:
        """
        Get a dictionary of all available entity types organized by version.
        
        Returns:
            Dictionary with version keys and lists of entity types
            
        Example:
            ```python
            entities = EntityServiceFactory.get_available_entities()
            print(entities["v1"])  # ['user', 'office', 'role', ...]
            ```
        """
        return {
            "v1": [
                "user", "office", "role", "permission", 
                "sharing_rule", "logon"
            ],
            "v2": [
                "client", "household", "spouse", 
                "contact", "relationship"
            ],
            "v3": [
                "financial_plan", "goal", "scenario", 
                "cash_flow", "net_worth"
            ],
            "v4": [
                "account", "account_type", "asset", 
                "asset_class", "liability"
            ]
        }
    
    @classmethod
    def get_version_services(cls, version: str, db: Session) -> dict:
        """
        Get all service instances for a specific version.
        
        Args:
            version: Version identifier (v1, v2, v3, v4)
            db: Database session
            
        Returns:
            Dictionary of entity_type -> service_instance for the version
            
        Raises:
            ValueError: If the version is not supported
            
        Example:
            ```python
            # Get all V2 services
            v2_services = EntityServiceFactory.get_version_services("v2", db)
            client_service = v2_services["client"]
            household_service = v2_services["household"]
            ```
        """
        available_entities = cls.get_available_entities()
        
        if version not in available_entities:
            available_versions = list(available_entities.keys())
            raise ValueError(
                f"Unsupported version: {version}. "
                f"Available versions: {', '.join(available_versions)}"
            )
        
        services = {}
        for entity_type in available_entities[version]:
            services[entity_type] = cls.get_service(entity_type, db)
        
        return services
    
    @classmethod
    def is_entity_supported(cls, entity_type: str) -> bool:
        """
        Check if an entity type is supported by the factory.
        
        Args:
            entity_type: The entity type to check
            
        Returns:
            True if the entity type is supported, False otherwise
            
        Example:
            ```python
            if EntityServiceFactory.is_entity_supported("client"):
                service = EntityServiceFactory.get_service("client", db)
            ```
        """
        return entity_type in cls._service_mapping
    
    @classmethod
    def get_entity_version(cls, entity_type: str) -> str:
        """
        Get the version that an entity type belongs to.
        
        Args:
            entity_type: The entity type to check
            
        Returns:
            Version identifier (v1, v2, v3, v4)
            
        Raises:
            ValueError: If the entity type is not supported
            
        Example:
            ```python
            version = EntityServiceFactory.get_entity_version("client")
            print(version)  # "v2"
            ```
        """
        available_entities = cls.get_available_entities()
        
        for version, entities in available_entities.items():
            if entity_type in entities:
                return version
        
        raise ValueError(f"Unsupported entity type: {entity_type}")
    
    @classmethod
    def get_service_info(cls) -> dict:
        """
        Get comprehensive information about all available services.
        
        Returns:
            Dictionary with service information organized by version
            
        Example:
            ```python
            info = EntityServiceFactory.get_service_info()
            print(info["v1"]["user"]["class_name"])  # "UserService"
            ```
        """
        available_entities = cls.get_available_entities()
        service_info = {}
        
        for version, entities in available_entities.items():
            service_info[version] = {}
            for entity_type in entities:
                service_class = cls._service_mapping[entity_type]
                service_info[version][entity_type] = {
                    "class_name": service_class.__name__,
                    "module": service_class.__module__,
                    "entity_type": entity_type,
                    "version": version
                }
        
        return service_info


# Convenience functions for common operations
def get_user_service(db: Session) -> UserService:
    """Get UserService instance."""
    return EntityServiceFactory.get_service("user", db)


def get_client_service(db: Session) -> ClientService:
    """Get ClientService instance."""
    return EntityServiceFactory.get_service("client", db)


def get_account_service(db: Session) -> AccountService:
    """Get AccountService instance."""
    return EntityServiceFactory.get_service("account", db)


def get_financial_plan_service(db: Session) -> FinancialPlanService:
    """Get FinancialPlanService instance."""
    return EntityServiceFactory.get_service("financial_plan", db)


# Service validation and debugging utilities
class ServiceValidator:
    """Utility class for validating service configurations and dependencies."""
    
    @staticmethod
    def validate_all_services(db: Session) -> dict:
        """
        Validate that all services can be instantiated successfully.
        
        Args:
            db: Database session for testing
            
        Returns:
            Dictionary with validation results for each service
        """
        results = {}
        factory = EntityServiceFactory()
        
        for entity_type in factory._service_mapping.keys():
            try:
                service = factory.get_service(entity_type, db)
                results[entity_type] = {
                    "status": "success",
                    "service_class": service.__class__.__name__,
                    "has_get_all": hasattr(service, "get_all"),
                    "has_get_by_id": hasattr(service, "get_by_id")
                }
            except Exception as e:
                results[entity_type] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    @staticmethod
    def get_service_dependencies() -> dict:
        """
        Analyze service dependencies and relationships.
        
        Returns:
            Dictionary showing which services depend on others
        """
        # This could be expanded to analyze actual service method dependencies
        return {
            "v1_dependencies": {
                "sharing_rule": ["user", "client"],  # SharingRule depends on User and Client
                "logon": ["user"]  # Logon depends on User
            },
            "v2_dependencies": {
                "client": ["household", "spouse", "user", "office"],  # Client references these
                "contact": ["client"],  # Contact belongs to Client
                "relationship": ["client"]  # Relationship connects Clients
            },
            "v3_dependencies": {
                "financial_plan": ["client", "household", "user"],  # Plan references these
                "goal": ["financial_plan", "client"],  # Goal belongs to Plan and Client
                "scenario": ["financial_plan"],  # Scenario belongs to Plan
                "cash_flow": ["financial_plan"],  # CashFlow belongs to Plan
                "net_worth": ["financial_plan", "household"]  # NetWorth belongs to Plan and Household
            },
            "v4_dependencies": {
                "account": ["client", "household", "account_type"],  # Account references these
                "asset": ["account", "asset_class"],  # Asset belongs to Account and AssetClass
                "liability": ["client", "household"]  # Liability belongs to Client/Household
            }
        }


# Factory instance for global use
entity_service_factory = EntityServiceFactory()
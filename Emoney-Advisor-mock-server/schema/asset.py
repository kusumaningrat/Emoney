from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class AssetType(str, Enum):
    REAL_ESTATE = "Real Estate"
    RETIREMENT = "Retirement"
    INVESTMENT = "Investment"
    CASH = "Cash"
    VEHICLE = "Vehicle"
    BUSINESS = "Business"
    PERSONAL = "Personal Property"
    OTHER = "Other"


# Base schemas
class AssetBase(BaseModel):
    client_id: str = Field(..., description="ID of client asset belongs to")
    plan_id: Optional[str] = Field(None, description="ID of plan asset belongs to")
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Asset description")
    type: str = Field(..., description="Asset type")
    value: float = Field(..., description="Current value")
    basis: Optional[float] = Field(None, description="Cost basis")
    growth_rate: float = Field(0.0, description="Annual growth rate")
    ownership: str = Field(..., description="Asset ownership")
    account_id: Optional[str] = Field(None, description="Associated account ID")
    created_by: str = Field(..., description="ID of user who created the asset")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the asset")


class AssetClassBase(BaseModel):
    name: str = Field(..., description="Asset class name")
    parent_id: Optional[str] = Field(None, description="Parent asset class ID")
    created_by: str = Field(..., description="ID of user who created the asset class")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the asset class")


class AllocationBase(BaseModel):
    asset_id: str = Field(..., description="Asset ID")
    asset_class_id: str = Field(..., description="Asset class ID")
    percentage: float = Field(..., description="Allocation percentage")
    value: float = Field(..., description="Allocation value")
    created_by: str = Field(..., description="ID of user who created the allocation")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the allocation")


class SecurityBase(BaseModel):
    symbol: Optional[str] = Field(None, description="Security symbol")
    name: str = Field(..., description="Security name")
    type: str = Field(..., description="Security type")
    price: float = Field(..., description="Current price")
    price_date: date = Field(..., description="Price date")
    asset_class_id: Optional[str] = Field(None, description="Asset class ID")
    created_by: str = Field(..., description="ID of user who created the security")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the security")


class HoldingBase(BaseModel):
    asset_id: str = Field(..., description="Asset ID")
    security_id: str = Field(..., description="Security ID")
    shares: float = Field(..., description="Number of shares")
    price: float = Field(..., description="Current price per share")
    value: float = Field(..., description="Total value")
    basis: Optional[float] = Field(None, description="Cost basis")
    created_by: str = Field(..., description="ID of user who created the holding")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the holding")


# Response models with ID and timestamps
class AssetResponse(BaseModel):
    id: str = Field(..., description="Asset ID")
    clientId: str = Field(..., description="ID of client asset belongs to")
    planId: Optional[str] = Field(None, description="ID of plan asset belongs to")
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Asset description")
    type: str = Field(..., description="Asset type")
    value: float = Field(..., description="Current value")
    basis: Optional[float] = Field(None, description="Cost basis")
    growthRate: float = Field(0.0, description="Annual growth rate")
    ownership: str = Field(..., description="Asset ownership")
    accountId: Optional[str] = Field(None, description="Associated account ID")
    createdBy: str = Field(..., description="ID of user who created the asset")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the asset")
    createdAt: datetime = Field(..., description="Timestamp when asset was created")
    updatedAt: datetime = Field(..., description="Timestamp when asset was last updated")
    
    model_config = {
        "from_attributes": True
    }


class AssetClassResponse(BaseModel):
    id: str = Field(..., description="Asset class ID")
    name: str = Field(..., description="Asset class name")
    parentId: Optional[str] = Field(None, description="Parent asset class ID")
    createdBy: str = Field(..., description="ID of user who created the asset class")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the asset class")
    createdAt: datetime = Field(..., description="Timestamp when asset class was created")
    updatedAt: datetime = Field(..., description="Timestamp when asset class was last updated")
    
    model_config = {
        "from_attributes": True
    }


class AllocationResponse(BaseModel):
    id: str = Field(..., description="Allocation ID")
    assetId: str = Field(..., description="Asset ID")
    assetClassId: str = Field(..., description="Asset class ID")
    percentage: float = Field(..., description="Allocation percentage")
    value: float = Field(..., description="Allocation value")
    createdBy: str = Field(..., description="ID of user who created the allocation")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the allocation")
    createdAt: datetime = Field(..., description="Timestamp when allocation was created")
    updatedAt: datetime = Field(..., description="Timestamp when allocation was last updated")
    
    model_config = {
        "from_attributes": True
    }


class SecurityResponse(BaseModel):
    id: str = Field(..., description="Security ID")
    symbol: Optional[str] = Field(None, description="Security symbol")
    name: str = Field(..., description="Security name")
    type: str = Field(..., description="Security type")
    price: float = Field(..., description="Current price")
    priceDate: date = Field(..., description="Price date")
    assetClassId: Optional[str] = Field(None, description="Asset class ID")
    createdBy: str = Field(..., description="ID of user who created the security")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the security")
    createdAt: datetime = Field(..., description="Timestamp when security was created")
    updatedAt: datetime = Field(..., description="Timestamp when security was last updated")
    
    model_config = {
        "from_attributes": True
    }


class HoldingResponse(BaseModel):
    id: str = Field(..., description="Holding ID")
    assetId: str = Field(..., description="Asset ID")
    securityId: str = Field(..., description="Security ID")
    shares: float = Field(..., description="Number of shares")
    price: float = Field(..., description="Current price per share")
    value: float = Field(..., description="Total value")
    basis: Optional[float] = Field(None, description="Cost basis")
    createdBy: str = Field(..., description="ID of user who created the holding")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the holding")
    createdAt: datetime = Field(..., description="Timestamp when holding was created")
    updatedAt: datetime = Field(..., description="Timestamp when holding was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class AssetListResponse(BaseModel):
    assets: List[AssetResponse] = Field(..., description="List of assets")
    totalValue: float = Field(..., description="Total asset value")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class AssetClassListResponse(BaseModel):
    assetClasses: List[AssetClassResponse] = Field(..., description="List of asset classes")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class AllocationListResponse(BaseModel):
    allocations: List[AllocationResponse] = Field(..., description="List of allocations")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class SecurityListResponse(BaseModel):
    securities: List[SecurityResponse] = Field(..., description="List of securities")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class HoldingListResponse(BaseModel):
    holdings: List[HoldingResponse] = Field(..., description="List of holdings")
    totalValue: float = Field(..., description="Total holding value")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class AssetFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    type: Optional[str] = Field(None, description="Filter by asset type")
    ownership: Optional[str] = Field(None, description="Filter by ownership")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    value_gt: Optional[float] = Field(None, description="Filter by minimum value")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("value", description="Sort field")
    count: bool = Field(False, description="Return count only")


class AssetClassFilterParams(BaseModel):
    parent_id: Optional[str] = Field(None, description="Filter by parent asset class ID")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class AllocationFilterParams(BaseModel):
    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    asset_class_id: Optional[str] = Field(None, description="Filter by asset class ID")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("percentage", description="Sort field")
    count: bool = Field(False, description="Return count only")


class SecurityFilterParams(BaseModel):
    asset_class_id: Optional[str] = Field(None, description="Filter by asset class ID")
    type: Optional[str] = Field(None, description="Filter by security type")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class HoldingFilterParams(BaseModel):
    asset_id: Optional[str] = Field(None, description="Filter by asset ID")
    security_id: Optional[str] = Field(None, description="Filter by security ID")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("value", description="Sort field")
    count: bool = Field(False, description="Return count only")
# schemas/scan.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ScanStatusEnum(str, Enum):
    """Enumeration for scan status values"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ScanRequest(BaseModel):
    scan_type: str = Field(..., description="Type of scan (auth, client, activity, etc.)")
    entity_types: List[str] = Field(..., description="List of entity types to scan")
    organizationId: Optional[str] = Field(None, description="Organization ID")
    auth: Dict[str, Any] = Field(default_factory=dict, description="Authentication configuration")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Scan filters")
    scanId: Optional[str] = Field(None, description="Optional scan ID")
    
    @validator("entity_types")
    def validate_entity_types(cls, v):
        """Validate that at least one entity type is specified"""
        if not v or len(v) == 0:
            raise ValueError("At least one entity type must be specified")
        return v

class EntityResultResponse(BaseModel):
    """Schema for entity result response"""
    id: str
    entity_type: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    record_count: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    warning_count: Optional[int] = None
    processing_time: Optional[float] = None

class ScanResponse(BaseModel):
    """Schema for scan response"""
    id: str
    scan_type: str
    status: str
    entity_types: List[str]
    organization_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ScanStatusResponse(ScanResponse):
    """Schema for scan status response"""
    entity_results: List[EntityResultResponse] = Field(default_factory=list)

class ScanListItem(BaseModel):
    """Schema for scan list item"""
    id: str
    scan_type: str
    status: str
    entity_types: List[str]
    organization_id: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ScanListResponse(BaseModel):
    """Schema for paginated scan list response"""
    items: List[ScanListItem] = Field(default_factory=list)
    total: int
    page: int
    limit: int
    pages: int
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# Pagination response schema
class PaginatedResponse(BaseModel):
    total: int = Field(..., description="Total number of records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of records per page")
    total_pages: int = Field(..., description="Total number of pages")


# Base filter parameters
class BaseFilterParams(BaseModel):
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")
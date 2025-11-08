from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class DocumentType(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    JPG = "JPG"
    PNG = "PNG"
    ZIP = "ZIP"
    TXT = "TXT"
    OTHER = "OTHER"


class AlertSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertType(str, Enum):
    SYSTEM = "System"
    CLIENT = "Client"
    PLAN = "Plan"


class AlertStatus(str, Enum):
    ACTIVE = "Active"
    DISMISSED = "Dismissed"


class TaskPriority(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TaskStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


# Base schemas
class VaultDocumentBase(BaseModel):
    client_id: str = Field(..., description="ID of client document belongs to")
    name: str = Field(..., description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    content: Optional[bytes] = Field(None, description="Document content")
    created_by: str = Field(..., description="ID of user who created the document")


class NoteBase(BaseModel):
    client_id: str = Field(..., description="ID of client note belongs to")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_by: str = Field(..., description="ID of user who created the note")


class TaskBase(BaseModel):
    client_id: str = Field(..., description="ID of client task belongs to")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    due_date: Optional[date] = Field(None, description="Due date")
    priority: str = Field(..., description="Task priority")
    status: str = Field(..., description="Task status")
    assigned_to: str = Field(..., description="ID of user task is assigned to")
    created_by: str = Field(..., description="ID of user who created the task")


class AlertBase(BaseModel):
    client_id: str = Field(..., description="ID of client alert belongs to")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    status: str = Field(..., description="Alert status")


# Response models with ID and timestamps
class VaultDocumentResponse(BaseModel):
    id: str = Field(..., description="Document ID")
    clientId: str = Field(..., description="ID of client document belongs to")
    name: str = Field(..., description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    fileName: str = Field(..., description="Original file name")
    fileType: str = Field(..., description="File type")
    fileSize: int = Field(..., description="File size in bytes")
    mimeType: str = Field(..., description="MIME type")
    createdBy: str = Field(..., description="ID of user who created the document")
    createdAt: datetime = Field(..., description="Timestamp when document was created")
    updatedAt: datetime = Field(..., description="Timestamp when document was last updated")
    
    model_config = {
        "from_attributes": True
    }


class NoteResponse(BaseModel):
    id: str = Field(..., description="Note ID")
    clientId: str = Field(..., description="ID of client note belongs to")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    createdBy: str = Field(..., description="ID of user who created the note")
    createdAt: datetime = Field(..., description="Timestamp when note was created")
    updatedAt: datetime = Field(..., description="Timestamp when note was last updated")
    
    model_config = {
        "from_attributes": True
    }


class TaskResponse(BaseModel):
    id: str = Field(..., description="Task ID")
    clientId: str = Field(..., description="ID of client task belongs to")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    dueDate: Optional[date] = Field(None, description="Due date")
    priority: str = Field(..., description="Task priority")
    status: str = Field(..., description="Task status")
    assignedTo: str = Field(..., description="ID of user task is assigned to")
    createdBy: str = Field(..., description="ID of user who created the task")
    createdAt: datetime = Field(..., description="Timestamp when task was created")
    updatedAt: datetime = Field(..., description="Timestamp when task was last updated")
    
    model_config = {
        "from_attributes": True
    }


class AlertResponse(BaseModel):
    id: str = Field(..., description="Alert ID")
    clientId: str = Field(..., description="ID of client alert belongs to")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    type: str = Field(..., description="Alert type")
    severity: str = Field(..., description="Alert severity")
    status: str = Field(..., description="Alert status")
    createdAt: datetime = Field(..., description="Timestamp when alert was created")
    updatedAt: datetime = Field(..., description="Timestamp when alert was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class VaultDocumentListResponse(BaseModel):
    documents: List[VaultDocumentResponse] = Field(..., description="List of documents")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class NoteListResponse(BaseModel):
    notes: List[NoteResponse] = Field(..., description="List of notes")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class AlertListResponse(BaseModel):
    alerts: List[AlertResponse] = Field(..., description="List of alerts")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class VaultDocumentFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    file_type: Optional[str] = Field(None, description="Filter by file type")
    name: Optional[str] = Field(None, description="Filter by name")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class NoteFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    title: Optional[str] = Field(None, description="Filter by title")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class TaskFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    status: Optional[str] = Field(None, description="Filter by task status")
    priority: Optional[str] = Field(None, description="Filter by task priority")
    assigned_to: Optional[str] = Field(None, description="Filter by assignee")
    due_date_before: Optional[date] = Field(None, description="Filter by due date before")
    due_date_after: Optional[date] = Field(None, description="Filter by due date after")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("due_date", description="Sort field")
    count: bool = Field(False, description="Return count only")


class AlertFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    type: Optional[str] = Field(None, description="Filter by alert type")
    severity: Optional[str] = Field(None, description="Filter by alert severity")
    status: Optional[str] = Field(None, description="Filter by alert status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")
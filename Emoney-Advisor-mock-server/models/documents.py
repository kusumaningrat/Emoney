from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, LargeBinary, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class FileType(Base):
    """
    FileType model for managing supported file types in the system
    Defines file categories, extensions, and metadata
    """
    __tablename__ = "file_types"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    extension = Column(String, nullable=False, unique=True)  # e.g., ".pdf", ".docx"
    mime_type = Column(String, nullable=False)  # e.g., "application/pdf"
    category = Column(String, nullable=False)  # e.g., "document", "image", "spreadsheet"
    icon = Column(String)  # Optional icon identifier or path
    max_size = Column(Integer)  # Maximum file size in bytes (optional)
    is_active = Column(Boolean, default=True)  # Whether this file type is currently accepted
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("VaultDocument", back_populates="file_type_obj")
    attachments = relationship("Attachment", back_populates="file_type_obj")

class Attachment(Base):
    """
    Attachment model for files attached to various entities
    Provides flexible file attachment capability for notes, tasks, alerts, etc.
    """
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)  # e.g., "note", "task", "alert", "client"
    entity_id = Column(String, nullable=False, index=True)  # ID of the entity this is attached to
    name = Column(String, nullable=False)  # Display name
    description = Column(String)
    file_name = Column(String, nullable=False)  # Original file name
    file_type = Column(String, ForeignKey("file_types.extension"))
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=False)
    content = Column(LargeBinary)  # Binary file content
    storage_path = Column(String)  # Optional external storage path
    checksum = Column(String)  # Optional file checksum for integrity verification
    is_public = Column(Boolean, default=False)  # Whether attachment is publicly accessible
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    file_type_obj = relationship("FileType", back_populates="attachments")
    creator = relationship("User", foreign_keys=[created_by])

class VaultDocument(Base):
    """
    VaultDocument model for client document storage
    Primary document repository for client files
    """
    __tablename__ = "vault_documents"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    file_name = Column(String, nullable=False)
    file_type = Column(String, ForeignKey("file_types.extension"), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    content = Column(LargeBinary)
    storage_path = Column(String)  # Optional external storage path
    checksum = Column(String)  # File checksum for integrity
    version = Column(Integer, default=1)  # Document version number
    is_archived = Column(Boolean, default=False)
    tags = Column(String)  # Comma-separated tags for categorization
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="vault_documents")
    file_type_obj = relationship("FileType", back_populates="documents")
    creator = relationship("User", foreign_keys=[created_by])
    tax_documents = relationship("TaxDocument", back_populates="document")

class Note(Base):
    """
    Note model for client notes and memos
    Supports rich text content for client documentation
    """
    __tablename__ = "notes"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String)  # Optional categorization (e.g., "meeting", "phone_call")
    is_pinned = Column(Boolean, default=False)  # Whether note should be highlighted
    is_private = Column(Boolean, default=False)  # Private notes visible only to creator
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="notes")
    creator = relationship("User", foreign_keys=[created_by])

class Task(Base):
    """
    Task model for client-related tasks and action items
    Supports task assignment, prioritization, and tracking
    """
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(Date)
    priority = Column(String, nullable=False)  # e.g., "low", "medium", "high", "urgent"
    status = Column(String, nullable=False)  # e.g., "pending", "in_progress", "completed", "cancelled"
    category = Column(String)  # Task category for filtering
    estimated_hours = Column(Float)  # Estimated time to complete
    actual_hours = Column(Float)  # Actual time spent
    completion_date = Column(DateTime)  # When task was completed
    assigned_to = Column(String, ForeignKey("users.id"))
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], overlaps="creator")
    creator = relationship("User", foreign_keys=[created_by], overlaps="assignee")

class Alert(Base):
    """
    Alert model for system notifications and warnings
    Tracks important events and conditions requiring attention
    """
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True, index=True)  # NULL for system alerts
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "deadline", "compliance", "review", "milestone", "system"
    severity = Column(String, nullable=False)  # e.g., "info", "warning", "error", "critical"
    status = Column(String, nullable=False)  # e.g., "active", "acknowledged", "resolved", "dismissed"
    action_required = Column(Boolean, default=False)  # Whether alert requires action
    action_url = Column(String)  # Optional URL for action
    expires_at = Column(DateTime)  # When alert should be automatically dismissed
    acknowledged_by = Column(String, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    resolved_by = Column(String, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="alerts")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by], overlaps="resolver")
    resolver = relationship("User", foreign_keys=[resolved_by], overlaps="acknowledger")
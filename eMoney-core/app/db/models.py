# db/models.py

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON, Enum, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from app.db.database import Base

class ScanStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Scan(Base):
    """Scan entity representing a data extraction operation"""
    
    __tablename__ = "scans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(Enum(ScanStatus), nullable=False, default=ScanStatus.PENDING)
    
    # Scan configuration
    organization_id = Column(String(255), nullable=True)  # For multi-tenant support
    scan_type = Column(String(50), nullable=True)  # Primary scan type (auth, contact, etc.)
    entity_types = Column(JSON, nullable=True)  # Which entities to scan (e.g., User, Role, Contact)
    scan_config = Column(JSON, nullable=True)  # Detailed scan configuration
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Add indices for common query fields
    __table_args__ = (
        Index('ix_scans_status', status),
        Index('ix_scans_created_at', created_at),
        Index('ix_scans_organization_id', organization_id),
        Index('ix_scans_scan_type', scan_type),
    )
    
    # Relationships
    entity_results = relationship("ScanEntityResult", back_populates="scan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scan {self.id} ({self.status.value})>"


class ScanEntityResult(Base):
    """
    Represents the extraction result for a specific entity type within a scan
    """
    
    __tablename__ = "scan_entity_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(100), nullable=False)  # Type of entity (User, Role, Contact, etc.)
    
    # Status information
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    # Result metrics
    record_count = Column(Integer, nullable=True)  # How many records processed
    success_count = Column(Integer, nullable=True)  # How many succeeded
    error_count = Column(Integer, nullable=True)  # How many failed
    warning_count = Column(Integer, nullable=True)  # How many with warnings
    processing_time = Column(Float, nullable=True)  # Total processing time in seconds
    
    # Result data
    result_data = Column(JSON, nullable=True)  # The extracted data or reference to it
    error_details = Column(JSON, nullable=True)  # Details about any errors
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship back to the scan
    scan = relationship("Scan", back_populates="entity_results")
    
    __table_args__ = (
        Index('ix_scan_entity_results_scan_id', scan_id),
        Index('ix_scan_entity_results_entity_type', entity_type),
        Index('ix_scan_entity_results_status', status),
    )
    
    def __repr__(self):
        return f"<ScanEntityResult {self.id} - {self.entity_type} ({self.status})>"
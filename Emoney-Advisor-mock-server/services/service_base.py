# services/service_base.py

from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import Base
from datetime import datetime
import uuid

ModelType = TypeVar("ModelType", bound=Base)

class BaseService(Generic[ModelType]):
    """
    Base service class that provides common methods for all models
    """
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    def get_entities(self, q=None, limit=100, offset=0, options=None, firm_id=None):
        """
        Generic entity retrieval method that standardizes the interface for entity data.
        
        Args:
            q: Optional query string for filtering
            limit: Maximum number of results to return
            offset: Number of results to skip (for pagination)
            options: Additional options for the query
            firm_id: Optional firm ID for filtering
            
        Returns:
            Dict containing items, total count, limit, and offset
        """
        query = self.db.query(self.model)
        
        # Apply firm_id filter if provided and model has firm_id
        if firm_id and hasattr(self.model, 'firm_id'):
            query = query.filter(self.model.firm_id == firm_id)
        
        # Handle options parameter for count only
        if options == "count":
            return {"count": query.count()}
        
        # Apply pagination
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        
        # Convert to dictionary format for JSON response
        item_list = [self._entity_to_dict(item) for item in items]
        
        # Format response
        return {
            "items": item_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_entity_by_id(self, entity_id: str):
        """Get a single entity by ID"""
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if not entity:
            return None
        
        return self._entity_to_dict(entity)
    
    def create_entity(self, entity_data: Dict[str, Any], user_id: str = None):
        """Create a new entity"""
        # Generate ID if not provided
        if 'id' not in entity_data:
            entity_data['id'] = str(uuid.uuid4())
        
        # Add timestamps and user info if model has them
        if hasattr(self.model, 'created_at'):
            entity_data['created_at'] = datetime.utcnow()
        
        if hasattr(self.model, 'updated_at'):
            entity_data['updated_at'] = datetime.utcnow()
        
        if user_id:
            if hasattr(self.model, 'created_by'):
                entity_data['created_by'] = user_id
                
            if hasattr(self.model, 'updated_by'):
                entity_data['updated_by'] = user_id
        
        # Create new entity
        entity = self.model(**entity_data)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        
        return self._entity_to_dict(entity)
    
    def update_entity(self, entity_id: str, entity_data: Dict[str, Any], user_id: str = None):
        """Update an existing entity"""
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if not entity:
            return None
        
        # Update fields
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        # Update timestamp and user info if available
        if hasattr(entity, 'updated_at'):
            entity.updated_at = datetime.utcnow()
        
        if user_id and hasattr(entity, 'updated_by'):
            entity.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(entity)
        
        return self._entity_to_dict(entity)
    
    def delete_entity(self, entity_id: str):
        """Delete an entity"""
        entity = self.db.query(self.model).filter(self.model.id == entity_id).first()
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def _entity_to_dict(self, entity: ModelType) -> Dict[str, Any]:
        """Helper method to convert model to dictionary"""
        result = {}
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            
            # Convert datetime to ISO format string
            if isinstance(value, datetime):
                value = value.isoformat()
            
            result[column.name] = value
        
        return result
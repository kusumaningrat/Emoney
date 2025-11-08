# services/client_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.clients import Client, Spouse, Contact, Household, HouseholdMember, Relationship
from models.enums import ClientStatus, MaritalStatus
from services.service_base import BaseService
from datetime import datetime
import uuid

class ClientService(BaseService[Client]):
    def __init__(self, db: Session):
        super().__init__(db, Client)
    
    def get_entities(self, q=None, limit=100, offset=0, options=None, firm_id=None):
        """
        Override get_entities to add client-specific filtering
        """
        query = self.db.query(Client)
        
        # Apply filters if query parameter is provided
        if q:
            # Parse the query string (e.g., "status==active")
            if "==" in q:
                field, value = q.split("==")
                if field == "status" and value.lower() == "active":
                    query = query.filter(Client.marital_status == ClientStatus.ACTIVE.value)
                elif field == "marital_status":
                    # Convert string value to enum value
                    for status in MaritalStatus:
                        if status.value.lower() == value.lower():
                            query = query.filter(Client.marital_status == status.value)
                            break
                elif hasattr(Client, field):
                    # Dynamic filtering based on field name
                    query = query.filter(getattr(Client, field) == value)
            else:
                # Simple text search across multiple fields
                search_term = f"%{q}%"
                query = query.filter(
                    or_(
                        Client.first_name.ilike(search_term),
                        Client.last_name.ilike(search_term),
                        Client.email.ilike(search_term)
                    )
                )
        
        # Apply firm_id filter if provided
        if firm_id:
            query = query.filter(Client.firm_id == firm_id)
        
        # Handle options parameter for count only
        if options == "count":
            return {"count": query.count()}
        
        # Apply pagination
        total = query.count()
        clients = query.limit(limit).offset(offset).all()
        
        # Convert to dictionary format for JSON response
        client_list = [self._client_to_dict(client) for client in clients]
        
        # Format response
        return {
            "items": client_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_spouse_by_client_id(self, client_id: str):
        """Get spouse information for a client"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client or not client.spouse:
            return None
        
        return {
            "id": client.spouse.id,
            "client_id": client.spouse.client_id,
            "first_name": client.spouse.first_name,
            "last_name": client.spouse.last_name,
            "email": client.spouse.email,
            "phone": client.spouse.phone,
            "date_of_birth": client.spouse.date_of_birth.isoformat() if client.spouse.date_of_birth else None,
            "previous_marriages": client.spouse.previous_marriages,
            "created_by": client.spouse.created_by,
            "updated_by": client.spouse.updated_by,
            "created_at": client.spouse.created_at.isoformat() if client.spouse.created_at else None,
            "updated_at": client.spouse.updated_at.isoformat() if client.spouse.updated_at else None
        }
    
    def get_client_households(self, client_id: str):
        """Get households that a client belongs to"""
        memberships = self.db.query(HouseholdMember).filter(HouseholdMember.client_id == client_id).all()
        household_ids = [membership.household_id for membership in memberships]
        
        households = self.db.query(Household).filter(Household.id.in_(household_ids)).all()
        return [self._household_to_dict(household) for household in households]
    
    def get_client_contacts(self, client_id: str):
        """Get contacts for a client"""
        contacts = self.db.query(Contact).filter(Contact.client_id == client_id).all()
        return [self._contact_to_dict(contact) for contact in contacts]
    
    def get_client_relationships(self, client_id: str):
        """Get relationships for a client"""
        relationships = self.db.query(Relationship).filter(Relationship.client_id == client_id).all()
        return [self._relationship_to_dict(relationship) for relationship in relationships]

    def create_relationship(self, relationship_data: Dict[str, Any], user_id: str):
        """Create a new relationship between clients"""
        if 'id' not in relationship_data:
            relationship_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in relationship_data:
            relationship_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in relationship_data:
            relationship_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in relationship_data:
                relationship_data['created_by'] = user_id
                
            if 'updated_by' not in relationship_data:
                relationship_data['updated_by'] = user_id
        
        relationship = Relationship(**relationship_data)
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        
        return self._relationship_to_dict(relationship)

    def update_relationship(self, relationship_id: str, relationship_data: Dict[str, Any], user_id: str):
        """Update an existing relationship"""
        relationship = self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        if not relationship:
            return None
        
        for key, value in relationship_data.items():
            if hasattr(relationship, key):
                setattr(relationship, key, value)
                
        relationship.updated_at = datetime.utcnow()
        if user_id:
            relationship.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(relationship)
        
        return self._relationship_to_dict(relationship)

    def delete_relationship(self, relationship_id: str):
        """Delete a relationship"""
        relationship = self.db.query(Relationship).filter(Relationship.id == relationship_id).first()
        if not relationship:
            return False
        
        self.db.delete(relationship)
        self.db.commit()
        
        return True
    
    def create_spouse(self, client_id: str, spouse_data: Dict[str, Any], user_id: str):
        """Create or update spouse for a client"""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None
        
        # Check if spouse already exists
        if client.spouse:
            # Update existing spouse
            for key, value in spouse_data.items():
                if hasattr(client.spouse, key):
                    setattr(client.spouse, key, value)
                    
            if hasattr(client.spouse, 'updated_at'):
                client.spouse.updated_at = datetime.utcnow()
                
            if user_id and hasattr(client.spouse, 'updated_by'):
                client.spouse.updated_by = user_id
                
            spouse = client.spouse
        else:
            # Create new spouse
            if 'id' not in spouse_data:
                spouse_data['id'] = str(uuid.uuid4())
                
            spouse_data['client_id'] = client_id
            
            if 'created_at' not in spouse_data and hasattr(Spouse, 'created_at'):
                spouse_data['created_at'] = datetime.utcnow()
                
            if 'updated_at' not in spouse_data and hasattr(Spouse, 'updated_at'):
                spouse_data['updated_at'] = datetime.utcnow()
                
            if user_id:
                if 'created_by' not in spouse_data and hasattr(Spouse, 'created_by'):
                    spouse_data['created_by'] = user_id
                    
                if 'updated_by' not in spouse_data and hasattr(Spouse, 'updated_by'):
                    spouse_data['updated_by'] = user_id
            
            spouse = Spouse(**spouse_data)
            self.db.add(spouse)
        
        self.db.commit()
        self.db.refresh(spouse)
        
        # Update client's marital status if not already married
        if client.marital_status != MaritalStatus.MARRIED.value:
            client.marital_status = MaritalStatus.MARRIED.value
            client.updated_at = datetime.utcnow()
            if user_id:
                client.updated_by = user_id
            self.db.commit()
        
        return self._spouse_to_dict(spouse)
    
    def _client_to_dict(self, client: Client) -> Dict[str, Any]:
        """Helper method to convert Client model to dictionary"""
        return {
            "id": client.id,
            "firm_id": client.firm_id,
            "first_name": client.first_name,
            "last_name": client.last_name,
            "email": client.email,
            "phone": client.phone,
            "marital_status": client.marital_status,
            "previous_marriages": client.previous_marriages,
            "date_of_birth": client.date_of_birth.isoformat() if client.date_of_birth else None,
            "owning_advisor": client.owning_advisor,
            "external_id": client.external_id,
            "created_by": client.created_by,
            "updated_by": client.updated_by,
            "has_spouse": client.spouse is not None,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None
        }
    
    def _spouse_to_dict(self, spouse: Spouse) -> Dict[str, Any]:
        """Helper method to convert Spouse model to dictionary"""
        return {
            "id": spouse.id,
            "client_id": spouse.client_id,
            "first_name": spouse.first_name,
            "last_name": spouse.last_name,
            "email": spouse.email,
            "phone": spouse.phone,
            "date_of_birth": spouse.date_of_birth.isoformat() if spouse.date_of_birth else None,
            "previous_marriages": spouse.previous_marriages,
            "created_by": spouse.created_by,
            "updated_by": spouse.updated_by,
            "created_at": spouse.created_at.isoformat() if spouse.created_at else None,
            "updated_at": spouse.updated_at.isoformat() if spouse.updated_at else None
        }
    
    def _household_to_dict(self, household: Household) -> Dict[str, Any]:
        """Helper method to convert Household model to dictionary"""
        return {
            "id": household.id,
            "name": household.name,
            "primary_client_id": household.primary_client_id,
            "status": household.status,
            "total_aum": float(household.total_aum) if household.total_aum else None,
            "annual_revenue": float(household.annual_revenue) if household.annual_revenue else None,
            "client_since": household.client_since.isoformat() if household.client_since else None,
            "servicing_model": household.servicing_model,
            "review_frequency": household.review_frequency,
            "next_review_date": household.next_review_date.isoformat() if household.next_review_date else None,
            "created_by": household.created_by,
            "updated_by": household.updated_by,
            "created_at": household.created_at.isoformat() if household.created_at else None,
            "updated_at": household.updated_at.isoformat() if household.updated_at else None
        }
    
    def _contact_to_dict(self, contact: Contact) -> Dict[str, Any]:
        """Helper method to convert Contact model to dictionary"""
        return {
            "id": contact.id,
            "client_id": contact.client_id,
            "type": contact.type,
            "address_line1": contact.address_line1,
            "address_line2": contact.address_line2,
            "city": contact.city,
            "state": contact.state,
            "postal_code": contact.postal_code,
            "country": contact.country,
            "email": contact.email,
            "phone": contact.phone,
            "is_preferred": contact.is_preferred,
            "created_by": contact.created_by,
            "updated_by": contact.updated_by,
            "created_at": contact.created_at.isoformat() if contact.created_at else None,
            "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
        }
    
    def _relationship_to_dict(self, relationship: Relationship) -> Dict[str, Any]:
        """Helper method to convert Relationship model to dictionary"""
        return {
            "id": relationship.id,
            "client_id": relationship.client_id,
            "related_client_id": relationship.related_client_id,
            "relationship_type": relationship.relationship_type,
            "description": relationship.description,
            "notes": relationship.notes,
            "start_date": relationship.start_date.isoformat() if relationship.start_date else None,
            "end_date": relationship.end_date.isoformat() if relationship.end_date else None,
            "is_active": relationship.is_active,
            "created_by": relationship.created_by,
            "updated_by": relationship.updated_by,
            "created_at": relationship.created_at.isoformat() if relationship.created_at else None,
            "updated_at": relationship.updated_at.isoformat() if relationship.updated_at else None
        }
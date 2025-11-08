from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
import math
from datetime import datetime

from models.users import User, Role, Permission, Firm, Logon

class UserService:
    """
    Service for User entity
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_model(self):
        return User
    
    def get_entity_type(self) -> str:
        return "User"
    
    def get_entities(self, q: Optional[str] = None, limit: int = 100, 
                     offset: int = 0, options: Optional[str] = None, 
                     firm_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get users with filtering and pagination
        """
        # Build query
        query = self.db.query(User)
        
        # Apply firm_id filter if provided
        if firm_id:
            query = query.filter(User.firm_id == firm_id)
        
        # Apply query filter if provided
        if q:
            try:
                # Example: "is_active==true" becomes User.is_active == True
                parts = q.split('==')
                if len(parts) == 2:
                    field, value = parts
                    if hasattr(User, field):
                        # Handle boolean values
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        query = query.filter(getattr(User, field) == value)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid query format: {q}")
        
        # Get total count if requested
        total_count = None
        if options and 'count' in options:
            total_count = query.count()
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        users = query.all()
        
        # If no users found, return mock data
        if not users:
            mock_users = [
                {
                    "id": "user-001",
                    "firmId": "firm-001",
                    "username": "johndoe",
                    "email": "john.doe@example.com",
                    "firstName": "John",
                    "lastName": "Doe",
                    "title": "Senior Financial Advisor",
                    "phone": "555-123-4567",
                    "isActive": True,
                    "roles": ["Advisor", "Manager"],
                    "createdAt": "2024-01-15T09:30:00Z",
                    "updatedAt": "2024-01-15T09:30:00Z"
                },
                {
                    "id": "user-002",
                    "firmId": "firm-001",
                    "username": "janedoe",
                    "email": "jane.doe@example.com",
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "title": "Financial Planner",
                    "phone": "555-987-6543",
                    "isActive": True,
                    "roles": ["Advisor"],
                    "createdAt": "2024-02-10T14:15:00Z",
                    "updatedAt": "2024-02-10T14:15:00Z"
                },
                {
                    "id": "user-003",
                    "firmId": "firm-001",
                    "username": "mikebrown",
                    "email": "mike.brown@example.com",
                    "firstName": "Mike",
                    "lastName": "Brown",
                    "title": "Compliance Officer",
                    "phone": "555-456-7890",
                    "isActive": True,
                    "roles": ["Compliance"],
                    "createdAt": "2024-03-05T11:45:00Z",
                    "updatedAt": "2024-03-05T11:45:00Z"
                },
                {
                    "id": "user-004",
                    "firmId": "firm-002",
                    "username": "sarahsmith",
                    "email": "sarah.smith@example.com",
                    "firstName": "Sarah",
                    "lastName": "Smith",
                    "title": "Investment Specialist",
                    "phone": "555-789-0123",
                    "isActive": True,
                    "roles": ["Advisor", "Investment"],
                    "createdAt": "2024-03-15T10:20:00Z",
                    "updatedAt": "2024-03-15T10:20:00Z"
                },
                {
                    "id": "user-005",
                    "firmId": "firm-002",
                    "username": "davidjones",
                    "email": "david.jones@example.com",
                    "firstName": "David",
                    "lastName": "Jones",
                    "title": "Client Services",
                    "phone": "555-321-6547",
                    "isActive": True,
                    "roles": ["Assistant"],
                    "createdAt": "2024-04-01T09:10:00Z",
                    "updatedAt": "2024-04-01T09:10:00Z"
                }
            ]
            
            # Apply filters to mock data
            if firm_id:
                mock_users = [user for user in mock_users if user["firmId"] == firm_id]
                
            if q:
                try:
                    parts = q.split('==')
                    if len(parts) == 2:
                        field, value = parts
                        # Convert to camelCase
                        field_camel = field[0].lower() + field[1:] if field else ""
                        # Handle boolean values
                        if value.lower() in ('true', 'false'):
                            value = value.lower() == 'true'
                        mock_users = [user for user in mock_users if str(user.get(field_camel)) == str(value)]
                except:
                    pass
            
            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_users = mock_users[start_idx:end_idx]
            
            result = {
                "users": paginated_users
            }
            
            if options and 'count' in options:
                result["total"] = len(mock_users)
                
            return result
        
        # Format users
        formatted_users = []
        
        for user in users:
            # Get roles for user
            roles = [role.name for role in user.roles]
            
            user_dict = {
                "id": user.id,
                "firmId": user.firm_id,
                "username": user.username,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "title": user.title,
                "phone": user.phone,
                "isActive": user.is_active,
                "roles": roles,
                "createdAt": user.created_at.isoformat() if user.created_at else None,
                "updatedAt": user.updated_at.isoformat() if user.updated_at else None
            }
            
            formatted_users.append(user_dict)
        
        # Create response
        result = {
            "users": formatted_users
        }
        
        # Add count if requested
        if total_count is not None:
            result["total"] = total_count
            
        return result
    
    def get_entity_by_id(self, entity_id: str) -> Dict[str, Any]:
        """
        Get user by ID
        """
        user = self.db.query(User).filter(User.id == entity_id).first()
        
        if not user:
            # Return mock user if not found (for development purposes)
            mock_user = {
                "id": entity_id,
                "firmId": "firm-001",
                "username": "johndoe",
                "email": "john.doe@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "title": "Senior Financial Advisor",
                "phone": "555-123-4567",
                "isActive": True,
                "roles": ["Advisor", "Manager"],
                "createdAt": "2024-01-15T09:30:00Z",
                "updatedAt": "2024-01-15T09:30:00Z"
            }
            
            return mock_user
            
        # Get roles for user
        roles = [role.name for role in user.roles]
        
        user_dict = {
            "id": user.id,
            "firmId": user.firm_id,
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "title": user.title,
            "phone": user.phone,
            "isActive": user.is_active,
            "roles": roles,
            "createdAt": user.created_at.isoformat() if user.created_at else None,
            "updatedAt": user.updated_at.isoformat() if user.updated_at else None
        }
        
        return user_dict


class LogonService:
    """
    Service for Logon entity
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_model(self):
        return Logon
    
    def get_entity_type(self) -> str:
        return "Logon"
    
    def get_entities(self, q: Optional[str] = None, limit: int = 100, 
                     offset: int = 0, options: Optional[str] = None, 
                     firm_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get logons with filtering and pagination
        """
        # Build query
        query = self.db.query(Logon)
        
        # Apply firm_id filter if provided (indirectly through user or client)
        if firm_id:
            # Use join and filter logic here if necessary
            pass
        
        # Apply query filter if provided
        if q:
            try:
                parts = q.split('==')
                if len(parts) == 2:
                    field, value = parts
                    if hasattr(Logon, field):
                        query = query.filter(getattr(Logon, field) == value)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid query format: {q}")
        
        # Get total count if requested
        total_count = None
        if options and 'count' in options:
            total_count = query.count()
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        logons = query.all()
        
        # If no logons found, return mock data
        if not logons:
            mock_logons = [
                {
                    "id": "logon-001",
                    "userId": "user-001",
                    "clientId": None,
                    "username": "johndoe",
                    "status": "Active",
                    "lastLogin": "2025-04-15T10:30:45Z",
                    "createdAt": "2024-01-15T09:30:00Z",
                    "updatedAt": "2025-04-15T10:30:45Z"
                },
                {
                    "id": "logon-002",
                    "userId": "user-002",
                    "clientId": None,
                    "username": "janedoe",
                    "status": "Active",
                    "lastLogin": "2025-04-20T14:15:30Z",
                    "createdAt": "2024-02-10T14:15:00Z",
                    "updatedAt": "2025-04-20T14:15:30Z"
                },
                {
                    "id": "logon-003",
                    "userId": None,
                    "clientId": "client-001",
                    "username": "client1",
                    "status": "Active",
                    "lastLogin": "2025-04-18T09:45:15Z",
                    "createdAt": "2024-03-10T11:00:00Z",
                    "updatedAt": "2025-04-18T09:45:15Z"
                },
                {
                    "id": "logon-004",
                    "userId": None,
                    "clientId": "client-002",
                    "username": "client2",
                    "status": "Active",
                    "lastLogin": "2025-04-12T16:20:10Z",
                    "createdAt": "2024-03-15T10:30:00Z",
                    "updatedAt": "2025-04-12T16:20:10Z"
                },
                {
                    "id": "logon-005",
                    "userId": "user-003",
                    "clientId": None,
                    "username": "mikebrown",
                    "status": "Active",
                    "lastLogin": "2025-04-19T11:05:25Z",
                    "createdAt": "2024-03-05T11:45:00Z",
                    "updatedAt": "2025-04-19T11:05:25Z"
                }
            ]
            
            # Apply query filter to mock data if provided
            if q:
                try:
                    parts = q.split('==')
                    if len(parts) == 2:
                        field, value = parts
                        # Convert to camelCase
                        field_camel = field[0].lower() + field[1:] if field else ""
                        mock_logons = [logon for logon in mock_logons if str(logon.get(field_camel)) == str(value)]
                except:
                    pass
            
            # Apply pagination
            start_idx = offset
            end_idx = offset + limit
            paginated_logons = mock_logons[start_idx:end_idx]
            
            result = {
                "logons": paginated_logons
            }
            
            if options and 'count' in options:
                result["total"] = len(mock_logons)
                
            return result
        
        # Format logons
        formatted_logons = []
        
        for logon in logons:
            logon_dict = {
                "id": logon.id,
                "userId": logon.user_id,
                "clientId": logon.client_id,
                "username": logon.username,
                "status": logon.status,
                "lastLogin": logon.last_login.isoformat() if logon.last_login else None,
                "createdAt": logon.created_at.isoformat() if logon.created_at else None,
                "updatedAt": logon.updated_at.isoformat() if logon.updated_at else None
            }
            
            formatted_logons.append(logon_dict)
        
        # Create response
        result = {
            "logons": formatted_logons
        }
        
        # Add count if requested
        if total_count is not None:
            result["total"] = total_count
            
        return result
    
    def get_entity_by_id(self, entity_id: str) -> Dict[str, Any]:
        """
        Get logon by ID
        """
        logon = self.db.query(Logon).filter(Logon.id == entity_id).first()
        
        if not logon:
            # Return mock logon if not found (for development purposes)
            mock_logon = {
                "id": entity_id,
                "userId": "user-001",
                "clientId": None,
                "username": "johndoe",
                "status": "Active",
                "lastLogin": "2025-04-15T10:30:45Z",
                "createdAt": "2024-01-15T09:30:00Z",
                "updatedAt": "2025-04-15T10:30:45Z"
            }
            
            return mock_logon
        
        logon_dict = {
            "id": logon.id,
            "userId": logon.user_id,
            "clientId": logon.client_id,
            "username": logon.username,
            "status": logon.status,
            "lastLogin": logon.last_login.isoformat() if logon.last_login else None,
            "createdAt": logon.created_at.isoformat() if logon.created_at else None,
            "updatedAt": logon.updated_at.isoformat() if logon.updated_at else None
        }
        
        return logon_dict
    
    def get_logon_by_client_id(self, client_id: str) -> Dict[str, Any]:
        """
        Get logon for a client
        """
        logon = self.db.query(Logon).filter(Logon.client_id == client_id).first()
        
        if not logon:
            # Return mock logon if not found (for development purposes)
            mock_logon = {
                "id": f"logon-{client_id}",
                "userId": None,
                "clientId": client_id,
                "username": f"client{client_id[-3:]}",
                "status": "Active",
                "lastLogin": "2025-04-18T09:45:15Z",
                "createdAt": "2024-03-10T11:00:00Z",
                "updatedAt": "2025-04-18T09:45:15Z"
            }
            
            return mock_logon
        
        logon_dict = {
            "id": logon.id,
            "userId": logon.user_id,
            "clientId": logon.client_id,
            "username": logon.username,
            "status": logon.status,
            "lastLogin": logon.last_login.isoformat() if logon.last_login else None,
            "createdAt": logon.created_at.isoformat() if logon.created_at else None,
            "updatedAt": logon.updated_at.isoformat() if logon.updated_at else None
        }
        
        return logon_dict
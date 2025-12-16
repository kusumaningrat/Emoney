# services/identity.py - Version 1: PascalCase column names

from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from models.identity import (
    User, Office, Role, Permission, SharingRule, Logon
)


class UserService:
    """Service for User operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[User]:
        """Get all users with pagination and optional status filter"""
        query = db.query(User)
        if status:
            query = query.filter(User.Status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID with relationships"""
        return db.query(User).options(
            joinedload(User.office),
            joinedload(User.roles)
        ).filter(User.UserID == user_id).first()
    
    def get_user_profile(self, db: Session, user_id: str) -> Optional[User]:
        """Get user profile with office details"""
        return db.query(User).options(
            joinedload(User.office)
        ).filter(User.UserID == user_id).first()
    
    def get_user_permissions(self, db: Session, user_id: str) -> List[Permission]:
        """Get aggregated permissions for a user from all assigned roles"""
        user = self.get_by_id(db, user_id)
        if not user:
            return []
        
        # Collect all permissions from user's roles
        all_permissions = []
        for role in user.roles:
            all_permissions.extend(role.permissions)
        
        # Remove duplicates
        unique_permissions = {perm.PermissionID: perm for perm in all_permissions}
        return list(unique_permissions.values())
    
    def get_user_roles(self, db: Session, user_id: str) -> List[Role]:
        """Get all roles assigned to a user"""
        user = self.get_by_id(db, user_id)
        return user.roles if user else []
    
    def get_user_clients(self, db: Session, user_id: str) -> List[str]:
        """Get all client IDs accessible by a user through sharing rules"""
        sharing_rules = db.query(SharingRule).filter(
            SharingRule.UserID == user_id,
            SharingRule.Status == "Active"
        ).all()
        return [rule.ClientID for rule in sharing_rules]


class OfficeService:
    """Service for Office operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Office]:
        """Get all offices with pagination and optional status filter"""
        query = db.query(Office)
        if status:
            query = query.filter(Office.Status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, office_id: str) -> Optional[Office]:
        """Get office by ID with relationships"""
        return db.query(Office).options(
            joinedload(Office.parent_office),
            joinedload(Office.child_offices)
        ).filter(Office.OfficeID == office_id).first()
    
    def get_office_users(self, db: Session, office_id: str, status: Optional[str] = None) -> List[User]:
        """Get all users in an office"""
        query = db.query(User).filter(User.OfficeID == office_id)
        if status:
            query = query.filter(User.Status == status)
        return query.all()
    
    def get_office_clients(self, db: Session, office_id: str) -> List[str]:
        """Get all client IDs associated with users in an office"""
        users = self.get_office_users(db, office_id, status="Active")
        client_ids = []
        for user in users:
            sharing_rules = db.query(SharingRule).filter(
                SharingRule.UserID == user.UserID,
                SharingRule.Status == "Active"
            ).all()
            client_ids.extend([rule.ClientID for rule in sharing_rules])
        return list(set(client_ids))  # Remove duplicates


class RoleService:
    """Service for Role operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Role]:
        """Get all roles with pagination and optional status filter"""
        query = db.query(Role)
        if status:
            query = query.filter(Role.Status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, role_id: str) -> Optional[Role]:
        """Get role by ID with permissions"""
        return db.query(Role).options(
            joinedload(Role.permissions)
        ).filter(Role.RoleID == role_id).first()
    
    def get_role_permissions(self, db: Session, role_id: str) -> List[Permission]:
        """Get all permissions for a role"""
        role = self.get_by_id(db, role_id)
        return role.permissions if role else []
    
    def get_role_users(self, db: Session, role_id: str) -> List[User]:
        """Get all users assigned to a role"""
        role = db.query(Role).options(
            joinedload(Role.users)
        ).filter(Role.RoleID == role_id).first()
        return role.users if role else []


class PermissionService:
    """Service for Permission operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, 
                category: Optional[str] = None, status: Optional[str] = None) -> List[Permission]:
        """Get all permissions with pagination and optional filters"""
        query = db.query(Permission)
        if category:
            query = query.filter(Permission.Category == category)
        if status:
            query = query.filter(Permission.Status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, permission_id: str) -> Optional[Permission]:
        """Get permission by ID"""
        return db.query(Permission).filter(
            Permission.PermissionID == permission_id
        ).first()
    
    def get_by_code(self, db: Session, permission_code: str) -> Optional[Permission]:
        """Get permission by permission code"""
        return db.query(Permission).filter(
            Permission.PermissionCode == permission_code
        ).first()


class SharingRuleService:
    """Service for SharingRule operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, 
                user_id: Optional[str] = None, client_id: Optional[str] = None,
                status: Optional[str] = None) -> List[SharingRule]:
        """Get all sharing rules with pagination and optional filters"""
        query = db.query(SharingRule)
        if user_id:
            query = query.filter(SharingRule.UserID == user_id)
        if client_id:
            query = query.filter(SharingRule.ClientID == client_id)
        if status:
            query = query.filter(SharingRule.Status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, sharing_rule_id: str) -> Optional[SharingRule]:
        """Get sharing rule by ID"""
        return db.query(SharingRule).options(
            joinedload(SharingRule.user),
            joinedload(SharingRule.created_by_user)
        ).filter(SharingRule.SharingRuleID == sharing_rule_id).first()
    
    def get_user_rules(self, db: Session, user_id: str, status: Optional[str] = "Active") -> List[SharingRule]:
        """Get all sharing rules for a specific user"""
        query = db.query(SharingRule).filter(SharingRule.UserID == user_id)
        if status:
            query = query.filter(SharingRule.Status == status)
        return query.all()
    
    def get_client_rules(self, db: Session, client_id: str, status: Optional[str] = "Active") -> List[SharingRule]:
        """Get all sharing rules for a specific client"""
        query = db.query(SharingRule).filter(SharingRule.ClientID == client_id)
        if status:
            query = query.filter(SharingRule.Status == status)
        return query.all()


class LogonService:
    """Service for Logon operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                user_id: Optional[str] = None, logon_type: Optional[str] = None,
                status: Optional[str] = None) -> List[Logon]:
        """Get all logons with pagination and optional filters"""
        query = db.query(Logon)
        if user_id:
            query = query.filter(Logon.UserID == user_id)
        if logon_type:
            query = query.filter(Logon.LogonType == logon_type)
        if status:
            query = query.filter(Logon.Status == status)
        return query.order_by(Logon.LogonDateTime.desc()).offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, logon_id: str) -> Optional[Logon]:
        """Get logon by ID"""
        return db.query(Logon).options(
            joinedload(Logon.user)
        ).filter(Logon.LogonID == logon_id).first()
    
    def get_user_logons(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Logon]:
        """Get all logons for a specific user"""
        return db.query(Logon).filter(
            Logon.UserID == user_id
        ).order_by(Logon.LogonDateTime.desc()).offset(skip).limit(limit).all()
    
    def get_logon_activity(self, db: Session, logon_id: str) -> Optional[Logon]:
        """Get logon activity history (same as get_by_id for now)"""
        return self.get_by_id(db, logon_id)
    
    def get_active_sessions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Logon]:
        """Get all currently active sessions"""
        return db.query(Logon).filter(
            Logon.Status == "Active"
        ).order_by(Logon.LogonDateTime.desc()).offset(skip).limit(limit).all()
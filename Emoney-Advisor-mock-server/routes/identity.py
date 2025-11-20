# routes/identity.py

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from database import get_db
from models.identity import User, Office, Role, Permission, SharingRule, Logon
from services.identity import (
    UserService, OfficeService, RoleService, 
    PermissionService, SharingRuleService, LogonService
)

router = APIRouter(
    tags=["Identity"],
    dependencies=[]
)

# Helper function to convert SQLAlchemy models to dict
def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime serialization
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        # Handle enum serialization
        elif hasattr(value, 'value'):
            value = value.value
        result[column.name] = value
    return result

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@router.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all users with pagination"""
    service = UserService()
    skip = (page - 1) * pageSize
    users = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    total = db.query(User).count()
    
    return {
        "users": [model_to_dict(user) for user in users],
        "total": total,
        "page": page,
        "pageSize": len(users)
    }

@router.get("/users/{userId}")
def get_user(
    userId: str = Path(...),
    includeRoles: bool = Query(False),
    includePermissions: bool = Query(False),
    includeClients: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get user by ID with optional includes"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = model_to_dict(user)
    
    # Add office details if available
    if user.office:
        result["office"] = model_to_dict(user.office)
    
    # Include roles if requested
    if includeRoles:
        result["roles"] = [model_to_dict(role) for role in user.roles]
    
    # Include permissions if requested
    if includePermissions:
        permissions = service.get_user_permissions(db, userId)
        result["permissions"] = [model_to_dict(p) for p in permissions]
    
    # Include clients if requested
    if includeClients:
        result["clients"] = service.get_user_clients(db, userId)
    
    return result

@router.get("/users/{userId}/profile")
def get_user_profile(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user profile with office details"""
    service = UserService()
    user = service.get_user_profile(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = model_to_dict(user)
    if user.office:
        result["office"] = model_to_dict(user.office)
    
    return result

@router.get("/users/{userId}/permissions")
def get_user_permissions(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user permissions"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    permissions = service.get_user_permissions(db, userId)
    
    return {
        "userId": userId,
        "permissions": [model_to_dict(p) for p in permissions],
        "total": len(permissions)
    }

@router.get("/users/{userId}/roles")
def get_user_roles(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user roles"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    roles = service.get_user_roles(db, userId)
    
    return {
        "userId": userId,
        "roles": [model_to_dict(role) for role in roles],
        "total": len(roles)
    }

@router.get("/users/{userId}/clients")
def get_user_clients(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user's assigned clients"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    client_ids = service.get_user_clients(db, userId)
    
    return {
        "userId": userId,
        "clients": client_ids,
        "total": len(client_ids)
    }

# ============================================================================
# OFFICE ENDPOINTS
# ============================================================================

@router.get("/offices")
def get_offices(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all offices with pagination"""
    service = OfficeService()
    skip = (page - 1) * pageSize
    offices = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    total = db.query(Office).count()
    
    return {
        "offices": [model_to_dict(office) for office in offices],
        "total": total,
        "page": page,
        "pageSize": len(offices)
    }

@router.get("/offices/{officeId}")
def get_office(
    officeId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get office by ID"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    
    result = model_to_dict(office)
    
    # Add parent office if available
    if office.parent_office:
        result["parentOffice"] = model_to_dict(office.parent_office)
    
    # Add child offices count
    result["childOfficeCount"] = len(office.child_offices)
    
    return result

@router.get("/offices/{officeId}/users")
def get_office_users(
    officeId: str = Path(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get users in an office"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    
    users = service.get_office_users(db, officeId, status=status)
    
    return {
        "officeId": officeId,
        "users": [model_to_dict(user) for user in users],
        "total": len(users)
    }

@router.get("/offices/{officeId}/clients")
def get_office_clients(
    officeId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get clients associated with an office"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")
    
    client_ids = service.get_office_clients(db, officeId)
    
    return {
        "officeId": officeId,
        "clients": client_ids,
        "total": len(client_ids)
    }

# ============================================================================
# ROLE ENDPOINTS
# ============================================================================

@router.get("/roles")
def get_roles(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all roles with pagination"""
    service = RoleService()
    skip = (page - 1) * pageSize
    roles = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    total = db.query(Role).count()
    
    return {
        "roles": [model_to_dict(role) for role in roles],
        "total": total,
        "page": page,
        "pageSize": len(roles)
    }

@router.get("/roles/{roleId}")
def get_role(
    roleId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get role by ID"""
    service = RoleService()
    role = service.get_by_id(db, roleId)
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    result = model_to_dict(role)
    result["permissionCount"] = len(role.permissions)
    result["userCount"] = len(role.users)
    
    return result

# ============================================================================
# PERMISSION ENDPOINTS
# ============================================================================

@router.get("/permissions")
def get_permissions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all permissions with pagination"""
    service = PermissionService()
    skip = (page - 1) * pageSize
    permissions = service.get_all(db, skip=skip, limit=pageSize, category=category, status=status)
    
    total = db.query(Permission).count()
    
    return {
        "permissions": [model_to_dict(perm) for perm in permissions],
        "total": total,
        "page": page,
        "pageSize": len(permissions)
    }

# ============================================================================
# SHARING RULE ENDPOINTS
# ============================================================================

@router.get("/sharingrules")
def get_sharing_rules(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    userId: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get client sharing rules"""
    service = SharingRuleService()
    skip = (page - 1) * pageSize
    sharing_rules = service.get_all(
        db, skip=skip, limit=pageSize, 
        user_id=userId, client_id=clientId, status=status
    )
    
    total_query = db.query(SharingRule)
    if userId:
        total_query = total_query.filter(SharingRule.user_id == userId)
    if clientId:
        total_query = total_query.filter(SharingRule.client_id == clientId)
    if status:
        total_query = total_query.filter(SharingRule.status == status)
    total = total_query.count()
    
    return {
        "sharingRules": [model_to_dict(rule) for rule in sharing_rules],
        "total": total,
        "page": page,
        "pageSize": len(sharing_rules)
    }

@router.get("/sharingrules/{ruleId}")
def get_sharing_rule(
    ruleId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific sharing rule"""
    service = SharingRuleService()
    rule = service.get_by_id(db, ruleId)
    
    if not rule:
        raise HTTPException(status_code=404, detail="Sharing rule not found")
    
    result = model_to_dict(rule)
    
    if rule.user:
        result["user"] = {
            "userId": rule.user.user_id,
            "username": rule.user.username,
            "firstName": rule.user.first_name,
            "lastName": rule.user.last_name
        }
    
    if rule.created_by_user:
        result["createdByUser"] = {
            "userId": rule.created_by_user.user_id,
            "username": rule.created_by_user.username
        }
    
    return result

# ============================================================================
# LOGON ENDPOINTS
# ============================================================================

@router.get("/logons")
def get_logons(
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
    userId: Optional[str] = Query(None),
    logonType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all logons (user and client portal)"""
    service = LogonService()
    skip = (page - 1) * pageSize
    logons = service.get_all(
        db, skip=skip, limit=pageSize,
        user_id=userId, logon_type=logonType, status=status
    )
    
    total_query = db.query(Logon)
    if userId:
        total_query = total_query.filter(Logon.user_id == userId)
    if logonType:
        total_query = total_query.filter(Logon.logon_type == logonType)
    if status:
        total_query = total_query.filter(Logon.status == status)
    total = total_query.count()
    
    return {
        "logons": [model_to_dict(logon) for logon in logons],
        "total": total,
        "page": page,
        "pageSize": len(logons)
    }

@router.get("/logons/{logonId}")
def get_logon(
    logonId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific logon"""
    service = LogonService()
    logon = service.get_by_id(db, logonId)
    
    if not logon:
        raise HTTPException(status_code=404, detail="Logon not found")
    
    result = model_to_dict(logon)
    
    if logon.user:
        result["user"] = {
            "userId": logon.user.user_id,
            "username": logon.user.username,
            "firstName": logon.user.first_name,
            "lastName": logon.user.last_name
        }
    
    return result

@router.get("/logons/{logonId}/activity")
def get_logon_activity(
    logonId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get logon activity history"""
    service = LogonService()
    logon = service.get_logon_activity(db, logonId)
    
    if not logon:
        raise HTTPException(status_code=404, detail="Logon not found")
    
    result = model_to_dict(logon)
    
    # Add computed fields
    if logon.logout_date_time and logon.logon_date_time:
        duration_seconds = (logon.logout_date_time - logon.logon_date_time).total_seconds()
        result["durationMinutes"] = int(duration_seconds / 60)
        result["durationFormatted"] = f"{int(duration_seconds // 3600)}h {int((duration_seconds % 3600) // 60)}m"
    
    if logon.user:
        result["user"] = {
            "userId": logon.user.user_id,
            "username": logon.user.username,
            "firstName": logon.user.first_name,
            "lastName": logon.user.last_name
        }
    
    return result
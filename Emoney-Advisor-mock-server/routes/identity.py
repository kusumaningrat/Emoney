# routes/identity.py - eMoney Advisor Identity & Access Management (Version 1)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from database import get_db
from models.identity import User, Office, Role, Permission, SharingRule, Logon
from services.identity import (
    UserService, OfficeService, RoleService, 
    PermissionService, SharingRuleService, LogonService
)

router = APIRouter(
    tags=["eMoney Identity & Access Management"],
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
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    office: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all users (Advisors, Assistants, Planners, etc.)"""
    service = UserService()
    skip = (page - 1) * pageSize
    
    users = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    # Apply additional filtering
    if office:
        users = [u for u in users if u.OfficeID == office]
    
    if role:
        # Filter by role name
        filtered_users = []
        for user in users:
            user_roles = service.get_user_roles(db, user.UserID)
            role_names = [r.RoleName for r in user_roles]
            if role in role_names:
                filtered_users.append(user)
        users = filtered_users
    
    # Get total count for pagination
    all_users = service.get_all(db, status=status)
    total = len(all_users)
    
    return {
        "users": [model_to_dict(user) for user in users],
        "total": total,
        "page": page,
        "pageSize": len(users),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/users/{userId}")
def get_user(
    userId: str = Path(...),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get specific user"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
    result = model_to_dict(user)
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'roles' in includes:
            roles = service.get_user_roles(db, userId)
            result['roles'] = [model_to_dict(r) for r in roles]
        
        if 'permissions' in includes:
            permissions = service.get_user_permissions(db, userId)
            result['permissions'] = [model_to_dict(p) for p in permissions]
        
        if 'clients' in includes:
            client_ids = service.get_user_clients(db, userId)
            result['clients'] = client_ids  # Just client IDs for now
    
    return result

@router.get("/users/{userId}/profile")
def get_user_profile(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    service = UserService()
    user = service.get_user_profile(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
    profile = model_to_dict(user)
    
    # Add office details
    if user.office:
        profile['officeName'] = user.office.OfficeName
        profile['officePath'] = user.office.OfficePath
    
    return profile

@router.get("/users/{userId}/permissions")
def get_user_permissions(
    userId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get user permissions"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
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
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
    roles = service.get_user_roles(db, userId)
    
    return {
        "userId": userId,
        "roles": [model_to_dict(r) for r in roles],
        "total": len(roles)
    }

@router.get("/users/{userId}/clients")
def get_user_clients(
    userId: str = Path(...),
    includeAccounts: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get user's assigned clients"""
    service = UserService()
    user = service.get_by_id(db, userId)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {userId} not found")
    
    client_ids = service.get_user_clients(db, userId)
    
    return {
        "userId": userId,
        "clients": client_ids,  # Just client IDs - full client objects would come from Version 2
        "total": len(client_ids),
        "note": "Full client details available via Client API endpoints (Version 2)"
    }

# ============================================================================
# OFFICE & ORGANIZATION MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/offices")
def get_offices(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all offices"""
    service = OfficeService()
    skip = (page - 1) * pageSize
    
    offices = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    # Get total count
    all_offices = service.get_all(db, status=status)
    total = len(all_offices)
    
    return {
        "offices": [model_to_dict(office) for office in offices],
        "total": total,
        "page": page,
        "pageSize": len(offices),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/offices/{officeId}")
def get_office(
    officeId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific office"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail=f"Office {officeId} not found")
    
    result = model_to_dict(office)
    
    # Add parent office info
    if office.parent_office:
        result['parentOfficeName'] = office.parent_office.OfficeName
    
    # Add child office count
    result['childOfficeCount'] = len(office.child_offices)
    
    return result

@router.get("/offices/{officeId}/users")
def get_office_users(
    officeId: str = Path(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get office users"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail=f"Office {officeId} not found")
    
    users = service.get_office_users(db, officeId, status=status)
    
    return {
        "officeId": officeId,
        "officeName": office.OfficeName,
        "users": [model_to_dict(u) for u in users],
        "total": len(users)
    }

@router.get("/offices/{officeId}/clients")
def get_office_clients(
    officeId: str = Path(...),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get office clients"""
    service = OfficeService()
    office = service.get_by_id(db, officeId)
    
    if not office:
        raise HTTPException(status_code=404, detail=f"Office {officeId} not found")
    
    client_ids = service.get_office_clients(db, officeId)
    
    return {
        "officeId": officeId,
        "officeName": office.OfficeName,
        "clients": client_ids,  # Just client IDs - full client objects would come from Version 2
        "total": len(client_ids),
        "note": "Full client details available via Client API endpoints (Version 2)"
    }

# ============================================================================
# ACCESS CONTROL ENDPOINTS
# ============================================================================

@router.get("/roles")
def get_roles(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all roles"""
    service = RoleService()
    skip = (page - 1) * pageSize
    
    roles = service.get_all(db, skip=skip, limit=pageSize, status=status)
    
    # Get total count
    all_roles = service.get_all(db, status=status)
    total = len(all_roles)
    
    return {
        "roles": [model_to_dict(role) for role in roles],
        "total": total,
        "page": page,
        "pageSize": len(roles),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/roles/{roleId}")
def get_role(
    roleId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific role"""
    service = RoleService()
    role = service.get_by_id(db, roleId)
    
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {roleId} not found")
    
    result = model_to_dict(role)
    
    # Include permissions
    permissions = service.get_role_permissions(db, roleId)
    result['permissions'] = [model_to_dict(p) for p in permissions]
    
    # Include user count
    users = service.get_role_users(db, roleId)
    result['userCount'] = len(users)
    
    return result

@router.get("/permissions")
def get_permissions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all permissions"""
    service = PermissionService()
    skip = (page - 1) * pageSize
    
    permissions = service.get_all(db, skip=skip, limit=pageSize, category=category, status=status)
    
    # Get total count
    all_permissions = service.get_all(db, category=category, status=status)
    total = len(all_permissions)
    
    return {
        "permissions": [model_to_dict(permission) for permission in permissions],
        "total": total,
        "page": page,
        "pageSize": len(permissions),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/sharingrules")
def get_sharing_rules(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    userId: Optional[str] = Query(None),
    clientId: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get client sharing rules"""
    service = SharingRuleService()
    skip = (page - 1) * pageSize
    
    rules = service.get_all(db, skip=skip, limit=pageSize, user_id=userId, client_id=clientId, status=status)
    
    # Get total count
    all_rules = service.get_all(db, user_id=userId, client_id=clientId, status=status)
    total = len(all_rules)
    
    return {
        "sharingRules": [model_to_dict(rule) for rule in rules],
        "total": total,
        "page": page,
        "pageSize": len(rules),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
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
        raise HTTPException(status_code=404, detail=f"Sharing rule {ruleId} not found")
    
    result = model_to_dict(rule)
    
    # Add user details
    if rule.user:
        result['userName'] = f"{rule.user.FirstName} {rule.user.LastName}"
        result['userUsername'] = rule.user.Username
    
    if rule.created_by_user:
        result['createdByName'] = f"{rule.created_by_user.FirstName} {rule.created_by_user.LastName}"
    
    return result

# ============================================================================
# LOGIN MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/logons")
def get_logons(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    userId: Optional[str] = Query(None),
    logonType: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all logons (user and client portal)"""
    service = LogonService()
    skip = (page - 1) * pageSize
    
    logons = service.get_all(db, skip=skip, limit=pageSize, user_id=userId, logon_type=logonType, status=status)
    
    # Apply date filtering if provided
    if startDate or endDate:
        filtered_logons = []
        for logon in logons:
            logon_date = logon.LogonDateTime
            if startDate and logon_date < datetime.fromisoformat(startDate.replace('Z', '+00:00')):
                continue
            if endDate and logon_date > datetime.fromisoformat(endDate.replace('Z', '+00:00')):
                continue
            filtered_logons.append(logon)
        logons = filtered_logons
    
    # Get total count
    all_logons = service.get_all(db, user_id=userId, logon_type=logonType, status=status)
    total = len(all_logons)
    
    return {
        "logons": [model_to_dict(logon) for logon in logons],
        "total": total,
        "page": page,
        "pageSize": len(logons),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
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
        raise HTTPException(status_code=404, detail=f"Logon {logonId} not found")
    
    result = model_to_dict(logon)
    
    # Add user details
    if logon.user:
        result['userName'] = f"{logon.user.FirstName} {logon.user.LastName}"
        result['userUsername'] = logon.user.Username
    
    # Calculate session duration if logged out
    if logon.LogoutDateTime:
        duration = logon.LogoutDateTime - logon.LogonDateTime
        result['calculatedDuration'] = int(duration.total_seconds() / 60)  # Duration in minutes
    
    return result

@router.get("/logons/{logonId}/activity")
def get_logon_activity(
    logonId: str = Path(...),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get logon activity history"""
    service = LogonService()
    logon = service.get_by_id(db, logonId)
    
    if not logon:
        raise HTTPException(status_code=404, detail=f"Logon {logonId} not found")
    
    # For now, just return the logon details
    # In a real system, this might include page views, actions, etc.
    activity = service.get_logon_activity(db, logonId)
    
    return {
        "logonId": logonId,
        "activity": model_to_dict(activity) if activity else None,
        "note": "Detailed activity tracking would require additional Activity model implementation"
    }

# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics/users")
def get_user_analytics(
    groupBy: Optional[str] = Query("status"),
    db: Session = Depends(get_db)
):
    """Get user analytics and statistics"""
    service = UserService()
    
    # Get all users for analytics
    all_users = service.get_all(db, limit=1000)
    
    # Calculate status counts
    status_counts = {}
    office_counts = {}
    recent_login_count = 0
    
    for user in all_users:
        # Status counts
        status = user.Status or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Office counts
        office = user.office.OfficeName if user.office else "Unknown"
        office_counts[office] = office_counts.get(office, 0) + 1
        
        # Recent logins (last 30 days)
        if user.LastLoginDate:
            days_since_login = (datetime.now() - user.LastLoginDate).days
            if days_since_login <= 30:
                recent_login_count += 1
    
    # Role counts
    role_service = RoleService()
    all_roles = role_service.get_all(db, limit=100)
    role_counts = {}
    for role in all_roles:
        users = role_service.get_role_users(db, role.RoleID)
        role_counts[role.RoleName] = len(users)
    
    analytics = {
        "total_users": len(all_users),
        "active_users": status_counts.get("Active", 0),
        "inactive_users": status_counts.get("Inactive", 0),
        "by_status": status_counts,
        "by_office": dict(list(office_counts.items())[:10]),  # Top 10 offices
        "by_role": role_counts,
        "recent_logins": recent_login_count
    }
    
    return analytics

@router.get("/analytics/access")
def get_access_analytics(
    db: Session = Depends(get_db)
):
    """Get access control analytics"""
    role_service = RoleService()
    permission_service = PermissionService()
    sharing_service = SharingRuleService()
    
    # Get all data for analytics
    all_roles = role_service.get_all(db, limit=100)
    all_permissions = permission_service.get_all(db, limit=500)
    all_sharing_rules = sharing_service.get_all(db, limit=1000)
    
    # Permission category counts
    permission_categories = {}
    for permission in all_permissions:
        category = permission.Category or "Unknown"
        permission_categories[category] = permission_categories.get(category, 0) + 1
    
    # Sharing rule status counts
    sharing_status_counts = {}
    for rule in all_sharing_rules:
        status = rule.Status or "Unknown"
        sharing_status_counts[status] = sharing_status_counts.get(status, 0) + 1
    
    analytics = {
        "total_roles": len(all_roles),
        "total_permissions": len(all_permissions),
        "total_sharing_rules": len(all_sharing_rules),
        "active_sharing_rules": sharing_status_counts.get("Active", 0),
        "permissions_by_category": permission_categories,
        "sharing_rules_by_status": sharing_status_counts
    }
    
    return analytics
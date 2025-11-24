# routes/client.py - eMoney Advisor Client & Household Management (Version 2)

from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from database import get_db
from models.client import Client, Contact, Household, Spouse, Relationship
from services.client import (
    ClientService, ContactService, HouseholdService, 
    SpouseService, RelationshipService
)

router = APIRouter(
    tags=["eMoney Client & Household Management"],
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
        # Handle decimal serialization
        elif hasattr(value, '__float__'):
            value = float(value)
        result[column.name] = value
    return result

# ============================================================================
# CLIENT ENDPOINTS
# ============================================================================

@router.get("/clients")
def get_clients(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None),
    advisor: Optional[str] = Query(None),
    office: Optional[str] = Query(None),
    household: Optional[str] = Query(None),
    netWorth: Optional[str] = Query(None),  # e.g., "gt:1000000" for high net worth
    db: Session = Depends(get_db)
):
    """List all clients"""
    service = ClientService()
    skip = (page - 1) * pageSize
    
    # Get clients with basic filtering
    clients = service.get_all(db, skip=skip, limit=pageSize, status=status, advisor_id=advisor)
    
    # Apply additional filtering
    if household:
        clients = [c for c in clients if c.HouseholdID == household]
    if office:
        clients = [c for c in clients if c.OfficeID == office]
    
    # Net worth filtering would require household data
    if netWorth:
        operator, amount = netWorth.split(":", 1) if ":" in netWorth else ("eq", netWorth)
        amount = float(amount)
        filtered_clients = []
        for client in clients:
            if client.household and client.household.NetWorth:
                household_net_worth = float(client.household.NetWorth)
                if operator == "gt" and household_net_worth > amount:
                    filtered_clients.append(client)
                elif operator == "lt" and household_net_worth < amount:
                    filtered_clients.append(client)
                elif operator == "eq" and household_net_worth == amount:
                    filtered_clients.append(client)
        clients = filtered_clients
    
    # Get total count for pagination
    all_clients = service.get_all(db, status=status, advisor_id=advisor)
    total = len(all_clients)
    
    return {
        "clients": [model_to_dict(client) for client in clients],
        "total": total,
        "page": page,
        "pageSize": len(clients),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/clients/{clientId}")
def get_client(
    clientId: str = Path(...),
    includeHousehold: bool = Query(False),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get specific client"""
    service = ClientService()
    client = service.get_by_id(db, clientId, include_household=includeHousehold)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {clientId} not found")
    
    result = model_to_dict(client)
    
    # Handle includeHousehold parameter
    if includeHousehold and client.household:
        result['household'] = model_to_dict(client.household)
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'household' in includes and not includeHousehold and client.household:
            result['household'] = model_to_dict(client.household)
        
        if 'spouse' in includes and client.spouse:
            result['spouse'] = model_to_dict(client.spouse)
        
        if 'contacts' in includes:
            contact_service = ContactService()
            contacts = contact_service.get_client_contacts(db, clientId)
            result['contacts'] = [model_to_dict(c) for c in contacts]
        
        if 'relationships' in includes:
            relationship_service = RelationshipService()
            relationships = relationship_service.get_client_relationships(db, clientId)
            result['relationships'] = [model_to_dict(r) for r in relationships]
        
        # Placeholder for future versions
        if 'accounts' in includes:
            result['accounts'] = []  # Version 4
        
        if 'goals' in includes:
            result['goals'] = []  # Version 3
        
        if 'policies' in includes:
            result['policies'] = []  # Version 8
        
        if 'documents' in includes:
            result['documents'] = []  # Version 10
    
    return result

@router.get("/clients/{clientId}/household")
def get_client_household(
    clientId: str = Path(...),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get client household"""
    service = ClientService()
    client = service.get_by_id(db, clientId)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {clientId} not found")
    
    household_service = HouseholdService()
    household = household_service.get_by_id(db, client.HouseholdID) if client.HouseholdID else None
    
    if not household:
        raise HTTPException(status_code=404, detail=f"No household found for client {clientId}")
    
    result = model_to_dict(household)
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'members' in includes:
            members = household_service.get_household_members(db, household.HouseholdID)
            result['members'] = [model_to_dict(m) for m in members]
        
        # Placeholder for future versions
        if 'accounts' in includes:
            result['accounts'] = []  # Version 4
        
        if 'assets' in includes:
            result['assets'] = []  # Version 4
        
        if 'liabilities' in includes:
            result['liabilities'] = []  # Version 4
        
        if 'networth' in includes:
            result['netWorthCalculated'] = float(household.NetWorth) if household.NetWorth else 0
    
    return result

@router.get("/clients/{clientId}/spouse")
def get_client_spouse(
    clientId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get client spouse"""
    service = ClientService()
    client = service.get_by_id(db, clientId)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {clientId} not found")
    
    spouse_service = SpouseService()
    spouse = spouse_service.get_by_client_id(db, clientId)
    
    if not spouse:
        raise HTTPException(status_code=404, detail=f"No spouse found for client {clientId}")
    
    return model_to_dict(spouse)

@router.get("/clients/search")
def search_clients(
    firstName: Optional[str] = Query(None),
    lastName: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    q: Optional[str] = Query(None),  # General search term
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Search clients"""
    service = ClientService()
    
    if q:
        # General search - search across multiple fields
        clients = service.search_clients(
            db, first_name=q, last_name=q, email=q, limit=limit
        )
    elif firstName or lastName or email:
        # Specific field search
        clients = service.search_clients(
            db, first_name=firstName, last_name=lastName, 
            email=email, limit=limit
        )
    else:
        raise HTTPException(status_code=400, detail="At least one search parameter is required")
    
    return {
        "clients": [model_to_dict(c) for c in clients],
        "total": len(clients),
        "searchParams": {
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "q": q
        }
    }

# ============================================================================
# HOUSEHOLD ENDPOINTS
# ============================================================================

@router.get("/households/{householdId}")
def get_household(
    householdId: str = Path(...),
    include: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get specific household"""
    service = HouseholdService()
    household = service.get_by_id(db, householdId)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {householdId} not found")
    
    result = model_to_dict(household)
    
    # Handle include parameter
    if include:
        includes = [i.strip().lower() for i in include.split(',')]
        
        if 'members' in includes:
            members = service.get_household_members(db, householdId)
            result['members'] = [model_to_dict(m) for m in members]
        
        # Placeholder for future versions
        if 'accounts' in includes:
            result['accounts'] = []  # Version 4
        
        if 'assets' in includes:
            result['assets'] = []  # Version 4
        
        if 'liabilities' in includes:
            result['liabilities'] = []  # Version 4
        
        if 'networth' in includes:
            result['netWorthCalculated'] = float(household.NetWorth) if household.NetWorth else 0
    
    return result

@router.get("/households/{householdId}/members")
def get_household_members(
    householdId: str = Path(...),
    includeSpouses: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get household members"""
    service = HouseholdService()
    household = service.get_by_id(db, householdId)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {householdId} not found")
    
    members = service.get_household_members(db, householdId)
    
    result = {
        "householdId": householdId,
        "members": [model_to_dict(m) for m in members],
        "total": len(members)
    }
    
    # Include spouse information if requested
    if includeSpouses:
        spouse_service = SpouseService()
        for i, member in enumerate(members):
            spouse = spouse_service.get_by_client_id(db, member.ClientID)
            if spouse:
                result["members"][i]["spouse"] = model_to_dict(spouse)
    
    return result

@router.get("/households/{householdId}/networth")
def get_household_networth(
    householdId: str = Path(...),
    asOfDate: Optional[str] = Query(None),
    includeBreakdown: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get household net worth"""
    service = HouseholdService()
    household = service.get_by_id(db, householdId)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {householdId} not found")
    
    net_worth = float(household.NetWorth) if household.NetWorth else 0
    
    result = {
        "householdId": householdId,
        "netWorth": net_worth,
        "asOfDate": asOfDate or datetime.now().isoformat()
    }
    
    if includeBreakdown:
        # Placeholder for detailed breakdown - would need Account/Asset data
        result["breakdown"] = {
            "totalAssets": 0,  # Would come from Version 4
            "totalLiabilities": 0,  # Would come from Version 4
            "netWorth": net_worth,
            "note": "Detailed breakdown requires Account & Asset data (Version 4)"
        }
    
    return result

# ============================================================================
# SPOUSE ENDPOINTS
# ============================================================================

@router.get("/spouse/{spouseId}")
def get_spouse(
    spouseId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get spouse details"""
    service = SpouseService()
    spouse = service.get_by_id(db, spouseId)
    
    if not spouse:
        raise HTTPException(status_code=404, detail=f"Spouse {spouseId} not found")
    
    result = model_to_dict(spouse)
    
    # Include client information
    if spouse.client:
        result['clientName'] = f"{spouse.client.FirstName} {spouse.client.LastName}"
        result['clientId'] = spouse.client.ClientID
    
    return result

# ============================================================================
# CONTACT ENDPOINTS
# ============================================================================

@router.get("/contacts")
def get_contacts(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    clientId: Optional[str] = Query(None),
    contactType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all contacts"""
    service = ContactService()
    skip = (page - 1) * pageSize
    
    contacts = service.get_all(
        db, skip=skip, limit=pageSize,
        client_id=clientId, contact_type=contactType, status=status
    )
    
    # Get total count
    all_contacts = service.get_all(db, client_id=clientId, contact_type=contactType, status=status)
    total = len(all_contacts)
    
    return {
        "contacts": [model_to_dict(contact) for contact in contacts],
        "total": total,
        "page": page,
        "pageSize": len(contacts),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/contacts/{contactId}")
def get_contact(
    contactId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific contact"""
    service = ContactService()
    contact = service.get_by_id(db, contactId)
    
    if not contact:
        raise HTTPException(status_code=404, detail=f"Contact {contactId} not found")
    
    result = model_to_dict(contact)
    
    # Include client information
    if contact.client:
        result['clientName'] = f"{contact.client.FirstName} {contact.client.LastName}"
    
    return result

# ============================================================================
# RELATIONSHIP ENDPOINTS
# ============================================================================

@router.get("/relationships")
def get_relationships(
    page: int = Query(1, ge=1),
    pageSize: int = Query(100, ge=1, le=500),
    clientId: Optional[str] = Query(None),
    relationshipType: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all relationships"""
    service = RelationshipService()
    skip = (page - 1) * pageSize
    
    relationships = service.get_all(
        db, skip=skip, limit=pageSize,
        client_id=clientId, relationship_type=relationshipType, status=status
    )
    
    # Get total count
    all_relationships = service.get_all(db, client_id=clientId, relationship_type=relationshipType, status=status)
    total = len(all_relationships)
    
    return {
        "relationships": [model_to_dict(rel) for rel in relationships],
        "total": total,
        "page": page,
        "pageSize": len(relationships),
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/relationships/{relationshipId}")
def get_relationship(
    relationshipId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get specific relationship"""
    service = RelationshipService()
    relationship = service.get_by_id(db, relationshipId)
    
    if not relationship:
        raise HTTPException(status_code=404, detail=f"Relationship {relationshipId} not found")
    
    result = model_to_dict(relationship)
    
    # Include client names
    if relationship.client:
        result['clientName'] = f"{relationship.client.FirstName} {relationship.client.LastName}"
    if relationship.related_client:
        result['relatedClientName'] = f"{relationship.related_client.FirstName} {relationship.related_client.LastName}"
    
    return result

# ============================================================================
# ANALYTICS & REPORTING ENDPOINTS
# ============================================================================

@router.get("/analytics/clients")
def get_client_analytics(
    groupBy: Optional[str] = Query("status"),
    db: Session = Depends(get_db)
):
    """Get client analytics and statistics"""
    service = ClientService()
    
    # Get all clients for analytics
    all_clients = service.get_all(db, limit=1000)
    
    # Calculate status counts
    status_counts = {}
    marital_status_counts = {}
    advisor_counts = {}
    office_counts = {}
    spouse_count = 0
    
    for client in all_clients:
        # Status counts
        status = client.Status or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Marital status counts
        marital = client.MaritalStatus or "Unknown"
        marital_status_counts[marital] = marital_status_counts.get(marital, 0) + 1
        
        # Advisor counts
        advisor = client.AdvisorID or "Unknown"
        advisor_counts[advisor] = advisor_counts.get(advisor, 0) + 1
        
        # Office counts
        office = client.OfficeID or "Unknown"
        office_counts[office] = office_counts.get(office, 0) + 1
        
        # Spouse count
        if client.SpouseID:
            spouse_count += 1
    
    # High net worth calculation (simplified)
    household_service = HouseholdService()
    high_net_worth_households = household_service.get_all(db, min_net_worth=1000000, limit=1000)
    
    analytics = {
        "total_clients": len(all_clients),
        "active_clients": status_counts.get("Active", 0),
        "inactive_clients": status_counts.get("Inactive", 0),
        "by_status": status_counts,
        "by_marital_status": marital_status_counts,
        "by_advisor": dict(list(advisor_counts.items())[:10]),  # Top 10
        "by_office": dict(list(office_counts.items())[:10]),    # Top 10
        "high_net_worth_households": len(high_net_worth_households),
        "with_spouse": spouse_count
    }
    
    return analytics

@router.get("/analytics/households")
def get_household_analytics(
    db: Session = Depends(get_db)
):
    """Get household analytics"""
    service = HouseholdService()
    
    # Get all households for analytics
    all_households = service.get_all(db, limit=1000)
    
    # Calculate statistics
    active_households = [h for h in all_households if h.Status == "Active"]
    net_worths = [float(h.NetWorth) for h in all_households if h.NetWorth and float(h.NetWorth) > 0]
    
    # Risk tolerance counts
    risk_tolerance_counts = {}
    for household in all_households:
        risk = household.RiskTolerance or "Unknown"
        risk_tolerance_counts[risk] = risk_tolerance_counts.get(risk, 0) + 1
    
    # Net worth calculations
    total_net_worth = sum(net_worths)
    average_net_worth = total_net_worth / len(net_worths) if net_worths else 0
    median_net_worth = sorted(net_worths)[len(net_worths)//2] if net_worths else 0
    
    # Net worth distribution
    distribution = {
        "under_100k": len([nw for nw in net_worths if nw < 100000]),
        "100k_500k": len([nw for nw in net_worths if 100000 <= nw < 500000]),
        "500k_1m": len([nw for nw in net_worths if 500000 <= nw < 1000000]),
        "1m_5m": len([nw for nw in net_worths if 1000000 <= nw < 5000000]),
        "over_5m": len([nw for nw in net_worths if nw >= 5000000])
    }
    
    analytics = {
        "total_households": len(all_households),
        "active_households": len(active_households),
        "average_net_worth": average_net_worth,
        "median_net_worth": median_net_worth,
        "total_net_worth": total_net_worth,
        "net_worth_distribution": distribution,
        "by_risk_tolerance": risk_tolerance_counts
    }
    
    return analytics

# ============================================================================
# COMPLEX DATA EXTRACTION ENDPOINTS
# ============================================================================

@router.get("/clients/{clientId}/complete-profile")
def get_client_complete_profile(
    clientId: str = Path(...),
    db: Session = Depends(get_db)
):
    """Get complete client profile with all related data"""
    service = ClientService()
    client = service.get_by_id(db, clientId, include_household=True)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {clientId} not found")
    
    result = model_to_dict(client)
    
    # Include all related data
    if client.household:
        result['household'] = model_to_dict(client.household)
        # Get household members
        household_service = HouseholdService()
        members = household_service.get_household_members(db, client.HouseholdID)
        result['household']['members'] = [model_to_dict(m) for m in members]
    
    if client.spouse:
        result['spouse'] = model_to_dict(client.spouse)
    
    # Get contacts
    contact_service = ContactService()
    contacts = contact_service.get_client_contacts(db, clientId)
    result['contacts'] = [model_to_dict(c) for c in contacts]
    
    # Get relationships
    relationship_service = RelationshipService()
    relationships = relationship_service.get_client_relationships(db, clientId)
    result['relationships'] = [model_to_dict(r) for r in relationships]
    
    # Placeholder for future versions
    result['accounts'] = []    # Version 4
    result['goals'] = []       # Version 3
    result['policies'] = []    # Version 8
    result['documents'] = []   # Version 10
    
    return result

@router.get("/households/{householdId}/financial-summary")
def get_household_financial_summary(
    householdId: str = Path(...),
    includeProjections: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get comprehensive household financial summary"""
    service = HouseholdService()
    household = service.get_by_id(db, householdId)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {householdId} not found")
    
    result = model_to_dict(household)
    
    # Get all members
    members = service.get_household_members(db, householdId)
    result['members'] = [model_to_dict(m) for m in members]
    
    # Calculate net worth
    result['netWorthCalculated'] = float(household.NetWorth) if household.NetWorth else 0
    result['netWorthBreakdown'] = {
        "totalAssets": 0,      # Would come from Version 4
        "totalLiabilities": 0, # Would come from Version 4
        "netWorth": float(household.NetWorth) if household.NetWorth else 0
    }
    
    # Placeholder for future versions
    result['accounts'] = []      # Version 4
    result['assets'] = []        # Version 4
    result['liabilities'] = []   # Version 4
    result['cashFlow'] = {}      # Version 3
    result['goals'] = []         # Version 3
    
    if includeProjections:
        # This would require Version 3 (Financial Planning)
        result['projections'] = {
            "note": "Financial projections require Financial Planning data (Version 3)"
        }
    
    return result
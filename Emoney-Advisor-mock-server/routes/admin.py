# routes/admin.py - Admin Endpoints for Database Management

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from services.admin import AdminService
from database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/seed", summary="Seed Database with Test Data")
async def seed_database(
    entity_type: str = Query(
        default="all", 
        description="Type of entities to seed: all, identity, clients, financial, accounts, assets"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Seed the database with test data.
    
    **Entity Types:**
    - `all`: Seed all entities across all versions
    - `identity`: V1 - Users, Offices, Roles, Permissions, etc.
    - `clients`: V2 - Clients, Households, Spouses, Contacts, etc.
    - `financial`: V3 - Financial Plans, Goals, Scenarios, etc.
    - `accounts`: V4 - Account Types, Accounts
    - `assets`: V4 - Asset Classes, Assets, Liabilities
    
    **Example:**
    ```
    POST /admin/seed?entity_type=all
    ```
    
    Returns seeding results including counts for each entity type.
    """
    valid_types = ["all", "identity", "clients", "financial", "accounts", "assets"]
    
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity_type: {entity_type}. Valid options: {', '.join(valid_types)}"
        )
    
    admin_service = AdminService(db)
    result = admin_service.seed_database(entity_type)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.post("/seed/version/{version}", summary="Seed Database by Version")
async def seed_version(
    version: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Seed the database with test data for a specific version.
    
    **Versions:**
    - `v1`: Identity & Access Management
    - `v2`: Client & Household Management
    - `v3`: Financial Planning Core
    - `v4`: Account & Asset Management
    - `all`: All versions
    
    **Example:**
    ```
    POST /admin/seed/version/v2
    ```
    
    Returns seeding results for the specified version.
    """
    valid_versions = ["v1", "v2", "v3", "v4", "all"]
    
    if version not in valid_versions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid version: {version}. Valid versions: {', '.join(valid_versions)}"
        )
    
    admin_service = AdminService(db)
    result = admin_service.seed_version(version)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.post("/reset", summary="Reset Database (Drop & Recreate All Tables)")
async def reset_database(
    confirm: bool = Query(
        default=False,
        description="Must be true to confirm database reset (DESTRUCTIVE OPERATION)"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    **⚠️ DESTRUCTIVE OPERATION ⚠️**
    
    Drop all tables and recreate them. This will DELETE ALL DATA in the database!
    
    **Parameters:**
    - `confirm`: Must be set to `true` to execute
    
    **Example:**
    ```
    POST /admin/reset?confirm=true
    ```
    
    Use this for complete database reinitialization during development/testing.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Database reset requires confirmation. Set confirm=true to proceed."
        )
    
    admin_service = AdminService(db)
    result = admin_service.reset_database()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.get("/status", summary="Get Database Status")
async def get_database_status(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive database status including table counts and statistics.
    
    **Returns:**
    - Total tables and their names
    - Record counts by table
    - Record counts by version
    - Overall statistics
    
    **Example:**
    ```
    GET /admin/status
    ```
    """
    admin_service = AdminService(db)
    result = admin_service.get_database_status()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.get("/verify", summary="Verify Seeding Results")
async def verify_seeding(
    version: Optional[str] = Query(
        default=None,
        description="Specific version to verify (v1, v2, v3, v4) or None for all"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify that database seeding was successful by comparing actual vs expected counts.
    
    **Parameters:**
    - `version`: Optional version filter (v1, v2, v3, v4)
    
    **Examples:**
    ```
    GET /admin/verify              # Verify all versions
    GET /admin/verify?version=v2   # Verify V2 only
    ```
    
    Returns verification results showing expected vs actual counts for each table.
    """
    if version and version not in ["v1", "v2", "v3", "v4"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid version: {version}. Valid versions: v1, v2, v3, v4"
        )
    
    admin_service = AdminService(db)
    result = admin_service.verify_seeding(version)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.delete("/truncate", summary="Truncate All Tables")
async def truncate_all_tables(
    confirm: bool = Query(
        default=False,
        description="Must be true to confirm table truncation (DESTRUCTIVE OPERATION)"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    **⚠️ DESTRUCTIVE OPERATION ⚠️**
    
    Truncate all tables (delete all data but keep table structure).
    Faster than reset for testing purposes.
    
    **Parameters:**
    - `confirm`: Must be set to `true` to execute
    
    **Example:**
    ```
    DELETE /admin/truncate?confirm=true
    ```
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Table truncation requires confirmation. Set confirm=true to proceed."
        )
    
    admin_service = AdminService(db)
    result = admin_service.truncate_all_tables()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.delete("/truncate/version/{version}", summary="Truncate Version Tables")
async def truncate_version_tables(
    version: str,
    confirm: bool = Query(
        default=False,
        description="Must be true to confirm table truncation (DESTRUCTIVE OPERATION)"
    ),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    **⚠️ DESTRUCTIVE OPERATION ⚠️**
    
    Truncate tables for a specific version only.
    
    **Parameters:**
    - `version`: Version to truncate (v1, v2, v3, v4)
    - `confirm`: Must be set to `true` to execute
    
    **Example:**
    ```
    DELETE /admin/truncate/version/v2?confirm=true
    ```
    """
    valid_versions = ["v1", "v2", "v3", "v4"]
    
    if version not in valid_versions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid version: {version}. Valid versions: {', '.join(valid_versions)}"
        )
    
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Table truncation requires confirmation. Set confirm=true to proceed."
        )
    
    admin_service = AdminService(db)
    result = admin_service.truncate_version_tables(version)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.get("/table/{table_name}", summary="Get Table Information")
async def get_table_info(
    table_name: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific table.
    
    **Parameters:**
    - `table_name`: Name of the table to inspect
    
    **Returns:**
    - Table structure (columns, types, constraints)
    - Foreign key relationships
    - Indexes
    - Record count
    
    **Example:**
    ```
    GET /admin/table/clients
    ```
    """
    admin_service = AdminService(db)
    result = admin_service.get_table_info(table_name)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result)
    
    return result


@router.get("/summary", summary="Get Version Implementation Summary")
async def get_version_summary(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get summary of implementation status for all versions.
    
    **Returns:**
    - Implementation status for each version
    - Table counts and record counts
    - Missing tables
    - Overall system status
    
    **Example:**
    ```
    GET /admin/summary
    ```
    
    Useful for checking which versions are fully implemented and seeded.
    """
    admin_service = AdminService(db)
    result = admin_service.get_version_summary()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    
    return result


@router.get("/health", summary="Admin Health Check")
async def admin_health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint for the admin service.
    
    **Example:**
    ```
    GET /admin/health
    ```
    
    Returns basic system information and timestamp.
    """
    return {
        "status": "healthy",
        "service": "eMoney Mock Server Admin",
        "version": "1.0.0",
        "features": [
            "Database seeding (V1-V4)",
            "Database reset & truncation",
            "Table inspection",
            "Verification & status checks"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# Additional utility endpoints
@router.get("/tables", summary="List All Tables")
async def list_all_tables(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a list of all tables in the database.
    
    **Example:**
    ```
    GET /admin/tables
    ```
    
    Returns sorted list of table names.
    """
    try:
        from sqlalchemy import inspect
        from database import engine
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        return {
            "status": "success",
            "total_tables": len(tables),
            "tables": sorted(tables),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to list tables",
                "error": str(e)
            }
        )
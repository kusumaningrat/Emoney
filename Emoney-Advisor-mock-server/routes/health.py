# routes/health.py - Health Check Endpoints

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from datetime import datetime
import time

from database import get_db, engine

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Basic Health Check")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint that returns system status and information.
    
    **Returns:**
    - Service status
    - Current timestamp
    - Version information
    - Available features
    
    **Example:**
    ```
    GET /health
    ```
    """
    return {
        "status": "healthy",
        "service": "eMoney Advisor Mock Server",
        "version": "1.0.0",
        "environment": "development",
        "features": {
            "v1_identity": "Identity & Access Management",
            "v2_clients": "Client & Household Management", 
            "v3_financial": "Financial Planning Core",
            "v4_accounts_assets": "Account & Asset Management"
        },
        "endpoints": {
            "entity_api": "/docs - Swagger documentation",
            "admin_api": "/admin/* - Database management",
            "health_api": "/health/* - Health monitoring"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "Service is running"
    }


@router.get("/health/detailed", summary="Detailed Health Check")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Detailed health check that includes database connectivity and basic statistics.
    
    **Returns:**
    - Service status
    - Database connectivity
    - Basic table counts
    - Performance metrics
    
    **Example:**
    ```
    GET /health/detailed
    ```
    """
    start_time = time.time()
    
    # Test database connectivity
    db_status = "unknown"
    db_error = None
    table_count = 0
    
    try:
        # Simple database query to test connectivity
        result = db.execute(text("SELECT 1"))
        db_status = "connected"
        
        # Get table count
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        table_count = len(tables)
        
    except Exception as e:
        db_status = "error"
        db_error = str(e)
    
    # Calculate response time
    response_time_ms = round((time.time() - start_time) * 1000, 2)
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "service": "eMoney Advisor Mock Server",
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "error": db_error,
            "total_tables": table_count,
            "connection_time_ms": response_time_ms
        },
        "performance": {
            "response_time_ms": response_time_ms,
            "database_query_time_ms": response_time_ms if db_status == "connected" else None
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/database", summary="Database Health Check")
async def database_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive database health check with table counts and connection status.
    
    **Returns:**
    - Database connection status
    - Table counts by version
    - Connection performance metrics
    - Recent activity indicators
    
    **Example:**
    ```
    GET /health/database
    ```
    """
    start_time = time.time()
    
    try:
        # Test basic connectivity
        db.execute(text("SELECT 1"))
        
        # Get table information
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # Count records in key tables
        table_counts = {}
        version_counts = {
            "v1_identity": 0,
            "v2_clients": 0, 
            "v3_financial": 0,
            "v4_accounts_assets": 0
        }
        
        # Version table mappings
        version_tables = {
            "v1_identity": ["users", "offices", "roles", "permissions", "sharing_rules", "logons"],
            "v2_clients": ["clients", "households", "spouses", "contacts", "relationships"],
            "v3_financial": ["financial_plans", "goals", "scenarios", "cash_flows", "net_worths"],
            "v4_accounts_assets": ["accounts", "account_types", "assets", "asset_classes", "liabilities"]
        }
        
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_counts[table] = count
                
                # Add to version totals
                for version, version_table_list in version_tables.items():
                    if table in version_table_list:
                        version_counts[version] += count
                        
            except Exception as e:
                table_counts[table] = f"Error: {str(e)}"
        
        # Calculate performance metrics
        query_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "database": {
                "connection": "active",
                "total_tables": len(tables),
                "query_time_ms": query_time,
                "version_counts": version_counts,
                "total_records": sum(count for count in table_counts.values() if isinstance(count, int))
            },
            "tables": table_counts,
            "performance": {
                "connection_time_ms": query_time,
                "queries_executed": len(tables) + 1,  # +1 for initial connectivity test
                "avg_query_time_ms": round(query_time / (len(tables) + 1), 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": {
                "connection": "failed",
                "error": str(e),
                "query_time_ms": round((time.time() - start_time) * 1000, 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/versions", summary="Version Status Check")
async def versions_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check implementation and data status for each eMoney version.
    
    **Returns:**
    - Implementation status for each version (V1-V4)
    - Expected vs actual table counts
    - Data completeness indicators
    - Version-specific health metrics
    
    **Example:**
    ```
    GET /health/versions
    ```
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # Version definitions
        versions = {
            "v1": {
                "name": "Identity & Access Management",
                "expected_tables": ["users", "offices", "roles", "permissions", "user_roles", "role_permissions", "sharing_rules", "logons"],
                "expected_records": {"users": 60, "offices": 15, "roles": 10, "permissions": 50, "sharing_rules": 80, "logons": 100}
            },
            "v2": {
                "name": "Client & Household Management",
                "expected_tables": ["clients", "households", "spouses", "contacts", "relationships"],
                "expected_records": {"clients": 250, "households": 150, "spouses": 180, "contacts": 100, "relationships": 120}
            },
            "v3": {
                "name": "Financial Planning Core",
                "expected_tables": ["financial_plans", "goals", "scenarios", "cash_flows", "net_worths"],
                "expected_records": {"financial_plans": 200, "goals": 800, "scenarios": 150, "cash_flows": 200, "net_worths": 200}
            },
            "v4": {
                "name": "Account & Asset Management",
                "expected_tables": ["account_types", "accounts", "asset_classes", "assets", "liabilities"],
                "expected_records": {"account_types": 15, "accounts": 500, "asset_classes": 12, "assets": 800, "liabilities": 300}
            }
        }
        
        version_status = {}
        overall_health = "healthy"
        
        for version_id, version_info in versions.items():
            expected_tables = set(version_info["expected_tables"])
            implemented_tables = expected_tables.intersection(existing_tables)
            missing_tables = expected_tables - existing_tables
            
            # Check record counts for implemented tables
            record_counts = {}
            total_records = 0
            data_health = "good"
            
            for table in implemented_tables:
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    record_counts[table] = count
                    total_records += count
                    
                    # Check if count is reasonable (at least 10% of expected)
                    expected = version_info["expected_records"].get(table, 0)
                    if expected > 0 and count < (expected * 0.1):
                        data_health = "low_data"
                        
                except Exception as e:
                    record_counts[table] = f"Error: {str(e)}"
                    data_health = "error"
            
            # Determine version status
            if len(implemented_tables) == len(expected_tables):
                if data_health == "good":
                    version_health = "healthy"
                elif data_health == "low_data":
                    version_health = "healthy_low_data"
                else:
                    version_health = "unhealthy"
            else:
                version_health = "incomplete"
                overall_health = "degraded"
            
            version_status[version_id] = {
                "name": version_info["name"],
                "status": version_health,
                "implementation": {
                    "tables_implemented": len(implemented_tables),
                    "tables_expected": len(expected_tables),
                    "completion_percentage": round(len(implemented_tables) / len(expected_tables) * 100, 1),
                    "missing_tables": list(missing_tables)
                },
                "data": {
                    "health": data_health,
                    "total_records": total_records,
                    "expected_total": sum(version_info["expected_records"].values()),
                    "record_counts": record_counts
                }
            }
        
        return {
            "status": overall_health,
            "versions": version_status,
            "summary": {
                "total_versions": len(versions),
                "healthy_versions": sum(1 for v in version_status.values() if v["status"] == "healthy"),
                "total_tables_expected": sum(len(v["expected_tables"]) for v in versions.values()),
                "total_tables_implemented": len(existing_tables),
                "total_records": sum(v["data"]["total_records"] for v in version_status.values())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/ready", summary="Readiness Check")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Kubernetes-style readiness check for load balancer health probes.
    
    **Returns:**
    - Simple ready/not_ready status
    - Minimal response for high-frequency health checks
    
    **Example:**
    ```
    GET /health/ready
    ```
    
    Returns HTTP 200 if ready, HTTP 503 if not ready.
    """
    try:
        # Quick database connectivity test
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Return 503 Service Unavailable for readiness failures
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/health/live", summary="Liveness Check")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes-style liveness check for container health monitoring.
    
    **Returns:**
    - Simple alive status
    - No external dependencies checked
    
    **Example:**
    ```
    GET /health/live
    ```
    
    Always returns HTTP 200 unless the application is completely unresponsive.
    """
    return {
        "status": "alive",
        "service": "eMoney Advisor Mock Server",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/metrics", summary="Performance Metrics")
async def performance_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Basic performance metrics for monitoring and alerting.
    
    **Returns:**
    - Response time metrics
    - Database performance indicators
    - System resource information
    
    **Example:**
    ```
    GET /health/metrics
    ```
    """
    start_time = time.time()
    
    try:
        # Test database performance with multiple queries
        db_start = time.time()
        
        # Simple query
        db.execute(text("SELECT 1"))
        simple_query_time = (time.time() - db_start) * 1000
        
        # Count query
        count_start = time.time()
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        count_query_time = (time.time() - count_start) * 1000
        
        # Join query simulation (if tables exist)
        join_start = time.time()
        try:
            db.execute(text("SELECT COUNT(*) FROM clients c LEFT JOIN households h ON c.household_id = h.household_id"))
            join_query_time = (time.time() - join_start) * 1000
        except:
            join_query_time = None
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",
            "performance": {
                "total_response_time_ms": round(total_time, 2),
                "database_metrics": {
                    "simple_query_ms": round(simple_query_time, 2),
                    "count_query_ms": round(count_query_time, 2),
                    "join_query_ms": round(join_query_time, 2) if join_query_time else None,
                    "connection_healthy": True
                },
                "sample_data": {
                    "user_count": user_count
                }
            },
            "thresholds": {
                "response_time_warning_ms": 1000,
                "response_time_critical_ms": 5000,
                "db_query_warning_ms": 500,
                "db_query_critical_ms": 2000
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        
        return {
            "status": "degraded",
            "performance": {
                "total_response_time_ms": round(total_time, 2),
                "database_metrics": {
                    "connection_healthy": False,
                    "error": str(e)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
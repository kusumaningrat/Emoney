# app.py - Main FastAPI Application Entry Point

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime

# Database setup
from database import engine, Base, get_db

# Import all models to ensure they're registered
from models import identity, client, financial, account, asset

# Import routers - UPDATED: Remove prefix from router includes
from routes.identity import router as identity_router
from routes.client import router as client_router
from routes.financial import router as financial_router
from routes.account import router as account_router
from routes.asset import router as asset_router
from routes.admin import router as admin_router
from routes.health import router as health_router

# Create FastAPI application
app = FastAPI(
    title="eMoney Advisor Mock Server",
    description="""
    A comprehensive mock server implementation of the eMoney Advisor API for development and testing.
    
    ## Features
    
    ### Version 1: Identity & Access Management
    - User management and authentication
    - Office hierarchy and organization
    - Role-based access control (RBAC)
    - Permission management
    - Client delegation and sharing rules
    - Session and logon tracking
    
    ### Version 2: Client & Household Management
    - Individual client profiles
    - Household groupings and relationships
    - Spouse and family member tracking
    - Contact information management
    - Business and family relationships
    
    ### Version 3: Financial Planning Core
    - Comprehensive financial plans
    - Goal setting and tracking
    - Scenario modeling and analysis
    - Cash flow projections
    - Net worth calculations
    
    ### Version 4: Account & Asset Management
    - Financial account management
    - Investment holdings and assets
    - Asset classification and performance
    - Liability tracking
    - Portfolio analysis
    
    ## Mock Data
    
    The server includes realistic mock data across all versions:
    - **V1**: 265 identity records (60 users, 15 offices, etc.)
    - **V2**: 800 client records (250 clients, 150 households, etc.)
    - **V3**: 1,350 financial records (200 plans, 800 goals, etc.)
    - **V4**: 1,627 account records (500 accounts, 800 assets, etc.)
    
    ## API Documentation
    
    - **Entity API**: All business entity endpoints
    - **Admin API**: Database management and seeding
    - **Health API**: Service monitoring and diagnostics
    
    ## Quick Start
    
    1. **Seed the database**: `POST /admin/seed?entity_type=all`
    2. **Check status**: `GET /admin/status`
    3. **List users**: `GET /users`
    4. **List clients**: `GET /clients`
    5. **Health check**: `GET /health`
    
    ## Authentication
    
    This mock server implements OAuth 2.0 with JWT tokens for compatibility with the real eMoney API.
    Authentication is optional for development but can be enabled for production-like testing.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "eMoney Mock Server Support",
        "url": "https://github.com/your-org/emoney-mock-server",
        "email": "support@example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - UPDATED: Removed /emoney/api/v1 prefix to match eMoney documentation
app.include_router(identity_router)
app.include_router(client_router)
app.include_router(financial_router)
app.include_router(account_router)
app.include_router(asset_router)
# Keep admin and health endpoints with prefix for server management
app.include_router(admin_router, prefix="/admin")
app.include_router(health_router, prefix="/health")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    Creates database tables and performs initial setup.
    """
    print("🚀 Starting eMoney Advisor Mock Server...")
    
    try:
        # Create all tables
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Log available endpoints
        print("✅ Database tables created successfully")
        print("📚 API Documentation available at: /docs")
        print("🔧 Admin endpoints available at: /admin/*")
        print("💓 Health checks available at: /health/*")
        print("👥 Identity endpoints available at: /users, /offices")
        print("🏠 Client endpoints available at: /clients, /households")
        print("📊 Financial endpoints available at: /plans, /goals")
        print("💰 Account endpoints available at: /accounts, /assets")
        
        print("🎉 eMoney Mock Server started successfully!")
        
    except Exception as e:
        print(f"❌ Error during startup: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    Performs cleanup operations.
    """
    print("🛑 Shutting down eMoney Advisor Mock Server...")
    print("👋 Goodbye!")


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    return RedirectResponse(url="/docs")


@app.get("/api-info", tags=["Root"], summary="API Information")
async def api_info():
    """
    Get information about this API and available endpoints.
    
    **Returns:**
    - API version information
    - Available endpoint categories
    - Quick start guide
    - Feature summary
    """
    return {
        "api_version": "1.0",
        "service": "eMoney Advisor Mock Server",
        "description": "Mock implementation of eMoney Advisor API for development and testing",
        "base_url": "/",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        },
        "endpoints": {
            "identity": {
                "description": "V1 - Identity & Access Management",
                "examples": [
                    "GET /users",
                    "GET /offices",
                    "GET /roles",
                    "GET /permissions"
                ]
            },
            "clients": {
                "description": "V2 - Client & Household Management",
                "examples": [
                    "GET /clients",
                    "GET /households/{householdId}",
                    "GET /contacts",
                    "GET /relationships"
                ]
            },
            "financial": {
                "description": "V3 - Financial Planning Core",
                "examples": [
                    "GET /plans/{planId}",
                    "GET /goals",
                    "GET /scenarios/{scenarioId}",
                    "GET /cashflow/{planId}"
                ]
            },
            "accounts": {
                "description": "V4a - Account Management",
                "examples": [
                    "GET /accounts",
                    "GET /accounts/{accountId}/holdings",
                    "GET /account-types"
                ]
            },
            "assets": {
                "description": "V4b - Asset Management",
                "examples": [
                    "GET /assets",
                    "GET /assetclasses",
                    "GET /liabilities"
                ]
            },
            "admin": {
                "description": "Database management and seeding",
                "examples": [
                    "POST /admin/seed",
                    "GET /admin/status",
                    "POST /admin/reset"
                ]
            },
            "health": {
                "description": "Service monitoring and diagnostics", 
                "examples": [
                    "GET /health",
                    "GET /health/detailed",
                    "GET /health/database"
                ]
            }
        },
        "versions": {
            "v1": "Identity & Access Management (users, offices, roles)",
            "v2": "Client & Household Management (clients, households, spouses)",
            "v3": "Financial Planning Core (plans, goals, scenarios)", 
            "v4": "Account & Asset Management (accounts, assets, liabilities)"
        },
        "quick_start": [
            "1. Seed database: POST /admin/seed?entity_type=all",
            "2. Check status: GET /admin/status", 
            "3. List users: GET /users",
            "4. List clients: GET /clients",
            "5. List accounts: GET /accounts"
        ],
        "authentication": {
            "type": "OAuth 2.0 with JWT",
            "endpoint": "https://signin.emoneyadvisor.com/connect/token",
            "note": "Authentication is optional for development mode"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# Global exception handler for better error responses
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler with helpful information."""
    return {
        "error": "Not Found",
        "message": "The requested endpoint was not found",
        "suggestion": "Check /docs for available endpoints",
        "request_path": str(request.url.path),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler for internal server errors."""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "suggestion": "Check /health for service status",
        "timestamp": datetime.utcnow().isoformat()
    }


# Custom middleware for request logging (optional)
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Optional request logging middleware.
    Enable this in production for monitoring and debugging.
    """
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log request info (customize as needed)
    if not request.url.path.startswith("/docs") and not request.url.path.startswith("/openapi.json"):
        print(f"📝 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response


# Development server configuration
if __name__ == "__main__":
    print("🔧 Starting development server...")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🏥 Health Check: http://localhost:8080/health")
    print("⚙️  Admin Panel: http://localhost:8080/admin/status")
    print("👥 Users API: http://localhost:8080/users")
    print("🏠 Clients API: http://localhost:8080/clients")
    print("💰 Accounts API: http://localhost:8080/accounts")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload for development
        log_level="info",
        access_log=True
    )
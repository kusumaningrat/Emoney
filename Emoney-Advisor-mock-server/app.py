from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from database import init_db

from database import get_db, Base, engine, SessionLocal
# Import all route modules
from routes.admin import router as admin_router
from routes.identity import router as identity_router

# Create database tables
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="eMoney Advisor Mock API",
    description="A FastAPI-based mock implementation of eMoney Advisor APIs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✓ Database initialized")
    print("✓ EMonet Mock API is ready")
    print("✓ Version 1.0 - Identity Management")
    print("✓ API Documentation: http://localhost:6820/docs")

# Include all routers with /v1 prefix
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(identity_router, prefix="/api/v1", tags=["Identity"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=6820, reload=True)
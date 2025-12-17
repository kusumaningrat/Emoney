import logging
from sqlalchemy import text
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import uvicorn

from app.api.routes import scans
from app.core.exceptions import setup_exception_handlers
from app.settings import get_settings
from app.db.database import initialize_database , engine

from fastapi.staticfiles import StaticFiles
from pathlib import Path

static_dir = Path("app/static")
static_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Service Orchestrator",
    description="Orchestration service for identity and other services",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.include_router(scans.router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/dashboard")
async def dashboard():
    """Redirect to the dashboard page"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html")

# Define startup event
@app.on_event("startup")
async def startup_event():
    try:
        await initialize_database()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.warning("Application will start with limited functionality")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

# Health check endpoint
@app.get("/health", status_code=200)
async def health_check():
    """Health check endpoint that includes database status and URL"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "components": {
            "api": "healthy"
        }
    }
    
    # Get the database URL and mask password for response and logging
    db_url = str(settings.DATABASE_URL)
    masked_url = db_url
    if ":" in db_url and "@" in db_url:
        masked_url = db_url.replace(
            db_url.split(":", 2)[2].split("@")[0],
            "********"
        )
        logger.info(f"Checking database connection to: {masked_url}")
    
    # Add database URL to response
    health_status["database_url"] = masked_url
    
    # Check database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = "healthy"
        logger.info("Database connection check: SUCCESS")
    except Exception as e:
        health_status["components"]["database"] = "unhealthy"
        health_status["database_error"] = str(e)
        logger.error(f"Database connection check: FAILED - {str(e)}")
    
    return health_status


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
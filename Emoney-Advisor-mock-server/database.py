import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://emoney:postgres@postgres:5432/emoney_mock")

# For local development with SQLite
# DATABASE_URL = "sqlite:///./emoney_mock.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    # For SQLite, this is needed to enable foreign key constraints
    # connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they're registered with SQLAlchemy
    # Import V1 models first (they're referenced by V2)
    from models import identity
    
    # Import V2 models second (they reference V1)
    from models import client
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
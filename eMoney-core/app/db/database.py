# Database setup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create SQLAlchemy engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
)

# Create async session factory
AsyncSessionFactory = sessionmaker(
    engine, 
    expire_on_commit=False, 
    class_=AsyncSession,
    autoflush=False,
)

# Create declarative base for models
Base = declarative_base()


async def initialize_database():
    """
    Initialize database - create all tables.
    Should be called during application startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        logger.warning("Application will continue without database functionality")
        return False


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager to get a database session.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get a database session for FastAPI.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
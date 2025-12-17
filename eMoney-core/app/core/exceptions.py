# app/core/exceptions.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Base exception class for service errors."""
    
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class ServiceConnectionError(ServiceException):
    """Raised when a service connection fails."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                         detail=detail)


def setup_exception_handlers(app: FastAPI):
    """
    Set up exception handlers for the application.
    
    Args:
        app: FastAPI application
    """
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        """
        Handle ServiceException.
        
        Args:
            request: Request object
            exc: Exception
            
        Returns:
            JSONResponse: Error response
        """
        logger.error(f"ServiceException: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """
        Handle ValidationError.
        
        Args:
            request: Request object
            exc: Exception
            
        Returns:
            JSONResponse: Error response
        """
        logger.error(f"ValidationError: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle general exceptions.
        
        Args:
            request: Request object
            exc: Exception
            
        Returns:
            JSONResponse: Error response
        """
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
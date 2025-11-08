import os
from fastapi import HTTPException, status

# Get API credentials from environment variables or use defaults
API_KEY = os.getenv("API_KEY", "test-api-key")
API_SECRET = os.getenv("API_SECRET", "test-api-secret")

def verify_api_key(x_api_key: str, x_api_secret: str):
    """
    Verify API key and secret
    """
    if x_api_key != API_KEY or x_api_secret != API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API credentials"
        )
    return True

def generate_jwt_token():
    """
    Mock implementation of JWT token generation for eMoney API
    In a real implementation, this would create a proper JWT
    using X.509 certificates as described in the documentation
    """
    # This is just a placeholder for the mock implementation
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJZT1VSX0NMSUVOVF9JRCIsInN1YiI6IllPVVJfQ0xJRU5UX0lEIiwiYXVkIjoiaHR0cHM6Ly9zaWduaW4tZXh0ZXJuYWxiZXRhMi5lbWFwbGFuLmNvbS9jb25uZWN0L3Rva2VuIiwiZXhwIjoxNjM1NTI5NjAwLCJqdGkiOiIxMjM0NTY3ODkwIn0.signature"
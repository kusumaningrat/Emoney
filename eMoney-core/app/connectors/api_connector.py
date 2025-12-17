import httpx
import time
import logging
from typing import Dict, Any, Optional, Union, List

logger = logging.getLogger(__name__)

class SimpleAPIConnector:
    """
    Enhanced API connector for making requests to EMoney services.
    Supports JWT token authentication and EMoney-specific patterns.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, timeout: float = 30.0):
        """
        Initialize the API connector with optional base URL and API key.
        
        Args:
            base_url: Base URL for API requests (optional)
            api_key: API key for authentication (optional) 
            timeout: Default request timeout in seconds (increased for EMoney)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.access_token = None
        
    def _prepare_emoney_headers(self, headers: Dict[str, str] = None, auth_config: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Prepare headers for EMoney API requests with proper authentication.
        
        Args:
            headers: Custom headers to merge
            auth_config: Authentication configuration containing JWT token, firm_id, etc.
            
        Returns:
            Dict[str, str]: Prepared headers
        """
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EMoney-Connector/1.0",
        }
        
        # Add API key if available
        if self.api_key:
            request_headers["X-API-Key"] = self.api_key
            
        # Handle EMoney JWT token authentication
        if auth_config:
            # JWT token takes precedence
            if 'jwt_token' in auth_config and auth_config['jwt_token']:
                jwt_token = auth_config['jwt_token']
                if not jwt_token.startswith('Bearer '):
                    jwt_token = f"Bearer {jwt_token}"
                request_headers["Authorization"] = jwt_token
                logger.debug("Added JWT token to Authorization header")
                
            # Add firm ID header if present
            if 'firm_id' in auth_config and auth_config['firm_id']:
                request_headers["X-Firm-ID"] = str(auth_config['firm_id'])
                logger.debug(f"Added Firm-ID header: {auth_config['firm_id']}")
                
            # Add client ID header if present
            if 'client_id' in auth_config and auth_config['client_id']:
                request_headers["X-Client-ID"] = str(auth_config['client_id'])
                logger.debug(f"Added Client-ID header: {auth_config['client_id']}")
                
            # Handle API key from auth config if not set in constructor
            if 'api_key' in auth_config and auth_config['api_key'] and not self.api_key:
                request_headers["X-API-Key"] = auth_config['api_key']
                logger.debug("Added API key from auth config")
        
        # Use stored access token if no auth_config provided
        elif self.access_token:
            if not self.access_token.startswith('Bearer '):
                self.access_token = f"Bearer {self.access_token}"
            request_headers["Authorization"] = self.access_token
            logger.debug("Used stored access token")
            
        # Add custom headers (these can override defaults)
        if headers:
            request_headers.update(headers)
            
        return request_headers
    
    async def request(
        self,
        method: str,
        url: str,
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: float = None,
        max_retries: int = 3,
        **kwargs  # Accept any additional parameters
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with EMoney-specific enhancements and return the JSON response.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: URL to request (if base_url is set, this can be a relative path)
            params: Query parameters
            json_data: JSON body data
            headers: Custom headers
            timeout: Request timeout override
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters (auth_config, oauth_config, etc.)
            
        Returns:
            Dict[str, Any]: JSON response data
        """
        # Extract authentication config from kwargs
        auth_config = kwargs.get('auth_config') or kwargs.get('oauth_config')
        
        # Prepare full URL
        full_url = url
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
            
        # Prepare EMoney-specific headers
        request_headers = self._prepare_emoney_headers(headers, auth_config)
            
        # Set timeout
        request_timeout = timeout or self.timeout
        
        logger.info(f"Making {method} request to: {full_url}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Authorization header present: {'Authorization' in request_headers}")
        
        # Retry logic for EMoney API patterns
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=request_timeout) as client:
                    response = await client.request(
                        method=method,
                        url=full_url,
                        params=params,
                        json=json_data,
                        headers=request_headers
                    )
                    
                    logger.info(f"Response status code: {response.status_code}")
                    logger.debug(f"Response headers: {dict(response.headers)}")
                    logger.debug(f"Response content length: {len(response.content)}")
                    
                    # Handle rate limiting (429)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    # Handle authentication errors (401)
                    if response.status_code == 401:
                        logger.warning("Authentication failed (401). Check JWT token validity.")
                        if attempt == max_retries - 1:
                            response.raise_for_status()
                        else:
                            # For now, just retry - in production you might want to refresh token
                            wait_time = (2**attempt) * 2
                            logger.warning(f"Retrying authentication in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    # Raise for other HTTP errors
                    response.raise_for_status()
                    
                    # Handle empty responses
                    if not response.content:
                        logger.warning("Empty response received from API")
                        return {}
                    
                    # Return JSON if possible, otherwise text
                    if response.headers.get("content-type", "").startswith("application/json"):
                        try:
                            return response.json()
                        except Exception as json_err:
                            logger.error(f"Failed to parse JSON response: {json_err}")
                            logger.error(f"Response content: {response.text[:500]}")
                            return {"text": response.text}
                    else:
                        return {"text": response.text}
                        
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                else:
                    wait_time = (2**attempt) * 2
                    logger.warning(f"Request failed, retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                else:
                    wait_time = (2**attempt) * 2
                    logger.warning(f"Request failed, retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    
        raise Exception(f"Failed to complete request after {max_retries} attempts")
    
    async def get(self, url: str, params: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for GET requests"""
        return await self.request("GET", url, params=params, **kwargs)
    
    async def post(self, url: str, json_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for POST requests"""
        return await self.request("POST", url, json_data=json_data, **kwargs)
    
    async def put(self, url: str, json_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for PUT requests"""
        return await self.request("PUT", url, json_data=json_data, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for DELETE requests"""
        return await self.request("DELETE", url, **kwargs)
    
    # EMoney-specific convenience methods
    async def get_with_auth(self, url: str, auth_config: Dict[str, Any], params: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Convenience method for GET requests with EMoney authentication config
        
        Args:
            url: Request URL
            auth_config: EMoney auth configuration (jwt_token, firm_id, client_id, api_key)
            params: Query parameters
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: JSON response
        """
        return await self.get(url, params=params, auth_config=auth_config, **kwargs)
    
    async def post_with_auth(self, url: str, auth_config: Dict[str, Any], json_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Convenience method for POST requests with EMoney authentication config
        
        Args:
            url: Request URL
            auth_config: EMoney auth configuration (jwt_token, firm_id, client_id, api_key)
            json_data: JSON body data
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: JSON response
        """
        return await self.post(url, json_data=json_data, auth_config=auth_config, **kwargs)
    
    def set_access_token(self, token: str):
        """
        Set the access token for future requests
        
        Args:
            token: JWT or other access token
        """
        self.access_token = token
        logger.debug("Access token updated")
    
    def clear_access_token(self):
        """Clear the stored access token"""
        self.access_token = None
        logger.debug("Access token cleared")

# Add asyncio import for sleep functionality
import asyncio
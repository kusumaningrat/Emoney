import httpx
from typing import Dict, Any, Optional, Union, List

class SimpleAPIConnector:
    """
    A minimalist API connector for making requests to Wealthbox services.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, timeout: float = 5.0):
        """
        Initialize the API connector with optional base URL and API key.
        
        Args:
            base_url: Base URL for API requests (optional)
            api_key: API key for authentication (optional)
            timeout: Default request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        
    async def request(
        self,
        method: str,
        url: str,
        params: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: float = None,
        **kwargs  # Accept any additional parameters
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and return the JSON response.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: URL to request (if base_url is set, this can be a relative path)
            params: Query parameters
            json_data: JSON body data
            headers: Custom headers
            timeout: Request timeout override
            **kwargs: Additional parameters (oauth_config etc.)
            
        Returns:
            Dict[str, Any]: JSON response data
        """
        # Process oauth_config if present in kwargs
        oauth_config = kwargs.get('oauth_config')
        
        # Prepare full URL
        full_url = url
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
            
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key if available
        if self.api_key:
            request_headers["X-API-Key"] = self.api_key
        
        # Add OAuth headers if oauth_config is provided
        if oauth_config:
            # You may need to customize this based on your OAuth implementation
            if 'client_id' in oauth_config and 'client_secret' in oauth_config:
                # For client credentials flow
                if oauth_config.get('grant_type') == 'client_credentials':
                    # Implement client credentials auth as needed
                    pass
                    
                # Other OAuth flows can be implemented here as needed
                
        # Add custom headers
        if headers:
            request_headers.update(headers)
            
        # Set timeout
        request_timeout = timeout or self.timeout
        
        # Make the request
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = await client.request(
                method=method,
                url=full_url,
                params=params,
                json=json_data,
                headers=request_headers
            )
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Return JSON if possible, otherwise text
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text}
    
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
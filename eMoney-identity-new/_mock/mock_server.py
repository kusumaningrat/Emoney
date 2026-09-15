# mock_server.py
from fastapi import FastAPI, HTTPException, Header, Query, Request
from fastapi.responses import JSONResponse
import time
import uvicorn
from typing import Optional
from faker import Faker
from mock_config import *
from collections import defaultdict, deque
from datetime import datetime, timedelta

app = FastAPI(
    title=APP_TITLE + " - Mock Server",
    version=APP_VERSION,
    description=APP_DESCRIPTION + " (Mock Implementation with HubSpot-like Rate Limiting)"
)

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: {"requests": deque(), "daily_count": 0, "daily_reset": datetime.now() + timedelta(days=1)})

# Initialize Faker with seed for consistent data
fake = Faker()
fake.seed_instance(FAKER_SEED)

# Generate realistic mock data using Faker
MOCK_USERS = []
for i in range(TOTAL_MOCK_USERS):
    MOCK_USERS.append({
        'id': f'user_{i}',
        'email': fake.email(),
        'firstName': fake.first_name(),
        'lastName': fake.last_name(),
        'roleId': fake.random_element(['admin', 'user', 'sales', 'marketing']),
        'superAdmin': fake.boolean(chance_of_getting_true=10),  # 10% super admins
        'teams': [fake.random_element(['Sales', 'Marketing', 'Customer Success', 'Support'])],
        'lastLoginDate': fake.date_time_between(start_date='-30d', end_date='now').isoformat() + 'Z',
        'createdAt': fake.date_time_between(start_date='-1y', end_date='now').isoformat() + 'Z',
        'isActive': fake.boolean(chance_of_getting_true=85),  # 85% active users
        'permissions': fake.random_elements(['contacts', 'companies', 'deals', 'reports'], unique=True)
    })

def check_rate_limit(token: str) -> dict:
    """Check HubSpot-like rate limits"""
    if not RATE_LIMIT_ENABLED:
        return {"allowed": True}
    
    now = datetime.now()
    client_data = rate_limit_storage[token]
    
    # Reset daily counter if needed
    if now > client_data["daily_reset"]:
        client_data["daily_count"] = 0
        client_data["daily_reset"] = now + timedelta(days=1)
    
    # Check daily limit
    if client_data["daily_count"] >= DAILY_LIMIT:
        return {
            "allowed": False,
            "reason": "daily_limit_exceeded",
            "retry_after": int((client_data["daily_reset"] - now).total_seconds())
        }
    
    # Clean old requests (older than window)
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    while client_data["requests"] and client_data["requests"][0] < window_start:
        client_data["requests"].popleft()
    
    # Check burst limit
    if len(client_data["requests"]) >= BURST_LIMIT:
        return {
            "allowed": False,
            "reason": "burst_limit_exceeded", 
            "retry_after": RATE_LIMIT_WINDOW
        }
    
    # Add current request
    client_data["requests"].append(now)
    client_data["daily_count"] += 1
    
    return {"allowed": True}

def add_rate_limit_headers(response: JSONResponse, token: str) -> JSONResponse:
    """Add HubSpot-like rate limit headers"""
    if not RATE_LIMIT_ENABLED:
        return response
        
    client_data = rate_limit_storage[token]
    daily_remaining = max(0, DAILY_LIMIT - client_data["daily_count"])
    burst_remaining = max(0, BURST_LIMIT - len(client_data["requests"]))
    
    response.headers["X-RateLimit-Daily"] = str(DAILY_LIMIT)
    response.headers["X-RateLimit-Daily-Remaining"] = str(daily_remaining)
    response.headers["X-RateLimit-Interval"] = str(BURST_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(burst_remaining)
    response.headers["X-RateLimit-Reset"] = str(int(client_data["daily_reset"].timestamp()))
    
    return response

@app.get("/settings/v3/users")
async def get_users(
    request: Request,
    limit: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE),
    after: str = Query("0"),
    _test_delay: float = Query(DEFAULT_TEST_DELAY),
    authorization: Optional[str] = Header(None)
):
    """Mock HubSpot users/accounts endpoint with rate limiting"""
    
    try:
        # Extract token for rate limiting
        token = "default"
        if authorization and authorization.startswith('Bearer '):
            token = authorization.replace('Bearer ', '')
        
        # Check rate limits
        rate_check = check_rate_limit(token)
        if not rate_check["allowed"]:
            headers = {
                "Retry-After": str(rate_check["retry_after"]),
                "X-RateLimit-Daily": str(DAILY_LIMIT),
                "X-RateLimit-Daily-Remaining": "0" if rate_check["reason"] == "daily_limit_exceeded" else str(DAILY_LIMIT - rate_limit_storage[token]["daily_count"]),
                "X-RateLimit-Interval": str(BURST_LIMIT),
                "X-RateLimit-Remaining": "0"
            }
            return JSONResponse(
                status_code=429,
                content={"error": f"Rate limit exceeded: {rate_check['reason']}", "retry_after": rate_check["retry_after"]},
                headers=headers
            )
        
        # Test delay - with bounds checking
        if _test_delay > 0 and _test_delay <= 60:  # Max 60 second delay
            time.sleep(_test_delay)
        
        # Parse cursor with better validation
        try:
            start_index = int(after) if after and after.isdigit() else 0
            # Ensure start_index is within bounds - don't cap at length, let it go beyond
            start_index = max(0, start_index)
        except (ValueError, TypeError):
            start_index = 0
        
        # Validate limit
        limit = max(1, min(limit, MAX_PAGE_SIZE))
        end_index = start_index + limit
        
        # Get page data - handle out of bounds gracefully
        if start_index >= len(MOCK_USERS):
            page_data = []
        else:
            page_data = MOCK_USERS[start_index:end_index]
        
        # Build response - always ensure consistent structure
        response_data = {
            'results': page_data if page_data is not None else []
        }
        
        # CRITICAL FIX: Always provide paging object, never null/None
        if end_index < len(MOCK_USERS) and len(page_data) > 0:
            # More data available
            response_data['paging'] = {
                'next': {
                    'after': str(end_index)
                }
            }
        else:
            # No more pages or no data - ALWAYS empty object, never null
            response_data['paging'] = {}
        
        # Final safety check - ensure paging is never None/null
        if response_data.get('paging') is None:
            response_data['paging'] = {}
        
        # Ensure response_data structure is valid
        if response_data is None:
            response_data = {'results': [], 'paging': {}}
        if 'results' not in response_data:
            response_data['results'] = []
        if 'paging' not in response_data:
            response_data['paging'] = {}
        
        # Debug logging for troubleshooting
        print(f"Mock server response: start_index={start_index}, end_index={end_index}, "
              f"total_users={len(MOCK_USERS)}, results_count={len(response_data['results'])}, "
              f"has_paging_next={'next' in response_data['paging']}")
        
        # Create JSON response
        response = JSONResponse(content=response_data)
        return add_rate_limit_headers(response, token)
        
    except Exception as e:
        # Log the error and return a safe empty response
        print(f"Error in get_users endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a safe fallback response - NEVER null paging
        fallback_response = JSONResponse(
            status_code=200,  # Don't return error status as it might break the pipeline
            content={
                'results': [],
                'paging': {},  # Empty object, never null
                'error_debug': f"Internal server error: {str(e)}"  # Only in development
            }
        )
        
        # Still apply rate limit headers if possible
        try:
            token = "default"
            if authorization and authorization.startswith('Bearer '):
                token = authorization.replace('Bearer ', '')
            return add_rate_limit_headers(fallback_response, token)
        except:
            return fallback_response

# Add a debug endpoint to check server state
@app.get("/debug/server-state")
async def debug_server_state():
    """Debug endpoint to check server state"""
    return {
        "mock_users_count": len(MOCK_USERS),
        "mock_users_sample": MOCK_USERS[:2] if MOCK_USERS else [],
        "constants": {
            "DEFAULT_PAGE_SIZE": globals().get('DEFAULT_PAGE_SIZE', 'UNDEFINED'),
            "MAX_PAGE_SIZE": globals().get('MAX_PAGE_SIZE', 'UNDEFINED'),
            "TOTAL_MOCK_USERS": globals().get('TOTAL_MOCK_USERS', 'UNDEFINED'),
            "FAKER_SEED": globals().get('FAKER_SEED', 'UNDEFINED'),
        }
    }

@app.get("/v1/me")
async def validate_token(authorization: Optional[str] = Header(None)):
    """Mock token validation"""
    if not authorization or not authorization.startswith('Bearer ') or authorization.replace('Bearer ', '') == 'invalid':
        raise HTTPException(status_code=401, detail='Invalid token')
    
    return {'id': 'test_account', 'name': 'Test Account'}

@app.get("/v1/account")
async def get_account():
    """Mock account info"""
    return {
        'id': 'account_123',
        'name': 'Test Organization'
    }

@app.get("/health")
async def health():
    """Health check with rate limiting status"""
    return {
        'status': 'healthy', 
        'users': len(MOCK_USERS),
        'rate_limiting': RATE_LIMIT_ENABLED,
        'daily_limit': DAILY_LIMIT,
        'burst_limit': BURST_LIMIT
    }

@app.get("/rate-limit-status")
async def rate_limit_status(authorization: Optional[str] = Header(None)):
    """Check current rate limit status for debugging"""
    token = "default"
    if authorization and authorization.startswith('Bearer '):
        token = authorization.replace('Bearer ', '')
    
    if not RATE_LIMIT_ENABLED:
        return {"rate_limiting": False}
    
    client_data = rate_limit_storage[token]
    daily_remaining = max(0, DAILY_LIMIT - client_data["daily_count"])
    burst_remaining = max(0, BURST_LIMIT - len(client_data["requests"]))
    
    return {
        "rate_limiting": True,
        "daily_used": client_data["daily_count"],
        "daily_remaining": daily_remaining,
        "burst_used": len(client_data["requests"]),
        "burst_remaining": burst_remaining,
        "daily_reset": client_data["daily_reset"].isoformat()
    }

if __name__ == '__main__':
    print(f"Mock server starting on {MOCK_HOST}:{MOCK_PORT}")
    print(f"Total mock users: {TOTAL_MOCK_USERS}")
    print(f"Rate limiting: {'Enabled' if RATE_LIMIT_ENABLED else 'Disabled'}")
    if RATE_LIMIT_ENABLED:
        print(f"Daily limit: {DAILY_LIMIT}, Burst limit: {BURST_LIMIT} per {RATE_LIMIT_WINDOW}s")
    uvicorn.run(app, host=MOCK_HOST, port=MOCK_PORT, log_level="info")
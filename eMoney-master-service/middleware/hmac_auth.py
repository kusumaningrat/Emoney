from functools import wraps
import hmac
import hashlib
import time
from flask import request, g, Response, current_app

from config import get_config

def hmac_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        config = get_config()
        if not config.HMAC_ENABLED:
            return f(*args, **kwargs)

        # Get headers
        signature = request.headers.get('X-Orion-Signature')
        timestamp = request.headers.get('X-Orion-Timestamp')
        client_id = request.headers.get('X-Orion-Client-ID')
        
        # Check required headers
        if not signature or not timestamp or not client_id:
            return {'status': 'error', 'message': 'Missing HMAC headers'}, 401
        
        # Check client is authorized
        config = current_app.config
        if client_id not in config.get('HMAC_ALLOWED_CLIENT_IDS', []):
            return {'status': 'error', 'message': 'Unauthorized client'}, 403
        
        # Check timestamp is recent
        try:
            if abs(int(time.time()) - int(timestamp)) > config.get('HMAC_SIGNATURE_MAX_AGE', 300):
                return {'status': 'error', 'message': 'Timestamp expired'}, 401
        except ValueError:
            return {'status': 'error', 'message': 'Invalid timestamp'}, 401
        
        # Verify signature
        method = request.method
        path = request.path
        query = request.query_string.decode('utf-8') if request.query_string else ''
        body = request.get_data().decode('utf-8') if request.get_data() else ''
        
        canonical_string = f"{method}{path}{query}{timestamp}{body}"
        
        calculated_hmac = hmac.new(
            config.get('HMAC_SECRET_KEY', '').encode('utf-8'),
            canonical_string.encode('utf-8'),
            getattr(hashlib, config.get('HMAC_ALGORITHM', 'sha256').lower())
        ).hexdigest()
        
        if not hmac.compare_digest(calculated_hmac, signature):
            return {'status': 'error', 'message': 'Invalid signature'}, 401
            
        # Store client ID for potential use in the route handlers
        g.client_id = client_id
        
        return f(*args, **kwargs)
    return decorated
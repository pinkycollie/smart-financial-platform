"""
Security Configuration Example for DHH Financial Platform

This module demonstrates best practices for securing the API endpoints
with OAuth 2.0 and API key authentication as specified in the OpenAPI spec.
"""

import os
from functools import wraps
from typing import Dict, List, Tuple, Optional, Any
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for API endpoints."""
    
    # OAuth 2.0 configuration
    OAUTH_AUTHORIZATION_URL = os.getenv('OAUTH_AUTHORIZATION_URL', 'https://api.mbtquniverse.com/oauth/authorize')
    OAUTH_TOKEN_URL = os.getenv('OAUTH_TOKEN_URL', 'https://api.mbtquniverse.com/oauth/token')
    OAUTH_SCOPES = ['read', 'write', 'admin']
    
    # API Key configuration
    API_KEY_HEADER = 'X-API-Key'
    VALID_API_KEYS = set(os.getenv('VALID_API_KEYS', '').split(','))
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # seconds
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }


def require_api_key(f):
    """
    Decorator to require API key authentication.
    
    Usage:
        @require_api_key
        def my_endpoint():
            return jsonify({'data': 'secure data'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get(SecurityConfig.API_KEY_HEADER)
        
        if not api_key:
            logger.warning("API key missing in request")
            return jsonify({
                'status': 'error',
                'message': 'API key required'
            }), 401
        
        if api_key not in SecurityConfig.VALID_API_KEYS:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_oauth_scope(*required_scopes):
    """
    Decorator to require specific OAuth 2.0 scopes.
    
    Usage:
        @require_oauth_scope('read', 'write')
        def my_endpoint():
            return jsonify({'data': 'secure data'})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In production, this would validate the OAuth token
            # and check the granted scopes
            
            # Placeholder implementation
            auth_header = request.headers.get('Authorization')
            
            if not auth_header or not auth_header.startswith('Bearer '):
                logger.warning("OAuth token missing in request")
                return jsonify({
                    'status': 'error',
                    'message': 'OAuth token required'
                }), 401
            
            # Extract token
            token = auth_header.split('Bearer ')[1]
            
            # In production, validate token and extract scopes
            # This is a placeholder for demonstration
            granted_scopes = _validate_oauth_token(token)
            
            # Check if required scopes are granted
            if not all(scope in granted_scopes for scope in required_scopes):
                logger.warning(f"Insufficient OAuth scopes. Required: {required_scopes}")
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def _validate_oauth_token(token: str) -> list:
    """
    Validate OAuth token and return granted scopes.
    
    In production, this would:
    1. Verify token signature
    2. Check token expiration
    3. Extract user identity and scopes
    4. Return the granted scopes
    
    This is a placeholder implementation.
    
    Args:
        token: OAuth access token
        
    Returns:
        list: List of scope strings granted to the token (e.g., ['read', 'write'])
    """
    # Placeholder: In production, use a proper OAuth library
    # like Authlib or python-oauth2
    
    if not token:
        return []
    
    # Mock implementation - returns read and write scopes
    return ['read', 'write']


def add_security_headers(response):
    """
    Add security headers to response.
    
    Usage in Flask:
        @app.after_request
        def after_request(response):
            return add_security_headers(response)
    """
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response


def validate_input(data: Dict[str, Any], required_fields: List[str], schema: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate input data against required fields and schema.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        schema: Optional schema for validation
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # If schema provided, validate against it
    if schema:
        for field, field_schema in schema.items():
            if field in data:
                value = data[field]
                field_type = field_schema.get('type')
                
                # Type validation
                if field_type == 'string' and not isinstance(value, str):
                    return False, f"Field '{field}' must be a string"
                elif field_type == 'number' and not isinstance(value, (int, float)):
                    return False, f"Field '{field}' must be a number"
                elif field_type == 'boolean' and not isinstance(value, bool):
                    return False, f"Field '{field}' must be a boolean"
                
                # Enum validation
                if 'enum' in field_schema:
                    if value not in field_schema['enum']:
                        return False, f"Field '{field}' must be one of: {field_schema['enum']}"
    
    return True, None


def sanitize_output(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
    """
    Sanitize output data by masking sensitive fields.
    
    Args:
        data: Output data dictionary
        sensitive_fields: List of field names to mask
        
    Returns:
        Sanitized data dictionary
    """
    if sensitive_fields is None:
        sensitive_fields = ['ssn', 'tax_id', 'api_key', 'password', 'token']
    
    sanitized = data.copy()
    
    for field in sensitive_fields:
        if field in sanitized:
            # Mask the value
            value = str(sanitized[field])
            if len(value) > 4:
                sanitized[field] = f"***{value[-4:]}"
            else:
                sanitized[field] = "***"
    
    return sanitized


# Example usage in endpoints
def example_secure_endpoint():
    """
    Example of a secure endpoint using the security decorators.
    
    This demonstrates best practices for securing DHH API endpoints.
    """
    from flask import Blueprint, request, jsonify
    
    secure_bp = Blueprint('secure_api', __name__)
    
    @secure_bp.route('/api/secure/client-data', methods=['GET'])
    @require_oauth_scope('read')
    def get_client_data():
        """
        Get client data (requires OAuth with 'read' scope).
        """
        # Implementation here
        return jsonify({'data': 'secure client data'})
    
    @secure_bp.route('/api/secure/admin/settings', methods=['POST'])
    @require_oauth_scope('admin')
    def update_settings():
        """
        Update system settings (requires OAuth with 'admin' scope).
        """
        # Implementation here
        return jsonify({'status': 'success'})
    
    @secure_bp.route('/api/secure/service/health', methods=['GET'])
    @require_api_key
    def service_health():
        """
        Service health check (requires API key for service-to-service).
        """
        return jsonify({'status': 'UP'})
    
    return secure_bp


# Rate limiting implementation (placeholder)
class RateLimiter:
    """
    Simple rate limiter for API endpoints.
    
    WARNING: This in-memory implementation will NOT work across multiple
    server instances or containers. This limitation is critical for:
    - Load-balanced deployments
    - Kubernetes/Docker multi-replica deployments
    - Any horizontal scaling scenario
    
    In production, use a proper rate limiting library like Flask-Limiter
    with Redis backend for distributed rate limiting across all instances.
    
    Example production setup:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            storage_uri="redis://localhost:6379"
        )
    """
    
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    def is_rate_limited(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique client identifier (IP, API key, user ID, etc.)
            
        Returns:
            True if rate limited, False otherwise
        """
        import time
        
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return True
        
        # Add current request
        self.requests[client_id].append(current_time)
        
        return False

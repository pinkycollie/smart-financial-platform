"""
MBTQ Group LLC Security Configuration
Enterprise-grade security for financial and real estate platform
"""

import os
import secrets
from datetime import timedelta
from flask import Flask
from flask_wtf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet

class SecurityManager:
    """Centralized security management for MBTQ Group LLC platform"""
    
    def __init__(self, app=None):
        self.app = app
        self.csrf = CSRFProtect()
        self.limiter = None
        self.talisman = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize comprehensive security for Flask application"""
        
        # 1. SESSION SECURITY
        self._configure_session_security(app)
        
        # 2. CSRF PROTECTION
        self._configure_csrf_protection(app)
        
        # 3. SECURITY HEADERS
        self._configure_security_headers(app)
        
        # 4. RATE LIMITING
        self._configure_rate_limiting(app)
        
        # 5. ENCRYPTION SETUP
        self._configure_encryption(app)
        
        # 6. BLUETOOTH SECURITY POLICY
        self._configure_bluetooth_policy(app)
        
        app.logger.info("Enterprise security configuration initialized")
    
    def _configure_session_security(self, app: Flask):
        """Configure secure session handling"""
        # Session configuration for financial data security
        app.config.update(
            SESSION_COOKIE_SECURE=True,  # HTTPS only
            SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
            SESSION_COOKIE_SAMESITE='Strict',  # CSRF protection
            PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # Short timeout for financial data
            SESSION_REFRESH_EACH_REQUEST=True,  # Refresh timeout on activity
            
            # Generate strong session secret if not provided
            SECRET_KEY=os.environ.get('SESSION_SECRET') or secrets.token_urlsafe(32)
        )
        
        # Session rotation on login (implemented in auth service)
        @app.before_request
        def rotate_session_on_auth():
            """Rotate session ID on authentication changes"""
            from flask import session, request
            from flask_login import current_user
            
            # Skip for static files
            if request.endpoint and request.endpoint.startswith('static'):
                return
                
            # Check if this is a login request
            if request.endpoint in ['auth.login', 'auth.register'] and request.method == 'POST':
                # Session will be rotated by Flask-Login automatically
                pass
    
    def _configure_csrf_protection(self, app: Flask):
        """Configure CSRF protection for all forms and sensitive endpoints"""
        
        # CSRF configuration
        app.config.update(
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_TIME_LIMIT=3600,  # 1 hour token lifetime
            WTF_CSRF_SSL_STRICT=True,  # Enforce HTTPS
            WTF_CSRF_SECRET_KEY=os.environ.get('CSRF_SECRET_KEY') or secrets.token_urlsafe(32)
        )
        
        # Initialize CSRF protection
        self.csrf.init_app(app)
        
        # Custom CSRF error handler for financial platform
        @app.errorhandler(400)
        def csrf_error(reason):
            from flask import render_template, request, jsonify
            
            app.logger.warning(f"CSRF validation failed: {reason} from IP: {request.remote_addr}")
            
            if request.is_json:
                return jsonify({
                    'error': 'Security validation failed',
                    'message': 'Please refresh the page and try again',
                    'code': 'CSRF_ERROR'
                }), 400
            
            return render_template('errors/security_error.html', 
                                 error_message='Security validation failed. Please refresh and try again.'), 400
    
    def _configure_security_headers(self, app: Flask):
        """Configure comprehensive security headers"""
        
        # Content Security Policy for deaf-first platform
        csp = {
            'default-src': "'self'",
            'script-src': [
                "'self'",
                "'unsafe-inline'",  # Required for HTMX and Bootstrap
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://code.jquery.com"
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for dynamic deaf UI components
                "https://cdn.jsdelivr.net",
                "https://cdnjs.cloudflare.com",
                "https://fonts.googleapis.com"
            ],
            'font-src': [
                "'self'",
                "https://fonts.gstatic.com",
                "https://cdnjs.cloudflare.com"
            ],
            'img-src': [
                "'self'",
                "data:",  # For base64 images
                "https:"  # Allow HTTPS images for ASL content
            ],
            'media-src': [
                "'self'",
                "https://stream.mux.com",  # Mux video streaming
                "https://api.pinksync.io",  # PinkSync ASL content
                "https://*.signasl.com"  # SignASL video content
            ],
            'connect-src': [
                "'self'",
                "https://api.openai.com",  # OpenAI API for ASL AI
                "https://api.pinksync.io",  # PinkSync API
                "https://api.getapril.com",  # April Tax API
                "https://api.boostinsurance.io"  # Boost Insurance API
            ],
            'frame-ancestors': "'none'",  # Prevent clickjacking
            'base-uri': "'self'"
        }
        
        # Initialize Talisman with strict security
        self.talisman = Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,  # 1 year
            content_security_policy=csp,
            referrer_policy='strict-origin-when-cross-origin',
            permissions_policy={
                'bluetooth': '()',  # STRICT: No Web Bluetooth allowed
                'camera': '()',     # No camera access
                'microphone': '()',  # No microphone access (ASL is visual)
                'geolocation': '()'  # No location tracking
            }
        )
        
        # Additional security headers
        @app.after_request
        def add_security_headers(response):
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Disable potentially dangerous features
            response.headers['Feature-Policy'] = (
                'bluetooth \'none\'; '
                'camera \'none\'; '
                'microphone \'none\'; '
                'geolocation \'none\''
            )
            
            # Custom header for deaf-first platform
            response.headers['X-MBTQ-Security'] = 'deaf-first-secure'
            
            return response
    
    def _configure_rate_limiting(self, app: Flask):
        """Configure rate limiting for sensitive endpoints"""
        
        # Rate limiter configuration
        app.config.update(
            RATELIMIT_STORAGE_URL=os.environ.get('REDIS_URL', 'memory://'),
            RATELIMIT_DEFAULT="100 per hour",
            RATELIMIT_ENABLED=True
        )
        
        # Initialize rate limiter
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["100 per hour"]
        )
        self.limiter.init_app(app)
        
        # Define strict limits for sensitive endpoints
        auth_limit = "5 per minute"
        api_limit = "30 per minute"
        ai_limit = "20 per minute"  # AI services are expensive
        
        # Apply limits to existing routes (will be applied via decorators)
        self.auth_limit = auth_limit
        self.api_limit = api_limit
        self.ai_limit = ai_limit
        
        # Rate limit exceeded handler
        @app.errorhandler(429)
        def ratelimit_handler(e):
            from flask import request, jsonify, render_template
            
            app.logger.warning(f"Rate limit exceeded from IP: {request.remote_addr}")
            
            if request.is_json:
                return jsonify({
                    'error': 'Too many requests',
                    'message': 'Please wait before trying again',
                    'retry_after': str(e.retry_after) if hasattr(e, 'retry_after') else None
                }), 429
            
            return render_template('errors/rate_limit.html'), 429
    
    def _configure_encryption(self, app: Flask):
        """Configure field-level encryption for sensitive data"""
        
        # Generate or load encryption key
        encryption_key = os.environ.get('FIELD_ENCRYPTION_KEY')
        if not encryption_key:
            # Generate a new key (should be stored securely in production)
            encryption_key = Fernet.generate_key().decode()
            app.logger.warning("Generated new encryption key - store this securely in FIELD_ENCRYPTION_KEY environment variable")
        
        app.config['FIELD_ENCRYPTION_KEY'] = encryption_key
        
        # Initialize Fernet cipher
        app.encryption_cipher = Fernet(encryption_key.encode())
        
        # Helper functions for encryption/decryption
        def encrypt_field(data: str) -> str:
            """Encrypt sensitive field data"""
            if not data:
                return data
            return app.encryption_cipher.encrypt(data.encode()).decode()
        
        def decrypt_field(encrypted_data: str) -> str:
            """Decrypt sensitive field data"""
            if not encrypted_data:
                return encrypted_data
            try:
                return app.encryption_cipher.decrypt(encrypted_data.encode()).decode()
            except Exception as e:
                app.logger.error(f"Decryption error: {e}")
                return "[ENCRYPTED_DATA_ERROR]"
        
        # Make encryption functions available globally
        app.jinja_env.globals.update(
            encrypt_field=encrypt_field,
            decrypt_field=decrypt_field
        )
        
        # Store functions in app for use in models
        app.encrypt_field = encrypt_field
        app.decrypt_field = decrypt_field
    
    def _configure_bluetooth_policy(self, app: Flask):
        """Configure strict Bluetooth security policy for deaf users"""
        
        # Store Bluetooth security policy in app config
        app.config['BLUETOOTH_SECURITY_POLICY'] = {
            'web_bluetooth_disabled': True,
            'policy': 'NO_WEB_BLUETOOTH',
            'reason': 'Hearing aid Bluetooth connections must use OS-level pairing only',
            'guidance': {
                'ios': 'Use Settings > Accessibility > Hearing Devices',
                'android': 'Use Settings > Accessibility > Hearing aids', 
                'windows': 'Use Settings > Devices > Bluetooth & other devices',
                'macos': 'Use System Preferences > Bluetooth'
            }
        }
        
        # Add route for Bluetooth security guidance
        @app.route('/security/bluetooth-guidance')
        def bluetooth_security_guidance():
            from flask import render_template
            return render_template('security/bluetooth_guidance.html',
                                 policy=app.config['BLUETOOTH_SECURITY_POLICY'])
    
    def get_limiter(self):
        """Get the rate limiter instance for use in route decorators"""
        return self.limiter

# Global security manager instance
security_manager = SecurityManager()
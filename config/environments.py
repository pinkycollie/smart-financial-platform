"""
Environment-specific configuration for the MBTQ Smart Financial Platform.

This module provides configuration classes for different deployment environments:
- Development: Local development with debug mode enabled
- Staging: Pre-production environment for testing
- Production: Live production environment with security hardened
"""

import os
from typing import Dict, Any


class BaseConfig:
    """Base configuration with common settings across all environments."""
    
    # Application
    APP_NAME = "MBTQ Smart Financial Platform"
    APP_VERSION = "1.0.0"
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/mbtq_platform')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100/minute"
    RATELIMIT_HEADERS_ENABLED = True
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # External APIs - Tax Services
    APRIL_API_URL = os.getenv('APRIL_API_URL', 'https://api.getapril.com')
    APRIL_CLIENT_ID = os.getenv('APRIL_CLIENT_ID')
    APRIL_CLIENT_SECRET = os.getenv('APRIL_CLIENT_SECRET')
    
    # External APIs - Insurance Services
    BOOST_API_URL = os.getenv('BOOST_API_URL', 'https://api.boostinsurance.io')
    BOOST_CLIENT_ID = os.getenv('BOOST_CLIENT_ID')
    BOOST_CLIENT_SECRET = os.getenv('BOOST_CLIENT_SECRET')
    
    # External APIs - Video & ASL Services
    MUX_TOKEN_ID = os.getenv('MUX_TOKEN_ID')
    MUX_TOKEN_SECRET = os.getenv('MUX_TOKEN_SECRET')
    VSL_API_KEY = os.getenv('VSL_API_KEY')
    VSL_API_URL = os.getenv('VSL_API_URL', 'https://api.vsl.com/v1')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    
    # Monitoring
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    SENTRY_ENVIRONMENT = 'development'
    SENTRY_TRACES_SAMPLE_RATE = float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', 1.0))
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TTL', 3600))
    
    # Feature Flags
    FEATURE_RESELLER_SYSTEM = os.getenv('FEATURE_RESELLER_SYSTEM', 'True').lower() == 'true'
    FEATURE_MINIAPPS = os.getenv('FEATURE_MINIAPPS', 'True').lower() == 'true'
    FEATURE_ASL_AI = os.getenv('FEATURE_ASL_AI', 'True').lower() == 'true'
    FEATURE_EDUCATION_MODULE = os.getenv('FEATURE_EDUCATION_MODULE', 'True').lower() == 'true'
    FEATURE_WEBHOOKS = os.getenv('FEATURE_WEBHOOKS', 'True').lower() == 'true'


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Less restrictive security for development
    SESSION_COOKIE_SECURE = False
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    SENTRY_ENVIRONMENT = 'development'
    
    # Mock external APIs for development
    MOCK_EXTERNAL_APIS = os.getenv('MOCK_EXTERNAL_APIS', 'False').lower() == 'true'
    
    # Disable rate limiting for development
    RATELIMIT_ENABLED = False
    
    # Development database
    SQLALCHEMY_ECHO = True  # Log all SQL queries
    
    # Flask Debug Toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class StagingConfig(BaseConfig):
    """Staging/pre-production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Staging environment uses sandbox APIs
    APRIL_ENVIRONMENT = 'sandbox'
    BOOST_ENVIRONMENT = 'sandbox'
    VSL_ENVIRONMENT = 'sandbox'
    
    # Staging monitoring
    SENTRY_ENVIRONMENT = 'staging'
    
    # Moderate rate limiting for staging
    RATELIMIT_DEFAULT = "200/minute"
    
    # Staging-specific logging
    LOG_LEVEL = 'INFO'


class ProductionConfig(BaseConfig):
    """Production environment configuration with enhanced security."""
    
    DEBUG = False
    TESTING = False
    
    # Production uses live APIs
    APRIL_ENVIRONMENT = 'production'
    BOOST_ENVIRONMENT = 'production'
    VSL_ENVIRONMENT = 'production'
    
    # Production monitoring
    SENTRY_ENVIRONMENT = 'production'
    SENTRY_TRACES_SAMPLE_RATE = 0.1  # Sample 10% of transactions
    
    # Strict rate limiting for production
    RATELIMIT_DEFAULT = "100/minute"
    RATELIMIT_STRICT = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Production security enhancements
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Require HTTPS
    PREFERRED_URL_SCHEME = 'https'
    
    # Disable SQL query logging
    SQLALCHEMY_ECHO = False
    
    # Production cache with longer TTL
    CACHE_DEFAULT_TIMEOUT = 7200  # 2 hours


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use test database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://localhost/mbtq_platform_test'
    )
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Mock all external APIs
    MOCK_EXTERNAL_APIS = True
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False
    
    # In-memory cache for tests
    CACHE_TYPE = 'simple'
    
    # Disable Sentry in tests
    SENTRY_DSN = None


# Configuration dictionary
config_by_name: Dict[str, Any] = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name: str = None) -> Any:
    """
    Get configuration class for the specified environment.
    
    Args:
        env_name: Environment name (development, staging, production, testing)
                 If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration class for the specified environment
    """
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(env_name, DevelopmentConfig)

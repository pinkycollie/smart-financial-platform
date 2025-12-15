"""
Logging configuration for MBTQ Smart Financial Platform.

Provides structured logging with support for:
- JSON formatting
- Log levels per environment
- Request/response logging
- Error tracking
- Performance monitoring
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any
from flask import Request, Response, has_request_context, request
from pythonjsonlogger import jsonlogger


class RequestFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes request context."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add request context if available
        if has_request_context():
            log_record['request'] = {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'unknown')
            }
            
            # Add request ID if present
            if hasattr(request, 'id'):
                log_record['request_id'] = request.id


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output in development."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(app):
    """
    Configure logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Get configuration
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', 'json')
    environment = app.config.get('FLASK_ENV', 'development')
    
    # Set root logger level
    logging.getLogger().setLevel(log_level)
    
    # Remove existing handlers
    for handler in logging.getLogger().handlers[:]:
        logging.getLogger().removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if environment == 'development' and log_format != 'json':
        # Use colored formatter for development
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        console_handler.setFormatter(ColoredFormatter(console_format))
    else:
        # Use JSON formatter for production
        console_handler.setFormatter(RequestFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        ))
    
    logging.getLogger().addHandler(console_handler)
    
    # File handler for production
    if environment in ('staging', 'production'):
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/application.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(RequestFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        ))
        logging.getLogger().addHandler(file_handler)
        
        # Error file handler (errors only)
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/errors.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(RequestFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        ))
        logging.getLogger().addHandler(error_handler)
    
    # Set levels for noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Application logger
    app.logger.setLevel(log_level)
    
    app.logger.info(f"Logging configured: level={log_level}, format={log_format}, env={environment}")


def log_request(request: Request):
    """
    Log incoming request details.
    
    Args:
        request: Flask request object
    """
    logger = logging.getLogger('mbtq.request')
    logger.info('Incoming request', extra={
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'unknown')
    })


def log_response(response: Response, duration_ms: float):
    """
    Log outgoing response details.
    
    Args:
        response: Flask response object
        duration_ms: Request processing time in milliseconds
    """
    logger = logging.getLogger('mbtq.response')
    logger.info('Outgoing response', extra={
        'status_code': response.status_code,
        'duration_ms': duration_ms,
        'content_length': response.content_length
    })


def log_error(error: Exception, context: Dict[str, Any] = None):
    """
    Log error with context.
    
    Args:
        error: Exception object
        context: Additional context information
    """
    logger = logging.getLogger('mbtq.error')
    extra = {
        'error_type': type(error).__name__,
        'error_message': str(error)
    }
    
    if context:
        extra.update(context)
    
    logger.error(f"Error occurred: {str(error)}", extra=extra, exc_info=True)


def setup_sentry(app):
    """
    Configure Sentry error tracking.
    
    Args:
        app: Flask application instance
    """
    sentry_dsn = app.config.get('SENTRY_DSN')
    
    if not sentry_dsn:
        app.logger.info("Sentry not configured (SENTRY_DSN not set)")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                FlaskIntegration(),
                SqlalchemyIntegration()
            ],
            environment=app.config.get('SENTRY_ENVIRONMENT', 'development'),
            traces_sample_rate=app.config.get('SENTRY_TRACES_SAMPLE_RATE', 1.0),
            send_default_pii=False,  # Don't send PII by default
            release=app.config.get('APP_VERSION', '1.0.0')
        )
        
        app.logger.info("Sentry error tracking initialized")
    except ImportError:
        app.logger.warning("Sentry SDK not installed. Install with: pip install sentry-sdk")
    except Exception as e:
        app.logger.error(f"Failed to initialize Sentry: {str(e)}")


class RequestLoggingMiddleware:
    """Middleware for logging requests and responses."""
    
    def __init__(self, app):
        """Initialize middleware."""
        self.app = app
        self.logger = logging.getLogger('mbtq.http')
    
    def __call__(self, environ, start_response):
        """Process request and log details."""
        import time
        
        # Record start time
        start_time = time.time()
        
        # Call the application
        def custom_start_response(status, headers, exc_info=None):
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.info('HTTP Request', extra={
                'method': environ.get('REQUEST_METHOD'),
                'path': environ.get('PATH_INFO'),
                'status': status.split()[0],
                'duration_ms': round(duration_ms, 2)
            })
            
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f'mbtq.{name}')

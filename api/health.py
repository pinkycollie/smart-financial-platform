"""
Health check and monitoring endpoints for MBTQ Smart Financial Platform.

Provides endpoints for:
- Basic health checks
- Detailed system status
- Readiness checks for dependencies
- Application metrics
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text


health_bp = Blueprint('health', __name__, url_prefix='/api/internal')


# Store application start time
APP_START_TIME = time.time()


def get_uptime() -> float:
    """Get application uptime in seconds."""
    return time.time() - APP_START_TIME


def check_database() -> Dict[str, Any]:
    """
    Check database connectivity.
    
    Returns:
        Dictionary with status and details
    """
    try:
        from app import db
        # Execute a simple query to verify connection
        db.session.execute(text('SELECT 1'))
        return {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }


def check_redis() -> Dict[str, Any]:
    """
    Check Redis connectivity.
    
    Returns:
        Dictionary with status and details
    """
    try:
        from flask import current_app
        redis_url = current_app.config.get('REDIS_URL')
        if not redis_url or redis_url == 'memory://':
            return {
                'status': 'not_configured',
                'message': 'Redis not configured (using in-memory cache)'
            }
        
        # Try to ping Redis
        import redis
        r = redis.from_url(redis_url)
        r.ping()
        return {
            'status': 'healthy',
            'message': 'Redis connection successful'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }


def get_system_metrics() -> Dict[str, Any]:
    """
    Get system resource metrics.
    
    Returns:
        Dictionary with CPU, memory, and disk metrics
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory': {
                'total_mb': round(memory.total / (1024 * 1024), 2),
                'available_mb': round(memory.available / (1024 * 1024), 2),
                'used_mb': round(memory.used / (1024 * 1024), 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024 * 1024 * 1024), 2),
                'used_gb': round(disk.used / (1024 * 1024 * 1024), 2),
                'free_gb': round(disk.free / (1024 * 1024 * 1024), 2),
                'percent': disk.percent
            }
        }
    except Exception as e:
        return {
            'error': f'Failed to get system metrics: {str(e)}'
        }


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    
    Returns a simple status indicating the application is running.
    This endpoint should be fast and not check external dependencies.
    
    Returns:
        JSON response with status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'uptime_seconds': round(get_uptime(), 2)
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint.
    
    Checks if the application is ready to serve traffic by verifying
    all critical dependencies are available.
    
    Returns:
        JSON response with detailed status of all dependencies
    """
    # Check all dependencies
    db_status = check_database()
    redis_status = check_redis()
    
    # Determine overall status
    is_ready = (
        db_status['status'] == 'healthy' and
        (redis_status['status'] == 'healthy' or redis_status['status'] == 'not_configured')
    )
    
    response = {
        'status': 'ready' if is_ready else 'not_ready',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'checks': {
            'database': db_status,
            'redis': redis_status
        }
    }
    
    status_code = 200 if is_ready else 503
    return jsonify(response), status_code


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness check endpoint.
    
    Indicates whether the application is alive and should not be restarted.
    This is a simple check that the application process is running.
    
    Returns:
        JSON response confirming the application is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@health_bp.route('/health/status', methods=['GET'])
def detailed_status():
    """
    Detailed status endpoint.
    
    Provides comprehensive information about the application status,
    including system metrics and dependency checks.
    
    Returns:
        JSON response with detailed status information
    """
    db_status = check_database()
    redis_status = check_redis()
    system_metrics = get_system_metrics()
    
    return jsonify({
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': current_app.config.get('APP_VERSION', '1.0.0'),
        'environment': current_app.config.get('FLASK_ENV', 'unknown'),
        'uptime_seconds': round(get_uptime(), 2),
        'dependencies': {
            'database': db_status,
            'redis': redis_status
        },
        'system': system_metrics
    }), 200


@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Application metrics endpoint.
    
    Provides basic application metrics for monitoring systems.
    
    Returns:
        JSON response with application metrics
    """
    system_metrics = get_system_metrics()
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime_seconds': round(get_uptime(), 2),
        'system': system_metrics,
        'application': {
            'version': current_app.config.get('APP_VERSION', '1.0.0'),
            'environment': current_app.config.get('FLASK_ENV', 'unknown')
        }
    }), 200

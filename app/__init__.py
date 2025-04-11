import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf.csrf import CSRFProtect

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize CSRF protection
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Set secret key
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Fix for proper HTTPS URLs behind proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes.fintech.routes import fintech_bp
    app.register_blueprint(fintech_bp, url_prefix='/fintech')
    
    from app.routes.accessibility.routes import accessibility_bp
    app.register_blueprint(accessibility_bp, url_prefix='/accessibility')
    
    # Create database tables
    with app.app_context():
        import app.models
        import app.services.april.models
        db.create_all()
    
    return app

import os

class Config:
    """Base configuration."""
    # Flask
    DEBUG = True
    TESTING = False
    
    # Security
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
    WTF_CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # April API
    APRIL_API_URL = os.environ.get("APRIL_API_URL", "https://api.getapril.com")
    APRIL_CLIENT_ID = os.environ.get("APRIL_CLIENT_ID", "")
    APRIL_CLIENT_SECRET = os.environ.get("APRIL_CLIENT_SECRET", "")
    
    # Mux Video
    MUX_TOKEN_ID = os.environ.get("MUX_TOKEN_ID", "")
    MUX_TOKEN_SECRET = os.environ.get("MUX_TOKEN_SECRET", "")
    
    # Accessibility
    ASL_VIDEOS_ENABLED = True
    DEAF_SUPPORT_BOT_ENABLED = True

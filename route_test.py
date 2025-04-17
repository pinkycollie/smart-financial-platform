"""
Test script to run the demo route directly
"""

from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.secret_key = "test-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import routes from demo file
from routes.demo import demo_bp
app.register_blueprint(demo_bp)

# Add a redirect for the root path
@app.route('/')
def index():
    """Redirect to the demo page"""
    return """
    <html>
    <head>
        <title>DEAF FIRST Platform Demo</title>
        <meta http-equiv="refresh" content="0;url=/demo" />
    </head>
    <body>
        <p>Redirecting to <a href="/demo">demo page</a>...</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    with app.app_context():
        # Import models for creating tables
        import models
        import models_additions
        import models_education
        import models_licensing
        import models_reseller
        
        # Create tables if they don't exist
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
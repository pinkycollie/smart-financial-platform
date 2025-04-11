from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("SESSION_SECRET", "mbtq-development-key")
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

# Define routes
@app.route('/')
def index():
    return jsonify({
        'message': 'MbTQ Financial Platform API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'fintech': {
                'tax_filing': '/fintech/tax-filing',
                'financial_profile': '/fintech/financial-profile',
                'dashboard': '/fintech/dashboard'
            },
            'accessibility': {
                'asl_videos': '/accessibility/asl-videos',
                'deaf_support_bot': '/accessibility/deaf-support-bot',
                'settings': '/accessibility/settings'
            }
        }
    })

@app.route('/fintech/dashboard')
def fintech_dashboard():
    return jsonify({
        'message': 'Financial Dashboard',
        'status': 'under development'
    })

@app.route('/fintech/tax-filing')
def tax_filing():
    return jsonify({
        'message': 'Tax Filing Service',
        'status': 'under development'
    })

@app.route('/fintech/financial-profile')
def financial_profile():
    return jsonify({
        'message': 'Financial Profile Service',
        'status': 'under development'
    })

@app.route('/accessibility/asl-videos')
def asl_videos():
    return jsonify({
        'message': 'ASL Videos Library',
        'status': 'under development'
    })

@app.route('/accessibility/deaf-support-bot')
def deaf_support_bot():
    return jsonify({
        'message': 'Deaf Support Bot',
        'status': 'under development'
    })

@app.route('/accessibility/settings')
def accessibility_settings():
    return jsonify({
        'message': 'Accessibility Settings',
        'status': 'under development'
    })

# Import models (needed for creating tables)
import models

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
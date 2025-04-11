from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
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

# Configure API services
app.config['MUX_TOKEN_ID'] = os.environ.get('MUX_TOKEN_ID', '')
app.config['MUX_TOKEN_SECRET'] = os.environ.get('MUX_TOKEN_SECRET', '')
app.config['APRIL_API_URL'] = os.environ.get('APRIL_API_URL', 'https://api.getapril.com')
app.config['APRIL_CLIENT_ID'] = os.environ.get('APRIL_CLIENT_ID', '')
app.config['APRIL_CLIENT_SECRET'] = os.environ.get('APRIL_CLIENT_SECRET', '')
app.config['BOOST_API_URL'] = os.environ.get('BOOST_API_URL', 'https://api.boostinsurance.io')
app.config['BOOST_CLIENT_ID'] = os.environ.get('BOOST_CLIENT_ID', '')
app.config['BOOST_CLIENT_SECRET'] = os.environ.get('BOOST_CLIENT_SECRET', '')

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import routes modules
from routes.fintech.insurance import insurance_bp

# Register blueprints
app.register_blueprint(insurance_bp)

# Define routes
@app.route('/')
def index():
    """Home page of the MbTQ Financial Platform"""
    return render_template('index.html', title='MbTQ Financial Platform')

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
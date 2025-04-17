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
from routes.fintech.business import business_bp
from routes.vsl_communication import vsl_bp

# Register blueprints
app.register_blueprint(insurance_bp)
app.register_blueprint(business_bp)
app.register_blueprint(vsl_bp)

# Define routes
@app.route('/')
def index():
    """Home page of the MbTQ Financial Platform"""
    return render_template('index.html', title='MbTQ Financial Platform')

@app.route('/dashboard')
def dashboard():
    """Main dashboard with simple, accessible UI"""
    # Example data for demonstration
    financial_summary = {
        'total_assets': 145000,
        'total_liabilities': 85000,
        'net_worth': 60000
    }
    
    recent_transactions = [
        {'date': '2025-04-15', 'description': 'Salary Deposit', 'amount': 3500, 'type': 'income'},
        {'date': '2025-04-14', 'description': 'Grocery Shopping', 'amount': 120, 'type': 'expense'},
        {'date': '2025-04-13', 'description': 'Electric Bill', 'amount': 85, 'type': 'expense'},
        {'date': '2025-04-10', 'description': 'Freelance Payment', 'amount': 750, 'type': 'income'}
    ]
    
    upcoming_tasks = [
        {'due_date': '2025-04-25', 'description': 'Tax Filing Deadline', 'priority': 'high'},
        {'due_date': '2025-05-01', 'description': 'Insurance Renewal', 'priority': 'medium'},
        {'due_date': '2025-05-15', 'description': 'Retirement Fund Review', 'priority': 'low'}
    ]
    
    return render_template('dashboard.html', 
                          title='Financial Dashboard',
                          financial_summary=financial_summary,
                          recent_transactions=recent_transactions,
                          upcoming_tasks=upcoming_tasks)
                          
@app.route('/investor-demo')
def investor_demo():
    """Demo page specially designed for investors, shareholders, and potential partners"""
    
    # Market opportunity data
    market_data = {
        'deaf_population': 37000000,  # US Deaf/HOH population
        'market_size': 250000000000,  # $250B estimated market size
        'unserved_percentage': 78,    # % of deaf population underserved
        'projected_growth': 14.5      # Annual growth % in deaf fintech
    }
    
    # Impact metrics
    impact_metrics = {
        'accessibility_increase': 85,  # % increase in financial access 
        'cost_savings': 35,           # % cost savings vs traditional services
        'financial_literacy': 65      # % improvement in financial literacy
    }
    
    # Competitive advantage
    advantages = [
        {
            'title': 'Deaf First Design',
            'description': 'Built from the ground up for the deaf community rather than as an afterthought.',
            'icon': 'fas fa-universal-access'
        },
        {
            'title': 'Multi-Layer ASL Integration',
            'description': 'Comprehensive video ASL integration through Mux, SignASL, and VSL Labs technologies.',
            'icon': 'fas fa-hands'
        },
        {
            'title': 'Specialized Insurance Products',
            'description': 'First-of-its-kind deaf-specific insurance coverage through Boost Insurance API.',
            'icon': 'fas fa-shield-alt'
        },
        {
            'title': 'Holistic Financial Approach',
            'description': 'Complete suite spanning tax, insurance, real estate, business and estate planning.',
            'icon': 'fas fa-chart-line'
        }
    ]
    
    # Revenue streams
    revenue_streams = [
        {'name': 'Premium Subscriptions', 'projected_percentage': 45, 'color': '#0066CC'},
        {'name': 'Insurance Commissions', 'projected_percentage': 30, 'color': '#00AA55'},
        {'name': 'Tax Preparation Fees', 'projected_percentage': 15, 'color': '#FFAA00'},
        {'name': 'Partner Referrals', 'projected_percentage': 10, 'color': '#FF5500'}
    ]
    
    # Roadmap milestones 
    roadmap = [
        {'date': '2025 Q2', 'milestone': 'Public Beta Launch', 'status': 'in_progress'},
        {'date': '2025 Q3', 'milestone': 'Insurance Integration', 'status': 'upcoming'},
        {'date': '2025 Q4', 'milestone': 'ASL Video Library Complete', 'status': 'upcoming'},
        {'date': '2026 Q1', 'milestone': 'Full Platform Launch', 'status': 'upcoming'},
        {'date': '2026 Q2', 'milestone': 'Mobile App Release', 'status': 'upcoming'}
    ]
    
    # Team members
    team = [
        {'name': 'Jane Doe', 'role': 'CEO & Founder', 'deaf': True, 'photo': 'team1.jpg'},
        {'name': 'John Smith', 'role': 'CTO', 'deaf': False, 'photo': 'team2.jpg'},
        {'name': 'Sarah Johnson', 'role': 'Director of Accessibility', 'deaf': True, 'photo': 'team3.jpg'},
        {'name': 'Michael Chen', 'role': 'Financial Services Lead', 'deaf': False, 'photo': 'team4.jpg'}
    ]
    
    return render_template('investor_demo.html',
                          title='Investor Demo - DEAF FIRST Platform',
                          market_data=market_data,
                          impact_metrics=impact_metrics,
                          advantages=advantages,
                          revenue_streams=revenue_streams,
                          roadmap=roadmap,
                          team=team)

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
    # Drop all tables if they exist and recreate
    db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
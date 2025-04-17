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

try:
    from routes.sitemap import sitemap_bp
    from routes.advisors import advisors_bp
except ImportError as e:
    app.logger.warning(f"Could not import some blueprints: {e}")

# Register blueprints
app.register_blueprint(insurance_bp)
app.register_blueprint(business_bp)
app.register_blueprint(vsl_bp)

# Register new blueprints
try:
    app.register_blueprint(sitemap_bp)
    app.logger.info("Sitemap blueprint registered")
except NameError:
    app.logger.warning("Sitemap blueprint not available")

try:
    app.register_blueprint(advisors_bp)
    app.logger.info("Advisors blueprint registered")
except NameError:
    app.logger.warning("Advisors blueprint not available")

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

@app.route('/investor-portal')
def investor_portal():
    """Portal page for investors, shareholders, and beta testers"""
    # Example data
    investments = [
        {'id': 1, 'amount': 150000, 'date': '2024-01-15', 'type': 'equity', 'roi': 12.5},
        {'id': 2, 'amount': 75000, 'date': '2024-03-22', 'type': 'convertible', 'roi': 10.0}
    ]
    
    platform_metrics = {
        'active_users': 12450,
        'retention_rate': 82.5,
        'new_signups_monthly': 2300,
        'avg_session_duration': 24.5
    }
    
    shareholder_updates = [
        {'id': 1, 'title': 'Q1 2025 Financial Results', 'date': '2025-04-10', 'confidentiality': 'shareholders'},
        {'id': 2, 'title': 'New Deaf-First Features Launched', 'date': '2025-03-28', 'confidentiality': 'public'},
        {'id': 3, 'title': 'Strategic Partnership with SignASL', 'date': '2025-03-15', 'confidentiality': 'investors'}
    ]
    
    beta_features = [
        {'id': 1, 'name': 'AI-Powered ASL Translation', 'status': 'active', 'release_date': '2025-05-15'},
        {'id': 2, 'name': 'Real-time Financial Advice with ASL', 'status': 'in_testing', 'release_date': '2025-06-01'},
        {'id': 3, 'name': 'Multi-modal Communication Hub', 'status': 'planned', 'release_date': '2025-07-01'}
    ]
    
    return render_template('investor_portal.html',
                          title='Investor Portal - DEAF FIRST',
                          investments=investments,
                          platform_metrics=platform_metrics,
                          shareholder_updates=shareholder_updates,
                          beta_features=beta_features)

# Import models (needed for creating tables)
import models
import models_additions
import models_education
import models_licensing
import models_reseller
from models_import import *

# Create tables and seed data
with app.app_context():
    # Create tables if they don't exist
    # db.drop_all()  # Disabled to preserve existing data
    db.create_all()
    
    # Add seed data for education categories
    from datetime import datetime
    
    # Check if categories already exist
    if models_education.EducationCategory.query.count() == 0:
        app.logger.info("Creating seed data for education categories")
        categories = [
            {
                'name': 'Personal Finance Basics',
                'description': 'Fundamental concepts of personal finance with ASL support',
                'icon': 'wallet',
                'display_order': 1
            },
            {
                'name': 'Investing',
                'description': 'Learn about investing principles and strategies with ASL support',
                'icon': 'chart-line',
                'display_order': 2
            },
            {
                'name': 'Insurance',
                'description': 'Understanding insurance concepts and products with ASL support',
                'icon': 'shield-alt',
                'display_order': 3
            },
            {
                'name': 'Retirement Planning',
                'description': 'Prepare for retirement with these ASL-supported modules',
                'icon': 'umbrella-beach',
                'display_order': 4
            }
        ]
        
        for category_data in categories:
            category = models_education.EducationCategory(**category_data)
            db.session.add(category)
        
        # Add a sample module
        basic_category = models_education.EducationCategory.query.filter_by(name='Personal Finance Basics').first()
        if basic_category:
            module = models_education.EducationModule(
                category_id=basic_category.id,
                title='Budgeting 101',
                slug='budgeting-101',
                summary='Learn the basics of creating and maintaining a budget with ASL support',
                difficulty_level='beginner',
                estimated_time=30,
                has_asl=True,
                captions_available=True,
                published=True,
                published_at=datetime.utcnow()
            )
            db.session.add(module)
            # Commit to get the module ID
            db.session.commit()
            
            # Add some lessons to the module
            lessons = [
                {
                    'module_id': module.id,
                    'title': 'What is a Budget?',
                    'content': '<p>A budget is a plan that helps you manage your money. It shows your income and expenses for a specific period of time.</p><p>Creating a budget helps you track where your money is going and make sure you have enough for your needs and goals.</p>',
                    'order': 1
                },
                {
                    'module_id': module.id,
                    'title': 'Setting Financial Goals',
                    'content': '<p>Financial goals give your budget purpose. Short-term goals might include saving for a vacation, while long-term goals might include saving for retirement.</p><p>SMART goals are Specific, Measurable, Achievable, Relevant, and Time-bound.</p>',
                    'order': 2
                },
                {
                    'module_id': module.id,
                    'title': 'Tracking Income and Expenses',
                    'content': '<p>To create an effective budget, you need to know how much money you have coming in and going out.</p><p>Track all sources of income and categorize your expenses to get a clear picture of your financial situation.</p>',
                    'order': 3
                }
            ]
            
            for lesson_data in lessons:
                lesson = models_education.EducationLesson(**lesson_data)
                db.session.add(lesson)
        
        # Commit all the seed data
        db.session.commit()
        app.logger.info("Seed data created successfully")

# Register blueprints
try:
    from routes.education import education_bp
    app.register_blueprint(education_bp)
    app.logger.info("Education blueprint registered")
except Exception as e:
    app.logger.error(f"Failed to register education blueprint: {e}")

# Register reseller blueprints
try:
    from routes.reseller.portal import reseller_portal_bp
    from routes.reseller.management import reseller_management_bp
    app.register_blueprint(reseller_portal_bp)
    app.register_blueprint(reseller_management_bp)
    app.logger.info("Reseller blueprints registered")
except Exception as e:
    app.logger.error(f"Failed to register reseller blueprints: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
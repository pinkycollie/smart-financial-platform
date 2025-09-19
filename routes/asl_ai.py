"""
MBTQ Group LLC ASL AI Routes
API endpoints for Sign Language AI support, appointment booking, and authentication
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
import json
import asyncio
import logging

from services.ai.asl_ai_service import asl_ai_service
from models import User
from simple_app import db
from config.security import security_manager
from services.auth.auth_service import auth_service

logger = logging.getLogger(__name__)

# Create blueprint
asl_ai_bp = Blueprint('asl_ai', __name__, url_prefix='/api/asl')
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

# ASL AI API Routes
@asl_ai_bp.route('/interpret-text', methods=['POST'])
@security_manager.get_limiter().limit("20 per minute")
async def interpret_text():
    """Convert text to ASL-friendly explanation"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'status': 'error', 'message': 'Text is required'}), 400
        
        text = data['text']
        context = data.get('context', 'general')
        
        result = await asl_ai_service.interpret_text_to_asl(text, context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"ASL text interpretation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to interpret text. Please try again.'
        }), 500

@asl_ai_bp.route('/explain-term', methods=['POST'])
@security_manager.get_limiter().limit("20 per minute")
def explain_term():
    """Get ASL explanation for a financial term"""
    try:
        data = request.get_json()
        if not data or 'term' not in data:
            return jsonify({'status': 'error', 'message': 'Term is required'}), 400
        
        term = data['term'].lower()
        context = data.get('context', 'financial_terms')
        
        # Run async function synchronously for this endpoint
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                asl_ai_service.interpret_text_to_asl(f"Explain the term '{term}' in simple language", context)
            )
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"ASL term explanation error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to explain term. Please try again.'
        }), 500

@asl_ai_bp.route('/support', methods=['POST'])
@security_manager.get_limiter().limit("10 per minute")
def real_time_support():
    """Provide real-time ASL support"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'status': 'error', 'message': 'Message is required'}), 400
        
        message = data['message']
        context = data.get('context', {})
        
        # Add user context if logged in
        if current_user.is_authenticated:
            context.update({
                'user_profile': {
                    'communication_preference': getattr(current_user, 'preferred_communication_method', 'ASL_video'),
                    'accessibility_settings': getattr(current_user, 'accessibility_settings', {})
                }
            })
        
        # Run async function synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                asl_ai_service.provide_real_time_support(message, context)
            )
            return jsonify(result)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"ASL real-time support error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to provide support. Please try again.'
        }), 500

@asl_ai_bp.route('/emergency-phrases', methods=['GET'])
def get_emergency_phrases():
    """Get emergency ASL phrases"""
    try:
        result = asl_ai_service.get_asl_emergency_phrases()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Emergency phrases error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load emergency phrases'
        }), 500

# Authentication Routes
@auth_bp.route('/register', methods=['GET', 'POST'])
@security_manager.get_limiter().limit("5 per minute")
def register():
    """User registration with accessibility preferences"""
    if request.method == 'GET':
        return render_template('auth/register.html', title='Create Account')
    
    try:
        form_data = request.form.to_dict()
        
        success, message, user = auth_service.register_user(form_data)
        
        if success:
            flash(message, 'success')
            # Auto-login after successful registration
            login_user(user)
            return redirect(url_for('asl_dashboard'))
        else:
            flash(message, 'error')
            return render_template('auth/register.html', title='Create Account')
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('auth/register.html', title='Create Account')

@auth_bp.route('/login', methods=['GET', 'POST'])
@security_manager.get_limiter().limit("5 per minute")
def login():
    """User login with accessibility support"""
    if request.method == 'GET':
        return render_template('auth/login.html', title='Sign In')
    
    try:
        login_identifier = request.form.get('email_or_username', '').strip()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        success, message, user = auth_service.authenticate_user(
            login_identifier, password, remember_me
        )
        
        if success:
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('asl_dashboard'))
        else:
            flash(message, 'error')
            return render_template('auth/login.html', title='Sign In')
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('auth/login.html', title='Sign In')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    auth_service.logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'GET':
        return render_template('auth/profile.html', title='My Profile')
    
    try:
        profile_data = request.form.to_dict()
        success, message = auth_service.update_user_profile(current_user.id, profile_data)
        
        flash(message, 'success' if success else 'error')
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        flash('Failed to update profile. Please try again.', 'error')
        return redirect(url_for('auth.profile'))

@auth_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """User accessibility preferences"""
    if request.method == 'GET':
        return render_template('auth/preferences.html', title='Accessibility Settings')
    
    try:
        preferences_data = request.form.to_dict()
        success, message = auth_service.update_user_preferences(current_user.id, preferences_data)
        
        flash(message, 'success' if success else 'error')
        return redirect(url_for('auth.preferences'))
        
    except Exception as e:
        logger.error(f"Preferences update error: {e}")
        flash('Failed to update preferences. Please try again.', 'error')
        return redirect(url_for('auth.preferences'))

# Appointment Routes
@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Book ASL interpretation appointment"""
    if request.method == 'GET':
        return render_template('appointments/book.html', title='Book Appointment')
    
    try:
        form_data = request.form.to_dict()
        
        # For now, just store appointment request info in user's accessibility settings
        if hasattr(current_user, 'accessibility_settings'):
            appointments = current_user.accessibility_settings.get('appointments', [])
            appointments.append({
                'appointment_type': form_data.get('appointment_type', 'asl_interpretation'),
                'scheduled_date': f"{form_data.get('date')} {form_data.get('time')}",
                'duration_minutes': int(form_data.get('duration_minutes', 60)),
                'service_title': form_data.get('service_title', ''),
                'status': 'requested',
                'created_at': datetime.utcnow().isoformat()
            })
            current_user.accessibility_settings['appointments'] = appointments
            db.session.commit()
        
        flash('Appointment request submitted successfully! We will confirm your appointment soon.', 'success')
        return redirect(url_for('appointments.my_appointments'))
            
    except Exception as e:
        logger.error(f"Appointment booking error: {e}")
        flash('Failed to book appointment. Please try again.', 'error')
        return redirect(url_for('asl_dashboard'))

@appointments_bp.route('/my-appointments')
@login_required
def my_appointments():
    """View user's appointments"""
    try:
        appointments = []
        if hasattr(current_user, 'accessibility_settings') and current_user.accessibility_settings:
            appointments = current_user.accessibility_settings.get('appointments', [])
        
        return render_template('appointments/my_appointments.html', 
                             title='My Appointments', 
                             appointments=appointments)
                             
    except Exception as e:
        logger.error(f"My appointments error: {e}")
        flash('Failed to load appointments.', 'error')
        return redirect(url_for('asl_dashboard'))

@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        if hasattr(current_user, 'accessibility_settings') and current_user.accessibility_settings:
            appointments = current_user.accessibility_settings.get('appointments', [])
            if appointment_id < len(appointments):
                appointments[appointment_id]['status'] = 'cancelled'
                appointments[appointment_id]['cancelled_at'] = datetime.utcnow().isoformat()
                current_user.accessibility_settings['appointments'] = appointments
                db.session.commit()
                flash('Appointment cancelled successfully.', 'success')
            else:
                flash('Appointment not found.', 'error')
        else:
            flash('Appointment not found.', 'error')
        
        return redirect(url_for('appointments.my_appointments'))
        
    except Exception as e:
        logger.error(f"Cancel appointment error: {e}")
        flash('Failed to cancel appointment.', 'error')
        return redirect(url_for('appointments.my_appointments'))

# Main Dashboard Route
def register_asl_dashboard_route(app):
    """Register the main ASL dashboard route"""
    
    @app.route('/asl-dashboard')
    @login_required
    def asl_dashboard():
        """Main ASL dashboard with video and context sidebar"""
        try:
            # Get user's context for AI
            user_context = {
                'communication_preference': getattr(current_user, 'preferred_communication_method', 'ASL_video'),
                'accessibility_settings': getattr(current_user, 'accessibility_settings', {})
            }
            
            # Sample context content - this would be dynamic based on user's current activity
            context_content = """
            <h3>Welcome to Your Financial Dashboard</h3>
            <p>This is your personalized financial services hub designed for the deaf and hard-of-hearing community.</p>
            
            <h4>Available Services:</h4>
            <ul>
                <li><strong>Insurance Products:</strong> Specialized coverage including Interpreter Insurance and Health Plus</li>
                <li><strong>Tax Preparation:</strong> Professional tax services with ASL support</li>
                <li><strong>Financial Education:</strong> Learn about budgeting, investing, and retirement planning</li>
                <li><strong>ASL Interpretation:</strong> Book live interpreters for financial consultations</li>
            </ul>
            
            <div class="visual-alert visual-alert-info mt-3">
                <h6><i class="fas fa-lightbulb me-2"></i>Quick Tip</h6>
                <p>Use the video panel on the left for ASL explanations of any financial terms. Just click on highlighted terms or ask the AI assistant!</p>
            </div>
            """
            
            # Sample document links
            document_links = [
                {'title': 'Tax Forms', 'url': '/resources/tax-forms', 'type': 'pdf'},
                {'title': 'Insurance Applications', 'url': '/resources/insurance-forms', 'type': 'contract'},
                {'title': 'Financial Planning Guide', 'url': '/resources/financial-guide', 'type': 'alt'}
            ]
            
            return render_template('asl_dashboard.html',
                                 title='ASL Dashboard',
                                 page_title='Financial Services Dashboard',
                                 context_title='Your Financial Hub',
                                 context_content=context_content,
                                 document_links=document_links,
                                 notary_required=True)
                                 
        except Exception as e:
            logger.error(f"ASL dashboard error: {e}")
            flash('Error loading dashboard. Please refresh the page.', 'error')
            return redirect(url_for('dashboard'))


# Export the blueprints
__all__ = ['asl_ai_bp', 'auth_bp', 'appointments_bp', 'register_asl_dashboard_route']
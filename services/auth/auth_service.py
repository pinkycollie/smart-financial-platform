"""
MBTQ Group LLC Authentication Service
Handles user registration, login, and session management with deaf community accessibility
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from simple_app import db
from models import User

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service with accessibility-focused features"""
    
    def __init__(self, app=None):
        self.app = app
        self.login_manager = LoginManager()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the authentication service with Flask app"""
        self.login_manager.init_app(app)
        self.login_manager.login_view = 'auth.login'
        self.login_manager.login_message = 'Please log in to access this page.'
        self.login_manager.login_message_category = 'info'
        
        # User loader for Flask-Login
        @self.login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    def register_user(self, form_data: Dict[str, Any]) -> Tuple[bool, str, Optional[User]]:
        """
        Register a new user with accessibility preferences
        
        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            # Validate required fields
            required_fields = ['email', 'username', 'password']
            for field in required_fields:
                if not form_data.get(field):
                    return False, f"Please provide your {field.replace('_', ' ')}", None
            
            # Check if user already exists
            existing_email = User.query.filter_by(email=form_data['email'].lower().strip()).first()
            if existing_email:
                return False, "An account with this email already exists", None
            
            existing_username = User.query.filter_by(username=form_data['username'].lower().strip()).first()
            if existing_username:
                return False, "This username is already taken", None
            
            # Create new user with existing model structure
            user = User()
            user.email = form_data['email'].lower().strip()
            user.username = form_data['username'].lower().strip()
            user.set_password(form_data['password'])
            user.first_name = form_data.get('first_name', '').strip()
            user.last_name = form_data.get('last_name', '').strip()
            user.account_type = 'deaf_user'
            user.preferred_communication_method = form_data.get('communication_preference', 'ASL_video')
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {user.username} ({user.email})")
            
            return True, "Account created successfully! You can now log in.", user
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error during registration: {e}")
            return False, "An error occurred creating your account. Please try again.", None
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {e}")
            return False, "An unexpected error occurred. Please try again later.", None
    
    def _create_default_preferences(self, user_id: int, form_data: Dict[str, Any]):
        """Create default user preferences using accessibility_settings JSON field"""
        try:
            user = User.query.get(user_id)
            if user:
                user.accessibility_settings = {
                    'high_contrast_mode': form_data.get('high_contrast_mode', False),
                    'large_text': form_data.get('large_text', False),
                    'reduced_motion': form_data.get('reduced_motion', False),
                    'color_scheme': form_data.get('color_scheme', 'light'),
                    'language_preference': form_data.get('language_preference', 'en')
                }
                db.session.commit()
            
        except Exception as e:
            logger.error(f"Error creating default preferences for user {user_id}: {e}")
    
    def authenticate_user(self, login_identifier: str, password: str, remember_me: bool = False) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user by email or username
        
        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            if not login_identifier or not password:
                return False, "Please provide both email/username and password", None
            
            # Find user by email or username
            user = User.query.filter(
                (User.email == login_identifier.lower().strip()) |
                (User.username == login_identifier.lower().strip())
            ).first()
            
            if not user:
                return False, "No account found with that email or username", None
            
            if user.account_status != 'active':
                return False, "Your account has been deactivated. Please contact support.", None
            
            if not user.check_password(password):
                return False, "Incorrect password", None
            
            # Log successful login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log in user with Flask-Login
            login_user(user, remember=remember_me)
            
            logger.info(f"User logged in: {user.username}")
            
            return True, "Login successful!", user
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "An error occurred during login. Please try again.", None
    
    def logout_user(self) -> bool:
        """Log out the current user"""
        try:
            if current_user.is_authenticated:
                username = current_user.username
                logout_user()
                logger.info(f"User logged out: {username}")
                return True
            return True
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update user profile information"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Update allowed fields
            updatable_fields = [
                'first_name', 'last_name', 'phone', 'emergency_contact', 
                'emergency_phone', 'communication_preference', 'needs_interpreter',
                'preferred_interpreter_gender', 'preferred_interpreter_specialty',
                'hearing_level', 'assistive_devices'
            ]
            
            for field in updatable_fields:
                if field in profile_data:
                    if field == 'communication_preference':
                        setattr(user, field, CommunicationPreference(profile_data[field]))
                    else:
                        setattr(user, field, profile_data[field])
            
            db.session.commit()
            logger.info(f"Profile updated for user: {user.username}")
            
            return True, "Profile updated successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {e}")
            return False, "Failed to update profile. Please try again."
    
    def update_user_preferences(self, user_id: int, preferences_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Update user accessibility preferences"""
        try:
            preferences = UserPreference.query.filter_by(user_id=user_id).first()
            if not preferences:
                # Create new preferences if they don't exist
                preferences = UserPreference(user_id=user_id)
                db.session.add(preferences)
            
            # Update allowed preference fields
            updatable_fields = [
                'high_contrast_mode', 'large_text', 'reduced_motion', 'color_scheme',
                'default_appointment_type', 'preferred_appointment_time', 'notification_methods',
                'language_preference', 'emergency_contact_1_name', 'emergency_contact_1_phone',
                'emergency_contact_1_relation', 'emergency_contact_2_name', 'emergency_contact_2_phone',
                'emergency_contact_2_relation', 'hearing_aid_details', 'cochlear_implant_details',
                'other_assistive_technology', 'allergy_information', 'medication_information',
                'allow_video_recording', 'allow_session_notes', 'allow_follow_up_contact',
                'allow_marketing_communications'
            ]
            
            for field in updatable_fields:
                if field in preferences_data:
                    setattr(preferences, field, preferences_data[field])
            
            preferences.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Preferences updated for user: {user_id}")
            
            return True, "Preferences updated successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Preferences update error: {e}")
            return False, "Failed to update preferences. Please try again."
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            if not check_password_hash(user.password_hash, current_password):
                return False, "Current password is incorrect"
            
            if len(new_password) < 8:
                return False, "New password must be at least 8 characters long"
            
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            logger.info(f"Password changed for user: {user.username}")
            
            return True, "Password changed successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Password change error: {e}")
            return False, "Failed to change password. Please try again."
    
    def get_user_accessibility_context(self, user_id: int) -> Dict[str, Any]:
        """Get user's accessibility context for AI services"""
        try:
            user = User.query.get(user_id)
            preferences = UserPreference.query.filter_by(user_id=user_id).first()
            
            if not user:
                return {}
            
            context = {
                'user_profile': {
                    'communication_preference': user.communication_preference.value if user.communication_preference else 'asl_video',
                    'needs_interpreter': user.needs_interpreter,
                    'hearing_level': user.hearing_level,
                    'assistive_devices': user.assistive_devices
                },
                'accessibility_needs': {
                    'high_contrast': preferences.high_contrast_mode if preferences else False,
                    'large_text': preferences.large_text if preferences else False,
                    'reduced_motion': preferences.reduced_motion if preferences else False,
                    'color_scheme': preferences.color_scheme if preferences else 'light'
                },
                'communication_method': user.communication_preference.value if user.communication_preference else 'asl_video',
                'emergency_contacts': []
            }
            
            # Add emergency contacts if preferences exist
            if preferences:
                if preferences.emergency_contact_1_name:
                    context['emergency_contacts'].append({
                        'name': preferences.emergency_contact_1_name,
                        'phone': preferences.emergency_contact_1_phone,
                        'relation': preferences.emergency_contact_1_relation
                    })
                if preferences.emergency_contact_2_name:
                    context['emergency_contacts'].append({
                        'name': preferences.emergency_contact_2_name,
                        'phone': preferences.emergency_contact_2_phone,
                        'relation': preferences.emergency_contact_2_relation
                    })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting accessibility context for user {user_id}: {e}")
            return {}
    
    def require_email_verification(self, user_id: int) -> bool:
        """Check if user requires email verification"""
        try:
            user = User.query.get(user_id)
            return user and not user.email_verified_at
        except Exception:
            return True  # Err on the side of caution
    
    def verify_email(self, user_id: int) -> Tuple[bool, str]:
        """Mark user email as verified"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"
            
            user.email_verified_at = datetime.utcnow()
            user.is_verified = True
            db.session.commit()
            
            logger.info(f"Email verified for user: {user.username}")
            
            return True, "Email verified successfully"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Email verification error: {e}")
            return False, "Failed to verify email"


# Global auth service instance
auth_service = AuthService()
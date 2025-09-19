"""
MBTQ Group LLC Appointment Booking Models
Handles ASL interpretation appointments, user profiles, and scheduling
"""

from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app import db


class AppointmentType(Enum):
    ASL_INTERPRETATION = "asl_interpretation"
    INSURANCE_CONSULTATION = "insurance_consultation"
    TAX_PREPARATION = "tax_preparation"
    FINANCIAL_EDUCATION = "financial_education"
    LEGAL_DOCUMENT_REVIEW = "legal_document_review"
    NOTARY_SERVICE = "notary_service"


class AppointmentStatus(Enum):
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CommunicationPreference(Enum):
    ASL_VIDEO = "asl_video"
    WRITTEN_CHAT = "written_chat"
    BOTH = "both"
    VOICE_WITH_INTERPRETER = "voice_with_interpreter"


class User(db.Model):
    """Enhanced user model with deaf community accessibility features"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    
    # Personal Information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    
    # Accessibility Preferences
    communication_preference = Column(SQLEnum(CommunicationPreference), 
                                    default=CommunicationPreference.ASL_VIDEO)
    needs_interpreter = Column(Boolean, default=True)
    preferred_interpreter_gender = Column(String(20))
    preferred_interpreter_specialty = Column(String(100))
    hearing_level = Column(String(50))  # deaf, hard_of_hearing, hearing
    assistive_devices = Column(Text)  # JSON string of devices used
    
    # Account Settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    email_verified_at = Column(DateTime)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    user_preferences = relationship("UserPreference", back_populates="user", 
                                  cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_communication_needs(self):
        """Return user's communication accessibility needs"""
        return {
            'communication_preference': self.communication_preference.value if self.communication_preference else 'asl_video',
            'needs_interpreter': self.needs_interpreter,
            'preferred_interpreter_gender': self.preferred_interpreter_gender,
            'preferred_interpreter_specialty': self.preferred_interpreter_specialty,
            'hearing_level': self.hearing_level,
            'assistive_devices': self.assistive_devices
        }


class Appointment(db.Model):
    """ASL interpretation and financial services appointments"""
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    
    # User and scheduling information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    appointment_type = Column(SQLEnum(AppointmentType), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.REQUESTED)
    
    # Scheduling details
    scheduled_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default='America/New_York')
    
    # Service details
    service_title = Column(String(200), nullable=False)
    service_description = Column(Text)
    special_requirements = Column(Text)
    preparation_notes = Column(Text)
    
    # Interpreter requirements
    interpreter_required = Column(Boolean, default=True)
    interpreter_specialty = Column(String(100))
    interpreter_gender_preference = Column(String(20))
    interpreter_assigned = Column(String(100))  # Interpreter name/ID when assigned
    
    # Meeting information
    meeting_link = Column(String(500))  # Video conference link
    meeting_room_id = Column(String(100))
    access_code = Column(String(50))
    backup_contact_method = Column(String(200))
    
    # Documentation
    documents_needed = Column(Text)  # JSON list of required documents
    documents_uploaded = Column(Text)  # JSON list of uploaded documents
    notary_required = Column(Boolean, default=False)
    
    # Follow-up and notes
    session_notes = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    satisfaction_rating = Column(Integer)  # 1-5 rating
    feedback = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="appointments")
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.service_title}>'
    
    def get_duration_display(self):
        """Return human-readable duration"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        if hours > 0:
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
        return f"{minutes}m"
    
    def is_upcoming(self):
        """Check if appointment is in the future"""
        return self.scheduled_date > datetime.utcnow()
    
    def can_be_cancelled(self):
        """Check if appointment can still be cancelled (24 hours before)"""
        if self.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            return False
        return self.scheduled_date > datetime.utcnow() + timedelta(hours=24)
    
    def get_status_display(self):
        """Return user-friendly status text"""
        status_map = {
            AppointmentStatus.REQUESTED: "Awaiting Confirmation",
            AppointmentStatus.CONFIRMED: "Confirmed",
            AppointmentStatus.IN_PROGRESS: "In Progress",
            AppointmentStatus.COMPLETED: "Completed",
            AppointmentStatus.CANCELLED: "Cancelled",
            AppointmentStatus.NO_SHOW: "Missed"
        }
        return status_map.get(self.status, self.status.value)


class UserPreference(db.Model):
    """User accessibility and communication preferences"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Visual preferences
    high_contrast_mode = Column(Boolean, default=False)
    large_text = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    color_scheme = Column(String(20), default='light')  # light, dark, auto
    
    # Communication preferences
    default_appointment_type = Column(SQLEnum(AppointmentType))
    preferred_appointment_time = Column(String(20))  # morning, afternoon, evening
    notification_methods = Column(Text)  # JSON array of notification preferences
    language_preference = Column(String(10), default='en')
    
    # Emergency contacts and information
    emergency_contact_1_name = Column(String(100))
    emergency_contact_1_phone = Column(String(20))
    emergency_contact_1_relation = Column(String(50))
    emergency_contact_2_name = Column(String(100))
    emergency_contact_2_phone = Column(String(20))
    emergency_contact_2_relation = Column(String(50))
    
    # Medical/accessibility information
    hearing_aid_details = Column(Text)
    cochlear_implant_details = Column(Text)
    other_assistive_technology = Column(Text)
    allergy_information = Column(Text)
    medication_information = Column(Text)
    
    # Privacy settings
    allow_video_recording = Column(Boolean, default=False)
    allow_session_notes = Column(Boolean, default=True)
    allow_follow_up_contact = Column(Boolean, default=True)
    allow_marketing_communications = Column(Boolean, default=False)
    
    # Created and updated timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_preferences")
    
    def __repr__(self):
        return f'<UserPreference for User {self.user_id}>'


class AppointmentTemplate(db.Model):
    """Pre-configured appointment templates for common services"""
    __tablename__ = 'appointment_templates'
    
    id = Column(Integer, primary_key=True)
    
    # Template information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    appointment_type = Column(SQLEnum(AppointmentType), nullable=False)
    
    # Default settings
    default_duration_minutes = Column(Integer, default=60)
    interpreter_required = Column(Boolean, default=True)
    interpreter_specialty_required = Column(String(100))
    notary_required = Column(Boolean, default=False)
    
    # Required documents and preparation
    required_documents = Column(Text)  # JSON list
    preparation_instructions = Column(Text)
    what_to_expect = Column(Text)
    
    # Pricing and availability
    estimated_cost = Column(String(50))
    availability_notes = Column(Text)
    booking_lead_time_hours = Column(Integer, default=24)
    
    # Display settings
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    icon_class = Column(String(50))  # CSS class for icon
    color_theme = Column(String(20))  # Color theme for the template
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AppointmentTemplate {self.name}>'
    
    def get_estimated_cost_display(self):
        """Return formatted cost display"""
        if not self.estimated_cost:
            return "Contact for pricing"
        return self.estimated_cost
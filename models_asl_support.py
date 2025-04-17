"""
Database models for ASL support functionality.
"""

from datetime import datetime
from simple_app import db

class ASLVideoCategory(db.Model):
    """
    Categories for ASL videos.
    """
    __tablename__ = 'asl_video_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('asl_video_categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('ASLVideoCategory', remote_side=[id], backref='subcategories')
    videos = db.relationship('ASLVideo', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f"<ASLVideoCategory {self.id}: {self.name}>"


class ASLVideo(db.Model):
    """
    ASL videos for financial terms and concepts.
    """
    __tablename__ = 'asl_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Video sources and identifiers
    provider = db.Column(db.String(50), nullable=False)  # mux, signasl, youtube, vimeo, etc.
    video_id = db.Column(db.String(255), nullable=False)  # External video ID
    duration = db.Column(db.Float)  # Duration in seconds
    
    # Metadata
    thumbnail_url = db.Column(db.String(255))
    transcript = db.Column(db.Text)
    keywords = db.Column(db.String(255))
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    
    # Categorization
    category_id = db.Column(db.Integer, db.ForeignKey('asl_video_categories.id'))
    
    # Flags
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    terms = db.relationship('ASLFinancialTerm', backref='video', lazy='dynamic')
    
    def __repr__(self):
        return f"<ASLVideo {self.id}: {self.title}>"


class ASLFinancialTerm(db.Model):
    """
    Financial terms with ASL video explanations.
    """
    __tablename__ = 'asl_financial_terms'
    
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    definition = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text)
    example = db.Column(db.Text)
    
    # Associated video
    video_id = db.Column(db.Integer, db.ForeignKey('asl_videos.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ASLFinancialTerm {self.id}: {self.term}>"


class ASLScheduledSession(db.Model):
    """
    Scheduled ASL support sessions.
    """
    __tablename__ = 'asl_scheduled_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Session details
    session_type = db.Column(db.String(50), nullable=False)  # live_support, training, consultation
    topic = db.Column(db.String(255))
    duration_minutes = db.Column(db.Integer, default=30)
    notes = db.Column(db.Text)
    
    # Scheduling
    scheduled_date = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Video provider
    provider = db.Column(db.String(50), nullable=False)  # asl_now, sign_vri, purple_vri
    meeting_id = db.Column(db.String(255))
    join_url = db.Column(db.String(255))
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ASLScheduledSession {self.id}: {self.session_type} on {self.scheduled_date}>"


class ASLSupportProvider(db.Model):
    """
    ASL support providers (interpreters, experts, etc.)
    """
    __tablename__ = 'asl_support_providers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    
    # Qualifications and expertise
    specialization = db.Column(db.String(100))  # finance, insurance, tax, etc.
    experience_years = db.Column(db.Integer)
    certifications = db.Column(db.Text)
    bio = db.Column(db.Text)
    
    # Availability
    available_days = db.Column(db.String(100))  # comma-separated days (mon,tue,wed)
    available_hours_start = db.Column(db.Time)
    available_hours_end = db.Column(db.Time)
    timezone = db.Column(db.String(50), default='UTC')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ASLSupportProvider {self.id}: {self.name}>"


class ASLLiveSessionFeedback(db.Model):
    """
    Feedback for live ASL support sessions.
    """
    __tablename__ = 'asl_live_session_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('asl_scheduled_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Feedback
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    communication_quality = db.Column(db.Integer)  # 1-5
    helpfulness = db.Column(db.Integer)  # 1-5
    technical_quality = db.Column(db.Integer)  # 1-5
    comments = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session = db.relationship('ASLScheduledSession', backref='feedback')
    
    def __repr__(self):
        return f"<ASLLiveSessionFeedback {self.id}: Rating {self.rating} for Session {self.session_id}>"
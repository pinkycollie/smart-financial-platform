"""
Database models for ASL Support functionality in the DEAF FIRST platform.
Handles video-based tech support with ASL interpreters.
"""

from datetime import datetime
from simple_app import db

class ASLSupportSession(db.Model):
    """
    ASL Support session for technical support with ASL interpreters.
    """
    __tablename__ = 'asl_support_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    category = db.Column(db.String(50), nullable=False)  # general, financial_tools, accessibility, etc.
    notes = db.Column(db.Text)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    
    # Meeting details
    provider = db.Column(db.String(50))  # asl_now, sign_vri, purple_vri, demo
    meeting_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # Rating and feedback
    rating = db.Column(db.Integer)  # 1-5 stars
    feedback = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='support_sessions')
    
    def __repr__(self):
        return f"<ASLSupportSession {self.id} for user {self.user_id}>"

class ASLSupportResource(db.Model):
    """
    ASL Support video resources for self-help.
    """
    __tablename__ = 'asl_support_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Resource details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # general, financial_tools, accessibility, etc.
    tags = db.Column(db.JSON)  # Array of tags
    
    # Media
    video_url = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255))
    transcript = db.Column(db.Text)
    
    # Metadata
    author = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    
    # White-label customization
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    is_white_labeled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ASLSupportResource {self.id}: {self.title}>"

class ASLSupportFAQ(db.Model):
    """
    Frequently asked questions with ASL video responses.
    """
    __tablename__ = 'asl_support_faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # FAQ details
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # general, financial_tools, accessibility, etc.
    
    # Media
    video_url = db.Column(db.String(255))
    thumbnail_url = db.Column(db.String(255))
    
    # Metadata
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    sort_order = db.Column(db.Integer, default=0)
    
    # White-label customization
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    is_white_labeled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ASLSupportFAQ {self.id}: {self.question[:50]}...>"
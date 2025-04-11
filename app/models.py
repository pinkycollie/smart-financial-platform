from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    accessibility_settings = db.Column(db.JSON, default={})
    
    # Relationship
    financial_profiles = db.relationship('FinancialProfile', back_populates='user', cascade='all, delete-orphan')
    tax_documents = db.relationship('TaxDocument', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class AccessibilityPreference(db.Model):
    __tablename__ = 'accessibility_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    asl_video_enabled = db.Column(db.Boolean, default=True)
    deaf_support_bot_enabled = db.Column(db.Boolean, default=True)
    visual_alerts_enabled = db.Column(db.Boolean, default=True)
    preferred_video_speed = db.Column(db.Float, default=1.0)
    color_contrast_preference = db.Column(db.String(20), default='standard')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('accessibility_preference', uselist=False))
    
    def __repr__(self):
        return f'<AccessibilityPreference user_id={self.user_id}>'

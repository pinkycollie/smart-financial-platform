from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from simple_app import db

class User(UserMixin, db.Model):
    """User model for authentication and profile information"""
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
    eula_accepted = db.Column(db.Boolean, default=False)
    
    # Relationships
    financial_profiles = db.relationship('FinancialProfile', back_populates='user', cascade='all, delete-orphan')
    tax_documents = db.relationship('TaxDocument', back_populates='user', cascade='all, delete-orphan')
    eula_acceptances = db.relationship('EULAAcceptance', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check user password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"


class AccessibilityPreference(db.Model):
    """User accessibility preferences"""
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
    
    # Relationship
    user = db.relationship('User', backref=db.backref('accessibility_preference', uselist=False))
    
    def __repr__(self):
        return f"<AccessibilityPreference for User {self.user_id}>"


class FinancialProfile(db.Model):
    """User financial profile information"""
    __tablename__ = 'financial_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    annual_income = db.Column(db.Float)
    filing_status = db.Column(db.String(50))
    dependents = db.Column(db.Integer, default=0)
    investments = db.Column(db.JSON)
    retirement_accounts = db.Column(db.JSON)
    external_id = db.Column(db.String(100))  # April API identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='financial_profiles')
    recommendations = db.relationship('FinancialRecommendation', back_populates='financial_profile', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<FinancialProfile {self.id} for User {self.user_id}>"


class TaxDocument(db.Model):
    """User tax document information"""
    __tablename__ = 'tax_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # W2, 1099, etc.
    document_data = db.Column(db.JSON)
    year = db.Column(db.Integer, nullable=False)
    external_id = db.Column(db.String(100))  # April API identifier
    status = db.Column(db.String(20), default='pending')  # pending, processed, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='tax_documents')
    
    def __repr__(self):
        return f"<TaxDocument {self.document_type} ({self.year}) for User {self.user_id}>"


class AprilTransaction(db.Model):
    """Record of API interactions with April"""
    __tablename__ = 'april_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    successful = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AprilTransaction {self.transaction_type} ({self.status_code}) for User {self.user_id}>"


class FinancialRecommendation(db.Model):
    """Financial recommendations based on user profile"""
    __tablename__ = 'financial_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    financial_profile_id = db.Column(db.Integer, db.ForeignKey('financial_profiles.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    potential_impact = db.Column(db.Float)  # Potential financial impact
    asl_video_id = db.Column(db.String(100))  # Mux video ID for ASL explanation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    financial_profile = db.relationship('FinancialProfile', back_populates='recommendations')
    
    def __repr__(self):
        return f"<FinancialRecommendation {self.recommendation_type} for Profile {self.financial_profile_id}>"
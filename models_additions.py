from datetime import datetime
from simple_app import db

# PLATFORM CONTENT STRUCTURE

class Industry(db.Model):
    """Industries covered by the platform"""
    __tablename__ = 'industries'
    
    id = db.Column(db.Integer, primary_key=True)
    industry_name = db.Column(db.String(100), nullable=False)
    industry_description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    color_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    content_modules = db.relationship('ContentModule', backref='industry', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Industry {self.industry_name}>"


class ContentModule(db.Model):
    """Educational and informational content modules"""
    __tablename__ = 'content_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    industry_id = db.Column(db.Integer, db.ForeignKey('industries.id'), nullable=False)
    module_title = db.Column(db.String(255), nullable=False)
    module_description = db.Column(db.Text)
    content_type = db.Column(db.String(20))  # video, text, interactive
    asl_available = db.Column(db.Boolean, default=False)
    captions_available = db.Column(db.Boolean, default=False)
    difficulty_level = db.Column(db.String(20))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    media_files = db.relationship('MediaFile', backref='module', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<ContentModule {self.module_title}>"


# MULTIMEDIA CONTENT STORAGE

class MediaFile(db.Model):
    """Media files associated with content modules"""
    __tablename__ = 'media_files'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('content_modules.id'), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # video, image, document
    file_path = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer)  # in seconds, for videos
    file_size = db.Column(db.Integer)  # in bytes
    asl_version_available = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    accessibility_rating = db.Column(db.Integer)  # 1-10 rating
    
    # Relationships
    captions = db.relationship('Caption', backref='media_file', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<MediaFile {self.id} - {self.file_type}>"


class Caption(db.Model):
    """Captions for media files"""
    __tablename__ = 'captions'
    
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('media_files.id'), nullable=False)
    language = db.Column(db.String(20), nullable=False)
    caption_text = db.Column(db.Text, nullable=False)
    timing_data = db.Column(db.JSON)  # Start/end times for each caption segment
    accuracy_score = db.Column(db.Float)  # AI-verified accuracy score
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Caption {self.id} - Media {self.media_id}>"


# AUTHENTICATION & ACCESS CONTROL

class AccessTier(db.Model):
    """Access tiers for different user types"""
    __tablename__ = 'access_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(50), nullable=False)  # investor, shareholder, beta_tester, general
    feature_permissions = db.Column(db.JSON)
    data_access_level = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_access = db.relationship('UserAccess', backref='tier', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<AccessTier {self.tier_name}>"


class UserAccess(db.Model):
    """User access permissions"""
    __tablename__ = 'user_access'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tier_id = db.Column(db.Integer, db.ForeignKey('access_tiers.id'), nullable=False)
    grant_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime)
    granted_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserAccess {self.id} - User {self.user_id} - Tier {self.tier_id}>"


# INVESTOR & SHAREHOLDER FEATURES

class Investment(db.Model):
    """Investment records for investor users"""
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    investment_date = db.Column(db.DateTime, nullable=False)
    investment_type = db.Column(db.String(20), nullable=False)  # equity, debt, convertible
    terms = db.Column(db.Text)
    expected_roi = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('investments', lazy='dynamic'))
    
    def __repr__(self):
        return f"<Investment {self.id} - User {self.user_id}>"


class ShareholderUpdate(db.Model):
    """Updates for shareholders and investors"""
    __tablename__ = 'shareholder_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publication_date = db.Column(db.DateTime, default=datetime.utcnow)
    confidential_level = db.Column(db.String(20), default='public')
    target_groups = db.Column(db.JSON)  # [investors, shareholders, all]
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ShareholderUpdate {self.id} - {self.title}>"


# ANALYTICS & REPORTING

class PlatformMetric(db.Model):
    """Platform-wide metrics for analytics"""
    __tablename__ = 'platform_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    date_recorded = db.Column(db.Date, nullable=False)
    active_users = db.Column(db.Integer)
    new_signups = db.Column(db.Integer)
    content_consumption = db.Column(db.JSON)
    retention_rate = db.Column(db.Float)
    accessibility_usage_stats = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PlatformMetric {self.id} - {self.date_recorded}>"


class UserEngagement(db.Model):
    """User engagement metrics"""
    __tablename__ = 'user_engagement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_start = db.Column(db.DateTime, nullable=False)
    session_end = db.Column(db.DateTime)
    modules_accessed = db.Column(db.JSON)
    interactions = db.Column(db.Integer)
    feedback_provided = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('engagement_data', lazy='dynamic'))
    
    def __repr__(self):
        return f"<UserEngagement {self.id} - User {self.user_id}>"


# BETA TESTING SYSTEM

class BetaFeature(db.Model):
    """Features in beta testing"""
    __tablename__ = 'beta_features'
    
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    target_audience = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedback = db.relationship('UserFeedback', backref='feature', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<BetaFeature {self.feature_name}>"


class UserFeedback(db.Model):
    """User feedback on features and content"""
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feature_id = db.Column(db.Integer, db.ForeignKey('beta_features.id'), nullable=False)
    feedback_type = db.Column(db.String(20), nullable=False)  # bug, suggestion, praise
    severity_level = db.Column(db.String(20))
    description = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, in_progress, resolved
    
    # Relationships
    user = db.relationship('User', backref=db.backref('feedback', lazy='dynamic'))
    responses = db.relationship('FeedbackResponse', backref='feedback', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<UserFeedback {self.id} - User {self.user_id}>"


class FeedbackResponse(db.Model):
    """Responses to user feedback"""
    __tablename__ = 'feedback_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('user_feedback.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_required = db.Column(db.Boolean, default=False)
    
    # Relationship to responder user
    responder = db.relationship('User', foreign_keys=[responder_id])
    
    def __repr__(self):
        return f"<FeedbackResponse {self.id} - Feedback {self.feedback_id}>"


# NOTIFICATION SYSTEM

class Notification(db.Model):
    """User notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    delivery_method = db.Column(db.String(20), nullable=False)  # visual_alert, email, sms
    sent_time = db.Column(db.DateTime, default=datetime.utcnow)
    read_status = db.Column(db.Boolean, default=False)
    priority_level = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f"<Notification {self.id} - User {self.user_id}>"


class Announcement(db.Model):
    """Platform-wide announcements"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_groups = db.Column(db.JSON)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime)
    urgency_level = db.Column(db.String(20), default='normal')  # low, normal, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Announcement {self.id} - {self.title}>"


class UserProfile(db.Model):
    """Extended user profile information"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    language_preferences = db.Column(db.JSON)  # [ASL, International_Sign, written_language]
    skill_level = db.Column(db.String(20))  # beginner, intermediate, expert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def __repr__(self):
        return f"<UserProfile for User {self.user_id}>"
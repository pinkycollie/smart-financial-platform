"""
Database models for licensing system in the DEAF FIRST platform.
"""

from datetime import datetime
from simple_app import db

class LicenseType(db.Model):
    """
    Types of licenses available for the platform.
    """
    __tablename__ = 'license_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # License features
    max_users = db.Column(db.Integer, default=10)
    max_storage_gb = db.Column(db.Integer)
    is_white_label = db.Column(db.Boolean, default=False)
    can_create_sublicenses = db.Column(db.Boolean, default=False)
    
    # License limitations
    api_rate_limit = db.Column(db.Integer)
    concurrent_users = db.Column(db.Integer)
    
    # Billing info
    suggested_price = db.Column(db.Float)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, quarterly, yearly
    
    # Features as JSON
    included_features = db.Column(db.JSON)  # Array of feature codes included
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    licenses = db.relationship('License', back_populates='license_type')
    
    def __repr__(self):
        return f"<LicenseType {self.id}: {self.name}>"

class License(db.Model):
    """
    License instances issued to licensees.
    """
    __tablename__ = 'licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    license_key = db.Column(db.String(100), nullable=False, unique=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    license_type_id = db.Column(db.Integer, db.ForeignKey('license_types.id'), nullable=False)
    
    # License status
    status = db.Column(db.String(20), default='active')  # active, suspended, expired, revoked
    activation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime)
    last_verified = db.Column(db.DateTime)
    
    # Custom overrides
    max_users_override = db.Column(db.Integer)
    max_storage_gb_override = db.Column(db.Integer)
    custom_features = db.Column(db.JSON)  # Custom feature configuration
    
    # Usage statistics
    current_user_count = db.Column(db.Integer, default=0)
    current_storage_usage_gb = db.Column(db.Float, default=0.0)
    api_calls_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    licensee = db.relationship('Licensee', backref='licenses')
    license_type = db.relationship('LicenseType', back_populates='licenses')
    usage_logs = db.relationship('LicenseUsageLog', back_populates='license', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<License {self.id}: {self.license_key}>"
    
    @property
    def is_active(self):
        """Check if license is active"""
        return self.status == 'active'
    
    @property
    def days_until_expiration(self):
        """Get days until license expires"""
        if not self.expiration_date:
            return None
        
        days = (self.expiration_date - datetime.utcnow()).days
        return max(0, days)
    
    @property
    def effective_max_users(self):
        """Get effective maximum users allowed"""
        return self.max_users_override or self.license_type.max_users
    
    @property
    def effective_max_storage(self):
        """Get effective maximum storage allowed"""
        return self.max_storage_gb_override or self.license_type.max_storage_gb

class LicenseUsageLog(db.Model):
    """
    Usage logs for licenses.
    """
    __tablename__ = 'license_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'), nullable=False)
    
    # Usage metrics
    user_count = db.Column(db.Integer)
    storage_usage_gb = db.Column(db.Float)
    api_calls_count = db.Column(db.Integer)
    feature_usage = db.Column(db.JSON)  # Usage statistics for specific features
    
    # Timestamp
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    license = db.relationship('License', back_populates='usage_logs')
    
    def __repr__(self):
        return f"<LicenseUsageLog {self.id} for License {self.license_id}>"

class Feature(db.Model):
    """
    Platform features that can be enabled or disabled by license.
    """
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # core, addon, premium, etc.
    
    # UI display
    icon = db.Column(db.String(50))
    ui_component = db.Column(db.String(100))  # Reference to UI component
    
    # Technical details
    implementation_path = db.Column(db.String(255))  # Path to implementation code
    dependencies = db.Column(db.JSON)  # Feature dependencies
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_beta = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Feature {self.id}: {self.name}>"

class PlatformConfig(db.Model):
    """
    Global platform configuration.
    """
    __tablename__ = 'platform_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.JSON)
    description = db.Column(db.Text)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    access_roles = db.Column(db.JSON)  # Roles allowed to access this config
    
    # Environment specific
    environment = db.Column(db.String(20), default='all')  # all, production, staging, development
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f"<PlatformConfig {self.id}: {self.name}>"

class WhiteLabelConfig(db.Model):
    """
    White-label configuration templates.
    """
    __tablename__ = 'white_label_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Theme configuration
    theme_data = db.Column(db.JSON)  # Theme colors, layout, fonts
    
    # Component visibility
    component_visibility = db.Column(db.JSON)  # Components to show/hide
    
    # Custom code
    custom_css = db.Column(db.Text)
    custom_js = db.Column(db.Text)
    
    # Content overrides
    content_overrides = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<WhiteLabelConfig {self.id}: {self.name}>"

class ApiKey(db.Model):
    """
    API keys for platform access.
    """
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Owner information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    
    # Permissions
    scopes = db.Column(db.JSON)  # API access scopes
    
    # Usage limits
    rate_limit = db.Column(db.Integer)
    daily_limit = db.Column(db.Integer)
    monthly_limit = db.Column(db.Integer)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    
    # Usage tracking
    last_used_at = db.Column(db.DateTime)
    last_ip = db.Column(db.String(50))
    usage_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='api_keys')
    licensee = db.relationship('Licensee', backref='api_keys')
    
    def __repr__(self):
        return f"<ApiKey {self.id}: {self.name}>"
    
    @property
    def is_valid(self):
        """Check if API key is valid"""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        return True
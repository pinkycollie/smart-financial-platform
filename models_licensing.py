"""
Database models for DEAF FIRST platform licensing program.
Enables white-label licensing and customization for licensees.
"""

from datetime import datetime
from simple_app import db

class Licensee(db.Model):
    """
    Licensee model for entities that license the DEAF FIRST platform.
    Represents an organization that uses a white-labeled version of the platform.
    """
    __tablename__ = 'licensees'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(100), unique=True)
    license_tier = db.Column(db.String(20), default='basic')  # basic, professional, enterprise
    status = db.Column(db.String(20), default='active')  # active, suspended, expired
    
    # Business details
    business_type = db.Column(db.String(50))  # financial_advisor, insurance_agency, education_provider, etc.
    tax_id = db.Column(db.String(50))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(50), default='USA')
    
    # Contact information
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20))
    
    # License details
    license_key = db.Column(db.String(100), unique=True)
    api_key = db.Column(db.String(100), unique=True)
    license_start_date = db.Column(db.Date, nullable=False)
    license_end_date = db.Column(db.Date)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Billing information
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, quarterly, annually
    billing_amount = db.Column(db.Float, nullable=False)
    next_billing_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    
    # Usage limits
    max_clients = db.Column(db.Integer, default=25)
    current_clients = db.Column(db.Integer, default=0)
    
    # Feature flags
    white_label_enabled = db.Column(db.Boolean, default=False)
    custom_modules_enabled = db.Column(db.Boolean, default=False)
    api_access_enabled = db.Column(db.Boolean, default=False)
    
    # Reseller relationship (optional)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id', use_alter=True, name='fk_licensee_reseller'))
    sub_reseller_id = db.Column(db.Integer, db.ForeignKey('sub_resellers.id', use_alter=True, name='fk_licensee_sub_reseller'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    branding = db.relationship('LicenseeBranding', backref='licensee', uselist=False, cascade='all, delete-orphan')
    features = db.relationship('LicenseeFeatures', backref='licensee', uselist=False, cascade='all, delete-orphan')
    billing_history = db.relationship('LicenseeBillingHistory', backref='licensee', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Licensee {self.company_name}>"
    
    def get_portal_url(self):
        """Get licensee portal URL"""
        if self.subdomain:
            return f"https://{self.subdomain}.deaffirst.com"
        return f"https://app.deaffirst.com/licensee/{self.id}"
    
    def can_add_client(self):
        """Check if licensee can add more clients"""
        return self.max_clients == float('inf') or self.current_clients < self.max_clients


class LicenseeBranding(db.Model):
    """
    Branding and customization settings for licensees.
    Only available for licensees with white_label_enabled=True.
    """
    __tablename__ = 'licensee_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    # Branding elements
    logo_path = db.Column(db.String(255))
    logo_light_path = db.Column(db.String(255))  # Light version for dark backgrounds
    favicon_path = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default='#0066CC')
    secondary_color = db.Column(db.String(20), default='#00AA55')
    accent_color = db.Column(db.String(20))
    font_family = db.Column(db.String(100), default='Open Sans, sans-serif')
    
    # Custom text
    company_tagline = db.Column(db.String(255))
    welcome_message = db.Column(db.Text)
    footer_text = db.Column(db.Text)
    legal_disclaimer = db.Column(db.Text)
    
    # Email customization
    sender_email = db.Column(db.String(100))
    sender_name = db.Column(db.String(100))
    email_header_image = db.Column(db.String(255))
    email_footer_text = db.Column(db.Text)
    
    # Advanced customization
    show_powered_by = db.Column(db.Boolean, default=True)
    custom_css = db.Column(db.Text)
    custom_javascript = db.Column(db.Text)
    
    # Social media
    facebook_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LicenseeBranding for {self.licensee_id}>"


class LicenseeFeatures(db.Model):
    """
    Feature configuration for licensees.
    Controls which modules are enabled for each licensee.
    """
    __tablename__ = 'licensee_features'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    # Available modules
    enabled_modules = db.Column(db.JSON, default=[])
    
    # Enhanced features
    enhanced_asl_support = db.Column(db.Boolean, default=False)
    advanced_analytics = db.Column(db.Boolean, default=False)
    premium_templates = db.Column(db.Boolean, default=False)
    priority_support = db.Column(db.Boolean, default=False)
    
    # Usage limits
    storage_limit_gb = db.Column(db.Integer, default=5)
    monthly_api_calls = db.Column(db.Integer, default=0)  # 0 means no API access
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LicenseeFeatures for {self.licensee_id}>"


class LicenseeBillingHistory(db.Model):
    """
    Billing history for licensees.
    Tracks all payments and invoices.
    """
    __tablename__ = 'licensee_billing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    billing_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Billing details
    invoice_number = db.Column(db.String(50), unique=True)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    
    # Billing period
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LicenseeBillingHistory {self.invoice_number} for {self.licensee_id}>"
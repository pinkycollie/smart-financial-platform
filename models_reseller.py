"""
Database models for DEAF FIRST platform reseller program.
Enables white-label reselling with multi-tier architecture.
"""

from datetime import datetime
from simple_app import db
from models import User
from models_licensing import Licensee, LicenseeBranding

class Reseller(db.Model):
    """
    Reseller model for entities that resell the DEAF FIRST platform.
    Represents an organization that white-labels and resells the platform to other businesses.
    """
    __tablename__ = 'resellers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    primary_domain = db.Column(db.String(100), unique=True)
    reseller_tier = db.Column(db.String(20), default='standard')  # standard, premium, enterprise
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
    contact_email = db.Column(db.String(100))
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
    
    # Reseller capabilities
    max_sub_resellers = db.Column(db.Integer, default=0)
    current_sub_resellers = db.Column(db.Integer, default=0)
    max_licensees = db.Column(db.Integer, default=50)
    current_licensees = db.Column(db.Integer, default=0)
    commission_rate = db.Column(db.Float, default=20.0)  # percentage
    
    # Feature flags
    can_customize_modules = db.Column(db.Boolean, default=False)
    can_set_pricing = db.Column(db.Boolean, default=False)
    can_create_sub_resellers = db.Column(db.Boolean, default=False)
    can_edit_source_code = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    branding = db.relationship('ResellerBranding', backref='reseller', uselist=False, cascade='all, delete-orphan')
    sub_resellers = db.relationship('SubReseller', backref='parent_reseller', lazy='dynamic', cascade='all, delete-orphan')
    licensees = db.relationship('Licensee', backref='reseller', lazy='dynamic')
    admins = db.relationship('ResellerAdmin', backref='reseller', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Reseller {self.company_name}>"
    
    def get_portal_url(self):
        """Get reseller portal URL"""
        if self.primary_domain:
            return f"https://{self.primary_domain}"
        return f"https://reseller.deaffirst.com/portal/{self.id}"
    
    def can_add_sub_reseller(self):
        """Check if reseller can add more sub-resellers"""
        return self.can_create_sub_resellers and (self.current_sub_resellers < self.max_sub_resellers)
    
    def can_add_licensee(self):
        """Check if reseller can add more licensees"""
        return self.current_licensees < self.max_licensees


class ResellerBranding(db.Model):
    """
    Branding and customization settings for resellers.
    Allows resellers to customize the platform appearance for their customers.
    """
    __tablename__ = 'reseller_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    
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
    
    # Domain settings
    custom_domain_enabled = db.Column(db.Boolean, default=False)
    sub_domains_pattern = db.Column(db.String(100))  # E.g., "{licensee}.{reseller}.deaffirst.com"
    
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
        return f"<ResellerBranding for {self.reseller_id}>"


class SubReseller(db.Model):
    """
    Sub-reseller model for multi-tier reseller structure.
    Represents a secondary reseller operating under a primary reseller.
    """
    __tablename__ = 'sub_resellers'
    
    id = db.Column(db.Integer, primary_key=True)
    parent_reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='active')  # active, suspended, expired
    
    # Contact information
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    
    # Sub-reseller capabilities
    max_licensees = db.Column(db.Integer, default=10)
    current_licensees = db.Column(db.Integer, default=0)
    commission_rate = db.Column(db.Float, default=10.0)  # percentage (of parent reseller's commission)
    
    # Feature flags
    can_customize_branding = db.Column(db.Boolean, default=True)
    can_set_pricing = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    branding = db.relationship('SubResellerBranding', backref='sub_reseller', uselist=False, cascade='all, delete-orphan')
    licensees = db.relationship('Licensee', backref='sub_reseller', lazy='dynamic')
    
    def __repr__(self):
        return f"<SubReseller {self.company_name} under {self.parent_reseller_id}>"
    
    def get_portal_url(self):
        """Get sub-reseller portal URL"""
        if self.subdomain:
            parent = Reseller.query.get(self.parent_reseller_id)
            if parent and parent.primary_domain:
                return f"https://{self.subdomain}.{parent.primary_domain}"
        return f"https://reseller.deaffirst.com/sub-portal/{self.id}"


class SubResellerBranding(db.Model):
    """
    Branding and customization settings for sub-resellers.
    """
    __tablename__ = 'sub_reseller_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    sub_reseller_id = db.Column(db.Integer, db.ForeignKey('sub_resellers.id'), nullable=False)
    
    # Branding elements (similar to ResellerBranding but with possibly fewer options)
    logo_path = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default='#0066CC')
    secondary_color = db.Column(db.String(20), default='#00AA55')
    
    # Custom text
    company_tagline = db.Column(db.String(255))
    welcome_message = db.Column(db.Text)
    
    # Branding options
    show_powered_by = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SubResellerBranding for {self.sub_reseller_id}>"


class ResellerAdmin(db.Model):
    """
    Admin users for resellers.
    These users can manage the reseller portal and licensees.
    """
    __tablename__ = 'reseller_admins'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    role = db.Column(db.String(20), default='admin')  # admin, sales, support, billing
    permissions = db.Column(db.JSON, default={})
    is_primary = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    
    def __repr__(self):
        return f"<ResellerAdmin {self.user_id} for {self.reseller_id}>"


class ResellerRevenue(db.Model):
    """
    Revenue tracking for resellers, including commissions and sales.
    """
    __tablename__ = 'reseller_revenue'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    sub_reseller_id = db.Column(db.Integer, db.ForeignKey('sub_resellers.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50))  # new_license, renewal, upgrade, etc.
    
    # Payment tracking
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ResellerRevenue {self.amount} for {self.reseller_id}>"


class ResellerTheme(db.Model):
    """
    Predefined themes that resellers can use and customize.
    """
    __tablename__ = 'reseller_themes'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))  # Null for global themes
    
    theme_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Can be used by other resellers
    
    # Theme properties
    primary_color = db.Column(db.String(20), nullable=False)
    secondary_color = db.Column(db.String(20), nullable=False)
    accent_color = db.Column(db.String(20))
    font_family = db.Column(db.String(100))
    background_color = db.Column(db.String(20))
    text_color = db.Column(db.String(20))
    
    # Component styling
    button_style = db.Column(db.JSON)  # radius, shadow, etc.
    card_style = db.Column(db.JSON)
    header_style = db.Column(db.JSON)
    
    # Additional CSS
    custom_css = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ResellerTheme {self.theme_name}>"


# Add relationships to existing models
Licensee.reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
Licensee.sub_reseller_id = db.Column(db.Integer, db.ForeignKey('sub_resellers.id'))
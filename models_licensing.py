"""
Database models for DEAF FIRST platform licensing system.
Enables financial professionals to license and customize the platform for deaf clients.
"""

from datetime import datetime
from simple_app import db
from models import User

class Licensee(db.Model):
    """
    Licensee model for financial professionals licensing the platform.
    Represents an organization or individual professional who has licensed the platform.
    """
    __tablename__ = 'licensees'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True)
    license_tier = db.Column(db.String(20), default='basic')  # basic, professional, enterprise
    status = db.Column(db.String(20), default='active')  # active, suspended, expired
    max_clients = db.Column(db.Integer, default=50)
    current_clients = db.Column(db.Integer, default=0)
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
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, annually
    billing_amount = db.Column(db.Float, nullable=False)
    next_billing_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    
    # Features and permissions
    white_label_enabled = db.Column(db.Boolean, default=False)
    custom_modules_enabled = db.Column(db.Boolean, default=False)
    api_access_enabled = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    branding = db.relationship('LicenseeBranding', backref='licensee', uselist=False, cascade='all, delete-orphan')
    custom_modules = db.relationship('LicenseeModule', backref='licensee', lazy='dynamic', cascade='all, delete-orphan')
    client_accounts = db.relationship('LicenseeClient', backref='licensee', lazy='dynamic', cascade='all, delete-orphan')
    admins = db.relationship('LicenseeAdmin', backref='licensee', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Licensee {self.company_name}>"
    
    def is_enterprise(self):
        """Check if licensee has enterprise tier"""
        return self.license_tier == 'enterprise'
    
    def is_professional(self):
        """Check if licensee has professional tier or higher"""
        return self.license_tier in ['professional', 'enterprise']
    
    def can_add_client(self):
        """Check if licensee can add more clients"""
        return self.current_clients < self.max_clients
    
    def get_portal_url(self):
        """Get customer portal URL for this licensee"""
        if self.subdomain:
            return f"https://{self.subdomain}.app.mbtqgroup.com"
        return f"https://app.mbtqgroup.com/licensee/{self.id}"


class LicenseeBranding(db.Model):
    """
    Branding and customization settings for licensees.
    Allows professionals to customize the platform appearance for their clients.
    """
    __tablename__ = 'licensee_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    # Branding elements
    logo_path = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default='#0066CC')
    secondary_color = db.Column(db.String(20), default='#00AA55')
    accent_color = db.Column(db.String(20))
    font_family = db.Column(db.String(100), default='Open Sans, sans-serif')
    
    # Custom text
    company_tagline = db.Column(db.String(255))
    welcome_message = db.Column(db.Text)
    footer_text = db.Column(db.Text)
    
    # Branding options
    show_powered_by = db.Column(db.Boolean, default=True)
    custom_css = db.Column(db.Text)
    custom_javascript = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LicenseeBranding for {self.licensee_id}>"


class LicenseeAdmin(db.Model):
    """
    Admin users for licensees.
    These users can manage the licensed platform instance.
    """
    __tablename__ = 'licensee_admins'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    role = db.Column(db.String(20), default='admin')  # admin, manager, billing
    permissions = db.Column(db.JSON, default={})
    is_primary = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    
    def __repr__(self):
        return f"<LicenseeAdmin {self.user_id} for {self.licensee_id}>"


class LicenseeModule(db.Model):
    """
    Custom education modules created by licensees.
    Enterprise licensees can create custom financial education content.
    """
    __tablename__ = 'licensee_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, pending_approval, approved, rejected
    
    # Module settings
    base_module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'))
    is_modification = db.Column(db.Boolean, default=False)
    approval_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    base_module = db.relationship('EducationModule')
    lessons = db.relationship('LicenseeLesson', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<LicenseeModule {self.title} for {self.licensee_id}>"


class LicenseeLesson(db.Model):
    """
    Custom lessons for licensee-created education modules.
    """
    __tablename__ = 'licensee_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('licensee_modules.id'), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=1)
    
    # Original lesson if this is a modification
    base_lesson_id = db.Column(db.Integer, db.ForeignKey('education_lessons.id'))
    is_modification = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    base_lesson = db.relationship('EducationLesson')
    
    def __repr__(self):
        return f"<LicenseeLesson {self.title}>"


class LicenseeClient(db.Model):
    """
    Clients of licensees using the platform.
    These are the deaf clients that financial professionals serve.
    """
    __tablename__ = 'licensee_clients'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    client_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, inactive
    notes = db.Column(db.Text)
    
    # Client data
    communication_preference = db.Column(db.String(20), default='ASL')  # ASL, text, both
    assigned_advisor_id = db.Column(db.Integer, db.ForeignKey('licensee_admins.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    assigned_advisor = db.relationship('LicenseeAdmin')
    
    def __repr__(self):
        return f"<LicenseeClient {self.user_id} for {self.licensee_id}>"


class LicenseeBillingHistory(db.Model):
    """
    Billing history for licensees.
    """
    __tablename__ = 'licensee_billing_history'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    billing_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    
    # Payment details
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    invoice_number = db.Column(db.String(50))
    
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LicenseeBilling {self.invoice_number} for {self.licensee_id}>"


class LicenseAgreement(db.Model):
    """
    License agreements between MBTQ GROUP and licensees.
    """
    __tablename__ = 'license_agreements'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False)
    
    agreement_version = db.Column(db.String(20), nullable=False)
    agreement_text = db.Column(db.Text, nullable=False)
    
    accepted = db.Column(db.Boolean, default=False)
    accepted_at = db.Column(db.DateTime)
    accepted_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    accepted_by_user = db.relationship('User')
    
    def __repr__(self):
        return f"<LicenseAgreement v{self.agreement_version} for {self.licensee_id}>"
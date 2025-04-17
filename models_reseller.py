"""
Database models for multi-tier white-label reseller system in the DEAF FIRST platform.
"""

from datetime import datetime
from simple_app import db

class Reseller(db.Model):
    """
    Primary reseller for the white-label platform.
    Can create and manage sub-licensees.
    """
    __tablename__ = 'resellers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    company_name = db.Column(db.String(100), nullable=False)
    reseller_code = db.Column(db.String(50), unique=True, nullable=False)
    external_id = db.Column(db.String(100), unique=True)  # Cheddar customer ID
    
    # Contact information
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20))
    owner_first_name = db.Column(db.String(50))
    owner_last_name = db.Column(db.String(50))
    
    # Business information
    business_type = db.Column(db.String(50))  # corporation, llc, partnership, sole_proprietorship
    tax_id = db.Column(db.String(50))
    tax_exempt = db.Column(db.Boolean, default=False)
    
    # Address
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    
    # Platform settings
    domain_name = db.Column(db.String(255))
    subdomain = db.Column(db.String(50), unique=True)
    white_label_enabled = db.Column(db.Boolean, default=True)
    
    # Account status
    status = db.Column(db.String(20), default='pending')  # pending, active, suspended, terminated
    approval_date = db.Column(db.DateTime)
    suspension_reason = db.Column(db.Text)
    
    # Reseller type and parent relationship (for multi-tier)
    reseller_type = db.Column(db.String(20), default='primary')  # primary, secondary
    parent_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    
    # Revenue sharing
    commission_rate = db.Column(db.Float, default=0.0)  # Percentage of revenue shared with parent
    revenue_share_type = db.Column(db.String(20), default='percentage')  # percentage, fixed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('Reseller', remote_side=[id], backref='sub_resellers')
    branding = db.relationship('ResellerBranding', uselist=False, back_populates='reseller', cascade='all, delete-orphan')
    subscriptions = db.relationship('ResellerSubscription', back_populates='reseller', cascade='all, delete-orphan')
    invoices = db.relationship('ResellerInvoice', back_populates='reseller', cascade='all, delete-orphan')
    # The revenue_transactions and sub_reseller_revenue are now defined on ResellerRevenue with backref
    licensees = db.relationship('Licensee', back_populates='reseller', cascade='all, delete-orphan')
    portal_users = db.relationship('PortalUser', back_populates='reseller', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Reseller {self.id}: {self.company_name}>"
    
    @property
    def full_domain(self):
        """Get the full domain for the reseller"""
        if self.domain_name:
            return self.domain_name
        elif self.subdomain:
            return f"{self.subdomain}.deaffirst.com"
        else:
            return None
    
    @property
    def is_active(self):
        """Check if reseller is active"""
        return self.status == 'active'
    
    @property
    def active_subscription(self):
        """Get the active subscription for the reseller"""
        return ResellerSubscription.query.filter_by(
            reseller_id=self.id, 
            status='active'
        ).first()

class ResellerSubscription(db.Model):
    """
    Subscription information for resellers.
    """
    __tablename__ = 'reseller_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    
    # Subscription details
    plan_code = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, canceled, expired
    external_id = db.Column(db.String(100))  # Cheddar subscription ID
    
    # Billing details
    billing_period = db.Column(db.String(20), default='month')  # month, year
    price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(3), default='USD')
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    next_billing_date = db.Column(db.DateTime)
    cancellation_date = db.Column(db.DateTime)
    
    # Payment information
    payment_method = db.Column(db.String(20), default='credit_card')  # credit_card, invoice, bank_transfer
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    cancellation_reason = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    reseller = db.relationship('Reseller', back_populates='subscriptions')
    
    def __repr__(self):
        return f"<ResellerSubscription {self.id}: {self.plan_code} for Reseller {self.reseller_id}>"
    
    @property
    def is_active(self):
        """Check if subscription is active"""
        return self.status == 'active'
    
    @property
    def formatted_price(self):
        """Get formatted price with currency"""
        return f"{self.currency_code} {self.price:.2f}"

class ResellerInvoice(db.Model):
    """
    Invoice information for resellers.
    """
    __tablename__ = 'reseller_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    
    # Invoice details
    external_id = db.Column(db.String(100))  # Cheddar invoice ID
    invoice_number = db.Column(db.String(50))
    amount = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(3), default='USD')
    status = db.Column(db.String(20), default='open')  # open, paid, failed, canceled
    
    # Dates
    due_date = db.Column(db.DateTime, nullable=False)
    paid_date = db.Column(db.DateTime)
    
    # Additional data
    invoice_data = db.Column(db.JSON)  # Full invoice data from Cheddar
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    reseller = db.relationship('Reseller', back_populates='invoices')
    
    def __repr__(self):
        return f"<ResellerInvoice {self.id}: {self.invoice_number} for Reseller {self.reseller_id}>"
    
    @property
    def is_paid(self):
        """Check if invoice is paid"""
        return self.status == 'paid'
    
    @property
    def formatted_amount(self):
        """Get formatted amount with currency"""
        return f"{self.currency_code} {self.amount:.2f}"

class ResellerRevenue(db.Model):
    """
    Revenue transactions for resellers.
    """
    __tablename__ = 'reseller_revenue'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(20), nullable=False)  # subscription, commission, fee
    amount = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(3), default='USD')
    description = db.Column(db.String(255))
    
    # Related entities
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    parent_reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    
    # External reference
    external_id = db.Column(db.String(100))  # Reference ID from payment processor
    
    # Timestamps
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - specify foreign keys explicitly to resolve ambiguity
    reseller = db.relationship('Reseller', foreign_keys=[reseller_id], backref=db.backref(
        'revenue_transactions', lazy='dynamic'
    ))
    parent_reseller = db.relationship('Reseller', foreign_keys=[parent_reseller_id], backref=db.backref(
        'sub_reseller_revenue', lazy='dynamic'
    ))
    licensee = db.relationship('Licensee', backref='revenue_transactions')
    
    def __repr__(self):
        return f"<ResellerRevenue {self.id}: {self.transaction_type} for Reseller {self.reseller_id}>"
    
    @property
    def formatted_amount(self):
        """Get formatted amount with currency"""
        return f"{self.currency_code} {self.amount:.2f}"

class ResellerBranding(db.Model):
    """
    Branding customization for resellers.
    """
    __tablename__ = 'reseller_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False, unique=True)
    
    # Brand assets
    logo_path = db.Column(db.String(255))
    favicon_path = db.Column(db.String(255))
    banner_path = db.Column(db.String(255))
    
    # Brand colors
    primary_color = db.Column(db.String(20), default='#0d6efd')
    secondary_color = db.Column(db.String(20), default='#6c757d')
    accent_color = db.Column(db.String(20))
    
    # Brand content
    company_tagline = db.Column(db.String(255))
    company_description = db.Column(db.Text)
    
    # Social media
    facebook_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    
    # Contact information (override)
    contact_email_override = db.Column(db.String(120))
    contact_phone_override = db.Column(db.String(20))
    
    # Footer customization
    custom_footer_html = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    reseller = db.relationship('Reseller', back_populates='branding')
    
    def __repr__(self):
        return f"<ResellerBranding {self.id} for Reseller {self.reseller_id}>"

class PortalUser(db.Model):
    """
    Users with access to reseller portal.
    """
    __tablename__ = 'portal_users'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Role and permissions
    role = db.Column(db.String(20), default='admin')  # admin, manager, viewer
    permissions = db.Column(db.JSON)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    reseller = db.relationship('Reseller', back_populates='portal_users')
    user = db.relationship('User', backref='portal_access')
    
    def __repr__(self):
        return f"<PortalUser {self.id}: User {self.user_id} for Reseller {self.reseller_id}>"

class Licensee(db.Model):
    """
    End customer licensee of the white-label platform.
    """
    __tablename__ = 'licensees'
    
    id = db.Column(db.Integer, primary_key=True)
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'), nullable=False)
    
    # Basic information
    company_name = db.Column(db.String(100), nullable=False)
    license_key = db.Column(db.String(100), unique=True, nullable=False)
    external_id = db.Column(db.String(100), unique=True)  # Cheddar customer ID
    
    # Contact information
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20))
    contact_name = db.Column(db.String(100))
    
    # Platform settings
    domain_name = db.Column(db.String(255))
    subdomain = db.Column(db.String(50), unique=True)
    white_label_enabled = db.Column(db.Boolean, default=True)
    
    # License details
    license_type = db.Column(db.String(20), default='standard')  # standard, premium, enterprise
    license_status = db.Column(db.String(20), default='active')  # active, suspended, expired
    max_users = db.Column(db.Integer, default=10)
    features = db.Column(db.JSON)  # Enabled features
    
    # Dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    reseller = db.relationship('Reseller', back_populates='licensees')
    branding = db.relationship('LicenseeBranding', uselist=False, back_populates='licensee', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Licensee {self.id}: {self.company_name}>"
    
    @property
    def full_domain(self):
        """Get the full domain for the licensee"""
        if self.domain_name:
            return self.domain_name
        elif self.subdomain:
            if self.reseller.domain_name:
                return f"{self.subdomain}.{self.reseller.domain_name}"
            else:
                return f"{self.subdomain}.{self.reseller.subdomain}.deaffirst.com"
        else:
            return None
    
    @property
    def is_active(self):
        """Check if license is active"""
        return self.license_status == 'active'

class LicenseeBranding(db.Model):
    """
    Branding customization for licensees.
    """
    __tablename__ = 'licensee_branding'
    
    id = db.Column(db.Integer, primary_key=True)
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'), nullable=False, unique=True)
    
    # Brand assets
    logo_path = db.Column(db.String(255))
    favicon_path = db.Column(db.String(255))
    banner_path = db.Column(db.String(255))
    
    # Brand colors
    primary_color = db.Column(db.String(20), default='#0d6efd')
    secondary_color = db.Column(db.String(20), default='#6c757d')
    accent_color = db.Column(db.String(20))
    
    # Brand content
    company_tagline = db.Column(db.String(255))
    company_description = db.Column(db.Text)
    
    # Social media
    facebook_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    
    # Contact information (override)
    contact_email_override = db.Column(db.String(120))
    contact_phone_override = db.Column(db.String(20))
    
    # Custom CSS
    custom_css = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    licensee = db.relationship('Licensee', back_populates='branding')
    
    def __repr__(self):
        return f"<LicenseeBranding {self.id} for Licensee {self.licensee_id}>"
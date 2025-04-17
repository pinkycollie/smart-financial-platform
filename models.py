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
    
    # DEAF FIRST specific fields
    account_type = db.Column(db.String(20), default='deaf_user')  # investor, shareholder, beta_user, deaf_user
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    account_status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    preferred_communication_method = db.Column(db.String(20), default='text')  # ASL_video, text, captions
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    accessibility_settings = db.Column(db.JSON, default={})
    eula_accepted = db.Column(db.Boolean, default=False)
    
    # Relationships
    financial_profiles = db.relationship('FinancialProfile', back_populates='user', cascade='all, delete-orphan')
    tax_documents = db.relationship('TaxDocument', back_populates='user', cascade='all, delete-orphan')
    eula_acceptances = db.relationship('EULAAcceptance', back_populates='user', cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check user password"""
        return check_password_hash(self.password_hash, password)
    
    def is_premium(self):
        """Check if user has an active premium subscription"""
        if self.account_type == 'premium':
            return True
        
        # Check for active subscriptions
        active_sub = Subscription.query.filter_by(
            user_id=self.id, 
            status='active'
        ).first()
        
        return active_sub is not None
    
    def __repr__(self):
        return f"<User {self.username}>"


class Subscription(db.Model):
    """User subscription information"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    plan_name = db.Column(db.String(50), nullable=False)  # e.g., "DEAF FIRST Premium"
    price = db.Column(db.Float, nullable=False)
    billing_interval = db.Column(db.String(20), nullable=False)  # monthly, yearly
    status = db.Column(db.String(20), default='pending')  # pending, active, cancelled, expired
    
    # Payment tracking
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    payment_method = db.Column(db.String(50))
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    next_billing_date = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='subscriptions')
    
    def __repr__(self):
        return f"<Subscription {self.id} - {self.plan_name} ({self.status})>"


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


class EULAAcceptance(db.Model):
    """Records of user EULA acceptances"""
    __tablename__ = 'eula_acceptances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    eula_version = db.Column(db.String(50), nullable=False)
    accepted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    
    # Relationship
    user = db.relationship('User', back_populates='eula_acceptances')
    
    def __repr__(self):
        return f"<EULAAcceptance v{self.eula_version} for User {self.user_id}>"


class InsuranceProduct(db.Model):
    """Insurance products available through Boost Insurance API"""
    __tablename__ = 'insurance_products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coverage_type = db.Column(db.String(50))  # health, property_casualty, liability, business, etc.
    coverage_category = db.Column(db.String(50))  # Standard or DeafFirst
    minimum_premium = db.Column(db.Float)
    maximum_coverage = db.Column(db.Float)
    asl_video_id = db.Column(db.String(100))  # Mux video ID for ASL explanation
    active = db.Column(db.Boolean, default=True)
    is_deaf_specialized = db.Column(db.Boolean, default=False)  # Specialized for deaf/HOH users
    accessibility_features = db.Column(db.JSON)  # Features specific to deaf/HOH users
    mandatory_components = db.Column(db.JSON)  # Required components of this insurance product
    optional_components = db.Column(db.JSON)  # Optional add-ons available
    deaf_first_differentiation = db.Column(db.Text)  # How this differs from standard market products
    annual_cost_range = db.Column(db.String(50))  # Estimated annual cost range
    potential_carriers = db.Column(db.JSON)  # Potential insurance carriers offering this product
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    policies = db.relationship('InsurancePolicy', back_populates='product')
    bundle_products = db.relationship('InsuranceBundleProduct', back_populates='product')
    
    def __repr__(self):
        return f"<InsuranceProduct {self.name}>"


class InsuranceBundle(db.Model):
    """Insurance bundles that combine multiple products for comprehensive coverage"""
    __tablename__ = 'insurance_bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bundle_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    integration_point = db.Column(db.String(100))  # e.g., Communication Access Bundle
    integration_rationale = db.Column(db.Text)  # Why these products are bundled together
    implementation_requirements = db.Column(db.Text)  # Required for implementation
    expected_outcome = db.Column(db.Text)  # Expected benefits of the bundle
    discount_percentage = db.Column(db.Float, default=0.0)  # Bundle discount
    asl_video_id = db.Column(db.String(100))  # Mux video ID for ASL explanation
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    bundle_products = db.relationship('InsuranceBundleProduct', back_populates='bundle')
    user_bundles = db.relationship('UserInsuranceBundle', back_populates='bundle')
    
    def __repr__(self):
        return f"<InsuranceBundle {self.name}>"


class InsuranceBundleProduct(db.Model):
    """Many-to-many relationship between bundles and products with additional attributes"""
    __tablename__ = 'insurance_bundle_products'
    
    id = db.Column(db.Integer, primary_key=True)
    bundle_id = db.Column(db.Integer, db.ForeignKey('insurance_bundles.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)  # Whether this is a primary or supporting product
    custom_discount = db.Column(db.Float)  # Product-specific discount within bundle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bundle = db.relationship('InsuranceBundle', back_populates='bundle_products')
    product = db.relationship('InsuranceProduct', back_populates='bundle_products')
    
    def __repr__(self):
        return f"<BundleProduct {self.bundle_id}:{self.product_id}>"


class UserInsuranceBundle(db.Model):
    """Users' insurance bundles purchased"""
    __tablename__ = 'user_insurance_bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bundle_id = db.Column(db.Integer, db.ForeignKey('insurance_bundles.id'), nullable=False)
    bundle_number = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, active, cancelled, expired
    total_premium = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('insurance_bundles', lazy='dynamic'))
    bundle = db.relationship('InsuranceBundle', back_populates='user_bundles')
    bundle_policies = db.relationship('BundlePolicyLink', back_populates='user_bundle')
    
    def __repr__(self):
        return f"<UserInsuranceBundle {self.bundle_number} for User {self.user_id}>"


class BundlePolicyLink(db.Model):
    """Links between user bundles and individual policies"""
    __tablename__ = 'bundle_policy_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_bundle_id = db.Column(db.Integer, db.ForeignKey('user_insurance_bundles.id'), nullable=False)
    policy_id = db.Column(db.Integer, db.ForeignKey('insurance_policies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_bundle = db.relationship('UserInsuranceBundle', back_populates='bundle_policies')
    policy = db.relationship('InsurancePolicy', backref=db.backref('bundle_links', lazy='dynamic'))
    
    def __repr__(self):
        return f"<BundlePolicyLink {self.user_bundle_id}:{self.policy_id}>"


class InsurancePolicy(db.Model):
    """User insurance policies purchased through Boost Insurance API"""
    __tablename__ = 'insurance_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('insurance_products.id'), nullable=False)
    policy_number = db.Column(db.String(100), unique=True)
    external_id = db.Column(db.String(100))  # Boost Insurance API identifier
    status = db.Column(db.String(20), default='pending')  # pending, active, cancelled, expired
    coverage_amount = db.Column(db.Float, nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    policy_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('insurance_policies', lazy='dynamic'))
    product = db.relationship('InsuranceProduct', back_populates='policies')
    
    def __repr__(self):
        return f"<InsurancePolicy {self.policy_number} for User {self.user_id}>"
"""
White-label licensing service for DEAF FIRST platform.
Handles licensing, feature provisioning, and customization for licensees.
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from simple_app import db
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from models_licensing import Licensee, LicenseeBranding, LicenseeBillingHistory, LicenseeFeatures

class WhiteLabelService:
    """
    Service for managing white-label licensing and customization.
    """
    
    def __init__(self, app_config=None):
        """Initialize white-label service with optional configuration"""
        self.app_config = app_config or {}
        self.upload_folder = self.app_config.get('UPLOAD_FOLDER', 'static/uploads/licensees')
        self.license_tiers = {
            "basic": {
                "name": "Basic License",
                "price": 499.00,
                "billing": "monthly",
                "features": [
                    "Core financial tools",
                    "Up to 25 clients",
                    "Email support",
                    "Basic ASL video support"
                ],
                "max_clients": 25,
                "white_label": False,
                "custom_modules": False
            },
            "professional": {
                "name": "Professional License",
                "price": 999.00,
                "billing": "monthly",
                "features": [
                    "All Basic features",
                    "Up to 100 clients",
                    "White-label branding",
                    "Priority email support",
                    "Enhanced ASL video support"
                ],
                "max_clients": 100,
                "white_label": True,
                "custom_modules": False
            },
            "enterprise": {
                "name": "Enterprise License",
                "price": 1999.00,
                "billing": "monthly",
                "features": [
                    "All Professional features",
                    "Unlimited clients",
                    "Custom module selection",
                    "Dedicated account manager",
                    "Premium ASL video support",
                    "API access"
                ],
                "max_clients": float('inf'),
                "white_label": True,
                "custom_modules": True
            }
        }
        
        # Available modules
        self.available_modules = {
            "tax_preparation": {
                "name": "Tax Preparation",
                "description": "Tax planning and preparation tools for deaf clients",
                "icon": "file-text",
                "basic_access": True
            },
            "insurance_services": {
                "name": "Insurance Services",
                "description": "Insurance comparison and management for deaf clients",
                "icon": "shield",
                "basic_access": True
            },
            "financial_education": {
                "name": "Financial Education",
                "description": "Financial literacy courses with ASL support",
                "icon": "book-open",
                "basic_access": True
            },
            "credit_restructuring": {
                "name": "Credit Restructuring",
                "description": "Credit analysis and improvement tools",
                "icon": "trending-up",
                "basic_access": False
            },
            "investor_portal": {
                "name": "Investor Portal",
                "description": "Investment management with ASL guidance",
                "icon": "bar-chart-2",
                "basic_access": False
            },
            "advisor_resources": {
                "name": "Advisor Resources",
                "description": "Tools and training for financial advisors serving deaf clients",
                "icon": "briefcase",
                "basic_access": False
            },
            "client_portal": {
                "name": "Client Portal",
                "description": "Client-facing dashboard for account management",
                "icon": "users",
                "basic_access": False
            },
            "analytical_tools": {
                "name": "Analytical Tools",
                "description": "Advanced financial analysis and reporting",
                "icon": "activity",
                "basic_access": False
            }
        }
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def get_license_tiers(self):
        """
        Get available license tiers.
        
        Returns:
            dict: License tier information
        """
        return self.license_tiers
    
    def get_available_modules(self):
        """
        Get available modules.
        
        Returns:
            dict: Available modules
        """
        return self.available_modules
    
    def create_licensee(self, company_name, contact_email, license_tier="basic", **kwargs):
        """
        Create a new licensee.
        
        Args:
            company_name (str): Company name
            contact_email (str): Contact email
            license_tier (str): License tier (basic, professional, enterprise)
            **kwargs: Additional licensee properties
            
        Returns:
            Licensee: The created licensee
        """
        # Generate a secure subdomain from company name
        subdomain = self._generate_subdomain(company_name)
        
        # Get tier details
        tier_details = self.license_tiers.get(license_tier, self.license_tiers["basic"])
        
        # Generate license and API keys
        license_key = self._generate_license_key()
        api_key = self._generate_api_key()
        
        # Create licensee
        licensee = Licensee(
            company_name=company_name,
            subdomain=subdomain,
            license_tier=license_tier,
            contact_email=contact_email,
            
            # Set tier-specific limits
            max_clients=tier_details["max_clients"],
            white_label_enabled=tier_details["white_label"],
            custom_modules_enabled=tier_details["custom_modules"],
            
            # License details
            license_key=license_key,
            api_key=api_key,
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            
            # Billing information
            billing_cycle=tier_details["billing"],
            billing_amount=tier_details["price"],
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
        )
        
        # Update with any additional properties
        for key, value in kwargs.items():
            if hasattr(licensee, key):
                setattr(licensee, key, value)
        
        # Add to database
        db.session.add(licensee)
        db.session.flush()  # Get ID without committing
        
        # Create default branding
        branding = LicenseeBranding(
            licensee_id=licensee.id,
            primary_color="#0066CC",
            secondary_color="#00AA55",
            company_tagline=f"{company_name} - Financial Services",
            welcome_message=f"Welcome to {company_name}'s Financial Platform",
            footer_text=f"© {datetime.utcnow().year} {company_name}. All rights reserved.",
            show_powered_by=True
        )
        
        db.session.add(branding)
        
        # Set up default features based on tier
        self._setup_default_features(licensee)
        
        db.session.commit()
        
        return licensee
    
    def update_licensee(self, licensee_id, **kwargs):
        """
        Update a licensee's properties.
        
        Args:
            licensee_id (int): Licensee ID
            **kwargs: Properties to update
            
        Returns:
            Licensee: The updated licensee
        """
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Update tier-specific properties if tier is changing
        if 'license_tier' in kwargs and kwargs['license_tier'] != licensee.license_tier:
            tier_details = self.license_tiers.get(kwargs['license_tier'], self.license_tiers["basic"])
            
            # Only update these properties if they weren't explicitly provided
            if 'max_clients' not in kwargs:
                kwargs['max_clients'] = tier_details["max_clients"]
            if 'white_label_enabled' not in kwargs:
                kwargs['white_label_enabled'] = tier_details["white_label"]
            if 'custom_modules_enabled' not in kwargs:
                kwargs['custom_modules_enabled'] = tier_details["custom_modules"]
            
            # Update features based on new tier
            self._update_features_for_tier(licensee, kwargs['license_tier'])
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(licensee, key):
                setattr(licensee, key, value)
        
        db.session.commit()
        return licensee
    
    def update_licensee_branding(self, licensee_id, **kwargs):
        """
        Update a licensee's branding.
        
        Args:
            licensee_id (int): Licensee ID
            **kwargs: Branding properties to update
            
        Returns:
            LicenseeBranding: The updated branding
        """
        # Verify licensee exists and can use white-label
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        if not licensee.white_label_enabled:
            raise ValueError(f"Licensee {licensee.company_name} does not have white-label enabled")
        
        branding = LicenseeBranding.query.filter_by(licensee_id=licensee_id).first()
        if not branding:
            # Create if doesn't exist
            branding = LicenseeBranding(licensee_id=licensee_id)
            db.session.add(branding)
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(branding, key):
                setattr(branding, key, value)
        
        db.session.commit()
        return branding
    
    def upload_logo(self, licensee_id, logo_file, light_version=False):
        """
        Upload a logo for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            logo_file: Uploaded file object
            light_version (bool): Whether this is the light version of the logo
            
        Returns:
            str: Logo path
        """
        # Verify licensee exists and can use white-label
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        if not licensee.white_label_enabled:
            raise ValueError(f"Licensee {licensee.company_name} does not have white-label enabled")
        
        if not logo_file:
            return None
            
        # Ensure filename is secure
        filename = secure_filename(logo_file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Only allow certain file extensions
        if file_ext not in ['.jpg', '.jpeg', '.png', '.svg']:
            raise ValueError("Invalid file extension. Allowed: .jpg, .jpeg, .png, .svg")
        
        # Create a unique filename
        unique_filename = f"licensee_{licensee_id}_logo_{'light' if light_version else 'dark'}_{uuid.uuid4().hex}{file_ext}"
        
        # Create the upload folder if it doesn't exist
        licensee_upload_folder = os.path.join(self.upload_folder, str(licensee_id))
        os.makedirs(licensee_upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(licensee_upload_folder, unique_filename)
        logo_file.save(file_path)
        
        # Get relative path for database
        relative_path = os.path.join('uploads/licensees', str(licensee_id), unique_filename)
        
        # Update branding
        branding = LicenseeBranding.query.filter_by(licensee_id=licensee_id).first()
        if not branding:
            branding = LicenseeBranding(licensee_id=licensee_id)
            db.session.add(branding)
        
        if light_version:
            branding.logo_light_path = relative_path
        else:
            branding.logo_path = relative_path
            
        db.session.commit()
        
        return relative_path
    
    def get_allowed_modules(self, licensee_id):
        """
        Get all modules allowed for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            dict: Module information with access status
        """
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Get licensee features
        features = LicenseeFeatures.query.filter_by(licensee_id=licensee_id).first()
        if not features:
            # Create default features
            features = self._setup_default_features(licensee)
        
        # Get enabled modules
        enabled_modules = features.enabled_modules or []
        
        # Build module access dict
        modules = {}
        for module_id, module_info in self.available_modules.items():
            # Module is accessible if:
            # 1. It's a basic module and user has at least basic tier, OR
            # 2. It's explicitly enabled for this licensee
            has_access = (module_info['basic_access'] or module_id in enabled_modules)
            
            modules[module_id] = {
                'name': module_info['name'],
                'description': module_info['description'],
                'icon': module_info['icon'],
                'has_access': has_access
            }
        
        return modules
    
    def update_licensee_modules(self, licensee_id, enabled_modules):
        """
        Update which modules a licensee has access to.
        
        Args:
            licensee_id (int): Licensee ID
            enabled_modules (list): List of module IDs to enable
            
        Returns:
            LicenseeFeatures: The updated features
        """
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Only enterprise tier can customize modules
        if not licensee.custom_modules_enabled:
            raise ValueError(f"Licensee {licensee.company_name} cannot customize modules")
        
        # Validate module IDs
        for module_id in enabled_modules:
            if module_id not in self.available_modules:
                raise ValueError(f"Invalid module ID: {module_id}")
        
        # Get features
        features = LicenseeFeatures.query.filter_by(licensee_id=licensee_id).first()
        if not features:
            features = LicenseeFeatures(licensee_id=licensee_id)
            db.session.add(features)
        
        # Update modules
        features.enabled_modules = enabled_modules
        
        db.session.commit()
        return features
    
    def get_licensee_stats(self, licensee_id):
        """
        Get statistics for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            dict: Licensee statistics
        """
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Get module access
        modules = self.get_allowed_modules(licensee_id)
        enabled_count = sum(1 for m in modules.values() if m['has_access'])
        
        # Get billing history
        billing_history = LicenseeBillingHistory.query.filter_by(
            licensee_id=licensee_id
        ).order_by(LicenseeBillingHistory.billing_date.desc()).limit(5).all()
        
        # Calculate days until renewal
        days_until_renewal = 0
        if licensee.license_end_date:
            today = datetime.utcnow().date()
            days_until_renewal = (licensee.license_end_date - today).days
        
        # Calculate days until next billing
        days_until_billing = 0
        if licensee.next_billing_date:
            today = datetime.utcnow().date()
            days_until_billing = (licensee.next_billing_date - today).days
        
        return {
            "licensee": {
                "id": licensee.id,
                "company_name": licensee.company_name,
                "tier": licensee.license_tier,
                "status": licensee.status
            },
            "client_counts": {
                "current": licensee.current_clients,
                "max": licensee.max_clients
            },
            "modules": {
                "total_available": len(modules),
                "enabled": enabled_count
            },
            "license": {
                "start_date": licensee.license_start_date.strftime('%Y-%m-%d') if licensee.license_start_date else None,
                "end_date": licensee.license_end_date.strftime('%Y-%m-%d') if licensee.license_end_date else None,
                "days_until_renewal": days_until_renewal
            },
            "billing": {
                "amount": licensee.billing_amount,
                "cycle": licensee.billing_cycle,
                "next_date": licensee.next_billing_date.strftime('%Y-%m-%d') if licensee.next_billing_date else None,
                "days_until_billing": days_until_billing,
                "recent_history": [
                    {
                        "date": bill.billing_date.strftime('%Y-%m-%d'),
                        "amount": bill.amount,
                        "status": bill.payment_status
                    } for bill in billing_history
                ]
            },
            "features": {
                "white_label_enabled": licensee.white_label_enabled,
                "custom_modules_enabled": licensee.custom_modules_enabled
            }
        }
    
    def apply_licensee_branding(self, licensee_id, context=None):
        """
        Apply branding settings for a specific licensee to a context.
        
        Args:
            licensee_id (int): Licensee ID
            context (dict, optional): Context to update with branding
            
        Returns:
            dict: Updated context with branding settings
        """
        if context is None:
            context = {}
        
        licensee = Licensee.query.get(licensee_id)
        if not licensee or not licensee.branding:
            return context
        
        branding = licensee.branding
        
        context['licensee'] = {
            'company_name': licensee.company_name,
            'logo_url': url_for('static', filename=branding.logo_path) if branding.logo_path else None,
            'logo_light_url': url_for('static', filename=branding.logo_light_path) if branding.logo_light_path else None,
            'primary_color': branding.primary_color,
            'secondary_color': branding.secondary_color,
            'accent_color': branding.accent_color,
            'font_family': branding.font_family,
            'company_tagline': branding.company_tagline,
            'welcome_message': branding.welcome_message,
            'footer_text': branding.footer_text,
            'show_powered_by': branding.show_powered_by,
            'custom_css': branding.custom_css,
            'custom_javascript': branding.custom_javascript,
            'social_links': {
                'facebook': branding.facebook_url,
                'twitter': branding.twitter_url,
                'linkedin': branding.linkedin_url,
                'instagram': branding.instagram_url
            }
        }
        
        return context
    
    def _generate_subdomain(self, company_name):
        """Generate a subdomain from company name."""
        # Remove non-alphanumeric characters and convert to lowercase
        subdomain = ''.join(c for c in company_name if c.isalnum()).lower()
        
        # Ensure subdomain is unique
        base_subdomain = subdomain
        counter = 1
        
        while self._subdomain_exists(subdomain):
            subdomain = f"{base_subdomain}{counter}"
            counter += 1
        
        return subdomain
    
    def _subdomain_exists(self, subdomain):
        """Check if a subdomain already exists."""
        return Licensee.query.filter_by(subdomain=subdomain).first() is not None
    
    def _generate_license_key(self):
        """Generate a unique license key."""
        return f"DEAFFIRST-{uuid.uuid4().hex[:16].upper()}"
    
    def _generate_api_key(self):
        """Generate a unique API key."""
        return f"df_api_{uuid.uuid4().hex}"
    
    def _setup_default_features(self, licensee):
        """Set up default features for a licensee based on tier."""
        # Get any existing features
        features = LicenseeFeatures.query.filter_by(licensee_id=licensee.id).first()
        
        if not features:
            # Create new features
            features = LicenseeFeatures(licensee_id=licensee.id)
            db.session.add(features)
        
        # Update features based on tier
        self._update_features_for_tier(licensee, licensee.license_tier)
        
        return features
    
    def _update_features_for_tier(self, licensee, tier):
        """Update features for a licensee based on tier."""
        features = LicenseeFeatures.query.filter_by(licensee_id=licensee.id).first()
        
        if not features:
            # Create new features
            features = LicenseeFeatures(licensee_id=licensee.id)
            db.session.add(features)
        
        # Basic tier: Only basic modules
        if tier == 'basic':
            # Enable only basic modules
            basic_modules = [module_id for module_id, module_info in self.available_modules.items() 
                            if module_info['basic_access']]
            features.enabled_modules = basic_modules
        
        # Professional tier: Basic modules + some additional
        elif tier == 'professional':
            # Enable basic modules plus client portal
            pro_modules = [module_id for module_id, module_info in self.available_modules.items() 
                          if module_info['basic_access']]
            pro_modules.append('client_portal')
            features.enabled_modules = pro_modules
        
        # Enterprise tier: All modules by default
        elif tier == 'enterprise':
            # Enable all modules
            all_modules = list(self.available_modules.keys())
            features.enabled_modules = all_modules
        
        db.session.commit()

# Initialize a single instance to be used application-wide
white_label_service = WhiteLabelService()
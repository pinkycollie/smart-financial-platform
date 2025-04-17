"""
Reseller management service for DEAF FIRST platform.
Handles reseller creation, configuration, and white-label management.
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from simple_app import db
from models_reseller import (
    Reseller, ResellerBranding, SubReseller, 
    SubResellerBranding, ResellerAdmin
)
from models import User
from models_licensing import Licensee, LicenseeBranding

class ResellerManagementService:
    """
    Service for managing resellers and their white-label configurations.
    """
    
    def __init__(self, app_config=None):
        """Initialize reseller management service with optional configuration"""
        self.app_config = app_config or {}
        self.upload_folder = self.app_config.get('UPLOAD_FOLDER', 'static/uploads/resellers')
        self.reseller_tiers = {
            "standard": {
                "name": "Standard Reseller",
                "price": 1999.00,
                "billing": "monthly",
                "features": [
                    "White-label platform",
                    "Up to 25 licensees",
                    "Basic branding customization",
                    "Email support"
                ],
                "max_licensees": 25,
                "max_sub_resellers": 0,
                "can_customize_modules": False,
                "can_set_pricing": False,
                "can_create_sub_resellers": False,
                "can_edit_source_code": False,
                "commission_rate": 20.0
            },
            "premium": {
                "name": "Premium Reseller",
                "price": 4999.00,
                "billing": "monthly",
                "features": [
                    "All Standard features",
                    "Up to 100 licensees",
                    "Up to 5 sub-resellers",
                    "Advanced branding customization",
                    "Custom pricing capability",
                    "Priority support",
                    "Usage analytics"
                ],
                "max_licensees": 100,
                "max_sub_resellers": 5,
                "can_customize_modules": False,
                "can_set_pricing": True,
                "can_create_sub_resellers": True,
                "can_edit_source_code": False,
                "commission_rate": 30.0
            },
            "enterprise": {
                "name": "Enterprise Reseller",
                "price": 9999.00,
                "billing": "monthly",
                "features": [
                    "All Premium features",
                    "Unlimited licensees",
                    "Unlimited sub-resellers",
                    "Module customization",
                    "Source code access",
                    "Dedicated account manager",
                    "Quarterly strategy sessions"
                ],
                "max_licensees": float('inf'),
                "max_sub_resellers": float('inf'),
                "can_customize_modules": True,
                "can_set_pricing": True,
                "can_create_sub_resellers": True,
                "can_edit_source_code": True,
                "commission_rate": 40.0
            }
        }
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def get_reseller_tiers(self):
        """
        Get available reseller tiers.
        
        Returns:
            dict: Reseller tier information
        """
        return self.reseller_tiers
    
    def create_reseller(self, company_name, contact_email, reseller_tier="standard", **kwargs):
        """
        Create a new reseller.
        
        Args:
            company_name (str): Company name
            contact_email (str): Contact email
            reseller_tier (str): Reseller tier (standard, premium, enterprise)
            **kwargs: Additional reseller properties
            
        Returns:
            Reseller: The created reseller
        """
        # Generate a secure subdomain from company name
        subdomain = self._generate_subdomain(company_name)
        
        # Get tier details
        tier_details = self.reseller_tiers.get(reseller_tier, self.reseller_tiers["standard"])
        
        # Generate license and API keys
        license_key = self._generate_license_key()
        api_key = self._generate_api_key()
        
        # Create reseller
        reseller = Reseller(
            company_name=company_name,
            primary_domain=subdomain + ".deaffirst.com",
            reseller_tier=reseller_tier,
            contact_email=contact_email,
            
            # Set tier-specific limits
            max_licensees=tier_details["max_licensees"],
            max_sub_resellers=tier_details["max_sub_resellers"],
            commission_rate=tier_details["commission_rate"],
            
            # Feature flags
            can_customize_modules=tier_details["can_customize_modules"],
            can_set_pricing=tier_details["can_set_pricing"],
            can_create_sub_resellers=tier_details["can_create_sub_resellers"],
            can_edit_source_code=tier_details["can_edit_source_code"],
            
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
            if hasattr(reseller, key):
                setattr(reseller, key, value)
        
        # Add to database
        db.session.add(reseller)
        db.session.flush()  # Get ID without committing
        
        # Create default branding
        branding = ResellerBranding(
            reseller_id=reseller.id,
            primary_color="#0066CC",
            secondary_color="#00AA55",
            company_tagline=f"{company_name} - Financial Services for the Deaf Community",
            welcome_message=f"Welcome to {company_name}'s Financial Platform",
            footer_text=f"© {datetime.utcnow().year} {company_name}. All rights reserved.",
            show_powered_by=True
        )
        
        db.session.add(branding)
        db.session.commit()
        
        return reseller
    
    def update_reseller(self, reseller_id, **kwargs):
        """
        Update a reseller's properties.
        
        Args:
            reseller_id (int): Reseller ID
            **kwargs: Properties to update
            
        Returns:
            Reseller: The updated reseller
        """
        reseller = Reseller.query.get(reseller_id)
        if not reseller:
            raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        # Update tier-specific properties if tier is changing
        if 'reseller_tier' in kwargs and kwargs['reseller_tier'] != reseller.reseller_tier:
            tier_details = self.reseller_tiers.get(kwargs['reseller_tier'], self.reseller_tiers["standard"])
            
            # Only update these properties if they weren't explicitly provided
            if 'max_licensees' not in kwargs:
                kwargs['max_licensees'] = tier_details["max_licensees"]
            if 'max_sub_resellers' not in kwargs:
                kwargs['max_sub_resellers'] = tier_details["max_sub_resellers"]
            if 'commission_rate' not in kwargs:
                kwargs['commission_rate'] = tier_details["commission_rate"]
            if 'can_customize_modules' not in kwargs:
                kwargs['can_customize_modules'] = tier_details["can_customize_modules"]
            if 'can_set_pricing' not in kwargs:
                kwargs['can_set_pricing'] = tier_details["can_set_pricing"]
            if 'can_create_sub_resellers' not in kwargs:
                kwargs['can_create_sub_resellers'] = tier_details["can_create_sub_resellers"]
            if 'can_edit_source_code' not in kwargs:
                kwargs['can_edit_source_code'] = tier_details["can_edit_source_code"]
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(reseller, key):
                setattr(reseller, key, value)
        
        db.session.commit()
        return reseller
    
    def update_reseller_branding(self, reseller_id, **kwargs):
        """
        Update a reseller's branding.
        
        Args:
            reseller_id (int): Reseller ID
            **kwargs: Branding properties to update
            
        Returns:
            ResellerBranding: The updated branding
        """
        branding = ResellerBranding.query.filter_by(reseller_id=reseller_id).first()
        if not branding:
            # Create if doesn't exist
            branding = ResellerBranding(reseller_id=reseller_id)
            db.session.add(branding)
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(branding, key):
                setattr(branding, key, value)
        
        db.session.commit()
        return branding
    
    def upload_logo(self, reseller_id, logo_file, light_version=False):
        """
        Upload a logo for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            logo_file: Uploaded file object
            light_version (bool): Whether this is the light version of the logo
            
        Returns:
            str: Logo path
        """
        if not logo_file:
            return None
            
        # Ensure filename is secure
        filename = secure_filename(logo_file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Only allow certain file extensions
        if file_ext not in ['.jpg', '.jpeg', '.png', '.svg']:
            raise ValueError("Invalid file extension. Allowed: .jpg, .jpeg, .png, .svg")
        
        # Create a unique filename
        unique_filename = f"reseller_{reseller_id}_logo_{'light' if light_version else 'dark'}_{uuid.uuid4().hex}{file_ext}"
        
        # Create the upload folder if it doesn't exist
        reseller_upload_folder = os.path.join(self.upload_folder, str(reseller_id))
        os.makedirs(reseller_upload_folder, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(reseller_upload_folder, unique_filename)
        logo_file.save(file_path)
        
        # Get relative path for database
        relative_path = os.path.join('uploads/resellers', str(reseller_id), unique_filename)
        
        # Update branding
        branding = ResellerBranding.query.filter_by(reseller_id=reseller_id).first()
        if not branding:
            branding = ResellerBranding(reseller_id=reseller_id)
            db.session.add(branding)
        
        if light_version:
            branding.logo_light_path = relative_path
        else:
            branding.logo_path = relative_path
            
        db.session.commit()
        
        return relative_path
    
    def create_sub_reseller(self, parent_reseller_id, company_name, contact_email, **kwargs):
        """
        Create a new sub-reseller under a parent reseller.
        
        Args:
            parent_reseller_id (int): Parent reseller ID
            company_name (str): Company name
            contact_email (str): Contact email
            **kwargs: Additional properties
            
        Returns:
            SubReseller: The created sub-reseller
        """
        # Get parent reseller
        parent = Reseller.query.get(parent_reseller_id)
        if not parent:
            raise ValueError(f"Parent reseller with ID {parent_reseller_id} not found")
        
        # Check if parent can create sub-resellers
        if not parent.can_create_sub_resellers:
            raise ValueError(f"Reseller {parent.company_name} cannot create sub-resellers")
        
        # Check if parent has reached sub-reseller limit
        if not parent.can_add_sub_reseller():
            raise ValueError(f"Reseller {parent.company_name} has reached sub-reseller limit")
        
        # Generate subdomain
        subdomain = self._generate_subdomain(company_name)
        
        # Create sub-reseller
        sub_reseller = SubReseller(
            parent_reseller_id=parent_reseller_id,
            company_name=company_name,
            subdomain=subdomain,
            contact_email=contact_email,
            max_licensees=kwargs.get('max_licensees', 10),
            commission_rate=kwargs.get('commission_rate', 10.0),
            can_customize_branding=kwargs.get('can_customize_branding', True),
            can_set_pricing=kwargs.get('can_set_pricing', False)
        )
        
        # Update with any additional properties
        for key, value in kwargs.items():
            if hasattr(sub_reseller, key):
                setattr(sub_reseller, key, value)
        
        # Add to database
        db.session.add(sub_reseller)
        db.session.flush()
        
        # Create default branding
        branding = SubResellerBranding(
            sub_reseller_id=sub_reseller.id,
            primary_color=parent.branding.primary_color if parent.branding else "#0066CC",
            secondary_color=parent.branding.secondary_color if parent.branding else "#00AA55",
            company_tagline=f"{company_name} - Financial Services for the Deaf Community",
            welcome_message=f"Welcome to {company_name}'s Financial Platform",
            show_powered_by=True
        )
        
        db.session.add(branding)
        
        # Increment parent's sub-reseller count
        parent.current_sub_resellers += 1
        
        db.session.commit()
        
        return sub_reseller
    
    def create_reseller_admin(self, reseller_id, email, first_name, last_name, role='admin', is_primary=False):
        """
        Create an admin user for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            email (str): Admin email
            first_name (str): First name
            last_name (str): Last name
            role (str): Admin role
            is_primary (bool): Whether this is the primary admin
            
        Returns:
            ResellerAdmin: The created admin
        """
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create user with random password (will be reset)
            from werkzeug.security import generate_password_hash
            temp_password = str(uuid.uuid4())
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password_hash=generate_password_hash(temp_password),
                user_type='reseller_admin',
                is_active=True
            )
            db.session.add(user)
            db.session.flush()
            
            # TODO: Send password reset email
        
        # Check if already an admin for this reseller
        existing = ResellerAdmin.query.filter_by(reseller_id=reseller_id, user_id=user.id).first()
        if existing:
            return existing
        
        # Set permissions based on role
        permissions = self._get_role_permissions(role)
        
        # Create admin
        admin = ResellerAdmin(
            reseller_id=reseller_id,
            user_id=user.id,
            role=role,
            permissions=permissions,
            is_primary=is_primary
        )
        
        db.session.add(admin)
        db.session.commit()
        
        return admin
    
    def create_licensee_for_reseller(self, reseller_id, company_name, contact_email, license_tier="basic", sub_reseller_id=None, **kwargs):
        """
        Create a licensee under a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            company_name (str): Company name
            contact_email (str): Contact email
            license_tier (str): License tier
            sub_reseller_id (int): Sub-reseller ID (optional)
            **kwargs: Additional properties
            
        Returns:
            Licensee: The created licensee
        """
        from services.licensing.white_label import white_label_service
        
        # Check if reseller can add licensee
        reseller = Reseller.query.get(reseller_id)
        if not reseller:
            raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        if not reseller.can_add_licensee():
            raise ValueError(f"Reseller {reseller.company_name} has reached licensee limit")
        
        # If sub-reseller provided, check if it belongs to this reseller
        if sub_reseller_id:
            sub_reseller = SubReseller.query.get(sub_reseller_id)
            if not sub_reseller or sub_reseller.parent_reseller_id != reseller_id:
                raise ValueError(f"Invalid sub-reseller ID {sub_reseller_id}")
            
            # Check if sub-reseller can add licensee
            if sub_reseller.current_licensees >= sub_reseller.max_licensees:
                raise ValueError(f"Sub-reseller {sub_reseller.company_name} has reached licensee limit")
        
        # Get tier details
        tiers = white_label_service.get_license_tiers()
        tier_details = tiers.get(license_tier, tiers["basic"])
        
        # Generate license and API keys
        license_key = self._generate_license_key()
        api_key = self._generate_api_key()
        
        # Create licensee
        licensee = Licensee(
            company_name=company_name,
            subdomain=self._generate_subdomain(company_name),
            license_tier=license_tier,
            contact_email=contact_email,
            
            # Link to reseller
            reseller_id=reseller_id,
            sub_reseller_id=sub_reseller_id,
            
            # License details
            license_key=license_key,
            api_key=api_key,
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            
            # Billing information
            billing_cycle='monthly',
            billing_amount=tier_details["price"],
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
            
            # Feature flags based on tier
            max_clients=tier_details["max_clients"],
            white_label_enabled=tier_details["white_label"],
            custom_modules_enabled=tier_details["custom_modules"]
        )
        
        # Update with any additional properties
        for key, value in kwargs.items():
            if hasattr(licensee, key):
                setattr(licensee, key, value)
        
        # Add to database
        db.session.add(licensee)
        db.session.flush()
        
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
        
        # Increment reseller's licensee count
        reseller.current_licensees += 1
        
        # If sub-reseller provided, increment its licensee count
        if sub_reseller_id:
            sub_reseller = SubReseller.query.get(sub_reseller_id)
            sub_reseller.current_licensees += 1
        
        db.session.commit()
        
        return licensee
    
    def get_reseller_licensees(self, reseller_id, include_sub_resellers=True):
        """
        Get all licensees for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            include_sub_resellers (bool): Whether to include sub-reseller licensees
            
        Returns:
            list: List of licensees
        """
        # Get direct licensees
        query = Licensee.query.filter_by(reseller_id=reseller_id)
        
        if include_sub_resellers:
            # Include sub-reseller licensees
            sub_reseller_ids = [sr.id for sr in SubReseller.query.filter_by(parent_reseller_id=reseller_id).all()]
            if sub_reseller_ids:
                query = query.union(Licensee.query.filter(Licensee.sub_reseller_id.in_(sub_reseller_ids)))
        
        return query.all()
    
    def get_sub_reseller_licensees(self, sub_reseller_id):
        """
        Get all licensees for a sub-reseller.
        
        Args:
            sub_reseller_id (int): Sub-reseller ID
            
        Returns:
            list: List of licensees
        """
        return Licensee.query.filter_by(sub_reseller_id=sub_reseller_id).all()
    
    def get_reseller_stats(self, reseller_id):
        """
        Get statistics for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            
        Returns:
            dict: Reseller statistics
        """
        reseller = Reseller.query.get(reseller_id)
        if not reseller:
            raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        # Get sub-resellers
        sub_resellers = SubReseller.query.filter_by(parent_reseller_id=reseller_id).all()
        
        # Get direct licensees
        direct_licensees = Licensee.query.filter_by(reseller_id=reseller_id, sub_reseller_id=None).all()
        
        # Get all licensees including from sub-resellers
        all_licensees = self.get_reseller_licensees(reseller_id)
        
        # Calculate client counts
        total_clients = sum(l.current_clients for l in all_licensees)
        
        # Calculate revenue (placeholder - real implementation would use the revenue service)
        monthly_revenue = sum(l.billing_amount for l in all_licensees)
        
        return {
            "reseller": {
                "id": reseller.id,
                "company_name": reseller.company_name,
                "tier": reseller.reseller_tier,
                "status": reseller.status
            },
            "counts": {
                "sub_resellers": len(sub_resellers),
                "direct_licensees": len(direct_licensees),
                "total_licensees": len(all_licensees),
                "total_clients": total_clients
            },
            "limits": {
                "max_sub_resellers": reseller.max_sub_resellers,
                "max_licensees": reseller.max_licensees
            },
            "revenue": {
                "monthly": monthly_revenue,
                "commission": monthly_revenue * (reseller.commission_rate / 100)
            }
        }
    
    def apply_reseller_branding(self, reseller_id, context=None):
        """
        Apply branding settings for a specific reseller to a context.
        
        Args:
            reseller_id (int): Reseller ID
            context (dict, optional): Context to update with branding
            
        Returns:
            dict: Updated context with branding settings
        """
        if context is None:
            context = {}
        
        reseller = Reseller.query.get(reseller_id)
        if not reseller or not reseller.branding:
            return context
        
        branding = reseller.branding
        
        context['reseller'] = {
            'company_name': reseller.company_name,
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
        reseller_exists = Reseller.query.filter(Reseller.primary_domain.like(f"{subdomain}%")).first() is not None
        licensee_exists = Licensee.query.filter_by(subdomain=subdomain).first() is not None
        sub_reseller_exists = SubReseller.query.filter_by(subdomain=subdomain).first() is not None
        
        return reseller_exists or licensee_exists or sub_reseller_exists
    
    def _generate_license_key(self):
        """Generate a unique license key."""
        return f"DEAFFIRST-{uuid.uuid4().hex[:16].upper()}"
    
    def _generate_api_key(self):
        """Generate a unique API key."""
        return f"df_api_{uuid.uuid4().hex}"
    
    def _get_role_permissions(self, role):
        """Get permissions for a specific role."""
        base_permissions = {
            "view_reseller": True,
            "view_licensees": True,
            "view_revenue": True
        }
        
        if role == 'admin':
            return {
                **base_permissions,
                "manage_reseller": True,
                "manage_branding": True,
                "manage_licensees": True,
                "manage_sub_resellers": True,
                "manage_admins": True,
                "manage_billing": True
            }
        elif role == 'sales':
            return {
                **base_permissions,
                "manage_licensees": True,
                "manage_sub_resellers": True,
                "view_commissions": True
            }
        elif role == 'support':
            return {
                **base_permissions,
                "view_licensees": True,
                "support_licensees": True
            }
        elif role == 'billing':
            return {
                **base_permissions,
                "view_billing": True,
                "manage_billing": True,
                "view_revenue": True
            }
        else:
            return base_permissions

# Initialize a single instance to be used application-wide
reseller_management_service = ResellerManagementService()
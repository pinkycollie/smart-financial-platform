"""
White-label licensing service for DEAF FIRST financial platform.
Enables customization for financial professionals serving deaf clients.
"""

import os
from datetime import datetime
from flask import current_app, render_template, url_for, request
from werkzeug.utils import secure_filename

class WhiteLabelService:
    """
    Service for managing white-label configurations and licensing
    for financial educators, advisors, and agents with deaf clients.
    """
    
    def __init__(self, app_config=None):
        """Initialize white-label service with optional configuration"""
        self.app_config = app_config or {}
        self.license_tiers = {
            "basic": {
                "name": "Basic",
                "price": 199.00,
                "billing": "monthly",
                "features": [
                    "Financial education modules with ASL",
                    "Branded login page",
                    "Up to 50 deaf clients",
                    "Email support"
                ],
                "max_clients": 50,
                "white_label": False,
                "custom_modules": False
            },
            "professional": {
                "name": "Professional",
                "price": 499.00,
                "billing": "monthly",
                "features": [
                    "All Basic features",
                    "Full white-labeling",
                    "Up to 200 deaf clients",
                    "Custom branding",
                    "Priority support",
                    "Usage analytics"
                ],
                "max_clients": 200,
                "white_label": True,
                "custom_modules": False
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 999.00,
                "billing": "monthly",
                "features": [
                    "All Professional features",
                    "Unlimited deaf clients",
                    "Custom module creation",
                    "API access",
                    "Dedicated account manager",
                    "Quarterly strategy sessions"
                ],
                "max_clients": float('inf'),
                "white_label": True,
                "custom_modules": True
            }
        }
    
    def get_license_tiers(self):
        """
        Get available license tiers for professionals.
        
        Returns:
            dict: License tier information
        """
        return self.license_tiers
    
    def apply_branding(self, licensee_id):
        """
        Apply branding settings for a specific licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            dict: Branding settings
        """
        # In a real implementation, this would fetch from database
        # For now, return dummy data
        licensee_branding = {
            "company_name": "Example Financial Services",
            "logo_url": url_for('static', filename=f'licensee/{licensee_id}/logo.png'),
            "primary_color": "#0066CC",
            "secondary_color": "#00AA55",
            "font_family": "Open Sans, sans-serif",
            "contact_email": "contact@example.com",
            "contact_phone": "555-123-4567",
            "show_powered_by": True
        }
        
        return licensee_branding
    
    def generate_license_agreement(self, tier="professional", company_name=None, licensee_name=None):
        """
        Generate a license agreement document.
        
        Args:
            tier (str): License tier
            company_name (str): Licensee company name
            licensee_name (str): Licensee name
            
        Returns:
            str: License agreement text
        """
        tier_data = self.license_tiers.get(tier, self.license_tiers["professional"])
        today = datetime.now().strftime("%Y-%m-%d")
        
        agreement = f"""
        DEAF FIRST PLATFORM LICENSE AGREEMENT
        
        This License Agreement (the "Agreement") is made effective as of {today} by and between:
        
        MBTQ GROUP ("Licensor")
        
        and
        
        {company_name or '[COMPANY NAME]'} ("Licensee")
        
        TERMS AND CONDITIONS:
        
        1. LICENSE GRANT
        
        Licensor grants Licensee a non-exclusive, non-transferable license to use the DEAF FIRST Financial Platform 
        (the "Platform") under the {tier_data["name"]} tier for the purpose of providing financial services to deaf clients.
        
        2. PERMITTED USES
        
        Licensee may:
        - Access and use the Platform for up to {tier_data["max_clients"]} deaf clients
        - {"Customize branding and appearance as specified in the white-label settings" if tier_data["white_label"] else "Use the Platform with standard DEAF FIRST branding"}
        - {"Create custom educational modules subject to Licensor approval" if tier_data["custom_modules"] else "Use the standard educational modules provided"}
        
        3. RESTRICTIONS
        
        Licensee may not:
        - Sublicense, sell, lease, or otherwise transfer the Platform
        - Modify, adapt, or create derivative works except as permitted in this Agreement
        - Remove or alter any proprietary notices or branding except as permitted by white-label settings
        - Exceed the client limit specified in the license tier
        
        4. FEES AND PAYMENT
        
        Licensee agrees to pay ${tier_data["price"]} per month, billed {tier_data["billing"]}.
        
        5. TERM AND TERMINATION
        
        This Agreement shall remain in effect until terminated. Either party may terminate with 30 days written notice.
        
        6. OWNERSHIP
        
        The Platform and all intellectual property rights remain the exclusive property of Licensor.
        
        7. SUPPORT
        
        Licensor will provide support as specified in the {tier_data["name"]} tier.
        
        8. LIMITATION OF LIABILITY
        
        IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES.
        
        9. GOVERNING LAW
        
        This Agreement shall be governed by the laws of the State of Texas.
        
        AGREED AND ACCEPTED:
        
        MBTQ GROUP
        
        By: _______________________
        
        {company_name or '[COMPANY NAME]'}
        
        By: {licensee_name or '________________________'}
        """
        
        return agreement
    
    def get_customer_portal_url(self, licensee_id):
        """
        Get the custom portal URL for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            str: Customer portal URL
        """
        if request and request.host:
            base = request.host
        else:
            base = "app.mbtqgroup.com"
            
        return f"https://{licensee_id}.{base}"
    
    def get_whitelabel_templates(self, licensee_id):
        """
        Get custom templates for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            dict: Template paths
        """
        templates = {
            "login": f"licensee/{licensee_id}/login.html",
            "dashboard": f"licensee/{licensee_id}/dashboard.html",
            "education": f"licensee/{licensee_id}/education/index.html"
        }
        
        # Check if custom templates exist, otherwise use defaults
        for key, path in templates.items():
            full_path = os.path.join(current_app.template_folder, path)
            if not os.path.exists(full_path):
                templates[key] = f"licensee/default/{key}.html"
                
        return templates
    
    def get_custom_modules(self, licensee_id):
        """
        Get custom education modules for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            list: Custom module IDs
        """
        # In a real implementation, this would fetch from database
        # For now, return dummy data
        return []
    
    def get_usage_analytics(self, licensee_id, start_date=None, end_date=None):
        """
        Get usage analytics for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            start_date (datetime, optional): Start date for analytics
            end_date (datetime, optional): End date for analytics
            
        Returns:
            dict: Usage analytics
        """
        # In a real implementation, this would fetch from database
        # For now, return dummy data
        analytics = {
            "active_clients": 0,
            "modules_completed": 0,
            "avg_engagement_time": 0,
            "most_popular_module": "",
            "client_satisfaction": 0
        }
        
        return analytics
    
    def generate_api_key(self, licensee_id):
        """
        Generate an API key for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            
        Returns:
            str: API key
        """
        # In a real implementation, this would generate a secure key
        # For now, return a dummy key
        import uuid
        return str(uuid.uuid4())

# Initialize a single instance to be used application-wide
white_label_service = WhiteLabelService()
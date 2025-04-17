"""
ASL Technical Support service for DEAF FIRST platform.
Provides video-based tech support with ASL interpreters for platform users.
"""

import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from flask import current_app, url_for
from simple_app import db

# Configure logging
logger = logging.getLogger(__name__)

class ASLSupportService:
    """
    Service for providing ASL-based technical support through video calls and resources.
    """
    
    def __init__(self, app_config=None):
        """Initialize ASL support service with optional configuration"""
        self.app_config = app_config or {}
        self.support_categories = {
            "general": {
                "name": "General Platform Support",
                "description": "Help with basic platform navigation and account setup",
                "icon": "question-circle",
                "video_url": None
            },
            "financial_tools": {
                "name": "Financial Tools Support",
                "description": "Assistance with tax preparation, investment, and other financial tools",
                "icon": "calculator",
                "video_url": None
            },
            "accessibility": {
                "name": "Accessibility Features",
                "description": "Help with ASL video configuration, caption settings, and accessibility options",
                "icon": "universal-access",
                "video_url": None
            },
            "reseller_support": {
                "name": "Reseller & White-Label Support",
                "description": "Assistance with white-label configuration and reseller features",
                "icon": "tags",
                "video_url": None
            },
            "api_integration": {
                "name": "API & Integration Support",
                "description": "Help with API usage and third-party integrations",
                "icon": "code",
                "video_url": None
            }
        }
        
        # Video meeting settings
        self.meeting_providers = {
            "asl_now": {
                "name": "ASL Now",
                "url_template": "https://aslnow.com/meeting/{meeting_id}",
                "api_key_env": "ASL_NOW_API_KEY",
                "available": self._check_provider_available("ASL_NOW_API_KEY")
            },
            "sign_vri": {
                "name": "SignVRI", 
                "url_template": "https://signvri.com/call/{meeting_id}",
                "api_key_env": "SIGN_VRI_API_KEY",
                "available": self._check_provider_available("SIGN_VRI_API_KEY")
            },
            "purple_vri": {
                "name": "Purple VRI",
                "url_template": "https://purplevri.com/connect/{meeting_id}",
                "api_key_env": "PURPLE_VRI_API_KEY",
                "available": self._check_provider_available("PURPLE_VRI_API_KEY")
            }
        }
        
        # Default video provider if none are available
        if not any(provider["available"] for provider in self.meeting_providers.values()):
            logger.warning("No ASL support video providers configured. Using demo mode.")
        
    def get_support_categories(self):
        """
        Get available support categories.
        
        Returns:
            dict: Support category information
        """
        return self.support_categories
    
    def get_video_providers(self):
        """
        Get available video meeting providers.
        
        Returns:
            dict: Available video providers
        """
        return {k: v for k, v in self.meeting_providers.items() if v["available"]}
    
    def create_support_session(self, user_id, category, notes=None, scheduled_time=None, provider=None):
        """
        Create a technical support session with ASL interpreter.
        
        Args:
            user_id (int): User ID
            category (str): Support category
            notes (str, optional): Additional notes
            scheduled_time (datetime, optional): Scheduled time or None for immediate
            provider (str, optional): Preferred video provider
            
        Returns:
            dict: Support session details including meeting link
        """
        # Validate category
        if category not in self.support_categories:
            raise ValueError(f"Invalid support category: {category}")
        
        # Choose provider
        if provider and provider in self.meeting_providers and self.meeting_providers[provider]["available"]:
            chosen_provider = provider
        else:
            # Choose first available provider
            available_providers = [k for k, v in self.meeting_providers.items() if v["available"]]
            if available_providers:
                chosen_provider = available_providers[0]
            else:
                logger.warning("No video providers available. Using demo mode.")
                chosen_provider = "demo"
        
        # Generate meeting ID
        meeting_id = self._generate_meeting_id()
        
        # Create session in database
        from models import User, ASLSupportSession
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"Invalid user ID: {user_id}")
        
        # Set default scheduled time if not provided
        if not scheduled_time:
            scheduled_time = datetime.utcnow() + timedelta(minutes=15)
        
        session = ASLSupportSession(
            user_id=user_id,
            category=category,
            notes=notes,
            scheduled_time=scheduled_time,
            provider=chosen_provider,
            meeting_id=meeting_id,
            status="scheduled"
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Generate meeting link
        if chosen_provider == "demo":
            meeting_link = f"/asl-support/demo/{meeting_id}"
        else:
            provider_data = self.meeting_providers[chosen_provider]
            meeting_link = provider_data["url_template"].format(meeting_id=meeting_id)
        
        # Return session details
        return {
            "session_id": session.id,
            "category": self.support_categories[category]["name"],
            "meeting_id": meeting_id,
            "meeting_link": meeting_link,
            "provider": chosen_provider,
            "scheduled_time": scheduled_time.strftime("%Y-%m-%d %H:%M"),
            "support_agent": self._get_available_agent()
        }
    
    def get_support_resources(self, category=None, white_label_id=None):
        """
        Get ASL video resources for technical support.
        
        Args:
            category (str, optional): Filter by category
            white_label_id (int, optional): White-label customization ID
            
        Returns:
            list: Support resources
        """
        # Get resources by category
        resources = []
        
        # Demo resources
        demo_resources = {
            "general": [
                {
                    "title": "Getting Started Guide",
                    "description": "Learn how to set up your account and navigate the platform",
                    "video_url": "https://example.com/videos/getting-started.mp4",
                    "thumbnail": "https://example.com/thumbnails/getting-started.jpg"
                },
                {
                    "title": "Account Settings",
                    "description": "How to manage your profile and account preferences",
                    "video_url": "https://example.com/videos/account-settings.mp4",
                    "thumbnail": "https://example.com/thumbnails/account-settings.jpg"
                }
            ],
            "financial_tools": [
                {
                    "title": "Tax Preparation Walkthrough",
                    "description": "Step-by-step guide to using the tax preparation module",
                    "video_url": "https://example.com/videos/tax-prep.mp4",
                    "thumbnail": "https://example.com/thumbnails/tax-prep.jpg"
                },
                {
                    "title": "Investment Portfolio Setup",
                    "description": "How to set up and manage your investment portfolio",
                    "video_url": "https://example.com/videos/investment.mp4",
                    "thumbnail": "https://example.com/thumbnails/investment.jpg"
                }
            ],
            "accessibility": [
                {
                    "title": "ASL Video Settings",
                    "description": "How to configure ASL video preferences",
                    "video_url": "https://example.com/videos/asl-settings.mp4",
                    "thumbnail": "https://example.com/thumbnails/asl-settings.jpg"
                },
                {
                    "title": "Caption Configuration",
                    "description": "Customizing closed captions for your needs",
                    "video_url": "https://example.com/videos/captions.mp4",
                    "thumbnail": "https://example.com/thumbnails/captions.jpg"
                }
            ],
            "reseller_support": [
                {
                    "title": "White-Label Configuration",
                    "description": "Setting up your white-label instance",
                    "video_url": "https://example.com/videos/white-label.mp4",
                    "thumbnail": "https://example.com/thumbnails/white-label.jpg"
                },
                {
                    "title": "Reseller Dashboard Tutorial",
                    "description": "Managing your reseller dashboard",
                    "video_url": "https://example.com/videos/reseller-dashboard.mp4",
                    "thumbnail": "https://example.com/thumbnails/reseller-dashboard.jpg"
                }
            ],
            "api_integration": [
                {
                    "title": "API Integration Basics",
                    "description": "Getting started with the DEAF FIRST API",
                    "video_url": "https://example.com/videos/api-basics.mp4",
                    "thumbnail": "https://example.com/thumbnails/api-basics.jpg"
                },
                {
                    "title": "Authentication & Security",
                    "description": "Secure API access and authentication",
                    "video_url": "https://example.com/videos/api-security.mp4",
                    "thumbnail": "https://example.com/thumbnails/api-security.jpg"
                }
            ]
        }
        
        # Filter by category if provided
        if category:
            if category in demo_resources:
                resources = demo_resources[category]
            else:
                return []
        else:
            # Collect all resources
            for cat_resources in demo_resources.values():
                resources.extend(cat_resources)
        
        # Apply white-label customization if provided
        if white_label_id:
            from models_licensing import Licensee
            licensee = Licensee.query.get(white_label_id)
            if licensee and licensee.branding:
                for resource in resources:
                    resource["white_label"] = {
                        "company_name": licensee.company_name,
                        "logo_url": licensee.branding.logo_path
                    }
        
        return resources
    
    def get_faq(self, category=None, white_label_id=None):
        """
        Get frequently asked questions with ASL video answers.
        
        Args:
            category (str, optional): Filter by category
            white_label_id (int, optional): White-label customization ID
            
        Returns:
            list: FAQs with videos
        """
        # Demo FAQs
        faqs = [
            {
                "question": "How do I reset my password?",
                "answer": "To reset your password, click on the 'Forgot Password' link on the login page. You will receive an email with instructions to create a new password. If you're still having trouble, contact support.",
                "category": "general",
                "video_url": "https://example.com/videos/faq/reset-password.mp4"
            },
            {
                "question": "How do I access ASL videos for financial terms?",
                "answer": "You can access ASL videos for financial terms in the Financial Education section. Click on the 'ASL Glossary' tab to browse all available term videos. You can also see ASL videos when hovering over highlighted terms throughout the platform.",
                "category": "accessibility",
                "video_url": "https://example.com/videos/faq/asl-glossary.mp4"
            },
            {
                "question": "How do I customize my white-label branding?",
                "answer": "To customize your white-label branding, go to your Reseller Dashboard and click on the Branding tab. There you can upload logos, set colors, and customize other branding elements. Changes will apply to your entire white-label instance.",
                "category": "reseller_support",
                "video_url": "https://example.com/videos/faq/custom-branding.mp4"
            },
            {
                "question": "How do I generate API keys?",
                "answer": "To generate API keys, go to your Account Settings and select the API Access tab. Click 'Generate New Key' and give it a name to identify its purpose. Make sure to store your API key securely as it won't be shown again.",
                "category": "api_integration",
                "video_url": "https://example.com/videos/faq/api-keys.mp4"
            },
            {
                "question": "How do I prepare a tax return for a client?",
                "answer": "To prepare a tax return, go to the Tax Preparation module and click 'New Return'. Select the client from your list or create a new client profile. Follow the step-by-step guide to enter all required information. You can save progress and return to it later.",
                "category": "financial_tools",
                "video_url": "https://example.com/videos/faq/tax-return.mp4"
            }
        ]
        
        # Filter by category if provided
        if category:
            faqs = [faq for faq in faqs if faq["category"] == category]
        
        # Apply white-label customization if provided
        if white_label_id:
            from models_licensing import Licensee
            licensee = Licensee.query.get(white_label_id)
            if licensee and licensee.branding:
                for faq in faqs:
                    faq["white_label"] = {
                        "company_name": licensee.company_name,
                        "logo_url": licensee.branding.logo_path
                    }
        
        return faqs
    
    def _check_provider_available(self, api_key_env):
        """Check if a provider API key is available"""
        return os.environ.get(api_key_env) is not None
    
    def _generate_meeting_id(self):
        """Generate a unique meeting ID"""
        return f"asl-{uuid.uuid4().hex[:10]}"
    
    def _get_available_agent(self):
        """Get an available support agent (demo data)"""
        # In a real implementation, this would check agent availability
        agents = [
            {"name": "Sarah Johnson", "languages": ["ASL", "English"], "avatar": "sarah.jpg"},
            {"name": "Michael Chen", "languages": ["ASL", "English", "Chinese"], "avatar": "michael.jpg"},
            {"name": "Lisa Rodriguez", "languages": ["ASL", "English", "Spanish"], "avatar": "lisa.jpg"}
        ]
        
        import random
        return random.choice(agents)

# Initialize a single instance to be used application-wide
asl_support_service = ASLSupportService()
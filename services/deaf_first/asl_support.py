"""
ASL Support Service for the DEAF FIRST platform.
Provides video-based technical support with ASL interpreters.
"""

import logging
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ASLSupportService:
    """
    Service for managing ASL support sessions and resources.
    Provides methods for scheduling and managing ASL support sessions,
    as well as accessing support resources.
    """
    
    def __init__(self):
        """Initialize the ASL support service"""
        self.meeting_providers = {
            "asl_now": {
                "name": "ASL Now",
                "url_template": "https://aslnow.com/meeting/{meeting_id}",
                "max_duration": 60,  # minutes
                "available": False
            },
            "sign_vri": {
                "name": "SignVRI",
                "url_template": "https://signvri.com/call/{meeting_id}",
                "max_duration": 45,  # minutes
                "available": False
            },
            "purple_vri": {
                "name": "Purple VRI",
                "url_template": "https://purplevri.com/connect/{meeting_id}",
                "max_duration": 30,  # minutes
                "available": False
            },
            "demo": {
                "name": "Demo Provider",
                "url_template": "/asl-support/demo-meeting/{meeting_id}",
                "max_duration": 60,  # minutes
                "available": True
            }
        }
        
        # Support categories
        self.support_categories = {
            "general": {
                "name": "General Support",
                "description": "General platform usage and account questions",
                "icon": "question-circle",
                "providers": ["asl_now", "sign_vri", "purple_vri", "demo"]
            },
            "financial_tools": {
                "name": "Financial Tools",
                "description": "Help with financial calculators and tools",
                "icon": "calculator",
                "providers": ["asl_now", "sign_vri", "demo"]
            },
            "accessibility": {
                "name": "Accessibility",
                "description": "Support for accessibility features and settings",
                "icon": "eye",
                "providers": ["asl_now", "sign_vri", "purple_vri", "demo"]
            },
            "personal_insurance": {
                "name": "Personal Insurance",
                "description": "Support for personal insurance features",
                "icon": "shield-check",
                "providers": ["asl_now", "demo"]
            },
            "business_insurance": {
                "name": "Business Insurance",
                "description": "Support for business insurance features",
                "icon": "building",
                "providers": ["asl_now", "demo"]
            },
            "technical": {
                "name": "Technical Support",
                "description": "Technical issues and troubleshooting",
                "icon": "tools",
                "providers": ["asl_now", "sign_vri", "demo"]
            }
        }
    
    def get_support_categories(self):
        """
        Get all support categories.
        
        Returns:
            dict: Dictionary of support categories
        """
        return self.support_categories
    
    def get_video_providers(self):
        """
        Get available video providers for ASL support.
        
        Returns:
            dict: Dictionary of available providers
        """
        return {k: v for k, v in self.meeting_providers.items() if v["available"]}
    
    def create_support_session(self, user_id, category, scheduled_time, provider="demo", notes=None):
        """
        Create a new ASL support session.
        
        Args:
            user_id (int): User ID requesting the session
            category (str): Support category
            scheduled_time (datetime): When the session is scheduled
            provider (str, optional): Video provider. Defaults to "demo".
            notes (str, optional): Notes about the session. Defaults to None.
            
        Returns:
            dict: Session details
        """
        from models_asl_support import ASLSupportSession
        from simple_app import db
        
        # Generate meeting ID
        meeting_id = f"{category}-{uuid.uuid4()}"
        
        # Create session in database
        session = ASLSupportSession(
            user_id=user_id,
            category=category,
            notes=notes,
            scheduled_time=scheduled_time,
            provider=provider,
            meeting_id=meeting_id,
            status="scheduled",
            duration_minutes=self.meeting_providers.get(provider, {}).get("max_duration", 30)
        )
        
        db.session.add(session)
        db.session.commit()
        
        logger.info(f"Created ASL support session {session.id} for user {user_id}")
        
        return {
            "session_id": session.id,
            "meeting_id": meeting_id,
            "provider": provider,
            "scheduled_time": scheduled_time.isoformat(),
            "category": category
        }
    
    def get_support_resources(self, category=None, white_label_id=None):
        """
        Get support resources.
        
        Args:
            category (str, optional): Filter by category. Defaults to None.
            white_label_id (int, optional): Filter by white-label. Defaults to None.
            
        Returns:
            list: List of support resources
        """
        from models_asl_support import ASLSupportResource
        
        query = ASLSupportResource.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if white_label_id:
            query = query.filter(
                (ASLSupportResource.licensee_id == white_label_id) | 
                (ASLSupportResource.is_white_labeled == False)
            )
        
        resources = query.order_by(ASLSupportResource.created_at.desc()).all()
        
        return resources
    
    def get_faq(self, category=None, white_label_id=None):
        """
        Get frequently asked questions.
        
        Args:
            category (str, optional): Filter by category. Defaults to None.
            white_label_id (int, optional): Filter by white-label. Defaults to None.
            
        Returns:
            list: List of FAQs
        """
        from models_asl_support import ASLSupportFAQ
        
        query = ASLSupportFAQ.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if white_label_id:
            query = query.filter(
                (ASLSupportFAQ.licensee_id == white_label_id) | 
                (ASLSupportFAQ.is_white_labeled == False)
            )
        
        faqs = query.order_by(ASLSupportFAQ.sort_order, ASLSupportFAQ.created_at.desc()).all()
        
        return faqs

# Initialize a single instance to be used application-wide
asl_support_service = ASLSupportService()
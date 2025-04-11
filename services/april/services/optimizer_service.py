import logging
from typing import Dict, Any
from datetime import datetime

from services.april.api_client import AprilAPIClient

logger = logging.getLogger(__name__)

class OptimizerService:
    """Service for product engagement tracking using April's Optimizer"""
    
    def __init__(self):
        """Initialize the optimizer service"""
        self.april_client = AprilAPIClient()
        logger.info("Optimizer service initialized")
    
    def track_user_engagement(self, user_id: int, product_id: str, engagement_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track user engagement with financial products
        
        Args:
            user_id: User identifier
            product_id: Product identifier (e.g., 'tax_filing', 'financial_profile')
            engagement_data: Data about the engagement
            
        Returns:
            API response
        """
        try:
            # Add timestamp if not provided
            if 'timestamp' not in engagement_data:
                engagement_data['timestamp'] = datetime.utcnow().isoformat()
                
            response = self.april_client.track_product_engagement(
                user_id=user_id,
                product_id=product_id,
                data=engagement_data
            )
            
            logger.info(f"Tracked engagement for user {user_id} with product {product_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to track engagement: {str(e)}")
            raise
    
    def track_page_view(self, user_id: int, page: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Track a page view as user engagement
        
        Args:
            user_id: User identifier
            page: Page identifier
            additional_data: Additional tracking data
            
        Returns:
            API response
        """
        engagement_data = additional_data or {}
        engagement_data.update({
            'action': 'page_view',
            'page': page
        })
        
        return self.track_user_engagement(
            user_id=user_id,
            product_id='page_engagement',
            engagement_data=engagement_data
        )
    
    def track_financial_action(self, user_id: int, action: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track a financial action as user engagement
        
        Args:
            user_id: User identifier
            action: Action identifier (e.g., 'tax_submission', 'profile_creation')
            financial_data: Financial data related to the action
            
        Returns:
            API response
        """
        engagement_data = {
            'action': action,
            'financial_data': financial_data
        }
        
        return self.track_user_engagement(
            user_id=user_id,
            product_id='financial_actions',
            engagement_data=engagement_data
        )
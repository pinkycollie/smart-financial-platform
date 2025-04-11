import logging
from typing import Dict, Any, List, Optional
from app import db
from app.services.april.api_client import AprilAPIClient
from app.services.april.models import FinancialProfile, FinancialRecommendation
from app.services.accessibility.mux_client import MuxClient

logger = logging.getLogger(__name__)

class EstimatorService:
    """Service for working with April's 'The Estimator' financial profile functionality"""
    
    def __init__(self):
        self.api_client = AprilAPIClient()
        self.mux_client = MuxClient()
    
    def create_financial_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a financial profile in April
        
        Args:
            user_id: User identifier
            profile_data: Financial profile data
        
        Returns:
            Dictionary with created profile details
        """
        try:
            # Call April API
            response = self.api_client.create_financial_profile(user_id, profile_data)
            
            # Create profile in database
            profile = FinancialProfile(
                user_id=user_id,
                annual_income=profile_data.get('annual_income', 0),
                filing_status=profile_data.get('filing_status', ''),
                dependents=profile_data.get('dependents', 0),
                investments=profile_data.get('investments', {}),
                retirement_accounts=profile_data.get('retirement_accounts', {}),
                external_id=response.get('profile_id')
            )
            
            db.session.add(profile)
            db.session.commit()
            
            return {
                'success': True,
                'profile_id': profile.id,
                'external_id': profile.external_id,
                'asl_video_id': self._get_asl_instruction_video('profile_created')
            }
            
        except Exception as e:
            logger.error(f"Error creating financial profile: {str(e)}")
            db.session.rollback()
            
            return {
                'success': False,
                'error': str(e),
                'asl_video_id': self._get_asl_instruction_video('profile_error')
            }
    
    def get_financial_recommendations(self, user_id: int, profile_id: int) -> Dict[str, Any]:
        """
        Get financial recommendations for a profile
        
        Args:
            user_id: User identifier
            profile_id: Financial profile identifier
        
        Returns:
            Dictionary with recommendations
        """
        try:
            # Get profile from database
            profile = FinancialProfile.query.filter_by(
                id=profile_id,
                user_id=user_id
            ).first()
            
            if not profile:
                return {
                    'success': False,
                    'error': 'Profile not found',
                    'asl_video_id': self._get_asl_instruction_video('profile_not_found')
                }
            
            # Call April API
            response = self.api_client.get_financial_recommendations(user_id, profile.external_id)
            
            # Save recommendations to database
            recommendations = []
            for rec_data in response.get('recommendations', []):
                # Get or create ASL video for this recommendation
                asl_video_id = self._get_recommendation_asl_video(rec_data.get('recommendation_type'))
                
                recommendation = FinancialRecommendation(
                    financial_profile_id=profile.id,
                    recommendation_type=rec_data.get('recommendation_type', ''),
                    title=rec_data.get('title', ''),
                    description=rec_data.get('description', ''),
                    potential_impact=rec_data.get('potential_impact', 0.0),
                    asl_video_id=asl_video_id
                )
                
                db.session.add(recommendation)
                recommendations.append(recommendation)
            
            db.session.commit()
            
            return {
                'success': True,
                'profile_id': profile_id,
                'recommendations': [
                    {
                        'id': rec.id,
                        'type': rec.recommendation_type,
                        'title': rec.title,
                        'description': rec.description,
                        'potential_impact': rec.potential_impact,
                        'asl_video_id': rec.asl_video_id
                    } for rec in recommendations
                ],
                'asl_video_id': self._get_asl_instruction_video('recommendations_available')
            }
            
        except Exception as e:
            logger.error(f"Error getting financial recommendations: {str(e)}")
            db.session.rollback()
            
            return {
                'success': False,
                'error': str(e),
                'asl_video_id': self._get_asl_instruction_video('recommendations_error')
            }
    
    def get_profile(self, user_id: int, profile_id: int) -> Optional[FinancialProfile]:
        """
        Get a financial profile from the database
        
        Args:
            user_id: User identifier
            profile_id: Financial profile identifier
        
        Returns:
            FinancialProfile object or None if not found
        """
        return FinancialProfile.query.filter_by(
            id=profile_id,
            user_id=user_id
        ).first()
    
    def _get_asl_instruction_video(self, context: str) -> Optional[str]:
        """
        Get the appropriate ASL instruction video ID for the given context
        
        Args:
            context: The context for the instruction video
        
        Returns:
            Mux video ID or None if not found
        """
        # Map contexts to video IDs
        video_map = {
            'profile_created': 'financial_profile_created',
            'profile_error': 'financial_profile_error',
            'profile_not_found': 'record_not_found',
            'recommendations_available': 'financial_recommendations',
            'recommendations_error': 'system_error'
        }
        
        # Get the predefined video ID or use a default
        video_key = video_map.get(context, 'general_instructions')
        
        try:
            # This would normally query the Mux API for the video ID
            # For now, we'll return a placeholder
            return f"mux_video_{video_key}"
        except Exception as e:
            logger.error(f"Error getting ASL instruction video: {str(e)}")
            return None
    
    def _get_recommendation_asl_video(self, recommendation_type: str) -> Optional[str]:
        """
        Get an ASL video ID for a specific recommendation type
        
        Args:
            recommendation_type: Type of financial recommendation
        
        Returns:
            Mux video ID or None if not found
        """
        # Map recommendation types to video keys
        video_map = {
            'retirement': 'retirement_planning',
            'tax_saving': 'tax_savings_strategies',
            'investment': 'investment_recommendations',
            'debt': 'debt_management',
            'emergency_fund': 'emergency_fund',
            'insurance': 'insurance_coverage'
        }
        
        # Get the predefined video ID or use a default
        video_key = video_map.get(recommendation_type, 'general_recommendation')
        
        try:
            # This would normally query the Mux API for the video ID
            # For now, we'll return a placeholder
            return f"mux_video_{video_key}"
        except Exception as e:
            logger.error(f"Error getting recommendation ASL video: {str(e)}")
            return None

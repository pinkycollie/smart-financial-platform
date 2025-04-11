import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import FinancialProfile, FinancialRecommendation, User
from simple_app import db
from services.april.api_client import AprilAPIClient

logger = logging.getLogger(__name__)

class EstimatorService:
    """Service for financial profile management using April's Estimator"""
    
    def __init__(self):
        """Initialize the estimator service"""
        self.april_client = AprilAPIClient()
        logger.info("Estimator service initialized")
    
    def create_financial_profile(self, user_id: int, profile_data: Dict[str, Any]) -> FinancialProfile:
        """
        Create a financial profile using April's Estimator service
        
        Args:
            user_id: User identifier
            profile_data: Financial profile data
            
        Returns:
            Created FinancialProfile instance
        """
        # Prepare investments and retirement accounts data
        investments = {
            'stocks': profile_data.get('stocks', 0),
            'bonds': profile_data.get('bonds', 0),
            'real_estate': profile_data.get('real_estate', 0)
        }
        
        retirement_accounts = {
            '401k': profile_data.get('retirement_401k', 0),
            'ira': profile_data.get('retirement_ira', 0)
        }
        
        # Create local record
        financial_profile = FinancialProfile(
            user_id=user_id,
            annual_income=profile_data.get('annual_income'),
            filing_status=profile_data.get('filing_status'),
            dependents=profile_data.get('dependents', 0),
            investments=investments,
            retirement_accounts=retirement_accounts
        )
        
        try:
            # Add to database
            db.session.add(financial_profile)
            db.session.commit()
            
            # Submit to April API
            april_profile_data = {
                'annual_income': profile_data.get('annual_income'),
                'filing_status': profile_data.get('filing_status'),
                'dependents': profile_data.get('dependents', 0),
                'investments': investments,
                'retirement_accounts': retirement_accounts
            }
            
            response = self.april_client.create_financial_profile(
                user_id=user_id,
                profile_data=april_profile_data
            )
            
            # Update local record with external ID
            financial_profile.external_id = response.get('profile_id')
            db.session.commit()
            
            # Get and store recommendations
            self.update_recommendations(financial_profile.id)
            
            logger.info(f"Successfully created financial profile for user {user_id}")
            return financial_profile
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create financial profile: {str(e)}")
            raise
    
    def get_user_financial_profiles(self, user_id: int) -> List[FinancialProfile]:
        """
        Get all financial profiles for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of FinancialProfile instances
        """
        return FinancialProfile.query.filter_by(user_id=user_id).order_by(FinancialProfile.created_at.desc()).all()
    
    def get_financial_profile(self, profile_id: int) -> FinancialProfile:
        """
        Get a specific financial profile
        
        Args:
            profile_id: Financial profile identifier
            
        Returns:
            FinancialProfile instance
        """
        return FinancialProfile.query.get_or_404(profile_id)
    
    def update_recommendations(self, profile_id: int) -> List[FinancialRecommendation]:
        """
        Update recommendations for a financial profile from April's API
        
        Args:
            profile_id: Financial profile identifier
            
        Returns:
            List of updated FinancialRecommendation instances
        """
        profile = self.get_financial_profile(profile_id)
        
        if not profile.external_id:
            logger.warning(f"Cannot update recommendations for profile {profile_id}: No external ID")
            return []
            
        try:
            # Get recommendations from April API
            response = self.april_client.get_financial_recommendations(
                user_id=profile.user_id,
                profile_id=profile.external_id
            )
            
            # Delete existing recommendations
            FinancialRecommendation.query.filter_by(financial_profile_id=profile_id).delete()
            
            # Create new recommendations
            recommendations = []
            for rec_data in response.get('recommendations', []):
                recommendation = FinancialRecommendation(
                    financial_profile_id=profile_id,
                    recommendation_type=rec_data.get('type'),
                    title=rec_data.get('title'),
                    description=rec_data.get('description'),
                    potential_impact=rec_data.get('potential_impact'),
                    asl_video_id=rec_data.get('asl_video_id')
                )
                
                db.session.add(recommendation)
                recommendations.append(recommendation)
            
            db.session.commit()
            logger.info(f"Updated {len(recommendations)} recommendations for profile {profile_id}")
            
            return recommendations
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update recommendations: {str(e)}")
            return []
"""
SignASL integration client for the DEAF FIRST platform.
Provides access to SignASL video content for ASL financial terms.
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class SignASLClient:
    """
    Client for SignASL API.
    Used for ASL financial term videos.
    """
    
    def __init__(self, api_key=None):
        """Initialize SignASL client with API credentials"""
        self.api_key = api_key or os.environ.get('VSL_LABS_API_KEY')
        self.api_url = "https://api.signasl.org/v1"  # Example URL, replace with actual
        
        if not self.api_key:
            logger.warning("SignASL API key not configured. Using demo mode.")
            self.demo_mode = True
        else:
            self.demo_mode = False
            
        # Initialize demo data for fallback
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize demo data for when API is not available"""
        self.demo_videos = {
            "sa_tax_deduction": {
                "id": "sa_tax_deduction",
                "title": "Tax Deduction",
                "description": "A tax deduction reduces the amount of income that is subject to taxation.",
                "duration": 15.5,
                "thumbnail_url": "https://example.com/thumbnails/tax_deduction.jpg",
                "video_url": "https://example.com/videos/tax_deduction.mp4"
            },
            "sa_investment": {
                "id": "sa_investment",
                "title": "Investment",
                "description": "Allocating resources with the expectation of generating income or profit over time.",
                "duration": 12.8,
                "thumbnail_url": "https://example.com/thumbnails/investment.jpg",
                "video_url": "https://example.com/videos/investment.mp4"
            },
            "sa_dividend": {
                "id": "sa_dividend",
                "title": "Dividend",
                "description": "A distribution of a company's earnings to shareholders.",
                "duration": 14.2,
                "thumbnail_url": "https://example.com/thumbnails/dividend.jpg",
                "video_url": "https://example.com/videos/dividend.mp4"
            },
            "sa_portfolio": {
                "id": "sa_portfolio",
                "title": "Portfolio",
                "description": "A collection of financial investments like stocks, bonds, commodities, cash, and cash equivalents.",
                "duration": 18.7,
                "thumbnail_url": "https://example.com/thumbnails/portfolio.jpg",
                "video_url": "https://example.com/videos/portfolio.mp4"
            },
            "sa_insurance_premium": {
                "id": "sa_insurance_premium",
                "title": "Insurance Premium",
                "description": "The amount paid for an insurance policy, typically in monthly installments.",
                "duration": 16.3,
                "thumbnail_url": "https://example.com/thumbnails/insurance_premium.jpg",
                "video_url": "https://example.com/videos/insurance_premium.mp4"
            },
            "sa_mortgage": {
                "id": "sa_mortgage",
                "title": "Mortgage",
                "description": "A loan used to purchase a home or property, with the property serving as collateral.",
                "duration": 19.5,
                "thumbnail_url": "https://example.com/thumbnails/mortgage.jpg",
                "video_url": "https://example.com/videos/mortgage.mp4"
            },
            "sa_capital_gain": {
                "id": "sa_capital_gain",
                "title": "Capital Gain",
                "description": "The profit earned when an investment is sold for more than its purchase price.",
                "duration": 17.2,
                "thumbnail_url": "https://example.com/thumbnails/capital_gain.jpg",
                "video_url": "https://example.com/videos/capital_gain.mp4"
            },
            "sa_diversification": {
                "id": "sa_diversification",
                "title": "Diversification",
                "description": "The strategy of allocating investments across various financial instruments to reduce risk.",
                "duration": 20.1,
                "thumbnail_url": "https://example.com/thumbnails/diversification.jpg",
                "video_url": "https://example.com/videos/diversification.mp4"
            },
            "sa_401k": {
                "id": "sa_401k",
                "title": "401(k)",
                "description": "A retirement savings plan sponsored by an employer.",
                "duration": 13.8,
                "thumbnail_url": "https://example.com/thumbnails/401k.jpg",
                "video_url": "https://example.com/videos/401k.mp4"
            },
            "sa_ira": {
                "id": "sa_ira",
                "title": "IRA",
                "description": "Individual Retirement Account - a tax-advantaged investment account for retirement savings.",
                "duration": 14.5,
                "thumbnail_url": "https://example.com/thumbnails/ira.jpg",
                "video_url": "https://example.com/videos/ira.mp4"
            }
        }
        
        self.demo_categories = {
            "taxes": ["sa_tax_deduction", "sa_capital_gain"],
            "investments": ["sa_investment", "sa_dividend", "sa_portfolio", "sa_diversification"],
            "insurance": ["sa_insurance_premium"],
            "real_estate": ["sa_mortgage"],
            "retirement": ["sa_401k", "sa_ira"]
        }
    
    def get_video_url(self, video_id: str) -> Optional[str]:
        """
        Get the URL for a video by ID.
        
        Args:
            video_id: Video ID in SignASL
            
        Returns:
            Video URL or None if not found
        """
        if self.demo_mode:
            video = self.demo_videos.get(video_id)
            return video["video_url"] if video else None
        
        try:
            endpoint = f"/videos/{video_id}"
            response = self._make_request("GET", endpoint)
            
            if response and "video_url" in response:
                return response["video_url"]
                
            return None
        except Exception as e:
            logger.error(f"Error getting video URL: {e}")
            return None
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """
        Get metadata for a video.
        
        Args:
            video_id: Video ID in SignASL
            
        Returns:
            Video metadata
        """
        if self.demo_mode:
            return self.demo_videos.get(video_id, {})
        
        try:
            endpoint = f"/videos/{video_id}"
            return self._make_request("GET", endpoint) or {}
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
            return {}
    
    def search_videos(self, query: str, limit: int = 10, category: str = None) -> List[Dict[str, Any]]:
        """
        Search for videos by query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            category: Optional category filter
            
        Returns:
            List of video metadata
        """
        if self.demo_mode:
            results = []
            query = query.lower()
            
            # Filter by category if provided
            video_ids = []
            if category and category in self.demo_categories:
                video_ids = self.demo_categories[category]
            else:
                # Use all videos if no category filter
                video_ids = list(self.demo_videos.keys())
            
            # Filter by query
            for video_id in video_ids:
                video = self.demo_videos[video_id]
                if (
                    query in video["title"].lower() or
                    query in video["description"].lower()
                ):
                    results.append(video)
                    if len(results) >= limit:
                        break
            
            return results
        
        try:
            params = {
                "q": query,
                "limit": limit
            }
            
            if category:
                params["category"] = category
            
            endpoint = "/search"
            response = self._make_request("GET", endpoint, params)
            
            if response and "results" in response:
                return response["results"]
                
            return []
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
    
    def get_financial_terms(self, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get financial terms with ASL videos.
        
        Args:
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of financial terms with videos
        """
        if self.demo_mode:
            results = []
            
            # Filter by category if provided
            video_ids = []
            if category and category in self.demo_categories:
                video_ids = self.demo_categories[category]
            else:
                # Use all videos if no category filter
                video_ids = list(self.demo_videos.keys())
            
            # Limit results
            for video_id in video_ids[:limit]:
                results.append(self.demo_videos[video_id])
            
            return results
        
        try:
            params = {
                "limit": limit
            }
            
            if category:
                params["category"] = category
            
            endpoint = "/financial-terms"
            response = self._make_request("GET", endpoint, params)
            
            if response and "terms" in response:
                return response["terms"]
                
            return []
        except Exception as e:
            logger.error(f"Error getting financial terms: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get available video categories.
        
        Returns:
            List of categories
        """
        if self.demo_mode:
            return [
                {"id": "taxes", "name": "Taxes", "video_count": len(self.demo_categories["taxes"])},
                {"id": "investments", "name": "Investments", "video_count": len(self.demo_categories["investments"])},
                {"id": "insurance", "name": "Insurance", "video_count": len(self.demo_categories["insurance"])},
                {"id": "real_estate", "name": "Real Estate", "video_count": len(self.demo_categories["real_estate"])},
                {"id": "retirement", "name": "Retirement", "video_count": len(self.demo_categories["retirement"])}
            ]
        
        try:
            endpoint = "/categories"
            response = self._make_request("GET", endpoint)
            
            if response and "categories" in response:
                return response["categories"]
                
            return []
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_white_label_video_url(self, video_id: str, white_label_id: int) -> Optional[str]:
        """
        Get white-labeled video URL for a licensee.
        
        Args:
            video_id: Video ID in SignASL
            white_label_id: Licensee ID for white-label
            
        Returns:
            White-labeled video URL or regular URL if white-labeling not available
        """
        if self.demo_mode:
            # In demo mode, we just return the regular video URL
            return self.get_video_url(video_id)
        
        try:
            # Get licensee info
            from models_reseller import Licensee
            licensee = Licensee.query.get(white_label_id)
            if not licensee:
                return self.get_video_url(video_id)
            
            # Add white-label parameters to request
            params = {
                "white_label_id": white_label_id,
                "company_name": licensee.company_name
            }
            
            if licensee.branding:
                params["primary_color"] = licensee.branding.primary_color
                params["logo_url"] = licensee.branding.logo_path
            
            endpoint = f"/videos/{video_id}/white-label"
            response = self._make_request("GET", endpoint, params)
            
            if response and "video_url" in response:
                return response["video_url"]
                
            # Fallback to regular URL if white-label not available
            return self.get_video_url(video_id)
        except Exception as e:
            logger.error(f"Error getting white-label video URL: {e}")
            return self.get_video_url(video_id)
    
    def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Make a request to the SignASL API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Response data or None if failed
        """
        if self.demo_mode:
            return None
        
        url = f"{self.api_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to SignASL API: {e}")
            return None

# Initialize a global client instance
signasl_client = SignASLClient()
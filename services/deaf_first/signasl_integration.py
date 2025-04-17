import os
import logging
import requests
from urllib.parse import urljoin

# Set up logging
logger = logging.getLogger(__name__)

class SignASLClient:
    """Client for interacting with SignASL API for ASL video content"""
    
    def __init__(self):
        """Initialize SignASL client with API credentials"""
        self.api_key = os.environ.get('VSL_LABS_API_KEY')
        self.base_url = "https://api.signasl.org/v1/"  # Placeholder URL
        
        # Basic validation of configuration
        if not self.api_key:
            logger.warning("SignASL API key not configured. Using demo mode.")
            self.demo_mode = True
        else:
            self.demo_mode = False
            
        # Test the API connection
        if not self.demo_mode:
            try:
                self._test_connection()
                self.api_available = True
                logger.info("SignASL integration service initialized")
            except Exception as e:
                logger.error(f"Failed to connect to SignASL API: {e}")
                self.api_available = False
                self.demo_mode = True
        else:
            self.api_available = False
    
    def _test_connection(self):
        """Test connection to the SignASL API"""
        response = requests.get(
            urljoin(self.base_url, "status"),
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def _get_headers(self):
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def search_asl_videos(self, term, limit=10):
        """
        Search ASL videos by term
        
        Args:
            term (str): Search term
            limit (int, optional): Maximum number of results. Defaults to 10.
            
        Returns:
            list: List of matching videos with their metadata
        """
        if self.demo_mode:
            return self._get_demo_results(term, limit)
            
        try:
            response = requests.get(
                urljoin(self.base_url, "search"),
                headers=self._get_headers(),
                params={"q": term, "limit": limit}
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Error searching ASL videos: {e}")
            return self._get_demo_results(term, limit)
    
    def get_asl_video(self, video_id):
        """
        Get details for a specific ASL video
        
        Args:
            video_id (str): The video ID
            
        Returns:
            dict: Video details if found, None otherwise
        """
        if self.demo_mode:
            return self._get_demo_video(video_id)
            
        try:
            response = requests.get(
                urljoin(self.base_url, f"videos/{video_id}"),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting ASL video details: {e}")
            return self._get_demo_video(video_id)
    
    def get_finance_terms(self, category="basic", limit=20):
        """
        Get ASL videos for common financial terms
        
        Args:
            category (str, optional): Finance category. Defaults to "basic".
            limit (int, optional): Maximum number of results. Defaults to 20.
            
        Returns:
            list: List of financial term videos
        """
        if self.demo_mode:
            return self._get_demo_finance_terms(category, limit)
            
        try:
            response = requests.get(
                urljoin(self.base_url, "finance/terms"),
                headers=self._get_headers(),
                params={"category": category, "limit": limit}
            )
            response.raise_for_status()
            return response.json().get("terms", [])
        except Exception as e:
            logger.error(f"Error getting finance terms: {e}")
            return self._get_demo_finance_terms(category, limit)
    
    def _get_demo_results(self, term, limit):
        """Get placeholder results for demo mode"""
        common_financial_terms = [
            "budget", "saving", "investing", "credit", "debt",
            "mortgage", "loan", "interest", "tax", "insurance",
            "retirement", "income", "expense", "asset", "liability"
        ]
        
        results = []
        term_lower = term.lower()
        
        for t in common_financial_terms:
            if term_lower in t or not term:
                if len(results) >= limit:
                    break
                    
                results.append({
                    "id": f"demo-{t}",
                    "term": t,
                    "description": f"ASL sign for the financial term '{t}'",
                    "thumbnail_url": f"https://placeholder.com/300x200?text={t}",
                    "video_url": "https://deaf-first-demo.mux.com/placeholder.mp4",
                    "duration": 8.5,
                    "difficulty": "beginner"
                })
                
        return results
    
    def _get_demo_video(self, video_id):
        """Get placeholder video for demo mode"""
        # Extract term from demo video ID
        if video_id.startswith("demo-"):
            term = video_id[5:]
        else:
            term = "finance"
            
        return {
            "id": video_id,
            "term": term,
            "description": f"ASL sign for the financial term '{term}'",
            "thumbnail_url": f"https://placeholder.com/300x200?text={term}",
            "video_url": "https://deaf-first-demo.mux.com/placeholder.mp4",
            "duration": 8.5,
            "difficulty": "beginner",
            "related_terms": ["budget", "saving", "investing"],
            "transcript": f"This is the ASL sign for {term}."
        }
    
    def _get_demo_finance_terms(self, category, limit):
        """Get placeholder finance terms for demo mode"""
        categories = {
            "basic": [
                "budget", "saving", "investing", "credit", "debt",
                "mortgage", "loan", "interest", "tax", "insurance"
            ],
            "advanced": [
                "diversification", "liquidity", "capital gain", "compound interest",
                "portfolio", "equity", "bond", "mutual fund", "inflation", "depreciation"
            ],
            "insurance": [
                "premium", "deductible", "claim", "coverage", "policy",
                "beneficiary", "liability", "term life", "whole life", "underwriting"
            ],
            "retirement": [
                "401k", "IRA", "Roth IRA", "pension", "annuity",
                "social security", "withdrawal", "distribution", "vesting", "rollover"
            ]
        }
        
        selected_terms = categories.get(category, categories["basic"])
        results = []
        
        for i, term in enumerate(selected_terms):
            if i >= limit:
                break
                
            results.append({
                "id": f"demo-{term.replace(' ', '-')}",
                "term": term,
                "category": category,
                "description": f"ASL sign for the financial term '{term}'",
                "thumbnail_url": f"https://placeholder.com/300x200?text={term}",
                "video_url": "https://deaf-first-demo.mux.com/placeholder.mp4",
                "duration": 8.5,
                "difficulty": "beginner" if category == "basic" else "intermediate"
            })
            
        return results
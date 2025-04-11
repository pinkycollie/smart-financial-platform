import os
import logging
from typing import Dict, Any, Optional, List
import requests
import json
import mux_python
from mux_python import AssetsApi, PlaybackIDApi, ApiException

logger = logging.getLogger(__name__)

class MuxClient:
    """Client for interacting with the Mux Video API for ASL content"""
    
    def __init__(self):
        # Retrieve Mux credentials from environment
        self.token_id = os.environ.get("MUX_TOKEN_ID", "")
        self.token_secret = os.environ.get("MUX_TOKEN_SECRET", "")
        
        # Initialize Mux SDK if credentials are available
        try:
            configuration = mux_python.Configuration()
            configuration.username = self.token_id
            configuration.password = self.token_secret
            
            # Initialize API clients
            self.assets_api = AssetsApi(mux_python.ApiClient(configuration))
            self.playback_api = PlaybackIDApi(mux_python.ApiClient(configuration))
            
            # The SpacesApi is not directly available in this version
            # We'll implement spaces functionality using direct HTTP requests
            self.api_client = mux_python.ApiClient(configuration)
            
            logger.info("Mux client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mux client: {str(e)}")
            # Initialize to None so we can handle the error gracefully
            self.assets_api = None
            self.playback_api = None
            self.api_client = None
    
    def get_asl_video(self, video_key: str) -> Optional[Dict[str, Any]]:
        """
        Get an ASL video by its key identifier
        
        Args:
            video_key: Key identifier for the ASL video
        
        Returns:
            Dictionary with video details or None if not found
        """
        if not self.api_client:
            logger.error("Mux client not properly initialized")
            return None
        
        try:
            # For development purposes, we'll return mock videos
            # based on the requested key
            mock_videos = {
                'tax_filing_overview': {
                    'asset_id': 'tax_filing_overview',
                    'playback_id': 'mock_playback_id_1',
                    'duration': 120.5,
                    'status': 'ready',
                    'created_at': '2025-04-10T00:00:00Z',
                    'playback_url': 'https://stream.mux.com/mock_playback_id_1.m3u8'
                },
                'financial_profile_overview': {
                    'asset_id': 'financial_profile_overview',
                    'playback_id': 'mock_playback_id_2', 
                    'duration': 90.0,
                    'status': 'ready',
                    'created_at': '2025-04-10T00:00:00Z',
                    'playback_url': 'https://stream.mux.com/mock_playback_id_2.m3u8'
                },
                'dashboard_overview': {
                    'asset_id': 'dashboard_overview',
                    'playback_id': 'mock_playback_id_3',
                    'duration': 60.0,
                    'status': 'ready',
                    'created_at': '2025-04-10T00:00:00Z',
                    'playback_url': 'https://stream.mux.com/mock_playback_id_3.m3u8'
                }
            }
            
            if video_key in mock_videos:
                return mock_videos[video_key]
            
            logger.warning(f"ASL video with key {video_key} not found")
            return self.get_fallback_video()
            
        except Exception as e:
            logger.error(f"Error getting ASL video: {str(e)}")
            return self.get_fallback_video()
    
    def get_asl_videos_for_context(self, context: str) -> List[Dict[str, Any]]:
        """
        Get all ASL videos for a specific context
        
        Args:
            context: The context for which to retrieve videos
        
        Returns:
            List of dictionaries with video details
        """
        if not self.api_client:
            logger.error("Mux client not properly initialized")
            return []
        
        try:
            # For development purposes, we'll return mock videos
            # based on the requested context
            mock_context_videos = {
                'tax_filing': [
                    {
                        'asset_id': 'tax_filing_1',
                        'playback_id': 'mock_tax_1',
                        'title': 'How to File Your Taxes',
                        'description': 'A comprehensive guide to filing your taxes correctly.',
                        'duration': 180.0,
                        'status': 'ready',
                        'created_at': '2025-04-10T00:00:00Z',
                        'playback_url': 'https://stream.mux.com/mock_tax_1.m3u8'
                    },
                    {
                        'asset_id': 'tax_filing_2',
                        'playback_id': 'mock_tax_2',
                        'title': 'Understanding Tax Deductions',
                        'description': 'Learn about various tax deductions available to you.',
                        'duration': 120.0,
                        'status': 'ready',
                        'created_at': '2025-04-10T00:00:00Z',
                        'playback_url': 'https://stream.mux.com/mock_tax_2.m3u8'
                    }
                ],
                'financial_profile': [
                    {
                        'asset_id': 'financial_profile_1',
                        'playback_id': 'mock_fin_1',
                        'title': 'Creating Your Financial Profile',
                        'description': 'Steps to create a comprehensive financial profile.',
                        'duration': 150.0,
                        'status': 'ready',
                        'created_at': '2025-04-10T00:00:00Z',
                        'playback_url': 'https://stream.mux.com/mock_fin_1.m3u8'
                    }
                ],
                'accessibility_settings': [
                    {
                        'asset_id': 'accessibility_1',
                        'playback_id': 'mock_access_1',
                        'title': 'Customizing Your Accessibility Settings',
                        'description': 'How to customize ASL video settings for a better experience.',
                        'duration': 90.0,
                        'status': 'ready',
                        'created_at': '2025-04-10T00:00:00Z',
                        'playback_url': 'https://stream.mux.com/mock_access_1.m3u8'
                    }
                ]
            }
            
            return mock_context_videos.get(context, [])
            
        except Exception as e:
            logger.error(f"Error getting ASL videos for context: {str(e)}")
            return []

    def get_fallback_video(self) -> Dict[str, Any]:
        """
        Get a fallback ASL video when the requested one is not available
        
        Returns:
            Dictionary with fallback video details
        """
        # Return a predefined fallback video
        return {
            'asset_id': 'fallback',
            'playback_id': 'fallback',
            'title': 'Information Unavailable',
            'description': 'The requested ASL content is not available.',
            'playback_url': 'https://stream.mux.com/fallback.m3u8'
        }
    
    def create_video_space(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Create a new Mux Space for live ASL interpretation
        
        Args:
            title: Title for the space
        
        Returns:
            Dictionary with space details or None if creation failed
        """
        if not self.api_client:
            logger.error("Mux client not properly initialized")
            return None
        
        try:
            # Since SpacesApi is not available in this version of the SDK,
            # we'll create a mock implementation for demo purposes
            logger.info(f"Creating mock space with title: {title}")
            
            # In a production environment, you would make API calls to Mux
            # to create a real space
            mock_space = {
                'space_id': f"mock-space-{hash(title)}",
                'status': 'active',
                'created_at': '2025-04-11T00:00:00Z',
                'broadcasts': []
            }
            
            return mock_space
            
        except Exception as e:
            logger.error(f"Error creating video space: {str(e)}")
            return None
    
    def get_available_asl_categories(self) -> List[str]:
        """
        Get a list of available ASL video categories
        
        Returns:
            List of category names
        """
        # This would normally retrieve categories from Mux or your database
        # For now, return a predefined list of categories
        return [
            'tax_filing',
            'financial_profile',
            'investment_recommendations',
            'retirement_planning',
            'tax_documents',
            'emergency_fund',
            'debt_management',
            'insurance_coverage'
        ]

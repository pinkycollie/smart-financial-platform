import os
import logging
from typing import Dict, List, Any, Optional
import mux_python
from mux_python.rest import ApiException

logger = logging.getLogger(__name__)

class MuxClient:
    """Client for interacting with the Mux Video API for ASL content"""
    
    def __init__(self):
        """Initialize Mux client with authentication"""
        try:
            # Configure API credentials from environment
            token_id = os.environ.get('MUX_TOKEN_ID', '')
            token_secret = os.environ.get('MUX_TOKEN_SECRET', '')
            
            # Configure HTTP basic authorization
            configuration = mux_python.Configuration()
            configuration.username = token_id
            configuration.password = token_secret
            
            # Create API clients
            self.assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))
            self.spaces_api = mux_python.SpacesApi(mux_python.ApiClient(configuration))
            
            # Cache for videos
            self._video_cache = {}
            
            logger.info("Mux client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mux client: {str(e)}")
            raise
    
    def get_asl_video(self, video_key: str) -> Optional[Dict[str, Any]]:
        """
        Get an ASL video by its key identifier
        
        Args:
            video_key: Key identifier for the ASL video
        
        Returns:
            Dictionary with video details or None if not found
        """
        # Check cache first
        if video_key in self._video_cache:
            return self._video_cache[video_key]
        
        try:
            # Get asset from Mux
            asset = self.assets_api.get_asset(video_key)
            
            if not asset or not asset.playback_ids:
                logger.warning(f"No playback IDs found for video: {video_key}")
                return None
            
            # Build video details
            playback_id = asset.playback_ids[0].id
            video_details = {
                'id': asset.id,
                'playback_id': playback_id,
                'duration': asset.duration,
                'status': asset.status,
                'created_at': asset.created_at,
                'playback_url': f"https://stream.mux.com/{playback_id}.m3u8",
                'thumbnail_url': f"https://image.mux.com/{playback_id}/thumbnail.jpg?width=640",
                'metadata': asset.metadata
            }
            
            # Cache the result
            self._video_cache[video_key] = video_details
            
            return video_details
        except ApiException as e:
            logger.error(f"Mux API error getting video {video_key}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting ASL video {video_key}: {str(e)}")
            return None
    
    def get_asl_videos_for_context(self, context: str) -> List[Dict[str, Any]]:
        """
        Get all ASL videos for a specific context
        
        Args:
            context: The context for which to retrieve videos (e.g., 'tax_filing', 'financial_concepts')
        
        Returns:
            List of dictionaries with video details
        """
        try:
            # Search for assets with context in metadata
            query = f"metadata.context='{context}'"
            assets = self.assets_api.list_assets(query=query)
            
            videos = []
            for asset in assets.data:
                if asset.playback_ids:
                    playback_id = asset.playback_ids[0].id
                    videos.append({
                        'id': asset.id,
                        'title': asset.metadata.get('title', 'Untitled ASL Video'),
                        'description': asset.metadata.get('description', ''),
                        'context': context,
                        'playback_id': playback_id,
                        'duration': asset.duration,
                        'playback_url': f"https://stream.mux.com/{playback_id}.m3u8",
                        'thumbnail_url': f"https://image.mux.com/{playback_id}/thumbnail.jpg?width=640"
                    })
            
            return videos
        except ApiException as e:
            logger.error(f"Mux API error getting videos for context {context}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting ASL videos for context {context}: {str(e)}")
            return []
    
    def get_fallback_video(self) -> Dict[str, Any]:
        """
        Get a fallback ASL video when the requested one is not available
        
        Returns:
            Dictionary with fallback video details
        """
        try:
            # Get a generic fallback video from Mux
            query = "metadata.type='fallback'"
            assets = self.assets_api.list_assets(query=query, limit=1)
            
            if assets.data and assets.data[0].playback_ids:
                asset = assets.data[0]
                playback_id = asset.playback_ids[0].id
                
                return {
                    'id': asset.id,
                    'title': 'Fallback ASL Video',
                    'description': 'This is a fallback ASL video when the requested content is not available',
                    'playback_id': playback_id,
                    'duration': asset.duration,
                    'playback_url': f"https://stream.mux.com/{playback_id}.m3u8",
                    'thumbnail_url': f"https://image.mux.com/{playback_id}/thumbnail.jpg?width=640",
                    'is_fallback': True
                }
            else:
                # Return a default response if no fallback video found
                logger.warning("No fallback ASL video found")
                return {
                    'id': 'fallback',
                    'title': 'ASL Video Not Available',
                    'description': 'We apologize, but the requested ASL video is not available at this time.',
                    'playback_url': '',
                    'thumbnail_url': '',
                    'is_fallback': True
                }
        except Exception as e:
            logger.error(f"Error getting fallback ASL video: {str(e)}")
            return {
                'id': 'error',
                'title': 'Error Loading ASL Video',
                'description': 'There was an error loading the ASL video. Please try again later.',
                'playback_url': '',
                'thumbnail_url': '',
                'is_fallback': True,
                'is_error': True
            }
    
    def create_video_space(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Create a new Mux Space for live ASL interpretation
        
        Args:
            title: Title for the space
        
        Returns:
            Dictionary with space details or None if creation failed
        """
        try:
            # Create space request
            create_space_request = mux_python.CreateSpaceRequest(
                type="browser",
                passive=False,
                broadcasts=[],
                session=None,  # Let Mux generate the session ID
                recording=None  # No recording by default
            )
            
            # Send request to create space
            space = self.spaces_api.create_space(create_space_request)
            
            # Format the response
            return {
                'id': space.id,
                'status': space.status,
                'created_at': space.created_at,
                'joins_allowed': space.broadcasts[0].joins_allowed if space.broadcasts else True,
                'active': space.active,
                'max_participants': 10,  # Default max participants
                'title': title
            }
        except ApiException as e:
            logger.error(f"Mux API error creating video space: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creating Mux video space: {str(e)}")
            return None
    
    def get_available_asl_categories(self) -> List[str]:
        """
        Get a list of available ASL video categories
        
        Returns:
            List of category names
        """
        try:
            # For financial categories, we'll have dedicated contexts
            categories = [
                'tax_filing',
                'financial_concepts',
                'investment_strategies',
                'retirement_planning',
                'debt_management',
                'financial_literacy',
                'banking_basics',
                'budgeting'
            ]
            
            # Check which categories have videos
            available_categories = []
            for category in categories:
                query = f"metadata.context='{category}'"
                assets = self.assets_api.list_assets(query=query, limit=1)
                if assets.data:
                    available_categories.append(category)
            
            return available_categories
        except Exception as e:
            logger.error(f"Error getting ASL categories: {str(e)}")
            return []
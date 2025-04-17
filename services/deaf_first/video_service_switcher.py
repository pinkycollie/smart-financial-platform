"""
Video service switcher for the DEAF FIRST platform.
Manages multiple video providers for different video needs.
"""

import os
import logging
import json
from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class VideoServiceType(Enum):
    """Types of video services used in the platform"""
    ASL_CONTENT = "asl_content"  # Pre-recorded ASL content
    LIVE_SUPPORT = "live_support"  # Live ASL support
    INTERACTIVE = "interactive"  # Interactive ASL components
    EDUCATIONAL = "educational"  # Educational ASL content

class VideoProviderType(Enum):
    """Types of video providers"""
    MUX = "mux"
    SIGN_ASL = "sign_asl"
    ASL_NOW = "asl_now"
    SIGN_VRI = "sign_vri"
    PURPLE_VRI = "purple_vri"
    DEAF_FIRST_LIBRARY = "deaf_first_library"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    CUSTOM = "custom"

class VideoServiceSwitcher:
    """
    Service that switches between different video providers
    based on the type of video service needed.
    """
    
    def __init__(self):
        """Initialize video service switcher"""
        self.provider_configs = {
            VideoServiceType.ASL_CONTENT: {
                "primary": os.environ.get("ASL_CONTENT_PRIMARY_PROVIDER", "mux"),
                "fallback": os.environ.get("ASL_CONTENT_FALLBACK_PROVIDER", "sign_asl")
            },
            VideoServiceType.LIVE_SUPPORT: {
                "primary": os.environ.get("LIVE_SUPPORT_PRIMARY_PROVIDER", "asl_now"),
                "fallback": os.environ.get("LIVE_SUPPORT_FALLBACK_PROVIDER", "sign_vri")
            },
            VideoServiceType.INTERACTIVE: {
                "primary": os.environ.get("INTERACTIVE_PRIMARY_PROVIDER", "mux"),
                "fallback": os.environ.get("INTERACTIVE_FALLBACK_PROVIDER", "sign_asl")
            },
            VideoServiceType.EDUCATIONAL: {
                "primary": os.environ.get("EDUCATIONAL_PRIMARY_PROVIDER", "deaf_first_library"),
                "fallback": os.environ.get("EDUCATIONAL_FALLBACK_PROVIDER", "sign_asl")
            }
        }
        
        # Initialize provider clients
        self._initialize_provider_clients()
    
    def _initialize_provider_clients(self):
        """Initialize provider client instances"""
        self.provider_clients = {}
        
        # Import service clients
        try:
            from services.deaf_first.mux_client import mux_client
            self.provider_clients[VideoProviderType.MUX.value] = mux_client
        except (ImportError, ModuleNotFoundError):
            logger.warning("MUX client not available")
        
        try:
            from services.deaf_first.signasl_integration import signasl_client
            self.provider_clients[VideoProviderType.SIGN_ASL.value] = signasl_client
        except (ImportError, ModuleNotFoundError):
            logger.warning("SignASL client not available")
        
        try:
            from services.deaf_first.asl_support import asl_support_service
            self.provider_clients[VideoProviderType.ASL_NOW.value] = asl_support_service
            # ASL support service handles multiple providers (ASL Now, SignVRI, PurpleVRI)
            self.provider_clients[VideoProviderType.SIGN_VRI.value] = asl_support_service
            self.provider_clients[VideoProviderType.PURPLE_VRI.value] = asl_support_service
        except (ImportError, ModuleNotFoundError):
            logger.warning("ASL support service not available")
        
        try:
            from services.deaf_first.deaffirst_library import deaffirst_library
            self.provider_clients[VideoProviderType.DEAF_FIRST_LIBRARY.value] = deaffirst_library
        except (ImportError, ModuleNotFoundError):
            logger.warning("DEAF FIRST library not available")
    
    def get_provider_for_service(self, service_type: Union[VideoServiceType, str], 
                                use_fallback: bool = False) -> str:
        """
        Get the configured provider for a service type.
        
        Args:
            service_type: Type of video service
            use_fallback: Whether to use fallback provider
            
        Returns:
            Provider type as string
        """
        if isinstance(service_type, str):
            service_type = VideoServiceType(service_type)
        
        provider_config = self.provider_configs.get(service_type, {})
        if not provider_config:
            logger.warning(f"No configuration found for service type {service_type}")
            return VideoProviderType.MUX.value
        
        provider_key = "fallback" if use_fallback else "primary"
        return provider_config.get(provider_key, VideoProviderType.MUX.value)
    
    def get_provider_client(self, provider_type: Union[VideoProviderType, str]):
        """
        Get the client for a provider type.
        
        Args:
            provider_type: Type of video provider
            
        Returns:
            Provider client instance
        """
        if isinstance(provider_type, str):
            # Convert string to enum if needed
            try:
                provider_type = VideoProviderType(provider_type).value
            except ValueError:
                provider_type = provider_type
        else:
            provider_type = provider_type.value
        
        client = self.provider_clients.get(provider_type)
        if not client:
            logger.warning(f"No client found for provider type {provider_type}")
        
        return client
    
    def get_client_for_service(self, service_type: Union[VideoServiceType, str], 
                             use_fallback: bool = False):
        """
        Get the appropriate client for a service type.
        
        Args:
            service_type: Type of video service
            use_fallback: Whether to use fallback provider
            
        Returns:
            Provider client instance
        """
        provider_type = self.get_provider_for_service(service_type, use_fallback)
        return self.get_provider_client(provider_type)
    
    def get_video_url(self, video_id: str, provider_type: Union[VideoProviderType, str] = None) -> Optional[str]:
        """
        Get the URL for a video by ID.
        
        Args:
            video_id: Video ID
            provider_type: Type of video provider (optional, detected from video_id if not provided)
            
        Returns:
            Video URL or None if not found
        """
        if not provider_type:
            # Detect provider from video ID format
            provider_type = self._detect_provider_from_id(video_id)
        
        client = self.get_provider_client(provider_type)
        if not client:
            return None
        
        if provider_type == VideoProviderType.MUX.value:
            return client.get_playback_url(video_id)
        elif provider_type == VideoProviderType.SIGN_ASL.value:
            return client.get_video_url(video_id)
        elif provider_type == VideoProviderType.DEAF_FIRST_LIBRARY.value:
            return client.get_video_url(video_id)
        elif provider_type in [VideoProviderType.YOUTUBE.value, VideoProviderType.VIMEO.value]:
            # Direct URLs for external providers
            if provider_type == VideoProviderType.YOUTUBE.value:
                return f"https://www.youtube.com/embed/{video_id}"
            else:
                return f"https://player.vimeo.com/video/{video_id}"
        
        return None
    
    def _detect_provider_from_id(self, video_id: str) -> str:
        """
        Detect provider type from video ID format.
        
        Args:
            video_id: Video ID
            
        Returns:
            Provider type as string
        """
        if video_id.startswith('mux_'):
            return VideoProviderType.MUX.value
        elif video_id.startswith('sa_'):
            return VideoProviderType.SIGN_ASL.value
        elif video_id.startswith('dfl_'):
            return VideoProviderType.DEAF_FIRST_LIBRARY.value
        elif len(video_id) == 11:  # Standard YouTube ID length
            return VideoProviderType.YOUTUBE.value
        elif video_id.isdigit():  # Vimeo IDs are numeric
            return VideoProviderType.VIMEO.value
        
        # Default to MUX
        return VideoProviderType.MUX.value
    
    def get_video_metadata(self, video_id: str, provider_type: Union[VideoProviderType, str] = None) -> Dict[str, Any]:
        """
        Get metadata for a video.
        
        Args:
            video_id: Video ID
            provider_type: Type of video provider (optional, detected from video_id if not provided)
            
        Returns:
            Video metadata
        """
        if not provider_type:
            # Detect provider from video ID format
            provider_type = self._detect_provider_from_id(video_id)
        
        client = self.get_provider_client(provider_type)
        if not client:
            return {}
        
        try:
            if provider_type == VideoProviderType.MUX.value:
                return client.get_asset_metadata(video_id)
            elif provider_type == VideoProviderType.SIGN_ASL.value:
                return client.get_video_metadata(video_id)
            elif provider_type == VideoProviderType.DEAF_FIRST_LIBRARY.value:
                return client.get_video_metadata(video_id)
        except Exception as e:
            logger.error(f"Error getting video metadata: {e}")
        
        return {}
    
    def search_videos(self, query: str, service_type: Union[VideoServiceType, str], 
                     limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for videos by query.
        
        Args:
            query: Search query
            service_type: Type of video service
            limit: Maximum number of results
            
        Returns:
            List of video metadata
        """
        client = self.get_client_for_service(service_type)
        if not client:
            return []
        
        try:
            provider_type = self.get_provider_for_service(service_type)
            
            if provider_type == VideoProviderType.MUX.value:
                return client.search_assets(query, limit=limit)
            elif provider_type == VideoProviderType.SIGN_ASL.value:
                return client.search_videos(query, limit=limit)
            elif provider_type == VideoProviderType.DEAF_FIRST_LIBRARY.value:
                return client.search_videos(query, limit=limit)
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
        
        return []
    
    def get_white_label_video_url(self, video_id: str, white_label_id: int = None, 
                                provider_type: Union[VideoProviderType, str] = None) -> Optional[str]:
        """
        Get white-labeled video URL for a licensee.
        
        Args:
            video_id: Video ID
            white_label_id: Licensee ID for white-label
            provider_type: Type of video provider (optional, detected from video_id if not provided)
            
        Returns:
            White-labeled video URL or regular URL if white-labeling not available
        """
        # If no white label ID, use regular URL
        if not white_label_id:
            return self.get_video_url(video_id, provider_type)
        
        if not provider_type:
            provider_type = self._detect_provider_from_id(video_id)
        
        client = self.get_provider_client(provider_type)
        if not client:
            return None
        
        # Get licensee info
        from models_reseller import Licensee
        licensee = Licensee.query.get(white_label_id)
        if not licensee:
            return self.get_video_url(video_id, provider_type)
        
        try:
            if provider_type == VideoProviderType.MUX.value:
                # MUX supports custom domain playback
                if licensee.domain_name:
                    return client.get_custom_domain_playback_url(video_id, licensee.domain_name)
                return client.get_playback_url(video_id)
            elif provider_type == VideoProviderType.SIGN_ASL.value:
                # SignASL may support white-labeling
                if hasattr(client, 'get_white_label_video_url'):
                    return client.get_white_label_video_url(video_id, white_label_id)
                return client.get_video_url(video_id)
            elif provider_type == VideoProviderType.DEAF_FIRST_LIBRARY.value:
                # Deaf First Library supports white-labeling
                if hasattr(client, 'get_white_label_video_url'):
                    return client.get_white_label_video_url(video_id, white_label_id)
                return client.get_video_url(video_id)
        except Exception as e:
            logger.error(f"Error getting white-label video URL: {e}")
            # Fall back to regular URL
            return self.get_video_url(video_id, provider_type)
        
        return self.get_video_url(video_id, provider_type)

# Initialize a singleton instance
video_service = VideoServiceSwitcher()
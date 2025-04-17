"""
Mux video integration client for the DEAF FIRST platform.
Handles ASL video content for white-label resellers.
"""

import os
import json
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

class MuxClient:
    """
    Client for Mux Video API.
    Used for hosting ASL videos with white-label support.
    """
    
    def __init__(self, token_id=None, token_secret=None):
        """Initialize Mux client with API credentials"""
        self.token_id = token_id or os.environ.get('MUX_TOKEN_ID')
        self.token_secret = token_secret or os.environ.get('MUX_TOKEN_SECRET')
        
        if not all([self.token_id, self.token_secret]):
            logger.warning("MUX credentials not configured. ASL video features will be limited.")
            self.client = None
        else:
            try:
                # Import Mux Python SDK
                import mux_python
                from mux_python.api import assets_api, playback_ids_api, spaces_api
                
                # Configure API client
                configuration = mux_python.Configuration()
                configuration.username = self.token_id
                configuration.password = self.token_secret
                
                api_client = mux_python.ApiClient(configuration)
                
                # Initialize API instances
                self.assets_api = assets_api.AssetsApi(api_client)
                self.playback_ids_api = playback_ids_api.PlaybackIDsApi(api_client)
                self.spaces_api = spaces_api.SpacesApi(api_client)
                
                self.client = api_client
                logger.info("Mux client initialized successfully")
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to initialize Mux client: {e}")
                self.client = None
        
        # Initialize signasl integration for fallback
        try:
            from services.deaf_first.signasl_integration import signasl_client
            self.signasl_client = signasl_client
            logger.info("SignASL integration initialized successfully")
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to initialize SignASL client: {e}")
            self.signasl_client = None
    
    def is_available(self) -> bool:
        """
        Check if Mux client is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.client is not None
    
    def get_playback_url(self, asset_id: str, policy: str = 'public') -> Optional[str]:
        """
        Get playback URL for a video asset.
        
        Args:
            asset_id: Mux asset ID or playback ID
            policy: Playback policy ('public' or 'signed')
            
        Returns:
            Playback URL or None if not available
        """
        if not self.is_available():
            # Try fallback to SignASL if available
            if self.signasl_client and asset_id.startswith('sa_'):
                return self.signasl_client.get_video_url(asset_id)
            return None
        
        try:
            # Check if asset_id is already a playback ID
            if asset_id.startswith('mux_'):
                asset_id = asset_id.replace('mux_', '')
            
            if policy == 'public':
                return f"https://stream.mux.com/{asset_id}.m3u8"
            else:
                # Generate signed playback URL
                return self._generate_signed_url(asset_id)
        except Exception as e:
            logger.error(f"Error getting playback URL: {e}")
            return None
    
    def get_custom_domain_playback_url(self, asset_id: str, domain: str) -> Optional[str]:
        """
        Get playback URL with custom domain.
        
        Args:
            asset_id: Mux asset ID or playback ID
            domain: Custom domain
            
        Returns:
            Custom domain playback URL or None if not available
        """
        if not self.is_available():
            return None
        
        try:
            # Check if asset_id is already a playback ID
            if asset_id.startswith('mux_'):
                asset_id = asset_id.replace('mux_', '')
            
            # Ensure domain is properly formatted
            if not domain.startswith('http'):
                domain = f"https://{domain}"
            
            # Remove trailing slash if present
            domain = domain.rstrip('/')
            
            return f"{domain}/video/{asset_id}.m3u8"
        except Exception as e:
            logger.error(f"Error getting custom domain playback URL: {e}")
            return self.get_playback_url(asset_id)
    
    def get_asset_metadata(self, asset_id: str) -> Dict[str, Any]:
        """
        Get metadata for a video asset.
        
        Args:
            asset_id: Mux asset ID
            
        Returns:
            Asset metadata
        """
        if not self.is_available():
            # Try fallback to SignASL if available
            if self.signasl_client and asset_id.startswith('sa_'):
                return self.signasl_client.get_video_metadata(asset_id)
            return {}
        
        try:
            # Check if asset_id is already a playback ID
            if asset_id.startswith('mux_'):
                asset_id = asset_id.replace('mux_', '')
                
                # Get asset ID from playback ID
                playback_id = asset_id
                playback_info = self.playback_ids_api.get_playback_id(playback_id)
                asset_id = playback_info.object.asset_id
            
            asset = self.assets_api.get_asset(asset_id)
            
            return {
                'id': asset.data.id,
                'playback_id': asset.data.playback_ids[0].id if asset.data.playback_ids else None,
                'title': asset.data.mp4_support,
                'duration': asset.data.duration,
                'created_at': asset.data.created_at,
                'status': asset.data.status,
                'aspect_ratio': asset.data.aspect_ratio,
                'resolution': f"{asset.data.max_stored_resolution or 'unknown'}p",
                'metadata': asset.data.metadata
            }
        except Exception as e:
            logger.error(f"Error getting asset metadata: {e}")
            return {}
    
    def search_assets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for video assets.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of asset metadata
        """
        if not self.is_available():
            # Try fallback to SignASL if available
            if self.signasl_client:
                return self.signasl_client.search_videos(query, limit=limit)
            return []
        
        try:
            # Mux doesn't have a search API, so we get all assets and filter
            # Note: This is inefficient and should be replaced with a proper database search
            assets = self.assets_api.list_assets()
            
            results = []
            for asset in assets.data:
                # Check if asset metadata or filename contains query
                if (
                    query.lower() in (asset.mp4_support or '').lower() or
                    query.lower() in (asset.playback_ids[0].id if asset.playback_ids else '').lower() or
                    (asset.metadata and any(query.lower() in str(value).lower() for value in asset.metadata.values()))
                ):
                    results.append({
                        'id': f"mux_{asset.playback_ids[0].id}" if asset.playback_ids else asset.id,
                        'title': asset.mp4_support,
                        'duration': asset.duration,
                        'created_at': asset.created_at,
                        'playback_url': self.get_playback_url(asset.playback_ids[0].id if asset.playback_ids else asset.id),
                        'thumbnail_url': f"https://image.mux.com/{asset.playback_ids[0].id if asset.playback_ids else asset.id}/thumbnail.jpg"
                    })
                    
                    if len(results) >= limit:
                        break
            
            return results
        except Exception as e:
            logger.error(f"Error searching assets: {e}")
            return []
    
    def create_asset(self, url: str, title: str = None, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new video asset from URL.
        
        Args:
            url: Video URL
            title: Video title
            metadata: Additional metadata
            
        Returns:
            Created asset information or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            import mux_python
            from mux_python.models import CreateAssetRequest, InputSettings
            
            # Prepare input settings
            input_settings = InputSettings(url=url)
            
            # Prepare metadata
            normalized_metadata = {
                'title': title or 'Untitled Video',
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
            if metadata:
                normalized_metadata.update(metadata)
            
            # Create asset request
            create_asset_request = CreateAssetRequest(
                input=input_settings,
                playback_policy=['public'],
                mp4_support='standard',
                normalize_audio=True,
                metadata=normalized_metadata
            )
            
            # Create asset
            asset = self.assets_api.create_asset(create_asset_request)
            
            return {
                'id': asset.data.id,
                'playback_id': asset.data.playback_ids[0].id if asset.data.playback_ids else None,
                'status': asset.data.status,
                'created_at': asset.data.created_at
            }
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            return None
    
    def delete_asset(self, asset_id: str) -> bool:
        """
        Delete a video asset.
        
        Args:
            asset_id: Mux asset ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            # Check if asset_id is already a playback ID
            if asset_id.startswith('mux_'):
                asset_id = asset_id.replace('mux_', '')
                
                # Get asset ID from playback ID
                playback_id = asset_id
                playback_info = self.playback_ids_api.get_playback_id(playback_id)
                asset_id = playback_info.object.asset_id
            
            self.assets_api.delete_asset(asset_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting asset: {e}")
            return False
    
    def create_signed_playback_id(self, asset_id: str, jwt_key: str = None) -> Optional[str]:
        """
        Create a signed playback ID for an asset.
        
        Args:
            asset_id: Mux asset ID
            jwt_key: Optional JWT key (uses default if not provided)
            
        Returns:
            Signed playback ID or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            import mux_python
            from mux_python.models import CreatePlaybackIDRequest
            
            # Create playback ID request
            create_playback_id_request = CreatePlaybackIDRequest(
                policy='signed'
            )
            
            # Create playback ID
            playback_id = self.playback_ids_api.create_asset_playback_id(
                asset_id, create_playback_id_request
            )
            
            return playback_id.data.id
        except Exception as e:
            logger.error(f"Error creating signed playback ID: {e}")
            return None
    
    def _generate_signed_url(self, playback_id: str, expires_in: int = 3600) -> str:
        """
        Generate a signed URL for playback.
        
        Args:
            playback_id: Playback ID
            expires_in: Expiration time in seconds
            
        Returns:
            Signed URL
        """
        if not self.token_secret:
            return f"https://stream.mux.com/{playback_id}.m3u8"
        
        # Create JWT payload
        expiration = int(time.time()) + expires_in
        
        payload = {
            'sub': playback_id,
            'exp': expiration,
            'aud': 'v'
        }
        
        # Encode payload
        header = {'typ': 'JWT', 'alg': 'HS256'}
        
        # Convert header and payload to JSON and base64 encode
        header_json = json.dumps(header).encode()
        header_b64 = base64.urlsafe_b64encode(header_json).decode().rstrip('=')
        
        payload_json = json.dumps(payload).encode()
        payload_b64 = base64.urlsafe_b64encode(payload_json).decode().rstrip('=')
        
        # Create signature
        to_sign = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.token_secret.encode(),
            to_sign.encode(),
            hashlib.sha256
        ).digest()
        
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Create JWT token
        jwt_token = f"{to_sign}.{signature_b64}"
        
        # Create signed URL
        return f"https://stream.mux.com/{playback_id}.m3u8?token={jwt_token}"
    
    def create_space(self, name: str, whitelist_domains: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new space for live video.
        
        Args:
            name: Space name
            whitelist_domains: List of domains to whitelist
            
        Returns:
            Created space information or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            import mux_python
            from mux_python.models import CreateSpaceRequest
            
            # Prepare space request
            create_space_request = CreateSpaceRequest(
                type='browser',
                passive=True,
                broadcasts=[{'passthrough': 'true', 'background_color': '#000000'}],
                broadcasts_enabled=True
            )
            
            # Create space
            space = self.spaces_api.create_space(create_space_request)
            
            return {
                'id': space.data.id,
                'status': space.data.status,
                'created_at': space.data.created_at,
                'broadcasts': [{
                    'id': b.id, 
                    'status': b.status, 
                    'live_stream_id': b.live_stream_id
                } for b in space.data.broadcasts]
            }
        except Exception as e:
            logger.error(f"Error creating space: {e}")
            return None

# Initialize a global client instance
mux_client = MuxClient()
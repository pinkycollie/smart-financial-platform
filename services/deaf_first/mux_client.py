import os
import logging
import mux_python
from mux_python.exceptions import NotFoundException, ApiException

# Set up logging
logger = logging.getLogger(__name__)

class MuxClient:
    """Client for interacting with Mux Video API for ASL content"""
    
    def __init__(self):
        """Initialize the Mux client with API credentials"""
        self.token_id = os.environ.get('MUX_TOKEN_ID')
        self.token_secret = os.environ.get('MUX_TOKEN_SECRET')
        
        if not self.token_id or not self.token_secret:
            logger.warning("MUX credentials not configured. ASL video features will be limited.")
            self.client_configured = False
            return
            
        # Configure the Mux client
        configuration = mux_python.Configuration()
        configuration.username = self.token_id
        configuration.password = self.token_secret
        
        # Initialize the API clients
        self.assets_api = mux_python.AssetsApi(mux_python.ApiClient(configuration))
        self.playback_ids_api = mux_python.PlaybackIDApi(mux_python.ApiClient(configuration))
        
        # Check if Mux Spaces API is available
        try:
            self.spaces_api = mux_python.SpacesApi(mux_python.ApiClient(configuration))
            self.client_configured = True
        except AttributeError:
            logger.warning("Mux Spaces API not available in this version of mux_python")
            self.spaces_api = None
            self.client_configured = True
    
    def create_asset(self, video_url, title=None):
        """
        Create a new Mux asset from a video URL
        
        Args:
            video_url (str): URL of the video file
            title (str, optional): Title for the asset
            
        Returns:
            str: Asset ID if successful, None otherwise
        """
        if not self.client_configured:
            logger.error("Mux client not configured. Cannot create asset.")
            return None
            
        try:
            create_asset_request = mux_python.CreateAssetRequest(
                input=video_url,
                playback_policy=[mux_python.PlaybackPolicy.PUBLIC],
                mp4_support="standard"
            )
            
            if title:
                create_asset_request.passthrough = {"title": title}
                
            result = self.assets_api.create_asset(create_asset_request)
            return result.data.id
            
        except ApiException as e:
            logger.error(f"Error creating Mux asset: {e}")
            return None
    
    def get_playback_url(self, asset_id):
        """
        Get the playback URL for a Mux asset
        
        Args:
            asset_id (str): The Mux asset ID
            
        Returns:
            str: Playback URL if successful, None otherwise
        """
        if not self.client_configured:
            logger.error("Mux client not configured. Cannot get playback URL.")
            return None
            
        try:
            asset = self.assets_api.get_asset(asset_id)
            
            if not asset.data.playback_ids:
                # Create a playback ID if none exists
                playback_id_request = mux_python.CreatePlaybackIDRequest(
                    policy=mux_python.PlaybackPolicy.PUBLIC
                )
                playback_id = self.assets_api.create_asset_playback_id(asset_id, playback_id_request)
                playback_id_value = playback_id.data.id
            else:
                playback_id_value = asset.data.playback_ids[0].id
                
            return f"https://stream.mux.com/{playback_id_value}.m3u8"
            
        except (ApiException, NotFoundException) as e:
            logger.error(f"Error getting Mux playback URL: {e}")
            return None
    
    def delete_asset(self, asset_id):
        """
        Delete a Mux asset
        
        Args:
            asset_id (str): The Mux asset ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.client_configured:
            logger.error("Mux client not configured. Cannot delete asset.")
            return False
            
        try:
            self.assets_api.delete_asset(asset_id)
            return True
        except (ApiException, NotFoundException) as e:
            logger.error(f"Error deleting Mux asset: {e}")
            return False
            
    def get_asset_info(self, asset_id):
        """
        Get information about a Mux asset
        
        Args:
            asset_id (str): The Mux asset ID
            
        Returns:
            dict: Asset information if successful, None otherwise
        """
        if not self.client_configured:
            logger.error("Mux client not configured. Cannot get asset info.")
            return None
            
        try:
            asset = self.assets_api.get_asset(asset_id)
            return {
                'id': asset.data.id,
                'status': asset.data.status,
                'duration': asset.data.duration,
                'created_at': asset.data.created_at
            }
        except (ApiException, NotFoundException) as e:
            logger.error(f"Error getting Mux asset info: {e}")
            return None
        
    def create_signed_url(self, asset_id, expiration_seconds=3600):
        """
        Create a signed URL for secure playback
        
        Args:
            asset_id (str): The Mux asset ID
            expiration_seconds (int): Seconds until URL expires
            
        Returns:
            str: Signed URL if successful, None otherwise
        """
        # Note: Implementation would require JWT library
        logger.info("Signed URL functionality requires additional implementation")
        return None

# Initialize an instance of the client
mux_client = MuxClient()

# SignASL Integration
def initialize_signasl():
    """Initialize connection to SignASL service"""
    from .signasl_integration import SignASLClient
    
    try:
        signasl_client = SignASLClient()
        logger.info("SignASL integration initialized successfully")
        return signasl_client
    except Exception as e:
        logger.error(f"Error initializing SignASL integration: {e}")
        return None

signasl_client = initialize_signasl()
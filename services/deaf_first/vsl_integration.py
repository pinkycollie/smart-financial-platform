"""
VSL Labs API Integration for DEAF FIRST Platform
https://www.vsllabs.com/

This module provides integration with VSL Labs' beta API for visual sign language technology.
"""

import os
import requests
import json
import logging
from urllib.parse import urljoin
from flask import current_app

# Configure logger
logger = logging.getLogger(__name__)

class VSLLabsClient:
    """Client for interacting with VSL Labs API"""
    
    def __init__(self, api_key=None, base_url="https://api.vsllabs.com/v1/"):
        """Initialize the VSL Labs client with API credentials"""
        self.api_key = api_key or os.environ.get("VSL_LABS_API_KEY", "")
        self.base_url = base_url
        self.initialized = bool(self.api_key)
        
        if not self.initialized:
            logger.warning("VSL Labs API key not configured. VSL features will be limited.")
    
    def _make_request(self, endpoint, method="GET", data=None, params=None):
        """Make a request to the VSL Labs API"""
        if not self.initialized:
            logger.error("Cannot make API request - VSL Labs API not initialized")
            return None
            
        url = urljoin(self.base_url, endpoint)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to VSL Labs API: {str(e)}")
            return None
    
    def get_asl_interpretation(self, text, options=None):
        """
        Get ASL interpretation for text content
        
        Args:
            text (str): English text to be interpreted in ASL
            options (dict): Additional options for interpretation
            
        Returns:
            dict: Response containing ASL interpretation data
        """
        data = {
            "text": text,
            "options": options or {}
        }
        
        return self._make_request("asl/interpret", method="POST", data=data)
    
    def get_sign_gloss(self, text):
        """
        Get sign gloss for English text
        
        Args:
            text (str): English text to convert to sign gloss
            
        Returns:
            dict: Response containing sign gloss data
        """
        return self._make_request("asl/gloss", method="POST", data={"text": text})
    
    def translate_asl_video(self, video_url):
        """
        Translate ASL video to English text
        
        Args:
            video_url (str): URL of ASL video content
            
        Returns:
            dict: Response containing English translation
        """
        return self._make_request(
            "asl/translate", 
            method="POST", 
            data={"video_url": video_url}
        )
    
    def create_asl_video_chat(self, session_name, user_id):
        """
        Create a new ASL video chat session
        
        Args:
            session_name (str): Name of the chat session
            user_id (str): User identifier
            
        Returns:
            dict: Response containing session details
        """
        data = {
            "session_name": session_name,
            "user_id": user_id,
            "features": {
                "asl_translation": True,
                "captioning": True,
                "recording": True
            }
        }
        
        return self._make_request("video/session/create", method="POST", data=data)
    
    def get_financial_terminology(self, term):
        """
        Get specialized financial terminology in ASL
        
        Args:
            term (str): Financial term to look up
            
        Returns:
            dict: Response containing ASL representation of the term
        """
        params = {"term": term, "category": "financial"}
        return self._make_request("asl/terminology", params=params)


# Initialize the VSL client
vsl_client = None

def init_app(app):
    """Initialize the VSL client with the Flask app"""
    global vsl_client
    
    api_key = app.config.get("VSL_LABS_API_KEY", "")
    vsl_client = VSLLabsClient(api_key=api_key)
    
    if vsl_client.initialized:
        logger.info("VSL Labs API client initialized successfully")
    else:
        logger.warning("VSL Labs API client initialized with limited functionality")
        
    return vsl_client
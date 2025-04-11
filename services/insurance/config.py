import os

class BoostConfig:
    """Configuration for Boost Insurance API"""
    
    API_URL = os.environ.get('BOOST_API_URL', 'https://api.boostinsurance.io')
    CLIENT_ID = os.environ.get('BOOST_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('BOOST_CLIENT_SECRET', '')
    
    # API Endpoints
    AUTH_ENDPOINT = '/oauth/token'
    PRODUCTS_ENDPOINT = '/api/v1/products'
    QUOTE_ENDPOINT = '/api/v1/quote'
    POLICY_ENDPOINT = '/api/v1/policies'
    CLAIMS_ENDPOINT = '/api/v1/claims'
    
    # Request Configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # seconds
    CONNECT_TIMEOUT = 5  # seconds
    READ_TIMEOUT = 30  # seconds
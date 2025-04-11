import os

class AprilConfig:
    # API Configuration
    API_URL = os.environ.get('APRIL_API_URL', 'https://api.getapril.com')
    CLIENT_ID = os.environ.get('APRIL_CLIENT_ID', '')
    CLIENT_SECRET = os.environ.get('APRIL_CLIENT_SECRET', '')
    
    # Endpoints
    AUTH_ENDPOINT = '/oauth/token'
    FILER_ENDPOINT = '/api/v1/tax/filing'
    ESTIMATOR_ENDPOINT = '/api/v1/profiles'
    OPTIMIZER_ENDPOINT = '/api/v1/products/engagement'
    
    # Rate limiting
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # seconds
    
    # Timeout settings
    CONNECT_TIMEOUT = 5  # seconds
    READ_TIMEOUT = 30  # seconds

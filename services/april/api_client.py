import logging
import time
import requests
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from models import AprilTransaction
from simple_app import db
from services.april.config import AprilConfig

logger = logging.getLogger(__name__)

class AprilAPIClient:
    """Client for interacting with the April API"""
    
    def __init__(self):
        """Initialize April API client"""
        self.config = AprilConfig
        self.token = None
        self.token_expiry = None
        logger.info("April API client initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication token"""
        if self._token_expired():
            self._refresh_token()
            
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _token_expired(self) -> bool:
        """Check if the current token has expired"""
        if not self.token or not self.token_expiry:
            return True
        return datetime.utcnow() >= self.token_expiry
    
    def _refresh_token(self) -> None:
        """Obtain a new access token"""
        url = f"{self.config.API_URL}{self.config.AUTH_ENDPOINT}"
        
        payload = {
            'client_id': self.config.CLIENT_ID,
            'client_secret': self.config.CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT)
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)  # Default to 1 hour
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            
            logger.info("Successfully refreshed April API token")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh April API token: {str(e)}")
            raise
    
    def _record_transaction(self, user_id: int, transaction_type: str, endpoint: str,
                           request_data: Dict, response_data: Dict, status_code: int,
                           successful: bool) -> None:
        """Record API transaction for audit and debugging"""
        transaction = AprilTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            endpoint=endpoint,
            request_data=request_data,
            response_data=response_data,
            status_code=status_code,
            successful=successful
        )
        
        try:
            db.session.add(transaction)
            db.session.commit()
            logger.debug(f"Recorded April API transaction: {transaction_type}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record April API transaction: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, user_id: int, transaction_type: str,
                     data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to April API with retry logic and transaction recording"""
        url = f"{self.config.API_URL}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                if method.lower() == 'get':
                    response = requests.get(url, headers=headers, params=params,
                                          timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT))
                elif method.lower() == 'post':
                    response = requests.post(url, headers=headers, json=data,
                                           timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT))
                elif method.lower() == 'put':
                    response = requests.put(url, headers=headers, json=data,
                                          timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT))
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                response_data = response.json()
                
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=data or params or {},
                    response_data=response_data,
                    status_code=response.status_code,
                    successful=True
                )
                
                return response_data
            
            except requests.exceptions.RequestException as e:
                response_data = {}
                status_code = 500
                
                if hasattr(e, 'response') and e.response:
                    try:
                        response_data = e.response.json()
                    except ValueError:
                        response_data = {'error': str(e)}
                    
                    status_code = e.response.status_code
                
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=data or params or {},
                    response_data=response_data,
                    status_code=status_code,
                    successful=False
                )
                
                # Retry only for certain status codes
                if status_code in [429, 500, 502, 503, 504] and attempt < self.config.MAX_RETRIES - 1:
                    retry_after = min(self.config.RETRY_BACKOFF * (2 ** attempt), 30)
                    logger.warning(f"Retrying request after {retry_after}s due to error: {str(e)}")
                    time.sleep(retry_after)
                    continue
                
                logger.error(f"April API request failed: {str(e)}")
                raise
    
    def submit_tax_documents(self, user_id: int, tax_year: int, documents: Dict[str, Any]) -> Dict[str, Any]:
        """Submit tax documents to April's Filer service"""
        endpoint = f"{self.config.FILER_ENDPOINT}/{tax_year}"
        
        return self._make_request(
            method='post',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='tax_document_submission',
            data={
                'tax_year': tax_year,
                'documents': documents
            }
        )
    
    def get_tax_filing_status(self, user_id: int, filing_id: str) -> Dict[str, Any]:
        """Get status of a tax filing"""
        endpoint = f"{self.config.FILER_ENDPOINT}/status/{filing_id}"
        
        return self._make_request(
            method='get',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='tax_filing_status'
        )
    
    def create_financial_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a financial profile in April's Estimator service"""
        endpoint = self.config.ESTIMATOR_ENDPOINT
        
        return self._make_request(
            method='post',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='create_financial_profile',
            data=profile_data
        )
    
    def get_financial_recommendations(self, user_id: int, profile_id: str) -> Dict[str, Any]:
        """Get financial recommendations based on a profile"""
        endpoint = f"{self.config.ESTIMATOR_ENDPOINT}/{profile_id}/recommendations"
        
        return self._make_request(
            method='get',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='get_financial_recommendations'
        )
    
    def track_product_engagement(self, user_id: int, product_id: str, 
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Track product engagement in April's Optimizer service"""
        endpoint = f"{self.config.OPTIMIZER_ENDPOINT}/{product_id}"
        
        return self._make_request(
            method='post',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='track_product_engagement',
            data=data
        )
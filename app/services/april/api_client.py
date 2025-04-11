import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, Timeout
from app.services.april.config import AprilConfig
from app import db
from app.services.april.models import AprilTransaction

logger = logging.getLogger(__name__)

class AprilAPIClient:
    """Client for interacting with the April API"""
    
    def __init__(self):
        self.config = AprilConfig
        self.base_url = self.config.API_URL
        self.client_id = self.config.CLIENT_ID
        self.client_secret = self.config.CLIENT_SECRET
        self.access_token = None
        self.token_expiry = None
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication token"""
        if not self.access_token or self._token_expired():
            self._refresh_token()
            
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _token_expired(self) -> bool:
        """Check if the current token has expired"""
        if not self.token_expiry:
            return True
        return datetime.utcnow() >= self.token_expiry
    
    def _refresh_token(self) -> None:
        """Obtain a new access token"""
        auth_url = f"{self.base_url}{self.config.AUTH_ENDPOINT}"
        
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(
                auth_url,
                data=payload,
                timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT)
            )
            response.raise_for_status()
            
            auth_data = response.json()
            self.access_token = auth_data['access_token']
            expires_in = auth_data['expires_in']
            self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # Buffer of 60 seconds
            
            logger.info("Successfully refreshed April API token")
        except (RequestException, KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to refresh API token: {str(e)}")
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
        
        db.session.add(transaction)
        db.session.commit()
        
    def _make_request(self, method: str, endpoint: str, user_id: int, transaction_type: str,
                     data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to April API with retry logic and transaction recording"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        request_data = {
            'data': data,
            'params': params
        }
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                if method.lower() == 'get':
                    response = requests.get(
                        url, 
                        headers=headers, 
                        params=params,
                        timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT)
                    )
                else:
                    response = requests.post(
                        url, 
                        headers=headers, 
                        json=data,
                        timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT)
                    )
                
                response.raise_for_status()
                response_data = response.json()
                
                # Record successful transaction
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=request_data,
                    response_data=response_data,
                    status_code=response.status_code,
                    successful=True
                )
                
                return response_data
                
            except (RequestException, json.JSONDecodeError) as e:
                logger.warning(f"API request failed (attempt {attempt+1}/{self.config.MAX_RETRIES}): {str(e)}")
                
                # Record failed transaction
                response_data = {}
                status_code = 500
                
                if isinstance(e, RequestException) and hasattr(e, 'response') and e.response is not None:
                    try:
                        response_data = e.response.json()
                    except json.JSONDecodeError:
                        response_data = {'error': e.response.text}
                    status_code = e.response.status_code
                
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=request_data,
                    response_data=response_data,
                    status_code=status_code,
                    successful=False
                )
                
                # If final attempt, raise the exception
                if attempt == self.config.MAX_RETRIES - 1:
                    raise
        
        # This should not be reached
        raise Exception("Failed to make API request after retries")
    
    # Tax filing endpoints
    def submit_tax_documents(self, user_id: int, tax_year: int, documents: Dict[str, Any]) -> Dict[str, Any]:
        """Submit tax documents to April's Filer service"""
        endpoint = self.config.FILER_ENDPOINT
        data = {
            'user_id': str(user_id),
            'tax_year': tax_year,
            'documents': documents
        }
        
        return self._make_request('post', endpoint, user_id, 'submit_tax_documents', data)
    
    def get_tax_filing_status(self, user_id: int, filing_id: str) -> Dict[str, Any]:
        """Get status of a tax filing"""
        endpoint = f"{self.config.FILER_ENDPOINT}/{filing_id}"
        
        return self._make_request('get', endpoint, user_id, 'get_tax_filing_status')
    
    # Financial profile endpoints
    def create_financial_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a financial profile in April's Estimator service"""
        endpoint = self.config.ESTIMATOR_ENDPOINT
        data = {
            'user_id': str(user_id),
            **profile_data
        }
        
        return self._make_request('post', endpoint, user_id, 'create_financial_profile', data)
    
    def get_financial_recommendations(self, user_id: int, profile_id: str) -> Dict[str, Any]:
        """Get financial recommendations based on a profile"""
        endpoint = f"{self.config.ESTIMATOR_ENDPOINT}/{profile_id}/recommendations"
        
        return self._make_request('get', endpoint, user_id, 'get_financial_recommendations')
    
    # Product engagement endpoints
    def track_product_engagement(self, user_id: int, product_id: str, 
                                data: Dict[str, Any]) -> Dict[str, Any]:
        """Track product engagement in April's Optimizer service"""
        endpoint = self.config.OPTIMIZER_ENDPOINT
        payload = {
            'user_id': str(user_id),
            'product_id': product_id,
            'interaction_data': data
        }
        
        return self._make_request('post', endpoint, user_id, 'track_product_engagement', payload)

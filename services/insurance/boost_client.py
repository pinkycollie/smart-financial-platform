import os
import time
import requests
from typing import Dict, List, Any, Optional

from services.insurance.config import BoostConfig
from models import InsuranceProduct, InsurancePolicy, User, db

# Constants for deaf/hard of hearing specific insurance considerations
DEAF_SPECIFIC_COVERAGES = {
    'signaling_device': 'Coverage for visual alerting devices (doorbells, smoke detectors, etc.)',
    'interpreter_services': 'Coverage for sign language interpreter services',
    'communication_devices': 'Coverage for specialized communication technology',
    'service_animals': 'Coverage for service animals trained to assist deaf individuals'
}


class BoostAPIClient:
    """Client for interacting with the Boost Insurance API"""
    
    def __init__(self):
        """Initialize Boost Insurance API client"""
        self.config = BoostConfig()
        self.token = None
        self.token_expiry = 0
    
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
        return self.token is None or time.time() >= self.token_expiry
    
    def _refresh_token(self) -> None:
        """Obtain a new access token"""
        if not self.config.CLIENT_ID or not self.config.CLIENT_SECRET:
            raise ValueError("Boost API credentials not configured")
        
        data = {
            'client_id': self.config.CLIENT_ID,
            'client_secret': self.config.CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(
                f"{self.config.API_URL}{self.config.AUTH_ENDPOINT}",
                json=data,
                timeout=(self.config.CONNECT_TIMEOUT, self.config.READ_TIMEOUT)
            )
            response.raise_for_status()
            response_data = response.json()
            
            self.token = response_data.get('access_token')
            # Set token expiry with a small buffer
            expires_in = response_data.get('expires_in', 3600)
            self.token_expiry = time.time() + expires_in - 60
            
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing Boost API token: {str(e)}")
            raise
    
    def _record_transaction(self, user_id: int, transaction_type: str, endpoint: str,
                           request_data: Dict, response_data: Dict, status_code: int,
                           successful: bool) -> None:
        """Record API transaction for audit and debugging"""
        # This would normally create a record in a BoostTransaction table
        # For now, we just log it
        print(f"Boost API Transaction: {transaction_type} to {endpoint}, Status: {status_code}, Success: {successful}")
    
    def _make_request(self, method: str, endpoint: str, user_id: int, transaction_type: str,
                     data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Boost API with retry logic and transaction recording"""
        url = f"{self.config.API_URL}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(1, self.config.MAX_RETRIES + 1):
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
                
                # Record successful transaction
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=data or {},
                    response_data=response_data,
                    status_code=response.status_code,
                    successful=True
                )
                
                return response_data
                
            except requests.exceptions.RequestException as e:
                # Record failed transaction
                response_data = {}
                status_code = -1
                
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    try:
                        response_data = e.response.json()
                    except:
                        response_data = {'error': str(e)}
                
                self._record_transaction(
                    user_id=user_id,
                    transaction_type=transaction_type,
                    endpoint=endpoint,
                    request_data=data or {},
                    response_data=response_data,
                    status_code=status_code,
                    successful=False
                )
                
                if attempt < self.config.MAX_RETRIES:
                    # Exponential backoff
                    backoff_time = self.config.RETRY_BACKOFF * (2 ** (attempt - 1))
                    time.sleep(backoff_time)
                    continue
                else:
                    raise
    
    def get_available_products(self, user_id: int) -> List[Dict[str, Any]]:
        """Get available insurance products from Boost"""
        response = self._make_request(
            method='get',
            endpoint=self.config.PRODUCTS_ENDPOINT,
            user_id=user_id,
            transaction_type='get_products'
        )
        return response.get('products', [])
    
    def get_insurance_quote(self, user_id: int, product_code: str, 
                           coverage_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get an insurance quote for a specific product"""
        data = {
            'product_code': product_code,
            'coverage_parameters': coverage_params
        }
        
        response = self._make_request(
            method='post',
            endpoint=self.config.QUOTE_ENDPOINT,
            user_id=user_id,
            transaction_type='get_quote',
            data=data
        )
        return response
    
    def purchase_policy(self, user_id: int, quote_id: str, 
                       policyholder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Purchase an insurance policy based on a quote"""
        data = {
            'quote_id': quote_id,
            'policyholder': policyholder_data
        }
        
        response = self._make_request(
            method='post',
            endpoint=self.config.POLICY_ENDPOINT,
            user_id=user_id,
            transaction_type='purchase_policy',
            data=data
        )
        return response
    
    def get_policy_details(self, user_id: int, policy_id: str) -> Dict[str, Any]:
        """Get details for a specific policy"""
        endpoint = f"{self.config.POLICY_ENDPOINT}/{policy_id}"
        
        response = self._make_request(
            method='get',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='get_policy_details'
        )
        return response
    
    def file_insurance_claim(self, user_id: int, policy_id: str, 
                            claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """File an insurance claim for a policy"""
        data = {
            'policy_id': policy_id,
            'claim_data': claim_data
        }
        
        response = self._make_request(
            method='post',
            endpoint=self.config.CLAIMS_ENDPOINT,
            user_id=user_id,
            transaction_type='file_claim',
            data=data
        )
        return response
    
    def get_claim_status(self, user_id: int, claim_id: str) -> Dict[str, Any]:
        """Get status of an insurance claim"""
        endpoint = f"{self.config.CLAIMS_ENDPOINT}/{claim_id}"
        
        response = self._make_request(
            method='get',
            endpoint=endpoint,
            user_id=user_id,
            transaction_type='get_claim_status'
        )
        return response
        
    # Specialized methods for deaf and hard of hearing insurance needs
    
    def get_deaf_accessibility_coverages(self) -> Dict[str, str]:
        """Get specialized coverages available for deaf and hard of hearing users"""
        return DEAF_SPECIFIC_COVERAGES
    
    def enhance_quote_with_deaf_coverages(self, user_id: int, quote_id: str, 
                                         selected_coverages: List[str]) -> Dict[str, Any]:
        """Add deaf-specific coverages to an existing quote"""
        # In a real implementation, this would call the Boost API to modify the quote
        # For now, we'll simulate the API call
        
        coverage_data = {
            'quote_id': quote_id,
            'additional_coverages': [
                {
                    'coverage_code': coverage,
                    'is_selected': True
                } for coverage in selected_coverages if coverage in DEAF_SPECIFIC_COVERAGES
            ]
        }
        
        # This would be a real API call in production
        response = self._make_request(
            method='put',
            endpoint=f"{self.config.QUOTE_ENDPOINT}/{quote_id}/coverages",
            user_id=user_id,
            transaction_type='add_deaf_coverages',
            data=coverage_data
        )
        return response
    
    def seed_insurance_products_for_deaf_users(self) -> None:
        """Seed the database with insurance products relevant to deaf and hard of hearing users"""
        # Check if we've already seeded products
        if InsuranceProduct.query.filter_by(is_deaf_specialized=True).count() > 0:
            return
            
        # This would normally come from the Boost API, but we're seeding for demonstration
        deaf_specialized_products = [
            {
                'product_code': 'DEAF-HOME',
                'name': 'Home Insurance for Deaf Community',
                'description': 'Specialized home insurance with coverage for visual alert systems and communication devices.',
                'coverage_type': 'home',
                'minimum_premium': 600.00,
                'maximum_coverage': 500000.00,
                'is_deaf_specialized': True,
                'deaf_accessibility_features': {
                    'visual_alerts': True,
                    'interpreter_coverage': True,
                    'communication_device_coverage': True
                }
            },
            {
                'product_code': 'DEAF-AUTO',
                'name': 'Auto Insurance for Deaf Drivers',
                'description': 'Auto insurance with specialized features for deaf and hard of hearing drivers.',
                'coverage_type': 'auto',
                'minimum_premium': 750.00,
                'maximum_coverage': 300000.00,
                'is_deaf_specialized': True,
                'deaf_accessibility_features': {
                    'specialized_driver_discounts': True,
                    'visual_alert_system_coverage': True
                }
            },
            {
                'product_code': 'DEAF-HEALTH',
                'name': 'Supplemental Health Coverage for Deaf Individuals',
                'description': 'Supplemental health coverage specifically designed for deaf and hard of hearing individuals.',
                'coverage_type': 'health',
                'minimum_premium': 85.00,
                'maximum_coverage': 50000.00,
                'is_deaf_specialized': True,
                'deaf_accessibility_features': {
                    'interpreter_services': True,
                    'specialized_medical_device_coverage': True,
                    'service_animal_coverage': True
                }
            }
        ]
        
        # Add products to database
        for product_data in deaf_specialized_products:
            product = InsuranceProduct(
                product_code=product_data['product_code'],
                name=product_data['name'],
                description=product_data['description'],
                coverage_type=product_data['coverage_type'],
                minimum_premium=product_data['minimum_premium'],
                maximum_coverage=product_data['maximum_coverage'],
                active=True,
                is_deaf_specialized=product_data['is_deaf_specialized'],
                accessibility_features=product_data['deaf_accessibility_features']
            )
            db.session.add(product)
        
        db.session.commit()
"""
Open Insurance API Integration for DEAF FIRST Platform
Provides standardized insurance data access and policy management
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class OpenInsuranceClient:
    """Client for Open Insurance API integration"""
    
    def __init__(self):
        self.base_url = os.environ.get('OPEN_INSURANCE_URL', 'http://localhost:8081')
        self.api_key = os.environ.get('OPEN_INSURANCE_API_KEY')
        self.session = requests.Session()
        
        if not self.api_key:
            logger.warning("Open Insurance API key not configured. Using demo mode.")
        else:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    # Insurance Entity Management
    def create_insurance_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new insurance entity"""
        try:
            response = self.session.post(f'{self.base_url}/insurance-entity', json=entity_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'entity_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'Insurance entity created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity creation failed'}
    
    def get_insurance_entity(self, entity_id: str) -> Dict[str, Any]:
        """Retrieve insurance entity by ID"""
        try:
            response = self.session.get(f'{self.base_url}/insurance-entity/{entity_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity retrieval failed'}
    
    def update_insurance_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update insurance entity"""
        try:
            response = self.session.put(f'{self.base_url}/insurance-entity/{entity_id}', json=entity_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'Insurance entity updated successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Update insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity update failed'}
    
    def delete_insurance_entity(self, entity_id: str) -> Dict[str, Any]:
        """Delete insurance entity"""
        try:
            response = self.session.delete(f'{self.base_url}/insurance-entity/{entity_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'Insurance entity deleted successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity deletion failed'}
    
    # Policy Management
    def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new insurance policy"""
        try:
            response = self.session.post(f'{self.base_url}/policies', json=policy_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'policy_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'Policy created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create policy failed: {e}")
            return {'status': 'error', 'message': 'Policy creation failed'}
    
    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Retrieve policy by ID"""
        try:
            response = self.session.get(f'{self.base_url}/policies/{policy_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get policy failed: {e}")
            return {'status': 'error', 'message': 'Policy retrieval failed'}
    
    def update_policy(self, policy_id: str, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update insurance policy"""
        try:
            response = self.session.put(f'{self.base_url}/policies/{policy_id}', json=policy_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'Policy updated successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Update policy failed: {e}")
            return {'status': 'error', 'message': 'Policy update failed'}
    
    def list_policies(self, customer_id: str = None, status: str = None) -> Dict[str, Any]:
        """List policies with optional filters"""
        try:
            params = {}
            if customer_id:
                params['customer_id'] = customer_id
            if status:
                params['status'] = status
            
            response = self.session.get(f'{self.base_url}/policies', params=params)
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"List policies failed: {e}")
            return {'status': 'error', 'message': 'Policy listing failed'}
    
    # Product Management
    def get_products(self, product_type: str = None) -> Dict[str, Any]:
        """Get available insurance products"""
        try:
            params = {}
            if product_type:
                params['type'] = product_type
            
            response = self.session.get(f'{self.base_url}/products', params=params)
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get products failed: {e}")
            return {'status': 'error', 'message': 'Product retrieval failed'}
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed product information"""
        try:
            response = self.session.get(f'{self.base_url}/products/{product_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get product details failed: {e}")
            return {'status': 'error', 'message': 'Product details retrieval failed'}
    
    # Claims Management
    def create_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new insurance claim"""
        try:
            response = self.session.post(f'{self.base_url}/claims', json=claim_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'claim_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'Claim created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create claim failed: {e}")
            return {'status': 'error', 'message': 'Claim creation failed'}
    
    def get_claim(self, claim_id: str) -> Dict[str, Any]:
        """Retrieve claim by ID"""
        try:
            response = self.session.get(f'{self.base_url}/claims/{claim_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get claim failed: {e}")
            return {'status': 'error', 'message': 'Claim retrieval failed'}
    
    def update_claim_status(self, claim_id: str, status: str, notes: str = None) -> Dict[str, Any]:
        """Update claim status"""
        try:
            update_data = {'status': status}
            if notes:
                update_data['notes'] = notes
            
            response = self.session.patch(f'{self.base_url}/claims/{claim_id}', json=update_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'Claim status updated successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Update claim status failed: {e}")
            return {'status': 'error', 'message': 'Claim status update failed'}
    
    def list_claims(self, policy_id: str = None, status: str = None) -> Dict[str, Any]:
        """List claims with optional filters"""
        try:
            params = {}
            if policy_id:
                params['policy_id'] = policy_id
            if status:
                params['status'] = status
            
            response = self.session.get(f'{self.base_url}/claims', params=params)
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"List claims failed: {e}")
            return {'status': 'error', 'message': 'Claims listing failed'}
    
    # Customer Management
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer record"""
        try:
            response = self.session.post(f'{self.base_url}/customers', json=customer_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'customer_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'Customer created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create customer failed: {e}")
            return {'status': 'error', 'message': 'Customer creation failed'}
    
    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer by ID"""
        try:
            response = self.session.get(f'{self.base_url}/customers/{customer_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get customer failed: {e}")
            return {'status': 'error', 'message': 'Customer retrieval failed'}
    
    def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update customer information"""
        try:
            response = self.session.put(f'{self.base_url}/customers/{customer_id}', json=customer_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'Customer updated successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Update customer failed: {e}")
            return {'status': 'error', 'message': 'Customer update failed'}
    
    # DEAF FIRST Specialized Methods
    def get_deaf_specialized_products(self) -> Dict[str, Any]:
        """Get insurance products specialized for deaf community"""
        try:
            # Filter products for deaf-specific features
            products_response = self.get_products()
            if products_response['status'] == 'error':
                return products_response
            
            deaf_products = []
            for product in products_response.get('data', []):
                # Look for deaf-specific indicators
                if any(keyword in str(product).lower() for keyword in 
                      ['deaf', 'hearing', 'accessibility', 'communication', 'interpreter']):
                    deaf_products.append(product)
            
            return {
                'status': 'success',
                'data': deaf_products,
                'total_count': len(deaf_products),
                'specialized_features': [
                    'ASL interpreter coverage',
                    'Assistive technology coverage',
                    'Communication device protection',
                    'Accessibility modification coverage'
                ]
            }
        except Exception as e:
            logger.error(f"Get deaf specialized products failed: {e}")
            return {'status': 'error', 'message': 'Specialized products retrieval failed'}
    
    def create_deaf_customer_profile(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create customer profile with deaf-specific accessibility needs"""
        try:
            # Enhance customer data with deaf-specific fields
            enhanced_data = {
                **customer_data,
                'accessibility_needs': {
                    'communication_method': customer_data.get('communication_method', 'asl'),
                    'interpreter_required': customer_data.get('interpreter_required', True),
                    'text_communication_preferred': customer_data.get('text_preferred', True),
                    'video_relay_service': customer_data.get('vrs_number'),
                    'assistive_devices': customer_data.get('assistive_devices', [])
                },
                'special_requirements': {
                    'asl_support': True,
                    'visual_alerts': True,
                    'written_documentation': True
                }
            }
            
            return self.create_customer(enhanced_data)
        except Exception as e:
            logger.error(f"Create deaf customer profile failed: {e}")
            return {'status': 'error', 'message': 'Deaf customer profile creation failed'}
    
    def get_accessibility_coverage_options(self, customer_id: str) -> Dict[str, Any]:
        """Get coverage options for accessibility needs"""
        try:
            coverage_options = {
                'assistive_technology': {
                    'description': 'Coverage for hearing aids, cochlear implants, and assistive devices',
                    'coverage_limit': '$10,000 annually',
                    'deductible': '$250',
                    'premium_addition': '$15/month'
                },
                'interpreter_services': {
                    'description': 'ASL interpreter services for medical and legal appointments',
                    'coverage_limit': '100 hours annually',
                    'no_deductible': True,
                    'premium_addition': '$25/month'
                },
                'communication_devices': {
                    'description': 'Smartphones, tablets, and communication apps',
                    'coverage_limit': '$5,000 annually',
                    'deductible': '$100',
                    'premium_addition': '$10/month'
                },
                'home_modifications': {
                    'description': 'Visual alert systems and accessibility modifications',
                    'coverage_limit': '$15,000 one-time',
                    'deductible': '$500',
                    'premium_addition': '$20/month'
                }
            }
            
            return {
                'status': 'success',
                'customer_id': customer_id,
                'accessibility_options': coverage_options,
                'total_monthly_premium_addition': '$70',
                'asl_explanation_available': True
            }
        except Exception as e:
            logger.error(f"Get accessibility coverage options failed: {e}")
            return {'status': 'error', 'message': 'Accessibility coverage options retrieval failed'}
    
    def calculate_deaf_premium_discount(self, base_premium: float, deaf_specific_features: List[str]) -> Dict[str, Any]:
        """Calculate premium discounts for deaf-specific safety features"""
        try:
            discount_factors = {
                'visual_smoke_detectors': 0.05,  # 5% discount
                'vibrating_alarm_systems': 0.03,  # 3% discount
                'security_monitoring_with_visual_alerts': 0.07,  # 7% discount
                'emergency_text_alert_system': 0.02,  # 2% discount
                'deaf_friendly_neighborhood': 0.04  # 4% discount
            }
            
            total_discount = 0
            applied_discounts = []
            
            for feature in deaf_specific_features:
                if feature in discount_factors:
                    discount = discount_factors[feature]
                    total_discount += discount
                    applied_discounts.append({
                        'feature': feature,
                        'discount_rate': discount,
                        'discount_amount': base_premium * discount
                    })
            
            # Cap total discount at 15%
            total_discount = min(total_discount, 0.15)
            final_premium = base_premium * (1 - total_discount)
            
            return {
                'status': 'success',
                'base_premium': base_premium,
                'total_discount_rate': total_discount,
                'total_discount_amount': base_premium * total_discount,
                'final_premium': final_premium,
                'applied_discounts': applied_discounts,
                'savings_annual': (base_premium * total_discount) * 12
            }
        except Exception as e:
            logger.error(f"Calculate deaf premium discount failed: {e}")
            return {'status': 'error', 'message': 'Premium discount calculation failed'}


# Global client instance
open_insurance_client = OpenInsuranceClient()
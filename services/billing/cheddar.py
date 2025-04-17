"""
Cheddar billing API integration for DEAF FIRST platform.
Handles subscription billing for resellers and licensees.
Based on: https://github.com/Tive-technology/node-cheddar-api
"""

import os
import json
import requests
import logging
import base64
import hmac
import hashlib
from datetime import datetime
from urllib.parse import urlencode

# Configure logging
logger = logging.getLogger(__name__)

class CheddarClient:
    """
    Client for Cheddar Billing API.
    Handles subscription management, billing, and payment processing.
    """
    
    def __init__(self, username=None, password=None, product_code=None, product_id=None):
        """Initialize Cheddar client with API credentials"""
        self.username = username or os.environ.get('CHEDDAR_USERNAME')
        self.password = password or os.environ.get('CHEDDAR_PASSWORD')
        self.product_code = product_code or os.environ.get('CHEDDAR_PRODUCT_CODE')
        self.product_id = product_id or os.environ.get('CHEDDAR_PRODUCT_ID')
        
        if not all([self.username, self.password, self.product_code]):
            logger.warning("Cheddar API credentials not fully configured. Some billing features may be limited.")
        
        # Base API URL
        self.base_url = 'https://api.getcheddar.com'
        
        # Auth header
        self._auth = None
        if self.username and self.password:
            self._auth = (self.username, self.password)
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make a request to the Cheddar API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Encode data as application/x-www-form-urlencoded
        encoded_data = urlencode(data) if data else None
        
        try:
            response = requests.request(
                method,
                url,
                params=params,
                data=encoded_data,
                headers=headers,
                auth=self._auth
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Return JSON response
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Cheddar API: {e}")
            
            # If response exists, try to get error details
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_code = error_data.get('code', 'unknown_error')
                    error_message = error_data.get('message', 'Unknown error')
                    raise CheddarAPIError(error_code, error_message, e.response.status_code)
                except (ValueError, json.JSONDecodeError):
                    # If JSON parsing fails, use the response text
                    pass
            
            # Generic error
            raise CheddarAPIError('api_error', str(e), 500 if not hasattr(e, 'response') else e.response.status_code)
    
    # Customer methods
    def get_customer(self, code):
        """
        Get a customer by customer code.
        
        Args:
            code (str): Customer code
            
        Returns:
            dict: Customer data
        """
        endpoint = f"/v1/customers/get/productCode/{self.product_code}/code/{code}"
        return self._make_request('GET', endpoint)
    
    def create_customer(self, code, first_name, last_name, email, plan_code, **kwargs):
        """
        Create a new customer with subscription.
        
        Args:
            code (str): Unique customer code
            first_name (str): Customer first name
            last_name (str): Customer last name
            email (str): Customer email
            plan_code (str): Subscription plan code
            **kwargs: Additional customer properties
            
        Returns:
            dict: Created customer data
        """
        data = {
            'code': code,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'planCode': plan_code
        }
        
        # Add optional fields
        for key, value in kwargs.items():
            # Convert snake_case to camelCase
            camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
            data[camel_key] = value
        
        endpoint = f"/v1/customers/new/productCode/{self.product_code}"
        return self._make_request('POST', endpoint, data=data)
    
    def update_customer(self, code, **kwargs):
        """
        Update a customer.
        
        Args:
            code (str): Customer code
            **kwargs: Properties to update
            
        Returns:
            dict: Updated customer data
        """
        data = {}
        
        # Add update fields
        for key, value in kwargs.items():
            # Convert snake_case to camelCase
            camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
            data[camel_key] = value
        
        endpoint = f"/v1/customers/edit/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint, data=data)
    
    def delete_customer(self, code):
        """
        Delete a customer.
        
        Args:
            code (str): Customer code
            
        Returns:
            dict: Response data
        """
        endpoint = f"/v1/customers/delete/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint)
    
    # Subscription methods
    def update_subscription(self, code, plan_code, **kwargs):
        """
        Update a customer's subscription.
        
        Args:
            code (str): Customer code
            plan_code (str): New plan code
            **kwargs: Additional subscription properties
            
        Returns:
            dict: Updated subscription data
        """
        data = {
            'planCode': plan_code
        }
        
        # Add optional fields
        for key, value in kwargs.items():
            # Convert snake_case to camelCase
            camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
            data[camel_key] = value
        
        endpoint = f"/v1/customers/edit-subscription/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint, data=data)
    
    def cancel_subscription(self, code, cancel_reason=None):
        """
        Cancel a customer's subscription.
        
        Args:
            code (str): Customer code
            cancel_reason (str, optional): Reason for cancellation
            
        Returns:
            dict: Cancellation response
        """
        data = {}
        if cancel_reason:
            data['cancelReason'] = cancel_reason
        
        endpoint = f"/v1/customers/cancel/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint, data=data)
    
    # Plans methods
    def get_plans(self):
        """
        Get all subscription plans.
        
        Returns:
            list: Available plans
        """
        endpoint = f"/v1/plans/get/productCode/{self.product_code}"
        return self._make_request('GET', endpoint)
    
    def get_plan(self, code):
        """
        Get a specific plan by code.
        
        Args:
            code (str): Plan code
            
        Returns:
            dict: Plan data
        """
        endpoint = f"/v1/plans/get/productCode/{self.product_code}/code/{code}"
        return self._make_request('GET', endpoint)
    
    # Invoice methods
    def get_invoices(self, code):
        """
        Get invoices for a customer.
        
        Args:
            code (str): Customer code
            
        Returns:
            list: Customer invoices
        """
        endpoint = f"/v1/customers/invoices/productCode/{self.product_code}/code/{code}"
        return self._make_request('GET', endpoint)
    
    def get_invoice(self, invoice_id):
        """
        Get a specific invoice.
        
        Args:
            invoice_id (str): Invoice ID
            
        Returns:
            dict: Invoice data
        """
        endpoint = f"/v1/invoices/get/id/{invoice_id}"
        return self._make_request('GET', endpoint)
    
    # Promotions methods
    def add_promotion(self, code, promotion_code):
        """
        Add a promotion code to a customer.
        
        Args:
            code (str): Customer code
            promotion_code (str): Promotion code
            
        Returns:
            dict: Response data
        """
        data = {
            'promotionCode': promotion_code
        }
        
        endpoint = f"/v1/customers/add-item/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint, data=data)
    
    def remove_promotion(self, code, promotion_code):
        """
        Remove a promotion code from a customer.
        
        Args:
            code (str): Customer code
            promotion_code (str): Promotion code
            
        Returns:
            dict: Response data
        """
        data = {
            'promotionCode': promotion_code
        }
        
        endpoint = f"/v1/customers/delete-item/productCode/{self.product_code}/code/{code}"
        return self._make_request('POST', endpoint, data=data)
    
    # Webhook validation
    def validate_webhook(self, webhook_data, signature):
        """
        Validate a webhook request from Cheddar.
        
        Args:
            webhook_data (str): Raw webhook payload
            signature (str): Webhook signature from X-CG-SIGN header
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.password:
            logger.warning("Cannot validate webhook without API password")
            return False
        
        # Create HMAC signature
        expected_signature = base64.b64encode(
            hmac.new(
                self.password.encode('utf-8'),
                webhook_data.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)
    
    # Analytics methods
    def get_revenue_metrics(self, start_date=None, end_date=None):
        """
        Get revenue metrics for your product.
        
        Args:
            start_date (str, optional): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
            
        Returns:
            dict: Revenue metrics
        """
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        endpoint = f"/v1/analytics/revenue-metrics/productCode/{self.product_code}"
        return self._make_request('GET', endpoint, params=params)
    
    def get_customer_metrics(self, start_date=None, end_date=None):
        """
        Get customer metrics for your product.
        
        Args:
            start_date (str, optional): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
            
        Returns:
            dict: Customer metrics
        """
        params = {}
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        endpoint = f"/v1/analytics/customer-metrics/productCode/{self.product_code}"
        return self._make_request('GET', endpoint, params=params)

class CheddarAPIError(Exception):
    """Exception raised for Cheddar API errors"""
    
    def __init__(self, code, message, status_code=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"Cheddar API Error ({code}): {message}")

# Initialize a single instance to be used application-wide
cheddar_client = CheddarClient()
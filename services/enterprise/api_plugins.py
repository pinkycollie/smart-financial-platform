"""
API Connector Plugins
Pluggable API connectors for enterprise integration
"""
from typing import Dict, Any, Optional
import logging
import requests
from services.enterprise.plugin_registry import PluginInterface, PluginType

logger = logging.getLogger(__name__)


class APIConnectorPlugin(PluginInterface):
    """Base class for API connector plugins"""
    
    plugin_type = PluginType.API_CONNECTOR.value
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key', '')
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
    
    def initialize(self) -> bool:
        """Initialize API connection"""
        if not self.base_url:
            logger.error(f"No base_url configured for {self.name}")
            return False
        return True
    
    def validate_config(self) -> bool:
        """Validate API connector configuration"""
        return bool(self.base_url)
    
    def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make HTTP request to the API"""
        try:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            headers = self.headers.copy()
            
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.RequestException as e:
            logger.error(f"API request failed for {self.name}: {str(e)}")
            return None
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute API call"""
        method = kwargs.get('method', 'GET')
        endpoint = kwargs.get('endpoint', '')
        data = kwargs.get('data')
        params = kwargs.get('params')
        
        return self.make_request(method, endpoint, data, params)


class BloombergAPIPlugin(APIConnectorPlugin):
    """Bloomberg API integration plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        config.setdefault('base_url', 'https://api.bloomberg.com')
        config.setdefault('name', 'bloomberg_api')
        super().__init__(config)
    
    def get_financial_data(self, symbols: list) -> Optional[Dict]:
        """Get financial data for given symbols"""
        return self.execute(
            method='GET',
            endpoint='/market-data/v1/securities',
            params={'symbols': ','.join(symbols)}
        )
    
    def get_terminology(self, term: str) -> Optional[Dict]:
        """Get financial terminology definition"""
        return self.execute(
            method='GET',
            endpoint=f'/terminology/v1/terms/{term}'
        )


class TurboTaxAPIPlugin(APIConnectorPlugin):
    """TurboTax/Intuit API integration plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        config.setdefault('base_url', 'https://api.intuit.com')
        config.setdefault('name', 'turbotax_api')
        super().__init__(config)
    
    def import_tax_data(self, user_id: str) -> Optional[Dict]:
        """Import tax data for user"""
        return self.execute(
            method='GET',
            endpoint=f'/tax/v1/users/{user_id}/data'
        )
    
    def submit_return(self, return_data: Dict) -> Optional[Dict]:
        """Submit tax return"""
        return self.execute(
            method='POST',
            endpoint='/tax/v1/returns',
            data=return_data
        )


class BankAPIPlugin(APIConnectorPlugin):
    """Generic bank API integration plugin"""
    
    def __init__(self, config: Dict[str, Any]):
        config.setdefault('name', 'bank_api')
        super().__init__(config)
        self.bank_name = config.get('bank_name', 'Generic Bank')
    
    def get_accounts(self, customer_id: str) -> Optional[Dict]:
        """Get customer accounts"""
        return self.execute(
            method='GET',
            endpoint=f'/accounts/v1/customers/{customer_id}/accounts'
        )
    
    def get_transactions(
        self, 
        account_id: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict]:
        """Get account transactions"""
        return self.execute(
            method='GET',
            endpoint=f'/transactions/v1/accounts/{account_id}',
            params={'start_date': start_date, 'end_date': end_date}
        )


class CustomEnterpriseAPIPlugin(APIConnectorPlugin):
    """
    Flexible plugin for custom enterprise APIs
    Can be configured for any RESTful API
    """
    
    def __init__(self, config: Dict[str, Any]):
        config.setdefault('name', 'custom_enterprise_api')
        super().__init__(config)
        self.custom_endpoints = config.get('endpoints', {})
    
    def call_endpoint(self, endpoint_name: str, **kwargs) -> Optional[Dict]:
        """Call a custom configured endpoint"""
        endpoint_config = self.custom_endpoints.get(endpoint_name)
        
        if not endpoint_config:
            logger.error(f"Endpoint {endpoint_name} not configured")
            return None
        
        return self.execute(
            method=endpoint_config.get('method', 'GET'),
            endpoint=endpoint_config.get('path', ''),
            data=kwargs.get('data'),
            params=kwargs.get('params')
        )

# Enterprise Integration Guide

## Overview

The MBTQ Smart Financial Platform provides a comprehensive enterprise plugin system designed for seamless integration with large financial institutions, banks, tax services, and insurance companies. This guide covers how to use and extend the pluggable architecture.

## Architecture

### Plugin System

The platform uses a modular plugin architecture that allows enterprises to:

- **Interchangeable Components**: Switch between providers (e.g., Twilio ↔ Zoom) without code changes
- **Custom Integrations**: Add your own plugins for proprietary systems
- **Configuration Management**: Centralized plugin configuration and management
- **API Standardization**: Consistent interfaces across all plugins

### Plugin Types

1. **API Connectors** - Connect to external financial APIs
   - Bloomberg API
   - TurboTax/Intuit API
   - Bank APIs
   - Custom Enterprise APIs

2. **Video Chat** - Embedded video conferencing
   - Twilio Video
   - Zoom
   - Custom video providers

3. **ASL Interpreters** - Accessibility services
   - VSL Labs (AI interpretation)
   - SignASL (live interpreters)
   - PinkSync (full accessibility suite)

4. **Additional Types**
   - UI Components
   - Payment Processors
   - Authentication providers
   - Data Connectors

## Quick Start

### 1. Access the Enterprise Portal

Navigate to `/enterprise` to access the enterprise integration portal.

### 2. Browse Available Plugins

Visit `/enterprise/plugins` to see all available plugins by category.

### 3. Register a Plugin

Example: Register Bloomberg API plugin

```python
from services.enterprise.plugin_registry import enterprise_registry, PluginType
from services.enterprise.api_plugins import BloombergAPIPlugin

enterprise_registry.register_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    BloombergAPIPlugin,
    config={
        'api_key': 'YOUR_BLOOMBERG_API_KEY',
        'base_url': 'https://api.bloomberg.com',
        'enabled': True
    }
)
```

### 4. Use the Plugin

```python
# Execute plugin
result = enterprise_registry.execute_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    method='GET',
    endpoint='/market-data/v1/securities',
    params={'symbols': 'AAPL,GOOGL'}
)
```

## Deployment Templates

Pre-built templates are available for common integration scenarios:

### Video Chat Integration Template

Provides complete video conferencing with ASL interpreter embedding:

```html
<!-- Twilio Video Integration -->
<div id="video-container"></div>
<script src="twilio-video.js"></script>
<script>
  const room = await Twilio.Video.connect(token, {
    name: 'financial-consultation',
    audio: true,
    video: true
  });
</script>

<!-- Embedded ASL Interpreter -->
<div id="vsl-interpreter">
  <iframe src="https://vsl.labs/embed/session-id"></iframe>
</div>
```

### ASL Interpreter Embedding Template

Embed interpreters directly in your interface:

```html
<!-- VSL Labs Integration -->
<script src="https://vsl.labs/widget.js"></script>
<script>
  VSLWidget.init({
    apiKey: 'YOUR_API_KEY',
    containerId: 'vsl-container',
    mode: 'interpreter'
  });
</script>

<!-- PinkSync Full Suite -->
<script src="https://pinksync.com/widget.js"></script>
<script>
  PinkSync.init({
    apiKey: 'YOUR_API_KEY',
    services: ['interpreter', 'gloss', 'captions']
  });
</script>
```

### Gloss ASL Conversion

Convert complex financial terminology to accessible gloss ASL:

```python
from services.enterprise.video_plugins import PinkSyncInterpreterPlugin

plugin = PinkSyncInterpreterPlugin(config={
    'api_key': 'YOUR_API_KEY',
    'subscription_tier': 'professional'
})

result = plugin.convert_to_gloss_asl(
    "The compound interest on your investment portfolio will be calculated quarterly..."
)

# Result includes:
# - gloss_asl: Simplified ASL gloss text
# - video_url: Generated ASL video explanation
```

## Creating Custom Plugins

### 1. Inherit from PluginInterface

```python
from services.enterprise.plugin_registry import PluginInterface, PluginType

class MyCustomPlugin(PluginInterface):
    plugin_type = PluginType.API_CONNECTOR.value
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = config.get('api_url')
    
    def initialize(self):
        """Initialize your plugin"""
        return bool(self.api_url)
    
    def execute(self, *args, **kwargs):
        """Execute plugin functionality"""
        # Your implementation here
        pass
    
    def validate_config(self):
        """Validate configuration"""
        return bool(self.api_url)
```

### 2. Register Your Plugin

```python
enterprise_registry.register_plugin(
    PluginType.API_CONNECTOR,
    'my_custom_plugin',
    MyCustomPlugin,
    config={'api_url': 'https://api.example.com'}
)
```

## PinkSync Partnership

PinkSync provides a complete accessibility solution with automatic deployment.

### Subscription Tiers

- **Basic** ($99/month): ASL interpreters, captions, 10 hours/month
- **Professional** ($299/month): All Basic features + gloss conversion, 50 hours/month
- **Enterprise** (Custom): Unlimited, white-label, SLA guarantees

### Features

- **Automatic Video Chat Setup**: Deploy video conferencing with embedded interpreters
- **Gloss ASL Conversion**: Convert heavy financial context to accessible format
- **Real-time Translation**: AI-powered English ↔ ASL translation
- **24/7 Availability**: Round-the-clock interpreter access

### Integration

```python
from services.enterprise.video_plugins import PinkSyncInterpreterPlugin

pinksync = PinkSyncInterpreterPlugin(config={
    'api_key': 'YOUR_PINKSYNC_KEY',
    'subscription_tier': 'professional'
})

# Request interpreter for appointment
result = pinksync.request_interpreter({
    'session_id': 'abc123',
    'scheduled_time': '2025-12-20T14:00:00Z',
    'duration': 60
})
```

## API Endpoints

The enterprise system provides REST API endpoints:

### List Plugins
```
GET /enterprise/api/plugins?type=api_connector
```

### Execute Plugin
```
POST /enterprise/api/plugin/execute
Content-Type: application/json

{
  "plugin_type": "api_connector",
  "plugin_name": "bloomberg",
  "parameters": {
    "method": "GET",
    "endpoint": "/market-data/v1/securities"
  }
}
```

## Contact & Support

### Enterprise Architecture Team

- **Email**: architect@360magicians.com
- **Email**: architect@mbtq.dev
- **Response Time**: Within 24 hours

### What We Provide

- Technical consultation calls
- Custom integration plans
- Deployment templates
- Ongoing support and monitoring

### Request Integration

Visit `/enterprise/inquiry` or contact the architecture team directly to discuss:

- Custom plugin development
- White-label solutions
- Enterprise deployment
- Integration support
- Training and onboarding

## Examples for Major Companies

### Bloomberg Integration

```python
from services.enterprise.api_plugins import BloombergAPIPlugin

bloomberg = BloombergAPIPlugin(config={
    'api_key': 'YOUR_BLOOMBERG_KEY',
    'base_url': 'https://api.bloomberg.com'
})

# Get financial data
data = bloomberg.get_financial_data(['AAPL', 'GOOGL'])

# Get terminology
term = bloomberg.get_terminology('compound_interest')
```

### TurboTax Integration

```python
from services.enterprise.api_plugins import TurboTaxAPIPlugin

turbotax = TurboTaxAPIPlugin(config={
    'api_key': 'YOUR_INTUIT_KEY',
    'client_id': 'YOUR_CLIENT_ID',
    'client_secret': 'YOUR_CLIENT_SECRET'
})

# Import tax data
tax_data = turbotax.import_tax_data('user_123')

# Submit return
result = turbotax.submit_return(return_data)
```

### Bank API Integration

```python
from services.enterprise.api_plugins import BankAPIPlugin

bank = BankAPIPlugin(config={
    'api_key': 'YOUR_BANK_API_KEY',
    'base_url': 'https://api.yourbank.com',
    'bank_name': 'Your Bank Name'
})

# Get customer accounts
accounts = bank.get_accounts('customer_123')

# Get transactions
transactions = bank.get_transactions(
    'account_456',
    '2024-01-01',
    '2024-12-31'
)
```

## Security

- All plugins support OAuth 2.0 authentication
- API keys are encrypted at rest
- TLS 1.2+ for data in transit
- SOC 2 compliant
- HIPAA ready for health data

## Best Practices

1. **Configuration Management**: Store sensitive credentials in environment variables
2. **Error Handling**: Always handle plugin execution failures gracefully
3. **Testing**: Use the test functionality in the dashboard before production
4. **Monitoring**: Monitor plugin health and API call metrics
5. **Updates**: Keep plugins updated to the latest versions

## Troubleshooting

### Plugin Registration Fails

- Check that the plugin class implements `PluginInterface`
- Verify configuration includes all required fields
- Ensure plugin type is valid

### Plugin Execution Fails

- Verify API credentials are correct
- Check network connectivity
- Review plugin logs for specific errors
- Test the plugin using the dashboard test functionality

### Need Help?

Contact our enterprise team at architect@360magicians.com or architect@mbtq.dev

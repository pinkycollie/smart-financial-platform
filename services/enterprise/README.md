# Enterprise Integration System

## Overview

The MBTQ Smart Financial Platform provides a comprehensive enterprise plugin system designed for seamless integration with large financial institutions, banks, tax services (like TurboTax), data providers (like Bloomberg), and insurance companies.

## Quick Start

### Access the Enterprise Portal

Visit `/enterprise` in your browser to access:
- Integration portal overview
- Available plugins browser
- Configuration dashboard
- Deployment templates
- PinkSync partnership portal
- Enterprise inquiry form

### Register a Plugin

```python
from services.enterprise.plugin_registry import enterprise_registry, PluginType
from services.enterprise.api_plugins import BloombergAPIPlugin

enterprise_registry.register_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    BloombergAPIPlugin,
    config={
        'api_key': 'YOUR_BLOOMBERG_API_KEY',
        'base_url': 'https://api.bloomberg.com'
    }
)
```

### Execute a Plugin

```python
result = enterprise_registry.execute_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    method='GET',
    endpoint='/market-data/v1/securities',
    params={'symbols': 'AAPL,GOOGL'}
)
```

## Available Plugins

### API Connectors
- **BloombergAPIPlugin** - Bloomberg financial data and terminology
- **TurboTaxAPIPlugin** - TurboTax/Intuit tax preparation
- **BankAPIPlugin** - Generic bank API integration
- **CustomEnterpriseAPIPlugin** - Flexible plugin for any RESTful API

### Video Chat
- **TwilioVideoPlugin** - Twilio video conferencing
- **ZoomVideoPlugin** - Zoom meetings integration

### ASL Interpreters
- **VSLLabsInterpreterPlugin** - AI-powered ASL interpretation
- **SignASLInterpreterPlugin** - Live ASL interpreter service
- **PinkSyncInterpreterPlugin** - Full accessibility suite with gloss ASL

## Key Features

### Pluggable Architecture
- **Interchangeable**: Switch between providers (Twilio ↔ Zoom) without code changes
- **Extensible**: Add custom plugins for proprietary systems
- **Configurable**: Centralized configuration management
- **Standardized**: Consistent API across all plugins

### Deployment Templates
Pre-built templates for common scenarios:
- Video chat integration with ASL interpreter embedding
- ASL interpreter widgets
- Gloss ASL conversion
- API integration suite

### PinkSync Partnership
Subscribe to PinkSync for automatic deployment:
- **Basic** ($99/month): ASL interpreters, captions, 10 hours/month
- **Professional** ($299/month): All Basic + gloss conversion, 50 hours/month
- **Enterprise** (Custom): Unlimited, white-label, SLA guarantees

Features:
- Automatic video chat setup
- Embedded ASL interpreters
- Gloss ASL conversion for heavy financial context
- Real-time translation
- 24/7 interpreter availability

## Documentation

- **Integration Guide**: [docs/ENTERPRISE_INTEGRATION.md](../../docs/ENTERPRISE_INTEGRATION.md)
- **Architecture**: [docs/ENTERPRISE_ARCHITECTURE.md](../../docs/ENTERPRISE_ARCHITECTURE.md)
- **Examples**: [examples/enterprise_integration.py](../../examples/enterprise_integration.py)

## Web Interface

### Routes
- `/enterprise` - Integration portal home
- `/enterprise/plugins` - Browse available plugins
- `/enterprise/dashboard` - Configuration dashboard
- `/enterprise/templates` - Deployment templates
- `/enterprise/pinksync` - PinkSync partnership portal
- `/enterprise/inquiry` - Contact enterprise team

### API Endpoints
- `GET /enterprise/api/plugins` - List registered plugins
- `POST /enterprise/api/plugin/execute` - Execute a plugin

## Contact

### Enterprise Architecture Team
- **Email**: architect@360magicians.com
- **Email**: architect@mbtq.dev
- **Response Time**: Within 24 hours

### What We Provide
- Technical consultation calls
- Custom integration plans
- Deployment templates
- Ongoing support and monitoring
- White-label solutions
- Training and onboarding

## Examples

### Bloomberg Integration
```python
from services.enterprise.api_plugins import BloombergAPIPlugin

bloomberg = BloombergAPIPlugin(config={
    'api_key': 'YOUR_KEY'
})

# Get financial data
data = bloomberg.get_financial_data(['AAPL', 'GOOGL'])

# Get terminology
term = bloomberg.get_terminology('compound_interest')
```

### Video Chat with ASL Interpreter
```python
from services.enterprise.video_plugins import (
    TwilioVideoPlugin,
    VSLLabsInterpreterPlugin
)

# Create video room
room = twilio.execute(
    action='create_room',
    room_config={'name': 'Consultation'}
)

# Request interpreter
interpreter = vsl_labs.execute(
    action='request_interpreter',
    appointment_details={'session_id': room['room_id']}
)
```

### Gloss ASL Conversion
```python
from services.enterprise.video_plugins import PinkSyncInterpreterPlugin

pinksync = PinkSyncInterpreterPlugin(config={
    'subscription_tier': 'professional'
})

gloss = pinksync.convert_to_gloss_asl(
    "Complex financial document text..."
)

print(f"Gloss: {gloss['gloss_asl']}")
print(f"Video: {gloss['video_url']}")
```

## Creating Custom Plugins

```python
from services.enterprise.plugin_registry import PluginInterface, PluginType

class MyCustomPlugin(PluginInterface):
    plugin_type = PluginType.API_CONNECTOR.value
    
    def __init__(self, config):
        super().__init__(config)
        self.api_url = config.get('api_url')
    
    def initialize(self):
        return bool(self.api_url)
    
    def execute(self, *args, **kwargs):
        # Your implementation
        pass
    
    def validate_config(self):
        return bool(self.api_url)

# Register your plugin
enterprise_registry.register_plugin(
    PluginType.API_CONNECTOR,
    'my_plugin',
    MyCustomPlugin,
    config={'api_url': 'https://api.example.com'}
)
```

## Architecture

```
Enterprise Client → Plugin Registry → Plugins → Services
                         ↓
                  Configuration
                         ↓
                  Deployment Templates
                         ↓
                  Accessibility Features
```

## Security

- OAuth 2.0 authentication
- API keys encrypted at rest
- TLS 1.2+ for data in transit
- SOC 2 compliant
- HIPAA ready

## Support

For questions, custom integrations, or enterprise support:
- Visit `/enterprise/inquiry`
- Email architect@360magicians.com
- Email architect@mbtq.dev

---

Built with ❤️ for enterprise accessibility and integration

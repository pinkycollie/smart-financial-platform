# MBTQ Smart Financial Platform for DHH Community

## Overview

The **MBTQ Smart Financial Platform** is a specialized financial services platform designed to serve the **Deaf and Hard of Hearing (DHH)** community. This platform provides accessible tax preparation, insurance services, and financial education with a focus on communication accessibility, DHH-specific deductions, and specialized insurance coverage.

## Mission

To enhance financial services for the Deaf and Hard of Hearing community by providing:
- Accessible communication options (ASL interpreters, VRI, captioned services)
- DHH-specific tax deductions and credits
- Insurance coverage for hearing aids and assistive technology
- Financial education in American Sign Language (ASL)

## Key Features

### 🤟 DHH-First Design
- **Communication Preferences**: ASL Interpreter, Video Remote Interpreting (VRI), Captioned Phone, Text-Only
- **Interpreter Coordination**: Built-in scheduling and contracting for interpreters
- **Visual Accessibility**: High-contrast interfaces and visual notifications
- **ASL Content**: Financial education and guidance delivered in ASL

### 💰 Tax Services
- **DHH-Specific Deductions**:
  - Work-related interpreter fees
  - Specialized equipment costs
  - Medical expenses (hearing aids, cochlear implants)
  - Assistive technology deductions
- **Refund Estimation**: Accurate calculations including DHH benefits
- **E-Filing Support**: Accessible filing process with ASL guidance

### 🏥 Insurance Services
- **Specialized Coverage**:
  - Hearing aid replacement and repair
  - Interpreter service riders
  - Assistive technology insurance
  - Medical appointment interpretation coverage
- **Quote Generation**: Customized quotes with DHH-specific riders
- **Policy Management**: Clear, accessible policy documentation

### 📚 Financial Education
- **ASL Educational Videos**: Financial concepts explained in ASL
- **Accessible Content**: Text, video, and visual learning materials
- **Community Support**: Forums and support groups for DHH individuals

### 🏢 Enterprise Integration
- **Pluggable Architecture**: Seamlessly integrate with Bloomberg, TurboTax, banks, and other enterprise systems
- **Interchangeable APIs**: Switch between providers (Twilio ↔ Zoom) without code changes
- **Video Chat**: Embedded video conferencing with ASL interpreter support
- **Gloss ASL Conversion**: Convert heavy financial context to accessible gloss ASL
- **PinkSync Partnership**: Full accessibility suite with automatic deployment
- **White Label**: Customizable UI and branding for enterprise clients
- **Contact**: architect@360magicians.com | architect@mbtq.dev

## Technology Stack

- **Backend**: Python 3.11+ with Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **API**: RESTful API with OpenAPI 3.0 specification
- **Security**: OAuth 2.0, Flask-Talisman, enterprise-grade encryption
- **ASL Integration**: VSL Labs API for ASL interpretation
- **Video**: Mux for video content delivery

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pinkycollie/smart-financial-platform.git
   cd smart-financial-platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Initialize the database**
   ```bash
   python scripts/migrate.py
   python scripts/seed.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   The application will be available at `http://localhost:5000`

### Environment Variables

Key environment variables to configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# API Keys
MUX_TOKEN_ID=your_mux_token_id
MUX_TOKEN_SECRET=your_mux_token_secret
VSL_API_KEY=your_vsl_labs_api_key

# External Services
APRIL_API_URL=https://api.getapril.com
APRIL_CLIENT_ID=your_april_client_id
APRIL_CLIENT_SECRET=your_april_client_secret

BOOST_API_URL=https://api.boostinsurance.io
BOOST_CLIENT_ID=your_boost_client_id
BOOST_CLIENT_SECRET=your_boost_client_secret
```

## API Documentation

The platform provides a comprehensive REST API documented using OpenAPI 3.0.

### Viewing API Documentation

1. **Swagger UI** (Interactive documentation):
   ```bash
   npx redoc-cli serve api/specs/openapi.json
   ```
   Open `http://localhost:8080` in your browser

2. **API Specification**: See `api/specs/openapi.json`

3. **API Guide**: See `api/specs/README.md`

### Key API Endpoints

- `POST /api/intake/tax-client` - Register new DHH client
- `POST /api/intake/needs-assessment` - Submit DHH needs assessment
- `POST /api/tax/refund-estimate` - Calculate tax refund estimate
- `POST /api/insurance/quote/request` - Request insurance quote
- `GET /api/internal/health` - Health check

See the [API Documentation](api/specs/README.md) for complete details.

## Enterprise Integration

The platform provides a comprehensive enterprise plugin system for seamless integration with large financial institutions, banks, tax services, and insurance companies.

### Available Integrations

- **Bloomberg API**: Financial data and terminology integration
- **TurboTax/Intuit API**: Tax preparation and filing
- **Bank APIs**: Account data and transaction integration
- **Video Chat**: Twilio, Zoom, and custom video providers
- **ASL Interpreters**: VSL Labs, SignASL, PinkSync
- **Custom APIs**: Flexible plugin system for proprietary systems

### Quick Start

```python
from services.enterprise.plugin_registry import enterprise_registry, PluginType
from services.enterprise.api_plugins import BloombergAPIPlugin

# Register plugin
enterprise_registry.register_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    BloombergAPIPlugin,
    config={'api_key': 'YOUR_API_KEY'}
)

# Use plugin
result = enterprise_registry.execute_plugin(
    PluginType.API_CONNECTOR,
    'bloomberg',
    method='GET',
    endpoint='/market-data/v1/securities'
)
```

### Resources

- **Web Portal**: Visit `/enterprise` for the integration portal
- **Documentation**: See [ENTERPRISE_INTEGRATION.md](docs/ENTERPRISE_INTEGRATION.md)
- **Examples**: See [examples/enterprise_integration.py](examples/enterprise_integration.py)
- **Contact**: architect@360magicians.com | architect@mbtq.dev

## Project Structure

```
smart-financial-platform/
├── api/                    # API specifications and routes
├── routes/                 # Application routes
├── services/               # Business logic services
├── models/                 # Database models
├── config/                 # Configuration files
├── static/                 # Static assets
├── templates/              # HTML templates
├── tests/                  # Test suite
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Testing

### Run Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=./ --cov-report=html
```

### API Testing

```bash
# Validate OpenAPI spec
npx @apidevtools/swagger-cli validate api/specs/openapi.json

# Property-based testing with Schemathesis
schemathesis run api/specs/openapi.json --base-url http://localhost:5000
```

## Security

This platform handles sensitive financial and personal data. Key security measures:

- **Authentication**: OAuth 2.0 and API Key authentication
- **Authorization**: Role-Based Access Control (RBAC)
- **Encryption**: TLS 1.2+ in transit, encrypted at rest
- **Compliance**: HIPAA-compliant for health data
- **Rate Limiting**: 100 requests/minute per client
- **Security Headers**: Flask-Talisman for CSP, HSTS, etc.

See [docs/security.md](docs/security.md) for details.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development workflow
- Coding standards
- Pull request process

## Roadmap

### Current Version (1.0.0)
- ✅ DHH client intake with communication preferences
- ✅ Tax refund estimation with DHH deductions
- ✅ Insurance quotes with DHH riders
- ✅ OpenAPI 3.0 specification
- ✅ Basic ASL integration

### Future Releases

**Version 1.1.0**
- [ ] Real-time ASL video interpretation
- [ ] Automated e-filing integration
- [ ] Enhanced mobile experience

**Version 2.0.0**
- [ ] AI-powered deduction discovery
- [ ] Multi-language support (BSL, Auslan, etc.)
- [ ] Community forum with ASL video support
- [ ] Insurance policy comparison engine

## Support

### For Users
- **Email**: support@mbtquniverse.com
- **ASL Video Support**: [Book an appointment](https://support.mbtquniverse.com/asl)
- **Text Support**: Available via the platform

### For Developers
- **API Documentation**: `api/specs/README.md`
- **Architecture Guide**: `ARCHITECTURE.md`
- **Issues**: [GitHub Issues](https://github.com/pinkycollie/smart-financial-platform/issues)

## License

Copyright © 2025 MBTQ GROUP LLC. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, modification, distribution, or use of this software, via any medium, is strictly prohibited.

## Acknowledgments

- VSL Labs for ASL interpretation technology
- The DHH community for guidance and feedback
- Open Insurance Initiative for insurance data standards

## Contact

**MBTQ GROUP LLC**
- Website: https://mbtquniverse.com
- Email: info@mbtquniverse.com
- Support: support@mbtquniverse.com

---

Made with ❤️ for the Deaf and Hard of Hearing community

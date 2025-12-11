# Smart Financial Platform - DHH Focused Architecture

## Project Structure Skeleton

This document outlines the modular, skeleton foundation for the MBTQ Smart Tax & Insurance Platform for the Deaf and Hard of Hearing community.

## Directory Structure

```
smart-financial-platform/
├── api/                          # API layer
│   ├── specs/                    # OpenAPI specifications
│   │   ├── openapi.json         # Main DHH-focused API spec
│   │   └── README.md            # API documentation
│   ├── deaf_first_api.py        # DHH-specific API routes
│   ├── miniapps.py              # Mini-application endpoints
│   └── webhooks.py              # Webhook handlers
│
├── routes/                       # Application routes
│   ├── deaf_first/              # DHH-specific routes
│   ├── fintech/                 # Financial technology routes
│   │   └── insurance/           # Insurance-related routes
│   ├── reseller/                # Reseller management
│   ├── advisors.py              # Financial advisor routes
│   ├── asl_ai.py                # ASL AI integration
│   ├── asl_support.py           # ASL support features
│   ├── education.py             # Financial education
│   ├── subscriptions.py         # Subscription management
│   ├── training.py              # Training modules
│   └── vsl_communication.py     # VSL communication integration
│
├── services/                     # Business logic services
│   ├── deaf_first/              # DHH-specific services
│   │   └── vsl_integration/     # VSL Labs integration
│   ├── tax/                     # Tax calculation services
│   │   ├── calculator.py        # Tax refund calculator
│   │   ├── dhh_deductions.py    # DHH-specific deduction logic
│   │   └── estimator.py         # Refund estimation
│   ├── insurance/               # Insurance services
│   │   ├── quote_generator.py   # Quote generation
│   │   ├── dhh_riders.py        # DHH-specific insurance riders
│   │   └── policy_manager.py    # Policy management
│   └── communication/           # Communication services
│       ├── interpreter.py       # Interpreter scheduling
│       ├── vri_integration.py   # VRI service integration
│       └── notification.py      # Accessible notifications
│
├── models/                       # Data models
│   ├── models.py                # Core models
│   ├── models_asl_support.py    # ASL support models
│   ├── models_education.py      # Education models
│   ├── models_licensing.py      # Licensing models
│   └── models_reseller.py       # Reseller models
│
├── config/                       # Configuration
│   ├── security.py              # Security configuration
│   ├── database.py              # Database configuration
│   └── api_keys.py              # API key management
│
├── static/                       # Static assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript
│   └── media/                   # Images, videos
│
├── templates/                    # HTML templates
│   ├── base.html                # Base template
│   ├── dhh/                     # DHH-specific templates
│   └── forms/                   # Form templates
│
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
│
├── docs/                         # Documentation
│   ├── architecture.md          # Architecture documentation
│   ├── api/                     # API documentation
│   ├── deployment.md            # Deployment guide
│   └── security.md              # Security documentation
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # Setup script
│   ├── migrate.py               # Database migration
│   └── seed.py                  # Database seeding
│
├── .gitignore                    # Git ignore rules
├── pyproject.toml                # Python project configuration
├── README.md                     # Project README
└── main.py                       # Application entry point
```

## Core Modules

### 1. Client Intake Module
**Purpose**: Capture DHH-specific client information and communication preferences

**Components**:
- DHH client registration
- Communication preference management
- Interpreter coordination
- Needs assessment workflow

**Key Files**:
- `routes/deaf_first/intake.py`
- `services/client/intake_service.py`
- `models/dhh_client.py`

### 2. Tax Services Module
**Purpose**: Calculate tax refunds with DHH-specific deductions

**Components**:
- W-2 income processing
- Standard deduction calculation
- DHH-specific deduction identification:
  - Interpreter fees
  - Specialized equipment
  - Medical expenses
  - Assistive technology

**Key Files**:
- `services/tax/calculator.py`
- `services/tax/dhh_deductions.py`
- `api/endpoints/tax.py`

### 3. Insurance Services Module
**Purpose**: Provide insurance quotes with DHH-specific coverage

**Components**:
- Quote generation
- DHH rider management:
  - Hearing aid coverage
  - Interpreter service coverage
  - Specialized equipment insurance
- Policy exception handling

**Key Files**:
- `services/insurance/quote_generator.py`
- `services/insurance/dhh_riders.py`
- `api/endpoints/insurance.py`

### 4. Communication Module
**Purpose**: Manage accessible communication methods

**Components**:
- ASL interpreter scheduling
- VRI integration
- Captioned phone support
- Text-only communication
- Visual notifications

**Key Files**:
- `services/communication/interpreter.py`
- `services/communication/vri_integration.py`
- `routes/vsl_communication.py`

### 5. ASL/VSL Integration Module
**Purpose**: Integrate with VSL Labs for ASL services

**Components**:
- ASL video interpretation
- Financial terminology in ASL
- Video chat with ASL support
- ASL translation services

**Key Files**:
- `services/deaf_first/vsl_integration.py`
- `routes/asl_ai.py`
- `routes/asl_support.py`

### 6. Financial Education Module
**Purpose**: Provide accessible financial education

**Components**:
- ASL educational videos
- Financial literacy content
- Tax filing guides in ASL
- Insurance education materials

**Key Files**:
- `routes/education.py`
- `services/education/content_service.py`
- `models/models_education.py`

## Data Flow

### Client Intake Flow
```
Client Registration → Communication Preference Selection → Interpreter Coordination → Needs Assessment → Service Assignment
```

### Tax Refund Estimation Flow
```
Income Input → Standard Deductions → DHH-Specific Deduction Identification → Calculation → Refund Estimate with Notes
```

### Insurance Quote Flow
```
Coverage Request → DHH Needs Assessment → Rider Selection → Quote Generation → Policy Customization
```

## API Architecture

### Layers
1. **API Layer** (`api/specs/openapi.json`)
   - RESTful endpoints
   - Request/response schemas
   - Authentication/authorization

2. **Route Layer** (`routes/`)
   - Request handling
   - Input validation
   - Response formatting

3. **Service Layer** (`services/`)
   - Business logic
   - DHH-specific calculations
   - External API integration

4. **Data Layer** (`models/`)
   - Database models
   - Data persistence
   - Relationships

## Security Architecture

### Authentication
- OAuth 2.0 for web applications
- API Key for service-to-service
- Role-Based Access Control (RBAC)

### Data Protection
- TLS 1.2+ for data in transit
- Database encryption for data at rest
- PII masking in logs
- HIPAA compliance for health data

### Rate Limiting
- 100 requests/minute per client
- Throttling for heavy endpoints
- Circuit breakers for external services

## Scalability Considerations

### Horizontal Scaling
- Stateless services
- Load balancer ready
- Session management via Redis

### Asynchronous Processing
- Message queues for long-running tasks
- Background jobs for:
  - Document generation
  - E-filing submission
  - Refund calculations

### Caching
- Redis for session data
- API response caching
- Static asset CDN

## Monitoring & Observability

### Logging
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- PII redaction in logs

### Metrics
- Request latency
- Error rates
- Throughput
- Resource utilization

### Alerting
- Critical error alerts
- Performance degradation alerts
- Security incident alerts

## Development Workflow

### Local Development
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run migrations: `python scripts/migrate.py`
5. Start server: `python main.py`

### Testing
1. Unit tests: `pytest tests/unit/`
2. Integration tests: `pytest tests/integration/`
3. E2E tests: `pytest tests/e2e/`

### Deployment
1. Build Docker image
2. Push to container registry
3. Deploy to Kubernetes/Cloud
4. Run health checks
5. Monitor metrics

## Future Enhancements

### Phase 2 Features
- [ ] Real-time ASL video interpretation
- [ ] AI-powered deduction discovery
- [ ] Automated e-filing integration
- [ ] Multi-language support (BSL, Auslan, etc.)
- [ ] Mobile app with ASL support

### Phase 3 Features
- [ ] Blockchain-based document verification
- [ ] Predictive analytics for tax optimization
- [ ] Insurance policy comparison engine
- [ ] Community forum with ASL video support

## Contributing

See CONTRIBUTING.md for guidelines on:
- Code style
- Testing requirements
- Pull request process
- Documentation standards

## License

Copyright © 2025 MBTQ GROUP LLC. All rights reserved.

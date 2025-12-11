# MBTQ Smart Tax & Insurance API for DHH Community

## Overview

This API specification is designed specifically for the **Deaf and Hard of Hearing (DHH) community**, providing specialized tax and insurance services with a focus on accessibility, communication preferences, and DHH-specific financial opportunities.

## Key Features

### DHH-Specific Capabilities

1. **Communication Preference Support**
   - ASL Interpreter coordination
   - Video Remote Interpreting (VRI)
   - Captioned Phone services
   - Text-only communication

2. **Specialized Tax Deductions**
   - Work-related interpreter fees
   - Specialized equipment deductions
   - Medical expenses related to hearing
   - Assistive technology costs

3. **Insurance Coverage for DHH Needs**
   - Hearing aid replacement/repair coverage
   - Interpreter service riders
   - Medical appointment interpretation coverage
   - Specialized equipment insurance

## API Documentation

### Base URLs

- **Production**: `https://api.mbtquniverse.com`
- **Development**: `http://localhost:5000`

### Authentication

The API supports two authentication methods:

1. **OAuth 2.0** (Recommended for web applications)
   - Authorization URL: `https://api.mbtquniverse.com/oauth/authorize`
   - Token URL: `https://api.mbtquniverse.com/oauth/token`
   - Scopes: `read`, `write`, `admin`

2. **API Key** (For service-to-service communication)
   - Header: `X-API-Key: your_api_key`

### Core Endpoints

#### Client Intake

##### POST /api/intake/tax-client
Register a new DHH client for tax services.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "communication_preference": "ASL_Interpreter",
  "interpreter_needed": true,
  "interpreter_contracting_status": "Pending"
}
```

**Response (201):**
```json
{
  "client_id": "12345",
  "status": "Registered",
  "next_step": "Proceed to Needs Assessment"
}
```

##### POST /api/intake/needs-assessment
Submit a detailed needs assessment for DHH-specific opportunities.

**Request Body:**
```json
{
  "hearing_aid_claims_history": "Annual replacements for past 5 years",
  "benefit_program_eligibility": ["SSDI", "Vocational_Rehab"],
  "tax_deductions_focus": ["Work_Related_Interpreter_Fees", "Specialized_Equipment"]
}
```

#### Tax Services

##### POST /api/tax/refund-estimate
Calculate estimated tax refund with DHH-specific deductions.

**Request Body:**
```json
{
  "income_w2": 65000.00,
  "deductions_standard": 12950.00,
  "special_deduction_amount": 3500.00
}
```

**Response (200):**
```json
{
  "estimated_refund": 2450.75,
  "dhh_benefit_applied": true,
  "notes": "Interpreter fees and assistive technology deductions applied. Please retain receipts for documentation."
}
```

#### Insurance Services

##### POST /api/insurance/quote/request
Request insurance quote with DHH-specific riders.

**Request Body:**
```json
{
  "insurance_type": "Health",
  "hearing_aid_coverage_required": true,
  "interpreter_service_rider": true,
  "current_policy_exception_summary": "Previous policy excluded hearing aid batteries"
}
```

**Response (200):**
```json
{
  "quote_id": "Q-2025-12345",
  "estimated_premium_range": "$150 - $200/month"
}
```

### Health Check

##### GET /api/internal/health
Check API operational status.

**Response (200):**
```json
{
  "status": "UP",
  "timestamp": "2025-12-10T17:48:00Z"
}
```

## Viewing the Specification

### Using Swagger UI

1. Install Swagger UI:
   ```bash
   npm install -g swagger-ui-dist
   ```

2. Serve the specification:
   ```bash
   swagger-ui serve api/specs/openapi.json
   ```

3. Open in browser: `http://localhost:8080`

### Using Redoc

```bash
npx redoc-cli serve api/specs/openapi.json
```

## Validation

To validate the OpenAPI specification:

```bash
npx @apidevtools/swagger-cli validate api/specs/openapi.json
```

## Generating Client SDKs

Use OpenAPI Generator to create client libraries:

### JavaScript/TypeScript
```bash
openapi-generator-cli generate -i api/specs/openapi.json -g typescript-axios -o ./client/typescript
```

### Python
```bash
openapi-generator-cli generate -i api/specs/openapi.json -g python -o ./client/python
```

### Java
```bash
openapi-generator-cli generate -i api/specs/openapi.json -g java -o ./client/java
```

## Testing

### Using Postman

1. Import the OpenAPI specification into Postman
2. Generate a collection from the spec
3. Configure environment variables for authentication
4. Run automated tests against endpoints

### Using Schemathesis

Automated property-based testing:

```bash
pip install schemathesis
schemathesis run api/specs/openapi.json --base-url http://localhost:5000
```

## Security Considerations

1. **Authentication Required**: All endpoints (except health check) require authentication
2. **HTTPS Only**: Production API only accepts HTTPS connections
3. **Rate Limiting**: 100 requests per minute per client
4. **Data Encryption**: All sensitive data encrypted in transit (TLS 1.2+) and at rest
5. **HIPAA Compliance**: Tax and insurance data handled according to HIPAA requirements
6. **PII Protection**: Personal identifiable information is masked in logs

## Best Practices

### Communication Preferences
Always respect the client's `communication_preference` setting. When scheduling appointments or sending notifications, use the preferred method.

### DHH-Specific Deductions
When calculating tax estimates:
- Verify interpreter receipts are properly documented
- Ensure medical equipment costs have supporting documentation
- Check eligibility for Disability Tax Credit (DTC)

### Insurance Quotes
For DHH clients requesting insurance:
- Always include hearing aid coverage options
- Offer interpreter service riders by default
- Explain policy exceptions in clear, accessible language

## Support

For API support and questions:
- **Documentation**: This file and the OpenAPI specification
- **Email**: api-support@mbtquniverse.com
- **Video Support (ASL)**: Schedule at support.mbtquniverse.com/asl

## Version History

- **1.0.0** (2025-12-10): Initial release with DHH-focused features
  - Client intake with communication preferences
  - Tax refund estimation with DHH-specific deductions
  - Insurance quotes with DHH riders
  - Health check endpoint

## License

Copyright © 2025 MBTQ GROUP LLC. All rights reserved.

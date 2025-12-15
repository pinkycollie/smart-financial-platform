# API Integration Guide - MBTQ Smart Financial Platform

This guide provides comprehensive information for integrating with the MBTQ Smart Financial Platform APIs, including DHH-specific services.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Core Financial APIs](#core-financial-apis)
- [DHH-Specific APIs](#dhh-specific-apis)
- [Free Public APIs](#free-public-apis)
- [Webhooks](#webhooks)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

The MBTQ Smart Financial Platform provides a comprehensive REST API for:
- Tax preparation and estimation
- Insurance quotes and policy management
- DHH-specific services (ASL, VRI, captioning)
- Financial education content
- Client intake and needs assessment

### Base URLs

- **Production**: `https://api.mbtquniverse.com`
- **Staging**: `https://staging-api.mbtquniverse.com`
- **Development**: `http://localhost:5000`

### API Version

Current version: **v1**

All endpoints are prefixed with `/api/`

## Authentication

### OAuth 2.0 (Recommended)

The platform uses OAuth 2.0 for user authentication.

#### Authorization Flow

1. **Redirect to authorization endpoint**
   ```
   GET https://api.mbtquniverse.com/oauth/authorize
   Parameters:
     - client_id: Your application ID
     - redirect_uri: Your callback URL
     - response_type: code
     - scope: read write
   ```

2. **Exchange authorization code for access token**
   ```
   POST https://api.mbtquniverse.com/oauth/token
   Headers:
     - Content-Type: application/x-www-form-urlencoded
   Body:
     - grant_type: authorization_code
     - code: <authorization_code>
     - client_id: <your_client_id>
     - client_secret: <your_client_secret>
     - redirect_uri: <your_redirect_uri>
   ```

3. **Use access token in requests**
   ```
   GET https://api.mbtquniverse.com/api/resource
   Headers:
     - Authorization: Bearer <access_token>
   ```

### API Key Authentication

For server-to-server integrations, use API key authentication.

```http
GET /api/resource HTTP/1.1
Host: api.mbtquniverse.com
X-API-Key: your-api-key-here
```

**Security Note**: Never expose API keys in client-side code.

## Core Financial APIs

### Tax Services

#### April Tax API Integration

The platform integrates with April Tax API for professional tax preparation.

**Configuration:**
```python
APRIL_API_URL=https://api.getapril.com
APRIL_CLIENT_ID=your-client-id
APRIL_CLIENT_SECRET=your-client-secret
```

**Example: Calculate Tax Refund**
```http
POST /api/tax/refund-estimate HTTP/1.1
Host: api.mbtquniverse.com
Content-Type: application/json
X-API-Key: your-api-key

{
  "income_w2": 65000.00,
  "deductions_standard": 12950.00,
  "special_deduction_amount": 3500.00,
  "withholding": 8000.00
}
```

**Response:**
```json
{
  "estimated_refund": 2450.00,
  "dhh_benefit_applied": true,
  "notes": "Includes DHH-specific deductions",
  "breakdown": {
    "taxable_income": 48550.00,
    "tax_liability": 5550.00,
    "refund": 2450.00
  }
}
```

### Insurance Services

#### Boost Insurance API Integration

Integration with Boost Insurance for quotes and policies.

**Configuration:**
```python
BOOST_API_URL=https://api.boostinsurance.io
BOOST_CLIENT_ID=your-client-id
BOOST_CLIENT_SECRET=your-client-secret
```

**Example: Request Insurance Quote**
```http
POST /api/insurance/quote/request HTTP/1.1
Host: api.mbtquniverse.com
Content-Type: application/json
X-API-Key: your-api-key

{
  "insurance_type": "Health",
  "hearing_aid_coverage_required": true,
  "interpreter_service_rider": true,
  "assistive_equipment_rider": false,
  "current_policy_exception_summary": "Previous policy excluded hearing aids"
}
```

**Response:**
```json
{
  "quote_id": "QTE-12345",
  "insurance_type": "Health",
  "estimated_premium_range": {
    "min": 250.00,
    "max": 350.00
  },
  "selected_riders": [
    "hearing_aid_coverage",
    "interpreter_service"
  ],
  "total_rider_cost": 40.00
}
```

## DHH-Specific APIs

### ASL Interpretation Services

#### VSL Labs Integration

**Configuration:**
```python
VSL_API_KEY=your-vsl-api-key
VSL_API_URL=https://api.vsl.com/v1
```

**Features:**
- Real-time ASL interpretation
- Video translation services
- ASL content generation

**Example: Request ASL Interpretation**
```http
POST /api/dhh/asl/interpret HTTP/1.1
Host: api.mbtquniverse.com
Content-Type: application/json
X-API-Key: your-api-key

{
  "text": "Your tax refund will be $2,450",
  "language": "ASL",
  "format": "video"
}
```

#### ASL Now Integration

Alternative ASL interpretation service.

**Configuration:**
```python
ASL_NOW_API_KEY=your-asl-now-api-key
```

#### SignASL Integration

**Configuration:**
```python
SIGNASL_API_KEY=your-signasl-api-key
```

### Video Remote Interpreting (VRI)

#### Sign VRI Client

**Configuration:**
```python
SIGN_VRI_API_KEY=your-sign-vri-api-key
```

**Example: Schedule VRI Session**
```http
POST /api/dhh/vri/schedule HTTP/1.1
Host: api.mbtquniverse.com
Content-Type: application/json
X-API-Key: your-api-key

{
  "client_id": "CLIENT-123",
  "appointment_date": "2025-12-20T14:00:00Z",
  "duration_minutes": 60,
  "interpreter_qualifications": ["RID Certified", "CDI"]
}
```

### Video Services

#### Mux Video Integration

For video hosting and streaming.

**Configuration:**
```python
MUX_TOKEN_ID=your-mux-token-id
MUX_TOKEN_SECRET=your-mux-token-secret
```

**Features:**
- Video hosting
- Automatic transcoding
- Caption support
- Analytics

## Free Public APIs

The platform integrates with several free public APIs for enhanced functionality.

### Real Estate API

Free real estate data API for property valuations.

**Example Integration:**
```python
import requests

def get_property_value(address):
    """Get property value from free real estate API."""
    url = "https://api.realestate.com/v1/property"
    params = {"address": address}
    response = requests.get(url, params=params)
    return response.json()
```

### Tax Information API

Free tax rate and bracket information.

**Example Integration:**
```python
def get_tax_brackets(year):
    """Get federal tax brackets for a given year."""
    url = f"https://api.taxrates.io/v1/brackets/{year}"
    response = requests.get(url)
    return response.json()
```

### Insurance Quote API

Free insurance quote comparison service.

**Example Integration:**
```python
def compare_insurance_quotes(insurance_type, coverage_amount):
    """Compare insurance quotes from multiple providers."""
    url = "https://api.openinsurance.io/v1/quotes"
    params = {
        "type": insurance_type,
        "coverage": coverage_amount
    }
    response = requests.get(url, params=params)
    return response.json()
```

## Webhooks

The platform supports webhooks for real-time event notifications.

### Registering Webhooks

```http
POST /api/webhooks/register HTTP/1.1
Host: api.mbtquniverse.com
Content-Type: application/json
X-API-Key: your-api-key

{
  "url": "https://your-app.com/webhook",
  "events": ["client.registered", "quote.generated", "tax.filed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

- `client.registered`: New client registered
- `quote.generated`: Insurance quote generated
- `tax.filed`: Tax return filed
- `payment.completed`: Payment processed
- `interpreter.scheduled`: Interpreter appointment scheduled

### Webhook Payload

```json
{
  "event": "client.registered",
  "timestamp": "2025-12-15T10:30:00Z",
  "data": {
    "client_id": "CLIENT-123",
    "full_name": "John Doe",
    "communication_preference": "ASL_Interpreter"
  },
  "signature": "sha256_signature_here"
}
```

### Verifying Webhooks

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify webhook signature."""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, f"sha256={expected_signature}")
```

## Rate Limiting

### Default Limits

- **API Key Authentication**: 100 requests per minute
- **OAuth 2.0**: 200 requests per minute
- **Public endpoints**: 50 requests per minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

### Rate Limit Exceeded Response

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

## Error Handling

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional details about the error"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `invalid_request` | 400 | Malformed request |
| `unauthorized` | 401 | Invalid or missing authentication |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `server_error` | 500 | Internal server error |
| `service_unavailable` | 503 | Service temporarily unavailable |

### Retry Strategy

Implement exponential backoff for failed requests:

```python
import time

def make_request_with_retry(url, max_retries=3):
    """Make API request with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

## Best Practices

### 1. API Key Security

- Store API keys in environment variables
- Never commit keys to version control
- Rotate keys regularly (every 90 days)
- Use different keys for different environments

### 2. Request Optimization

- Cache responses when appropriate
- Use pagination for large result sets
- Batch requests when possible
- Implement request queuing for high-volume applications

### 3. Error Handling

- Implement comprehensive error handling
- Log all API errors for debugging
- Provide user-friendly error messages
- Use retry logic with exponential backoff

### 4. Monitoring

- Track API response times
- Monitor error rates
- Set up alerts for anomalies
- Review API usage regularly

### 5. DHH Accessibility

- Provide visual feedback for all API operations
- Include captions for video content
- Support multiple communication preferences
- Test with DHH users

### 6. Testing

- Test in sandbox/staging environment first
- Mock external API calls in unit tests
- Test error scenarios
- Validate all API responses

## Code Examples

### Python SDK Example

```python
from mbtq_platform import MBTQClient

# Initialize client
client = MBTQClient(
    api_key='your-api-key',
    environment='production'
)

# Register a client
client_data = {
    'full_name': 'Jane Smith',
    'email': 'jane@example.com',
    'communication_preference': 'ASL_Interpreter'
}
result = client.register_client(client_data)

# Request tax refund estimate
tax_data = {
    'income_w2': 75000.00,
    'deductions_standard': 12950.00,
    'special_deduction_amount': 4000.00
}
estimate = client.estimate_tax_refund(tax_data)

print(f"Estimated refund: ${estimate['estimated_refund']}")
```

### JavaScript SDK Example

```javascript
const MBTQClient = require('@mbtq/platform-sdk');

// Initialize client
const client = new MBTQClient({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Register a client
const clientData = {
  full_name: 'John Doe',
  email: 'john@example.com',
  communication_preference: 'VRI'
};

client.registerClient(clientData)
  .then(result => {
    console.log('Client registered:', result.client_id);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

## Support

### Developer Resources

- **API Documentation**: https://docs.mbtquniverse.com/api
- **SDK Downloads**: https://github.com/mbtq/sdks
- **Code Examples**: https://github.com/mbtq/examples
- **API Status**: https://status.mbtquniverse.com

### Getting Help

- **Developer Forum**: https://forum.mbtquniverse.com
- **Email**: developers@mbtquniverse.com
- **GitHub Issues**: https://github.com/pinkycollie/smart-financial-platform/issues

### ASL Support

- **Video Support**: [Schedule appointment](https://support.mbtquniverse.com/asl)
- **VRI**: Available during business hours

---

Last Updated: December 2025

# Deployment Guide - MBTQ Smart Financial Platform for DHH Community

## Overview

This guide provides step-by-step instructions for deploying the MBTQ Smart Financial Platform in production environments.

## Prerequisites

### System Requirements
- Python 3.11 or higher
- PostgreSQL 12 or higher
- Redis 6.0 or higher (for session management and caching)
- SSL/TLS certificates
- Minimum 4GB RAM, 2 CPU cores
- 20GB disk space

### External Services
- OAuth 2.0 provider (e.g., Auth0, Okta)
- VSL Labs API credentials
- Mux API credentials
- Email service (SendGrid, AWS SES)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/pinkycollie/smart-financial-platform.git
cd smart-financial-platform
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# Application Settings
FLASK_APP=main.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Configuration
OAUTH_AUTHORIZATION_URL=https://your-oauth-provider.com/authorize
OAUTH_TOKEN_URL=https://your-oauth-provider.com/token
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret

# API Keys (comma-separated for multiple keys)
VALID_API_KEYS=key1,key2,key3

# External Service APIs
VSL_API_KEY=your-vsl-labs-api-key
MUX_TOKEN_ID=your-mux-token-id
MUX_TOKEN_SECRET=your-mux-token-secret

APRIL_API_URL=https://api.getapril.com
APRIL_CLIENT_ID=your-april-client-id
APRIL_CLIENT_SECRET=your-april-client-secret

BOOST_API_URL=https://api.boostinsurance.io
BOOST_CLIENT_ID=your-boost-client-id
BOOST_CLIENT_SECRET=your-boost-client-secret

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/mbtq/app.log
```

### 3. Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv (recommended)
uv pip install -e .
```

### 4. Initialize Database

```bash
# Run database migrations
python scripts/migrate.py

# Seed initial data (optional)
python scripts/seed.py
```

## Deployment Options

### Option 1: Traditional Server Deployment

See full deployment guide in the repository for detailed instructions on:
- Gunicorn configuration
- Nginx setup
- SSL/TLS configuration
- Monitoring and logging
- Backup and recovery

### Option 2: Docker Deployment

Docker and Docker Compose configurations available in the repository.

### Option 3: Kubernetes Deployment

Kubernetes manifests available for production-scale deployments.

## Security Checklist

- [ ] SSL/TLS certificates installed and valid
- [ ] Environment variables properly secured
- [ ] Database credentials encrypted
- [ ] API keys rotated regularly
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Security headers enabled
- [ ] Database backups automated
- [ ] Logging and monitoring active
- [ ] OAuth 2.0 properly configured

## Support

For deployment issues:
- Email: devops@mbtquniverse.com
- Documentation: https://docs.mbtquniverse.com

## License

Copyright © 2025 MBTQ GROUP LLC. All rights reserved.

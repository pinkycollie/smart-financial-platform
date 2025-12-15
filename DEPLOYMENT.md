# Deployment Guide - MBTQ Smart Financial Platform

This guide provides comprehensive instructions for deploying the MBTQ Smart Financial Platform to various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Options](#deployment-options)
- [Database Setup](#database-setup)
- [Security Configuration](#security-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7 or higher (for caching and sessions)
- **Memory**: Minimum 2GB RAM (4GB recommended for production)
- **Storage**: Minimum 20GB available disk space
- **OS**: Linux (Ubuntu 22.04 LTS recommended) or Docker

### Required Credentials

Before deployment, ensure you have:

- Database connection credentials
- OAuth 2.0 client credentials
- API keys for external services:
  - Mux (video service)
  - VSL Labs (ASL interpretation)
  - April Tax API
  - Boost Insurance API
  - OpenAI API (for AI features)
- Email service credentials (SendGrid/Mailgun)
- Cloud storage credentials (AWS S3 or Azure Blob)

## Environment Setup

### 1. Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and configure all required variables. See [.env.example](.env.example) for details.

### 2. Environment-Specific Configuration

Set the `FLASK_ENV` variable to match your target environment:

- `development`: Local development
- `staging`: Pre-production testing
- `production`: Live production environment

```bash
export FLASK_ENV=production
```

## Deployment Options

### Option 1: Docker Deployment (Recommended)

Docker provides the most consistent deployment experience across environments.

#### Prerequisites

- Docker 24.0+
- Docker Compose 2.0+

#### Steps

1. **Build the Docker image**

```bash
docker build -t mbtq-platform:latest .
```

2. **Run with Docker Compose**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

3. **Initialize the database**

```bash
docker-compose exec web python scripts/migrate.py
docker-compose exec web python scripts/seed.py
```

4. **Access the application**

- Application: http://localhost:5000
- Health Check: http://localhost:5000/api/internal/health

#### Production Docker Compose

For production, use the production profile:

```bash
docker-compose --profile production up -d
```

This includes Nginx as a reverse proxy with SSL termination.

### Option 2: Traditional Server Deployment

#### On Ubuntu 22.04 LTS

1. **Install system dependencies**

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip postgresql-15 redis-server nginx
```

2. **Create application user**

```bash
sudo useradd -m -s /bin/bash mbtq
sudo su - mbtq
```

3. **Clone repository and setup**

```bash
cd /opt
sudo git clone https://github.com/pinkycollie/smart-financial-platform.git
sudo chown -R mbtq:mbtq smart-financial-platform
cd smart-financial-platform

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e .
```

4. **Configure environment**

```bash
cp .env.example .env
nano .env  # Edit with your configuration
```

5. **Initialize database**

```bash
python scripts/migrate.py
python scripts/seed.py
```

6. **Set up systemd service**

Create `/etc/systemd/system/mbtq-platform.service`:

```ini
[Unit]
Description=MBTQ Smart Financial Platform
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=mbtq
Group=mbtq
WorkingDirectory=/opt/smart-financial-platform
Environment="PATH=/opt/smart-financial-platform/venv/bin"
ExecStart=/opt/smart-financial-platform/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile /var/log/mbtq/access.log \
    --error-logfile /var/log/mbtq/error.log \
    wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

7. **Create log directory**

```bash
sudo mkdir -p /var/log/mbtq
sudo chown mbtq:mbtq /var/log/mbtq
```

8. **Start and enable service**

```bash
sudo systemctl daemon-reload
sudo systemctl start mbtq-platform
sudo systemctl enable mbtq-platform
sudo systemctl status mbtq-platform
```

9. **Configure Nginx**

Create `/etc/nginx/sites-available/mbtq-platform`:

```nginx
upstream mbtq_app {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name mbtquniverse.com www.mbtquniverse.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mbtquniverse.com www.mbtquniverse.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/mbtquniverse.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mbtquniverse.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/mbtq_access.log;
    error_log /var/log/nginx/mbtq_error.log;

    # Static files
    location /static {
        alias /opt/smart-financial-platform/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to application
    location / {
        proxy_pass http://mbtq_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /api/internal/health {
        proxy_pass http://mbtq_app;
        access_log off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/mbtq-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

10. **Set up SSL with Let's Encrypt**

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d mbtquniverse.com -d www.mbtquniverse.com
```

### Option 3: Cloud Platform Deployment

#### Heroku

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login and create app
heroku login
heroku create mbtq-platform

# Add PostgreSQL and Redis
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
# ... set other variables from .env

# Deploy
git push heroku main

# Run migrations
heroku run python scripts/migrate.py
```

#### AWS Elastic Beanstalk

See [AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) for detailed instructions.

#### Google Cloud Run

See [GCP_DEPLOYMENT.md](docs/GCP_DEPLOYMENT.md) for detailed instructions.

## Database Setup

### PostgreSQL Configuration

1. **Create database and user**

```sql
CREATE DATABASE mbtq_platform;
CREATE USER mbtq_user WITH ENCRYPTED PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE mbtq_platform TO mbtq_user;
```

2. **Enable required extensions**

```sql
\c mbtq_platform
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

3. **Configure connection pooling**

For production, use PgBouncer for connection pooling:

```bash
sudo apt-get install pgbouncer
```

Configure `/etc/pgbouncer/pgbouncer.ini`:

```ini
[databases]
mbtq_platform = host=localhost port=5432 dbname=mbtq_platform

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 100
default_pool_size = 25
```

Update `DATABASE_URL` to use PgBouncer:
```
DATABASE_URL=postgresql://mbtq_user:password@localhost:6432/mbtq_platform
```

## Security Configuration

### 1. Firewall Setup

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban

Protect against brute-force attacks:

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Security Headers

Ensure all security headers are configured (already included in Nginx config above).

### 4. Secrets Management

For production, use a secrets manager:

- **AWS**: AWS Secrets Manager or Systems Manager Parameter Store
- **Azure**: Azure Key Vault
- **Google Cloud**: Secret Manager
- **HashiCorp**: Vault

Example using AWS Secrets Manager:

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

## Monitoring & Logging

### Application Monitoring

#### Sentry Integration

1. Sign up at [sentry.io](https://sentry.io)
2. Set `SENTRY_DSN` in environment variables
3. Errors will be automatically reported

#### New Relic (Optional)

```bash
pip install newrelic
newrelic-admin generate-config LICENSE_KEY newrelic.ini
```

Update startup command:
```bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn ...
```

### Log Aggregation

#### Using ELK Stack

See [LOGGING.md](docs/LOGGING.md) for detailed setup.

#### Using Cloud Services

- **AWS CloudWatch**: Configure CloudWatch agent
- **Google Cloud Logging**: Use Cloud Logging agent
- **Datadog**: Install Datadog agent

### Health Checks

Monitor the health endpoint:

```bash
curl https://mbtquniverse.com/api/internal/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-15T04:00:00Z",
  "version": "1.0.0"
}
```

## Backup & Recovery

### Database Backups

#### Automated Daily Backups

Create `/opt/scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mbtq"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U mbtq_user -h localhost mbtq_platform | \
    gzip > $BACKUP_DIR/mbtq_platform_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/mbtq_platform_$DATE.sql.gz \
    s3://mbtq-backups/database/
```

Make executable and add to crontab:

```bash
chmod +x /opt/scripts/backup-db.sh
crontab -e
# Add: 0 2 * * * /opt/scripts/backup-db.sh
```

#### Restore from Backup

```bash
gunzip -c backup.sql.gz | psql -U mbtq_user -d mbtq_platform
```

### File Storage Backups

If using local file storage, back up the uploads directory:

```bash
tar -czf uploads_backup.tar.gz static/uploads/
```

For cloud storage (S3/Azure), enable versioning and cross-region replication.

## Troubleshooting

### Application Won't Start

1. **Check logs**
```bash
sudo journalctl -u mbtq-platform -n 100 -f
```

2. **Verify database connection**
```bash
psql -U mbtq_user -h localhost -d mbtq_platform
```

3. **Check environment variables**
```bash
sudo -u mbtq env | grep -i flask
```

### Database Connection Issues

1. **Check PostgreSQL is running**
```bash
sudo systemctl status postgresql
```

2. **Verify connection string**
```bash
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"
```

### High Memory Usage

1. **Reduce Gunicorn workers**
```bash
# Edit systemd service, reduce --workers value
sudo systemctl edit mbtq-platform
```

2. **Enable connection pooling** (see Database Setup section)

### SSL Certificate Issues

```bash
# Test certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run
```

## Post-Deployment Checklist

- [ ] Application accessible via HTTPS
- [ ] Health check endpoint responding
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Firewall rules configured
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Security headers verified
- [ ] Rate limiting functional
- [ ] External API connections working
- [ ] Email notifications working
- [ ] Documentation updated with deployment details

## Support

For deployment assistance:

- **Documentation**: https://docs.mbtquniverse.com
- **Email**: support@mbtquniverse.com
- **GitHub Issues**: https://github.com/pinkycollie/smart-financial-platform/issues

---

Last Updated: December 2025

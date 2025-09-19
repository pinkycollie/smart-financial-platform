# MBTQ Group LLC Financial Platform

## Overview

MBTQ Group LLC is a comprehensive financial services platform built specifically for the deaf and hard-of-hearing community. The platform provides accessible financial education, tax preparation services, and insurance products through innovative ASL (American Sign Language) video integration and visual-first design principles. The system includes a multi-tier white-label reseller architecture that enables financial advisors and educators to license and customize the platform for their deaf clients.

## Business Structure

- **MBTQ Group LLC**: Main platform entity (legal but inactive status)
- **MBTQ Properties Group**: Legal entity registered in Washington DC for real estate services
- **Business Focus**: Insurance, tax preparation, and financial education services
- **Regulatory Status**: Not yet certified for financial advice or financial planning services

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web application with Python
- **Database**: PostgreSQL with SQLAlchemy ORM using DeclarativeBase
- **Authentication**: Flask-Login for user session management
- **API Design**: RESTful endpoints organized by business domain
- **Module Structure**: Domain-driven design with separate modules for education, resellers, licensing, ASL support, and financial services

### Frontend Architecture
- **Template Engine**: Jinja2 templates with responsive Bootstrap framework
- **Interactive Components**: HTMX for dynamic content updates without full page reloads
- **Accessibility**: Visual-first design with comprehensive ASL video integration
- **Mobile Support**: Responsive design optimized for mobile accessibility

### Database Design
- **User Management**: Comprehensive user profiles with accessibility preferences and communication settings
- **Multi-tier Architecture**: Support for resellers, sub-resellers, and licensees with customizable branding
- **Content Management**: Educational modules, ASL video categories, and financial content organization
- **Financial Services**: Tax documents, financial profiles, subscription management, and billing history

### ASL Video Integration
- **Multi-provider Strategy**: Integration with three video service providers (Mux, SignASL, VSL Labs)
- **Tiered Content Delivery**: Pre-recorded ASL content library, live ASL technical support, and interactive ASL components
- **Content Management**: Categorized ASL video library with metadata, transcripts, and difficulty levels

### White-Label System
- **Multi-tier Reseller Model**: Primary resellers can create sub-resellers and manage licensees
- **Customizable Branding**: Complete branding customization including logos, colors, domains, and content
- **Revenue Management**: Automated billing, commission calculation, and revenue distribution across tiers

## External Dependencies

### Video and Media Services
- **Mux Video Platform**: Primary video streaming and hosting service for ASL content delivery
- **SignASL Integration**: Specialized ASL content provider for financial terminology
- **VSL Labs API**: Interactive ASL components and live interpretation support

### Financial Service Integrations
- **April API**: Tax preparation and filing services with automated form completion
- **Boost Insurance**: Insurance product integration and policy management
- **Open Insurance API**: Standardized insurance data exchange for product comparison

### Infrastructure and Hosting
- **PostgreSQL Database**: Primary data storage with high availability configuration
- **AWS Cloud Services**: Scalable hosting infrastructure with CDN for video content
- **Stripe Payment Processing**: Subscription billing and payment management for white-label licensing

### Communication Platforms
- **Twilio**: SMS integration for mini-app command processing
- **Telegram Bot API**: Messaging platform integration with file upload capabilities
- **Discord API**: Community support and slash command integration
- **WhatsApp Business API**: Business messaging and document handling

### Development and Security
- **Flask-WTF**: CSRF protection and form handling
- **Werkzeug**: WSGI utilities and password hashing
- **ProxyFix Middleware**: Proper HTTPS handling behind load balancers
- **Environment-based Configuration**: Secure API key and credential management
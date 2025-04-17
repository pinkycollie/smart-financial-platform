# DEAF FIRST Multi-Tier White-Label Reseller System

This document provides an overview of the multi-tier white-label reseller system implemented for the DEAF FIRST platform. The system enables financial professionals serving the deaf community to license, customize, and distribute the platform through a hierarchical structure.

## System Architecture

The multi-tier white-label reseller system is designed with the following hierarchy:

1. **Primary Resellers**: Top-level distribution partners who license the platform directly from DEAF FIRST.
2. **Sub-Resellers**: Secondary distribution partners created under primary resellers.
3. **Licensees**: End users of the platform who provide services to deaf clients.

This hierarchical structure enables broader market reach while maintaining quality control and generating revenue at multiple levels.

## Core Features

### 1. Multi-Tier Distribution

- Primary resellers can create sub-resellers
- Commission rates cascade down the distribution tiers
- Customizable limits for number of sub-resellers and licensees
- Automated tracking of relationships across tiers

### 2. White-Label Branding

- Complete customization of branding elements (logos, colors, fonts)
- Custom domain and email settings
- Themed templates with preview capabilities
- Custom CSS and JavaScript for advanced customization
- Customizable content (welcome messages, legal disclaimers, etc.)

### 3. Revenue Management

- Automated billing and invoicing system
- Commission calculation and distribution across tiers
- Revenue reporting and forecasting
- Configurable commission rates by reseller tier

### 4. Module Management

- Tiered access to platform modules
- Customizable module selection by license tier
- Feature flags for enhanced capabilities
- ASL video support across all modules

## Reseller Tiers

The system supports multiple reseller tiers, each with different capabilities:

1. **Standard Tier**
   - Basic white-label capabilities
   - Limited number of licensees (25)
   - No sub-reseller capabilities
   - 20% commission rate

2. **Premium Tier**
   - Enhanced white-label capabilities
   - Larger number of licensees (100)
   - Limited sub-reseller capabilities (5)
   - Custom pricing capabilities
   - 30% commission rate

3. **Enterprise Tier**
   - Full white-label capabilities
   - Unlimited licensees
   - Unlimited sub-resellers
   - Module customization capabilities
   - Source code access
   - 40% commission rate

## Licensee Tiers

Licensees can be created at different tiers as well:

1. **Basic Tier**
   - Core financial tools
   - Limited client count (25)
   - Basic ASL video support
   - No white-label capabilities

2. **Professional Tier**
   - All basic features
   - Increased client limit (100)
   - Enhanced ASL video support
   - White-label branding capabilities

3. **Enterprise Tier**
   - All professional features
   - Unlimited clients
   - Custom module selection
   - Premium ASL video support
   - API access

## Implementation Details

### Database Structure

The system uses the following key database models:

- `Reseller`: Primary reseller information
- `ResellerBranding`: Branding settings for resellers
- `SubReseller`: Secondary distribution partners
- `SubResellerBranding`: Branding for sub-resellers
- `ResellerAdmin`: Admin users for reseller portals
- `ResellerRevenue`: Revenue tracking across tiers
- `ResellerTheme`: Predefined themes for white-label instances
- `Licensee`: End users of the platform
- `LicenseeBranding`: Branding settings for licensees
- `LicenseeFeatures`: Feature settings for licensees
- `LicenseeBillingHistory`: Billing records for licensees

### Services

The system is implemented through several service modules:

- `ResellerManagementService`: Handles reseller creation and management
- `ThemeManagementService`: Manages white-label themes
- `RevenueManagementService`: Handles billing and commission tracking
- `WhiteLabelService`: Manages white-label functionality for licensees

### Administrative Interface

The system includes comprehensive administrative interfaces:

- Reseller portal for managing licensees and sub-resellers
- Admin interface for platform administrators to manage resellers
- White-label preview capabilities
- Revenue and performance dashboards

## Getting Started

To explore the multi-tier white-label reseller system:

1. Run the database creation script: `python create_reseller_demo.py`
2. Start the demo application: `python route_test.py`
3. Visit the demo in your browser at http://localhost:5000/demo

## Implementation Files

The key files implementing this system include:

- `models_reseller.py`: Database models for the reseller system
- `models_licensing.py`: Database models for the licensing system
- `services/reseller/management.py`: Reseller management service
- `services/reseller/theme.py`: Theme management service
- `services/reseller/revenue.py`: Revenue management service
- `services/licensing/white_label.py`: White-label service
- `routes/reseller/portal.py`: Routes for the reseller portal
- `routes/reseller/management.py`: Routes for platform administrators
- `routes/demo.py`: Demo routes showcasing the system

## Deaf First Integration

The entire system is built with Deaf First principles, including:

- ASL video support throughout the platform
- Accessible UI design focused on visual communication
- Multi-modal communication channels for deaf users
- Design that prioritizes deaf accessibility from the beginning
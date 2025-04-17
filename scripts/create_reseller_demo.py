#!/usr/bin/env python3
"""
Demo script to create sample reseller data for the DEAF FIRST platform.
This creates a complete multi-tier reseller hierarchy with test data.
"""

import os
import uuid
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_app import app, db
from models_reseller import (
    Reseller, ResellerBranding, ResellerSubscription, Licensee, 
    LicenseeBranding, PortalUser, ResellerRevenue
)
from models_licensing import LicenseType, License, Feature
from models import User

def create_license_types():
    """Create license types for demo"""
    license_types = [
        {
            'name': 'Deaf First Standard',
            'code': 'deaf_first_standard',
            'description': 'Standard license for Deaf First platform',
            'max_users': 10,
            'max_storage_gb': 5,
            'is_white_label': False,
            'can_create_sublicenses': False,
            'suggested_price': 99.00,
            'included_features': ['basic_features', 'asl_videos']
        },
        {
            'name': 'Deaf First Professional',
            'code': 'deaf_first_pro',
            'description': 'Professional license with additional features',
            'max_users': 25,
            'max_storage_gb': 20,
            'is_white_label': True,
            'can_create_sublicenses': False,
            'suggested_price': 299.00,
            'included_features': ['basic_features', 'asl_videos', 'premium_features', 'api_access']
        },
        {
            'name': 'Deaf First Enterprise',
            'code': 'deaf_first_enterprise',
            'description': 'Enterprise license with all features',
            'max_users': 100,
            'max_storage_gb': 100,
            'is_white_label': True,
            'can_create_sublicenses': True,
            'suggested_price': 999.00,
            'included_features': ['basic_features', 'asl_videos', 'premium_features', 'api_access', 'enterprise_features']
        }
    ]
    
    created_types = []
    for lt_data in license_types:
        # Check if already exists
        if LicenseType.query.filter_by(code=lt_data['code']).first():
            continue
            
        license_type = LicenseType(
            name=lt_data['name'],
            code=lt_data['code'],
            description=lt_data['description'],
            max_users=lt_data['max_users'],
            max_storage_gb=lt_data['max_storage_gb'],
            is_white_label=lt_data['is_white_label'],
            can_create_sublicenses=lt_data['can_create_sublicenses'],
            suggested_price=lt_data['suggested_price'],
            included_features=lt_data['included_features']
        )
        db.session.add(license_type)
        created_types.append(license_type)
    
    db.session.commit()
    return created_types

def create_features():
    """Create features for demo"""
    features = [
        {
            'code': 'basic_features',
            'name': 'Basic Features',
            'description': 'Core platform functionality',
            'category': 'core',
            'icon': 'box'
        },
        {
            'code': 'asl_videos',
            'name': 'ASL Videos',
            'description': 'Access to ASL video library',
            'category': 'core',
            'icon': 'video'
        },
        {
            'code': 'premium_features',
            'name': 'Premium Features',
            'description': 'Advanced features for professionals',
            'category': 'premium',
            'icon': 'star'
        },
        {
            'code': 'api_access',
            'name': 'API Access',
            'description': 'Access to platform APIs',
            'category': 'developer',
            'icon': 'code'
        },
        {
            'code': 'enterprise_features',
            'name': 'Enterprise Features',
            'description': 'Features for enterprise users',
            'category': 'enterprise',
            'icon': 'building'
        }
    ]
    
    created_features = []
    for feature_data in features:
        # Check if already exists
        if Feature.query.filter_by(code=feature_data['code']).first():
            continue
            
        feature = Feature(
            code=feature_data['code'],
            name=feature_data['name'],
            description=feature_data['description'],
            category=feature_data['category'],
            icon=feature_data['icon']
        )
        db.session.add(feature)
        created_features.append(feature)
    
    db.session.commit()
    return created_features

def create_demo_user(username, email, first_name, last_name, is_admin=False):
    """Create demo user if not exists"""
    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    
    # Create new user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        account_type='admin' if is_admin else 'reseller'
    )
    user.set_password('password123')  # Demo password
    
    db.session.add(user)
    db.session.commit()
    
    return user

def create_primary_reseller(name, contact_email, user):
    """Create a primary reseller"""
    # Check if reseller already exists
    reseller = Reseller.query.filter_by(company_name=name).first()
    if reseller:
        return reseller
    
    # Create reseller code
    code = name.lower().replace(' ', '_')
    if Reseller.query.filter_by(reseller_code=code).first():
        code = f"{code}_{uuid.uuid4().hex[:6]}"
    
    # Create new reseller
    reseller = Reseller(
        company_name=name,
        reseller_code=code,
        contact_email=contact_email,
        owner_first_name=user.first_name,
        owner_last_name=user.last_name,
        business_type='corporation',
        tax_id='12-3456789',
        subdomain=code,
        white_label_enabled=True,
        status='active',
        approval_date=datetime.utcnow(),
        reseller_type='primary',
        commission_rate=0.0,
        external_id=f"reseller-{uuid.uuid4().hex[:12]}"
    )
    
    db.session.add(reseller)
    db.session.commit()
    
    # Create branding
    branding = ResellerBranding(
        reseller_id=reseller.id,
        logo_path=f"/static/images/resellers/{code}_logo.png",
        primary_color='#0d6efd',
        secondary_color='#6c757d',
        company_tagline=f"{name} - Empowering Deaf Communities",
        company_description=f"{name} provides specialized financial services for deaf and hard of hearing individuals."
    )
    
    db.session.add(branding)
    
    # Create subscription
    subscription = ResellerSubscription(
        reseller_id=reseller.id,
        plan_code='deaffirst-reseller-enterprise',
        status='active',
        external_id=f"sub-{uuid.uuid4().hex[:8]}",
        billing_period='month',
        price=999.00,
        start_date=datetime.utcnow() - timedelta(days=30),
        next_billing_date=datetime.utcnow() + timedelta(days=30),
        payment_method='credit_card',
        payment_status='paid'
    )
    
    db.session.add(subscription)
    
    # Create portal user
    portal_user = PortalUser(
        reseller_id=reseller.id,
        user_id=user.id,
        role='admin',
        permissions={'full_access': True}
    )
    
    db.session.add(portal_user)
    db.session.commit()
    
    return reseller

def create_secondary_reseller(name, contact_email, user, parent_reseller):
    """Create a secondary reseller (sub-reseller)"""
    # Check if reseller already exists
    reseller = Reseller.query.filter_by(company_name=name).first()
    if reseller:
        return reseller
    
    # Create reseller code
    code = name.lower().replace(' ', '_')
    if Reseller.query.filter_by(reseller_code=code).first():
        code = f"{code}_{uuid.uuid4().hex[:6]}"
    
    # Create new reseller
    reseller = Reseller(
        company_name=name,
        reseller_code=code,
        contact_email=contact_email,
        owner_first_name=user.first_name,
        owner_last_name=user.last_name,
        business_type='llc',
        tax_id='98-7654321',
        subdomain=code,
        white_label_enabled=True,
        status='active',
        approval_date=datetime.utcnow(),
        reseller_type='secondary',
        parent_id=parent_reseller.id,
        commission_rate=20.0,  # Parent gets 20% commission
        external_id=f"reseller-{uuid.uuid4().hex[:12]}"
    )
    
    db.session.add(reseller)
    db.session.commit()
    
    # Create branding
    branding = ResellerBranding(
        reseller_id=reseller.id,
        logo_path=f"/static/images/resellers/{code}_logo.png",
        primary_color='#28a745',
        secondary_color='#6c757d',
        company_tagline=f"{name} - Financial Services for the Deaf Community",
        company_description=f"{name} offers specialized financial planning and education for deaf and hard of hearing individuals."
    )
    
    db.session.add(branding)
    
    # Create subscription
    subscription = ResellerSubscription(
        reseller_id=reseller.id,
        plan_code='deaffirst-sublicensee-pro',
        status='active',
        external_id=f"sub-{uuid.uuid4().hex[:8]}",
        billing_period='month',
        price=299.00,
        start_date=datetime.utcnow() - timedelta(days=15),
        next_billing_date=datetime.utcnow() + timedelta(days=15),
        payment_method='credit_card',
        payment_status='paid'
    )
    
    db.session.add(subscription)
    
    # Create portal user
    portal_user = PortalUser(
        reseller_id=reseller.id,
        user_id=user.id,
        role='admin',
        permissions={'full_access': True}
    )
    
    db.session.add(portal_user)
    
    # Create revenue transaction for parent
    revenue = ResellerRevenue(
        reseller_id=parent_reseller.id,
        transaction_type='commission',
        amount=subscription.price * (reseller.commission_rate / 100),
        description=f"Commission from {name} subscription",
        parent_reseller_id=None,
        licensee_id=None,
        transaction_date=datetime.utcnow() - timedelta(days=15)
    )
    
    db.session.add(revenue)
    db.session.commit()
    
    return reseller

def create_licensee(name, contact_email, reseller, license_type_code='deaf_first_pro'):
    """Create a licensee (end customer)"""
    # Check if licensee already exists
    licensee = Licensee.query.filter_by(company_name=name, reseller_id=reseller.id).first()
    if licensee:
        return licensee
    
    # Get license type
    license_type = LicenseType.query.filter_by(code=license_type_code).first()
    if not license_type:
        raise ValueError(f"License type {license_type_code} not found")
    
    # Create licensee code
    code = name.lower().replace(' ', '_')
    license_key = f"DEAF-{uuid.uuid4().hex[:16].upper()}"
    
    # Create new licensee
    licensee = Licensee(
        reseller_id=reseller.id,
        company_name=name,
        license_key=license_key,
        contact_email=contact_email,
        contact_name=f"{name} Administrator",
        subdomain=code,
        white_label_enabled=license_type.is_white_label,
        license_type=license_type_code.split('_')[-1],  # standard, pro, enterprise
        license_status='active',
        max_users=license_type.max_users,
        features=license_type.included_features,
        start_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        external_id=f"licensee-{uuid.uuid4().hex[:12]}"
    )
    
    db.session.add(licensee)
    db.session.commit()
    
    # Create license
    license = License(
        license_key=license_key,
        licensee_id=licensee.id,
        license_type_id=license_type.id,
        status='active',
        activation_date=datetime.utcnow(),
        expiration_date=datetime.utcnow() + timedelta(days=365),
        current_user_count=random.randint(1, license_type.max_users)
    )
    
    db.session.add(license)
    
    # Create branding if white-label enabled
    if license_type.is_white_label:
        branding = LicenseeBranding(
            licensee_id=licensee.id,
            logo_path=f"/static/images/licensees/{code}_logo.png",
            primary_color=random.choice(['#0d6efd', '#28a745', '#dc3545', '#fd7e14', '#6f42c1']),
            secondary_color='#6c757d',
            company_tagline=f"{name} - Financial Empowerment",
            company_description=f"{name} is dedicated to providing accessible financial services and education."
        )
        
        db.session.add(branding)
    
    # Create revenue transaction for reseller
    price = license_type.suggested_price
    revenue = ResellerRevenue(
        reseller_id=reseller.id,
        transaction_type='subscription',
        amount=price,
        description=f"License subscription for {name}",
        licensee_id=licensee.id,
        transaction_date=datetime.utcnow()
    )
    
    db.session.add(revenue)
    
    # Create commission for parent if secondary reseller
    if reseller.parent_id and reseller.commission_rate > 0:
        parent_commission = ResellerRevenue(
            reseller_id=reseller.parent_id,
            transaction_type='commission',
            amount=price * (reseller.commission_rate / 100),
            description=f"Commission from {reseller.company_name} for {name}",
            licensee_id=licensee.id,
            parent_reseller_id=reseller.id,
            transaction_date=datetime.utcnow()
        )
        
        db.session.add(parent_commission)
    
    db.session.commit()
    
    return licensee

def create_demo_data():
    """Create demo reseller data with multi-tier structure"""
    print("Creating demo data for DEAF FIRST platform...")
    
    # Create license types and features
    print("Creating license types and features...")
    create_license_types()
    create_features()
    
    # Create admin user
    admin_user = create_demo_user(
        'admin', 'admin@deaffirst.com', 'Admin', 'User', is_admin=True
    )
    
    # Create primary resellers
    print("Creating primary resellers...")
    primary_resellers = []
    
    # Primary Reseller 1
    john = create_demo_user(
        'john_smith', 'john@signfinance.com', 'John', 'Smith'
    )
    sign_finance = create_primary_reseller(
        'Sign Finance', 'info@signfinance.com', john
    )
    primary_resellers.append(sign_finance)
    
    # Primary Reseller 2
    jennifer = create_demo_user(
        'jennifer_lee', 'jennifer@deafwealthadvisors.com', 'Jennifer', 'Lee'
    )
    deaf_wealth = create_primary_reseller(
        'Deaf Wealth Advisors', 'info@deafwealthadvisors.com', jennifer
    )
    primary_resellers.append(deaf_wealth)
    
    # Create secondary resellers (sub-resellers)
    print("Creating secondary resellers...")
    secondary_resellers = []
    
    # Secondary Resellers under Sign Finance
    michael = create_demo_user(
        'michael_davis', 'michael@asltax.com', 'Michael', 'Davis'
    )
    asl_tax = create_secondary_reseller(
        'ASL Tax Professionals', 'info@asltax.com', michael, sign_finance
    )
    secondary_resellers.append(asl_tax)
    
    sarah = create_demo_user(
        'sarah_johnson', 'sarah@signinsurance.com', 'Sarah', 'Johnson'
    )
    sign_insurance = create_secondary_reseller(
        'Sign Insurance Group', 'info@signinsurance.com', sarah, sign_finance
    )
    secondary_resellers.append(sign_insurance)
    
    # Secondary Resellers under Deaf Wealth Advisors
    robert = create_demo_user(
        'robert_chen', 'robert@deafinvestors.com', 'Robert', 'Chen'
    )
    deaf_investors = create_secondary_reseller(
        'Deaf Investors Alliance', 'info@deafinvestors.com', robert, deaf_wealth
    )
    secondary_resellers.append(deaf_investors)
    
    # Create licensees (end customers)
    print("Creating licensees...")
    
    # Licensees under Sign Finance (Primary)
    create_licensee(
        'Gallaudet Financial Services', 'admin@gallaudetfs.com', sign_finance, 'deaf_first_enterprise'
    )
    create_licensee(
        'NTID Credit Union', 'admin@ntidcu.com', sign_finance, 'deaf_first_pro'
    )
    create_licensee(
        'ASL Financial Literacy Center', 'admin@aslflc.org', sign_finance, 'deaf_first_standard'
    )
    
    # Licensees under ASL Tax Professionals (Secondary under Sign Finance)
    create_licensee(
        'Deaf Tax Relief', 'admin@deaftaxrelief.com', asl_tax, 'deaf_first_pro'
    )
    create_licensee(
        'ASL Bookkeeping', 'admin@aslbookkeeping.com', asl_tax, 'deaf_first_standard'
    )
    
    # Licensees under Sign Insurance Group (Secondary under Sign Finance)
    create_licensee(
        'Deaf Insurance Agency', 'admin@deafinsurance.com', sign_insurance, 'deaf_first_pro'
    )
    create_licensee(
        'ASL Benefits Consultants', 'admin@aslbenefits.com', sign_insurance, 'deaf_first_standard'
    )
    
    # Licensees under Deaf Wealth Advisors (Primary)
    create_licensee(
        'Deaf Retirement Planning', 'admin@deafretirement.com', deaf_wealth, 'deaf_first_enterprise'
    )
    create_licensee(
        'ASL Investment Group', 'admin@aslinvestment.com', deaf_wealth, 'deaf_first_pro'
    )
    
    # Licensees under Deaf Investors Alliance (Secondary under Deaf Wealth Advisors)
    create_licensee(
        'Deaf College Savings', 'admin@deafcollegesavings.com', deaf_investors, 'deaf_first_pro'
    )
    create_licensee(
        'ASL Estate Planning', 'admin@aslestateplanning.com', deaf_investors, 'deaf_first_standard'
    )
    
    print("Demo data creation complete!")
    print(f"Created {len(primary_resellers)} primary resellers")
    print(f"Created {len(secondary_resellers)} secondary resellers")
    print(f"Created {Licensee.query.count()} licensees")
    
    return {
        'primary_resellers': primary_resellers,
        'secondary_resellers': secondary_resellers
    }

if __name__ == '__main__':
    with app.app_context():
        create_demo_data()
"""
Demo script to create sample reseller data for the DEAF FIRST platform.
This creates a complete multi-tier reseller hierarchy with test data.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)

# Configure app
app.secret_key = "test-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

def create_demo_data():
    """Create demo reseller data with multi-tier structure"""
    from models_reseller import Reseller, ResellerBranding, SubReseller, SubResellerBranding, ResellerTheme, ResellerAdmin, ResellerRevenue
    from models_licensing import Licensee, LicenseeBranding, LicenseeFeatures, LicenseeBillingHistory
    from models import User
    from werkzeug.security import generate_password_hash
    
    print("Starting demo data creation...")
    
    # Check if data already exists
    if Reseller.query.filter_by(company_name="MbTQ Resellers").first():
        print("Demo data already exists.")
        return
    
    # Create themes
    print("Creating themes...")
    themes = [
        {
            "theme_name": "Financial Blue",
            "description": "Professional blue theme for financial services",
            "primary_color": "#003366",
            "secondary_color": "#0099CC",
            "accent_color": "#FF6600",
            "font_family": "Montserrat, sans-serif",
            "background_color": "#FFFFFF",
            "text_color": "#333333",
            "is_public": True
        },
        {
            "theme_name": "Modern Green",
            "description": "Fresh green theme with modern styling",
            "primary_color": "#006633",
            "secondary_color": "#66CC99",
            "accent_color": "#FFCC00",
            "font_family": "Roboto, sans-serif",
            "background_color": "#F9F9F9",
            "text_color": "#444444",
            "is_public": True
        },
        {
            "theme_name": "Deep Purple",
            "description": "Elegant purple theme with high contrast",
            "primary_color": "#663399",
            "secondary_color": "#9966CC",
            "accent_color": "#FFCC00",
            "font_family": "Raleway, sans-serif",
            "background_color": "#FFFFFF",
            "text_color": "#333333",
            "is_public": True
        }
    ]
    
    theme_ids = []
    for theme_data in themes:
        theme = ResellerTheme(**theme_data)
        db.session.add(theme)
        db.session.flush()
        theme_ids.append(theme.id)
    
    # Create main reseller (premium tier)
    print("Creating main reseller...")
    main_reseller = Reseller(
        company_name="MbTQ Resellers",
        primary_domain="mbtq-resellers.deaffirst.com",
        reseller_tier="premium",
        status="active",
        business_type="financial_advisor",
        contact_name="John Smith",
        contact_email="john@mbtqresellers.com",
        contact_phone="555-123-4567",
        license_key="DEAFFIRST-MBTQ12345",
        api_key="df_api_mbtq12345",
        license_start_date=datetime.utcnow().date(),
        license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
        billing_cycle="monthly",
        billing_amount=4999.00,
        next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
        max_sub_resellers=5,
        current_sub_resellers=2,
        max_licensees=100,
        current_licensees=3,
        commission_rate=30.0,
        can_customize_modules=False,
        can_set_pricing=True,
        can_create_sub_resellers=True,
        can_edit_source_code=False
    )
    db.session.add(main_reseller)
    db.session.flush()
    
    # Create branding for main reseller
    main_branding = ResellerBranding(
        reseller_id=main_reseller.id,
        primary_color="#0066CC",
        secondary_color="#00AA55",
        accent_color="#FF6600",
        font_family="Montserrat, sans-serif",
        company_tagline="MbTQ Resellers - Financial Solutions for the Deaf Community",
        welcome_message="Welcome to MbTQ Resellers Financial Platform",
        footer_text=f"© {datetime.utcnow().year} MbTQ Resellers. All rights reserved.",
        show_powered_by=True,
        facebook_url="https://facebook.com/mbtqresellers",
        twitter_url="https://twitter.com/mbtqresellers",
        linkedin_url="https://linkedin.com/company/mbtqresellers"
    )
    db.session.add(main_branding)
    
    # Create reseller admin user
    admin_user = User(
        email="john@mbtqresellers.com",
        password_hash=generate_password_hash("password123"),
        first_name="John",
        last_name="Smith",
        is_active=True,
        user_type="reseller_admin"
    )
    db.session.add(admin_user)
    db.session.flush()
    
    # Link admin to reseller
    admin = ResellerAdmin(
        reseller_id=main_reseller.id,
        user_id=admin_user.id,
        role="admin",
        is_primary=True,
        permissions={
            "view_reseller": True,
            "manage_reseller": True,
            "view_licensees": True,
            "manage_licensees": True,
            "view_revenue": True,
            "manage_revenue": True,
            "view_sub_resellers": True,
            "manage_sub_resellers": True,
            "manage_branding": True,
            "manage_admins": True
        }
    )
    db.session.add(admin)
    
    # Create sub-resellers
    print("Creating sub-resellers...")
    sub_resellers_data = [
        {
            "company_name": "ASL Financial",
            "subdomain": "asl-financial",
            "contact_name": "Sarah Johnson",
            "contact_email": "sarah@aslfinancial.com",
            "contact_phone": "555-234-5678",
            "max_licensees": 15,
            "commission_rate": 15.0
        },
        {
            "company_name": "Deaf Tax Pros",
            "subdomain": "deaf-tax-pros",
            "contact_name": "Michael Chen",
            "contact_email": "michael@deaftaxpros.com",
            "contact_phone": "555-345-6789",
            "max_licensees": 10,
            "commission_rate": 12.5
        }
    ]
    
    for i, sr_data in enumerate(sub_resellers_data):
        sub_reseller = SubReseller(
            parent_reseller_id=main_reseller.id,
            status="active",
            current_licensees=i+1,
            can_customize_branding=True,
            can_set_pricing=False,
            **sr_data
        )
        db.session.add(sub_reseller)
        db.session.flush()
        
        # Create branding for sub-reseller
        sub_branding = SubResellerBranding(
            sub_reseller_id=sub_reseller.id,
            primary_color="#" + format(int("0066CC", 16) + i*0x112233, "06x"),
            secondary_color="#" + format(int("00AA55", 16) + i*0x112233, "06x"),
            company_tagline=f"{sr_data['company_name']} - Specialized Financial Services for the Deaf",
            welcome_message=f"Welcome to {sr_data['company_name']}",
            show_powered_by=True
        )
        db.session.add(sub_branding)
    
    # Get sub-resellers for reference
    db.session.flush()
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=main_reseller.id).all()
    
    # Create direct licensees (under main reseller)
    print("Creating direct licensees...")
    direct_licensees_data = [
        {
            "company_name": "Austin Deaf Services",
            "subdomain": "austin-deaf",
            "license_tier": "professional",
            "contact_name": "Emma Wilson",
            "contact_email": "emma@austindeaf.com",
            "business_type": "financial_advisor",
            "current_clients": 45
        },
        {
            "company_name": "Houston ASL Finance",
            "subdomain": "houston-asl",
            "license_tier": "professional",
            "contact_name": "Robert Lee",
            "contact_email": "robert@houstonasl.com",
            "business_type": "insurance_agency",
            "current_clients": 32
        }
    ]
    
    for i, l_data in enumerate(direct_licensees_data):
        tier = l_data.pop("license_tier")
        tier_details = {
            "basic": {
                "price": 499.00,
                "white_label": False,
                "custom_modules": False,
                "max_clients": 25
            },
            "professional": {
                "price": 999.00,
                "white_label": True,
                "custom_modules": False,
                "max_clients": 100
            },
            "enterprise": {
                "price": 1999.00,
                "white_label": True,
                "custom_modules": True,
                "max_clients": 1000
            }
        }[tier]
        
        licensee = Licensee(
            reseller_id=main_reseller.id,
            license_tier=tier,
            status="active",
            license_key=f"DEAFFIRST-DIRECT{i+1}",
            api_key=f"df_api_direct{i+1}",
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            billing_cycle="monthly",
            billing_amount=tier_details["price"],
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
            max_clients=tier_details["max_clients"],
            white_label_enabled=tier_details["white_label"],
            custom_modules_enabled=tier_details["custom_modules"],
            **l_data
        )
        db.session.add(licensee)
        db.session.flush()
        
        # Create branding for licensee
        if tier_details["white_label"]:
            licensee_branding = LicenseeBranding(
                licensee_id=licensee.id,
                primary_color="#" + format(int("0066CC", 16) + i*0x223344, "06x"),
                secondary_color="#" + format(int("00AA55", 16) + i*0x223344, "06x"),
                company_tagline=f"{l_data['company_name']} - Financial Services",
                welcome_message=f"Welcome to {l_data['company_name']}",
                footer_text=f"© {datetime.utcnow().year} {l_data['company_name']}. All rights reserved.",
                show_powered_by=True
            )
            db.session.add(licensee_branding)
        
        # Create features
        licensee_features = LicenseeFeatures(
            licensee_id=licensee.id,
            enabled_modules=["tax_preparation", "insurance_services", "financial_education"],
            enhanced_asl_support=tier != "basic",
            advanced_analytics=tier == "enterprise",
            premium_templates=tier != "basic",
            priority_support=tier != "basic",
            storage_limit_gb=5 * (1 if tier == "basic" else (2 if tier == "professional" else 5))
        )
        db.session.add(licensee_features)
        
        # Create billing history
        for j in range(3):
            billing_date = datetime.utcnow().date() - timedelta(days=j*30)
            billing = LicenseeBillingHistory(
                licensee_id=licensee.id,
                billing_date=billing_date,
                amount=tier_details["price"],
                invoice_number=f"INV-{licensee.id}-{billing_date.strftime('%Y%m%d')}",
                payment_status="paid",
                period_start=billing_date,
                period_end=billing_date + timedelta(days=30),
                payment_method="credit_card",
                transaction_id=f"txn_{uuid.uuid4().hex[:10]}"
            )
            db.session.add(billing)
    
    # Create sub-reseller licensees
    print("Creating sub-reseller licensees...")
    sub_licensees_data = [
        {
            "company_name": "Dallas Deaf Taxes",
            "subdomain": "dallas-deaf",
            "license_tier": "basic",
            "contact_name": "Lisa Kim",
            "contact_email": "lisa@dallasdeaf.com",
            "business_type": "tax_preparer",
            "current_clients": 18,
            "sub_reseller_id": sub_resellers[0].id
        },
        {
            "company_name": "San Antonio ASL Finance",
            "subdomain": "sa-asl",
            "license_tier": "professional",
            "contact_name": "James Martinez",
            "contact_email": "james@saasl.com",
            "business_type": "financial_advisor",
            "current_clients": 27,
            "sub_reseller_id": sub_resellers[1].id
        }
    ]
    
    for i, l_data in enumerate(sub_licensees_data):
        sub_reseller_id = l_data.pop("sub_reseller_id")
        tier = l_data.pop("license_tier")
        tier_details = {
            "basic": {
                "price": 499.00,
                "white_label": False,
                "custom_modules": False,
                "max_clients": 25
            },
            "professional": {
                "price": 999.00,
                "white_label": True,
                "custom_modules": False,
                "max_clients": 100
            },
            "enterprise": {
                "price": 1999.00,
                "white_label": True,
                "custom_modules": True,
                "max_clients": 1000
            }
        }[tier]
        
        licensee = Licensee(
            reseller_id=main_reseller.id,
            sub_reseller_id=sub_reseller_id,
            license_tier=tier,
            status="active",
            license_key=f"DEAFFIRST-SUB{i+1}",
            api_key=f"df_api_sub{i+1}",
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            billing_cycle="monthly",
            billing_amount=tier_details["price"],
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
            max_clients=tier_details["max_clients"],
            white_label_enabled=tier_details["white_label"],
            custom_modules_enabled=tier_details["custom_modules"],
            **l_data
        )
        db.session.add(licensee)
        db.session.flush()
        
        # Create branding for licensee if white label enabled
        if tier_details["white_label"]:
            licensee_branding = LicenseeBranding(
                licensee_id=licensee.id,
                primary_color="#" + format(int("0066CC", 16) + (i+2)*0x223344, "06x"),
                secondary_color="#" + format(int("00AA55", 16) + (i+2)*0x223344, "06x"),
                company_tagline=f"{l_data['company_name']} - Financial Services",
                welcome_message=f"Welcome to {l_data['company_name']}",
                footer_text=f"© {datetime.utcnow().year} {l_data['company_name']}. All rights reserved.",
                show_powered_by=True
            )
            db.session.add(licensee_branding)
        
        # Create features
        licensee_features = LicenseeFeatures(
            licensee_id=licensee.id,
            enabled_modules=["tax_preparation", "insurance_services", "financial_education"],
            enhanced_asl_support=tier != "basic",
            advanced_analytics=tier == "enterprise",
            premium_templates=tier != "basic",
            priority_support=tier != "basic",
            storage_limit_gb=5 * (1 if tier == "basic" else (2 if tier == "professional" else 5))
        )
        db.session.add(licensee_features)
    
    # Create revenue transactions
    print("Creating revenue transactions...")
    # Direct licensee transactions
    licensees = Licensee.query.filter_by(reseller_id=main_reseller.id, sub_reseller_id=None).all()
    for licensee in licensees:
        # Initial license purchase
        transaction = ResellerRevenue(
            reseller_id=main_reseller.id,
            licensee_id=licensee.id,
            amount=licensee.billing_amount,
            commission_amount=licensee.billing_amount * (main_reseller.commission_rate / 100),
            transaction_type="new_license",
            payment_status="paid",
            transaction_date=licensee.license_start_date
        )
        db.session.add(transaction)
        
        # Monthly billing (3 months)
        for i in range(1, 4):
            transaction_date = licensee.license_start_date + timedelta(days=30*i)
            if transaction_date > datetime.utcnow().date():
                continue
                
            transaction = ResellerRevenue(
                reseller_id=main_reseller.id,
                licensee_id=licensee.id,
                amount=licensee.billing_amount,
                commission_amount=licensee.billing_amount * (main_reseller.commission_rate / 100),
                transaction_type="renewal",
                payment_status="paid",
                transaction_date=transaction_date
            )
            db.session.add(transaction)
    
    # Sub-reseller licensee transactions
    sub_licensees = Licensee.query.filter(Licensee.reseller_id == main_reseller.id, Licensee.sub_reseller_id != None).all()
    for licensee in sub_licensees:
        sub_reseller = SubReseller.query.get(licensee.sub_reseller_id)
        
        # Initial license purchase
        transaction = ResellerRevenue(
            reseller_id=main_reseller.id,
            sub_reseller_id=sub_reseller.id,
            licensee_id=licensee.id,
            amount=licensee.billing_amount,
            commission_amount=licensee.billing_amount * ((main_reseller.commission_rate - sub_reseller.commission_rate) / 100),
            transaction_type="new_license",
            payment_status="paid",
            transaction_date=licensee.license_start_date
        )
        db.session.add(transaction)
        
        # Monthly billing (2 months)
        for i in range(1, 3):
            transaction_date = licensee.license_start_date + timedelta(days=30*i)
            if transaction_date > datetime.utcnow().date():
                continue
                
            transaction = ResellerRevenue(
                reseller_id=main_reseller.id,
                sub_reseller_id=sub_reseller.id,
                licensee_id=licensee.id,
                amount=licensee.billing_amount,
                commission_amount=licensee.billing_amount * ((main_reseller.commission_rate - sub_reseller.commission_rate) / 100),
                transaction_type="renewal",
                payment_status="paid",
                transaction_date=transaction_date
            )
            db.session.add(transaction)
    
    # Commit all changes
    db.session.commit()
    print("Demo data created successfully!")

if __name__ == "__main__":
    # Run the demo data creation function
    with app.app_context():
        import uuid  # Imported here for UUID generation
        create_demo_data()
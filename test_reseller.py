from flask import Flask, render_template, redirect, url_for
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

# Define route
@app.route('/')
def test_reseller():
    """Test route to create and display reseller data"""
    from models_reseller import Reseller, ResellerBranding, SubReseller, ResellerAdmin, ResellerRevenue
    from models_licensing import Licensee, LicenseeBranding
    
    # Check if test reseller exists
    reseller = Reseller.query.filter_by(company_name="Test Reseller").first()
    
    if not reseller:
        print("Creating test reseller...")
        # Create a test reseller
        reseller = Reseller(
            company_name="Test Reseller",
            primary_domain="test.deaffirst.com",
            reseller_tier="premium",
            status="active",
            contact_name="Test User",
            contact_email="test@example.com",
            contact_phone="555-1234",
            business_type="financial_advisor",
            license_key="DEAFFIRST-TEST12345",
            api_key="df_api_test12345",
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            billing_cycle="monthly",
            billing_amount=4999.00,
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
            max_sub_resellers=5,
            current_sub_resellers=1,
            max_licensees=100,
            current_licensees=3,
            commission_rate=30.0,
            can_customize_modules=False,
            can_set_pricing=True,
            can_create_sub_resellers=True,
            can_edit_source_code=False
        )
        db.session.add(reseller)
        db.session.flush()
        
        # Create branding
        branding = ResellerBranding(
            reseller_id=reseller.id,
            primary_color="#0066CC",
            secondary_color="#00AA55",
            company_tagline="Test Reseller - Financial Services for the Deaf Community",
            welcome_message=f"Welcome to Test Reseller's Financial Platform",
            footer_text=f"© {datetime.utcnow().year} Test Reseller. All rights reserved.",
            show_powered_by=True
        )
        db.session.add(branding)
        
        # Create a sub-reseller
        sub_reseller = SubReseller(
            parent_reseller_id=reseller.id,
            company_name="Test Sub-Reseller",
            subdomain="testsub",
            status="active",
            contact_name="Sub Test User",
            contact_email="testsub@example.com",
            contact_phone="555-5678",
            max_licensees=10,
            current_licensees=1,
            commission_rate=10.0,
            can_customize_branding=True,
            can_set_pricing=False
        )
        db.session.add(sub_reseller)
        
        # Create direct licensees
        for i in range(2):
            licensee = Licensee(
                company_name=f"Direct Licensee {i+1}",
                subdomain=f"direct{i+1}",
                license_tier="professional",
                status="active",
                contact_name=f"Licensee User {i+1}",
                contact_email=f"licensee{i+1}@example.com",
                reseller_id=reseller.id,
                license_key=f"DEAFFIRST-DIRECT{i+1}",
                api_key=f"df_api_direct{i+1}",
                license_start_date=datetime.utcnow().date(),
                license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
                billing_cycle="monthly",
                billing_amount=999.00,
                next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
                max_clients=100,
                current_clients=i*5,
                white_label_enabled=True,
                custom_modules_enabled=False
            )
            db.session.add(licensee)
            
            # Add branding
            licensee_branding = LicenseeBranding(
                licensee_id=licensee.id,
                primary_color="#0066CC",
                secondary_color="#00AA55",
                company_tagline=f"Direct Licensee {i+1} - Financial Services"
            )
            db.session.add(licensee_branding)
        
        # Create sub-reseller licensee
        sub_licensee = Licensee(
            company_name="Sub Licensee",
            subdomain="sublicensee",
            license_tier="basic",
            status="active",
            contact_name="Sub Licensee User",
            contact_email="sublicensee@example.com",
            reseller_id=reseller.id,
            sub_reseller_id=sub_reseller.id,
            license_key="DEAFFIRST-SUB12345",
            api_key="df_api_sub12345",
            license_start_date=datetime.utcnow().date(),
            license_end_date=(datetime.utcnow() + timedelta(days=365)).date(),
            billing_cycle="monthly",
            billing_amount=499.00,
            next_billing_date=(datetime.utcnow() + timedelta(days=30)).date(),
            max_clients=25,
            current_clients=3,
            white_label_enabled=False,
            custom_modules_enabled=False
        )
        db.session.add(sub_licensee)
        
        # Create some revenue transactions
        transaction_types = ["new_license", "renewal", "upgrade"]
        for i in range(3):
            transaction = ResellerRevenue(
                reseller_id=reseller.id,
                amount=500 * (i+1),
                commission_amount=500 * (i+1) * 0.3,  # 30% commission
                transaction_type=transaction_types[i],
                payment_status="paid",
                transaction_date=datetime.utcnow() - timedelta(days=i*7)
            )
            db.session.add(transaction)
        
        # Create sub-reseller transaction
        sub_transaction = ResellerRevenue(
            reseller_id=reseller.id,
            sub_reseller_id=sub_reseller.id,
            licensee_id=sub_licensee.id,
            amount=499.00,
            commission_amount=499.00 * 0.2,  # 20% effective commission (30% - 10%)
            transaction_type="new_license",
            payment_status="paid",
            transaction_date=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add(sub_transaction)
        
        db.session.commit()
        print("Test data created successfully!")
    
    # Get reseller stats
    stats = {
        'counts': {
            'direct_licensees': Licensee.query.filter_by(reseller_id=reseller.id, sub_reseller_id=None).count(),
            'sub_resellers': SubReseller.query.filter_by(parent_reseller_id=reseller.id).count(),
            'total_licensees': Licensee.query.filter_by(reseller_id=reseller.id).count(),
            'total_clients': sum(l.current_clients for l in Licensee.query.filter_by(reseller_id=reseller.id).all())
        },
        'limits': {
            'max_sub_resellers': reseller.max_sub_resellers,
            'max_licensees': reseller.max_licensees
        },
        'revenue': {
            'monthly': sum(t.amount for t in ResellerRevenue.query.filter_by(reseller_id=reseller.id).all()),
            'commission': sum(t.commission_amount for t in ResellerRevenue.query.filter_by(reseller_id=reseller.id).all())
        }
    }
    
    # Get direct licensees
    direct_licensees = Licensee.query.filter_by(reseller_id=reseller.id, sub_reseller_id=None).all()
    
    # Get recent transactions
    recent_transactions = ResellerRevenue.query.filter_by(reseller_id=reseller.id).order_by(ResellerRevenue.transaction_date.desc()).limit(5).all()
    
    # Get sub-resellers
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=reseller.id).all()
    
    # Render reseller dashboard
    return render_template(
        'reseller/dashboard.html',
        reseller=reseller,
        stats=stats,
        recent_transactions=recent_transactions,
        direct_licensees=direct_licensees,
        sub_resellers=sub_resellers
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
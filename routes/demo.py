"""
Demo routes to showcase the DEAF FIRST platform's white-label reseller system.
"""

from flask import Blueprint, render_template, jsonify, redirect, url_for, request, flash
from simple_app import db
from services.reseller.management import reseller_management_service
from services.reseller.theme import theme_management_service
from services.reseller.revenue import revenue_management_service
from services.licensing.white_label import white_label_service
from models_reseller import Reseller, SubReseller, ResellerAdmin, ResellerRevenue, ResellerTheme
from models_licensing import Licensee, LicenseeFeatures

# Create blueprint
demo_bp = Blueprint('demo', __name__, url_prefix='/demo')

@demo_bp.route('/')
def index():
    """Demo home page showcasing the white-label reseller system"""
    return render_template('demo/index.html')

@demo_bp.route('/reseller-system')
def reseller_system():
    """Overview of the multi-tier reseller system"""
    # Get reseller stats
    main_reseller = Reseller.query.filter_by(company_name="MbTQ Resellers").first()
    
    if not main_reseller:
        flash("Demo data not found. Please run the create_reseller_demo.py script first.", "warning")
        return redirect(url_for('demo.index'))
    
    # Get reseller hierarchy
    reseller_hierarchy = {
        "main_reseller": {
            "id": main_reseller.id,
            "company_name": main_reseller.company_name,
            "tier": main_reseller.reseller_tier,
            "licensee_count": Licensee.query.filter_by(reseller_id=main_reseller.id, sub_reseller_id=None).count(),
            "sub_reseller_count": SubReseller.query.filter_by(parent_reseller_id=main_reseller.id).count()
        },
        "sub_resellers": [],
        "direct_licensees": [],
        "sub_licensees": []
    }
    
    # Get sub-resellers
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=main_reseller.id).all()
    for sub in sub_resellers:
        sub_licensee_count = Licensee.query.filter_by(sub_reseller_id=sub.id).count()
        reseller_hierarchy["sub_resellers"].append({
            "id": sub.id,
            "company_name": sub.company_name,
            "commission_rate": sub.commission_rate,
            "licensee_count": sub_licensee_count
        })
    
    # Get direct licensees
    direct_licensees = Licensee.query.filter_by(reseller_id=main_reseller.id, sub_reseller_id=None).all()
    for licensee in direct_licensees:
        reseller_hierarchy["direct_licensees"].append({
            "id": licensee.id,
            "company_name": licensee.company_name,
            "tier": licensee.license_tier,
            "white_label": licensee.white_label_enabled,
            "client_count": licensee.current_clients
        })
    
    # Get sub-reseller licensees
    sub_licensees = Licensee.query.filter(Licensee.reseller_id == main_reseller.id, Licensee.sub_reseller_id != None).all()
    for licensee in sub_licensees:
        sub_reseller = SubReseller.query.get(licensee.sub_reseller_id)
        reseller_hierarchy["sub_licensees"].append({
            "id": licensee.id,
            "company_name": licensee.company_name,
            "tier": licensee.license_tier,
            "white_label": licensee.white_label_enabled,
            "client_count": licensee.current_clients,
            "sub_reseller_name": sub_reseller.company_name if sub_reseller else "Unknown"
        })
    
    # Revenue stats
    revenue_stats = {
        "total_monthly_revenue": sum(l.billing_amount for l in Licensee.query.filter_by(reseller_id=main_reseller.id).all()),
        "direct_revenue": sum(l.billing_amount for l in direct_licensees),
        "sub_reseller_revenue": sum(l.billing_amount for l in sub_licensees),
        "total_transactions": ResellerRevenue.query.filter_by(reseller_id=main_reseller.id).count(),
        "commission_earned": sum(t.commission_amount for t in ResellerRevenue.query.filter_by(reseller_id=main_reseller.id).all())
    }
    
    # Module usage
    all_licensees = Licensee.query.filter_by(reseller_id=main_reseller.id).all()
    licensee_count = len(all_licensees)
    module_stats = {}
    
    for licensee in all_licensees:
        features = LicenseeFeatures.query.filter_by(licensee_id=licensee.id).first()
        if features and features.enabled_modules:
            for module in features.enabled_modules:
                if module not in module_stats:
                    module_stats[module] = 0
                module_stats[module] += 1
    
    # Convert to percentages
    for module, count in module_stats.items():
        module_stats[module] = round((count / licensee_count) * 100)
    
    # Themes data
    themes = ResellerTheme.query.filter(ResellerTheme.is_public == True).all()
    themes_data = [
        {
            "id": theme.id,
            "name": theme.theme_name,
            "primary_color": theme.primary_color,
            "secondary_color": theme.secondary_color
        }
        for theme in themes
    ]
    
    return render_template(
        'demo/reseller_system.html',
        reseller_hierarchy=reseller_hierarchy,
        revenue_stats=revenue_stats,
        module_stats=module_stats,
        themes=themes_data
    )

@demo_bp.route('/white-label/<int:licensee_id>')
def white_label_preview(licensee_id):
    """Preview a white-label instance"""
    licensee = Licensee.query.get_or_404(licensee_id)
    
    if not licensee.white_label_enabled:
        flash("This licensee does not have white-label enabled.", "warning")
        return redirect(url_for('demo.reseller_system'))
    
    # Get branding
    branding = licensee.branding
    
    # Get modules
    modules = white_label_service.get_allowed_modules(licensee.id)
    
    # Get some mock clients for demonstration
    mock_clients = [
        {"name": "Jane Smith", "type": "Individual", "joined": "2025-01-15", "products": 3},
        {"name": "ABC Deaf Services", "type": "Business", "joined": "2025-02-03", "products": 5},
        {"name": "John Johnson", "type": "Individual", "joined": "2025-02-28", "products": 2},
        {"name": "ASL Interpreting Co.", "type": "Business", "joined": "2025-03-10", "products": 4}
    ]
    
    # Create context with branding applied
    context = white_label_service.apply_licensee_branding(licensee.id)
    
    context.update({
        "licensee": licensee,
        "branding": branding,
        "modules": modules,
        "clients": mock_clients
    })
    
    return render_template('demo/white_label_preview.html', **context)

@demo_bp.route('/api/theme/<int:theme_id>')
def api_theme_preview(theme_id):
    """Get theme preview data"""
    preview = theme_management_service.get_theme_preview(theme_id)
    return jsonify(preview)

@demo_bp.route('/api/reseller-tiers')
def api_reseller_tiers():
    """Get reseller tier information"""
    tiers = reseller_management_service.get_reseller_tiers()
    return jsonify(tiers)

@demo_bp.route('/api/license-tiers')
def api_license_tiers():
    """Get license tier information"""
    tiers = white_label_service.get_license_tiers()
    return jsonify(tiers)

@demo_bp.route('/api/modules')
def api_modules():
    """Get module information"""
    modules = white_label_service.get_available_modules()
    return jsonify(modules)
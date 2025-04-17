"""
Reseller management routes for DEAF FIRST platform.
Enables platform administrators to manage resellers.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, abort, g
from flask_login import login_required, current_user
from functools import wraps
from simple_app import db
from models_reseller import Reseller, SubReseller, ResellerAdmin, ResellerRevenue, ResellerTheme
from models_licensing import Licensee
from services.reseller.management import reseller_management_service
from services.reseller.theme import theme_management_service
from services.reseller.revenue import revenue_management_service

# Create blueprint
reseller_management_bp = Blueprint('reseller_management', __name__, url_prefix='/admin/resellers')

# Helper function to check if user is a platform admin
def platform_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user is a platform admin
        if not current_user.is_admin:
            flash('You do not have permission to access this area.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@reseller_management_bp.route('/')
@login_required
@platform_admin_required
def index():
    """Reseller management dashboard"""
    # Get all resellers
    resellers = Reseller.query.all()
    
    # Get reseller counts
    standard_count = Reseller.query.filter_by(reseller_tier='standard').count()
    premium_count = Reseller.query.filter_by(reseller_tier='premium').count()
    enterprise_count = Reseller.query.filter_by(reseller_tier='enterprise').count()
    
    # Get top resellers by revenue
    top_revenue_resellers = Reseller.query.join(ResellerRevenue).group_by(Reseller.id).order_by(
        db.func.sum(ResellerRevenue.amount).desc()
    ).limit(5).all()
    
    # Get top resellers by licensees
    top_licensee_resellers = Reseller.query.order_by(Reseller.current_licensees.desc()).limit(5).all()
    
    return render_template(
        'admin/resellers/index.html',
        resellers=resellers,
        counts={
            'total': len(resellers),
            'standard': standard_count,
            'premium': premium_count,
            'enterprise': enterprise_count
        },
        top_revenue_resellers=top_revenue_resellers,
        top_licensee_resellers=top_licensee_resellers
    )

@reseller_management_bp.route('/create', methods=['GET', 'POST'])
@login_required
@platform_admin_required
def create():
    """Create a new reseller"""
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        contact_email = request.form.get('contact_email')
        reseller_tier = request.form.get('reseller_tier')
        
        # Additional fields
        contact_name = request.form.get('contact_name')
        contact_phone = request.form.get('contact_phone')
        business_type = request.form.get('business_type')
        
        try:
            # Create reseller
            reseller = reseller_management_service.create_reseller(
                company_name=company_name,
                contact_email=contact_email,
                reseller_tier=reseller_tier,
                contact_name=contact_name,
                contact_phone=contact_phone,
                business_type=business_type
            )
            
            # Create primary admin if email provided
            admin_email = request.form.get('admin_email')
            admin_first_name = request.form.get('admin_first_name')
            admin_last_name = request.form.get('admin_last_name')
            
            if admin_email and admin_first_name and admin_last_name:
                reseller_management_service.create_reseller_admin(
                    reseller_id=reseller.id,
                    email=admin_email,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    role='admin',
                    is_primary=True
                )
            
            flash(f'Reseller {reseller.company_name} created successfully.', 'success')
            return redirect(url_for('reseller_management.view', reseller_id=reseller.id))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    # Get reseller tiers for the form
    reseller_tiers = reseller_management_service.get_reseller_tiers()
    
    # Business types
    business_types = [
        ('financial_advisor', 'Financial Advisor'),
        ('insurance_agency', 'Insurance Agency'),
        ('tax_preparer', 'Tax Preparer'),
        ('accounting_firm', 'Accounting Firm'),
        ('education_provider', 'Education Provider'),
        ('other', 'Other')
    ]
    
    return render_template(
        'admin/resellers/create.html',
        reseller_tiers=reseller_tiers,
        business_types=business_types
    )

@reseller_management_bp.route('/<int:reseller_id>')
@login_required
@platform_admin_required
def view(reseller_id):
    """View reseller details"""
    # Get reseller
    reseller = Reseller.query.get_or_404(reseller_id)
    
    # Get reseller stats
    stats = reseller_management_service.get_reseller_stats(reseller.id)
    
    # Get admins
    admins = ResellerAdmin.query.filter_by(reseller_id=reseller.id).all()
    
    # Get recent revenue transactions
    recent_transactions = ResellerRevenue.query.filter_by(
        reseller_id=reseller.id
    ).order_by(ResellerRevenue.transaction_date.desc()).limit(5).all()
    
    # Get direct licensees
    direct_licensees = Licensee.query.filter_by(
        reseller_id=reseller.id, 
        sub_reseller_id=None
    ).order_by(Licensee.created_at.desc()).limit(5).all()
    
    # Get sub-resellers
    sub_resellers = SubReseller.query.filter_by(
        parent_reseller_id=reseller.id
    ).order_by(SubReseller.created_at.desc()).all()
    
    return render_template(
        'admin/resellers/view.html',
        reseller=reseller,
        stats=stats,
        admins=admins,
        recent_transactions=recent_transactions,
        direct_licensees=direct_licensees,
        sub_resellers=sub_resellers
    )

@reseller_management_bp.route('/<int:reseller_id>/edit', methods=['GET', 'POST'])
@login_required
@platform_admin_required
def edit(reseller_id):
    """Edit reseller"""
    # Get reseller
    reseller = Reseller.query.get_or_404(reseller_id)
    
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        contact_email = request.form.get('contact_email')
        reseller_tier = request.form.get('reseller_tier')
        status = request.form.get('status')
        
        # Additional fields
        contact_name = request.form.get('contact_name')
        contact_phone = request.form.get('contact_phone')
        business_type = request.form.get('business_type')
        
        # Specific limit overrides (for enterprise)
        max_licensees = request.form.get('max_licensees')
        max_sub_resellers = request.form.get('max_sub_resellers')
        commission_rate = request.form.get('commission_rate')
        
        # Feature flags
        can_customize_modules = request.form.get('can_customize_modules') == 'on'
        can_set_pricing = request.form.get('can_set_pricing') == 'on'
        can_create_sub_resellers = request.form.get('can_create_sub_resellers') == 'on'
        can_edit_source_code = request.form.get('can_edit_source_code') == 'on'
        
        try:
            # Update reseller
            update_data = {
                'company_name': company_name,
                'contact_email': contact_email,
                'reseller_tier': reseller_tier,
                'status': status,
                'contact_name': contact_name,
                'contact_phone': contact_phone,
                'business_type': business_type,
                'can_customize_modules': can_customize_modules,
                'can_set_pricing': can_set_pricing,
                'can_create_sub_resellers': can_create_sub_resellers,
                'can_edit_source_code': can_edit_source_code
            }
            
            # Add numeric fields if provided
            if max_licensees:
                update_data['max_licensees'] = int(max_licensees)
            
            if max_sub_resellers:
                update_data['max_sub_resellers'] = int(max_sub_resellers)
            
            if commission_rate:
                update_data['commission_rate'] = float(commission_rate)
            
            # Update reseller
            reseller = reseller_management_service.update_reseller(
                reseller_id=reseller.id,
                **update_data
            )
            
            flash(f'Reseller {reseller.company_name} updated successfully.', 'success')
            return redirect(url_for('reseller_management.view', reseller_id=reseller.id))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    # Get reseller tiers for the form
    reseller_tiers = reseller_management_service.get_reseller_tiers()
    
    # Business types
    business_types = [
        ('financial_advisor', 'Financial Advisor'),
        ('insurance_agency', 'Insurance Agency'),
        ('tax_preparer', 'Tax Preparer'),
        ('accounting_firm', 'Accounting Firm'),
        ('education_provider', 'Education Provider'),
        ('other', 'Other')
    ]
    
    # Status options
    status_options = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired')
    ]
    
    return render_template(
        'admin/resellers/edit.html',
        reseller=reseller,
        reseller_tiers=reseller_tiers,
        business_types=business_types,
        status_options=status_options
    )

@reseller_management_bp.route('/<int:reseller_id>/branding', methods=['GET', 'POST'])
@login_required
@platform_admin_required
def branding(reseller_id):
    """Edit reseller branding"""
    # Get reseller
    reseller = Reseller.query.get_or_404(reseller_id)
    
    if request.method == 'POST':
        # Get form data
        form_data = request.form.to_dict()
        
        # Handle file uploads
        logo_file = request.files.get('logo')
        logo_light_file = request.files.get('logo_light')
        
        if logo_file and logo_file.filename:
            reseller_management_service.upload_logo(
                reseller_id=reseller.id,
                logo_file=logo_file,
                light_version=False
            )
        
        if logo_light_file and logo_light_file.filename:
            reseller_management_service.upload_logo(
                reseller_id=reseller.id,
                logo_file=logo_light_file,
                light_version=True
            )
        
        # Update branding
        branding_fields = [
            'primary_color', 'secondary_color', 'accent_color', 'font_family',
            'company_tagline', 'welcome_message', 'footer_text', 'legal_disclaimer',
            'show_powered_by', 'custom_css', 'custom_javascript',
            'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'
        ]
        
        branding_data = {k: form_data.get(k) for k in branding_fields if k in form_data}
        
        # Convert checkbox to boolean
        if 'show_powered_by' in branding_data:
            branding_data['show_powered_by'] = branding_data['show_powered_by'] == 'on'
        
        # Update branding
        reseller_management_service.update_reseller_branding(reseller.id, **branding_data)
        
        flash('Branding updated successfully.', 'success')
        return redirect(url_for('reseller_management.branding', reseller_id=reseller.id))
    
    # Get branding
    branding = reseller.branding
    
    # Get available themes
    themes = theme_management_service.get_available_themes(reseller.id)
    
    return render_template(
        'admin/resellers/branding.html',
        reseller=reseller,
        branding=branding,
        themes=themes
    )

@reseller_management_bp.route('/<int:reseller_id>/revenue')
@login_required
@platform_admin_required
def revenue(reseller_id):
    """View reseller revenue"""
    # Get reseller
    reseller = Reseller.query.get_or_404(reseller_id)
    
    # Get date range from query params
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        except ValueError:
            pass
    
    # Get revenue data
    revenue_data = revenue_management_service.get_reseller_revenue(
        reseller_id=reseller.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return render_template(
        'admin/resellers/revenue.html',
        reseller=reseller,
        revenue_data=revenue_data,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

@reseller_management_bp.route('/themes')
@login_required
@platform_admin_required
def themes():
    """Manage global themes"""
    # Get all themes
    global_themes = ResellerTheme.query.filter(ResellerTheme.reseller_id.is_(None)).all()
    custom_themes = ResellerTheme.query.filter(ResellerTheme.reseller_id.isnot(None), ResellerTheme.is_public.is_(True)).all()
    
    return render_template(
        'admin/resellers/themes.html',
        global_themes=global_themes,
        custom_themes=custom_themes
    )

@reseller_management_bp.route('/themes/create', methods=['GET', 'POST'])
@login_required
@platform_admin_required
def create_theme():
    """Create a new global theme"""
    if request.method == 'POST':
        # Get form data
        theme_name = request.form.get('theme_name')
        description = request.form.get('description')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        accent_color = request.form.get('accent_color')
        font_family = request.form.get('font_family')
        background_color = request.form.get('background_color')
        text_color = request.form.get('text_color')
        
        try:
            # Create theme
            theme = theme_management_service.create_theme(
                theme_name=theme_name,
                description=description,
                primary_color=primary_color,
                secondary_color=secondary_color,
                accent_color=accent_color,
                font_family=font_family,
                background_color=background_color,
                text_color=text_color,
                is_public=True
            )
            
            flash(f'Theme {theme.theme_name} created successfully.', 'success')
            return redirect(url_for('reseller_management.themes'))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    # Font family options
    font_families = [
        ('Open Sans, sans-serif', 'Open Sans'),
        ('Roboto, sans-serif', 'Roboto'),
        ('Montserrat, sans-serif', 'Montserrat'),
        ('Lato, sans-serif', 'Lato'),
        ('Nunito, sans-serif', 'Nunito'),
        ('Raleway, sans-serif', 'Raleway'),
        ('Source Sans Pro, sans-serif', 'Source Sans Pro'),
        ('Arial, sans-serif', 'Arial')
    ]
    
    return render_template(
        'admin/resellers/create_theme.html',
        font_families=font_families
    )

@reseller_management_bp.route('/billing')
@login_required
@platform_admin_required
def billing():
    """Manage reseller billing"""
    # Get all active resellers
    resellers = Reseller.query.filter_by(status='active').all()
    
    # Group by billing cycle
    monthly = [r for r in resellers if r.billing_cycle == 'monthly']
    quarterly = [r for r in resellers if r.billing_cycle == 'quarterly']
    annually = [r for r in resellers if r.billing_cycle == 'annually']
    
    # Get upcoming billings
    from datetime import datetime, timedelta
    upcoming_date = datetime.utcnow().date() + timedelta(days=10)
    upcoming = Reseller.query.filter(
        Reseller.next_billing_date <= upcoming_date,
        Reseller.status == 'active'
    ).order_by(Reseller.next_billing_date).all()
    
    return render_template(
        'admin/resellers/billing.html',
        resellers=resellers,
        monthly=monthly,
        quarterly=quarterly,
        annually=annually,
        upcoming=upcoming
    )

@reseller_management_bp.route('/api/themes/refresh', methods=['POST'])
@login_required
@platform_admin_required
def api_refresh_themes():
    """Refresh default themes"""
    # Create default themes
    created_ids = theme_management_service.create_default_themes()
    
    return jsonify({
        'success': True,
        'created': len(created_ids),
        'theme_ids': created_ids
    })
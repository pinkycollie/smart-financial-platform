"""
Reseller portal routes for DEAF FIRST platform.
Enables resellers to manage their white-label branding, licensees, and revenue.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, abort
from flask_login import login_required, current_user
from functools import wraps
from simple_app import db
from models_reseller import Reseller, SubReseller, ResellerAdmin, ResellerRevenue
from models_licensing import Licensee
from services.reseller.management import reseller_management_service
from services.reseller.theme import theme_management_service
from services.reseller.revenue import revenue_management_service

# Create blueprint
reseller_portal_bp = Blueprint('reseller_portal', __name__, url_prefix='/reseller-portal')

# Helper function to check if user is a reseller admin
def reseller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if user is a reseller admin
        admin = ResellerAdmin.query.filter_by(user_id=current_user.id).first()
        if not admin:
            flash('You do not have permission to access the reseller portal.', 'danger')
            return redirect(url_for('main.index'))
        
        # Add reseller admin to flask g object for access in views
        from flask import g
        g.reseller_admin = admin
        g.reseller = Reseller.query.get(admin.reseller_id)
        g.admin_permissions = admin.permissions
        
        return f(*args, **kwargs)
    return decorated_function

# Helper function to check specific permission
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import g
            
            # Check if permission exists
            if not g.admin_permissions.get(permission, False):
                flash(f'You do not have permission to perform this action.', 'danger')
                return redirect(url_for('reseller_portal.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@reseller_portal_bp.route('/')
@reseller_portal_bp.route('/dashboard')
@login_required
@reseller_required
def dashboard():
    """Reseller portal dashboard"""
    from flask import g
    reseller = g.reseller
    
    # Get reseller stats
    stats = reseller_management_service.get_reseller_stats(reseller.id)
    
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
        'reseller/dashboard.html',
        reseller=reseller,
        stats=stats,
        recent_transactions=recent_transactions,
        direct_licensees=direct_licensees,
        sub_resellers=sub_resellers
    )

@reseller_portal_bp.route('/branding')
@login_required
@reseller_required
@permission_required('manage_branding')
def branding():
    """Manage reseller branding"""
    from flask import g
    reseller = g.reseller
    
    # Get branding
    branding = reseller.branding
    
    # Get available themes
    themes = theme_management_service.get_available_themes(reseller.id)
    
    return render_template(
        'reseller/branding.html',
        reseller=reseller,
        branding=branding,
        themes=themes
    )

@reseller_portal_bp.route('/branding/update', methods=['POST'])
@login_required
@reseller_required
@permission_required('manage_branding')
def update_branding():
    """Update reseller branding"""
    from flask import g
    reseller = g.reseller
    
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
    return redirect(url_for('reseller_portal.branding'))

@reseller_portal_bp.route('/theme/apply/<int:theme_id>', methods=['POST'])
@login_required
@reseller_required
@permission_required('manage_branding')
def apply_theme(theme_id):
    """Apply a theme to the reseller branding"""
    from flask import g
    reseller = g.reseller
    
    # Apply theme
    theme_management_service.apply_theme_to_reseller(theme_id, reseller.id)
    
    flash('Theme applied successfully.', 'success')
    return redirect(url_for('reseller_portal.branding'))

@reseller_portal_bp.route('/theme/preview/<int:theme_id>')
@login_required
@reseller_required
def theme_preview(theme_id):
    """Preview a theme"""
    # Get theme preview
    preview = theme_management_service.get_theme_preview(theme_id)
    
    return render_template(
        'reseller/theme_preview.html',
        preview=preview
    )

@reseller_portal_bp.route('/licensees')
@login_required
@reseller_required
@permission_required('view_licensees')
def licensees():
    """Manage licensees"""
    from flask import g
    reseller = g.reseller
    
    # Get licensees
    licensees = reseller_management_service.get_reseller_licensees(
        reseller.id,
        include_sub_resellers=True
    )
    
    # Get sub-resellers for filtering
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=reseller.id).all()
    
    return render_template(
        'reseller/licensees.html',
        reseller=reseller,
        licensees=licensees,
        sub_resellers=sub_resellers
    )

@reseller_portal_bp.route('/licensees/create', methods=['GET', 'POST'])
@login_required
@reseller_required
@permission_required('manage_licensees')
def create_licensee():
    """Create a new licensee"""
    from flask import g
    reseller = g.reseller
    
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        contact_email = request.form.get('contact_email')
        license_tier = request.form.get('license_tier')
        sub_reseller_id = request.form.get('sub_reseller_id')
        
        if not sub_reseller_id or sub_reseller_id == '':
            sub_reseller_id = None
        else:
            sub_reseller_id = int(sub_reseller_id)
        
        # Additional fields
        contact_name = request.form.get('contact_name')
        contact_phone = request.form.get('contact_phone')
        
        try:
            # Create licensee
            licensee = reseller_management_service.create_licensee_for_reseller(
                reseller_id=reseller.id,
                company_name=company_name,
                contact_email=contact_email,
                license_tier=license_tier,
                sub_reseller_id=sub_reseller_id,
                contact_name=contact_name,
                contact_phone=contact_phone
            )
            
            flash(f'Licensee {licensee.company_name} created successfully.', 'success')
            return redirect(url_for('reseller_portal.licensees'))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    # Get license tiers for the form
    from services.licensing.white_label import white_label_service
    license_tiers = white_label_service.get_license_tiers()
    
    # Get sub-resellers for the form
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=reseller.id).all()
    
    return render_template(
        'reseller/create_licensee.html',
        reseller=reseller,
        license_tiers=license_tiers,
        sub_resellers=sub_resellers
    )

@reseller_portal_bp.route('/sub-resellers')
@login_required
@reseller_required
@permission_required('manage_sub_resellers')
def sub_resellers():
    """Manage sub-resellers"""
    from flask import g
    reseller = g.reseller
    
    # Get sub-resellers
    sub_resellers = SubReseller.query.filter_by(parent_reseller_id=reseller.id).all()
    
    return render_template(
        'reseller/sub_resellers.html',
        reseller=reseller,
        sub_resellers=sub_resellers
    )

@reseller_portal_bp.route('/sub-resellers/create', methods=['GET', 'POST'])
@login_required
@reseller_required
@permission_required('manage_sub_resellers')
def create_sub_reseller():
    """Create a new sub-reseller"""
    from flask import g
    reseller = g.reseller
    
    # Check if reseller can create sub-resellers
    if not reseller.can_create_sub_resellers:
        flash('Your reseller tier does not allow creating sub-resellers.', 'danger')
        return redirect(url_for('reseller_portal.sub_resellers'))
    
    # Check if reseller has reached sub-reseller limit
    if not reseller.can_add_sub_reseller():
        flash('You have reached the maximum number of sub-resellers allowed.', 'danger')
        return redirect(url_for('reseller_portal.sub_resellers'))
    
    if request.method == 'POST':
        # Get form data
        company_name = request.form.get('company_name')
        contact_email = request.form.get('contact_email')
        contact_name = request.form.get('contact_name')
        contact_phone = request.form.get('contact_phone')
        max_licensees = int(request.form.get('max_licensees', 10))
        commission_rate = float(request.form.get('commission_rate', 10.0))
        
        try:
            # Create sub-reseller
            sub_reseller = reseller_management_service.create_sub_reseller(
                parent_reseller_id=reseller.id,
                company_name=company_name,
                contact_email=contact_email,
                contact_name=contact_name,
                contact_phone=contact_phone,
                max_licensees=max_licensees,
                commission_rate=commission_rate
            )
            
            flash(f'Sub-reseller {sub_reseller.company_name} created successfully.', 'success')
            return redirect(url_for('reseller_portal.sub_resellers'))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template(
        'reseller/create_sub_reseller.html',
        reseller=reseller
    )

@reseller_portal_bp.route('/revenue')
@login_required
@reseller_required
@permission_required('view_revenue')
def revenue():
    """View revenue and commissions"""
    from flask import g
    reseller = g.reseller
    
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
        'reseller/revenue.html',
        reseller=reseller,
        revenue_data=revenue_data,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

@reseller_portal_bp.route('/revenue/export', methods=['POST'])
@login_required
@reseller_required
@permission_required('view_revenue')
def export_revenue():
    """Export revenue report"""
    from flask import g, send_file
    reseller = g.reseller
    
    # Get form data
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    report_format = request.form.get('format', 'csv')
    
    try:
        # Parse dates
        from datetime import datetime
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate report
        report_path = revenue_management_service.generate_reseller_revenue_report(
            reseller_id=reseller.id,
            start_date=start_date,
            end_date=end_date,
            format=report_format
        )
        
        # Send file
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f"revenue_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{report_format}"
        )
        
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return redirect(url_for('reseller_portal.revenue'))

@reseller_portal_bp.route('/admins')
@login_required
@reseller_required
@permission_required('manage_admins')
def admins():
    """Manage reseller admins"""
    from flask import g
    reseller = g.reseller
    
    # Get admins
    admins = ResellerAdmin.query.filter_by(reseller_id=reseller.id).all()
    
    return render_template(
        'reseller/admins.html',
        reseller=reseller,
        admins=admins
    )

@reseller_portal_bp.route('/admins/create', methods=['GET', 'POST'])
@login_required
@reseller_required
@permission_required('manage_admins')
def create_admin():
    """Create a new reseller admin"""
    from flask import g
    reseller = g.reseller
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        is_primary = request.form.get('is_primary') == 'on'
        
        try:
            # Create admin
            admin = reseller_management_service.create_reseller_admin(
                reseller_id=reseller.id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_primary=is_primary
            )
            
            flash(f'Admin {admin.user.email} created successfully.', 'success')
            return redirect(url_for('reseller_portal.admins'))
            
        except ValueError as e:
            flash(str(e), 'danger')
    
    # Available roles
    roles = [
        ('admin', 'Administrator'),
        ('sales', 'Sales Manager'),
        ('support', 'Support Agent'),
        ('billing', 'Billing Manager')
    ]
    
    return render_template(
        'reseller/create_admin.html',
        reseller=reseller,
        roles=roles
    )

# API endpoints for AJAX requests
@reseller_portal_bp.route('/api/licensees/sub-reseller/<int:sub_reseller_id>')
@login_required
@reseller_required
def api_sub_reseller_licensees(sub_reseller_id):
    """Get licensees for a sub-reseller"""
    from flask import g
    reseller = g.reseller
    
    # Verify sub-reseller belongs to this reseller
    sub_reseller = SubReseller.query.get(sub_reseller_id)
    if not sub_reseller or sub_reseller.parent_reseller_id != reseller.id:
        return jsonify({'error': 'Invalid sub-reseller ID'}), 400
    
    # Get licensees
    licensees = reseller_management_service.get_sub_reseller_licensees(sub_reseller_id)
    
    # Format response
    licensee_data = []
    for licensee in licensees:
        licensee_data.append({
            'id': licensee.id,
            'company_name': licensee.company_name,
            'license_tier': licensee.license_tier,
            'contact_email': licensee.contact_email,
            'status': licensee.status,
            'current_clients': licensee.current_clients,
            'created_at': licensee.created_at.strftime('%Y-%m-%d')
        })
    
    return jsonify(licensee_data)

@reseller_portal_bp.route('/api/revenue/sub-reseller/<int:sub_reseller_id>')
@login_required
@reseller_required
@permission_required('view_revenue')
def api_sub_reseller_revenue(sub_reseller_id):
    """Get revenue data for a sub-reseller"""
    from flask import g
    reseller = g.reseller
    
    # Verify sub-reseller belongs to this reseller
    sub_reseller = SubReseller.query.get(sub_reseller_id)
    if not sub_reseller or sub_reseller.parent_reseller_id != reseller.id:
        return jsonify({'error': 'Invalid sub-reseller ID'}), 400
    
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
    revenue_data = revenue_management_service.get_sub_reseller_revenue(
        sub_reseller_id=sub_reseller_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(revenue_data)
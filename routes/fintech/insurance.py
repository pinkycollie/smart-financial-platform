from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime, date

from models import db, InsuranceProduct, InsurancePolicy, User
from services.insurance.boost_client import BoostAPIClient
from services.deaf_first.mux_client import MuxClient

# Create Blueprint
insurance_bp = Blueprint('insurance', __name__, url_prefix='/insurance')

# Initialize clients
boost_client = BoostAPIClient()
mux_client = MuxClient()

@insurance_bp.route('/')
@login_required
def insurance_dashboard():
    """Main insurance dashboard page"""
    products = InsuranceProduct.query.filter_by(active=True).all()
    policies = InsurancePolicy.query.filter_by(user_id=current_user.id).all()
    
    # Get ASL videos for insurance concepts
    asl_videos = mux_client.get_asl_videos_for_context('insurance_concepts')
    
    return render_template(
        'fintech/insurance/dashboard.html',
        products=products,
        policies=policies,
        asl_videos=asl_videos
    )

@insurance_bp.route('/products')
@login_required
def product_list():
    """List available insurance products"""
    products = InsuranceProduct.query.filter_by(active=True).all()
    
    # Get ASL videos explaining each product type
    product_videos = {}
    for product in products:
        if product.asl_video_id:
            video_details = mux_client.get_asl_video(product.asl_video_id)
            if video_details:
                product_videos[product.id] = video_details
    
    return render_template(
        'fintech/insurance/products.html',
        products=products,
        product_videos=product_videos
    )

@insurance_bp.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    """Show details for a specific insurance product"""
    product = InsuranceProduct.query.get_or_404(product_id)
    
    # Get ASL video for this product
    product_video = None
    if product.asl_video_id:
        product_video = mux_client.get_asl_video(product.asl_video_id)
    
    return render_template(
        'fintech/insurance/product_detail.html',
        product=product,
        product_video=product_video
    )

@insurance_bp.route('/quote/<int:product_id>', methods=['GET', 'POST'])
@login_required
def get_quote(product_id):
    """Get an insurance quote for a product"""
    product = InsuranceProduct.query.get_or_404(product_id)
    
    if request.method == 'POST':
        # Get coverage parameters from form
        coverage_params = {
            'coverage_amount': float(request.form.get('coverage_amount', 0)),
            'coverage_term': int(request.form.get('coverage_term', 12)),  # in months
            'deductible': float(request.form.get('deductible', 0))
        }
        
        try:
            # Get quote from Boost API
            quote_response = boost_client.get_insurance_quote(
                user_id=current_user.id,
                product_code=product.product_code,
                coverage_params=coverage_params
            )
            
            # Store quote in session for purchase flow
            session['pending_quote'] = {
                'quote_id': quote_response.get('quote_id'),
                'product_id': product_id,
                'premium': quote_response.get('premium'),
                'coverage_amount': coverage_params['coverage_amount'],
                'coverage_term': coverage_params['coverage_term'],
                'expires_at': quote_response.get('expires_at')
            }
            
            return redirect(url_for('insurance.review_quote'))
            
        except Exception as e:
            flash(f"Error getting quote: {str(e)}", "error")
            return redirect(url_for('insurance.product_detail', product_id=product_id))
    
    # GET request - show quote form
    return render_template(
        'fintech/insurance/get_quote.html',
        product=product
    )

@insurance_bp.route('/quote/review', methods=['GET', 'POST'])
@login_required
def review_quote():
    """Review and purchase an insurance quote"""
    # Get quote from session
    quote = session.get('pending_quote')
    if not quote:
        flash("No quote found. Please start a new quote.", "error")
        return redirect(url_for('insurance.product_list'))
    
    product = InsuranceProduct.query.get_or_404(quote['product_id'])
    
    if request.method == 'POST':
        # User confirmed purchase
        policyholder_data = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
            'address': {
                'street': request.form.get('street'),
                'city': request.form.get('city'),
                'state': request.form.get('state'),
                'zip': request.form.get('zip')
            }
        }
        
        try:
            # Purchase policy through Boost API
            policy_response = boost_client.purchase_policy(
                user_id=current_user.id,
                quote_id=quote['quote_id'],
                policyholder_data=policyholder_data
            )
            
            # Create policy record in database
            policy = InsurancePolicy(
                user_id=current_user.id,
                product_id=product.id,
                policy_number=policy_response.get('policy_number'),
                external_id=policy_response.get('policy_id'),
                status='active',
                coverage_amount=quote['coverage_amount'],
                premium_amount=quote['premium'],
                start_date=datetime.strptime(policy_response.get('start_date'), '%Y-%m-%d').date(),
                end_date=datetime.strptime(policy_response.get('end_date'), '%Y-%m-%d').date(),
                policy_data=policy_response
            )
            
            db.session.add(policy)
            db.session.commit()
            
            # Clear quote from session
            session.pop('pending_quote', None)
            
            flash("Policy successfully purchased!", "success")
            return redirect(url_for('insurance.policy_detail', policy_id=policy.id))
            
        except Exception as e:
            flash(f"Error purchasing policy: {str(e)}", "error")
    
    # GET request - show quote review page
    return render_template(
        'fintech/insurance/review_quote.html',
        quote=quote,
        product=product
    )

@insurance_bp.route('/policies')
@login_required
def policy_list():
    """List user's insurance policies"""
    policies = InsurancePolicy.query.filter_by(user_id=current_user.id).all()
    
    return render_template(
        'fintech/insurance/policies.html',
        policies=policies
    )

@insurance_bp.route('/policies/<int:policy_id>')
@login_required
def policy_detail(policy_id):
    """Show details for a specific policy"""
    policy = InsurancePolicy.query.get_or_404(policy_id)
    
    # Ensure user can only view their own policies
    if policy.user_id != current_user.id:
        flash("You don't have permission to view this policy", "error")
        return redirect(url_for('insurance.policy_list'))
    
    # Get latest policy details from Boost API
    try:
        policy_details = boost_client.get_policy_details(
            user_id=current_user.id,
            policy_id=policy.external_id
        )
    except Exception:
        # Use stored policy data if API call fails
        policy_details = policy.policy_data
    
    return render_template(
        'fintech/insurance/policy_detail.html',
        policy=policy,
        policy_details=policy_details
    )

@insurance_bp.route('/claims/new/<int:policy_id>', methods=['GET', 'POST'])
@login_required
def file_claim(policy_id):
    """File a new insurance claim"""
    policy = InsurancePolicy.query.get_or_404(policy_id)
    
    # Ensure user can only file claims for their own policies
    if policy.user_id != current_user.id:
        flash("You don't have permission to file a claim for this policy", "error")
        return redirect(url_for('insurance.policy_list'))
    
    if request.method == 'POST':
        claim_data = {
            'incident_date': request.form.get('incident_date'),
            'incident_description': request.form.get('incident_description'),
            'claim_amount': float(request.form.get('claim_amount', 0)),
            'supporting_details': request.form.get('supporting_details')
        }
        
        try:
            # File claim through Boost API
            claim_response = boost_client.file_insurance_claim(
                user_id=current_user.id,
                policy_id=policy.external_id,
                claim_data=claim_data
            )
            
            flash("Claim successfully filed!", "success")
            return redirect(url_for('insurance.policy_detail', policy_id=policy.id))
            
        except Exception as e:
            flash(f"Error filing claim: {str(e)}", "error")
    
    # GET request - show claim form
    return render_template(
        'fintech/insurance/file_claim.html',
        policy=policy
    )

@insurance_bp.route('/asl-video/<video_key>')
@login_required
def get_asl_video(video_key):
    """Get ASL video for insurance concept"""
    video = mux_client.get_asl_video(video_key)
    
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    return jsonify(video)
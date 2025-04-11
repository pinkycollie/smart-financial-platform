from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from models import InsuranceProduct, InsurancePolicy, db
import logging

# Create a Blueprint for insurance routes
insurance_bp = Blueprint('insurance', __name__, url_prefix='/insurance')

# Logger
logger = logging.getLogger(__name__)

# Initialize Mux client for ASL videos
try:
    from services.deaf_first.mux_client import MuxClient
    mux_client = MuxClient()
except ImportError as e:
    logger.error(f"Failed to import MuxClient: {e}")
    mux_client = None
except Exception as e:
    logger.error(f"Failed to initialize Mux client: {e}")
    mux_client = None

@insurance_bp.route('/')
def insurance_dashboard():
    """Main insurance dashboard page"""
    # Placeholder for fetching real data
    # In a real implementation, these would be fetched from the database
    products = []
    policies = []
    asl_videos = []
    
    # For demo purposes, add placeholder insurance products if none exist
    if not products:
        try:
            # Demo products can be populated here
            pass
        except Exception as e:
            logger.error(f"Error loading demo insurance products: {e}")
    
    # If Mux client is available, get ASL videos for insurance
    if mux_client:
        try:
            asl_videos = mux_client.get_asl_videos_for_context('insurance')
        except Exception as e:
            logger.error(f"Error fetching ASL videos: {e}")
            asl_videos = []
    
    return render_template(
        'fintech/insurance/dashboard.html',
        products=products,
        policies=policies,
        asl_videos=asl_videos
    )

@insurance_bp.route('/products')
def product_list():
    """List available insurance products"""
    try:
        products = InsuranceProduct.query.filter_by(active=True).all()
    except Exception as e:
        logger.error(f"Error fetching insurance products: {e}")
        products = []
        flash("Unable to load insurance products. Please try again later.", "error")
    
    return render_template(
        'fintech/insurance/product_list.html',
        products=products
    )

@insurance_bp.route('/products/<int:product_id>')
def product_detail(product_id):
    """Show details for a specific insurance product"""
    try:
        product = InsuranceProduct.query.get_or_404(product_id)
        product_video = None
        
        # Get ASL video for product if available
        if mux_client and product.asl_video_id:
            try:
                product_video = mux_client.get_asl_video(product.asl_video_id)
            except Exception as e:
                logger.error(f"Error fetching ASL video for product: {e}")
    except Exception as e:
        logger.error(f"Error fetching product details: {e}")
        flash("Unable to load product details. Please try again later.", "error")
        return redirect(url_for('insurance.product_list'))
    
    return render_template(
        'fintech/insurance/product_detail.html',
        product=product,
        product_video=product_video
    )

@insurance_bp.route('/products/<int:product_id>/quote', methods=['GET', 'POST'])
@login_required
def get_quote(product_id):
    """Get an insurance quote for a product"""
    try:
        product = InsuranceProduct.query.get_or_404(product_id)
        
        if request.method == 'POST':
            # Process quote request
            # In a real implementation, this would call the Boost API
            
            # Store quote details in session for review page
            session = {}
            session['quote'] = {
                'product_id': product.id,
                'coverage_amount': float(request.form.get('coverage_amount', 0)),
                'coverage_term': int(request.form.get('coverage_term', 12)),
                'deductible': float(request.form.get('deductible', 500)),
                'deaf_coverages': request.form.getlist('deaf_coverages[]')
            }
            
            # Calculate premium (placeholder)
            premium = calculate_premium(product, session['quote'])
            session['quote']['premium'] = premium
            
            # Redirect to quote review page
            return redirect(url_for('insurance.review_quote'))
    except Exception as e:
        logger.error(f"Error processing quote request: {e}")
        flash("An error occurred while processing your quote. Please try again.", "error")
        return redirect(url_for('insurance.product_list'))
    
    return render_template(
        'fintech/insurance/get_quote.html',
        product=product
    )

@insurance_bp.route('/quote/review', methods=['GET', 'POST'])
@login_required
def review_quote():
    """Review and purchase an insurance quote"""
    # Placeholder implementation
    return jsonify({
        'message': 'Quote review feature coming soon',
        'status': 'under development'
    })

@insurance_bp.route('/policies')
@login_required
def policy_list():
    """List user's insurance policies"""
    try:
        policies = InsurancePolicy.query.filter_by(user_id=current_user.id).all()
    except Exception as e:
        logger.error(f"Error fetching user policies: {e}")
        policies = []
        flash("Unable to load your policies. Please try again later.", "error")
    
    return render_template(
        'fintech/insurance/policy_list.html',
        policies=policies
    )

@insurance_bp.route('/policies/<int:policy_id>')
@login_required
def policy_detail(policy_id):
    """Show details for a specific policy"""
    try:
        policy = InsurancePolicy.query.filter_by(id=policy_id, user_id=current_user.id).first_or_404()
    except Exception as e:
        logger.error(f"Error fetching policy details: {e}")
        flash("Unable to load policy details. Please try again later.", "error")
        return redirect(url_for('insurance.policy_list'))
    
    return render_template(
        'fintech/insurance/policy_detail.html',
        policy=policy
    )

@insurance_bp.route('/policies/<int:policy_id>/claim', methods=['GET', 'POST'])
@login_required
def file_claim(policy_id):
    """File a new insurance claim"""
    # Placeholder implementation
    return jsonify({
        'message': 'Claim filing feature coming soon',
        'status': 'under development'
    })

@insurance_bp.route('/asl-videos/<string:video_key>')
def get_asl_video(video_key):
    """Get ASL video for insurance concept"""
    if not mux_client:
        return jsonify({
            'error': 'ASL video service unavailable',
            'status': 'error'
        }), 503
    
    try:
        video = mux_client.get_asl_video(video_key)
        if not video:
            video = mux_client.get_fallback_video()
            
        return jsonify(video)
    except Exception as e:
        logger.error(f"Error fetching ASL video: {e}")
        return jsonify({
            'error': 'Failed to retrieve ASL video',
            'status': 'error'
        }), 500

def calculate_premium(product, quote_data):
    """Calculate premium based on product and quote data"""
    # Simplified premium calculation
    base_premium = product.minimum_premium
    coverage_multiplier = quote_data['coverage_amount'] / (product.minimum_premium * 100)
    deductible_factor = 1.0
    
    if quote_data['deductible'] == 250:
        deductible_factor = 1.2
    elif quote_data['deductible'] == 500:
        deductible_factor = 1.0
    elif quote_data['deductible'] == 1000:
        deductible_factor = 0.9
    elif quote_data['deductible'] == 2500:
        deductible_factor = 0.8
    
    # Adjust for deaf-specific coverages
    deaf_coverage_factor = 1.0
    if 'deaf_coverages' in quote_data and quote_data['deaf_coverages']:
        deaf_coverage_factor = 1.0 + (len(quote_data['deaf_coverages']) * 0.05)
    
    # Calculate total premium
    monthly_premium = base_premium * coverage_multiplier * deductible_factor * deaf_coverage_factor
    
    return round(monthly_premium, 2)
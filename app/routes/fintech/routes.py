import logging
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.routes.fintech import fintech_bp
from app.routes.fintech.forms import FinancialProfileForm, TaxDocumentForm
from app.services.april.services.tax_service import TaxService
from app.services.april.services.estimator_service import EstimatorService
from app.services.april.services.optimizer_service import OptimizerService
from app.services.accessibility.deaf_support_bot import DeafSupportBot

logger = logging.getLogger(__name__)

# Initialize services
tax_service = TaxService()
estimator_service = EstimatorService()
optimizer_service = OptimizerService()
deaf_support_bot = DeafSupportBot()

@fintech_bp.route('/dashboard')
@login_required
def dashboard():
    """Financial dashboard showing user's profiles, tax documents, and recommendations"""
    try:
        # Track page view in optimizer
        optimizer_service.track_product_engagement(
            current_user.id,
            'dashboard',
            {'action': 'page_view', 'page': 'dashboard'}
        )
        
        # Get ASL video for the dashboard
        asl_video = {'video_id': 'dashboard_overview'}
        
        return render_template(
            'fintech/dashboard.html',
            user=current_user,
            asl_video=asl_video
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        flash("An error occurred while loading your dashboard. Please try again later.", "error")
        return redirect(url_for('index'))

@fintech_bp.route('/tax-filing', methods=['GET', 'POST'])
@login_required
def tax_filing():
    """Tax filing page with ASL accessibility"""
    form = TaxDocumentForm()
    
    if form.validate_on_submit():
        try:
            # Save tax document
            document_data = {
                'income': form.income.data,
                'withholding': form.withholding.data,
                'employer': form.employer.data
            }
            
            document = tax_service.save_tax_document(
                current_user.id,
                form.document_type.data,
                document_data,
                form.tax_year.data
            )
            
            if document:
                flash("Tax document saved successfully.", "success")
                
                # Track successful document upload in optimizer
                optimizer_service.track_product_engagement(
                    current_user.id,
                    'tax_filer',
                    {'action': 'document_upload', 'document_type': form.document_type.data}
                )
                
                return redirect(url_for('fintech.tax_filing'))
            else:
                flash("Failed to save tax document. Please try again.", "error")
        except Exception as e:
            logger.error(f"Error saving tax document: {str(e)}")
            flash(f"An error occurred: {str(e)}", "error")
    
    # Get user's tax documents
    documents = []  # This would normally query the database
    
    # Get ASL video for tax filing page
    asl_video = {'video_id': 'tax_filing_overview'}
    
    return render_template(
        'fintech/tax_filing.html',
        form=form,
        documents=documents,
        asl_video=asl_video
    )

@fintech_bp.route('/financial-profile', methods=['GET', 'POST'])
@login_required
def financial_profile():
    """Financial profile creation and management with ASL accessibility"""
    form = FinancialProfileForm()
    
    if form.validate_on_submit():
        try:
            # Create profile data
            profile_data = {
                'annual_income': form.annual_income.data,
                'filing_status': form.filing_status.data,
                'dependents': form.dependents.data,
                'investments': {
                    'stocks': form.stocks.data,
                    'bonds': form.bonds.data,
                    'real_estate': form.real_estate.data
                },
                'retirement_accounts': {
                    '401k': form.retirement_401k.data,
                    'ira': form.retirement_ira.data
                }
            }
            
            # Create financial profile
            result = estimator_service.create_financial_profile(
                current_user.id,
                profile_data
            )
            
            if result['success']:
                flash("Financial profile created successfully.", "success")
                
                # Track successful profile creation in optimizer
                optimizer_service.track_product_engagement(
                    current_user.id,
                    'estimator',
                    {'action': 'profile_create'}
                )
                
                return redirect(url_for('fintech.financial_profile'))
            else:
                flash(f"Failed to create financial profile: {result.get('error', 'Unknown error')}", "error")
        except Exception as e:
            logger.error(f"Error creating financial profile: {str(e)}")
            flash(f"An error occurred: {str(e)}", "error")
    
    # Get user's financial profiles
    profiles = []  # This would normally query the database
    
    # Get ASL video for financial profile page
    asl_video = {'video_id': 'financial_profile_overview'}
    
    return render_template(
        'fintech/financial_profile.html',
        form=form,
        profiles=profiles,
        asl_video=asl_video
    )

@fintech_bp.route('/api/get-recommendations/<int:profile_id>')
@login_required
def get_recommendations(profile_id):
    """API endpoint to get financial recommendations for a profile"""
    try:
        # Get recommendations
        result = estimator_service.get_financial_recommendations(
            current_user.id,
            profile_id
        )
        
        # Track recommendation view in optimizer
        optimizer_service.track_product_engagement(
            current_user.id,
            'estimator',
            {'action': 'view_recommendations', 'profile_id': profile_id}
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@fintech_bp.route('/api/deaf-support', methods=['POST'])
@login_required
def deaf_support():
    """API endpoint for the deaf support bot"""
    try:
        data = request.json
        message = data.get('message', '')
        context = data.get('context', None)
        
        # Get response from deaf support bot
        response = deaf_support_bot.get_support_response(
            current_user.id,
            message,
            context
        )
        
        # Track bot interaction in optimizer
        optimizer_service.track_product_engagement(
            current_user.id,
            'deaf_support_bot',
            {'action': 'message', 'context': context}
        )
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in deaf support bot: {str(e)}")
        return jsonify({
            'text': "I'm sorry, I encountered an error. Please try again later.",
            'asl_video_id': 'error',
            'suggestions': ['Start over', 'Contact support']
        }), 500

@fintech_bp.route('/api/request-asl-session', methods=['POST'])
@login_required
def request_asl_session():
    """API endpoint to request a live ASL support session"""
    try:
        data = request.json
        context = data.get('context', None)
        
        # Create ASL support session
        session_result = deaf_support_bot.create_asl_support_session(
            current_user.id,
            context
        )
        
        # Track session request in optimizer
        optimizer_service.track_product_engagement(
            current_user.id,
            'asl_live_support',
            {'action': 'request_session', 'context': context}
        )
        
        return jsonify(session_result)
    except Exception as e:
        logger.error(f"Error requesting ASL session: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

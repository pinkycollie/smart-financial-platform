"""
DHH Tax and Insurance API Endpoints

This module implements the OpenAPI specification endpoints for
the MBTQ Smart Tax & Insurance Platform for DHH community.
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

# Import services
from services.client.intake_service import DHHClientIntakeService, NeedsAssessmentService
from services.tax.dhh_deductions import TaxRefundEstimator
from services.insurance.dhh_riders import InsuranceQuoteGenerator

# Create Blueprint for DHH-specific endpoints
dhh_api_bp = Blueprint('dhh_api', __name__, url_prefix='/api')

# Initialize services
client_intake_service = DHHClientIntakeService()
needs_assessment_service = NeedsAssessmentService()
tax_estimator = TaxRefundEstimator()
insurance_quote_generator = InsuranceQuoteGenerator()

logger = logging.getLogger(__name__)


@dhh_api_bp.route('/intake/tax-client', methods=['POST'])
def register_tax_client():
    """
    Register a new DHH client for tax services.
    
    OpenAPI Endpoint: POST /api/intake/tax-client
    Schema: DHHClientIntake
    Response: ClientConfirmation
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'communication_preference']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Register client
        confirmation = client_intake_service.register_client(
            full_name=data['full_name'],
            email=data['email'],
            communication_preference=data['communication_preference'],
            interpreter_needed=data.get('interpreter_needed', False),
            interpreter_contracting_status=data.get('interpreter_contracting_status', 'Not_Required')
        )
        
        logger.info(f"New DHH client registered: {confirmation['client_id']}")
        
        return jsonify(confirmation), 201
        
    except ValueError as e:
        logger.error(f"Validation error in client registration: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error registering tax client: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during registration'
        }), 500


@dhh_api_bp.route('/intake/needs-assessment', methods=['POST'])
def submit_needs_assessment():
    """
    Submit a detailed needs assessment for DHH-specific opportunities.
    
    OpenAPI Endpoint: POST /api/intake/needs-assessment
    Schema: NeedsAssessmentRequest
    Response: StandardSuccessResponse
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'hearing_aid_claims_history' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: hearing_aid_claims_history'
            }), 400
        
        # TODO: SECURITY - Extract client_id from authentication context
        # IMPORTANT: This is a security vulnerability placeholder.
        # In production, client_id MUST be extracted from the validated OAuth token
        # or authenticated session to prevent unauthorized access to other clients' data.
        # Example production code:
        #   from flask_login import current_user
        #   client_id = current_user.client_id
        # Or from OAuth token:
        #   token_data = validate_token(request.headers.get('Authorization'))
        #   client_id = token_data['client_id']
        
        client_id = data.get('client_id')
        if not client_id:
            return jsonify({
                'status': 'error',
                'message': 'Client ID required. Please authenticate.'
            }), 401
        
        # Submit assessment
        result = needs_assessment_service.submit_assessment(
            client_id=client_id,
            hearing_aid_claims_history=data['hearing_aid_claims_history'],
            benefit_program_eligibility=data.get('benefit_program_eligibility', []),
            tax_deductions_focus=data.get('tax_deductions_focus', [])
        )
        
        logger.info(f"Needs assessment submitted: {result.get('assessment_id')}")
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f"Validation error in needs assessment: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error submitting needs assessment: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during assessment submission'
        }), 500


@dhh_api_bp.route('/tax/refund-estimate', methods=['POST'])
def calculate_refund_estimate():
    """
    Calculate estimated tax refund with DHH-specific deductions.
    
    OpenAPI Endpoint: POST /api/tax/refund-estimate
    Schema: TaxDataInput
    Response: RefundEstimateResponse
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'income_w2' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: income_w2'
            }), 400
        
        # Calculate refund estimate
        estimate = tax_estimator.estimate_refund(
            income_w2=float(data['income_w2']),
            deductions_standard=float(data.get('deductions_standard', 12950.00)),
            special_deduction_amount=float(data.get('special_deduction_amount', 0.00)),
            withholding=float(data.get('withholding', 0.00))
        )
        
        logger.info(f"Tax refund estimate calculated: ${estimate['estimated_refund']:.2f}")
        
        return jsonify(estimate), 200
        
    except ValueError as e:
        logger.error(f"Validation error in refund estimate: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid numeric value provided'
        }), 400
    except Exception as e:
        logger.error(f"Error calculating refund estimate: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during calculation'
        }), 500


@dhh_api_bp.route('/insurance/quote/request', methods=['POST'])
def request_insurance_quote():
    """
    Request an insurance quote with DHH-specific riders.
    
    OpenAPI Endpoint: POST /api/insurance/quote/request
    Schema: InsuranceQuoteRequestDHH
    Response: QuoteConfirmation
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['insurance_type', 'hearing_aid_coverage_required']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Generate quote
        quote = insurance_quote_generator.generate_quote(
            insurance_type=data['insurance_type'],
            hearing_aid_coverage_required=data['hearing_aid_coverage_required'],
            interpreter_service_rider=data.get('interpreter_service_rider', False),
            assistive_equipment_rider=data.get('assistive_equipment_rider', False),
            current_policy_exception_summary=data.get('current_policy_exception_summary', '')
        )
        
        logger.info(f"Insurance quote generated: {quote['quote_id']}")
        
        # Return simplified response matching OpenAPI spec
        return jsonify({
            'quote_id': quote['quote_id'],
            'estimated_premium_range': quote['estimated_premium_range']
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating insurance quote: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during quote generation'
        }), 500


@dhh_api_bp.route('/internal/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    OpenAPI Endpoint: GET /api/internal/health
    Response: Health status
    """
    return jsonify({
        'status': 'UP',
        'timestamp': datetime.now().isoformat()
    }), 200


# Error handlers
@dhh_api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@dhh_api_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed'
    }), 405


@dhh_api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

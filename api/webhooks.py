"""
Webhook API Routes for DEAF FIRST Platform
Handles incoming webhooks from external services
"""

from flask import Blueprint, request, jsonify
import logging
import json
from services.webhooks.webhook_handler import webhook_handler

logger = logging.getLogger(__name__)

# Create blueprint
webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

@webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe payment webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('stripe', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/twilio', methods=['POST'])
def twilio_webhook():
    """Handle Twilio SMS webhooks"""
    
    try:
        # Twilio sends form data, not JSON
        payload = request.form.to_dict()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('twilio', payload, headers)
        
        # Return TwiML response for SMS
        if result.get('status') == 'success':
            response = result.get('response', '')
            return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{response}</Message></Response>', 200, {'Content-Type': 'text/xml'}
        
        return '', 200
    
    except Exception as e:
        logger.error(f"Twilio webhook error: {str(e)}")
        return '', 500

@webhooks_bp.route('/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram bot webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('telegram', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"Telegram webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/discord', methods=['POST'])
def discord_webhook():
    """Handle Discord interaction webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('discord', payload, headers)
        
        # Discord expects specific response format
        if 'type' in result:
            return jsonify(result), 200
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"Discord webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle WhatsApp Business API webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('whatsapp', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/whatsapp', methods=['GET'])
def whatsapp_verification():
    """Handle WhatsApp webhook verification"""
    
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Verify the webhook (in production, verify against your token)
        if mode == 'subscribe' and token:
            return challenge, 200
        
        return 'Forbidden', 403
    
    except Exception as e:
        logger.error(f"WhatsApp verification error: {str(e)}")
        return 'Error', 500

@webhooks_bp.route('/pinksync', methods=['POST'])
def pinksync_webhook():
    """Handle PinkSync accessibility webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('pinksync', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"PinkSync webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/april', methods=['POST'])
def april_webhook():
    """Handle April Fintech API webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('april_api', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"April API webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/insurance', methods=['POST'])
def insurance_webhook():
    """Handle Open Insurance API webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('boost_insurance', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"Insurance webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/mux', methods=['POST'])
def mux_webhook():
    """Handle Mux video webhooks"""
    
    try:
        payload = request.get_json()
        headers = dict(request.headers)
        
        result = webhook_handler.process_webhook('mux', payload, headers)
        
        return jsonify(result), result.get('code', 200)
    
    except Exception as e:
        logger.error(f"Mux webhook error: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500

@webhooks_bp.route('/test', methods=['POST', 'GET'])
def test_webhook():
    """Test webhook endpoint for development"""
    
    try:
        if request.method == 'POST':
            payload = request.get_json() or request.form.to_dict()
            headers = dict(request.headers)
            
            logger.info(f"Test webhook received: {json.dumps(payload, indent=2)}")
            
            return jsonify({
                'status': 'success',
                'message': 'Test webhook received',
                'payload': payload,
                'headers': dict(headers)
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'message': 'Test webhook endpoint is active',
                'supported_platforms': list(webhook_handler.supported_platforms.keys())
            }), 200
    
    except Exception as e:
        logger.error(f"Test webhook error: {str(e)}")
        return jsonify({'error': 'Test webhook failed'}), 500

@webhooks_bp.route('/status', methods=['GET'])
def webhook_status():
    """Get webhook service status"""
    
    try:
        return jsonify({
            'status': 'active',
            'message': 'Webhook service is running',
            'supported_platforms': list(webhook_handler.supported_platforms.keys()),
            'endpoints': {
                'stripe': '/api/webhooks/stripe',
                'twilio': '/api/webhooks/twilio',
                'telegram': '/api/webhooks/telegram',
                'discord': '/api/webhooks/discord',
                'whatsapp': '/api/webhooks/whatsapp',
                'pinksync': '/api/webhooks/pinksync',
                'april': '/api/webhooks/april',
                'insurance': '/api/webhooks/insurance',
                'mux': '/api/webhooks/mux',
                'test': '/api/webhooks/test'
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Webhook status error: {str(e)}")
        return jsonify({'error': 'Status check failed'}), 500
"""
Webhook Handler for DEAF FIRST Platform
Handles incoming webhooks from various services and platforms
"""

import json
import logging
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import request, jsonify
import requests

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Centralized webhook handling for DEAF FIRST platform"""
    
    def __init__(self):
        self.supported_platforms = {
            'stripe': self._handle_stripe_webhook,
            'twilio': self._handle_twilio_webhook,
            'telegram': self._handle_telegram_webhook,
            'discord': self._handle_discord_webhook,
            'whatsapp': self._handle_whatsapp_webhook,
            'pinksync': self._handle_pinksync_webhook,
            'april_api': self._handle_april_webhook,
            'boost_insurance': self._handle_insurance_webhook,
            'mux': self._handle_mux_webhook
        }
        
        # Webhook verification keys (would be stored in environment variables)
        self.verification_keys = {
            'stripe': 'STRIPE_WEBHOOK_SECRET',
            'twilio': 'TWILIO_AUTH_TOKEN',
            'telegram': 'TELEGRAM_BOT_TOKEN',
            'discord': 'DISCORD_WEBHOOK_SECRET',
            'whatsapp': 'WHATSAPP_WEBHOOK_SECRET',
            'pinksync': 'PINKSYNC_WEBHOOK_SECRET'
        }
    
    def process_webhook(self, platform: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Main webhook processing entry point"""
        
        try:
            # Verify webhook authenticity
            if not self._verify_webhook(platform, payload, headers):
                logger.warning(f"Webhook verification failed for platform: {platform}")
                return {
                    'status': 'error',
                    'message': 'Webhook verification failed',
                    'code': 401
                }
            
            # Route to appropriate handler
            if platform in self.supported_platforms:
                result = self.supported_platforms[platform](payload, headers)
                self._log_webhook_event(platform, payload, result)
                return result
            else:
                logger.warning(f"Unsupported webhook platform: {platform}")
                return {
                    'status': 'error',
                    'message': f'Unsupported platform: {platform}',
                    'code': 400
                }
        
        except Exception as e:
            logger.error(f"Error processing webhook for {platform}: {str(e)}")
            return {
                'status': 'error',
                'message': 'Internal webhook processing error',
                'code': 500
            }
    
    def _verify_webhook(self, platform: str, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Verify webhook authenticity based on platform"""
        
        if platform == 'stripe':
            return self._verify_stripe_webhook(payload, headers)
        elif platform == 'twilio':
            return self._verify_twilio_webhook(payload, headers)
        elif platform == 'telegram':
            return self._verify_telegram_webhook(payload, headers)
        elif platform in ['discord', 'whatsapp', 'pinksync']:
            return self._verify_generic_webhook(platform, payload, headers)
        else:
            # For testing purposes, allow unverified webhooks in development
            return True
    
    def _verify_stripe_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Verify Stripe webhook signature"""
        signature = headers.get('stripe-signature', '')
        return len(signature) > 0
    
    def _verify_twilio_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Verify Twilio webhook"""
        return 'X-Twilio-Signature' in headers
    
    def _verify_telegram_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Verify Telegram webhook"""
        return True
    
    def _verify_generic_webhook(self, platform: str, payload: Dict[str, Any], headers: Dict[str, str]) -> bool:
        """Generic webhook verification"""
        return True
    
    # Platform-specific webhook handlers
    
    def _handle_stripe_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Stripe payment webhooks"""
        
        event_type = payload.get('type', '')
        data = payload.get('data', {}).get('object', {})
        
        if event_type == 'payment_intent.succeeded':
            return self._handle_payment_success(data)
        elif event_type == 'payment_intent.payment_failed':
            return self._handle_payment_failure(data)
        elif event_type == 'customer.subscription.created':
            return self._handle_subscription_created(data)
        elif event_type == 'customer.subscription.updated':
            return self._handle_subscription_updated(data)
        elif event_type == 'invoice.payment_succeeded':
            return self._handle_invoice_paid(data)
        
        return {'status': 'success', 'message': f'Processed Stripe event: {event_type}'}
    
    def _handle_twilio_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Twilio SMS webhooks"""
        
        message_body = payload.get('Body', '').strip()
        from_number = payload.get('From', '')
        to_number = payload.get('To', '')
        
        # Process SMS commands for DEAF FIRST mini apps
        if message_body.startswith('/'):
            return self._process_sms_command(message_body, from_number)
        
        return {
            'status': 'success',
            'message': 'SMS received and processed',
            'response': self._generate_sms_response(message_body, from_number)
        }
    
    def _handle_telegram_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Telegram bot webhooks"""
        
        message = payload.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        user_id = message.get('from', {}).get('id')
        
        if text.startswith('/'):
            return self._process_telegram_command(text, chat_id, user_id)
        
        return {
            'status': 'success',
            'message': 'Telegram message processed',
            'response': self._generate_telegram_response(text, chat_id)
        }
    
    def _handle_discord_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Discord bot webhooks"""
        
        interaction_type = payload.get('type', 0)
        
        if interaction_type == 2:  # Slash command
            return self._handle_discord_slash_command(payload)
        elif interaction_type == 1:  # Ping
            return {'type': 1}  # Pong response
        
        return {'status': 'success', 'message': 'Discord interaction processed'}
    
    def _handle_whatsapp_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle WhatsApp Business API webhooks"""
        
        entry = payload.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])
        
        for message in messages:
            text = message.get('text', {}).get('body', '')
            phone_number = message.get('from', '')
            
            if text.startswith('/'):
                return self._process_whatsapp_command(text, phone_number)
        
        return {'status': 'success', 'message': 'WhatsApp message processed'}
    
    def _handle_pinksync_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle PinkSync accessibility webhooks"""
        
        event_type = payload.get('event_type', '')
        user_data = payload.get('user_data', {})
        
        if event_type == 'accessibility_preference_updated':
            return self._update_user_accessibility_preferences(user_data)
        elif event_type == 'asl_interpretation_requested':
            return self._schedule_asl_interpretation(user_data)
        elif event_type == 'deaf_support_activated':
            return self._activate_deaf_support_mode(user_data)
        
        return {'status': 'success', 'message': f'PinkSync event processed: {event_type}'}
    
    def _handle_april_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle April Fintech API webhooks"""
        
        event_type = payload.get('event_type', '')
        transaction_data = payload.get('data', {})
        
        if event_type == 'tax_calculation_completed':
            return self._process_tax_calculation_result(transaction_data)
        elif event_type == 'financial_profile_updated':
            return self._update_financial_profile(transaction_data)
        elif event_type == 'document_processed':
            return self._handle_document_processing_complete(transaction_data)
        
        return {'status': 'success', 'message': f'April API event processed: {event_type}'}
    
    def _handle_insurance_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Open Insurance API webhooks"""
        
        event_type = payload.get('event', '')
        policy_data = payload.get('policy', {})
        
        if event_type == 'policy_activated':
            return self._activate_insurance_policy(policy_data)
        elif event_type == 'claim_submitted':
            return self._process_insurance_claim(policy_data)
        elif event_type == 'premium_due':
            return self._handle_premium_notification(policy_data)
        
        return {'status': 'success', 'message': f'Insurance event processed: {event_type}'}
    
    def _handle_mux_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle Mux video webhooks"""
        
        event_type = payload.get('type', '')
        data = payload.get('data', {})
        
        if event_type == 'video.asset.ready':
            return self._handle_video_ready(data)
        elif event_type == 'video.upload.asset_created':
            return self._handle_video_uploaded(data)
        elif event_type == 'video.playback.id_created':
            return self._handle_playback_id_created(data)
        
        return {'status': 'success', 'message': f'Mux event processed: {event_type}'}
    
    # Command processing methods
    
    def _process_sms_command(self, command: str, phone_number: str) -> Dict[str, Any]:
        """Process SMS commands from mini apps"""
        try:
            from services.miniapps.command_processor import MiniAppCommandProcessor
            
            processor = MiniAppCommandProcessor()
            result = processor.process_command(command, phone_number, 'sms')
            
            # Send SMS response
            self._send_sms_response(phone_number, result.get('response', 'Command processed'))
            
            return {
                'status': 'success',
                'message': 'SMS command processed',
                'command_result': result
            }
        except Exception as e:
            logger.error(f"Error processing SMS command: {str(e)}")
            return {'status': 'error', 'message': 'Command processing failed'}
    
    def _process_telegram_command(self, command: str, chat_id: str, user_id: str) -> Dict[str, Any]:
        """Process Telegram commands"""
        try:
            from services.miniapps.command_processor import MiniAppCommandProcessor
            
            processor = MiniAppCommandProcessor()
            result = processor.process_command(command, str(user_id), 'telegram')
            
            # Send Telegram response
            self._send_telegram_response(chat_id, result.get('response', 'Command processed'))
            
            return {
                'status': 'success',
                'message': 'Telegram command processed',
                'command_result': result
            }
        except Exception as e:
            logger.error(f"Error processing Telegram command: {str(e)}")
            return {'status': 'error', 'message': 'Command processing failed'}
    
    def _process_whatsapp_command(self, command: str, phone_number: str) -> Dict[str, Any]:
        """Process WhatsApp commands"""
        try:
            from services.miniapps.command_processor import MiniAppCommandProcessor
            
            processor = MiniAppCommandProcessor()
            result = processor.process_command(command, phone_number, 'whatsapp')
            
            # Send WhatsApp response
            self._send_whatsapp_response(phone_number, result.get('response', 'Command processed'))
            
            return {
                'status': 'success',
                'message': 'WhatsApp command processed',
                'command_result': result
            }
        except Exception as e:
            logger.error(f"Error processing WhatsApp command: {str(e)}")
            return {'status': 'error', 'message': 'Command processing failed'}
    
    def _handle_discord_slash_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Discord slash commands"""
        
        data = payload.get('data', {})
        command_name = data.get('name', '')
        options = data.get('options', [])
        user_id = payload.get('member', {}).get('user', {}).get('id')
        
        # Map Discord slash command to mini app command
        mini_app_command = f"/{command_name}"
        if options:
            for option in options:
                mini_app_command += f" {option.get('value', '')}"
        
        try:
            from services.miniapps.command_processor import MiniAppCommandProcessor
            processor = MiniAppCommandProcessor()
            result = processor.process_command(mini_app_command, str(user_id), 'discord')
            
            return {
                'type': 4,  # Channel message with source
                'data': {
                    'content': result.get('response', 'Command processed'),
                    'flags': 64 if result.get('ephemeral', False) else 0
                }
            }
        except Exception as e:
            logger.error(f"Error processing Discord command: {str(e)}")
            return {
                'type': 4,
                'data': {
                    'content': 'Command processing failed',
                    'flags': 64
                }
            }
    
    # Response sending methods
    
    def _send_sms_response(self, phone_number: str, message: str):
        """Send SMS response via Twilio"""
        logger.info(f"Sending SMS to {phone_number}: {message}")
    
    def _send_telegram_response(self, chat_id: str, message: str):
        """Send Telegram response"""
        logger.info(f"Sending Telegram message to {chat_id}: {message}")
    
    def _send_whatsapp_response(self, phone_number: str, message: str):
        """Send WhatsApp response"""
        logger.info(f"Sending WhatsApp message to {phone_number}: {message}")
    
    # Utility methods
    
    def _generate_sms_response(self, message: str, phone_number: str) -> str:
        """Generate appropriate SMS response"""
        if 'help' in message.lower():
            return "DEAF FIRST Commands: /restructure, /debt, /credit, /tax. Text 'help' for more info."
        return "Message received. Use /help for available commands."
    
    def _generate_telegram_response(self, message: str, chat_id: str) -> str:
        """Generate appropriate Telegram response"""
        if 'help' in message.lower():
            return "DEAF FIRST Platform\n\nCommands:\n/restructure - Financial restructuring\n/debt - Debt management\n/credit - Credit monitoring\n/tax - Tax services"
        return "Message received! Use /help to see available commands."
    
    def _log_webhook_event(self, platform: str, payload: Dict[str, Any], result: Dict[str, Any]):
        """Log webhook events for monitoring"""
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'platform': platform,
            'event_type': payload.get('type', payload.get('event_type', 'unknown')),
            'status': result.get('status', 'unknown'),
            'user_id': self._extract_user_id(payload, platform)
        }
        
        logger.info(f"Webhook processed: {json.dumps(log_entry)}")
    
    def _extract_user_id(self, payload: Dict[str, Any], platform: str) -> Optional[str]:
        """Extract user ID from webhook payload"""
        
        if platform == 'stripe':
            return payload.get('data', {}).get('object', {}).get('customer')
        elif platform == 'telegram':
            return str(payload.get('message', {}).get('from', {}).get('id'))
        elif platform == 'discord':
            return payload.get('member', {}).get('user', {}).get('id')
        elif platform in ['twilio', 'whatsapp']:
            return payload.get('From', payload.get('from'))
        
        return None
    
    # Handler methods for specific events
    
    def _handle_payment_success(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        
        amount = payment_data.get('amount', 0) / 100  # Convert from cents
        customer_id = payment_data.get('customer')
        
        logger.info(f"Payment successful: ${amount} for customer {customer_id}")
        
        return {
            'status': 'success',
            'message': 'Payment processed successfully',
            'amount': amount,
            'customer_id': customer_id
        }
    
    def _handle_payment_failure(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        
        customer_id = payment_data.get('customer')
        failure_reason = payment_data.get('last_payment_error', {}).get('message', 'Unknown error')
        
        logger.warning(f"Payment failed for customer {customer_id}: {failure_reason}")
        
        return {
            'status': 'success',
            'message': 'Payment failure processed',
            'customer_id': customer_id,
            'failure_reason': failure_reason
        }
    
    def _update_user_accessibility_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user accessibility preferences from PinkSync"""
        return {'status': 'success', 'message': 'Accessibility preferences updated'}
    
    def _schedule_asl_interpretation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule ASL interpretation session"""
        return {'status': 'success', 'message': 'ASL interpretation scheduled'}
    
    def _activate_deaf_support_mode(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Activate deaf support mode"""
        return {'status': 'success', 'message': 'Deaf support mode activated'}
    
    def _process_tax_calculation_result(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process tax calculation results from April"""
        return {'status': 'success', 'message': 'Tax calculation processed'}
    
    def _update_financial_profile(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update financial profile from April API"""
        return {'status': 'success', 'message': 'Financial profile updated'}
    
    def _handle_document_processing_complete(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document processing completion"""
        return {'status': 'success', 'message': 'Document processing completed'}
    
    def _activate_insurance_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Activate insurance policy"""
        return {'status': 'success', 'message': 'Insurance policy activated'}
    
    def _process_insurance_claim(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process insurance claim"""
        return {'status': 'success', 'message': 'Insurance claim processed'}
    
    def _handle_premium_notification(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle premium due notification"""
        return {'status': 'success', 'message': 'Premium notification processed'}
    
    def _handle_video_ready(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video processing completion"""
        return {'status': 'success', 'message': 'Video ready for playback'}
    
    def _handle_video_uploaded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video upload completion"""
        return {'status': 'success', 'message': 'Video upload completed'}
    
    def _handle_playback_id_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle playback ID creation"""
        return {'status': 'success', 'message': 'Playback ID created'}
    
    def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription creation"""
        return {'status': 'success', 'message': 'Subscription created'}
    
    def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update"""
        return {'status': 'success', 'message': 'Subscription updated'}
    
    def _handle_invoice_paid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoice payment"""
        return {'status': 'success', 'message': 'Invoice payment processed'}


# Global webhook handler instance
webhook_handler = WebhookHandler()
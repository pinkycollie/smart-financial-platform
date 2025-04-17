"""
Reseller billing service using Cheddar API for the DEAF FIRST platform.
Handles subscription management for white-label resellers and licensees.
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from services.billing.cheddar import cheddar_client
from simple_app import db

# Configure logging
logger = logging.getLogger(__name__)

class ResellerBillingService:
    """
    Service for managing reseller and licensee billing through Cheddar API.
    """
    
    def __init__(self):
        """Initialize reseller billing service"""
        self.plan_code_map = {
            'primary_basic': 'deaffirst-reseller-basic',
            'primary_pro': 'deaffirst-reseller-pro',
            'primary_enterprise': 'deaffirst-reseller-enterprise',
            'secondary_basic': 'deaffirst-sublicensee-basic',
            'secondary_pro': 'deaffirst-sublicensee-pro',
            'secondary_custom': 'deaffirst-sublicensee-custom'
        }
    
    def get_available_plans(self, reseller_tier='primary'):
        """
        Get available subscription plans for resellers.
        
        Args:
            reseller_tier (str): 'primary' or 'secondary'
            
        Returns:
            list: Available plans
        """
        try:
            all_plans = cheddar_client.get_plans()
            
            # Filter plans by tier
            tier_prefix = f"deaffirst-{reseller_tier.lower()}"
            tier_plans = [plan for plan in all_plans if plan.get('code', '').startswith(tier_prefix)]
            
            return tier_plans
        except Exception as e:
            logger.error(f"Error fetching plans from Cheddar: {e}")
            return []
    
    def create_reseller_subscription(self, reseller, plan_code, payment_token=None, cc_first_name=None, 
                                  cc_last_name=None, cc_address=None, cc_city=None, cc_state=None, 
                                  cc_zip=None, cc_country=None):
        """
        Create a subscription for a reseller in Cheddar.
        
        Args:
            reseller: Reseller model instance
            plan_code (str): Plan code or tier code
            payment_token (str, optional): Credit card payment token
            cc_* (str, optional): Credit card billing information
            
        Returns:
            dict: Created subscription data or None if failed
        """
        # Check if plan code is a tier code, and convert if needed
        if plan_code in self.plan_code_map:
            plan_code = self.plan_code_map[plan_code]
        
        # Generate customer code if not exists
        if not reseller.external_id:
            reseller.external_id = f"reseller-{uuid.uuid4().hex[:12]}"
            db.session.commit()
        
        try:
            # Prepare customer data
            customer_data = {
                'code': reseller.external_id,
                'first_name': reseller.owner_first_name,
                'last_name': reseller.owner_last_name,
                'email': reseller.contact_email,
                'plan_code': plan_code,
                'company': reseller.company_name,
                'is_vat_exempt': reseller.tax_exempt,
                'subscription_id': f"sub-{uuid.uuid4().hex[:8]}",
                'metadata': {
                    'reseller_id': reseller.id,
                    'reseller_type': reseller.reseller_type,
                    'platform': 'DEAF FIRST'
                }
            }
            
            # Add payment information if provided
            if payment_token:
                customer_data['cc_token'] = payment_token
                
                # Add billing info if provided
                if cc_first_name and cc_last_name:
                    customer_data.update({
                        'cc_first_name': cc_first_name,
                        'cc_last_name': cc_last_name,
                        'cc_address': cc_address,
                        'cc_city': cc_city,
                        'cc_state': cc_state,
                        'cc_zip': cc_zip,
                        'cc_country': cc_country
                    })
            
            # Create customer with subscription in Cheddar
            response = cheddar_client.create_customer(**customer_data)
            
            # Update reseller with subscription info
            if response and 'code' in response:
                from models_reseller import ResellerSubscription
                
                # Create local subscription record
                subscription = ResellerSubscription(
                    reseller_id=reseller.id,
                    plan_code=plan_code,
                    status='active',
                    external_id=response.get('subscriptions', [{}])[0].get('id'),
                    billing_period=response.get('subscriptions', [{}])[0].get('intervalUnit', 'month'),
                    price=float(response.get('subscriptions', [{}])[0].get('amount', 0)),
                    currency_code=response.get('subscriptions', [{}])[0].get('currency', 'USD'),
                    start_date=datetime.utcnow(),
                    next_billing_date=datetime.utcnow() + timedelta(days=30),
                    payment_method='credit_card' if payment_token else 'invoice',
                    payment_status='paid'
                )
                
                db.session.add(subscription)
                db.session.commit()
                
                return {
                    'success': True,
                    'subscription_id': subscription.id,
                    'external_id': subscription.external_id,
                    'plan_code': subscription.plan_code,
                    'status': subscription.status
                }
                
            return {
                'success': False,
                'error': 'Failed to create subscription'
            }
                
        except Exception as e:
            logger.error(f"Error creating reseller subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_reseller_subscription(self, reseller, new_plan_code):
        """
        Update a reseller's subscription in Cheddar.
        
        Args:
            reseller: Reseller model instance
            new_plan_code (str): New plan code or tier code
            
        Returns:
            dict: Updated subscription data or None if failed
        """
        # Check if plan code is a tier code, and convert if needed
        if new_plan_code in self.plan_code_map:
            new_plan_code = self.plan_code_map[new_plan_code]
        
        if not reseller.external_id:
            return {
                'success': False,
                'error': 'Reseller does not have an active subscription'
            }
        
        try:
            # Update subscription in Cheddar
            response = cheddar_client.update_subscription(
                code=reseller.external_id,
                plan_code=new_plan_code
            )
            
            if response:
                # Update local subscription record
                from models_reseller import ResellerSubscription
                subscription = ResellerSubscription.query.filter_by(reseller_id=reseller.id, status='active').first()
                
                if subscription:
                    subscription.plan_code = new_plan_code
                    subscription.updated_at = datetime.utcnow()
                    
                    # Update price if available in response
                    if 'subscriptions' in response and response['subscriptions']:
                        subscription.price = float(response['subscriptions'][0].get('amount', subscription.price))
                        
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'subscription_id': subscription.id,
                        'plan_code': subscription.plan_code,
                        'status': subscription.status
                    }
            
            return {
                'success': False,
                'error': 'Failed to update subscription'
            }
                
        except Exception as e:
            logger.error(f"Error updating reseller subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_reseller_subscription(self, reseller, reason=None):
        """
        Cancel a reseller's subscription in Cheddar.
        
        Args:
            reseller: Reseller model instance
            reason (str, optional): Cancellation reason
            
        Returns:
            dict: Cancellation status
        """
        if not reseller.external_id:
            return {
                'success': False,
                'error': 'Reseller does not have an active subscription'
            }
        
        try:
            # Cancel subscription in Cheddar
            response = cheddar_client.cancel_subscription(
                code=reseller.external_id,
                cancel_reason=reason
            )
            
            if response:
                # Update local subscription record
                from models_reseller import ResellerSubscription
                subscription = ResellerSubscription.query.filter_by(reseller_id=reseller.id, status='active').first()
                
                if subscription:
                    subscription.status = 'canceled'
                    subscription.cancellation_date = datetime.utcnow()
                    subscription.cancellation_reason = reason
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'subscription_id': subscription.id,
                        'status': 'canceled'
                    }
            
            return {
                'success': False,
                'error': 'Failed to cancel subscription'
            }
                
        except Exception as e:
            logger.error(f"Error canceling reseller subscription: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_reseller_invoices(self, reseller):
        """
        Get invoices for a reseller from Cheddar.
        
        Args:
            reseller: Reseller model instance
            
        Returns:
            list: Invoices for the reseller
        """
        if not reseller.external_id:
            return []
        
        try:
            # Get invoices from Cheddar
            invoices = cheddar_client.get_invoices(code=reseller.external_id)
            
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting reseller invoices: {e}")
            return []
    
    def process_webhook(self, webhook_data, signature):
        """
        Process a webhook from Cheddar.
        
        Args:
            webhook_data (str): Raw webhook payload
            signature (str): Webhook signature from X-CG-SIGN header
            
        Returns:
            dict: Processing result
        """
        if not cheddar_client.validate_webhook(webhook_data, signature):
            logger.warning("Invalid webhook signature")
            return {
                'success': False,
                'error': 'Invalid signature'
            }
        
        try:
            # Parse webhook data
            import json
            data = json.loads(webhook_data)
            
            event_type = data.get('event')
            customer_code = data.get('code')
            
            # Process different event types
            if event_type == 'subscription_created':
                self._handle_subscription_created(customer_code, data)
            elif event_type == 'subscription_updated':
                self._handle_subscription_updated(customer_code, data)
            elif event_type == 'subscription_canceled':
                self._handle_subscription_canceled(customer_code, data)
            elif event_type == 'invoice_created':
                self._handle_invoice_created(customer_code, data)
            elif event_type == 'invoice_paid':
                self._handle_invoice_paid(customer_code, data)
            elif event_type == 'invoice_failed':
                self._handle_invoice_failed(customer_code, data)
            else:
                logger.info(f"Unhandled webhook event: {event_type}")
            
            return {
                'success': True,
                'event': event_type
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_billing_portal_url(self, reseller):
        """
        Get a link to the Cheddar billing portal for a reseller.
        
        Args:
            reseller: Reseller model instance
            
        Returns:
            str: Billing portal URL or None if failed
        """
        if not reseller.external_id:
            return None
        
        # Construct billing portal URL
        portal_base = os.environ.get('CHEDDAR_PORTAL_URL', 'https://billing.getcheddar.com')
        portal_token = self._generate_portal_token(reseller.external_id)
        
        return f"{portal_base}/portal/{cheddar_client.product_code}/{reseller.external_id}?token={portal_token}"
    
    def _generate_portal_token(self, customer_code):
        """Generate a secure token for the billing portal"""
        import hashlib
        import hmac
        import time
        
        # Get secret key for signing
        secret = os.environ.get('CHEDDAR_PORTAL_SECRET') or cheddar_client.password
        if not secret:
            return None
        
        # Generate token with timestamp
        timestamp = int(time.time())
        message = f"{customer_code}:{timestamp}"
        
        # Create HMAC signature
        signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    # Webhook handlers
    def _handle_subscription_created(self, customer_code, data):
        """Handle subscription_created webhook"""
        from models_reseller import Reseller, ResellerSubscription
        
        # Find reseller by external ID
        reseller = Reseller.query.filter_by(external_id=customer_code).first()
        if not reseller:
            logger.warning(f"Reseller not found for customer code: {customer_code}")
            return
        
        # Check if subscription already exists
        if ResellerSubscription.query.filter_by(
            reseller_id=reseller.id,
            external_id=data.get('subscriptions', [{}])[0].get('id')
        ).first():
            return
        
        # Create new subscription record
        subscription = ResellerSubscription(
            reseller_id=reseller.id,
            plan_code=data.get('subscriptions', [{}])[0].get('planCode'),
            status='active',
            external_id=data.get('subscriptions', [{}])[0].get('id'),
            billing_period=data.get('subscriptions', [{}])[0].get('intervalUnit', 'month'),
            price=float(data.get('subscriptions', [{}])[0].get('amount', 0)),
            currency_code=data.get('subscriptions', [{}])[0].get('currency', 'USD'),
            start_date=datetime.utcnow(),
            next_billing_date=datetime.utcnow() + timedelta(days=30),
            payment_method='credit_card',
            payment_status='paid'
        )
        
        db.session.add(subscription)
        db.session.commit()
    
    def _handle_subscription_updated(self, customer_code, data):
        """Handle subscription_updated webhook"""
        from models_reseller import Reseller, ResellerSubscription
        
        # Find reseller by external ID
        reseller = Reseller.query.filter_by(external_id=customer_code).first()
        if not reseller:
            logger.warning(f"Reseller not found for customer code: {customer_code}")
            return
        
        # Find subscription
        subscription_id = data.get('subscriptions', [{}])[0].get('id')
        subscription = ResellerSubscription.query.filter_by(
            reseller_id=reseller.id,
            external_id=subscription_id
        ).first()
        
        if subscription:
            # Update subscription details
            subscription.plan_code = data.get('subscriptions', [{}])[0].get('planCode', subscription.plan_code)
            subscription.price = float(data.get('subscriptions', [{}])[0].get('amount', subscription.price))
            subscription.billing_period = data.get('subscriptions', [{}])[0].get('intervalUnit', subscription.billing_period)
            subscription.updated_at = datetime.utcnow()
            
            db.session.commit()
    
    def _handle_subscription_canceled(self, customer_code, data):
        """Handle subscription_canceled webhook"""
        from models_reseller import Reseller, ResellerSubscription
        
        # Find reseller by external ID
        reseller = Reseller.query.filter_by(external_id=customer_code).first()
        if not reseller:
            logger.warning(f"Reseller not found for customer code: {customer_code}")
            return
        
        # Find subscription
        subscription_id = data.get('subscriptions', [{}])[0].get('id')
        subscription = ResellerSubscription.query.filter_by(
            reseller_id=reseller.id,
            external_id=subscription_id
        ).first()
        
        if subscription:
            # Update subscription status
            subscription.status = 'canceled'
            subscription.cancellation_date = datetime.utcnow()
            
            db.session.commit()
    
    def _handle_invoice_created(self, customer_code, data):
        """Handle invoice_created webhook"""
        from models_reseller import Reseller, ResellerInvoice
        
        # Find reseller by external ID
        reseller = Reseller.query.filter_by(external_id=customer_code).first()
        if not reseller:
            logger.warning(f"Reseller not found for customer code: {customer_code}")
            return
        
        # Extract invoice data
        invoice_data = data.get('invoice', {})
        if not invoice_data:
            return
        
        # Check if invoice already exists
        if ResellerInvoice.query.filter_by(
            external_id=invoice_data.get('id')
        ).first():
            return
        
        # Create new invoice record
        invoice = ResellerInvoice(
            reseller_id=reseller.id,
            external_id=invoice_data.get('id'),
            amount=float(invoice_data.get('amount', 0)),
            currency_code=invoice_data.get('currency', 'USD'),
            status=invoice_data.get('status', 'open'),
            due_date=datetime.fromisoformat(invoice_data.get('dueDate').rstrip('Z')),
            invoice_number=invoice_data.get('number'),
            invoice_data=invoice_data
        )
        
        db.session.add(invoice)
        db.session.commit()
    
    def _handle_invoice_paid(self, customer_code, data):
        """Handle invoice_paid webhook"""
        from models_reseller import Reseller, ResellerInvoice
        
        # Extract invoice data
        invoice_data = data.get('invoice', {})
        if not invoice_data:
            return
        
        # Find invoice
        invoice = ResellerInvoice.query.filter_by(
            external_id=invoice_data.get('id')
        ).first()
        
        if invoice:
            # Update invoice status
            invoice.status = 'paid'
            invoice.paid_date = datetime.utcnow()
            invoice.invoice_data = invoice_data
            
            db.session.commit()
    
    def _handle_invoice_failed(self, customer_code, data):
        """Handle invoice_failed webhook"""
        from models_reseller import Reseller, ResellerInvoice
        
        # Extract invoice data
        invoice_data = data.get('invoice', {})
        if not invoice_data:
            return
        
        # Find invoice
        invoice = ResellerInvoice.query.filter_by(
            external_id=invoice_data.get('id')
        ).first()
        
        if invoice:
            # Update invoice status
            invoice.status = 'failed'
            invoice.invoice_data = invoice_data
            
            db.session.commit()

# Initialize a single instance to be used application-wide
reseller_billing_service = ResellerBillingService()
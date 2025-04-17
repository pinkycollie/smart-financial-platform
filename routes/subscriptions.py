from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_required, current_user
from models import db, User, Subscription
from datetime import datetime, timedelta
import logging
import os

# Create a Blueprint for subscription routes
subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscriptions')

# Logger
logger = logging.getLogger(__name__)

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    'monthly': {
        'name': 'DEAF FIRST Premium (Monthly)',
        'price': 19.99,
        'interval': 'monthly',
        'features': [
            'Full ASL financial video library access',
            'Advanced tax tools with CPA integration',
            'Bloomberg financial data integration',
            'Specialized insurance bundle access',
            'Personalized financial recommendations'
        ]
    },
    'yearly': {
        'name': 'DEAF FIRST Premium (Yearly)',
        'price': 199.99,
        'interval': 'yearly',
        'features': [
            'All Monthly features',
            'Two months free (save 16%)',
            'Priority deaf support bot access',
            'Exclusive financial webinars with ASL',
            'Annual financial health review'
        ]
    }
}

@subscription_bp.route('/')
def subscription_plans():
    """Display available subscription plans"""
    return render_template(
        'subscriptions/plans.html', 
        plans=SUBSCRIPTION_PLANS,
        title="Premium Subscription Plans"
    )

@subscription_bp.route('/checkout/<plan_id>')
@login_required
def checkout(plan_id):
    """Process checkout for a subscription plan"""
    if plan_id not in SUBSCRIPTION_PLANS:
        flash('Invalid subscription plan.', 'danger')
        return redirect(url_for('subscription.subscription_plans'))
    
    plan = SUBSCRIPTION_PLANS[plan_id]
    
    # Check if Stripe is configured
    if not current_app.config.get('STRIPE_SECRET_KEY'):
        # For demo purposes, create a subscription without payment processing
        # In production, this would redirect to Stripe Checkout
        subscription = create_demo_subscription(plan)
        
        if subscription:
            flash('Your premium subscription has been activated!', 'success')
            return redirect(url_for('subscription.thank_you'))
        else:
            flash('There was an error processing your subscription.', 'danger')
            return redirect(url_for('subscription.subscription_plans'))
    
    # This section would normally integrate with Stripe Checkout
    # For now, just redirect to a thank you page with a demo subscription
    stripe_public_key = current_app.config.get('STRIPE_PUBLIC_KEY', 'pk_test_demo')
    
    return render_template(
        'subscriptions/checkout.html',
        plan=plan,
        plan_id=plan_id,
        stripe_public_key=stripe_public_key
    )

@subscription_bp.route('/thank-you')
@login_required
def thank_you():
    """Thank you page after successful subscription"""
    return render_template('subscriptions/thank_you.html')

@subscription_bp.route('/manage')
@login_required
def manage_subscription():
    """Manage existing subscription"""
    # Get user's active subscription
    subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    
    return render_template(
        'subscriptions/manage.html',
        subscription=subscription,
        plans=SUBSCRIPTION_PLANS
    )

@subscription_bp.route('/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel subscription"""
    subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).first()
    
    if not subscription:
        flash('No active subscription found.', 'warning')
        return redirect(url_for('subscription.manage_subscription'))
    
    # Update subscription status
    subscription.status = 'cancelled'
    subscription.cancelled_at = datetime.utcnow()
    db.session.commit()
    
    flash('Your subscription has been cancelled. You will have access until the end of your billing period.', 'info')
    return redirect(url_for('subscription.manage_subscription'))

@subscription_bp.route('/premium-content')
@login_required
def premium_content():
    """Example of premium content"""
    if not current_user.is_premium():
        flash('This content requires a premium subscription.', 'warning')
        return redirect(url_for('subscription.subscription_plans'))
    
    return render_template('subscriptions/premium_content.html')

def create_demo_subscription(plan):
    """Create a demo subscription for testing"""
    try:
        # Calculate end date based on billing interval
        if plan['interval'] == 'monthly':
            end_date = datetime.utcnow() + timedelta(days=30)
            next_billing = end_date
        else:
            end_date = datetime.utcnow() + timedelta(days=365)
            next_billing = end_date
        
        # Create subscription record
        subscription = Subscription(
            user_id=current_user.id,
            plan_name=plan['name'],
            price=plan['price'],
            billing_interval=plan['interval'],
            status='active',
            start_date=datetime.utcnow(),
            end_date=end_date,
            next_billing_date=next_billing
        )
        
        # Update user account type
        current_user.account_type = 'premium'
        
        # Save to database
        db.session.add(subscription)
        db.session.commit()
        
        return subscription
    except Exception as e:
        logger.error(f"Error creating demo subscription: {str(e)}")
        db.session.rollback()
        return None
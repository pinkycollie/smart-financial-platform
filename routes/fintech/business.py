from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
import logging

# Create a Blueprint for business routes
business_bp = Blueprint('business', __name__, url_prefix='/fintech/business')

# Logger
logger = logging.getLogger(__name__)

@business_bp.route('/')
def business_dashboard():
    """Main business dashboard page"""
    return render_template('fintech/business/dashboard.html')

@business_bp.route('/pitch-deck')
def pitch_deck():
    """Pitch deck presentation for DEAF FIRST"""
    return render_template('fintech/business/pitch_deck.html')

@business_bp.route('/impact-data')
def impact_data():
    """Financial disparity impact data for the deaf community"""
    return render_template('fintech/business/impact_data.html')

@business_bp.route('/partnerships/bloomberg')
def bloomberg_partnership():
    """Bloomberg partnership and integration page"""
    return render_template('fintech/business/bloomberg_partnership.html')

@business_bp.route('/partnerships')
def partnerships():
    """Business partnerships overview"""
    return render_template('fintech/business/partnerships.html')

@business_bp.route('/market-analysis')
def market_analysis():
    """Market analysis for deaf financial services"""
    return render_template('fintech/business/market_analysis.html')
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, session
from flask_login import login_required, current_user
import logging

# Create a Blueprint for business routes
business_bp = Blueprint('business', __name__, url_prefix='/business')

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

@business_bp.route('/pitch-deck')
def pitch_deck():
    """Show the business model and pitch deck for the DEAF FIRST platform"""
    # Get ASL videos for business context
    asl_videos = []
    if mux_client:
        try:
            asl_videos = mux_client.get_asl_videos_for_context('business')
        except Exception as e:
            logger.error(f"Error fetching business ASL videos: {e}")
    
    return render_template('fintech/business/pitch_deck.html', asl_videos=asl_videos)
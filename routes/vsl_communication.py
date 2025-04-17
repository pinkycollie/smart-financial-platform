"""
VSL Communication Routes for DEAF FIRST Platform
Routes for video communication and ASL interpretation using VSL Labs API
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, session
from flask_login import login_required, current_user
import logging
import json
import os
from datetime import datetime

# Create a Blueprint for VSL communication routes
vsl_bp = Blueprint('vsl', __name__, url_prefix='/communication')

# Logger
logger = logging.getLogger(__name__)

# Import VSL client
from services.deaf_first.vsl_integration import vsl_client

@vsl_bp.route('/')
@login_required
def communication_dashboard():
    """Main communication dashboard"""
    return render_template('communication/dashboard.html')

@vsl_bp.route('/video-messages')
@login_required
def video_messages():
    """Video message inbox (Marco Polo-style async communication)"""
    # In production, we would fetch actual messages from the database
    # For now, we'll use sample data
    messages = []
    
    # Check if API is available to show appropriate UI options
    vsl_available = vsl_client and vsl_client.initialized
    
    return render_template(
        'communication/video_messages.html',
        messages=messages,
        vsl_available=vsl_available
    )

@vsl_bp.route('/create-message', methods=['GET', 'POST'])
@login_required
def create_message():
    """Create a new video message"""
    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        message_type = request.form.get('message_type')
        message_data = request.form.get('message_data')
        
        # In production, we would save the message to the database
        # and potentially process it through VSL Labs API
        
        flash('Your message has been sent.', 'success')
        return redirect(url_for('vsl.video_messages'))
        
    # GET request - show message creation form
    return render_template('communication/create_message.html')

@vsl_bp.route('/meetings')
@login_required
def video_meetings():
    """Video meetings schedule and history"""
    # In production, fetch actual meetings from database
    # For now, use sample data
    meetings = []
    
    return render_template(
        'communication/meetings.html',
        meetings=meetings
    )

@vsl_bp.route('/schedule-meeting', methods=['GET', 'POST'])
@login_required
def schedule_meeting():
    """Schedule a new video meeting"""
    if request.method == 'POST':
        meeting_type = request.form.get('meeting_type')
        professional_id = request.form.get('professional_id')
        meeting_date = request.form.get('meeting_date')
        meeting_time = request.form.get('meeting_time')
        topic = request.form.get('topic')
        
        # In production, save meeting to database and send notifications
        
        # If this is a premium feature, check subscription status
        if meeting_type == 'financial_advisor' and not current_user.is_premium():
            flash('Meetings with financial advisors require a premium subscription.', 'warning')
            return redirect(url_for('subscription.subscription_plans'))
        
        flash('Your meeting has been scheduled.', 'success')
        return redirect(url_for('vsl.video_meetings'))
        
    # GET request - show meeting scheduling form
    return render_template('communication/schedule_meeting.html')

@vsl_bp.route('/join-meeting/<meeting_id>')
@login_required
def join_meeting(meeting_id):
    """Join a video meeting"""
    # In production, fetch meeting details and generate join URL
    # Potentially create a VSL Labs video session
    
    if vsl_client and vsl_client.initialized:
        try:
            # Create VSL video session
            session_result = vsl_client.create_asl_video_chat(
                session_name=f"Meeting-{meeting_id}",
                user_id=str(current_user.id)
            )
            
            if session_result and 'session_url' in session_result:
                # Redirect to VSL video interface
                return redirect(session_result['session_url'])
        except Exception as e:
            logger.error(f"Error creating VSL video session: {str(e)}")
    
    # Fallback to standard meeting template if VSL integration fails
    return render_template(
        'communication/meeting_room.html',
        meeting_id=meeting_id
    )

@vsl_bp.route('/api/interpret', methods=['POST'])
@login_required
def api_interpret_asl():
    """API endpoint to interpret text as ASL"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        if not vsl_client or not vsl_client.initialized:
            return jsonify({
                'error': 'VSL API not configured',
                'fallback': True,
                'text': text
            }), 503
            
        # Get ASL interpretation
        result = vsl_client.get_asl_interpretation(text)
        
        if not result:
            return jsonify({'error': 'Failed to get ASL interpretation'}), 500
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in ASL interpretation API: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
@vsl_bp.route('/api/translate', methods=['POST'])
@login_required
def api_translate_video():
    """API endpoint to translate ASL video to text"""
    try:
        data = request.get_json()
        video_url = data.get('video_url', '')
        
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400
            
        if not vsl_client or not vsl_client.initialized:
            return jsonify({
                'error': 'VSL API not configured',
                'fallback': True
            }), 503
            
        # Translate ASL video
        result = vsl_client.translate_asl_video(video_url)
        
        if not result:
            return jsonify({'error': 'Failed to translate ASL video'}), 500
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in ASL video translation API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@vsl_bp.route('/api/financial-term', methods=['GET'])
def api_financial_term():
    """API endpoint to get ASL for financial term"""
    term = request.args.get('term', '')
    
    if not term:
        return jsonify({'error': 'No term provided'}), 400
        
    if not vsl_client or not vsl_client.initialized:
        return jsonify({
            'error': 'VSL API not configured',
            'fallback': True,
            'term': term
        }), 503
        
    # Get financial terminology
    result = vsl_client.get_financial_terminology(term)
    
    if not result:
        return jsonify({'error': 'Failed to get financial terminology'}), 500
        
    return jsonify(result)
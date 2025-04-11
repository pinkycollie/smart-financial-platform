import logging
from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.routes.accessibility import accessibility_bp
from app.services.accessibility.mux_client import MuxClient
from app.services.accessibility.deaf_support_bot import DeafSupportBot
from app import db

logger = logging.getLogger(__name__)

# Initialize services
mux_client = MuxClient()
deaf_support_bot = DeafSupportBot()

@accessibility_bp.route('/asl-videos')
@login_required
def asl_videos():
    """Page showing all available ASL videos categorized"""
    try:
        categories = mux_client.get_available_asl_categories()
        
        # For each category, get videos
        categorized_videos = {}
        for category in categories:
            videos = mux_client.get_asl_videos_for_context(category)
            if videos:
                categorized_videos[category] = videos
        
        # Get ASL video explaining this page
        asl_video = {'video_id': 'asl_video_library'}
        
        return render_template(
            'accessibility/asl_videos.html',
            categories=categorized_videos,
            asl_video=asl_video
        )
    except Exception as e:
        logger.error(f"Error loading ASL videos: {str(e)}")
        return redirect(url_for('index'))

@accessibility_bp.route('/deaf-support-bot')
@login_required
def deaf_support_bot_page():
    """Dedicated page for the deaf support bot"""
    try:
        # Get conversation history
        history = deaf_support_bot.get_conversation_history(current_user.id)
        
        # Get ASL video explaining the bot
        asl_video = {'video_id': 'deaf_support_bot_intro'}
        
        return render_template(
            'accessibility/deaf_support_bot.html',
            history=history,
            asl_video=asl_video
        )
    except Exception as e:
        logger.error(f"Error loading deaf support bot: {str(e)}")
        return redirect(url_for('index'))

@accessibility_bp.route('/api/asl-video/<video_key>')
@login_required
def get_asl_video(video_key):
    """API endpoint to get an ASL video by its key"""
    try:
        video = mux_client.get_asl_video(video_key)
        
        if video:
            return jsonify({
                'success': True,
                'video': video
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
    except Exception as e:
        logger.error(f"Error getting ASL video: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accessibility_bp.route('/api/clear-bot-history', methods=['POST'])
@login_required
def clear_bot_history():
    """API endpoint to clear bot conversation history"""
    try:
        deaf_support_bot.clear_conversation_history(current_user.id)
        
        return jsonify({
            'success': True,
            'message': 'Conversation history cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing bot history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@accessibility_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def accessibility_settings():
    """Page for managing accessibility preferences"""
    try:
        if request.method == 'POST':
            # Save accessibility preferences
            preferences = request.form.to_dict()
            
            # Update or create preference record in database
            from app.models import AccessibilityPreference
            
            preference = AccessibilityPreference.query.filter_by(user_id=current_user.id).first()
            if not preference:
                preference = AccessibilityPreference(user_id=current_user.id)
            
            # Update fields
            preference.asl_video_enabled = 'asl_video_enabled' in preferences
            preference.deaf_support_bot_enabled = 'deaf_support_bot_enabled' in preferences
            preference.visual_alerts_enabled = 'visual_alerts_enabled' in preferences
            preference.preferred_video_speed = float(preferences.get('preferred_video_speed', 1.0))
            preference.color_contrast_preference = preferences.get('color_contrast_preference', 'standard')
            
            db.session.add(preference)
            db.session.commit()
            
            return redirect(url_for('accessibility.accessibility_settings'))
        
        # Get current preferences
        from app.models import AccessibilityPreference
        
        preference = AccessibilityPreference.query.filter_by(user_id=current_user.id).first()
        if not preference:
            # Default preferences
            preference = {
                'asl_video_enabled': True,
                'deaf_support_bot_enabled': True,
                'visual_alerts_enabled': True,
                'preferred_video_speed': 1.0,
                'color_contrast_preference': 'standard'
            }
        
        # Get ASL video explaining settings
        asl_video = {'video_id': 'accessibility_settings'}
        
        return render_template(
            'accessibility/settings.html',
            preferences=preference,
            asl_video=asl_video
        )
    except Exception as e:
        logger.error(f"Error with accessibility settings: {str(e)}")
        return redirect(url_for('index'))

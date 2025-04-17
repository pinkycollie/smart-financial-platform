"""
Routes for ASL support features.
This module handles ASL videos, live ASL support scheduling, and ASL interpreters.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import logging

from models_asl_support import (
    ASLVideoCategory, ASLVideo, ASLFinancialTerm, 
    ASLScheduledSession, ASLSupportProvider, ASLLiveSessionFeedback
)
from simple_app import db

# Initialize blueprint
asl_support_bp = Blueprint('asl_support', __name__, url_prefix='/asl-support')

# Configure logging
logger = logging.getLogger(__name__)

@asl_support_bp.route('/')
def index():
    """ASL support home page"""
    # Get featured videos
    featured_videos = ASLVideo.query.filter_by(is_featured=True, is_published=True).limit(4).all()
    
    # Get video categories
    categories = ASLVideoCategory.query.filter_by(parent_id=None).all()
    
    # Get upcoming sessions if user is logged in
    upcoming_sessions = []
    if current_user.is_authenticated:
        upcoming_sessions = ASLScheduledSession.query.filter_by(
            user_id=current_user.id,
            status='scheduled'
        ).filter(
            ASLScheduledSession.scheduled_date > datetime.utcnow()
        ).order_by(ASLScheduledSession.scheduled_date).limit(3).all()
    
    return render_template(
        'asl_support/index.html',
        title='ASL Support - DEAF FIRST',
        featured_videos=featured_videos,
        categories=categories,
        upcoming_sessions=upcoming_sessions
    )

@asl_support_bp.route('/videos')
def videos():
    """ASL videos library page"""
    # Get query parameters
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Build query
    query = ASLVideo.query.filter_by(is_published=True)
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search_query:
        query = query.filter(
            (ASLVideo.title.ilike(f'%{search_query}%')) |
            (ASLVideo.description.ilike(f'%{search_query}%')) |
            (ASLVideo.keywords.ilike(f'%{search_query}%'))
        )
    
    # Get categories for sidebar
    categories = ASLVideoCategory.query.all()
    
    # Execute query with pagination
    videos = query.order_by(ASLVideo.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return render_template(
        'asl_support/videos.html',
        title='ASL Videos - DEAF FIRST',
        videos=videos,
        categories=categories,
        current_category=category_id,
        search_query=search_query
    )

@asl_support_bp.route('/videos/<int:video_id>')
def view_video(video_id):
    """ASL video detail page"""
    video = ASLVideo.query.get_or_404(video_id)
    
    # Get related videos from same category
    related_videos = ASLVideo.query.filter(
        ASLVideo.category_id == video.category_id,
        ASLVideo.id != video.id,
        ASLVideo.is_published == True
    ).limit(4).all()
    
    # Get financial terms explained in the video
    terms = video.terms.all()
    
    return render_template(
        'asl_support/video_detail.html',
        title=f'{video.title} - ASL Videos',
        video=video,
        related_videos=related_videos,
        terms=terms
    )

@asl_support_bp.route('/terms')
def financial_terms():
    """Financial terms with ASL explanations"""
    # Get query parameters
    search_query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build query
    query = ASLFinancialTerm.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            (ASLFinancialTerm.term.ilike(f'%{search_query}%')) |
            (ASLFinancialTerm.definition.ilike(f'%{search_query}%'))
        )
    
    # Execute query with pagination
    terms = query.order_by(ASLFinancialTerm.term).paginate(page=page, per_page=per_page)
    
    return render_template(
        'asl_support/financial_terms.html',
        title='Financial Terms with ASL - DEAF FIRST',
        terms=terms,
        search_query=search_query
    )

@asl_support_bp.route('/terms/<int:term_id>')
def view_term(term_id):
    """Financial term detail page"""
    term = ASLFinancialTerm.query.get_or_404(term_id)
    
    # Get related terms (implement this based on your needs)
    related_terms = ASLFinancialTerm.query.filter(
        ASLFinancialTerm.id != term.id
    ).order_by(db.func.random()).limit(5).all()
    
    return render_template(
        'asl_support/term_detail.html',
        title=f'{term.term} - Financial Terms',
        term=term,
        related_terms=related_terms
    )

@asl_support_bp.route('/schedule')
@login_required
def schedule():
    """Schedule ASL support sessions page"""
    # Get available ASL support providers
    providers = ASLSupportProvider.query.filter_by(is_active=True).all()
    
    # Get user's upcoming sessions
    upcoming_sessions = ASLScheduledSession.query.filter_by(
        user_id=current_user.id,
        status='scheduled'
    ).filter(
        ASLScheduledSession.scheduled_date > datetime.utcnow()
    ).order_by(ASLScheduledSession.scheduled_date).all()
    
    # Get user's past sessions
    past_sessions = ASLScheduledSession.query.filter_by(
        user_id=current_user.id
    ).filter(
        (ASLScheduledSession.status == 'completed') |
        (ASLScheduledSession.scheduled_date < datetime.utcnow())
    ).order_by(ASLScheduledSession.scheduled_date.desc()).limit(5).all()
    
    # Get available time slots (next 14 days)
    available_slots = []
    today = datetime.utcnow().date()
    
    for day_offset in range(14):
        day = today + timedelta(days=day_offset)
        
        # Skip weekends (implement your business logic here)
        if day.weekday() >= 5:  # Saturday (5) and Sunday (6)
            continue
        
        # Add slots for morning, afternoon, evening (example)
        slots = [
            {
                'date': day,
                'time': '09:00 AM',
                'datetime': datetime.combine(day, datetime.strptime('09:00', '%H:%M').time()),
                'available': True
            },
            {
                'date': day,
                'time': '01:00 PM',
                'datetime': datetime.combine(day, datetime.strptime('13:00', '%H:%M').time()),
                'available': True
            },
            {
                'date': day,
                'time': '05:00 PM',
                'datetime': datetime.combine(day, datetime.strptime('17:00', '%H:%M').time()),
                'available': True
            }
        ]
        
        # Filter out slots in the past
        slots = [slot for slot in slots if slot['datetime'] > datetime.utcnow()]
        
        # Add to available slots
        if slots:
            available_slots.append({
                'date': day,
                'slots': slots
            })
    
    return render_template(
        'asl_support/schedule.html',
        title='Schedule ASL Support - DEAF FIRST',
        providers=providers,
        upcoming_sessions=upcoming_sessions,
        past_sessions=past_sessions,
        available_slots=available_slots
    )

@asl_support_bp.route('/schedule/create', methods=['POST'])
@login_required
def create_session():
    """Create a new ASL support session"""
    try:
        # Get form data
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        session_type = request.form.get('session_type')
        topic = request.form.get('topic')
        notes = request.form.get('notes')
        provider_id = request.form.get('provider_id')
        
        # Validate form data
        if not all([date_str, time_str, session_type]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('asl_support.schedule'))
        
        # Parse date and time
        scheduled_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        
        # Create new session
        session = ASLScheduledSession(
            user_id=current_user.id,
            session_type=session_type,
            topic=topic,
            notes=notes,
            scheduled_date=scheduled_datetime,
            provider='asl_now',  # Default provider
            status='scheduled'
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Generate video meeting link (placeholder)
        session.meeting_id = f"asl-meeting-{session.id}"
        session.join_url = f"https://meetings.example.com/{session.meeting_id}"
        
        db.session.commit()
        
        flash('Your ASL support session has been scheduled.', 'success')
        return redirect(url_for('asl_support.schedule'))
    
    except Exception as e:
        logger.error(f"Error creating ASL session: {e}")
        flash('An error occurred while scheduling your session. Please try again.', 'danger')
        return redirect(url_for('asl_support.schedule'))

@asl_support_bp.route('/schedule/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id):
    """Cancel a scheduled ASL support session"""
    session = ASLScheduledSession.query.get_or_404(session_id)
    
    # Check if user owns the session
    if session.user_id != current_user.id:
        flash('You do not have permission to cancel this session.', 'danger')
        return redirect(url_for('asl_support.schedule'))
    
    # Check if session can be cancelled
    if session.status != 'scheduled':
        flash('This session cannot be cancelled.', 'danger')
        return redirect(url_for('asl_support.schedule'))
    
    # Update session status
    session.status = 'cancelled'
    db.session.commit()
    
    flash('Your ASL support session has been cancelled.', 'success')
    return redirect(url_for('asl_support.schedule'))

@asl_support_bp.route('/schedule/<int:session_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(session_id):
    """Submit feedback for an ASL support session"""
    session = ASLScheduledSession.query.get_or_404(session_id)
    
    # Check if user owns the session
    if session.user_id != current_user.id:
        flash('You do not have permission to submit feedback for this session.', 'danger')
        return redirect(url_for('asl_support.schedule'))
    
    try:
        # Get form data
        rating = request.form.get('rating', type=int)
        communication = request.form.get('communication_quality', type=int)
        helpfulness = request.form.get('helpfulness', type=int)
        technical = request.form.get('technical_quality', type=int)
        comments = request.form.get('comments')
        
        # Validate rating
        if not rating or not 1 <= rating <= 5:
            flash('Please provide a valid rating (1-5).', 'danger')
            return redirect(url_for('asl_support.schedule'))
        
        # Create feedback
        feedback = ASLLiveSessionFeedback(
            session_id=session_id,
            user_id=current_user.id,
            rating=rating,
            communication_quality=communication,
            helpfulness=helpfulness,
            technical_quality=technical,
            comments=comments
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('asl_support.schedule'))
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        flash('An error occurred while submitting your feedback. Please try again.', 'danger')
        return redirect(url_for('asl_support.schedule'))

@asl_support_bp.route('/api/videos/<int:video_id>', methods=['GET'])
def api_video(video_id):
    """API endpoint for video information"""
    video = ASLVideo.query.get_or_404(video_id)
    
    # Use video service switcher to get the playback URL
    try:
        from services.deaf_first.video_service_switcher import video_service
        
        # Get white label ID if applicable
        white_label_id = None
        if hasattr(current_user, 'licensee_id') and current_user.licensee_id:
            white_label_id = current_user.licensee_id
        
        # Get playback URL with white label if needed
        playback_url = video_service.get_white_label_video_url(
            video.video_id, 
            white_label_id=white_label_id, 
            provider_type=video.provider
        )
    except (ImportError, Exception) as e:
        logger.error(f"Error using video service: {e}")
        # Fallback direct URL (just for demo)
        playback_url = f"https://example.com/videos/{video.video_id}"
    
    return jsonify({
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'provider': video.provider,
        'video_id': video.video_id,
        'playback_url': playback_url,
        'thumbnail_url': video.thumbnail_url,
        'duration': video.duration
    })
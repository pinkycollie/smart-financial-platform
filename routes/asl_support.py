"""
ASL Support routes for the DEAF FIRST platform.
Provides video-based technical support with ASL interpreters.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, g, session, current_app
from flask_login import login_required, current_user
from simple_app import db
from models_asl_support import ASLSupportSession, ASLSupportResource, ASLSupportFAQ
from services.deaf_first.asl_support import asl_support_service
from datetime import datetime, timedelta

# Create blueprint
asl_support_bp = Blueprint('asl_support', __name__, url_prefix='/asl-support')

@asl_support_bp.route('/')
@login_required
def index():
    """ASL Support home page"""
    # Get support categories
    categories = asl_support_service.get_support_categories()
    
    # Get user's upcoming sessions
    upcoming_sessions = ASLSupportSession.query.filter_by(
        user_id=current_user.id, 
        status='scheduled'
    ).filter(
        ASLSupportSession.scheduled_time >= datetime.utcnow()
    ).order_by(
        ASLSupportSession.scheduled_time
    ).limit(3).all()
    
    # Get FAQ highlights
    faqs = asl_support_service.get_faq()[:5]  # Top 5 FAQs
    
    return render_template(
        'asl_support/index.html',
        categories=categories,
        upcoming_sessions=upcoming_sessions,
        faqs=faqs,
        page_title="ASL Technical Support"
    )

@asl_support_bp.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    """Schedule an ASL support session"""
    if request.method == 'POST':
        # Get form data
        category = request.form.get('category')
        notes = request.form.get('notes')
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        provider = request.form.get('provider')
        
        try:
            # Parse date and time
            scheduled_datetime = datetime.strptime(
                f"{scheduled_date} {scheduled_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # Create support session
            session_data = asl_support_service.create_support_session(
                user_id=current_user.id,
                category=category,
                notes=notes,
                scheduled_time=scheduled_datetime,
                provider=provider
            )
            
            flash(f"Your ASL support session has been scheduled for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}", "success")
            return redirect(url_for('asl_support.session_confirmation', session_id=session_data['session_id']))
            
        except ValueError as e:
            flash(str(e), "danger")
    
    # Get support categories
    categories = asl_support_service.get_support_categories()
    
    # Get video providers
    providers = asl_support_service.get_video_providers()
    
    # Default date/time (15 min from now, rounded to nearest 15 min)
    now = datetime.utcnow()
    minutes = (now.minute // 15 + 1) * 15
    default_time = (now + timedelta(minutes=minutes - now.minute)).replace(second=0, microsecond=0)
    
    return render_template(
        'asl_support/schedule.html',
        categories=categories,
        providers=providers,
        default_date=default_time.strftime('%Y-%m-%d'),
        default_time=default_time.strftime('%H:%M'),
        page_title="Schedule ASL Support"
    )

@asl_support_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    """View a support session"""
    session = ASLSupportSession.query.get_or_404(session_id)
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to view this session.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Get category info
    category_info = asl_support_service.get_support_categories().get(session.category, {})
    
    return render_template(
        'asl_support/session_detail.html',
        session=session,
        category_info=category_info,
        page_title="Support Session Details"
    )

@asl_support_bp.route('/session/<int:session_id>/confirmation')
@login_required
def session_confirmation(session_id):
    """Confirmation page after scheduling a session"""
    session = ASLSupportSession.query.get_or_404(session_id)
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to view this session.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Get category info
    category_info = asl_support_service.get_support_categories().get(session.category, {})
    
    return render_template(
        'asl_support/session_confirmation.html',
        session=session,
        category_info=category_info,
        page_title="Session Scheduled"
    )

@asl_support_bp.route('/session/<int:session_id>/join')
@login_required
def join_session(session_id):
    """Join a support session"""
    session = ASLSupportSession.query.get_or_404(session_id)
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to join this session.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Check if session is scheduled and time is valid
    now = datetime.utcnow()
    session_time = session.scheduled_time
    
    # Only allow joining 5 minutes before scheduled time
    if session.status != 'scheduled' or session_time - timedelta(minutes=5) > now:
        flash(f"This session is scheduled for {session_time.strftime('%B %d, %Y at %I:%M %p')}. You can join 5 minutes before the scheduled time.", "warning")
        return redirect(url_for('asl_support.session_detail', session_id=session_id))
    
    # Update session status to in_progress
    if session.status == 'scheduled':
        session.status = 'in_progress'
        db.session.commit()
    
    # Generate meeting URL
    if session.provider == 'demo':
        return redirect(url_for('asl_support.demo_meeting', meeting_id=session.meeting_id))
    else:
        # Get provider info
        provider = asl_support_service.meeting_providers.get(session.provider, {})
        if provider and 'url_template' in provider:
            meeting_url = provider['url_template'].format(meeting_id=session.meeting_id)
            return redirect(meeting_url)
    
    flash("Unable to join session. Please contact support.", "danger")
    return redirect(url_for('asl_support.session_detail', session_id=session_id))

@asl_support_bp.route('/session/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id):
    """Cancel a support session"""
    session = ASLSupportSession.query.get_or_404(session_id)
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to cancel this session.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Check if session can be cancelled (not in progress or completed)
    if session.status in ['in_progress', 'completed']:
        flash("Cannot cancel a session that is in progress or completed.", "danger")
        return redirect(url_for('asl_support.session_detail', session_id=session_id))
    
    # Update session status
    session.status = 'cancelled'
    db.session.commit()
    
    flash("Your session has been cancelled.", "success")
    return redirect(url_for('asl_support.index'))

@asl_support_bp.route('/session/<int:session_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(session_id):
    """Submit feedback for a support session"""
    session = ASLSupportSession.query.get_or_404(session_id)
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to submit feedback for this session.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Check if session is completed
    if session.status != 'completed':
        flash("Can only submit feedback for completed sessions.", "danger")
        return redirect(url_for('asl_support.session_detail', session_id=session_id))
    
    # Get form data
    rating = request.form.get('rating')
    feedback = request.form.get('feedback')
    
    # Update session with feedback
    if rating:
        session.rating = int(rating)
    session.feedback = feedback
    db.session.commit()
    
    flash("Thank you for your feedback!", "success")
    return redirect(url_for('asl_support.session_detail', session_id=session_id))

@asl_support_bp.route('/resources')
def resources():
    """Browse support resources"""
    # Get category from query param
    category = request.args.get('category')
    
    # Get white-label ID if applicable
    white_label_id = None
    if hasattr(g, 'licensee') and g.licensee:
        white_label_id = g.licensee.id
    
    # Get resources
    resources = asl_support_service.get_support_resources(category, white_label_id)
    
    # Get all categories
    categories = asl_support_service.get_support_categories()
    
    return render_template(
        'asl_support/resources.html',
        resources=resources,
        categories=categories,
        selected_category=category,
        page_title="ASL Support Resources"
    )

@asl_support_bp.route('/faq')
def faq():
    """Frequently asked questions"""
    # Get category from query param
    category = request.args.get('category')
    
    # Get white-label ID if applicable
    white_label_id = None
    if hasattr(g, 'licensee') and g.licensee:
        white_label_id = g.licensee.id
    
    # Get FAQs
    faqs = asl_support_service.get_faq(category, white_label_id)
    
    # Get all categories
    categories = asl_support_service.get_support_categories()
    
    return render_template(
        'asl_support/faq.html',
        faqs=faqs,
        categories=categories,
        selected_category=category,
        page_title="ASL Support FAQ"
    )

@asl_support_bp.route('/demo-meeting/<meeting_id>')
@login_required
def demo_meeting(meeting_id):
    """Demo meeting page for testing"""
    # Find session by meeting ID
    session = ASLSupportSession.query.filter_by(meeting_id=meeting_id).first_or_404()
    
    # Check if user owns this session
    if session.user_id != current_user.id:
        flash("You do not have permission to join this meeting.", "danger")
        return redirect(url_for('asl_support.index'))
    
    # Get category info
    category_info = asl_support_service.get_support_categories().get(session.category, {})
    
    return render_template(
        'asl_support/demo_meeting.html',
        session=session,
        category_info=category_info,
        meeting_id=meeting_id,
        page_title="ASL Support Meeting"
    )

@asl_support_bp.route('/api/sessions')
@login_required
def api_sessions():
    """API: Get user's support sessions"""
    # Get user's sessions
    sessions = ASLSupportSession.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ASLSupportSession.scheduled_time.desc()
    ).all()
    
    # Format response
    response = []
    categories = asl_support_service.get_support_categories()
    
    for session in sessions:
        category_info = categories.get(session.category, {})
        response.append({
            'id': session.id,
            'category': session.category,
            'category_name': category_info.get('name', 'Unknown'),
            'scheduled_time': session.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            'status': session.status,
            'provider': session.provider,
            'meeting_id': session.meeting_id
        })
    
    return jsonify(response)

# White-label integration
@asl_support_bp.context_processor
def inject_white_label():
    """Inject white-label context for templates"""
    context = {}
    
    # Check if white-label is active
    if hasattr(g, 'licensee') and g.licensee and g.licensee.white_label_enabled and g.licensee.branding:
        context['white_label'] = {
            'company_name': g.licensee.company_name,
            'logo_url': g.licensee.branding.logo_path,
            'primary_color': g.licensee.branding.primary_color,
            'secondary_color': g.licensee.branding.secondary_color
        }
    
    return context
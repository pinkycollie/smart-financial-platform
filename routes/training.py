"""
Routes for personnel training in the DEAF FIRST platform.
Handles training modules, courses, progress tracking, and certifications.
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, jsonify
from flask_login import login_required, current_user
from simple_app import db
from models_education import TrainingType, TrainingModule, TrainingCourse, UserTrainingProgress, TrainingCertification
from datetime import datetime

# Create blueprint
training_bp = Blueprint('training', __name__, url_prefix='/training')

@training_bp.route('/')
def index():
    """Training home page"""
    
    # Get training types
    training_types = [
        {
            'id': t.value,
            'name': t.name.replace('_', ' ').title(),
            'description': get_training_type_description(t),
            'icon': get_training_type_icon(t)
        }
        for t in TrainingType
    ]
    
    # Get featured modules
    featured_modules = TrainingModule.query.filter_by(
        is_published=True
    ).order_by(
        TrainingModule.created_at.desc()
    ).limit(4).all()
    
    # Get user progress if logged in
    user_progress = []
    user_certifications = []
    
    if current_user.is_authenticated:
        # Get user's recent progress
        user_progress = UserTrainingProgress.query.filter_by(
            user_id=current_user.id
        ).filter(
            UserTrainingProgress.status != 'completed'
        ).order_by(
            UserTrainingProgress.last_activity_at.desc()
        ).limit(3).all()
        
        # Add status color
        for progress in user_progress:
            progress.status_color = get_status_color(progress.status)
        
        # Get user's certifications
        user_certifications = TrainingCertification.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(
            TrainingCertification.issued_at.desc()
        ).all()
    
    return render_template(
        'training/index.html',
        training_types=training_types,
        featured_modules=featured_modules,
        user_progress=user_progress,
        user_certifications=user_certifications,
        now=datetime.utcnow()
    )

@training_bp.route('/modules')
def modules():
    """Browse training modules"""
    
    # Get filter parameters
    training_type = request.args.get('type')
    level = request.args.get('level')
    
    # Query modules
    query = TrainingModule.query.filter_by(is_published=True)
    
    if training_type:
        query = query.filter_by(type=training_type)
    
    if level:
        query = query.filter_by(level=int(level))
    
    # Get modules
    modules = query.order_by(TrainingModule.level, TrainingModule.title).all()
    
    # Get training types
    training_types = [
        {
            'id': t.value,
            'name': t.name.replace('_', ' ').title(),
            'selected': t.value == training_type
        }
        for t in TrainingType
    ]
    
    # Get levels
    levels = [
        {'id': 1, 'name': 'Beginner', 'selected': level == '1'},
        {'id': 2, 'name': 'Intermediate', 'selected': level == '2'},
        {'id': 3, 'name': 'Advanced', 'selected': level == '3'}
    ]
    
    return render_template(
        'training/modules.html',
        modules=modules,
        training_types=training_types,
        levels=levels,
        selected_type=training_type,
        selected_level=level
    )

@training_bp.route('/module/<int:module_id>')
def module_detail(module_id):
    """View details of a training module"""
    
    # Get module
    module = TrainingModule.query.get_or_404(module_id)
    
    # Check if module is published
    if not module.is_published and not (current_user.is_authenticated and current_user.is_admin):
        flash("This module is not currently available.", "warning")
        return redirect(url_for('training.modules'))
    
    # Get user progress if logged in
    progress = None
    if current_user.is_authenticated:
        progress = UserTrainingProgress.query.filter_by(
            user_id=current_user.id,
            module_id=module_id
        ).first()
        
        if progress:
            progress.status_color = get_status_color(progress.status)
    
    # Get prerequisites
    prerequisites = []
    if module.prerequisites:
        prereq_ids = module.prerequisites
        prereq_modules = TrainingModule.query.filter(TrainingModule.id.in_(prereq_ids)).all()
        
        for prereq in prereq_modules:
            # Check if user has completed this prerequisite
            completed = False
            if current_user.is_authenticated:
                prereq_progress = UserTrainingProgress.query.filter_by(
                    user_id=current_user.id,
                    module_id=prereq.id,
                    status='completed'
                ).first()
                completed = prereq_progress is not None
            
            prerequisites.append({
                'id': prereq.id,
                'title': prereq.title,
                'description': prereq.description,
                'completed': completed
            })
    
    # Get related modules
    related_modules = TrainingModule.query.filter_by(
        type=module.type,
        is_published=True
    ).filter(
        TrainingModule.id != module_id
    ).order_by(
        TrainingModule.level
    ).limit(3).all()
    
    return render_template(
        'training/module_detail.html',
        module=module,
        progress=progress,
        prerequisites=prerequisites,
        related_modules=related_modules
    )

@training_bp.route('/module/<int:module_id>/start')
@login_required
def start_module(module_id):
    """Start a training module"""
    
    # Get module
    module = TrainingModule.query.get_or_404(module_id)
    
    # Check if module is published
    if not module.is_published and not current_user.is_admin:
        flash("This module is not currently available.", "warning")
        return redirect(url_for('training.modules'))
    
    # Check prerequisites
    if module.prerequisites:
        prereq_ids = module.prerequisites
        
        for prereq_id in prereq_ids:
            prereq_completed = UserTrainingProgress.query.filter_by(
                user_id=current_user.id,
                module_id=prereq_id,
                status='completed'
            ).first()
            
            if not prereq_completed:
                prereq = TrainingModule.query.get(prereq_id)
                
                if prereq:
                    flash(f"You need to complete '{prereq.title}' before starting this module.", "warning")
                    return redirect(url_for('training.module_detail', module_id=module_id))
    
    # Check if already started
    existing_progress = UserTrainingProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    if existing_progress:
        # Update existing progress
        existing_progress.status = 'in_progress'
        existing_progress.last_activity_at = datetime.utcnow()
        db.session.commit()
        
        # Redirect to continue
        return redirect(url_for('training.continue_module', module_id=module_id))
    
    # Create new progress
    progress = UserTrainingProgress(
        user_id=current_user.id,
        module_id=module_id,
        status='in_progress',
        progress_percent=0,
        current_position={'unit_index': 0, 'lesson_index': 0},
        last_activity_at=datetime.utcnow()
    )
    
    db.session.add(progress)
    db.session.commit()
    
    flash(f"You've started the '{module.title}' module!", "success")
    
    # Redirect to module content
    return redirect(url_for('training.continue_module', module_id=module_id))

@training_bp.route('/module/<int:module_id>/continue')
@login_required
def continue_module(module_id):
    """Continue a training module"""
    
    # Get module
    module = TrainingModule.query.get_or_404(module_id)
    
    # Get user progress
    progress = UserTrainingProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    if not progress:
        # Redirect to start
        return redirect(url_for('training.start_module', module_id=module_id))
    
    # Update activity timestamp
    progress.last_activity_at = datetime.utcnow()
    db.session.commit()
    
    # Get current position
    current_position = progress.current_position or {'unit_index': 0, 'lesson_index': 0}
    
    # Get units for this module ordered by sort_order
    units = module.units
    
    # Check if there are units
    if not units:
        flash("This module doesn't have any content yet.", "warning")
        return redirect(url_for('training.module_detail', module_id=module_id))
    
    # Get current unit
    unit_index = current_position.get('unit_index', 0)
    if unit_index >= len(units):
        unit_index = len(units) - 1
    
    current_unit = units[unit_index]
    
    # Get lessons for current unit ordered by sort_order
    lessons = current_unit.lessons
    
    # Check if there are lessons
    if not lessons:
        flash("This unit doesn't have any lessons yet.", "warning")
        return redirect(url_for('training.module_detail', module_id=module_id))
    
    # Get current lesson
    lesson_index = current_position.get('lesson_index', 0)
    if lesson_index >= len(lessons):
        lesson_index = len(lessons) - 1
    
    current_lesson = lessons[lesson_index]
    
    return render_template(
        'training/module_content.html',
        module=module,
        progress=progress,
        units=units,
        current_unit=current_unit,
        current_lesson=current_lesson,
        unit_index=unit_index,
        lesson_index=lesson_index,
        total_units=len(units),
        total_lessons=len(lessons)
    )

@training_bp.route('/courses')
def courses():
    """Browse training courses"""
    
    # Get filter parameters
    training_type = request.args.get('type')
    level = request.args.get('level')
    
    # Query courses
    query = TrainingCourse.query.filter_by(is_published=True)
    
    if training_type:
        query = query.filter_by(type=training_type)
    
    if level:
        query = query.filter_by(level=int(level))
    
    # Get courses
    courses = query.order_by(TrainingCourse.level, TrainingCourse.title).all()
    
    # Get training types
    training_types = [
        {
            'id': t.value,
            'name': t.name.replace('_', ' ').title(),
            'selected': t.value == training_type
        }
        for t in TrainingType
    ]
    
    # Get levels
    levels = [
        {'id': 1, 'name': 'Beginner', 'selected': level == '1'},
        {'id': 2, 'name': 'Intermediate', 'selected': level == '2'},
        {'id': 3, 'name': 'Advanced', 'selected': level == '3'}
    ]
    
    return render_template(
        'training/courses.html',
        courses=courses,
        training_types=training_types,
        levels=levels,
        selected_type=training_type,
        selected_level=level
    )

@training_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    """View details of a training course"""
    
    # Get course
    course = TrainingCourse.query.get_or_404(course_id)
    
    # Check if course is published
    if not course.is_published and not (current_user.is_authenticated and current_user.is_admin):
        flash("This course is not currently available.", "warning")
        return redirect(url_for('training.courses'))
    
    # Get user progress if logged in
    progress = None
    if current_user.is_authenticated:
        progress = UserTrainingProgress.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if progress:
            progress.status_color = get_status_color(progress.status)
    
    # Get modules in this course
    course_modules = []
    if course.modules:
        module_ids = course.modules
        modules = TrainingModule.query.filter(TrainingModule.id.in_(module_ids)).all()
        
        # Sort modules according to the order in course.modules
        course_modules = sorted(modules, key=lambda m: module_ids.index(m.id))
        
        # Add completion status for each module
        if current_user.is_authenticated:
            for module in course_modules:
                module_progress = UserTrainingProgress.query.filter_by(
                    user_id=current_user.id,
                    module_id=module.id
                ).first()
                
                if module_progress:
                    module.progress = module_progress
                    module.completed = module_progress.status == 'completed'
                else:
                    module.progress = None
                    module.completed = False
    
    return render_template(
        'training/course_detail.html',
        course=course,
        progress=progress,
        course_modules=course_modules
    )

@training_bp.route('/api/progress/update', methods=['POST'])
@login_required
def update_progress():
    """API: Update lesson progress"""
    
    # Get request data
    data = request.json
    module_id = data.get('module_id')
    unit_index = data.get('unit_index')
    lesson_index = data.get('lesson_index')
    progress_percent = data.get('progress_percent')
    
    # Validate data
    if not module_id or unit_index is None or lesson_index is None:
        return jsonify({'success': False, 'error': 'Missing required data'})
    
    # Get progress
    progress = UserTrainingProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    if not progress:
        return jsonify({'success': False, 'error': 'Progress not found'})
    
    # Update progress
    progress.current_position = {'unit_index': unit_index, 'lesson_index': lesson_index}
    
    if progress_percent is not None:
        progress.progress_percent = progress_percent
    
    progress.last_activity_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

# Helper functions
def get_training_type_description(training_type):
    """Get description for a training type"""
    descriptions = {
        TrainingType.ONBOARDING: "Get started with the DEAF FIRST platform and its features",
        TrainingType.PLATFORM_USAGE: "Learn how to use the platform effectively",
        TrainingType.ASL_BASICS: "Learn the basics of American Sign Language",
        TrainingType.FINANCIAL_CONCEPTS: "Understand core financial concepts and terminology",
        TrainingType.CUSTOMER_SERVICE: "Provide excellent service to deaf customers",
        TrainingType.COMPLIANCE: "Stay compliant with regulations and best practices",
        TrainingType.ADVANCED: "Advanced training for experienced users"
    }
    return descriptions.get(training_type, "")

def get_training_type_icon(training_type):
    """Get icon for a training type"""
    icons = {
        TrainingType.ONBOARDING: "info-circle",
        TrainingType.PLATFORM_USAGE: "display",
        TrainingType.ASL_BASICS: "hand-index",
        TrainingType.FINANCIAL_CONCEPTS: "cash-coin",
        TrainingType.CUSTOMER_SERVICE: "headset",
        TrainingType.COMPLIANCE: "shield-check",
        TrainingType.ADVANCED: "star"
    }
    return icons.get(training_type, "journal-text")

def get_status_color(status):
    """Get color for a status"""
    colors = {
        'not_started': 'secondary',
        'in_progress': 'primary',
        'completed': 'success',
        'certified': 'info',
        'expired': 'warning'
    }
    return colors.get(status, 'secondary')
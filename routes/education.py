from flask import Blueprint, render_template, abort, request, flash, redirect, url_for, jsonify
from models_education import (
    EducationCategory, EducationModule, EducationLesson, 
    EducationQuiz, QuizQuestion, QuizAnswer, QuizAttempt,
    QuizResponse, ModuleCompletion, UserProgress
)
from simple_app import db
from services.deaf_first.mux_client import mux_client
from services.deaf_first.signasl_integration import SignASLClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
education_bp = Blueprint('education', __name__, url_prefix='/education')

# Initialize SignASL client
signasl_client = SignASLClient()

# Routes for education modules
@education_bp.route('/')
def index():
    """Show all education categories and featured modules"""
    categories = EducationCategory.query.order_by(EducationCategory.display_order).all()
    featured_modules = EducationModule.query.filter_by(published=True).order_by(EducationModule.created_at.desc()).limit(4).all()
    
    return render_template(
        'education/index.html',
        categories=categories,
        featured_modules=featured_modules,
        title="Financial Education - DEAF FIRST"
    )

@education_bp.route('/category/<int:category_id>')
def category_detail(category_id):
    """Show all modules in a category"""
    category = EducationCategory.query.get_or_404(category_id)
    modules = EducationModule.query.filter_by(
        category_id=category_id, 
        published=True
    ).order_by(EducationModule.created_at.desc()).all()
    
    return render_template(
        'education/category.html',
        category=category,
        modules=modules,
        title=f"{category.name} - Financial Education"
    )

@education_bp.route('/module/<string:slug>')
def module_detail(slug):
    """Show module details and lessons"""
    module = EducationModule.query.filter_by(slug=slug).first_or_404()
    lessons = EducationLesson.query.filter_by(module_id=module.id).order_by(EducationLesson.order).all()
    
    # Get ASL video URL if available
    asl_video_url = None
    if module.has_asl and module.asl_video_id:
        try:
            asl_video_url = mux_client.get_playback_url(module.asl_video_id)
        except Exception as e:
            logger.error(f"Error getting ASL video URL for module {module.id}: {e}")
    
    # Get financial terms for glossary
    financial_terms = []
    try:
        difficulty = "advanced" if module.difficulty_level == "advanced" else "basic"
        financial_terms = signasl_client.get_finance_terms(category=difficulty, limit=10)
    except Exception as e:
        logger.error(f"Error getting financial terms: {e}")
    
    return render_template(
        'education/module.html',
        module=module,
        lessons=lessons,
        asl_video_url=asl_video_url,
        financial_terms=financial_terms,
        title=f"{module.title} - Financial Education"
    )

@education_bp.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    """Show lesson content with ASL video"""
    lesson = EducationLesson.query.get_or_404(lesson_id)
    module = lesson.module
    
    # Get next and previous lessons
    next_lesson = EducationLesson.query.filter(
        EducationLesson.module_id == module.id,
        EducationLesson.order > lesson.order
    ).order_by(EducationLesson.order).first()
    
    prev_lesson = EducationLesson.query.filter(
        EducationLesson.module_id == module.id,
        EducationLesson.order < lesson.order
    ).order_by(EducationLesson.order.desc()).first()
    
    # Get lesson resources
    resources = lesson.resources.all()
    
    # Get ASL video URL if available
    asl_video_url = None
    if lesson.asl_video_id:
        try:
            asl_video_url = mux_client.get_playback_url(lesson.asl_video_id)
        except Exception as e:
            logger.error(f"Error getting ASL video URL for lesson {lesson.id}: {e}")
    
    # Get module quiz if this is the last lesson
    quiz = None
    if not next_lesson:
        quiz = module.quiz
    
    return render_template(
        'education/lesson.html',
        lesson=lesson,
        module=module,
        next_lesson=next_lesson,
        prev_lesson=prev_lesson,
        resources=resources,
        asl_video_url=asl_video_url,
        quiz=quiz,
        title=f"{lesson.title} - {module.title}"
    )

@education_bp.route('/search')
def search():
    """Search education content"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('education.index'))
    
    # Search modules and lessons
    modules = EducationModule.query.filter(
        EducationModule.published == True,
        EducationModule.title.ilike(f'%{query}%') | 
        EducationModule.summary.ilike(f'%{query}%')
    ).all()
    
    lessons = EducationLesson.query.join(EducationModule).filter(
        EducationModule.published == True,
        EducationLesson.title.ilike(f'%{query}%') | 
        EducationLesson.content.ilike(f'%{query}%')
    ).all()
    
    # If query looks like a financial term, search ASL videos
    asl_videos = []
    if len(query.split()) <= 3:
        try:
            asl_videos = signasl_client.search_asl_videos(query, limit=5)
        except Exception as e:
            logger.error(f"Error searching ASL videos: {e}")
    
    return render_template(
        'education/search_results.html',
        query=query,
        modules=modules,
        lessons=lessons,
        asl_videos=asl_videos,
        title=f"Search: {query} - Financial Education"
    )

@education_bp.route('/glossary')
def glossary():
    """Financial terms glossary with ASL videos"""
    category = request.args.get('category', 'basic')
    
    # Valid categories
    valid_categories = ['basic', 'advanced', 'insurance', 'retirement']
    if category not in valid_categories:
        category = 'basic'
    
    # Get financial terms for the selected category
    financial_terms = []
    try:
        financial_terms = signasl_client.get_finance_terms(category=category, limit=30)
    except Exception as e:
        logger.error(f"Error getting financial terms: {e}")
    
    return render_template(
        'education/glossary.html',
        financial_terms=financial_terms,
        category=category,
        categories=valid_categories,
        title="Financial Terms Glossary - DEAF FIRST"
    )

@education_bp.route('/term/<string:term_id>')
def term_detail(term_id):
    """Show detail for a financial term with ASL video"""
    term_info = None
    try:
        term_info = signasl_client.get_asl_video(term_id)
    except Exception as e:
        logger.error(f"Error getting term details: {e}")
        abort(404)
    
    if not term_info:
        abort(404)
    
    return render_template(
        'education/term.html',
        term=term_info,
        title=f"{term_info.get('term', 'Financial Term')} - ASL Glossary"
    )

# API endpoints for interactive elements
@education_bp.route('/api/quiz/<int:quiz_id>')
def get_quiz(quiz_id):
    """Get quiz data for interactive quiz component"""
    quiz = EducationQuiz.query.get_or_404(quiz_id)
    
    # Format quiz data for the frontend
    questions = []
    for question in quiz.questions.order_by(QuizQuestion.order):
        q_data = {
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type,
            'points': question.points,
            'asl_video_id': question.asl_video_id,
            'answers': []
        }
        
        # Add answers (without revealing which is correct)
        for answer in question.answers:
            q_data['answers'].append({
                'id': answer.id,
                'text': answer.answer_text
            })
        
        questions.append(q_data)
    
    quiz_data = {
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'passing_score': quiz.passing_score,
        'asl_instructions_id': quiz.asl_instructions_id,
        'questions': questions
    }
    
    return jsonify(quiz_data)

@education_bp.route('/api/financial-calculator')
def financial_calculator_data():
    """API endpoint for financial calculator interactive element"""
    calculator_type = request.args.get('type', 'compound_interest')
    
    # Sample data for compound interest calculator
    if calculator_type == 'compound_interest':
        data = {
            'title': 'Compound Interest Calculator',
            'description': 'See how your savings grow over time with compound interest',
            'fields': [
                {'name': 'principal', 'label': 'Initial Investment', 'type': 'number', 'default': 1000},
                {'name': 'rate', 'label': 'Annual Interest Rate (%)', 'type': 'number', 'default': 5},
                {'name': 'years', 'label': 'Number of Years', 'type': 'number', 'default': 10},
                {'name': 'compound', 'label': 'Compound Frequency', 'type': 'select', 
                 'options': [
                     {'value': 1, 'label': 'Annually'}, 
                     {'value': 4, 'label': 'Quarterly'}, 
                     {'value': 12, 'label': 'Monthly'}, 
                     {'value': 365, 'label': 'Daily'}
                 ], 
                 'default': 12}
            ],
            'asl_video_id': 'demo-compound-interest-calculator'
        }
    # Sample data for mortgage calculator
    elif calculator_type == 'mortgage':
        data = {
            'title': 'Mortgage Payment Calculator',
            'description': 'Calculate your monthly mortgage payment',
            'fields': [
                {'name': 'home_price', 'label': 'Home Price', 'type': 'number', 'default': 300000},
                {'name': 'down_payment', 'label': 'Down Payment', 'type': 'number', 'default': 60000},
                {'name': 'interest_rate', 'label': 'Interest Rate (%)', 'type': 'number', 'default': 4.5},
                {'name': 'loan_term', 'label': 'Loan Term (years)', 'type': 'select', 
                 'options': [
                     {'value': 15, 'label': '15 years'}, 
                     {'value': 20, 'label': '20 years'}, 
                     {'value': 30, 'label': '30 years'}
                 ], 
                 'default': 30}
            ],
            'asl_video_id': 'demo-mortgage-calculator'
        }
    else:
        return jsonify({'error': 'Invalid calculator type'}), 400
    
    return jsonify(data)
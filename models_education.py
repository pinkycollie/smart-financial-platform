from datetime import datetime
from simple_app import db

class EducationCategory(db.Model):
    """Categories for financial education content"""
    __tablename__ = 'education_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('EducationModule', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationCategory {self.name}>"


class EducationModule(db.Model):
    """Financial education module with sign language support"""
    __tablename__ = 'education_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('education_categories.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    summary = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_time = db.Column(db.Integer)  # in minutes
    has_asl = db.Column(db.Boolean, default=True)
    asl_video_id = db.Column(db.String(100))
    captions_available = db.Column(db.Boolean, default=True)
    published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('EducationLesson', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    quiz = db.relationship('EducationQuiz', backref='module', uselist=False, cascade='all, delete-orphan')
    completions = db.relationship('ModuleCompletion', backref='module', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationModule {self.title}>"


class EducationLesson(db.Model):
    """Individual lesson within a financial education module"""
    __tablename__ = 'education_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=1)
    asl_video_id = db.Column(db.String(100))
    captions_available = db.Column(db.Boolean, default=True)
    interactive_elements = db.Column(db.JSON)  # Store JSON with interactive elements configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    resources = db.relationship('LessonResource', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationLesson {self.title}>"


class LessonResource(db.Model):
    """Additional resources for a lesson"""
    __tablename__ = 'lesson_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('education_lessons.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(20))  # document, video, link
    url = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    asl_explanation_id = db.Column(db.String(100))  # Video ID for ASL explanation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LessonResource {self.title} - {self.resource_type}>"


class EducationQuiz(db.Model):
    """Quiz associated with a financial education module"""
    __tablename__ = 'education_quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    passing_score = db.Column(db.Integer, default=70)  # Percentage needed to pass
    asl_instructions_id = db.Column(db.String(100))  # Video ID for ASL instructions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationQuiz {self.title}>"


class QuizQuestion(db.Model):
    """Question for a financial education quiz"""
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('education_quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, open_ended
    points = db.Column(db.Integer, default=1)
    asl_video_id = db.Column(db.String(100))
    order = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('QuizAnswer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<QuizQuestion {self.id}>"


class QuizAnswer(db.Model):
    """Possible answer for a quiz question"""
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)
    asl_explanation_id = db.Column(db.String(100))  # Video ID for ASL explanation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<QuizAnswer {self.id}>"


class QuizAttempt(db.Model):
    """Record of a user's attempt at a quiz"""
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('education_quizzes.id'), nullable=False)
    score = db.Column(db.Integer)  # Percentage score
    passed = db.Column(db.Boolean)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    responses = db.relationship('QuizResponse', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    user = db.relationship('User', backref=db.backref('quiz_attempts', lazy='dynamic'))
    
    def __repr__(self):
        return f"<QuizAttempt {self.id} - User {self.user_id}>"


class QuizResponse(db.Model):
    """User's response to a quiz question"""
    __tablename__ = 'quiz_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    selected_answer_id = db.Column(db.Integer, db.ForeignKey('quiz_answers.id'))
    text_response = db.Column(db.Text)  # For open-ended questions
    is_correct = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    question = db.relationship('QuizQuestion')
    selected_answer = db.relationship('QuizAnswer')
    
    def __repr__(self):
        return f"<QuizResponse {self.id}>"


class ModuleCompletion(db.Model):
    """Record of a user completing an education module"""
    __tablename__ = 'module_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    certificate_generated = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('module_completions', lazy='dynamic'))
    quiz_attempt = db.relationship('QuizAttempt')
    
    def __repr__(self):
        return f"<ModuleCompletion User {self.user_id} - Module {self.module_id}>"


class InteractiveElement(db.Model):
    """Interactive elements for financial education"""
    __tablename__ = 'interactive_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    element_type = db.Column(db.String(50), nullable=False)  # calculator, simulation, drag_drop, etc.
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    config_data = db.Column(db.JSON, nullable=False)  # Configuration data for the interactive element
    asl_instructions_id = db.Column(db.String(100))  # Video ID for ASL instructions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InteractiveElement {self.name} - {self.element_type}>"


class UserProgress(db.Model):
    """Track user progress through education modules"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    last_lesson_id = db.Column(db.Integer, db.ForeignKey('education_lessons.id'))
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('learning_progress', lazy='dynamic'))
    module = db.relationship('EducationModule')
    last_lesson = db.relationship('EducationLesson')
    
    def __repr__(self):
        return f"<UserProgress User {self.user_id} - Module {self.module_id} - {self.progress_percentage}%>"
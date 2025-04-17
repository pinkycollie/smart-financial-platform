"""
Database models for education features in the DEAF FIRST platform.
Handles financial education content with ASL videos.
"""

from datetime import datetime
from simple_app import db

class EducationCategory(db.Model):
    """
    Categories for financial education content.
    """
    __tablename__ = 'education_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('EducationModule', back_populates='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationCategory {self.id}: {self.name}>"

class EducationModule(db.Model):
    """
    Education modules containing financial education content.
    """
    __tablename__ = 'education_modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('education_categories.id'), nullable=False)
    level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    author = db.Column(db.String(100))
    duration_minutes = db.Column(db.Integer)
    prerequisites = db.Column(db.JSON)  # Array of prerequisite module slugs
    is_premium = db.Column(db.Boolean, default=False)
    thumbnail_url = db.Column(db.String(255))
    
    # White-label customization
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    is_white_labeled = db.Column(db.Boolean, default=False)
    
    # Publication status
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('EducationCategory', back_populates='modules')
    units = db.relationship('EducationUnit', back_populates='module', cascade='all, delete-orphan')
    enrollments = db.relationship('ModuleEnrollment', back_populates='module', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<EducationModule {self.id}: {self.title}>"

class EducationUnit(db.Model):
    """
    Education units within modules, containing individual lessons.
    """
    __tablename__ = 'education_units'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    module = db.relationship('EducationModule', back_populates='units')
    lessons = db.relationship('EducationLesson', back_populates='unit', cascade='all, delete-orphan')
    
    # Unique constraint for slug within a module
    __table_args__ = (
        db.UniqueConstraint('module_id', 'slug', name='uix_unit_module_slug'),
    )
    
    def __repr__(self):
        return f"<EducationUnit {self.id}: {self.title}>"

class EducationLesson(db.Model):
    """
    Individual lessons within units, containing educational content.
    """
    __tablename__ = 'education_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('education_units.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # text, video, quiz, interactive
    content = db.Column(db.Text)  # HTML content or JSON data
    duration_minutes = db.Column(db.Integer)
    sort_order = db.Column(db.Integer, default=0)
    
    # Video content (if applicable)
    video_url = db.Column(db.String(255))
    asl_video_id = db.Column(db.String(100))  # Mux video ID for ASL version
    transcript = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    unit = db.relationship('EducationUnit', back_populates='lessons')
    progress = db.relationship('LessonProgress', back_populates='lesson', cascade='all, delete-orphan')
    
    # Unique constraint for slug within a unit
    __table_args__ = (
        db.UniqueConstraint('unit_id', 'slug', name='uix_lesson_unit_slug'),
    )
    
    def __repr__(self):
        return f"<EducationLesson {self.id}: {self.title}>"

class ModuleEnrollment(db.Model):
    """
    User enrollments in education modules.
    """
    __tablename__ = 'module_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('education_modules.id'), nullable=False)
    
    # Enrollment status
    status = db.Column(db.String(20), default='active')  # active, completed, dropped
    progress_percent = db.Column(db.Float, default=0.0)
    
    # Timestamps
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('module_enrollments', lazy='dynamic'))
    module = db.relationship('EducationModule', back_populates='enrollments')
    lesson_progress = db.relationship('LessonProgress', back_populates='enrollment', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='uix_user_module'),
    )
    
    def __repr__(self):
        return f"<ModuleEnrollment {self.id}: User {self.user_id} in Module {self.module_id}>"

class LessonProgress(db.Model):
    """
    User progress in individual lessons.
    """
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('module_enrollments.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('education_lessons.id'), nullable=False)
    
    # Progress status
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    progress_percent = db.Column(db.Float, default=0.0)
    
    # Quiz results (if applicable)
    quiz_score = db.Column(db.Float)
    quiz_attempts = db.Column(db.Integer, default=0)
    quiz_data = db.Column(db.JSON)
    
    # Timestamps
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime)
    
    # Relationships
    enrollment = db.relationship('ModuleEnrollment', back_populates='lesson_progress')
    lesson = db.relationship('EducationLesson', back_populates='progress')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'lesson_id', name='uix_enrollment_lesson'),
    )
    
    def __repr__(self):
        return f"<LessonProgress {self.id}: Enrollment {self.enrollment_id}, Lesson {self.lesson_id}>"

class FinancialTerm(db.Model):
    """
    Financial terminology with ASL video explanations.
    """
    __tablename__ = 'financial_terms'
    
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), nullable=False, unique=True)
    definition = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # tax, investment, insurance, etc.
    complexity_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    
    # ASL video explanation
    asl_video_id = db.Column(db.String(100))  # Mux video ID
    
    # White-label customization
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    licensee_id = db.Column(db.Integer, db.ForeignKey('licensees.id'))
    is_white_labeled = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FinancialTerm {self.id}: {self.term}>"
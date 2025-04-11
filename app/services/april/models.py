from datetime import datetime
from app import db

class FinancialProfile(db.Model):
    __tablename__ = 'financial_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    annual_income = db.Column(db.Float)
    filing_status = db.Column(db.String(50))
    dependents = db.Column(db.Integer, default=0)
    investments = db.Column(db.JSON)
    retirement_accounts = db.Column(db.JSON)
    external_id = db.Column(db.String(100))  # April API identifier
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='financial_profiles')
    recommendations = db.relationship('FinancialRecommendation', back_populates='financial_profile', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<FinancialProfile id={self.id}, user_id={self.user_id}>'

class TaxDocument(db.Model):
    __tablename__ = 'tax_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(20), nullable=False)  # W2, 1099, etc.
    document_data = db.Column(db.JSON)
    year = db.Column(db.Integer, nullable=False)
    external_id = db.Column(db.String(100))  # April API identifier
    status = db.Column(db.String(20), default='pending')  # pending, processed, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='tax_documents')
    
    def __repr__(self):
        return f'<TaxDocument id={self.id}, type={self.document_type}, year={self.year}>'

class AprilTransaction(db.Model):
    __tablename__ = 'april_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    successful = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AprilTransaction id={self.id}, type={self.transaction_type}, successful={self.successful}>'

class FinancialRecommendation(db.Model):
    __tablename__ = 'financial_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    financial_profile_id = db.Column(db.Integer, db.ForeignKey('financial_profiles.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    potential_impact = db.Column(db.Float)  # Potential financial impact
    asl_video_id = db.Column(db.String(100))  # Mux video ID for ASL explanation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    financial_profile = db.relationship('FinancialProfile', back_populates='recommendations')
    
    def __repr__(self):
        return f'<FinancialRecommendation id={self.id}, type={self.recommendation_type}>'

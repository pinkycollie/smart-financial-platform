from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional

class TaxDocumentForm(FlaskForm):
    """Form for submitting tax documents"""
    document_type = SelectField(
        'Document Type',
        choices=[
            ('W2', 'W-2 - Wage and Tax Statement'),
            ('1099-MISC', '1099-MISC - Miscellaneous Income'),
            ('1099-INT', '1099-INT - Interest Income'),
            ('1099-DIV', '1099-DIV - Dividends and Distributions'),
            ('1098-E', '1098-E - Student Loan Interest'),
            ('1098-T', '1098-T - Tuition Statement')
        ],
        validators=[DataRequired()]
    )
    
    tax_year = IntegerField(
        'Tax Year',
        validators=[
            DataRequired(),
            NumberRange(min=2000, max=2030, message='Please enter a valid tax year')
        ]
    )
    
    employer = StringField('Employer/Payer Name', validators=[DataRequired()])
    income = FloatField('Income Amount', validators=[DataRequired(), NumberRange(min=0)])
    withholding = FloatField('Tax Withholding', validators=[NumberRange(min=0)])
    
    submit = SubmitField('Submit Document')

class FinancialProfileForm(FlaskForm):
    """Form for creating a financial profile"""
    annual_income = FloatField(
        'Annual Income ($)',
        validators=[DataRequired(), NumberRange(min=0)]
    )
    
    filing_status = SelectField(
        'Filing Status',
        choices=[
            ('single', 'Single'),
            ('married_joint', 'Married Filing Jointly'),
            ('married_separate', 'Married Filing Separately'),
            ('head_household', 'Head of Household'),
            ('widower', 'Qualifying Widow(er)')
        ],
        validators=[DataRequired()]
    )
    
    dependents = IntegerField(
        'Number of Dependents',
        validators=[NumberRange(min=0)],
        default=0
    )
    
    # Investment information
    stocks = FloatField(
        'Stock Investments ($)',
        validators=[Optional(), NumberRange(min=0)],
        default=0
    )
    
    bonds = FloatField(
        'Bond Investments ($)',
        validators=[Optional(), NumberRange(min=0)],
        default=0
    )
    
    real_estate = FloatField(
        'Real Estate Investments ($)',
        validators=[Optional(), NumberRange(min=0)],
        default=0
    )
    
    # Retirement accounts
    retirement_401k = FloatField(
        '401(k) Balance ($)',
        validators=[Optional(), NumberRange(min=0)],
        default=0
    )
    
    retirement_ira = FloatField(
        'IRA Balance ($)',
        validators=[Optional(), NumberRange(min=0)],
        default=0
    )
    
    submit = SubmitField('Create Profile')

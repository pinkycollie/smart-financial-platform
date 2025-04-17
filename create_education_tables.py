"""
Script to create education categories and tables.
"""

from datetime import datetime
from simple_app import app, db
import models_education

def create_education_categories():
    """Create initial education categories"""
    
    # Check if table exists, if not create it
    with app.app_context():
        # Ensure tables are created
        print("Creating education tables...")
        db.create_all()
        
        # Check if we already have categories
        if models_education.EducationCategory.query.count() == 0:
            print("Creating default education categories...")
            
            # Create parent categories
            financial_basics = models_education.EducationCategory(
                name="Financial Basics",
                slug="financial-basics",
                description="Foundational financial concepts and terminology",
                icon="book",
                sort_order=1
            )
            
            insurance = models_education.EducationCategory(
                name="Insurance",
                slug="insurance",
                description="Insurance concepts, products, and terminology",
                icon="shield-check",
                sort_order=2
            )
            
            platform_usage = models_education.EducationCategory(
                name="Platform Usage",
                slug="platform-usage",
                description="How to use the DEAF FIRST platform effectively",
                icon="window",
                sort_order=3
            )
            
            asl_training = models_education.EducationCategory(
                name="ASL Training",
                slug="asl-training",
                description="American Sign Language training for financial terms",
                icon="hand-index",
                sort_order=4
            )
            
            db.session.add_all([financial_basics, insurance, platform_usage, asl_training])
            db.session.commit()
            
            # Create subcategories for Financial Basics
            db.session.add_all([
                models_education.EducationCategory(
                    name="Budgeting",
                    slug="budgeting",
                    description="Creating and managing personal and business budgets",
                    icon="calculator",
                    parent_id=financial_basics.id,
                    sort_order=1
                ),
                models_education.EducationCategory(
                    name="Investing",
                    slug="investing",
                    description="Investment concepts and strategies",
                    icon="graph-up",
                    parent_id=financial_basics.id,
                    sort_order=2
                ),
                models_education.EducationCategory(
                    name="Credit",
                    slug="credit",
                    description="Understanding and managing credit",
                    icon="credit-card",
                    parent_id=financial_basics.id,
                    sort_order=3
                )
            ])
            
            # Create subcategories for Insurance
            db.session.add_all([
                models_education.EducationCategory(
                    name="Personal Insurance",
                    slug="personal-insurance",
                    description="Insurance products for individuals",
                    icon="person",
                    parent_id=insurance.id,
                    sort_order=1
                ),
                models_education.EducationCategory(
                    name="Business Insurance",
                    slug="business-insurance",
                    description="Insurance products for businesses",
                    icon="building",
                    parent_id=insurance.id,
                    sort_order=2
                )
            ])
            
            # Create subcategories for Platform Usage
            db.session.add_all([
                models_education.EducationCategory(
                    name="Getting Started",
                    slug="getting-started",
                    description="First steps with the DEAF FIRST platform",
                    icon="info-circle",
                    parent_id=platform_usage.id,
                    sort_order=1
                ),
                models_education.EducationCategory(
                    name="Advanced Features",
                    slug="advanced-features",
                    description="Advanced platform capabilities",
                    icon="gear",
                    parent_id=platform_usage.id,
                    sort_order=2
                )
            ])
            
            db.session.commit()
            
            print("Created default education categories successfully")
        else:
            print("Education categories already exist")

if __name__ == "__main__":
    create_education_categories()
"""
Script to populate the insurance products and bundles for deaf and hard of hearing users.
This includes specialized insurance coverage based on the Deaf First approach.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the parent directory to the path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_app import app, db
from models import (
    InsuranceProduct, 
    InsuranceBundle, 
    InsuranceBundleProduct
)

def create_insurance_products():
    """Create insurance products based on the Deaf First approach"""
    
    products = [
        # Health Insurance Enhancement
        {
            "product_code": "HEALTH_DEAF",
            "name": "Health Insurance Enhancement for Deaf Community",
            "description": "Comprehensive health insurance coverage designed specifically for deaf and hard of hearing individuals, focusing on communication access and specialized services.",
            "coverage_type": "health",
            "coverage_category": "DeafFirst",
            "minimum_premium": 75.00,  # Monthly premium
            "maximum_coverage": 1000000.00,
            "mandatory_components": {
                "communication_access": "Coverage for communication access in all healthcare settings",
                "hearing_aids": "Coverage for all types of hearing aids without caps",
                "deaf_mental_health": "Mental health providers with Deaf competence"
            },
            "optional_components": {
                "cochlear_implant": "Cochlear implant maintenance",
                "specialized_therapy": "Specialized therapy services",
                "remote_interpreting": "Remote interpreting services"
            },
            "deaf_first_differentiation": "No pathologizing of deafness; Emphasis on communication access as essential not supplemental; Recognition of Deaf-specialized providers as primary care not specialty care",
            "annual_cost_range": "$900-$2400",
            "potential_carriers": ["Aetna", "Blue Cross", "United Healthcare"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "video_remote_interpreting": True,
                "asl_fluent_representatives": True,
                "visual_claim_system": True
            }
        },
        
        # Property & Casualty Insurance
        {
            "product_code": "PROPERTY_DEAF",
            "name": "Property & Casualty Insurance for Deaf Community",
            "description": "Specialized home and property insurance that covers visual alert systems, communication technology, and Deaf-specific home modifications.",
            "coverage_type": "property_casualty",
            "coverage_category": "DeafFirst",
            "minimum_premium": 45.00,  # Monthly premium
            "maximum_coverage": 500000.00,
            "mandatory_components": {
                "visual_alert_systems": "Coverage for visual alert systems",
                "communication_technology": "Full-value recognition of communication technology",
                "home_modifications": "Coverage for Deaf-specific home modifications"
            },
            "optional_components": {
                "enhanced_security": "Enhanced security system coverage",
                "smart_home": "Smart home device integration",
                "home_office": "Specialized home office coverage"
            },
            "deaf_first_differentiation": "Recognition of visual alert systems as essential safety features not upgrades; Full valuation of communication technology; Understanding of Deaf space design principles",
            "annual_cost_range": "$540-$1200",
            "potential_carriers": ["State Farm", "Allstate", "Liberty Mutual"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "visual_emergency_notifications": True,
                "video_claims_process": True,
                "asl_home_assessments": True
            }
        },
        
        # Specialized Liability Coverage
        {
            "product_code": "LIABILITY_DEAF",
            "name": "Specialized Liability Coverage for Deaf Community",
            "description": "Liability protection specifically designed for the unique situations faced by deaf and hard of hearing individuals, including communication-related misunderstandings.",
            "coverage_type": "liability",
            "coverage_category": "DeafFirst",
            "minimum_premium": 25.00,  # Monthly premium
            "maximum_coverage": 2000000.00,
            "mandatory_components": {
                "discrimination_protection": "Protection against discrimination claims",
                "interpreter_errors": "Interpreter error & omission coverage",
                "communication_interruption": "Communication access interruption protection"
            },
            "optional_components": {
                "personal_injury": "Personal injury coverage specific to communication barriers",
                "professional_liability": "Extended professional liability protection"
            },
            "deaf_first_differentiation": "Coverage specifically for communication-related misunderstandings; Protection against discrimination impacts; Recognition of interpreter dependency risks",
            "annual_cost_range": "$300-$900",
            "potential_carriers": ["Travelers", "CNA", "Hiscox"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "deaf_legal_network": True,
                "asl_legal_assistance": True,
                "communication_risk_assessment": True
            }
        },
        
        # Business Coverage for Deaf Entrepreneurs
        {
            "product_code": "BUSINESS_DEAF",
            "name": "Business Coverage for Deaf Entrepreneurs",
            "description": "Comprehensive business insurance tailored to the specific needs of deaf-owned businesses and entrepreneurs, with focus on communication access costs.",
            "coverage_type": "business",
            "coverage_category": "DeafFirst",
            "minimum_premium": 85.00,  # Monthly premium
            "maximum_coverage": 3000000.00,
            "mandatory_components": {
                "communication_interruption": "Business interruption due to communication barriers",
                "access_expenses": "Coverage for required communication access expenses",
                "specialized_equipment": "Protection for specialized equipment"
            },
            "optional_components": {
                "key_person": "Key person coverage with communication component",
                "cyber_protection": "Extended cyber protection for visual communication",
                "succession_planning": "Succession planning"
            },
            "deaf_first_differentiation": "Recognition of communication access as business necessity not compliance cost; Understanding of Deaf business networking differences; Specialized business interruption definitions",
            "annual_cost_range": "$1020-$3600",
            "potential_carriers": ["Hartford", "Chubb", "Nationwide"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "deaf_business_consultant": True,
                "bilingual_documentation": True,
                "visual_training_materials": True
            }
        },
        
        # Service Animal/Assistive Device Coverage
        {
            "product_code": "ASSISTIVE_DEAF",
            "name": "Service Animal & Assistive Device Coverage",
            "description": "Specialized insurance for service animals and assistive devices critical to deaf and hard of hearing individuals, including rapid replacement guarantees.",
            "coverage_type": "service_animal_device",
            "coverage_category": "DeafFirst",
            "minimum_premium": 35.00,  # Monthly premium
            "maximum_coverage": 100000.00,
            "mandatory_components": {
                "service_animal_medical": "Full medical coverage for service animals",
                "device_replacement": "Replacement cost for assistive devices",
                "liability_protection": "Liability protection"
            },
            "optional_components": {
                "retirement_benefits": "Service animal retirement benefits",
                "training_maintenance": "Training maintenance coverage",
                "backup_equipment": "Backup equipment provision"
            },
            "deaf_first_differentiation": "Recognition of service animals as essential aids not pets; Understanding of technology dependence; Quick replacement guarantees",
            "annual_cost_range": "$420-$900",
            "potential_carriers": ["Petplan", "Nationwide", "ASPCA"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "emergency_device_replacement": True,
                "visual_communication_preferred": True,
                "asl_fluent_veterinary_network": True
            }
        },
        
        # Legal Expense Coverage
        {
            "product_code": "LEGAL_DEAF",
            "name": "Legal Expense Coverage for Deaf Community",
            "description": "Legal expense insurance that covers interpreter/CART services, specialized legal representation, and document translation services.",
            "coverage_type": "legal",
            "coverage_category": "DeafFirst",
            "minimum_premium": 30.00,  # Monthly premium
            "maximum_coverage": 250000.00,
            "mandatory_components": {
                "interpreter_cart": "Interpreter/CART coverage for legal proceedings",
                "specialized_legal": "Coverage for specialized legal representation",
                "document_translation": "Document translation services"
            },
            "optional_components": {
                "expert_witness": "Expert witness fees for Deaf-specific cases",
                "regulatory_compliance": "Coverage for regulatory compliance assistance"
            },
            "deaf_first_differentiation": "Direct communication with legal professionals; Understanding of Deaf-specific legal challenges; Recognition of additional time requirements for effective communication",
            "annual_cost_range": "$360-$720",
            "potential_carriers": ["ARAG", "LegalShield", "MetLife"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "asl_fluent_attorneys": True,
                "video_remote_interpreting": True,
                "visual_legal_resources": True
            }
        },
        
        # Education Coverage
        {
            "product_code": "EDUCATION_DEAF",
            "name": "Specialized Education Coverage for Deaf Community",
            "description": "Education insurance that covers communication access in educational settings, educational interpreters, and protection against education interruptions.",
            "coverage_type": "education",
            "coverage_category": "DeafFirst",
            "minimum_premium": 40.00,  # Monthly premium
            "maximum_coverage": 150000.00,
            "mandatory_components": {
                "education_access": "College/continuing education communication access",
                "educational_interpreters": "Coverage for educational interpreters",
                "education_interruption": "Education interruption protection"
            },
            "optional_components": {
                "test_preparation": "Test preparation accommodation coverage",
                "remote_learning": "Remote learning technology coverage",
                "career_counseling": "Career counseling services"
            },
            "deaf_first_differentiation": "Recognition of communication access as educational necessity; Coverage for potential educational delays due to access issues; Support for bilingual education approaches",
            "annual_cost_range": "$480-$960",
            "potential_carriers": ["Sallie Mae", "GradGuard", "A.W.G. Dewar"],
            "active": True,
            "is_deaf_specialized": True,
            "accessibility_features": {
                "asl_educational_materials": True,
                "visual_learning_platforms": True,
                "deaf_education_specialists": True
            }
        }
    ]
    
    db_products = []
    for product_data in products:
        product = InsuranceProduct.query.filter_by(product_code=product_data['product_code']).first()
        
        if not product:
            product = InsuranceProduct(
                product_code=product_data['product_code'],
                name=product_data['name'],
                description=product_data['description'],
                coverage_type=product_data['coverage_type'],
                coverage_category=product_data['coverage_category'],
                minimum_premium=product_data['minimum_premium'],
                maximum_coverage=product_data['maximum_coverage'],
                mandatory_components=product_data['mandatory_components'],
                optional_components=product_data['optional_components'],
                deaf_first_differentiation=product_data['deaf_first_differentiation'],
                annual_cost_range=product_data['annual_cost_range'],
                potential_carriers=product_data['potential_carriers'],
                active=product_data['active'],
                is_deaf_specialized=product_data['is_deaf_specialized'],
                accessibility_features=product_data['accessibility_features']
            )
            db.session.add(product)
            print(f"Created insurance product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")
        
        db_products.append(product)
    
    db.session.commit()
    return db_products

def create_insurance_bundles(products):
    """Create insurance bundles based on integration points"""
    
    # Map products by code for easy reference
    product_map = {product.product_code: product for product in products}
    
    bundles = [
        # Communication Access Bundle
        {
            "name": "Communication Access Bundle",
            "bundle_code": "COMM_ACCESS",
            "description": "A comprehensive insurance bundle that ensures communication access across all domains of life, combining health, liability, and legal expense coverage.",
            "integration_point": "Communication Access Bundle",
            "integration_rationale": "Comprehensive approach to communication access across all life domains; Recognition that communication barriers cross traditional insurance lines",
            "implementation_requirements": "Unified communication needs assessment; Cross-line communication access fund; Coordinated claims handling",
            "expected_outcome": "Seamless coverage for communication needs regardless of setting; Elimination of coverage gaps for interpreters/CART/etc.",
            "discount_percentage": 15.0,
            "active": True,
            "primary_products": ["HEALTH_DEAF", "LIABILITY_DEAF", "LEGAL_DEAF"],
            "supporting_products": ["BUSINESS_DEAF", "PROPERTY_DEAF"]
        },
        
        # Technology Ecosystem Protection
        {
            "name": "Technology Ecosystem Protection",
            "bundle_code": "TECH_ECOSYSTEM",
            "description": "Protection for the entire technology ecosystem that deaf and hard of hearing individuals rely on, covering devices across home, work, and personal use.",
            "integration_point": "Technology Ecosystem Protection",
            "integration_rationale": "Modern Deaf living relies on interconnected technology ecosystem that spans traditional coverage boundaries",
            "implementation_requirements": "Inventory management system for all devices; Cross-line technology replacement fund; Rapid replacement protocol",
            "expected_outcome": "Protection against technology ecosystem disruption; Recognition of full replacement value across settings",
            "discount_percentage": 12.0,
            "active": True,
            "primary_products": ["PROPERTY_DEAF", "ASSISTIVE_DEAF", "BUSINESS_DEAF"],
            "supporting_products": ["HEALTH_DEAF"]
        },
        
        # Professional Development Pathway
        {
            "name": "Professional Development Pathway",
            "bundle_code": "PROF_DEV",
            "description": "Career advancement protection that integrates education, business protection, and liability considerations for deaf professionals and entrepreneurs.",
            "integration_point": "Professional Development Pathway",
            "integration_rationale": "Career advancement requires specialized integration of education, business protection and disability considerations",
            "implementation_requirements": "Career milestone assessment; Development milestone protection; Cross-line opportunity protection",
            "expected_outcome": "Enhanced career advancement; Protection against discrimination impacts; Reduced entrepreneurial failure rate",
            "discount_percentage": 10.0,
            "active": True,
            "primary_products": ["BUSINESS_DEAF", "EDUCATION_DEAF"],
            "supporting_products": ["LEGAL_DEAF", "LIABILITY_DEAF"]
        },
        
        # Family Communication Security
        {
            "name": "Family Communication Security",
            "bundle_code": "FAMILY_COMM",
            "description": "Protection for family communication access spanning health, education, and property insurance needs for deaf family members.",
            "integration_point": "Family Communication Security",
            "integration_rationale": "Family communication access represents unique consideration across traditional insurance lines",
            "implementation_requirements": "Family communication assessment; Cross-generational protection; Family emergency communication protocol",
            "expected_outcome": "Family resilience during crises; Enhanced family communication security; Protection against family communication breakdown",
            "discount_percentage": 10.0,
            "active": True,
            "primary_products": ["HEALTH_DEAF", "EDUCATION_DEAF"],
            "supporting_products": ["PROPERTY_DEAF", "LEGAL_DEAF"]
        }
    ]
    
    for bundle_data in bundles:
        bundle = InsuranceBundle.query.filter_by(bundle_code=bundle_data['bundle_code']).first()
        
        if not bundle:
            bundle = InsuranceBundle(
                name=bundle_data['name'],
                bundle_code=bundle_data['bundle_code'],
                description=bundle_data['description'],
                integration_point=bundle_data['integration_point'],
                integration_rationale=bundle_data['integration_rationale'],
                implementation_requirements=bundle_data['implementation_requirements'],
                expected_outcome=bundle_data['expected_outcome'],
                discount_percentage=bundle_data['discount_percentage'],
                active=bundle_data['active']
            )
            db.session.add(bundle)
            db.session.flush()  # Get the bundle ID before adding products
            
            # Add primary products
            for product_code in bundle_data['primary_products']:
                if product_code in product_map:
                    bundle_product = InsuranceBundleProduct(
                        bundle_id=bundle.id,
                        product_id=product_map[product_code].id,
                        is_primary=True
                    )
                    db.session.add(bundle_product)
            
            # Add supporting products
            for product_code in bundle_data['supporting_products']:
                if product_code in product_map:
                    bundle_product = InsuranceBundleProduct(
                        bundle_id=bundle.id,
                        product_id=product_map[product_code].id,
                        is_primary=False
                    )
                    db.session.add(bundle_product)
            
            print(f"Created insurance bundle: {bundle.name}")
        else:
            print(f"Bundle already exists: {bundle.name}")
    
    db.session.commit()

def run():
    """Run the population script"""
    with app.app_context():
        try:
            print("Starting Deaf First insurance data population...")
            products = create_insurance_products()
            create_insurance_bundles(products)
            print("Successfully populated Deaf First insurance data.")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            raise

if __name__ == "__main__":
    run()
"""
Routes for financial advisor resources in the DEAF FIRST platform.
Provides information on serving deaf clients and licensing the platform.
"""

from flask import Blueprint, render_template
from services.seo import seo_service
from services.licensing import white_label_service

advisors_bp = Blueprint('advisors', __name__, url_prefix='/advisors')

@advisors_bp.route('/')
def advisor_resources():
    """
    Main page for financial advisor resources.
    Shows how advisors can better serve deaf clients and license the platform.
    
    Returns:
        Response: Rendered advisor resources page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="Resources for Financial Advisors with Deaf Clients",
        description="Tools, resources, and guidance for financial advisors serving deaf clients. Learn how to provide accessible financial services with ASL support.",
        keywords=[
            "financial advisor deaf clients",
            "deaf client financial advice",
            "ASL financial consulting",
            "deaf financial planning",
            "serving deaf clients finance",
            "deaf community financial advisor"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'advisors/resources.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="Resources for Financial Advisors with Deaf Clients"
    )

@advisors_bp.route('/case-studies')
def case_studies():
    """
    Success stories from financial professionals using the platform.
    
    Returns:
        Response: Rendered case studies page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="DEAF FIRST Success Stories | Financial Advisors Serving Deaf Clients",
        description="Read success stories from financial advisors, agents, and educators using the DEAF FIRST platform to serve deaf clients and grow their practice.",
        keywords=[
            "deaf financial success stories",
            "financial advisor deaf clients",
            "deaf client case studies",
            "ASL financial planning success",
            "deaf financial education case study",
            "deaf-friendly financial practice"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors"),
        ("Case Studies", "/advisors/case-studies")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'advisors/case_studies.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="Success Stories | Financial Advisors Serving Deaf Clients"
    )

@advisors_bp.route('/roi-calculator')
def roi_calculator():
    """
    ROI calculator for financial professionals considering the platform.
    
    Returns:
        Response: Rendered ROI calculator page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="ROI Calculator for DEAF FIRST Platform | Financial Advisors",
        description="Calculate your return on investment when licensing the DEAF FIRST platform for serving deaf clients. See how expanding your practice to deaf clients can benefit your bottom line.",
        keywords=[
            "financial advisor ROI calculator",
            "deaf clients ROI",
            "financial practice ROI deaf",
            "deaf client acquisition cost",
            "financial platform ROI calculator",
            "deaf financial services profitability"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors"),
        ("ROI Calculator", "/advisors/roi-calculator")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    # Get licensing tiers for ROI calculation
    license_tiers = white_label_service.get_license_tiers()
    
    return render_template(
        'advisors/roi_calculator.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        license_tiers=license_tiers,
        title="ROI Calculator | DEAF FIRST Platform for Financial Advisors"
    )

@advisors_bp.route('/testimonials')
def testimonials():
    """
    Testimonials from financial professionals using the platform.
    
    Returns:
        Response: Rendered testimonials page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="Testimonials from Financial Professionals | DEAF FIRST Platform",
        description="Hear what financial advisors, agents, and educators say about using the DEAF FIRST platform to serve deaf clients. Real testimonials from real professionals.",
        keywords=[
            "financial advisor testimonials",
            "deaf client financial testimonials",
            "ASL financial platform reviews",
            "financial advisor deaf clients",
            "deaf financial education reviews",
            "financial professional testimonials"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors"),
        ("Testimonials", "/advisors/testimonials")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'advisors/testimonials.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="Testimonials | Financial Professionals Using DEAF FIRST"
    )

@advisors_bp.route('/certifications')
def certifications():
    """
    Information on getting certified for serving deaf clients.
    
    Returns:
        Response: Rendered certifications page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="Deaf-Friendly Financial Professional Certification",
        description="Get certified as a deaf-friendly financial professional. Learn how to effectively communicate with and serve deaf clients in the financial industry.",
        keywords=[
            "deaf-friendly certification",
            "financial advisor deaf certification",
            "ASL financial professional",
            "deaf client service certification",
            "financial advisor ASL training",
            "deaf accessible financial services"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors"),
        ("Certification", "/advisors/certifications")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'advisors/certifications.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="Deaf-Friendly Financial Professional Certification"
    )

@advisors_bp.route('/best-practices')
def best_practices():
    """
    Best practices for financial professionals serving deaf clients.
    
    Returns:
        Response: Rendered best practices page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="Best Practices for Financial Advisors Serving Deaf Clients",
        description="Learn best practices for financial advisors, agents, and educators working with deaf clients. Tips on communication, accessibility, and providing exceptional service.",
        keywords=[
            "deaf client best practices",
            "financial advisor deaf clients",
            "deaf financial communication",
            "ASL financial services",
            "deaf accessible finance",
            "serving deaf clients effectively"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("For Advisors", "/advisors"),
        ("Best Practices", "/advisors/best-practices")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'advisors/best_practices.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="Best Practices | Financial Advisors Serving Deaf Clients"
    )
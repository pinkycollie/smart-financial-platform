"""
Sitemap routes for DEAF FIRST platform.
Provides XML and HTML sitemaps for search engines and users.
"""

from flask import Blueprint, render_template, make_response
from services.sitemap import sitemap_generator
from services.seo import seo_service

sitemap_bp = Blueprint('sitemap', __name__)

@sitemap_bp.route('/sitemap.xml')
def sitemap_xml():
    """
    Generate and serve sitemap.xml for search engines.
    
    Returns:
        Response: XML sitemap
    """
    xml_content = sitemap_generator.generate_xml()
    response = make_response(xml_content)
    response.headers["Content-Type"] = "application/xml"
    return response


@sitemap_bp.route('/sitemap')
def sitemap_html():
    """
    Human-readable HTML sitemap.
    
    Returns:
        Response: Rendered HTML sitemap
    """
    sitemap_sections = sitemap_generator.generate_html_sitemap()
    
    meta_tags = seo_service.generate_meta_tags(
        title="DEAF FIRST Platform Sitemap",
        description="Complete sitemap of the DEAF FIRST financial platform with ASL support for deaf clients.",
        keywords=[
            "deaf financial sitemap",
            "ASL finance",
            "deaf financial services",
            "financial platform map",
            "financial advisor deaf clients"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("Sitemap", "/sitemap")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'sitemap.html',
        sitemap_sections=sitemap_sections,
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="DEAF FIRST Platform Sitemap"
    )


@sitemap_bp.route('/platform')
def platform_overview():
    """
    Platform overview page. Shows main features and benefits for financial professionals.
    Similar to Holistiplan's approach but with DEAF FIRST focus.
    
    Returns:
        Response: Rendered platform overview page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="DEAF FIRST Platform for Financial Professionals",
        description="Financial platform with ASL support, designed for advisors, agents and educators serving deaf clients.",
        keywords=[
            "deaf financial platform",
            "ASL financial services",
            "deaf client financial software",
            "deaf-friendly financial advisor",
            "ASL finance tools",
            "white label deaf financial services"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("Platform", "/platform")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'platform/overview.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="DEAF FIRST Platform for Financial Professionals"
    )


@sitemap_bp.route('/platform/whitelabel')
def whitelabel_platform():
    """
    White-label platform page. Shows licensing options for financial professionals.
    
    Returns:
        Response: Rendered white-label platform page
    """
    meta_tags = seo_service.generate_meta_tags(
        title="White-Label DEAF FIRST Platform for Financial Professionals",
        description="License and customize the DEAF FIRST platform for your deaf clients. White-label financial education with ASL support.",
        keywords=[
            "white label financial platform",
            "custom financial software deaf clients",
            "branded financial services ASL",
            "deaf client platform license",
            "financial advisor deaf tools",
            "white label ASL financial education"
        ]
    )
    
    # Structured data for breadcrumbs
    breadcrumbs = [
        ("Home", "/"),
        ("Platform", "/platform"),
        ("White Label", "/platform/whitelabel")
    ]
    breadcrumb_ld = seo_service.generate_education_breadcrumbs(breadcrumbs)
    
    return render_template(
        'platform/whitelabel.html',
        meta_tags=meta_tags,
        breadcrumb_ld=breadcrumb_ld,
        title="White-Label DEAF FIRST Platform"
    )


@sitemap_bp.route('/advisors')
def advisor_resources():
    """
    Resources for financial advisors serving deaf clients.
    
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
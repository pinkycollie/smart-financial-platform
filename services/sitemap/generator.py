"""
Sitemap generator for DEAF FIRST platform, following professional financial
software structure similar to Holistiplan but optimized for deaf clients.
"""

import os
from datetime import datetime
from flask import url_for, current_app

class SitemapGenerator:
    """
    Generates XML and HTML sitemaps for the DEAF FIRST platform.
    Focuses on SEO-friendly structure for financial professionals serving deaf clients.
    """
    
    def __init__(self, app_config=None):
        """Initialize sitemap generator with optional configuration"""
        self.app_config = app_config or {}
        self.base_url = self.app_config.get('BASE_URL', 'https://deaffirst.mbtqgroup.com')
        self.priority_paths = {
            '/': 1.0,
            '/platform': 0.9,
            '/pricing': 0.9,
            '/education': 0.8,
            '/resources': 0.8,
            '/about': 0.7,
            '/contact': 0.7
        }
        self.change_frequency = {
            '/': 'daily',
            '/platform': 'weekly',
            '/blog': 'weekly',
            '/resources': 'weekly',
            '/pricing': 'monthly',
            '/about': 'monthly',
            '/education': 'weekly'
        }
    
    def generate_sitemap_data(self):
        """
        Generate sitemap data structure for the entire platform.
        
        Returns:
            list: List of sitemap entries
        """
        # Base platform pages (similar to Holistiplan but DEAF FIRST focused)
        sitemap_data = [
            # Main marketing pages
            self._create_entry('/', 'Home', 'DEAF FIRST Financial Platform for Deaf Clients', 'daily', 1.0),
            self._create_entry('/platform', 'Platform', 'Financial Platform with ASL Support', 'weekly', 0.9),
            self._create_entry('/platform/features', 'Features', 'ASL-Supported Financial Features', 'weekly', 0.9),
            self._create_entry('/platform/whitelabel', 'White Label', 'Customize for Your Financial Practice', 'weekly', 0.9),
            self._create_entry('/platform/security', 'Security', 'Secure Financial Data Management', 'monthly', 0.8),
            self._create_entry('/pricing', 'Pricing', 'License the DEAF FIRST Platform', 'monthly', 0.9),
            self._create_entry('/about', 'About', 'About MBTQ GROUP & DEAF FIRST', 'monthly', 0.7),
            self._create_entry('/about/mission', 'Our Mission', 'DEAF FIRST Mission and Vision', 'monthly', 0.7),
            self._create_entry('/about/team', 'Team', 'Meet the DEAF FIRST Team', 'monthly', 0.7),
            self._create_entry('/contact', 'Contact', 'Contact MBTQ GROUP', 'monthly', 0.7),
            
            # Resources section
            self._create_entry('/resources', 'Resources', 'Financial Resources for Deaf Clients', 'weekly', 0.8),
            self._create_entry('/resources/videos', 'ASL Videos', 'Financial Education Videos in ASL', 'weekly', 0.8),
            self._create_entry('/resources/glossary', 'ASL Glossary', 'Financial Terms in ASL', 'monthly', 0.8),
            self._create_entry('/resources/tools', 'Financial Tools', 'Interactive Financial Tools with ASL Support', 'monthly', 0.8),
            self._create_entry('/resources/downloads', 'Downloads', 'Downloadable Financial Resources', 'monthly', 0.7),
            
            # Advisor resources (similar to Holistiplan's approach)
            self._create_entry('/advisors', 'For Financial Advisors', 'Tools for Advisors Serving Deaf Clients', 'weekly', 0.9),
            self._create_entry('/advisors/case-studies', 'Case Studies', 'Success Stories with Deaf Clients', 'monthly', 0.8),
            self._create_entry('/advisors/roi-calculator', 'ROI Calculator', 'Calculate Return on Investment', 'monthly', 0.8),
            self._create_entry('/advisors/testimonials', 'Testimonials', 'Advisor Testimonials', 'monthly', 0.7),
            self._create_entry('/advisors/certifications', 'Deaf-Friendly Certification', 'Get Certified for Deaf Financial Services', 'monthly', 0.8),
            
            # Education hub
            self._create_entry('/education', 'Financial Education', 'ASL Financial Education Center', 'weekly', 0.8),
            self._create_entry('/education/modules', 'Education Modules', 'Interactive Financial Modules with ASL', 'weekly', 0.8),
            self._create_entry('/education/webinars', 'Webinars', 'ASL Financial Webinars', 'weekly', 0.8),
            self._create_entry('/education/courses', 'Courses', 'In-depth Financial Courses with ASL', 'weekly', 0.8),
            
            # Blog and news (like Holistiplan)
            self._create_entry('/blog', 'Blog', 'Financial Insights for the Deaf Community', 'weekly', 0.8),
            self._create_entry('/blog/categories/tips', 'Financial Tips', 'Financial Tips for Deaf Individuals', 'weekly', 0.7),
            self._create_entry('/blog/categories/news', 'Financial News', 'Financial News for the Deaf Community', 'weekly', 0.7),
            self._create_entry('/blog/categories/accessibility', 'Financial Accessibility', 'Making Finance Accessible to Deaf Clients', 'weekly', 0.7),
            
            # Legal and compliance (similar to Holistiplan)
            self._create_entry('/legal/privacy', 'Privacy Policy', 'DEAF FIRST Privacy Policy', 'yearly', 0.5),
            self._create_entry('/legal/terms', 'Terms of Service', 'DEAF FIRST Terms of Service', 'yearly', 0.5),
            self._create_entry('/legal/licensing', 'Licensing Terms', 'Platform Licensing Terms', 'yearly', 0.5),
            self._create_entry('/legal/accessibility', 'Accessibility Statement', 'DEAF FIRST Accessibility Commitment', 'yearly', 0.6),
            
            # Support (similar to Holistiplan)
            self._create_entry('/support', 'Support', 'DEAF FIRST Support Center', 'monthly', 0.7),
            self._create_entry('/support/faqs', 'FAQs', 'Frequently Asked Questions', 'monthly', 0.7),
            self._create_entry('/support/knowledge-base', 'Knowledge Base', 'DEAF FIRST Knowledge Base', 'weekly', 0.7),
            self._create_entry('/support/contact', 'Contact Support', 'Contact DEAF FIRST Support', 'monthly', 0.7),
            
            # Demo and trials (similar to Holistiplan)
            self._create_entry('/demo', 'Request Demo', 'Request a DEAF FIRST Platform Demo', 'monthly', 0.9),
            self._create_entry('/trial', 'Free Trial', 'Try DEAF FIRST Platform Free', 'monthly', 0.9),
            
            # Client portal
            self._create_entry('/client-portal', 'Client Portal', 'DEAF FIRST Client Portal', 'monthly', 0.6),
            self._create_entry('/client-portal/login', 'Client Login', 'Login to DEAF FIRST Client Portal', 'monthly', 0.6),
            
            # Advisor portal (like Holistiplan)
            self._create_entry('/advisor-portal', 'Advisor Portal', 'DEAF FIRST Advisor Portal', 'monthly', 0.6),
            self._create_entry('/advisor-portal/login', 'Advisor Login', 'Login to DEAF FIRST Advisor Portal', 'monthly', 0.6),
            
            # Deaf-specific pages (unique to our platform)
            self._create_entry('/deaf-resources', 'Deaf Financial Resources', 'Specialized Financial Resources for Deaf Individuals', 'weekly', 0.8),
            self._create_entry('/asl-finance', 'ASL Finance Hub', 'Financial Education in American Sign Language', 'weekly', 0.8),
            self._create_entry('/find-deaf-friendly-advisor', 'Find Deaf-Friendly Advisor', 'Locate Financial Advisors Serving Deaf Clients', 'monthly', 0.8),
        ]
        
        return sitemap_data
    
    def _create_entry(self, path, title, description, change_freq='monthly', priority=0.5):
        """
        Create a sitemap entry.
        
        Args:
            path (str): URL path
            title (str): Page title
            description (str): Page description
            change_freq (str): Change frequency
            priority (float): SEO priority
            
        Returns:
            dict: Sitemap entry
        """
        today = datetime.now().strftime('%Y-%m-%d')
        url = f"{self.base_url}{path}" if path.startswith('/') else f"{self.base_url}/{path}"
        
        return {
            'loc': url,
            'lastmod': today,
            'changefreq': change_freq,
            'priority': priority,
            'title': title,
            'description': description
        }
    
    def generate_xml(self):
        """
        Generate XML sitemap.
        
        Returns:
            str: XML sitemap content
        """
        sitemap_data = self.generate_sitemap_data()
        
        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        ]
        
        for entry in sitemap_data:
            xml.append('  <url>')
            xml.append(f'    <loc>{entry["loc"]}</loc>')
            xml.append(f'    <lastmod>{entry["lastmod"]}</lastmod>')
            xml.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
            xml.append(f'    <priority>{entry["priority"]}</priority>')
            xml.append('  </url>')
        
        xml.append('</urlset>')
        
        return '\n'.join(xml)
    
    def generate_html_sitemap(self):
        """
        Generate HTML sitemap structure.
        
        Returns:
            dict: HTML sitemap structure
        """
        sitemap_data = self.generate_sitemap_data()
        
        # Group by sections
        sections = {}
        
        for entry in sitemap_data:
            path = entry['loc'].replace(self.base_url, '')
            parts = path.strip('/').split('/')
            
            if len(parts) == 0 or parts[0] == '':
                section = 'Home'
            else:
                section = parts[0].capitalize()
            
            if section not in sections:
                sections[section] = []
            
            sections[section].append(entry)
        
        return sections
    
    def get_sitemap_sections(self):
        """
        Get main sitemap sections.
        
        Returns:
            list: Main sitemap sections
        """
        sections = [
            {'key': 'platform', 'title': 'Platform', 'description': 'DEAF FIRST Platform Features'},
            {'key': 'education', 'title': 'Financial Education', 'description': 'Interactive Financial Education with ASL'},
            {'key': 'advisors', 'title': 'For Advisors', 'description': 'Tools for Financial Advisors Serving Deaf Clients'},
            {'key': 'resources', 'title': 'Resources', 'description': 'Financial Resources in ASL'},
            {'key': 'blog', 'title': 'Blog', 'description': 'Financial Insights for the Deaf Community'},
            {'key': 'support', 'title': 'Support', 'description': 'Get Help with the DEAF FIRST Platform'},
            {'key': 'about', 'title': 'About', 'description': 'About MBTQ GROUP and DEAF FIRST'},
            {'key': 'legal', 'title': 'Legal', 'description': 'Legal Information and Compliance'},
        ]
        
        return sections

# Initialize the sitemap generator
sitemap_generator = SitemapGenerator()
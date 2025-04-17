"""
SEO and indexing optimization service for DEAF FIRST financial platform.
Designed for maximum discoverability and search engine visibility.
"""

import json
from flask import request, url_for
from urllib.parse import urljoin

class SEOService:
    """
    Service for optimizing SEO across the DEAF FIRST platform.
    Helps with structured data, meta tags, and content optimization.
    """
    
    def __init__(self, app_config=None):
        """Initialize SEO service with optional configuration"""
        self.app_config = app_config or {}
        self.site_name = self.app_config.get('SITE_NAME', 'MBTQ GROUP | DEAF FIRST Financial Platform')
        self.default_description = self.app_config.get(
            'DEFAULT_DESCRIPTION', 
            'MBTQ GROUP DEAF FIRST Financial Platform - Accessible financial services with ASL support, designed for the deaf community. Launched April 26, 2022.'
        )
        self.base_url = self.app_config.get('BASE_URL', '')
        self.founded_date = "2022-04-26"
    
    def get_canonical_url(self):
        """Get canonical URL for current page"""
        if request:
            path = request.path
            return urljoin(self.base_url, path)
        return self.base_url
    
    def generate_meta_tags(self, title=None, description=None, keywords=None, image_url=None, content_type=None):
        """
        Generate meta tags for SEO optimization.
        
        Args:
            title (str): Page title
            description (str): Page description
            keywords (list): List of keywords
            image_url (str): URL to featured image
            content_type (str): Type of content (article, course, etc.)
            
        Returns:
            dict: Dictionary of meta tags
        """
        meta_tags = {
            'title': title or self.site_name,
            'description': description or self.default_description,
            'canonical': self.get_canonical_url(),
            'og:title': title or self.site_name,
            'og:description': description or self.default_description,
            'og:type': content_type or 'website',
            'og:url': self.get_canonical_url(),
            'twitter:card': 'summary_large_image',
            'twitter:title': title or self.site_name,
            'twitter:description': description or self.default_description,
        }
        
        if image_url:
            meta_tags['og:image'] = image_url
            meta_tags['twitter:image'] = image_url
        
        if keywords:
            meta_tags['keywords'] = ', '.join(keywords)
        
        return meta_tags
    
    def generate_structured_data(self, data_type, data):
        """
        Generate structured data for Rich Results in search engines.
        
        Args:
            data_type (str): Type of structured data (Course, Article, etc.)
            data (dict): Data to include in structured data
            
        Returns:
            str: JSON-LD structured data
        """
        structured_data = {
            "@context": "https://schema.org",
            "@type": data_type
        }
        
        # Merge with provided data
        structured_data.update(data)
        
        return json.dumps(structured_data)
    
    def generate_organization_structured_data(self):
        """
        Generate Organization structured data for MBTQ GROUP.
        
        Returns:
            str: JSON-LD structured data for Organization
        """
        organization_data = {
            "name": "MBTQ GROUP",
            "alternateName": "DEAF FIRST Financial Platform",
            "description": "MBTQ GROUP provides financial services with ASL support designed specifically for the deaf community.",
            "foundingDate": self.founded_date,
            "url": self.base_url,
            "sameAs": [
                "https://www.example.com/mbtq-group",  # Replace with actual social media links
                "https://www.linkedin.com/company/mbtq-group"
            ],
            "logo": {
                "@type": "ImageObject",
                "url": urljoin(self.base_url, "/static/images/mbtq-logo.png")
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "email": "contact@example.com"  # Replace with actual contact email
            }
        }
        
        return self.generate_structured_data("Organization", organization_data)
    
    def generate_course_structured_data(self, module):
        """
        Generate Course structured data for educational modules.
        
        Args:
            module (EducationModule): Education module
            
        Returns:
            str: JSON-LD structured data for Course
        """
        provider = {
            "@type": "Organization",
            "name": "MBTQ GROUP | DEAF FIRST Financial Platform",
            "sameAs": self.base_url,
            "foundingDate": self.founded_date
        }
        
        course_data = {
            "name": module.title,
            "description": module.summary,
            "provider": provider,
            "accessMode": ["textual", "visual"],
            "accessModeSufficient": ["textual", "visual"],
            "accessibilityFeature": ["signLanguage", "captions"],
            "accessibilityHazard": "none",
            "audience": {
                "@type": "Audience",
                "audienceType": "DeafCommunity"
            }
        }
        
        if module.category:
            course_data["courseCode"] = f"DF-{module.category.name[:3].upper()}-{module.id}"
        
        if module.published_at:
            course_data["datePublished"] = module.published_at.strftime("%Y-%m-%d")
        
        if module.lessons and module.lessons.count() > 0:
            course_data["numberOfLessons"] = module.lessons.count()
            
            # Add hasCourseInstance if there are lessons
            instance = {
                "@type": "CourseInstance",
                "courseMode": "online",
                "courseWorkload": f"PT{module.estimated_time}M"
            }
            course_data["hasCourseInstance"] = instance
        
        return self.generate_structured_data("Course", course_data)
    
    def generate_education_breadcrumbs(self, items):
        """
        Generate breadcrumb structured data.
        
        Args:
            items (list): List of (name, url) tuples
            
        Returns:
            str: JSON-LD structured data for BreadcrumbList
        """
        breadcrumb_list = {
            "@type": "BreadcrumbList",
            "itemListElement": []
        }
        
        for position, (name, url) in enumerate(items, start=1):
            breadcrumb_list["itemListElement"].append({
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": urljoin(self.base_url, url) if url else None
            })
        
        return self.generate_structured_data("BreadcrumbList", breadcrumb_list)
    
    def generate_lesson_structured_data(self, lesson):
        """
        Generate Article structured data for education lessons.
        
        Args:
            lesson (EducationLesson): Education lesson
            
        Returns:
            str: JSON-LD structured data for Article
        """
        article_data = {
            "name": lesson.title,
            "headline": lesson.title,
            "accessMode": ["textual", "visual"],
            "accessModeSufficient": ["textual", "visual"],
            "accessibilityFeature": ["signLanguage", "captions"],
            "accessibilityHazard": "none",
            "author": {
                "@type": "Organization",
                "name": "MBTQ GROUP | DEAF FIRST Financial Platform",
                "sameAs": self.base_url
            }
        }
        
        if lesson.created_at:
            article_data["datePublished"] = lesson.created_at.strftime("%Y-%m-%d")
            
        if lesson.updated_at:
            article_data["dateModified"] = lesson.updated_at.strftime("%Y-%m-%d")
            
        if lesson.asl_video_id:
            article_data["video"] = {
                "@type": "VideoObject",
                "name": f"ASL Video: {lesson.title}",
                "description": f"American Sign Language video for {lesson.title}",
                "accessMode": "visual",
                "accessibilityFeature": ["signLanguage"]
            }
            
        return self.generate_structured_data("Article", article_data)
    
    def generate_seo_keywords(self, content_type, obj):
        """
        Generate SEO keywords based on content type and object.
        
        Args:
            content_type (str): Type of content (module, lesson, etc.)
            obj: Content object
            
        Returns:
            list: List of keywords
        """
        # Base keywords for all content
        keywords = [
            "deaf education", "ASL", "sign language", "finance", 
            "accessible finance", "deaf first", "MBTQ GROUP", 
            "deaf community", "financial literacy", "deaf financial services",
            "Texas Workforce", "Vocational Rehabilitation"
        ]
        
        if content_type == "module":
            keywords.extend([
                obj.title.lower(),
                f"{obj.title.lower()} ASL",
                f"{obj.difficulty_level} financial education",
                "financial literacy",
                "deaf financial education",
                "licensed financial platform",
                "CBTEC"
            ])
            
            if obj.category:
                keywords.extend([
                    obj.category.name.lower(),
                    f"{obj.category.name.lower()} for deaf"
                ])
        
        elif content_type == "lesson":
            keywords.extend([
                obj.title.lower(),
                f"{obj.title.lower()} ASL",
                "financial lesson",
                "financial education video",
                "ASL financial lesson",
                "Brikor Inc"
            ])
            
            if obj.module:
                keywords.extend([
                    obj.module.title.lower(),
                    f"{obj.module.title.lower()} lesson"
                ])
        
        elif content_type == "glossary":
            keywords.extend([
                "financial terms",
                "ASL financial glossary",
                "deaf financial terms",
                "sign language finance",
                "financial vocabulary ASL",
                "financial coaching for deaf"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = [k for k in keywords if not (k in seen or seen.add(k))]
        
        return unique_keywords
    
    def generate_sitemap_entry(self, url, last_modified=None, change_freq="weekly", priority=0.8):
        """
        Generate a sitemap entry for a URL.
        
        Args:
            url (str): The URL
            last_modified (datetime, optional): Last modified date
            change_freq (str, optional): Change frequency
            priority (float, optional): Priority
            
        Returns:
            dict: Sitemap entry data
        """
        entry = {
            "loc": urljoin(self.base_url, url),
            "changefreq": change_freq,
            "priority": priority
        }
        
        if last_modified:
            entry["lastmod"] = last_modified.strftime("%Y-%m-%d")
            
        return entry

# Initialize a single instance to be used application-wide
seo_service = SEOService()
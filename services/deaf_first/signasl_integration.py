"""
SignASL.org Integration Service for DEAF FIRST platform
Provides ASL videos for insurance and financial terms from SignASL.org
"""

import logging

logger = logging.getLogger(__name__)

class SignASLIntegration:
    """Integrates SignASL.org videos for ASL financial terminology"""
    
    def __init__(self):
        """Initialize the SignASL integration service"""
        self.base_embed_url = "https://embed.signasl.org/widgets.js"
        self.base_sign_url = "https://www.signasl.org/sign/"
        
        # Dict of known insurance and financial terms with their video reference IDs
        self.known_term_refs = {
            'insurance': 'trkcerilxk',
            # Add more terms as they're identified
        }
        
        logger.info("SignASL integration service initialized")
    
    def get_embed_code(self, term):
        """
        Get the embed code for a specific ASL term
        
        Args:
            term (str): The financial or insurance term to show in ASL
            
        Returns:
            dict: The embed information with HTML code
        """
        term = term.lower().strip()
        
        if term not in self.known_term_refs:
            logger.warning(f"No known SignASL reference for term: {term}")
            return None
        
        vid_ref = self.known_term_refs[term]
        
        # Generate the embed HTML
        embed_html = f"""
        <div class="signasl-video-container">
            <blockquote class="signasldata-embed" data-vidref="{vid_ref}">
                <a href="{self.base_sign_url}{term}">Watch how to sign '{term}' in American Sign Language</a>
            </blockquote>
            <script async src="{self.base_embed_url}" charset="utf-8"></script>
        </div>
        """
        
        return {
            'term': term,
            'embed_html': embed_html,
            'source': 'SignASL.org',
            'url': f"{self.base_sign_url}{term}"
        }
    
    def get_embedded_script_tag(self):
        """
        Get the script tag needed for SignASL embeds
        Should be included once in the page.
        
        Returns:
            str: The script tag HTML
        """
        return f'<script async src="{self.base_embed_url}" charset="utf-8"></script>'

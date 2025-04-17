"""
Investopedia Integration Service for DEAF FIRST platform
Provides financial definitions from Investopedia to accompany ASL videos
"""

import logging
import trafilatura
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
import json

logger = logging.getLogger(__name__)

class InvestopediaIntegration:
    """Integrates Investopedia financial term definitions with ASL videos"""
    
    def __init__(self):
        """Initialize the Investopedia integration service"""
        self.base_url = "https://www.investopedia.com/terms"
        self.dictionary_url = "https://www.investopedia.com/financial-term-dictionary-4769738"
        
        # Cache for storing definitions to reduce API calls
        self.definitions_cache = {}
        
        logger.info("Investopedia integration service initialized")
    
    def get_term_definition(self, term: str) -> Optional[Dict]:
        """
        Get the definition for a financial or insurance term from Investopedia
        
        Args:
            term (str): The financial or insurance term to define
            
        Returns:
            dict: The definition information with URL and content or None if not found
        """
        # Normalize term
        term = term.lower().strip()
        
        # Check cache first
        if term in self.definitions_cache:
            return self.definitions_cache[term]
        
        try:
            # Format the URL based on term (handle multi-word terms)
            formatted_term = term.replace(' ', '-')
            term_url = f"{self.base_url}/{formatted_term}"
            
            # Try to fetch the page
            response = requests.get(term_url, timeout=10)
            
            # If page doesn't exist, try searching the dictionary
            if response.status_code != 200:
                logger.info(f"No direct page for term '{term}', trying dictionary search")
                return self._search_dictionary(term)
            
            # Use trafilatura to extract clean content
            content = trafilatura.extract(response.text)
            
            if not content:
                logger.warning(f"Could not extract content for term: {term}")
                return None
            
            # Try to extract structured data
            structured_data = self._extract_structured_data(response.text)
            
            definition = {
                "term": term,
                "url": term_url,
                "source": "Investopedia",
                "definition": content[:500] + "..." if len(content) > 500 else content,
                "full_content": content
            }
            
            # Add structured data if available
            if structured_data:
                definition.update(structured_data)
            
            # Store in cache
            self.definitions_cache[term] = definition
            
            return definition
        
        except Exception as e:
            logger.error(f"Error fetching definition for {term}: {e}")
            return None
    
    def _search_dictionary(self, term: str) -> Optional[Dict]:
        """
        Search the Investopedia dictionary for a term
        
        Args:
            term (str): Term to search for
            
        Returns:
            dict: Definition data or None if not found
        """
        try:
            # Get the dictionary page
            response = requests.get(self.dictionary_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Could not access Investopedia dictionary: {response.status_code}")
                return None
            
            # Parse with BeautifulSoup to find matching terms
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all term links in the dictionary
            term_links = soup.select('a[href^="/terms/"]')
            
            # Look for matching terms
            for link in term_links:
                link_text = link.text.lower()
                if term in link_text or link_text in term:
                    # Found a match, get the URL
                    term_url = "https://www.investopedia.com" + link['href']
                    
                    # Fetch the term page
                    term_response = requests.get(term_url, timeout=10)
                    
                    if term_response.status_code == 200:
                        # Use trafilatura to extract clean content
                        content = trafilatura.extract(term_response.text)
                        
                        if content:
                            definition = {
                                "term": link.text,
                                "url": term_url,
                                "source": "Investopedia",
                                "definition": content[:500] + "..." if len(content) > 500 else content,
                                "full_content": content
                            }
                            
                            # Try to extract structured data
                            structured_data = self._extract_structured_data(term_response.text)
                            if structured_data:
                                definition.update(structured_data)
                            
                            # Store in cache
                            self.definitions_cache[term] = definition
                            
                            return definition
            
            logger.info(f"No matching term found in dictionary for: {term}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching dictionary for {term}: {e}")
            return None
    
    def _extract_structured_data(self, html_content: str) -> Optional[Dict]:
        """
        Extract structured data from the HTML content
        
        Args:
            html_content (str): HTML content to parse
            
        Returns:
            dict: Structured data or None if not available
        """
        try:
            # Look for JSON-LD structured data
            match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
            
            if match:
                json_data = match.group(1)
                data = json.loads(json_data)
                
                structured = {}
                
                # Extract relevant fields
                if '@type' in data and data['@type'] == 'Article':
                    if 'headline' in data:
                        structured['headline'] = data['headline']
                    
                    if 'description' in data:
                        structured['short_definition'] = data['description']
                    
                    if 'author' in data:
                        if isinstance(data['author'], list) and len(data['author']) > 0:
                            structured['author'] = data['author'][0].get('name', '')
                        elif isinstance(data['author'], dict):
                            structured['author'] = data['author'].get('name', '')
                
                return structured if structured else None
            
            return None
        
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return None
    
    def search_terms(self, query: str, limit: int = 5) -> list:
        """
        Search for terms related to a query
        
        Args:
            query (str): The search query
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of matching term dictionaries
        """
        # This would ideally call an Investopedia search API
        # As a fallback, we'll return some common financial terms related to the query
        
        # For insurance terms
        insurance_terms = {
            'insurance': ['premium', 'deductible', 'policy', 'claim', 'coverage', 'underwriting', 'risk', 'liability'],
            'health': ['health insurance', 'copay', 'coinsurance', 'hmo', 'ppo', 'medicare', 'preexisting condition'],
            'property': ['property insurance', 'homeowners insurance', 'renters insurance', 'flood insurance', 'actuarial'],
            'life': ['life insurance', 'term life', 'whole life', 'beneficiary', 'death benefit', 'cash value'],
            'auto': ['auto insurance', 'comprehensive coverage', 'collision coverage', 'liability coverage', 'no-fault'],
            'finance': ['bond', 'stock', 'mutual fund', 'etf', 'retirement', 'ira', '401k', 'dividend', 'interest rate'],
            'tax': ['tax deduction', 'tax credit', 'exemption', 'withholding', 'capital gains', 'agi', 'taxable income']
        }
        
        # Normalize query
        query = query.lower().strip()
        
        # Find matching categories
        results = []
        for category, terms in insurance_terms.items():
            if query in category or category in query:
                for term in terms:
                    if len(results) < limit:
                        results.append({"term": term, "category": category})
        
        # If no category matches, check individual terms
        if not results:
            for category, terms in insurance_terms.items():
                for term in terms:
                    if query in term or term in query:
                        if len(results) < limit:
                            results.append({"term": term, "category": category})
        
        return results
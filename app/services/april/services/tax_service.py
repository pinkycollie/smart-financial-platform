import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app import db
from app.services.april.api_client import AprilAPIClient
from app.services.april.models import TaxDocument, AprilTransaction
from app.services.accessibility.mux_client import MuxClient

logger = logging.getLogger(__name__)

class TaxService:
    """Service for working with April's 'The Filer' tax filing functionality"""
    
    def __init__(self):
        self.api_client = AprilAPIClient()
        self.mux_client = MuxClient()
    
    def submit_tax_documents(self, user_id: int, tax_year: int, documents: List[TaxDocument]) -> Dict[str, Any]:
        """
        Submit tax documents to April for processing
        
        Args:
            user_id: User identifier
            tax_year: Tax year for the documents
            documents: List of tax document objects
        
        Returns:
            Dictionary with filing status and details
        """
        try:
            # Format documents for April API
            formatted_docs = []
            for doc in documents:
                formatted_docs.append({
                    'document_type': doc.document_type,
                    'document_data': doc.document_data,
                })
            
            # Call April API
            response = self.api_client.submit_tax_documents(user_id, tax_year, formatted_docs)
            
            # Update document statuses in database
            filing_id = response.get('filing_id')
            for doc in documents:
                doc.external_id = filing_id
                doc.status = 'processing'
            
            db.session.commit()
            
            return {
                'success': True,
                'filing_id': filing_id,
                'status': 'processing',
                'asl_video_id': self._get_asl_instruction_video('tax_filing_submitted')
            }
            
        except Exception as e:
            logger.error(f"Error submitting tax documents: {str(e)}")
            
            # Update document statuses to error
            for doc in documents:
                doc.status = 'error'
            
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'asl_video_id': self._get_asl_instruction_video('tax_filing_error')
            }
    
    def get_filing_status(self, user_id: int, filing_id: str) -> Dict[str, Any]:
        """
        Get the status of a tax filing
        
        Args:
            user_id: User identifier
            filing_id: April filing identifier
        
        Returns:
            Dictionary with filing status and details
        """
        try:
            response = self.api_client.get_tax_filing_status(user_id, filing_id)
            
            status = response.get('status', 'unknown')
            
            # Update document statuses in database
            documents = TaxDocument.query.filter_by(
                user_id=user_id,
                external_id=filing_id
            ).all()
            
            for doc in documents:
                doc.status = status
            
            db.session.commit()
            
            return {
                'success': True,
                'filing_id': filing_id,
                'status': status,
                'details': response.get('details', {}),
                'asl_video_id': self._get_asl_instruction_video(f'tax_filing_{status}')
            }
            
        except Exception as e:
            logger.error(f"Error getting filing status: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'asl_video_id': self._get_asl_instruction_video('tax_filing_status_error')
            }

    def save_tax_document(self, user_id: int, document_type: str, document_data: Dict[str, Any], 
                         year: int) -> Optional[TaxDocument]:
        """
        Save a tax document to the database
        
        Args:
            user_id: User identifier
            document_type: Type of document (W2, 1099, etc.)
            document_data: Document data in JSON format
            year: Tax year for the document
        
        Returns:
            Created TaxDocument object or None if error
        """
        try:
            document = TaxDocument(
                user_id=user_id,
                document_type=document_type,
                document_data=document_data,
                year=year,
                status='pending'
            )
            
            db.session.add(document)
            db.session.commit()
            
            return document
        
        except Exception as e:
            logger.error(f"Error saving tax document: {str(e)}")
            db.session.rollback()
            return None
    
    def _get_asl_instruction_video(self, context: str) -> Optional[str]:
        """
        Get the appropriate ASL instruction video ID for the given context
        
        Args:
            context: The context for the instruction video
        
        Returns:
            Mux video ID or None if not found
        """
        # Map contexts to video IDs
        video_map = {
            'tax_filing_submitted': 'tax_filing_confirmation',
            'tax_filing_processing': 'tax_filing_in_progress',
            'tax_filing_completed': 'tax_filing_success',
            'tax_filing_error': 'tax_filing_error',
            'tax_filing_status_error': 'system_error'
        }
        
        # Get the predefined video ID or use a default
        video_key = video_map.get(context, 'general_instructions')
        
        try:
            # This would normally query the Mux API for the video ID
            # For now, we'll return a placeholder
            return f"mux_video_{video_key}"
        except Exception as e:
            logger.error(f"Error getting ASL instruction video: {str(e)}")
            return None

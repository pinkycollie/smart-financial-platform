import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from models import TaxDocument, User
from simple_app import db
from services.april.api_client import AprilAPIClient

logger = logging.getLogger(__name__)

class TaxService:
    """Service for tax document filing and management using April's Filer"""
    
    def __init__(self):
        """Initialize the tax service"""
        self.april_client = AprilAPIClient()
        logger.info("Tax service initialized")
    
    def submit_tax_document(self, user_id: int, document_data: Dict[str, Any]) -> TaxDocument:
        """
        Submit a tax document to April's Filer service
        
        Args:
            user_id: User identifier
            document_data: Tax document data including type, year, etc.
            
        Returns:
            Created TaxDocument instance
        """
        # Create local record
        tax_document = TaxDocument(
            user_id=user_id,
            document_type=document_data.get('document_type'),
            document_data=document_data,
            year=document_data.get('tax_year'),
            status='pending'
        )
        
        try:
            # Add to database
            db.session.add(tax_document)
            db.session.commit()
            
            # Submit to April API
            response = self.april_client.submit_tax_documents(
                user_id=user_id,
                tax_year=document_data.get('tax_year'),
                documents={document_data.get('document_type'): document_data}
            )
            
            # Update local record with external ID
            tax_document.external_id = response.get('filing_id')
            tax_document.status = 'processed'
            db.session.commit()
            
            logger.info(f"Successfully submitted tax document for user {user_id}")
            return tax_document
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to submit tax document: {str(e)}")
            
            # Update document status to error if it was created
            if tax_document.id:
                tax_document.status = 'error'
                db.session.commit()
                
            raise
    
    def get_user_tax_documents(self, user_id: int, year: Optional[int] = None) -> List[TaxDocument]:
        """
        Get all tax documents for a user, optionally filtered by year
        
        Args:
            user_id: User identifier
            year: Optional tax year filter
            
        Returns:
            List of TaxDocument instances
        """
        query = TaxDocument.query.filter_by(user_id=user_id)
        
        if year:
            query = query.filter_by(year=year)
            
        return query.order_by(TaxDocument.created_at.desc()).all()
    
    def get_tax_filing_status(self, document_id: int) -> Dict[str, Any]:
        """
        Get the status of a tax filing from April
        
        Args:
            document_id: Tax document identifier
            
        Returns:
            Dictionary with filing status details
        """
        # Retrieve document
        document = TaxDocument.query.get_or_404(document_id)
        
        # Get status from April if we have an external ID
        if document.external_id:
            try:
                status = self.april_client.get_tax_filing_status(
                    user_id=document.user_id,
                    filing_id=document.external_id
                )
                
                # Update local status
                document.status = status.get('status', document.status)
                db.session.commit()
                
                return status
            except Exception as e:
                logger.error(f"Failed to get tax filing status: {str(e)}")
                return {'status': document.status, 'error': str(e)}
        
        return {'status': document.status}
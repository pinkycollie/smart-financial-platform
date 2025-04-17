"""
Revenue management service for DEAF FIRST platform resellers.
Handles revenue tracking, commission calculations, and billing management.
"""

import os
import csv
import json
from datetime import datetime, timedelta
from flask import current_app
from simple_app import db
from models_reseller import Reseller, SubReseller, ResellerRevenue
from models_licensing import Licensee, LicenseeBillingHistory

class RevenueManagementService:
    """
    Service for managing revenue, commissions, and billing for resellers.
    """
    
    def __init__(self, app_config=None):
        """Initialize revenue management service with optional configuration"""
        self.app_config = app_config or {}
        self.reports_folder = self.app_config.get('REPORTS_FOLDER', 'reports/revenue')
        
        # Ensure reports directory exists
        os.makedirs(self.reports_folder, exist_ok=True)
    
    def record_transaction(self, reseller_id, amount, transaction_type, licensee_id=None, sub_reseller_id=None, **kwargs):
        """
        Record a revenue transaction for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            amount (float): Transaction amount
            transaction_type (str): Transaction type (new_license, renewal, upgrade, etc.)
            licensee_id (int, optional): Licensee ID
            sub_reseller_id (int, optional): Sub-reseller ID
            **kwargs: Additional transaction properties
            
        Returns:
            ResellerRevenue: The created transaction record
        """
        # Calculate commission based on reseller tier
        reseller = Reseller.query.get(reseller_id)
        if not reseller:
            raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        commission_rate = reseller.commission_rate
        
        # If through sub-reseller, adjust commission
        if sub_reseller_id:
            sub_reseller = SubReseller.query.get(sub_reseller_id)
            if not sub_reseller or sub_reseller.parent_reseller_id != reseller_id:
                raise ValueError(f"Invalid sub-reseller ID {sub_reseller_id}")
            
            # Sub-reseller gets a portion of the commission
            sub_commission_rate = sub_reseller.commission_rate
            # Parent reseller gets reduced commission
            commission_rate = commission_rate - sub_commission_rate
        
        # Calculate commission amount
        commission_amount = (amount * commission_rate) / 100
        
        # Create transaction record
        transaction = ResellerRevenue(
            reseller_id=reseller_id,
            sub_reseller_id=sub_reseller_id,
            licensee_id=licensee_id,
            amount=amount,
            commission_amount=commission_amount,
            transaction_type=transaction_type,
            payment_status=kwargs.get('payment_status', 'pending'),
            payment_method=kwargs.get('payment_method'),
            transaction_id=kwargs.get('transaction_id'),
            notes=kwargs.get('notes')
        )
        
        # Update with any additional properties
        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        db.session.add(transaction)
        db.session.commit()
        
        return transaction
    
    def record_licensee_billing(self, licensee_id, amount, billing_date=None, **kwargs):
        """
        Record a billing transaction for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            amount (float): Billing amount
            billing_date (datetime, optional): Billing date
            **kwargs: Additional properties
            
        Returns:
            LicenseeBillingHistory: The created billing record
        """
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Default to today if no date provided
        if billing_date is None:
            billing_date = datetime.utcnow().date()
        
        # Calculate period start/end based on billing cycle
        period_start = billing_date
        
        if licensee.billing_cycle == 'monthly':
            period_end = (datetime.combine(billing_date, datetime.min.time()) + timedelta(days=30)).date()
        elif licensee.billing_cycle == 'quarterly':
            period_end = (datetime.combine(billing_date, datetime.min.time()) + timedelta(days=90)).date()
        elif licensee.billing_cycle == 'annually':
            period_end = (datetime.combine(billing_date, datetime.min.time()) + timedelta(days=365)).date()
        else:
            period_end = (datetime.combine(billing_date, datetime.min.time()) + timedelta(days=30)).date()
        
        # Create billing record
        billing = LicenseeBillingHistory(
            licensee_id=licensee_id,
            amount=amount,
            billing_date=billing_date,
            payment_status=kwargs.get('payment_status', 'pending'),
            payment_method=kwargs.get('payment_method'),
            transaction_id=kwargs.get('transaction_id'),
            invoice_number=kwargs.get('invoice_number', self._generate_invoice_number(licensee_id)),
            period_start=period_start,
            period_end=period_end
        )
        
        # Add to database
        db.session.add(billing)
        
        # Record reseller revenue transaction if licensee has a reseller
        if licensee.reseller_id:
            # Create reseller revenue record
            self.record_transaction(
                reseller_id=licensee.reseller_id,
                amount=amount,
                transaction_type='licensee_billing',
                licensee_id=licensee_id,
                sub_reseller_id=licensee.sub_reseller_id,
                payment_status=kwargs.get('payment_status', 'pending'),
                payment_method=kwargs.get('payment_method'),
                transaction_id=kwargs.get('transaction_id'),
                notes=f"Licensee billing: {licensee.company_name}"
            )
        
        db.session.commit()
        
        return billing
    
    def get_reseller_revenue(self, reseller_id, start_date=None, end_date=None, transaction_type=None):
        """
        Get revenue data for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date
            transaction_type (str, optional): Filter by transaction type
            
        Returns:
            dict: Revenue data
        """
        # Build query
        query = ResellerRevenue.query.filter_by(reseller_id=reseller_id)
        
        if start_date:
            query = query.filter(ResellerRevenue.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(ResellerRevenue.transaction_date <= end_date)
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        # Execute query
        transactions = query.all()
        
        # Calculate totals
        total_revenue = sum(t.amount for t in transactions)
        total_commission = sum(t.commission_amount for t in transactions)
        
        # Group by transaction type
        by_type = {}
        for t in transactions:
            if t.transaction_type not in by_type:
                by_type[t.transaction_type] = {
                    'count': 0,
                    'amount': 0,
                    'commission': 0
                }
            
            by_type[t.transaction_type]['count'] += 1
            by_type[t.transaction_type]['amount'] += t.amount
            by_type[t.transaction_type]['commission'] += t.commission_amount
        
        # Group by sub-reseller
        by_sub_reseller = {}
        for t in transactions:
            if t.sub_reseller_id:
                if t.sub_reseller_id not in by_sub_reseller:
                    sub_reseller = SubReseller.query.get(t.sub_reseller_id)
                    by_sub_reseller[t.sub_reseller_id] = {
                        'id': t.sub_reseller_id,
                        'name': sub_reseller.company_name if sub_reseller else f"Sub-reseller {t.sub_reseller_id}",
                        'count': 0,
                        'amount': 0,
                        'commission': 0
                    }
                
                by_sub_reseller[t.sub_reseller_id]['count'] += 1
                by_sub_reseller[t.sub_reseller_id]['amount'] += t.amount
                by_sub_reseller[t.sub_reseller_id]['commission'] += t.commission_amount
        
        # Group by month (for time series)
        by_month = {}
        for t in transactions:
            month_key = t.transaction_date.strftime("%Y-%m")
            
            if month_key not in by_month:
                by_month[month_key] = {
                    'count': 0,
                    'amount': 0,
                    'commission': 0
                }
            
            by_month[month_key]['count'] += 1
            by_month[month_key]['amount'] += t.amount
            by_month[month_key]['commission'] += t.commission_amount
        
        # Return compiled data
        return {
            'total_transactions': len(transactions),
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'by_type': by_type,
            'by_sub_reseller': list(by_sub_reseller.values()),
            'by_month': [{'month': k, **v} for k, v in by_month.items()],
            'transactions': [self._format_transaction(t) for t in transactions[-10:]]  # Last 10 transactions
        }
    
    def get_sub_reseller_revenue(self, sub_reseller_id, start_date=None, end_date=None, transaction_type=None):
        """
        Get revenue data for a sub-reseller.
        
        Args:
            sub_reseller_id (int): Sub-reseller ID
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date
            transaction_type (str, optional): Filter by transaction type
            
        Returns:
            dict: Revenue data
        """
        # Build query
        query = ResellerRevenue.query.filter_by(sub_reseller_id=sub_reseller_id)
        
        if start_date:
            query = query.filter(ResellerRevenue.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(ResellerRevenue.transaction_date <= end_date)
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        # Execute query
        transactions = query.all()
        
        # Calculate sub-reseller commission
        sub_reseller = SubReseller.query.get(sub_reseller_id)
        if not sub_reseller:
            raise ValueError(f"Sub-reseller with ID {sub_reseller_id} not found")
        
        sub_commission_rate = sub_reseller.commission_rate
        
        # Calculate totals
        total_revenue = sum(t.amount for t in transactions)
        # Sub-reseller commission is a portion of the transaction amount
        total_commission = sum((t.amount * sub_commission_rate) / 100 for t in transactions)
        
        # Return compiled data
        return {
            'total_transactions': len(transactions),
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'commission_rate': sub_commission_rate,
            'transactions': [self._format_transaction(t) for t in transactions[-10:]]  # Last 10 transactions
        }
    
    def generate_reseller_revenue_report(self, reseller_id, start_date=None, end_date=None, format='csv'):
        """
        Generate a revenue report for a reseller.
        
        Args:
            reseller_id (int): Reseller ID
            start_date (datetime, optional): Start date
            end_date (datetime, optional): End date
            format (str): Report format (csv, json)
            
        Returns:
            str: Report file path
        """
        # Get reseller
        reseller = Reseller.query.get(reseller_id)
        if not reseller:
            raise ValueError(f"Reseller with ID {reseller_id} not found")
        
        # Default dates
        if not start_date:
            # Default to first day of current month
            now = datetime.utcnow()
            start_date = datetime(now.year, now.month, 1)
        
        if not end_date:
            # Default to today
            end_date = datetime.utcnow()
        
        # Get revenue data
        query = ResellerRevenue.query.filter_by(reseller_id=reseller_id)
        query = query.filter(ResellerRevenue.transaction_date >= start_date, 
                            ResellerRevenue.transaction_date <= end_date)
        transactions = query.all()
        
        # Create report directory if it doesn't exist
        reseller_report_dir = os.path.join(self.reports_folder, str(reseller_id))
        os.makedirs(reseller_report_dir, exist_ok=True)
        
        # Generate filename
        period = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
        filename = f"revenue_report_{reseller_id}_{period}.{format}"
        file_path = os.path.join(reseller_report_dir, filename)
        
        if format == 'csv':
            # Generate CSV report
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['Transaction Date', 'Type', 'Amount', 'Commission', 
                            'Licensee', 'Sub-Reseller', 'Status', 'Transaction ID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for t in transactions:
                    licensee = Licensee.query.get(t.licensee_id) if t.licensee_id else None
                    sub_reseller = SubReseller.query.get(t.sub_reseller_id) if t.sub_reseller_id else None
                    
                    writer.writerow({
                        'Transaction Date': t.transaction_date.strftime('%Y-%m-%d'),
                        'Type': t.transaction_type,
                        'Amount': f"${t.amount:.2f}",
                        'Commission': f"${t.commission_amount:.2f}",
                        'Licensee': licensee.company_name if licensee else 'N/A',
                        'Sub-Reseller': sub_reseller.company_name if sub_reseller else 'N/A',
                        'Status': t.payment_status,
                        'Transaction ID': t.transaction_id or 'N/A'
                    })
        
        elif format == 'json':
            # Generate JSON report
            data = {
                'reseller': {
                    'id': reseller.id,
                    'company_name': reseller.company_name
                },
                'period': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                'transactions': [self._format_transaction(t, include_details=True) for t in transactions],
                'summary': {
                    'total_transactions': len(transactions),
                    'total_revenue': sum(t.amount for t in transactions),
                    'total_commission': sum(t.commission_amount for t in transactions)
                }
            }
            
            with open(file_path, 'w') as jsonfile:
                json.dump(data, jsonfile, indent=2)
        
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        return file_path
    
    def generate_invoice(self, licensee_id, billing_id=None):
        """
        Generate an invoice for a licensee.
        
        Args:
            licensee_id (int): Licensee ID
            billing_id (int, optional): Specific billing ID
            
        Returns:
            dict: Invoice data
        """
        # Get licensee
        licensee = Licensee.query.get(licensee_id)
        if not licensee:
            raise ValueError(f"Licensee with ID {licensee_id} not found")
        
        # Get billing record
        if billing_id:
            billing = LicenseeBillingHistory.query.get(billing_id)
            if not billing or billing.licensee_id != licensee_id:
                raise ValueError(f"Invalid billing ID {billing_id} for licensee {licensee_id}")
        else:
            # Get most recent billing
            billing = LicenseeBillingHistory.query.filter_by(licensee_id=licensee_id).order_by(
                LicenseeBillingHistory.billing_date.desc()).first()
            
            if not billing:
                raise ValueError(f"No billing records found for licensee {licensee_id}")
        
        # Generate invoice data
        invoice = {
            'invoice_number': billing.invoice_number,
            'date': billing.billing_date.strftime('%Y-%m-%d'),
            'due_date': (billing.billing_date + timedelta(days=15)).strftime('%Y-%m-%d'),
            'licensee': {
                'id': licensee.id,
                'company_name': licensee.company_name,
                'contact_name': licensee.contact_name,
                'contact_email': licensee.contact_email,
                'contact_phone': licensee.contact_phone
            },
            'vendor': {
                'name': 'MBTQ GROUP',
                'address': '123 Main St, Austin, TX 78701',
                'email': 'billing@deaffirst.com',
                'website': 'https://deaffirst.com'
            },
            'items': [
                {
                    'description': f"DEAF FIRST Platform - {licensee.license_tier.capitalize()} License",
                    'period': f"{billing.period_start.strftime('%Y-%m-%d')} to {billing.period_end.strftime('%Y-%m-%d')}",
                    'amount': billing.amount
                }
            ],
            'totals': {
                'subtotal': billing.amount,
                'tax': 0.00,  # No tax for digital services
                'total': billing.amount
            },
            'status': billing.payment_status,
            'payment_method': billing.payment_method,
            'transaction_id': billing.transaction_id,
            'notes': "Thank you for using DEAF FIRST Platform!"
        }
        
        # If reseller exists, add reseller info
        if licensee.reseller_id:
            reseller = Reseller.query.get(licensee.reseller_id)
            if reseller:
                invoice['vendor'] = {
                    'name': reseller.company_name,
                    'address': reseller.address or 'N/A',
                    'email': reseller.contact_email,
                    'website': reseller.get_portal_url()
                }
        
        return invoice
    
    def process_monthly_billing(self):
        """
        Process monthly billing for all licensees.
        
        Returns:
            dict: Billing results
        """
        today = datetime.utcnow().date()
        
        # Find licensees due for billing
        licensees = Licensee.query.filter(
            Licensee.status == 'active',
            Licensee.next_billing_date <= today
        ).all()
        
        results = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'total_billed': 0.0,
            'details': []
        }
        
        for licensee in licensees:
            try:
                # Record billing
                billing = self.record_licensee_billing(
                    licensee_id=licensee.id,
                    amount=licensee.billing_amount,
                    billing_date=today,
                    payment_status='pending'  # In a real system, would integrate with payment processor
                )
                
                # Update next billing date
                if licensee.billing_cycle == 'monthly':
                    next_date = today + timedelta(days=30)
                elif licensee.billing_cycle == 'quarterly':
                    next_date = today + timedelta(days=90)
                elif licensee.billing_cycle == 'annually':
                    next_date = today + timedelta(days=365)
                else:
                    next_date = today + timedelta(days=30)
                
                licensee.next_billing_date = next_date
                db.session.commit()
                
                results['succeeded'] += 1
                results['total_billed'] += licensee.billing_amount
                results['details'].append({
                    'licensee_id': licensee.id,
                    'company_name': licensee.company_name,
                    'amount': licensee.billing_amount,
                    'invoice_number': billing.invoice_number,
                    'status': 'success'
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'licensee_id': licensee.id,
                    'company_name': licensee.company_name,
                    'amount': licensee.billing_amount,
                    'status': 'failed',
                    'error': str(e)
                })
            
            results['processed'] += 1
        
        return results
    
    def _generate_invoice_number(self, licensee_id):
        """Generate a unique invoice number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
        return f"INV-{licensee_id}-{timestamp}"
    
    def _format_transaction(self, transaction, include_details=False):
        """Format a transaction for API response."""
        data = {
            'id': transaction.id,
            'date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'type': transaction.transaction_type,
            'amount': transaction.amount,
            'commission': transaction.commission_amount,
            'status': transaction.payment_status
        }
        
        if include_details:
            # Add licensee info if available
            if transaction.licensee_id:
                licensee = Licensee.query.get(transaction.licensee_id)
                if licensee:
                    data['licensee'] = {
                        'id': licensee.id,
                        'company_name': licensee.company_name
                    }
            
            # Add sub-reseller info if available
            if transaction.sub_reseller_id:
                sub_reseller = SubReseller.query.get(transaction.sub_reseller_id)
                if sub_reseller:
                    data['sub_reseller'] = {
                        'id': sub_reseller.id,
                        'company_name': sub_reseller.company_name
                    }
            
            # Add payment details
            data['payment'] = {
                'method': transaction.payment_method,
                'transaction_id': transaction.transaction_id,
                'notes': transaction.notes
            }
        
        return data

# Initialize a single instance to be used application-wide
revenue_management_service = RevenueManagementService()
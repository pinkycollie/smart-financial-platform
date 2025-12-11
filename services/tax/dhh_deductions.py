"""
Tax Service - DHH-Specific Deductions

This module handles tax-related calculations with a focus on
Deaf and Hard of Hearing specific deductions.
"""

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal


class DHHDeductionCalculator:
    """Calculate DHH-specific tax deductions."""
    
    # IRS-recognized DHH-related deduction categories
    INTERPRETER_FEE_CATEGORY = "work_related_interpreter_fees"
    MEDICAL_EXPENSE_CATEGORY = "medical_expenses"
    SPECIALIZED_EQUIPMENT_CATEGORY = "specialized_equipment"
    
    def __init__(self):
        self.deductions = {}
    
    def calculate_interpreter_fees(self, fees: List[Dict[str, float]]) -> Decimal:
        """
        Calculate deductible interpreter fees.
        
        Args:
            fees: List of interpreter fee records with 'amount' and 'purpose' keys
            
        Returns:
            Total deductible interpreter fees
        """
        total = Decimal('0.00')
        
        for fee in fees:
            # Work-related interpreter fees are fully deductible
            if fee.get('purpose') == 'work_related':
                total += Decimal(str(fee.get('amount', 0)))
        
        return total
    
    def calculate_medical_expenses(self, expenses: List[Dict[str, float]]) -> Decimal:
        """
        Calculate deductible medical expenses related to hearing.
        
        Args:
            expenses: List of medical expense records
            
        Returns:
            Total deductible medical expenses
        """
        total = Decimal('0.00')
        
        # DHH-related medical expenses
        dhh_categories = [
            'hearing_aids',
            'cochlear_implants',
            'batteries',
            'repairs',
            'maintenance',
            'audiologist_visits'
        ]
        
        for expense in expenses:
            if expense.get('category') in dhh_categories:
                total += Decimal(str(expense.get('amount', 0)))
        
        return total
    
    def calculate_equipment_deductions(self, equipment: List[Dict[str, float]]) -> Decimal:
        """
        Calculate deductions for specialized equipment.
        
        Args:
            equipment: List of equipment purchases
            
        Returns:
            Total deductible equipment costs
        """
        total = Decimal('0.00')
        
        # Deductible equipment types
        deductible_equipment = [
            'captioned_phone',
            'alerting_devices',
            'assistive_listening_devices',
            'amplified_telephone',
            'TTY_device',
            'video_phone'
        ]
        
        for item in equipment:
            if item.get('type') in deductible_equipment:
                total += Decimal(str(item.get('amount', 0)))
        
        return total
    
    def calculate_total_dhh_deductions(
        self, 
        interpreter_fees: List[Dict[str, float]] = None,
        medical_expenses: List[Dict[str, float]] = None,
        equipment: List[Dict[str, float]] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate all DHH-specific deductions.
        
        Args:
            interpreter_fees: List of interpreter fee records
            medical_expenses: List of medical expense records
            equipment: List of equipment purchases
            
        Returns:
            Dictionary with breakdown of deductions
        """
        deductions = {
            'interpreter_fees': Decimal('0.00'),
            'medical_expenses': Decimal('0.00'),
            'specialized_equipment': Decimal('0.00'),
            'total': Decimal('0.00')
        }
        
        if interpreter_fees:
            deductions['interpreter_fees'] = self.calculate_interpreter_fees(interpreter_fees)
        
        if medical_expenses:
            deductions['medical_expenses'] = self.calculate_medical_expenses(medical_expenses)
        
        if equipment:
            deductions['specialized_equipment'] = self.calculate_equipment_deductions(equipment)
        
        deductions['total'] = (
            deductions['interpreter_fees'] +
            deductions['medical_expenses'] +
            deductions['specialized_equipment']
        )
        
        return deductions


class TaxRefundEstimator:
    """Estimate tax refunds including DHH-specific deductions."""
    
    def __init__(self):
        self.dhh_calculator = DHHDeductionCalculator()
    
    def estimate_refund(
        self,
        income_w2: float,
        deductions_standard: float = 12950.00,
        special_deduction_amount: float = 0.00,
        withholding: float = 0.00
    ) -> Dict[str, Union[float, bool, str, Dict[str, float]]]:
        """
        Estimate tax refund.
        
        Args:
            income_w2: W-2 income
            deductions_standard: Standard deduction (2023: $12,950 single)
            special_deduction_amount: DHH-specific deductions
            withholding: Amount withheld from paychecks
            
        Returns:
            Dictionary with refund estimate and details
        """
        # Calculate adjusted gross income
        agi = Decimal(str(income_w2))
        
        # Total deductions
        total_deductions = Decimal(str(deductions_standard)) + Decimal(str(special_deduction_amount))
        
        # Taxable income
        taxable_income = max(agi - total_deductions, Decimal('0.00'))
        
        # Simplified tax calculation (actual would use tax brackets)
        # This is a placeholder - real implementation would use IRS tax tables
        tax_rate = Decimal('0.12')  # Example 12% bracket
        calculated_tax = taxable_income * tax_rate
        
        # Refund is withholding minus calculated tax
        refund = Decimal(str(withholding)) - calculated_tax
        
        return {
            'estimated_refund': float(refund),
            'dhh_benefit_applied': special_deduction_amount > 0,
            'notes': self._generate_notes(special_deduction_amount),
            'breakdown': {
                'agi': float(agi),
                'total_deductions': float(total_deductions),
                'taxable_income': float(taxable_income),
                'calculated_tax': float(calculated_tax),
                'withholding': withholding
            }
        }
    
    def _generate_notes(self, special_deduction_amount: float) -> str:
        """Generate personalized notes for the refund estimate."""
        if special_deduction_amount > 0:
            return (
                f"DHH-specific deductions of ${special_deduction_amount:.2f} have been applied. "
                "Please retain all receipts for interpreter fees, medical expenses, and "
                "specialized equipment for documentation during e-filing."
            )
        else:
            return (
                "No DHH-specific deductions were applied. Consider documenting interpreter fees, "
                "hearing aid expenses, and specialized equipment purchases for potential deductions."
            )

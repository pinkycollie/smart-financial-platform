"""
Unit tests for DHH API endpoints

Tests the OpenAPI specification compliance and DHH-specific features.
"""

import unittest
import json
from decimal import Decimal

# Import services directly for unit testing
from services.client.intake_service import DHHClientIntakeService, NeedsAssessmentService
from services.tax.dhh_deductions import DHHDeductionCalculator, TaxRefundEstimator
from services.insurance.dhh_riders import DHHInsuranceRider, InsuranceQuoteGenerator


class TestDHHClientIntakeService(unittest.TestCase):
    """Test DHH client intake functionality."""
    
    def setUp(self):
        self.service = DHHClientIntakeService()
    
    def test_register_client_success(self):
        """Test successful client registration."""
        result = self.service.register_client(
            full_name="John Doe",
            email="john.doe@example.com",
            communication_preference="ASL_Interpreter",
            interpreter_needed=True,
            interpreter_contracting_status="Pending"
        )
        
        self.assertIn('client_id', result)
        self.assertEqual(result['status'], 'Registered')
        self.assertIn('next_step', result)
    
    def test_register_client_invalid_preference(self):
        """Test client registration with invalid communication preference."""
        with self.assertRaises(ValueError):
            self.service.register_client(
                full_name="Jane Smith",
                email="jane@example.com",
                communication_preference="Invalid_Preference"
            )
    
    def test_communication_preferences(self):
        """Test all valid communication preferences."""
        preferences = ["ASL_Interpreter", "VRI", "Captioned_Phone", "Text_Only"]
        
        for pref in preferences:
            result = self.service.register_client(
                full_name="Test User",
                email="test@example.com",
                communication_preference=pref
            )
            self.assertEqual(result['status'], 'Registered')


class TestNeedsAssessmentService(unittest.TestCase):
    """Test needs assessment functionality."""
    
    def setUp(self):
        self.service = NeedsAssessmentService()
    
    def test_submit_assessment_success(self):
        """Test successful assessment submission."""
        result = self.service.submit_assessment(
            client_id="TEST-001",
            hearing_aid_claims_history="Annual replacements for past 5 years",
            benefit_program_eligibility=["SSDI", "Vocational_Rehab"],
            tax_deductions_focus=["Work_Related_Interpreter_Fees", "Medical_Expenses"]
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('assessment_id', result)
        self.assertIn('recommendations', result)
    
    def test_assessment_invalid_benefit_program(self):
        """Test assessment with invalid benefit program."""
        with self.assertRaises(ValueError):
            self.service.submit_assessment(
                client_id="TEST-002",
                hearing_aid_claims_history="None",
                benefit_program_eligibility=["Invalid_Program"]
            )


class TestDHHDeductionCalculator(unittest.TestCase):
    """Test DHH deduction calculation."""
    
    def setUp(self):
        self.calculator = DHHDeductionCalculator()
    
    def test_calculate_interpreter_fees(self):
        """Test interpreter fee calculation."""
        fees = [
            {'amount': 500.00, 'purpose': 'work_related'},
            {'amount': 300.00, 'purpose': 'work_related'},
            {'amount': 200.00, 'purpose': 'personal'}
        ]
        
        result = self.calculator.calculate_interpreter_fees(fees)
        
        # Only work-related fees should be counted
        self.assertEqual(result, Decimal('800.00'))
    
    def test_calculate_medical_expenses(self):
        """Test medical expense calculation."""
        expenses = [
            {'amount': 5000.00, 'category': 'hearing_aids'},
            {'amount': 150.00, 'category': 'batteries'},
            {'amount': 100.00, 'category': 'other'}
        ]
        
        result = self.calculator.calculate_medical_expenses(expenses)
        
        self.assertEqual(result, Decimal('5150.00'))
    
    def test_calculate_equipment_deductions(self):
        """Test equipment deduction calculation."""
        equipment = [
            {'amount': 800.00, 'type': 'captioned_phone'},
            {'amount': 200.00, 'type': 'alerting_devices'},
            {'amount': 500.00, 'type': 'non_deductible'}
        ]
        
        result = self.calculator.calculate_equipment_deductions(equipment)
        
        self.assertEqual(result, Decimal('1000.00'))
    
    def test_calculate_total_dhh_deductions(self):
        """Test total DHH deduction calculation."""
        interpreter_fees = [{'amount': 500.00, 'purpose': 'work_related'}]
        medical_expenses = [{'amount': 2000.00, 'category': 'hearing_aids'}]
        equipment = [{'amount': 300.00, 'type': 'TTY_device'}]
        
        result = self.calculator.calculate_total_dhh_deductions(
            interpreter_fees=interpreter_fees,
            medical_expenses=medical_expenses,
            equipment=equipment
        )
        
        self.assertEqual(result['interpreter_fees'], Decimal('500.00'))
        self.assertEqual(result['medical_expenses'], Decimal('2000.00'))
        self.assertEqual(result['specialized_equipment'], Decimal('300.00'))
        self.assertEqual(result['total'], Decimal('2800.00'))


class TestTaxRefundEstimator(unittest.TestCase):
    """Test tax refund estimation."""
    
    def setUp(self):
        self.estimator = TaxRefundEstimator()
    
    def test_estimate_refund_with_dhh_deductions(self):
        """Test refund estimation with DHH deductions."""
        result = self.estimator.estimate_refund(
            income_w2=65000.00,
            deductions_standard=12950.00,
            special_deduction_amount=3500.00,
            withholding=8000.00
        )
        
        self.assertIn('estimated_refund', result)
        self.assertTrue(result['dhh_benefit_applied'])
        self.assertIn('notes', result)
        self.assertIn('breakdown', result)
    
    def test_estimate_refund_without_dhh_deductions(self):
        """Test refund estimation without DHH deductions."""
        result = self.estimator.estimate_refund(
            income_w2=50000.00,
            deductions_standard=12950.00,
            special_deduction_amount=0.00,
            withholding=6000.00
        )
        
        self.assertFalse(result['dhh_benefit_applied'])


class TestDHHInsuranceRider(unittest.TestCase):
    """Test DHH insurance rider functionality."""
    
    def setUp(self):
        self.rider_manager = DHHInsuranceRider()
    
    def test_calculate_rider_premium(self):
        """Test rider premium calculation."""
        riders = [
            DHHInsuranceRider.HEARING_AID_COVERAGE,
            DHHInsuranceRider.INTERPRETER_SERVICE
        ]
        
        result = self.rider_manager.calculate_rider_premium(riders)
        
        expected = Decimal('25.00') + Decimal('15.00')
        self.assertEqual(result, expected)
    
    def test_get_rider_details(self):
        """Test rider details retrieval."""
        details = self.rider_manager.get_rider_details(
            DHHInsuranceRider.HEARING_AID_COVERAGE
        )
        
        self.assertIn('name', details)
        self.assertIn('description', details)
        self.assertIn('monthly_cost', details)
        self.assertIn('coverage_limit', details)


class TestInsuranceQuoteGenerator(unittest.TestCase):
    """Test insurance quote generation."""
    
    def setUp(self):
        self.generator = InsuranceQuoteGenerator()
    
    def test_generate_quote_health_insurance(self):
        """Test health insurance quote generation."""
        result = self.generator.generate_quote(
            insurance_type='Health',
            hearing_aid_coverage_required=True,
            interpreter_service_rider=True,
            assistive_equipment_rider=False,
            current_policy_exception_summary='Previous policy excluded hearing aids'
        )
        
        self.assertIn('quote_id', result)
        self.assertIn('estimated_premium_range', result)
        self.assertEqual(result['insurance_type'], 'Health')
        self.assertEqual(len(result['selected_riders']), 2)
    
    def test_generate_quote_life_insurance(self):
        """Test life insurance quote generation."""
        result = self.generator.generate_quote(
            insurance_type='Life',
            hearing_aid_coverage_required=False
        )
        
        self.assertEqual(result['insurance_type'], 'Life')
        self.assertIn('quote_id', result)


if __name__ == '__main__':
    unittest.main()

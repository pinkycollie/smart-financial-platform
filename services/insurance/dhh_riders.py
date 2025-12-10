"""
Insurance Service - DHH-Specific Riders

This module handles insurance quote generation with DHH-specific coverage options.
"""

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime
import uuid


class DHHInsuranceRider:
    """Manage DHH-specific insurance riders."""
    
    # Standard DHH riders
    HEARING_AID_COVERAGE = "hearing_aid_coverage"
    INTERPRETER_SERVICE = "interpreter_service_rider"
    ASSISTIVE_EQUIPMENT = "assistive_equipment_rider"
    
    RIDER_COSTS = {
        HEARING_AID_COVERAGE: Decimal('25.00'),  # Monthly premium add-on
        INTERPRETER_SERVICE: Decimal('15.00'),
        ASSISTIVE_EQUIPMENT: Decimal('10.00')
    }
    
    def __init__(self):
        self.selected_riders = []
    
    def calculate_rider_premium(self, riders: List[str]) -> Decimal:
        """
        Calculate total premium for selected riders.
        
        Args:
            riders: List of rider identifiers
            
        Returns:
            Total monthly premium for riders
        """
        total = Decimal('0.00')
        
        for rider in riders:
            if rider in self.RIDER_COSTS:
                total += self.RIDER_COSTS[rider]
        
        return total
    
    def get_rider_details(self, rider_type: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific rider.
        
        Args:
            rider_type: Type of rider
            
        Returns:
            Dictionary with rider details
        """
        rider_info = {
            self.HEARING_AID_COVERAGE: {
                'name': 'Hearing Aid Coverage',
                'description': 'Covers replacement and repair of hearing aids up to $5,000 per year',
                'monthly_cost': float(self.RIDER_COSTS[self.HEARING_AID_COVERAGE]),
                'coverage_limit': 5000.00,
                'deductible': 100.00
            },
            self.INTERPRETER_SERVICE: {
                'name': 'Interpreter Service Rider',
                'description': 'Covers interpreter fees for medical appointments',
                'monthly_cost': float(self.RIDER_COSTS[self.INTERPRETER_SERVICE]),
                'coverage_limit': 2000.00,
                'sessions_per_year': 24
            },
            self.ASSISTIVE_EQUIPMENT: {
                'name': 'Assistive Equipment Rider',
                'description': 'Covers specialized equipment like captioned phones, alerting devices',
                'monthly_cost': float(self.RIDER_COSTS[self.ASSISTIVE_EQUIPMENT]),
                'coverage_limit': 1500.00,
                'deductible': 50.00
            }
        }
        
        return rider_info.get(rider_type, {})


class InsuranceQuoteGenerator:
    """Generate insurance quotes with DHH-specific options."""
    
    BASE_PREMIUMS = {
        'Health': Decimal('350.00'),
        'Life': Decimal('85.00'),
        'Home': Decimal('150.00'),
        'Auto': Decimal('125.00')
    }
    
    def __init__(self):
        self.rider_manager = DHHInsuranceRider()
    
    def generate_quote(
        self,
        insurance_type: str,
        hearing_aid_coverage_required: bool = False,
        interpreter_service_rider: bool = False,
        assistive_equipment_rider: bool = False,
        current_policy_exception_summary: str = ""
    ) -> Dict[str, Union[str, float, List[Dict[str, Any]]]]:
        """
        Generate an insurance quote with DHH-specific riders.
        
        Args:
            insurance_type: Type of insurance (Health, Life, Home, Auto)
            hearing_aid_coverage_required: Include hearing aid coverage
            interpreter_service_rider: Include interpreter service rider
            assistive_equipment_rider: Include assistive equipment rider
            current_policy_exception_summary: Summary of current policy exceptions
            
        Returns:
            Dictionary with quote details
        """
        # Generate unique quote ID
        quote_id = f"Q-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Base premium for insurance type
        base_premium = self.BASE_PREMIUMS.get(insurance_type, Decimal('100.00'))
        
        # Calculate rider costs
        selected_riders = []
        if hearing_aid_coverage_required:
            selected_riders.append(DHHInsuranceRider.HEARING_AID_COVERAGE)
        if interpreter_service_rider:
            selected_riders.append(DHHInsuranceRider.INTERPRETER_SERVICE)
        if assistive_equipment_rider:
            selected_riders.append(DHHInsuranceRider.ASSISTIVE_EQUIPMENT)
        
        rider_premium = self.rider_manager.calculate_rider_premium(selected_riders)
        
        # Total monthly premium
        total_premium = base_premium + rider_premium
        
        # Generate premium range (±10%)
        min_premium = total_premium * Decimal('0.90')
        max_premium = total_premium * Decimal('1.10')
        
        return {
            'quote_id': quote_id,
            'insurance_type': insurance_type,
            'estimated_premium_range': f"${float(min_premium):.2f} - ${float(max_premium):.2f}/month",
            'base_premium': float(base_premium),
            'rider_premium': float(rider_premium),
            'total_monthly_premium': float(total_premium),
            'selected_riders': [
                self.rider_manager.get_rider_details(rider) 
                for rider in selected_riders
            ],
            'notes': self._generate_quote_notes(
                insurance_type, 
                selected_riders, 
                current_policy_exception_summary
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_quote_notes(
        self, 
        insurance_type: str, 
        riders: List[str], 
        exceptions: str
    ) -> str:
        """Generate personalized notes for the quote."""
        notes = [
            f"{insurance_type} insurance quote with DHH-specific coverage options."
        ]
        
        if riders:
            notes.append(
                f"Quote includes {len(riders)} DHH-specific rider(s) for enhanced coverage."
            )
        
        if exceptions:
            notes.append(
                f"Previous policy exceptions noted: {exceptions}. "
                "This quote addresses those exceptions."
            )
        
        notes.append(
            "Final premium will be determined after underwriting review. "
            "All DHH-specific riders are optional and can be customized."
        )
        
        return " ".join(notes)

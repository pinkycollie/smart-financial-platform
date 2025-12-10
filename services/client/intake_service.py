"""
Client Service - DHH Client Intake

This module handles client intake and needs assessment for DHH clients.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid


class DHHClientIntakeService:
    """Manage DHH client intake and registration."""
    
    COMMUNICATION_PREFERENCES = [
        "ASL_Interpreter",
        "VRI",
        "Captioned_Phone",
        "Text_Only"
    ]
    
    INTERPRETER_STATUSES = [
        "Pending",
        "Approved",
        "Self-Provided",
        "Not_Required"
    ]
    
    def __init__(self):
        self.clients = {}
    
    def register_client(
        self,
        full_name: str,
        email: str,
        communication_preference: str,
        interpreter_needed: bool = False,
        interpreter_contracting_status: str = "Not_Required"
    ) -> Dict[str, any]:
        """
        Register a new DHH client.
        
        Args:
            full_name: Client's full legal name
            email: Client's email address
            communication_preference: Preferred communication method
            interpreter_needed: Whether client needs an interpreter
            interpreter_contracting_status: Status of interpreter arrangement
            
        Returns:
            Client confirmation with ID and next steps
        """
        # Validate communication preference
        if communication_preference not in self.COMMUNICATION_PREFERENCES:
            raise ValueError(
                f"Invalid communication preference. Must be one of: {self.COMMUNICATION_PREFERENCES}"
            )
        
        # Generate unique client ID
        client_id = f"DHH-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8]}"
        
        # Store client information
        self.clients[client_id] = {
            'client_id': client_id,
            'full_name': full_name,
            'email': email,
            'communication_preference': communication_preference,
            'interpreter_needed': interpreter_needed,
            'interpreter_contracting_status': interpreter_contracting_status,
            'registration_date': datetime.now().isoformat(),
            'status': 'Active'
        }
        
        # Determine next step
        next_step = self._determine_next_step(
            communication_preference, 
            interpreter_needed
        )
        
        return {
            'client_id': client_id,
            'status': 'Registered',
            'next_step': next_step
        }
    
    def _determine_next_step(
        self, 
        communication_preference: str, 
        interpreter_needed: bool
    ) -> str:
        """Determine the next step in the client onboarding process."""
        if interpreter_needed and communication_preference == "ASL_Interpreter":
            return "Schedule interpreter for consultation, then proceed to Needs Assessment"
        elif communication_preference == "VRI":
            return "Set up VRI access, then proceed to Needs Assessment"
        else:
            return "Proceed to Needs Assessment"


class NeedsAssessmentService:
    """Manage DHH-specific needs assessments."""
    
    BENEFIT_PROGRAMS = [
        "SSI",
        "SSDI",
        "Vocational_Rehab",
        "Other"
    ]
    
    TAX_DEDUCTION_CATEGORIES = [
        "Medical_Expenses",
        "Work_Related_Interpreter_Fees",
        "Specialized_Equipment"
    ]
    
    def __init__(self):
        self.assessments = {}
    
    def submit_assessment(
        self,
        client_id: str,
        hearing_aid_claims_history: str,
        benefit_program_eligibility: List[str] = None,
        tax_deductions_focus: List[str] = None
    ) -> Dict[str, any]:
        """
        Submit a needs assessment for a DHH client.
        
        Args:
            client_id: Unique client identifier
            hearing_aid_claims_history: Summary of hearing aid claims
            benefit_program_eligibility: List of relevant benefit programs
            tax_deductions_focus: List of potential tax deductions
            
        Returns:
            Assessment confirmation with recommendations
        """
        # Validate benefit programs
        if benefit_program_eligibility:
            for program in benefit_program_eligibility:
                if program not in self.BENEFIT_PROGRAMS:
                    raise ValueError(
                        f"Invalid benefit program: {program}. "
                        f"Must be one of: {self.BENEFIT_PROGRAMS}"
                    )
        
        # Validate tax deduction categories
        if tax_deductions_focus:
            for category in tax_deductions_focus:
                if category not in self.TAX_DEDUCTION_CATEGORIES:
                    raise ValueError(
                        f"Invalid tax deduction category: {category}. "
                        f"Must be one of: {self.TAX_DEDUCTION_CATEGORIES}"
                    )
        
        # Generate assessment ID
        assessment_id = f"ASSESS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Store assessment
        self.assessments[assessment_id] = {
            'assessment_id': assessment_id,
            'client_id': client_id,
            'hearing_aid_claims_history': hearing_aid_claims_history,
            'benefit_program_eligibility': benefit_program_eligibility or [],
            'tax_deductions_focus': tax_deductions_focus or [],
            'assessment_date': datetime.now().isoformat(),
            'status': 'Completed'
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            hearing_aid_claims_history,
            benefit_program_eligibility,
            tax_deductions_focus
        )
        
        return {
            'status': 'success',
            'message': 'Assessment successfully recorded and analyzed.',
            'assessment_id': assessment_id,
            'recommendations': recommendations
        }
    
    def _generate_recommendations(
        self,
        hearing_aid_claims: str,
        benefit_programs: List[str],
        tax_deductions: List[str]
    ) -> List[str]:
        """Generate personalized recommendations based on assessment."""
        recommendations = []
        
        # Hearing aid recommendations
        if hearing_aid_claims:
            recommendations.append(
                "Consider documenting all hearing aid expenses for potential tax deductions. "
                "Medical expenses exceeding 7.5% of AGI may be deductible."
            )
            recommendations.append(
                "Review insurance options with hearing aid coverage riders to reduce out-of-pocket costs."
            )
        
        # Benefit program recommendations
        if benefit_programs:
            if "SSDI" in benefit_programs or "SSI" in benefit_programs:
                recommendations.append(
                    "You may qualify for additional tax credits. Consult with a tax professional about "
                    "Earned Income Tax Credit (EITC) and disability-related deductions."
                )
        
        # Tax deduction recommendations
        if tax_deductions:
            if "Work_Related_Interpreter_Fees" in tax_deductions:
                recommendations.append(
                    "Work-related interpreter fees are fully deductible as a business expense. "
                    "Keep detailed records of all interpreter services."
                )
            
            if "Specialized_Equipment" in tax_deductions:
                recommendations.append(
                    "Assistive technology and specialized equipment may qualify for deductions. "
                    "Document purchases of captioned phones, alerting devices, and communication aids."
                )
        
        # General recommendations
        recommendations.append(
            "Schedule a consultation with our DHH-specialized financial advisor to explore all available opportunities."
        )
        
        return recommendations

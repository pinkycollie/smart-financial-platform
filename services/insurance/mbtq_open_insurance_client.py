"""
MBTQ Group LLC Open Insurance API Integration
Comprehensive insurance services client based on Open Insurance API standard
Provides accessible insurance services for the deaf and hard-of-hearing community
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class MBTQOpenInsuranceClient:
    """
    MBTQ Group LLC Open Insurance API Client
    Provides comprehensive insurance services with accessibility features
    """
    
    def __init__(self):
        self.base_url = os.environ.get('OPEN_INSURANCE_URL', 'http://localhost:8081')
        self.api_key = os.environ.get('OPEN_INSURANCE_API_KEY')
        self.session = requests.Session()
        
        if not self.api_key:
            logger.warning("Open Insurance API key not configured. Using demo mode for MBTQ Group LLC.")
        else:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-MBTQ-Client': 'MBTQ-Group-LLC'
            })
    
    # ============================================================================
    # INSURANCE ENTITY MANAGEMENT
    # ============================================================================
    
    def create_insurance_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new insurance entity for MBTQ Group LLC"""
        try:
            # Enhance entity data with MBTQ accessibility features
            enhanced_data = {
                **entity_data,
                'mbtq_group_llc': True,
                'accessibility_features': {
                    'asl_support': True,
                    'visual_communication': True,
                    'deaf_friendly_services': True
                },
                'created_by': 'MBTQ Group LLC Platform'
            }
            
            response = self.session.post(f'{self.base_url}/insurance-entity', json=enhanced_data)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'entity_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ insurance entity created successfully',
                'accessibility_enabled': True
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"MBTQ insurance entity creation failed: {e}")
            return {'status': 'error', 'message': 'Entity creation failed'}
    
    def get_insurance_entity(self, entity_id: str) -> Dict[str, Any]:
        """Retrieve insurance entity with MBTQ accessibility enhancements"""
        try:
            response = self.session.get(f'{self.base_url}/insurance-entity/{entity_id}')
            response.raise_for_status()
            
            entity_data = response.json()
            # Add MBTQ accessibility information if available
            if entity_data:
                entity_data['mbtq_accessibility_score'] = self._calculate_accessibility_score(entity_data)
                entity_data['asl_support_available'] = True
            
            return {
                'status': 'success',
                'data': entity_data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get MBTQ insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity retrieval failed'}
    
    def update_insurance_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update insurance entity with MBTQ enhancements"""
        try:
            response = self.session.put(f'{self.base_url}/insurance-entity/{entity_id}', json=entity_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'MBTQ insurance entity updated successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Update MBTQ insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity update failed'}
    
    def delete_insurance_entity(self, entity_id: str) -> Dict[str, Any]:
        """Delete insurance entity"""
        try:
            response = self.session.delete(f'{self.base_url}/insurance-entity/{entity_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'message': 'MBTQ insurance entity deleted successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Delete MBTQ insurance entity failed: {e}")
            return {'status': 'error', 'message': 'Entity deletion failed'}
    
    # ============================================================================
    # COMMERCIAL INSURANCE SERVICES
    # ============================================================================
    
    def create_commercial_policy(self, commercial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create commercial insurance policy for MBTQ business clients"""
        try:
            # Add MBTQ business accessibility features
            enhanced_data = {
                **commercial_data,
                'mbtq_business_features': {
                    'deaf_employee_coverage': True,
                    'accessibility_equipment_coverage': True,
                    'interpreter_services_coverage': True,
                    'assistive_technology_coverage': True
                }
            }
            
            response = self.session.post(f'{self.base_url}/commercial', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'policy_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ commercial policy created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ commercial policy failed: {e}")
            return {'status': 'error', 'message': 'Commercial policy creation failed'}
    
    def get_commercial_policy(self, policy_id: str) -> Dict[str, Any]:
        """Retrieve commercial policy"""
        try:
            response = self.session.get(f'{self.base_url}/commercial/{policy_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get MBTQ commercial policy failed: {e}")
            return {'status': 'error', 'message': 'Commercial policy retrieval failed'}
    
    # ============================================================================
    # INSURANCE PRODUCTS MANAGEMENT
    # ============================================================================
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create insurance product with MBTQ accessibility features"""
        try:
            # Enhance product with MBTQ-specific features
            enhanced_data = {
                **product_data,
                'mbtq_accessibility_features': {
                    'asl_explanations_available': True,
                    'visual_policy_documents': True,
                    'deaf_customer_discounts': True,
                    'accessibility_equipment_coverage': True
                }
            }
            
            response = self.session.post(f'{self.base_url}/product', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'product_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ insurance product created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ insurance product failed: {e}")
            return {'status': 'error', 'message': 'Product creation failed'}
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Retrieve insurance product"""
        try:
            response = self.session.get(f'{self.base_url}/product/{product_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get MBTQ insurance product failed: {e}")
            return {'status': 'error', 'message': 'Product retrieval failed'}
    
    def get_mbtq_specialized_products(self) -> Dict[str, Any]:
        """Get comprehensive insurance products specialized for MBTQ Group LLC deaf community clients"""
        try:
            specialized_products = {
                'deaf_community_health_plus': {
                    'product_id': 'mbtq_health_001',
                    'name': 'Deaf Community Health Insurance Plus',
                    'category': 'health',
                    'base_coverage': {
                        'medical': 'comprehensive',
                        'dental': 'included',
                        'vision': 'enhanced_for_visual_dependency'
                    },
                    'deaf_specific_coverage': {
                        'hearing_aids': {
                            'coverage_limit': 6000,  # per ear, per 3 years
                            'replacement_coverage': True,
                            'upgrade_coverage': 'partial',
                            'repair_coverage': True,
                            'loss_protection': True
                        },
                        'cochlear_implants': {
                            'surgical_coverage': 'full',
                            'device_coverage': 50000,
                            'mapping_sessions': 'unlimited_first_year',
                            'replacement_coverage': True,
                            'upgrade_path': 'covered_after_5_years'
                        },
                        'assistive_technology': {
                            'vibrating_alarms': 1500,
                            'visual_alert_systems': 2500,
                            'communication_devices': 3000,
                            'smartphone_apps': 500,
                            'home_alert_systems': 5000
                        },
                        'occupational_therapy': {
                            'signing_related_injuries': 'full_coverage',
                            'ergonomic_assessments': 'annual',
                            'preventive_care': 'enhanced'
                        },
                        'mental_health': {
                            'deaf_culturally_competent_therapists': True,
                            'asl_therapy_sessions': 'covered',
                            'isolation_support': 'specialized_programs'
                        }
                    }
                },
                'interpreter_professional_insurance': {
                    'product_id': 'mbtq_interp_001',
                    'name': 'Professional Sign Language Interpreter Insurance',
                    'category': 'professional_liability',
                    'coverage_areas': {
                        'repetitive_strain_protection': {
                            'carpal_tunnel_syndrome': 'full_medical_plus_income',
                            'tendinitis_treatment': 'comprehensive',
                            'ergonomic_workplace_setup': 'covered',
                            'preventive_care': 'mandatory_annual_screenings'
                        },
                        'professional_liability': {
                            'interpretation_errors': 'e_and_o_coverage',
                            'confidentiality_breaches': 'cyber_liability',
                            'client_injury_claims': 'general_liability'
                        },
                        'income_protection': {
                            'hand_arm_injury_disability': 'specialized_short_term',
                            'voice_loss_coverage': 'for_voice_interpreters',
                            'covid_exposure_quarantine': 'income_replacement'
                        },
                        'equipment_coverage': {
                            'interpretation_equipment': 5000,
                            'professional_development': 2000,
                            'continuing_education': 'annual_allowance'
                        }
                    }
                },
                'deaf_property_insurance_enhanced': {
                    'product_id': 'mbtq_property_001',
                    'name': 'Deaf Homeowner\'s/Renter\'s Insurance Enhanced',
                    'category': 'property',
                    'enhanced_coverage': {
                        'accessibility_modifications': {
                            'visual_alert_systems': 'replacement_cost',
                            'vibrating_notification_systems': 'full_coverage',
                            'doorbell_light_systems': 'included',
                            'smoke_detector_bed_shakers': 'required_coverage'
                        },
                        'service_animal_protection': {
                            'hearing_dog_medical': 10000,
                            'service_animal_liability': 'enhanced',
                            'training_replacement_cost': 25000,
                            'temporary_care_coverage': 'during_owner_hospitalization'
                        },
                        'communication_equipment': {
                            'vp_video_phone_equipment': 2000,
                            'computer_communication_setup': 5000,
                            'internet_backup_systems': 1500,
                            'emergency_communication_devices': 3000
                        },
                        'liability_enhancements': {
                            'interpreter_services_liability': 'when_hosting',
                            'accessibility_compliance': 'ada_protection',
                            'guest_injury_deaf_modifications': 'enhanced_coverage'
                        }
                    }
                },
                'deaf_auto_insurance_plus': {
                    'product_id': 'mbtq_auto_001',
                    'name': 'Deaf Community Auto Insurance Plus',
                    'category': 'auto',
                    'specialized_features': {
                        'vehicle_modifications': {
                            'visual_alert_systems': 2500,
                            'vibrating_notification_seats': 1500,
                            'enhanced_mirror_systems': 1000,
                            'emergency_communication_devices': 800
                        },
                        'accident_coverage': {
                            'interpreter_services': 'at_accident_scene',
                            'communication_assistance': 'police_hospital_interaction',
                            'legal_interpreter_coverage': 'court_proceedings'
                        },
                        'roadside_assistance': {
                            'text_based_communication': True,
                            'visual_location_sharing': True,
                            'asl_video_support': 'available_24_7'
                        }
                    }
                },
                'deaf_life_disability_insurance': {
                    'product_id': 'mbtq_life_001',
                    'name': 'Life and Disability Insurance for Deaf Community',
                    'category': 'life_disability',
                    'coverage_enhancements': {
                        'disability_definitions': {
                            'hand_arm_functionality': 'partial_disability_trigger',
                            'signing_ability_loss': 'occupational_disability',
                            'combined_sensory_loss': 'enhanced_benefits'
                        },
                        'income_replacement': {
                            'interpreter_income_loss': 'specialized_calculation',
                            'deaf_professional_accommodations': 'workplace_modification_costs',
                            'retraining_benefits': 'career_transition_support'
                        },
                        'life_insurance_enhancements': {
                            'service_animal_care_provision': 'beneficiary_support',
                            'accessibility_modification_funds': 'survivor_benefits',
                            'interpreter_funeral_services': 'covered_expense'
                        }
                    }
                }
            
            return {
                'status': 'success',
                'data': specialized_products,
                'total_products': len(specialized_products),
                'mbtq_exclusive': True,
                'market_analysis': {
                    'target_market_size': '500,000+ deaf/hard-of-hearing individuals in US',
                    'secondary_market': '60,000+ professional interpreters',
                    'revenue_projection_year_1': '$5M premium volume',
                    'competitive_advantages': [
                        'Cultural competency',
                        'Technology integration', 
                        'Specialized coverage',
                        'Deaf-friendly provider network',
                        'ASL-accessible claims process'
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Get MBTQ specialized products failed: {e}")
            return {'status': 'error', 'message': 'Specialized products retrieval failed'}
    
    # ============================================================================
    # COVERAGE MANAGEMENT
    # ============================================================================
    
    def create_coverage(self, coverage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create insurance coverage with MBTQ accessibility options"""
        try:
            response = self.session.post(f'{self.base_url}/coverage', json=coverage_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'coverage_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ insurance coverage created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ coverage failed: {e}")
            return {'status': 'error', 'message': 'Coverage creation failed'}
    
    def get_coverage(self, coverage_id: str) -> Dict[str, Any]:
        """Retrieve insurance coverage"""
        try:
            response = self.session.get(f'{self.base_url}/coverage/{coverage_id}')
            response.raise_for_status()
            return {
                'status': 'success',
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Get MBTQ coverage failed: {e}")
            return {'status': 'error', 'message': 'Coverage retrieval failed'}
    
    # ============================================================================
    # PERSONAL INSURANCE SERVICES
    # ============================================================================
    
    def create_personal_policy(self, personal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create personal insurance policy with MBTQ accessibility features"""
        try:
            # Enhance with MBTQ personal insurance features
            enhanced_data = {
                **personal_data,
                'mbtq_personal_features': {
                    'deaf_customer_profile': True,
                    'asl_claims_support': True,
                    'accessibility_coverage': True,
                    'communication_preferences': personal_data.get('communication_method', 'asl')
                }
            }
            
            response = self.session.post(f'{self.base_url}/personal', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'policy_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ personal policy created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ personal policy failed: {e}")
            return {'status': 'error', 'message': 'Personal policy creation failed'}
    
    # ============================================================================
    # DRIVER MANAGEMENT (Auto Insurance)
    # ============================================================================
    
    def create_driver_profile(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create driver profile with deaf-specific considerations"""
        try:
            # Add deaf driver safety features
            enhanced_data = {
                **driver_data,
                'deaf_driver_profile': {
                    'enhanced_visual_awareness': True,
                    'defensive_driving_certified': driver_data.get('defensive_driving', False),
                    'assistive_driving_equipment': driver_data.get('assistive_equipment', []),
                    'deaf_safe_driver_discount_eligible': True
                }
            }
            
            response = self.session.post(f'{self.base_url}/driver', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'driver_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ driver profile created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ driver profile failed: {e}")
            return {'status': 'error', 'message': 'Driver profile creation failed'}
    
    # ============================================================================
    # VEHICLE MANAGEMENT
    # ============================================================================
    
    def create_vehicle_profile(self, vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create vehicle profile with accessibility equipment coverage"""
        try:
            # Add accessibility equipment tracking
            enhanced_data = {
                **vehicle_data,
                'accessibility_equipment': {
                    'visual_alert_systems': vehicle_data.get('visual_alerts', []),
                    'vibrating_alerts': vehicle_data.get('vibrating_alerts', []),
                    'backup_cameras': vehicle_data.get('backup_camera', False),
                    'enhanced_mirrors': vehicle_data.get('enhanced_mirrors', False)
                }
            }
            
            response = self.session.post(f'{self.base_url}/vehicle', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'vehicle_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ vehicle profile created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ vehicle profile failed: {e}")
            return {'status': 'error', 'message': 'Vehicle profile creation failed'}
    
    # ============================================================================
    # BENEFICIARY MANAGEMENT
    # ============================================================================
    
    def create_beneficiary(self, beneficiary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create beneficiary with communication preferences"""
        try:
            # Add communication method tracking for beneficiaries
            enhanced_data = {
                **beneficiary_data,
                'communication_preferences': {
                    'preferred_method': beneficiary_data.get('communication_method', 'email'),
                    'asl_interpreter_needed': beneficiary_data.get('needs_interpreter', False),
                    'text_communication': beneficiary_data.get('text_preferred', True)
                }
            }
            
            response = self.session.post(f'{self.base_url}/beneficiary', json=enhanced_data)
            response.raise_for_status()
            return {
                'status': 'success',
                'beneficiary_id': response.headers.get('Location', '').split('/')[-1],
                'message': 'MBTQ beneficiary created successfully'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Create MBTQ beneficiary failed: {e}")
            return {'status': 'error', 'message': 'Beneficiary creation failed'}
    
    # ============================================================================
    # MBTQ GROUP LLC SPECIALIZED SERVICES
    # ============================================================================
    
    def calculate_deaf_community_premium(self, applicant_profile: Dict[str, Any], product_type: str) -> Dict[str, Any]:
        """Calculate premium pricing for MBTQ deaf community insurance products"""
        try:
            base_premium = self._calculate_base_premium(applicant_profile, product_type)
            
            risk_factors = {
                'positive_factors': {
                    'visual_alertness': -0.05,  # 5% discount for enhanced visual awareness
                    'defensive_driving': -0.10,  # Often better drivers due to visual focus
                    'health_conscious': -0.03,   # Often more health-aware due to medical needs
                    'visual_smoke_detectors': -0.05,
                    'vibrating_alarm_systems': -0.03,
                    'security_monitoring_with_visual_alerts': -0.07,
                    'emergency_text_alert_system': -0.02,
                    'accessibility_friendly_neighborhood': -0.04,
                    'deaf_safe_driver_certification': -0.06,
                    'assistive_driving_equipment': -0.03
                },
                'risk_considerations': {
                    'assistive_device_dependency': 0.02,
                    'specialized_medical_needs': 0.03,
                    'limited_provider_network': 0.01
                },
                'deaf_community_discounts': {
                    'group_enrollment': -0.15,
                    'preventive_care_participation': -0.08,
                    'deaf_organization_member': -0.05,
                    'interpreter_professional': -0.10,
                    'service_animal_owner': -0.03
                }
            }
            
            total_adjustment = 0
            applied_adjustments = []
            
            # Apply positive factors (discounts)
            for factor, discount in risk_factors['positive_factors'].items():
                if applicant_profile.get(factor, False):
                    total_adjustment += discount
                    applied_adjustments.append({
                        'factor': factor,
                        'type': 'discount',
                        'rate': abs(discount),
                        'amount': base_premium * abs(discount)
                    })
            
            # Apply risk considerations (increases)
            for factor, increase in risk_factors['risk_considerations'].items():
                if applicant_profile.get(factor, False):
                    total_adjustment += increase
                    applied_adjustments.append({
                        'factor': factor,
                        'type': 'surcharge',
                        'rate': increase,
                        'amount': base_premium * increase
                    })
            
            # Apply deaf community discounts
            for factor, discount in risk_factors['deaf_community_discounts'].items():
                if applicant_profile.get(factor, False):
                    total_adjustment += discount
                    applied_adjustments.append({
                        'factor': factor,
                        'type': 'community_discount',
                        'rate': abs(discount),
                        'amount': base_premium * abs(discount)
                    })
            
            # Cap total adjustment (max 25% discount or 10% increase)
            total_adjustment = max(min(total_adjustment, 0.10), -0.25)
            final_premium = base_premium * (1 + total_adjustment)
            
            return {
                'status': 'success',
                'product_type': product_type,
                'base_premium': base_premium,
                'total_adjustment_rate': total_adjustment,
                'total_adjustment_amount': base_premium * total_adjustment,
                'final_premium': final_premium,
                'applied_adjustments': applied_adjustments,
                'annual_cost': final_premium * 12,
                'annual_savings': max(0, (base_premium - final_premium) * 12),
                'mbtq_deaf_community_pricing': True,
                'payment_options': {
                    'monthly': final_premium,
                    'quarterly': final_premium * 3 * 0.98,  # 2% discount
                    'annual': final_premium * 12 * 0.95     # 5% discount
                }
            }
        except Exception as e:
            logger.error(f"Calculate MBTQ deaf community premium failed: {e}")
            return {'status': 'error', 'message': 'MBTQ deaf community premium calculation failed'}
    
    def get_mbtq_customer_dashboard(self, customer_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard for MBTQ insurance customers"""
        try:
            dashboard_data = {
                'customer_id': customer_id,
                'active_policies': [],
                'accessibility_features': {
                    'asl_support_enabled': True,
                    'visual_alerts_configured': True,
                    'text_communication_preferred': True
                },
                'claims_status': [],
                'premium_discounts': {
                    'total_annual_savings': 0,
                    'accessibility_discounts': []
                },
                'available_services': [
                    'ASL claims assistance',
                    'Visual policy documents',
                    'Accessibility equipment coverage',
                    'Deaf-friendly repair network'
                ],
                'next_steps': [
                    'Schedule ASL policy review',
                    'Update accessibility equipment inventory',
                    'Verify emergency contact preferences'
                ]
            }
            
            return {
                'status': 'success',
                'data': dashboard_data,
                'mbtq_services_active': True
            }
        except Exception as e:
            logger.error(f"Get MBTQ customer dashboard failed: {e}")
            return {'status': 'error', 'message': 'Customer dashboard retrieval failed'}
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _calculate_base_premium(self, applicant_profile: Dict[str, Any], product_type: str) -> float:
        """Calculate base premium before deaf community adjustments"""
        # Base premium calculation logic would typically involve actuarial tables
        # For demo purposes, using simplified base rates
        base_rates = {
            'health': 450.0,              # Monthly health insurance
            'auto': 125.0,                # Monthly auto insurance
            'property': 180.0,            # Monthly property insurance
            'professional_liability': 85.0, # Monthly professional liability
            'life_disability': 95.0       # Monthly life/disability insurance
        }
        
        base_premium = base_rates.get(product_type, 200.0)
        
        # Basic demographic adjustments
        age = applicant_profile.get('age', 35)
        if age < 25:
            base_premium *= 1.15  # Higher rate for younger drivers/clients
        elif age > 65:
            base_premium *= 1.25  # Higher rate for seniors
        
        # Coverage amount adjustments
        coverage_amount = applicant_profile.get('coverage_amount', 100000)
        if coverage_amount > 500000:
            base_premium *= 1.5
        elif coverage_amount > 250000:
            base_premium *= 1.25
        
        return base_premium
    
    def _calculate_accessibility_score(self, entity_data: Dict[str, Any]) -> float:
        """Calculate accessibility score for insurance entities"""
        score = 0.0
        max_score = 100.0
        
        # Check for various accessibility features
        if entity_data.get('asl_support'):
            score += 20
        if entity_data.get('visual_communication'):
            score += 15
        if entity_data.get('text_communication_available'):
            score += 10
        if entity_data.get('accessibility_equipment_coverage'):
            score += 25
        if entity_data.get('deaf_friendly_services'):
            score += 20
        if entity_data.get('interpreter_services'):
            score += 10
        
        return min(score, max_score)
    
    def get_api_health_status(self) -> Dict[str, Any]:
        """Check MBTQ Open Insurance API health"""
        try:
            response = self.session.get(f'{self.base_url}/health')
            return {
                'status': 'healthy',
                'mbtq_integration': 'active',
                'accessibility_services': 'available',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'mbtq_integration': 'unavailable'
            }


# Global client instance for MBTQ Group LLC
mbtq_open_insurance_client = MBTQOpenInsuranceClient()
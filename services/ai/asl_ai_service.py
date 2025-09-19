"""
MBTQ Group LLC Sign Language AI Service
Provides AI-powered ASL support, interpretation, and accessibility features
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
from openai import OpenAI

logger = logging.getLogger(__name__)

class ASLAIService:
    """Advanced Sign Language AI Service for MBTQ Group LLC"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured. ASL AI features will be limited.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.openai_api_key)
        
        self.asl_context = {
            'financial_terms': self._load_financial_asl_context(),
            'insurance_terms': self._load_insurance_asl_context(),
            'legal_terms': self._load_legal_asl_context()
        }
    
    def _load_financial_asl_context(self) -> Dict[str, str]:
        """Load financial terminology with ASL explanations"""
        return {
            'premium': 'The money you pay for insurance, signed like paying money regularly',
            'deductible': 'Amount you pay before insurance helps, shown as subtraction gesture',
            'coverage': 'Protection insurance gives you, signed like umbrella over yourself',
            'claim': 'Asking insurance for help when something happens, like requesting assistance',
            'policy': 'Your insurance contract, signed like holding important papers'
        }
    
    def _load_insurance_asl_context(self) -> Dict[str, str]:
        """Load insurance-specific ASL terminology"""
        return {
            'auto_insurance': 'Car protection, signed as driving motion with safety coverage',
            'health_insurance': 'Medical care protection, signed as health plus security',
            'life_insurance': 'Family protection when you die, signed as life plus giving',
            'disability_insurance': 'Income protection if you cannot work, signed as work plus support',
            'beneficiary': 'Person who gets insurance money, signed as receiving or inheriting'
        }
    
    def _load_legal_asl_context(self) -> Dict[str, str]:
        """Load legal terminology with ASL explanations"""
        return {
            'notary': 'Official witness for documents, signed as witnessing plus official stamp',
            'contract': 'Legal agreement, signed as two people agreeing and shaking hands',
            'liability': 'Legal responsibility, signed as burden or weight on shoulders',
            'settlement': 'Agreement to solve problem, signed as balance and agreement',
            'lawsuit': 'Court case, signed as fighting in court with judge deciding'
        }
    
    async def interpret_text_to_asl(self, text: str, context: str = 'general') -> Dict[str, Any]:
        """Convert text to ASL-friendly explanation"""
        if not self.client:
            return {'status': 'error', 'message': 'AI service not available'}
        
        try:
            # Get relevant context
            context_terms = self.asl_context.get(context, {})
            context_info = "\n".join([f"{term}: {explanation}" for term, explanation in context_terms.items()])
            
            prompt = f"""
            You are an expert ASL interpreter and deaf education specialist. Convert the following text into clear, visual, ASL-friendly explanations that deaf users can easily understand.

            Context terms for {context}:
            {context_info}

            Original text: {text}

            Please provide:
            1. Simple explanation in everyday language
            2. Visual description of how to sign key concepts
            3. ASL grammar structure (object-subject-verb when appropriate)
            4. Any important facial expressions or body language
            5. Cultural considerations for deaf community

            Respond in JSON format with these fields: simplified_text, signing_description, asl_grammar, facial_expressions, cultural_notes
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'original_text': text,
                'asl_interpretation': result,
                'context_used': context,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ASL interpretation failed: {e}")
            return {'status': 'error', 'message': 'Failed to interpret text to ASL'}
    
    async def analyze_sign_language_video(self, video_base64: str) -> Dict[str, Any]:
        """Analyze sign language video for accuracy and feedback"""
        if not self.client:
            return {'status': 'error', 'message': 'AI service not available'}
        
        try:
            prompt = """
            You are an ASL expert. Analyze this sign language video and provide:
            1. Recognition of signed words/phrases if visible
            2. Grammar feedback (ASL vs English structure)
            3. Clarity and fluency assessment
            4. Suggestions for improvement
            5. Cultural appropriateness feedback
            
            Respond in JSON format with: recognized_signs, grammar_feedback, fluency_score, improvements, cultural_notes
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:video/mp4;base64,{video_base64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'analysis': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sign language video analysis failed: {e}")
            return {'status': 'error', 'message': 'Failed to analyze sign language video'}
    
    async def generate_asl_lesson(self, topic: str, difficulty: str = 'beginner') -> Dict[str, Any]:
        """Generate ASL lesson content for specific topics"""
        if not self.client:
            return {'status': 'error', 'message': 'AI service not available'}
        
        try:
            prompt = f"""
            Create a comprehensive ASL lesson for "{topic}" at {difficulty} level.
            
            Include:
            1. Learning objectives
            2. Key vocabulary with signing descriptions
            3. Practice sentences in ASL grammar order
            4. Cultural context and usage
            5. Common mistakes to avoid
            6. Practice exercises
            7. Assessment criteria
            
            Make it engaging and respectful of deaf culture. Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'lesson': result,
                'topic': topic,
                'difficulty': difficulty,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"ASL lesson generation failed: {e}")
            return {'status': 'error', 'message': 'Failed to generate ASL lesson'}
    
    async def provide_real_time_support(self, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide real-time ASL support and guidance"""
        if not self.client:
            return {'status': 'error', 'message': 'AI service not available'}
        
        try:
            user_context = f"""
            User profile: {context.get('user_profile', 'Not specified')}
            Current page: {context.get('current_page', 'Unknown')}
            Accessibility needs: {context.get('accessibility_needs', 'ASL support')}
            Communication preference: {context.get('communication_method', 'Visual/ASL')}
            """
            
            prompt = f"""
            You are an AI assistant specialized in helping deaf and hard-of-hearing users navigate financial services.
            
            User context:
            {user_context}
            
            User message: {user_message}
            
            Provide helpful, clear responses that:
            1. Use simple, visual language
            2. Avoid complex financial jargon
            3. Offer ASL-friendly explanations
            4. Include visual or tactile alternatives when possible
            5. Are culturally appropriate for the deaf community
            
            Respond in JSON format with: response_text, asl_tips, visual_aids, next_steps, follow_up_questions
            """
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'status': 'success',
                'support_response': result,
                'user_message': user_message,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Real-time ASL support failed: {e}")
            return {'status': 'error', 'message': 'Failed to provide real-time support'}
    
    async def schedule_interpreter_session(self, session_details: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule an ASL interpreter session with AI pre-screening"""
        try:
            # Use AI to analyze the request and suggest optimal interpreter matching
            prompt = f"""
            Analyze this interpreter session request and provide recommendations:
            
            Session details: {json.dumps(session_details)}
            
            Provide:
            1. Session complexity assessment
            2. Recommended interpreter qualifications
            3. Estimated session duration
            4. Preparation materials needed
            5. Special accommodations required
            6. Follow-up requirements
            
            Respond in JSON format.
            """
            
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                
                ai_analysis = json.loads(response.choices[0].message.content)
            else:
                ai_analysis = {
                    "complexity": "standard",
                    "qualifications": "certified_asl_interpreter",
                    "duration": "60_minutes",
                    "materials": "standard_preparation",
                    "accommodations": "none_specified",
                    "follow_up": "session_summary"
                }
            
            # Create session record
            session_id = f"asl_session_{int(datetime.utcnow().timestamp())}"
            
            return {
                'status': 'success',
                'session_id': session_id,
                'ai_analysis': ai_analysis,
                'session_details': session_details,
                'booking_status': 'pending_confirmation',
                'next_steps': [
                    'Confirm interpreter availability',
                    'Send preparation materials',
                    'Set up video connection',
                    'Schedule reminder notifications'
                ]
            }
            
        except Exception as e:
            logger.error(f"Interpreter session scheduling failed: {e}")
            return {'status': 'error', 'message': 'Failed to schedule interpreter session'}
    
    def get_asl_emergency_phrases(self) -> Dict[str, Any]:
        """Get essential ASL phrases for emergency situations"""
        return {
            'status': 'success',
            'emergency_phrases': {
                'help': {
                    'description': 'Need immediate assistance',
                    'signing': 'Place right hand on left palm, lift both hands up urgently',
                    'context': 'Use when you need immediate help'
                },
                'emergency': {
                    'description': 'Serious emergency situation',
                    'signing': 'Shake both hands rapidly with urgent facial expression',
                    'context': 'Life-threatening or urgent medical situation'
                },
                'interpreter_needed': {
                    'description': 'Request for ASL interpreter',
                    'signing': 'Point to self, then make interpretation gesture (rotating hands)',
                    'context': 'When communication barrier exists'
                },
                'write_down': {
                    'description': 'Ask someone to write information',
                    'signing': 'Mime writing motion, point to paper/phone',
                    'context': 'When spoken communication is not working'
                },
                'call_relay': {
                    'description': 'Ask someone to call relay service',
                    'signing': 'Phone gesture + interpreter sign',
                    'context': 'When you need to make a phone call'
                }
            }
        }


# Global service instance
asl_ai_service = ASLAIService()
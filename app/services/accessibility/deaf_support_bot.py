import logging
from typing import Dict, Any, List, Optional
from app.services.accessibility.mux_client import MuxClient

logger = logging.getLogger(__name__)

class DeafSupportBot:
    """Bot service that provides ASL support for deaf users"""
    
    def __init__(self):
        self.mux_client = MuxClient()
        self.message_history = {}  # Store conversation history by user_id
    
    def get_support_response(self, user_id: int, message: str, context: str = None) -> Dict[str, Any]:
        """
        Get a support response for a user message
        
        Args:
            user_id: User identifier
            message: User message or query
            context: Optional context of the conversation
        
        Returns:
            Dictionary with support response including ASL video
        """
        try:
            # Store the message in conversation history
            if user_id not in self.message_history:
                self.message_history[user_id] = []
            
            self.message_history[user_id].append({
                'role': 'user',
                'message': message
            })
            
            # Determine the appropriate response
            response_data = self._generate_response(user_id, message, context)
            
            # Get an ASL video for the response
            video = self._get_asl_video_for_response(response_data['response_key'])
            
            # Store the bot response in conversation history
            self.message_history[user_id].append({
                'role': 'bot',
                'message': response_data['text']
            })
            
            return {
                'text': response_data['text'],
                'asl_video_id': video.get('playback_id'),
                'asl_video_url': video.get('playback_url'),
                'suggestions': response_data.get('suggestions', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting support response: {str(e)}")
            
            # Get a fallback video
            fallback = self.mux_client.get_fallback_video()
            
            return {
                'text': "I'm sorry, I encountered an error. Please try again later.",
                'asl_video_id': fallback.get('playback_id'),
                'asl_video_url': fallback.get('playback_url'),
                'suggestions': ['Start over', 'Contact support']
            }
    
    def create_asl_support_session(self, user_id: int, context: str = None) -> Dict[str, Any]:
        """
        Create a live ASL support session for a user
        
        Args:
            user_id: User identifier
            context: Optional context for the support session
        
        Returns:
            Dictionary with session details
        """
        try:
            # Create a Mux Space for the ASL session
            title = f"ASL Support Session for User {user_id}"
            if context:
                title += f" - {context}"
                
            space = self.mux_client.create_video_space(title)
            
            if not space:
                raise Exception("Failed to create video space")
            
            return {
                'success': True,
                'session_id': space.get('space_id'),
                'status': space.get('status'),
                'join_url': f"https://space.mux.com/{space.get('space_id')}"
            }
            
        except Exception as e:
            logger.error(f"Error creating ASL support session: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of message dictionaries
        """
        return self.message_history.get(user_id, [])
    
    def clear_conversation_history(self, user_id: int) -> None:
        """
        Clear conversation history for a user
        
        Args:
            user_id: User identifier
        """
        if user_id in self.message_history:
            self.message_history[user_id] = []
    
    def _generate_response(self, user_id: int, message: str, context: str = None) -> Dict[str, Any]:
        """
        Generate a response to the user message
        
        Args:
            user_id: User identifier
            message: User message
            context: Optional context
        
        Returns:
            Dictionary with response data
        """
        # Simple rule-based responses
        # In a real implementation, this could use a more sophisticated
        # natural language understanding system
        
        message_lower = message.lower()
        
        # Context-specific responses
        if context == 'tax_filing':
            if 'how' in message_lower and ('file' in message_lower or 'submit' in message_lower):
                return {
                    'text': "To file your taxes with April, first upload your W-2 and any other tax documents. The system will guide you through the process with ASL videos at each step.",
                    'response_key': 'tax_filing_instructions',
                    'suggestions': ['Upload W-2', 'What documents do I need?', 'Tax filing deadline']
                }
            elif 'documents' in message_lower or 'need' in message_lower:
                return {
                    'text': "For most tax filings, you'll need your W-2 from your employer, any 1099 forms for contract work, and documents showing deductions like mortgage interest or charitable donations.",
                    'response_key': 'tax_document_requirements',
                    'suggestions': ['Upload documents', 'How to find my W-2', "What's a 1099?"]
                }
        
        elif context == 'financial_profile':
            if 'profile' in message_lower or 'create' in message_lower:
                return {
                    'text': "Your financial profile helps April provide personalized recommendations. To create one, provide information about your income, investments, and financial goals.",
                    'response_key': 'create_financial_profile',
                    'suggestions': ['Start profile', 'Why is this useful?', 'Privacy policy']
                }
        
        # General responses
        if 'hello' in message_lower or 'hi' in message_lower:
            return {
                'text': "Hello! I'm April's ASL support assistant. How can I help you today?",
                'response_key': 'greeting',
                'suggestions': ['Tax filing help', 'Financial profile', 'Investment advice']
            }
        elif 'tax' in message_lower:
            return {
                'text': "April offers tax filing services designed to be accessible for deaf users. All instructions are available in ASL. Would you like to learn more about tax filing options?",
                'response_key': 'tax_information',
                'suggestions': ['Tax filing options', 'Tax deadlines', 'Required documents']
            }
        elif 'invest' in message_lower:
            return {
                'text': "April can provide investment recommendations based on your financial profile. These recommendations are explained in ASL to ensure you understand the opportunities.",
                'response_key': 'investment_information',
                'suggestions': ['Create financial profile', 'Types of investments', 'Risk tolerance']
            }
        elif 'asl' in message_lower or 'video' in message_lower:
            return {
                'text': "All of April's features are accessible through ASL videos. Each section of the platform has corresponding ASL explanations, and you can request live ASL support if needed.",
                'response_key': 'asl_support_information',
                'suggestions': ['Request live ASL', 'All ASL videos', 'Accessibility settings']
            }
        else:
            return {
                'text': "I'm here to help with April's financial services. You can ask about tax filing, financial profiles, investment recommendations, or ASL support options.",
                'response_key': 'general_help',
                'suggestions': ['Tax help', 'Financial profile', 'ASL support', 'Contact human']
            }
    
    def _get_asl_video_for_response(self, response_key: str) -> Dict[str, Any]:
        """
        Get an ASL video for a specific response
        
        Args:
            response_key: Key identifying the response
        
        Returns:
            Dictionary with video details
        """
        video = self.mux_client.get_asl_video(response_key)
        
        if not video:
            # If no specific video is found, return a fallback
            logger.warning(f"No ASL video found for response key: {response_key}")
            return self.mux_client.get_fallback_video()
        
        return video

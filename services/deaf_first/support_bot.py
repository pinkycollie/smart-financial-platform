import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from services.deaf_first.mux_client import MuxClient

logger = logging.getLogger(__name__)

class DeafFirstSupportBot:
    """Bot service that provides ASL support for Deaf users with financial questions"""
    
    def __init__(self):
        """Initialize the Deaf First support bot"""
        self.mux_client = MuxClient()
        self._conversation_histories = {}  # In-memory storage for conversation histories
        
        # Initialize response patterns for common financial questions
        self._load_response_patterns()
        
        logger.info("Deaf First support bot initialized")
    
    def _load_response_patterns(self):
        """Load response patterns from a file or define inline"""
        # In a production environment, these would be loaded from a database or file
        self.response_patterns = {
            'tax_filing': {
                'keywords': ['tax', 'filing', 'w2', '1099', 'deduction', 'refund', 'irs'],
                'video_keys': {
                    'general': 'tax_filing_overview',
                    'forms': 'tax_filing_forms',
                    'deductions': 'tax_filing_deductions',
                    'status': 'tax_filing_status'
                }
            },
            'financial_profile': {
                'keywords': ['profile', 'income', 'asset', 'investment', 'retirement'],
                'video_keys': {
                    'general': 'financial_profile_overview',
                    'income': 'financial_profile_income',
                    'investments': 'financial_profile_investments',
                    'retirement': 'financial_profile_retirement'
                }
            },
            'investment': {
                'keywords': ['stock', 'bond', 'fund', 'invest', 'portfolio', 'risk', 'return'],
                'video_keys': {
                    'general': 'investment_overview',
                    'stocks': 'investment_stocks',
                    'bonds': 'investment_bonds',
                    'funds': 'investment_funds',
                    'risk': 'investment_risk'
                }
            },
            'retirement': {
                'keywords': ['401k', 'ira', 'roth', 'pension', 'retire', 'saving'],
                'video_keys': {
                    'general': 'retirement_overview',
                    '401k': 'retirement_401k',
                    'ira': 'retirement_ira',
                    'planning': 'retirement_planning'
                }
            }
        }
    
    def get_support_response(self, user_id: int, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a support response for a user message
        
        Args:
            user_id: User identifier
            message: User message or query
            context: Optional context of the conversation
        
        Returns:
            Dictionary with support response including ASL video
        """
        # Store message in conversation history
        self._add_to_conversation_history(user_id, 'user', message)
        
        # Generate response
        response = self._generate_response(user_id, message, context)
        
        # Store response in conversation history
        self._add_to_conversation_history(user_id, 'bot', response['text'])
        
        return response
    
    def create_asl_support_session(self, user_id: int, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a live ASL support session for a user
        
        Args:
            user_id: User identifier
            context: Optional context for the support session
        
        Returns:
            Dictionary with session details
        """
        title = f"ASL Financial Support Session - User {user_id}"
        if context:
            title += f" - {context}"
            
        # Create a Mux Space for the support session
        space = self.mux_client.create_video_space(title)
        
        if not space:
            logger.error(f"Failed to create ASL support session for user {user_id}")
            return {
                'success': False,
                'message': 'Unable to create ASL support session at this time.',
                'session_id': None
            }
        
        logger.info(f"Created ASL support session for user {user_id}: {space['id']}")
        
        return {
            'success': True,
            'message': 'ASL support session created successfully.',
            'session_id': space['id'],
            'space_details': space
        }
    
    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get conversation history for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of message dictionaries
        """
        return self._conversation_histories.get(str(user_id), [])
    
    def clear_conversation_history(self, user_id: int) -> None:
        """
        Clear conversation history for a user
        
        Args:
            user_id: User identifier
        """
        self._conversation_histories[str(user_id)] = []
        logger.info(f"Cleared conversation history for user {user_id}")
    
    def _add_to_conversation_history(self, user_id: int, sender: str, message: str) -> None:
        """
        Add a message to the user's conversation history
        
        Args:
            user_id: User identifier
            sender: Message sender ('user' or 'bot')
            message: Message content
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self._conversation_histories:
            self._conversation_histories[user_id_str] = []
            
        self._conversation_histories[user_id_str].append({
            'id': str(uuid.uuid4()),
            'sender': sender,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Limit history to last 50 messages
        if len(self._conversation_histories[user_id_str]) > 50:
            self._conversation_histories[user_id_str] = self._conversation_histories[user_id_str][-50:]
    
    def _generate_response(self, user_id: int, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response to the user message
        
        Args:
            user_id: User identifier
            message: User message
            context: Optional context
        
        Returns:
            Dictionary with response data
        """
        message_lower = message.lower()
        
        # Determine the most relevant topic based on keywords
        relevant_topic = None
        max_matches = 0
        
        for topic, data in self.response_patterns.items():
            matches = sum(1 for keyword in data['keywords'] if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                relevant_topic = topic
        
        # Use the provided context if no relevant topic found
        if max_matches == 0 and context:
            relevant_topic = context if context in self.response_patterns else None
        
        # Generate response based on topic
        if relevant_topic:
            # Determine the specific sub-topic
            subtopic = 'general'  # Default
            
            topic_data = self.response_patterns[relevant_topic]
            for sub, video_key in topic_data['video_keys'].items():
                if sub != 'general' and sub in message_lower:
                    subtopic = sub
                    break
            
            # Get video for the response
            video_key = topic_data['video_keys'][subtopic]
            asl_video = self._get_asl_video_for_response(video_key)
            
            # Generate text response
            if relevant_topic == 'tax_filing':
                if subtopic == 'general':
                    text = "The tax filing process involves reporting your income and deductions to determine if you owe more taxes or are due a refund. Would you like information about specific tax forms or deductions?"
                elif subtopic == 'forms':
                    text = "Common tax forms include W-2 (for employees), 1099 (for contractors and other income), and Form 1040 (the main tax return). Which form do you need help with?"
                elif subtopic == 'deductions':
                    text = "Tax deductions reduce your taxable income. Common deductions include mortgage interest, charitable donations, and some business expenses. Would you like to know more about specific deductions?"
                elif subtopic == 'status':
                    text = "Your filing status affects your tax rates and deduction amounts. Options include Single, Married Filing Jointly, Married Filing Separately, Head of Household, and Qualifying Widow(er)."
                else:
                    text = "I can help you understand tax filing concepts. What specific aspect of taxes would you like to learn more about?"
                    
            elif relevant_topic == 'financial_profile':
                if subtopic == 'general':
                    text = "Your financial profile includes your income, assets, investments, and retirement accounts. It helps create personalized financial recommendations. Would you like to set up your profile?"
                elif subtopic == 'income':
                    text = "Your income includes wages, business income, investment income, and other sources. Accurate income reporting helps with tax filing and financial planning."
                elif subtopic == 'investments':
                    text = "Investments might include stocks, bonds, mutual funds, and real estate. These can help grow your wealth over time. Would you like information on specific investment types?"
                elif subtopic == 'retirement':
                    text = "Retirement accounts like 401(k)s and IRAs offer tax advantages for saving for retirement. Would you like to learn more about retirement planning?"
                else:
                    text = "I can help you understand your financial profile. What specific aspect would you like to learn more about?"
                    
            elif relevant_topic == 'investment':
                if subtopic == 'general':
                    text = "Investing means putting money into assets with the goal of growing your wealth. Common investments include stocks, bonds, mutual funds, and real estate."
                elif subtopic == 'stocks':
                    text = "Stocks represent ownership in a company. When you buy stock, you own a small piece of that business and may receive dividends and/or benefit from price appreciation."
                elif subtopic == 'bonds':
                    text = "Bonds are loans you make to companies or governments. They typically pay regular interest and return your principal at maturity."
                elif subtopic == 'funds':
                    text = "Mutual funds and ETFs pool money from many investors to buy a diversified portfolio of stocks, bonds, or other assets. They offer instant diversification."
                elif subtopic == 'risk':
                    text = "All investments carry risk. Generally, investments with higher potential returns also carry higher risk. Diversification can help manage risk."
                else:
                    text = "I can help you understand investment concepts. What specific aspect would you like to learn more about?"
                    
            elif relevant_topic == 'retirement':
                if subtopic == 'general':
                    text = "Retirement planning involves saving and investing now to have income when you stop working. Key considerations include how much to save and which accounts to use."
                elif subtopic == '401k':
                    text = "A 401(k) is an employer-sponsored retirement plan. Contributions are typically made pre-tax, reducing your current taxable income, and grow tax-deferred until retirement."
                elif subtopic == 'ira':
                    text = "Individual Retirement Accounts (IRAs) come in two main types: Traditional and Roth. Traditional IRAs offer tax-deferred growth, while Roth IRAs provide tax-free withdrawals in retirement."
                elif subtopic == 'planning':
                    text = "Retirement planning involves estimating expenses, managing investments, and creating income streams. The earlier you start, the more time your money has to grow."
                else:
                    text = "I can help you understand retirement planning concepts. What specific aspect would you like to learn more about?"
            else:
                text = "I can help you with various financial topics including taxes, investments, and retirement planning. What would you like to learn about?"
        else:
            # Generic response when no relevant topic is found
            text = "I'm here to help with financial questions related to taxes, investments, and retirement planning. Could you provide more details about what you're looking for?"
            asl_video = self._get_asl_video_for_response('general_greeting')
        
        return {
            'text': text,
            'asl_video': asl_video,
            'topic': relevant_topic,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_asl_video_for_response(self, response_key: str) -> Dict[str, Any]:
        """
        Get an ASL video for a specific response
        
        Args:
            response_key: Key identifying the response
        
        Returns:
            Dictionary with video details
        """
        # Try to get the specific video
        video = self.mux_client.get_asl_video(response_key)
        
        # If not found, try to get a related video or fallback
        if not video:
            # Extract the general topic from the key (e.g., 'tax_filing_forms' -> 'tax_filing')
            if '_' in response_key:
                general_topic = response_key.split('_')[0]
                general_key = f"{general_topic}_general"
                video = self.mux_client.get_asl_video(general_key)
            
            # If still not found, use fallback
            if not video:
                video = self.mux_client.get_fallback_video()
        
        return video
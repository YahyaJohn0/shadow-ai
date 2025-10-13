# shadow_core/clean_output.py
"""
Clean output system - removes logging and shows only clean responses
"""

import logging
import re
from typing import Optional

class CleanOutput:
    """Handles clean, user-friendly output without technical logs"""
    
    def __init__(self, show_technical_logs=False):
        self.show_technical_logs = show_technical_logs
        self.setup_clean_logging()
    
    def setup_clean_logging(self):
        """Configure logging to be less verbose"""
        if not self.show_technical_logs:
            # Reduce logging level for cleaner output
            logging.getLogger('shadow_core').setLevel(logging.WARNING)
            logging.getLogger('openai').setLevel(logging.ERROR)
            logging.getLogger('httpx').setLevel(logging.ERROR)
            logging.getLogger('comtypes').setLevel(logging.ERROR)
            logging.getLogger('google').setLevel(logging.ERROR)
    
    @staticmethod
    def format_user_input(text: str) -> str:
        """Format user input cleanly"""
        return f"👤 You: {text}"
    
    @staticmethod
    def format_ai_response(text: str) -> str:
        """Format AI response cleanly"""
        # Remove any technical prefixes or suffixes
        cleaned_text = CleanOutput.clean_response_text(text)
        return f"🤖 Shadow: {cleaned_text}"
    
    @staticmethod
    def clean_response_text(text: str) -> str:
        """Remove technical language from responses"""
        # Remove common AI disclaimers and technical phrases
        patterns_to_remove = [
            r'As an AI(.*?)(?=\.|$)',
            r'I am an AI(.*?)(?=\.|$)',
            r'mujhe maaf karna, mujhe samajh nahi aa raha hai',
            r'I apologize(.*?)(?=\.|$)',
            r'Sorry(.*?)(?=\.|$)',
        ]
        
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[.,]\s*', '', cleaned)
        
        return cleaned if cleaned else text
    
    @staticmethod
    def print_separator():
        """Print a clean separator"""
        print("=" * 60)
    
    @staticmethod
    def print_clean_conversation(user_input: str, ai_response: str):
        """Print clean conversation without logs"""
        CleanOutput.print_separator()
        print(CleanOutput.format_user_input(user_input))
        print(CleanOutput.format_ai_response(ai_response))
        print()
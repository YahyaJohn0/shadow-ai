# shadow_core/gemini_brain.py
"""
Google Gemini API integration for Shadow AI
Free and powerful alternative to OpenAI
"""

import logging
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GeminiBrain:
    """
    Google Gemini API brain - Free and powerful
    """
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key or self.api_key == 'your_actual_gemini_api_key_here':
            raise ValueError("Gemini API key not configured. Please set GOOGLE_API_KEY in .env file")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat_sessions = {}
        
        logger.info("Gemini Brain initialized successfully")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to Gemini and get response"""
        try:
            # Convert messages to Gemini format
            gemini_messages = self._convert_to_gemini_format(messages)
            
            # Start or continue chat session
            chat_session_id = str(hash(str(messages)))
            if chat_session_id not in self.chat_sessions:
                self.chat_sessions[chat_session_id] = self.model.start_chat(history=[])
            
            chat = self.chat_sessions[chat_session_id]
            
            # Get the last user message
            last_user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content")
                    break
            
            if not last_user_message:
                return "I didn't receive a message to respond to."
            
            # Send message to Gemini (using async execution)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: chat.send_message(last_user_message)
            )
            
            response_text = response.text.strip()
            
            logger.info(f"Gemini response received: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert OpenAI format to Gemini format"""
        gemini_messages = []
        
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        return gemini_messages
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using Gemini"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini content generation error: {e}")
            raise

# Fallback Gemini brain for when API is not available
class GeminiFallbackBrain:
    """Fallback when Gemini is not installed"""
    
    def __init__(self):
        logger.warning("Gemini package not available. Using rule-based fallback.")
        from shadow_core.robust_brain import EnhancedRuleBasedBrain
        self.fallback_brain = EnhancedRuleBasedBrain()
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        return await self.fallback_brain.ask(messages)

def create_gemini_brain():
    """Create Gemini brain with proper error handling"""
    try:
        # Try to import Gemini
        import google.generativeai
        return GeminiBrain()
    except ImportError:
        logger.error("Google Generative AI package not installed.")
        logger.info("Install with: pip install google-generativeai")
        return GeminiFallbackBrain()
    except Exception as e:
        logger.error(f"Gemini initialization failed: {e}")
        return GeminiFallbackBrain()
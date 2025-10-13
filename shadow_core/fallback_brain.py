# shadow_core/fallback_brain.py
"""
Fallback brain for when API keys are invalid or unavailable
"""

import logging
import random
from typing import List, Dict

logger = logging.getLogger(__name__)

class FallbackBrain:
    """Simple fallback brain that works without API keys"""
    
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! I'm Shadow AI. How can I help you today?",
                "Hi there! I'm here to assist you.",
                "Greetings! What can I do for you?"
            ],
            "help": [
                "I can help you with: opening apps, controlling your computer, setting reminders, sending messages, and more!",
                "I'm your AI assistant. Try asking me to open an application or set a reminder.",
                "I'm here to help! You can ask me to control your computer, search the web, or manage your tasks."
            ],
            "weather": [
                "I'd need an API key to check real weather. For now, I can help you with computer tasks!",
                "Weather service is currently unavailable. Try asking me to open an app or file instead."
            ],
            "default": [
                "I understand. How can I assist you further?",
                "Got it! What would you like me to do next?",
                "I see. Is there anything else you'd like help with?"
            ]
        }
        logger.info("Fallback brain initialized")
    
    async def ask(self, messages: List[Dict]) -> str:
        """Simple response generation without API"""
        try:
            if not messages:
                return random.choice(self.responses["greeting"])
            
            # Get the last user message
            last_message = messages[-1]
            if last_message.get("role") == "user":
                user_text = last_message.get("content", "").lower()
                
                # Simple intent matching
                if any(word in user_text for word in ["hello", "hi", "hey"]):
                    return random.choice(self.responses["greeting"])
                elif any(word in user_text for word in ["help", "what can you do"]):
                    return random.choice(self.responses["help"])
                elif any(word in user_text for word in ["weather", "temperature"]):
                    return random.choice(self.responses["weather"])
                else:
                    return random.choice(self.responses["default"])
            
            return random.choice(self.responses["default"])
            
        except Exception as e:
            logger.error(f"Fallback brain error: {e}")
            return "I'm here to help! What would you like me to do?"
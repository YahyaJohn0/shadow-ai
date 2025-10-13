# shadow_core/brain.py
"""
GEMINI 2.5 FLASH BRAIN - ALWAYS ONLINE
Completely replaces old OpenAI brain with free Gemini API
"""

import logging
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time

logger = logging.getLogger(__name__)

class ShadowBrain:
    """
    Gemini 2.5 Flash Brain - Always Online, Free Forever
    """
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.conversation_history = []
        self.max_history = 10
        self.request_timestamps = []
        self.daily_requests = 0
        self.last_reset_time = time.time()
        
        # Rate limiting (stay within free limits)
        self.requests_per_minute = 55  # Stay under 60/minute
        self.requests_per_day = 1400   # Stay under 1500/day
        
        # Model configuration - Using latest Gemini Flash
        self.model_name = "gemini-2.0-flash-exp"
        
        # Initialize Gemini
        if self.api_key and self.api_key != 'your_actual_gemini_api_key_here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.available = True
                logger.info(f"🎯 Gemini 2.5 Flash Brain initialized - Model: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Gemini initialization failed: {e}")
                self.available = False
                raise Exception(f"Gemini API failed: {e}")
        else:
            logger.error("❌ No Gemini API key found in .env file")
            raise Exception("Missing GOOGLE_API_KEY in .env file")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """
        Get response from Gemini 2.5 Flash - Always Online
        """
        try:
            # Check rate limits
            if not self._check_rate_limits():
                return "I've reached my free API limit for now. Please try again in a minute."
            
            # Update request tracking
            current_time = time.time()
            self.request_timestamps.append(current_time)
            self.daily_requests += 1
            
            # Clean old timestamps
            two_minutes_ago = current_time - 120
            self.request_timestamps = [ts for ts in self.request_timestamps if ts > two_minutes_ago]
            
            # Build optimized prompt for Gemini
            prompt = self._build_gemini_prompt(messages)
            
            # Get response from Gemini
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=1024,
                    )
                )
            )
            
            response_text = response.text.strip()
            
            # Update conversation history
            last_user_message = self._get_last_user_message(messages)
            self._update_conversation_history(last_user_message, response_text)
            
            logger.info(f"🚀 Gemini 2.5 Flash response (Daily: {self.daily_requests}/1400)")
            return response_text
            
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            # Don't fallback to rule-based - just return error message
            return f"I'm experiencing a temporary issue with the AI service. Please try again in a moment. Error: {str(e)}"
    
    def _build_gemini_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build optimized prompt for Gemini 2.5 Flash"""
        system_prompt = """You are Shadow, a helpful AI assistant with these capabilities:
- Send messages (WhatsApp, SMS)
- Set reminders, alarms, and schedules
- Check weather information for any location
- Get stock prices and financial data
- Search the web for information
- Answer questions and provide assistance

Be concise, helpful, and friendly. If the user asks about your capabilities, explain what you can do in a natural way."""
        
        # Extract conversation history
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation.append(f"{role}: {msg['content']}")
        
        # Build final prompt
        if conversation:
            return f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation) + "\n\nAssistant:"
        else:
            return system_prompt + "\n\nUser: " + messages[-1]["content"] + "\n\nAssistant:"
    
    def _get_last_user_message(self, messages: List[Dict[str, str]]) -> str:
        """Extract the last user message"""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within free rate limits"""
        current_time = time.time()
        
        # Reset daily counter if new day
        if current_time - self.last_reset_time > 86400:
            self.daily_requests = 0
            self.last_reset_time = current_time
        
        # Check daily limit
        if self.daily_requests >= self.requests_per_day:
            logger.warning("Daily limit reached")
            return False
        
        # Check minute limit
        minute_ago = current_time - 60
        recent_requests = [ts for ts in self.request_timestamps if ts > minute_ago]
        
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning("Minute rate limit reached")
            return False
        
        return True
    
    def _update_conversation_history(self, user_message: str, ai_response: str):
        """Update conversation history"""
        self.conversation_history.append({
            'user': user_message,
            'assistant': ai_response,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_time = time.time()
        minute_ago = current_time - 60
        recent_requests = len([ts for ts in self.request_timestamps if ts > minute_ago])
        
        return {
            "model": self.model_name,
            "daily_requests": self.daily_requests,
            "recent_requests": recent_requests,
            "remaining_daily": max(0, self.requests_per_day - self.daily_requests),
            "remaining_minute": max(0, self.requests_per_minute - recent_requests),
            "status": "gemini_2.5_flash_online"
        }

# Legacy fallback class for compatibility (but it should never be used)
class FallbackBrain:
    """
    LEGACY - This should not be used anymore
    Shadow AI is now always online with Gemini
    """
    
    def __init__(self):
        logger.error("❌ FALLBACK BRAIN SHOULD NOT BE USED - Shadow AI is always online")
        raise Exception("FallbackBrain should not be used. Shadow AI is always online with Gemini.")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        raise Exception("FallbackBrain should not be used. Check your Gemini API configuration.")
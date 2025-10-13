# shadow_core/free_gemini.py
"""
Free Gemini 2.5 Flash API - Latest, Fastest, Free Forever
"""

import logging
import asyncio
import google.generativeai as genai
import time
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import random

logger = logging.getLogger(__name__)

class GeminiFlashBrain:
    """
    Free Gemini 2.5 Flash - Latest model, completely free
    """
    
    def __init__(self):
        load_dotenv()
        
        # Load multiple API keys
        self.api_keys = self._load_api_keys()
        if not self.api_keys:
            raise ValueError("No Gemini API keys found. Please set GOOGLE_API_KEY in .env")
        
        self.current_key_index = 0
        self.request_timestamps = []
        self.daily_requests = 0
        self.last_reset_time = time.time()
        
        # Rate limiting (stay within free limits)
        self.requests_per_minute = 55  # Stay under 60/minute
        self.requests_per_day = 1400   # Stay under 1500/day
        
        # Model configuration
        self.model_name = "gemini-2.0-flash-exp"  # Latest free model
        # Alternative: "gemini-1.5-flash" or "gemini-1.5-pro"
        
        logger.info(f"🎯 Gemini 2.5 Flash Brain initialized")
        logger.info(f"🤖 Using model: {self.model_name}")
        logger.info(f"🔑 Loaded {len(self.api_keys)} API keys")
        logger.info(f"📊 Rate limits: {self.requests_per_minute}/minute, {self.requests_per_day}/day")
    
    def _load_api_keys(self) -> List[str]:
        """Load all available Gemini API keys"""
        keys = []
        
        # Primary key
        primary_key = os.getenv('GOOGLE_API_KEY')
        if primary_key and primary_key != 'your_actual_gemini_api_key_here':
            keys.append(primary_key)
        
        # Backup keys
        for i in range(2, 6):
            backup_key = os.getenv(f'GOOGLE_API_KEY_{i}')
            if backup_key and backup_key.startswith('AIza'):
                keys.append(backup_key)
        
        return keys
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
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
    
    def _get_next_api_key(self) -> str:
        """Rotate to next API key"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """Ask Gemini 2.5 Flash with optimized prompts"""
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
        
        # Get API key
        api_key = self._get_next_api_key()
        
        try:
            # Configure with current key
            genai.configure(api_key=api_key)
            
            # Use the latest Gemini 2.5 Flash model
            model = genai.GenerativeModel(self.model_name)
            
            # Convert messages to Gemini format with system prompt
            prompt = self._build_optimized_prompt(messages)
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(
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
            
            logger.info(f"🚀 Gemini 2.5 Flash response (Key: {api_key[:10]}..., Daily: {self.daily_requests}/1400)")
            return response_text
            
        except Exception as e:
            logger.error(f"Gemini 2.5 Flash error: {e}")
            
            # Try with fallback model
            if "not found" in str(e).lower():
                return await self._try_fallback_model(api_key, messages)
            
            # Try next key if this one fails
            if len(self.api_keys) > 1:
                logger.info("Trying next API key...")
                return await self.ask(messages)
            else:
                return self._get_fallback_response()
    
    def _build_optimized_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build optimized prompt for Gemini 2.5 Flash"""
        system_prompt = """You are Shadow, a helpful AI assistant. You can:
- Send messages (WhatsApp, SMS)
- Set reminders and schedules  
- Check weather, stocks, news
- Search the web
- Answer questions conversationally

Be concise, helpful, and friendly. If the user asks about your capabilities, explain what you can do."""
        
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
    
    async def _try_fallback_model(self, api_key: str, messages: List[Dict[str, str]]) -> str:
        """Try fallback models if 2.5 Flash is not available"""
        fallback_models = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro"
        ]
        
        for model_name in fallback_models:
            try:
                logger.info(f"Trying fallback model: {model_name}")
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                
                prompt = self._build_optimized_prompt(messages)
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: model.generate_content(prompt)
                )
                
                logger.info(f"✅ Success with fallback model: {model_name}")
                return response.text.strip()
                
            except Exception as e:
                logger.warning(f"Fallback model {model_name} failed: {e}")
                continue
        
        # All models failed
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Get fallback response when all models fail"""
        fallbacks = [
            "I'm optimizing my connection. Please try again in a moment!",
            "Let me refresh and try that again...",
            "I'm here! Just dealing with a temporary connection issue.",
            "One moment while I reconnect to provide the best response...",
        ]
        return random.choice(fallbacks)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_time = time.time()
        minute_ago = current_time - 60
        recent_requests = len([ts for ts in self.request_timestamps if ts > minute_ago])
        
        return {
            "model": self.model_name,
            "daily_requests": self.daily_requests,
            "recent_requests": recent_requests,
            "available_keys": len(self.api_keys),
            "remaining_daily": max(0, self.requests_per_day - self.daily_requests),
            "remaining_minute": max(0, self.requests_per_minute - recent_requests),
            "status": "gemini_2.5_flash"
        }

class ForeverFreeFlashBrain:
    """
    Forever Free Brain with Gemini 2.5 Flash
    """
    
    def __init__(self):
        try:
            self.gemini_brain = GeminiFlashBrain()
            self.active_brain = self.gemini_brain
            logger.info("🎯 Forever Free Flash Brain initialized!")
        except Exception as e:
            logger.error(f"Gemini 2.5 Flash failed: {e}")
            # Fallback to basic Gemini
            try:
                from shadow_core.gemini_brain import create_gemini_brain
                self.active_brain = create_gemini_brain()
                logger.info("🔄 Using basic Gemini fallback")
            except:
                from shadow_core.robust_brain import EnhancedRuleBasedBrain
                self.active_brain = EnhancedRuleBasedBrain()
                logger.info("🔄 Using rule-based fallback")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        return await self.active_brain.ask(messages)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        if hasattr(self.active_brain, 'get_usage_stats'):
            return self.active_brain.get_usage_stats()
        return {"status": "fallback", "free": True}
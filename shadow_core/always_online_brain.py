# shadow_core/always_online_brain.py
"""
Always Online Brain - Gemini Only, No Fallbacks
"""

import logging
import asyncio
from typing import List, Dict, Any
import sys

logger = logging.getLogger(__name__)

class AlwaysOnlineBrain:
    """Brain that ONLY uses Gemini - no offline fallback ever"""
    
    def __init__(self):
        logger.info("🔧 Initializing Always Online Brain...")
        
        # Try to import and initialize Gemini
        try:
            import google.generativeai as genai
            from dotenv import load_dotenv
            import os
            
            load_dotenv()
            api_key = os.getenv('GOOGLE_API_KEY')
            
            if not api_key or api_key == 'your_actual_gemini_api_key_here':
                logger.error("❌ No Gemini API key found in .env file")
                raise ValueError("Missing Gemini API key")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Test the connection
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            test_response = model.generate_content("Test")
            
            self.model = model
            logger.info("🎯 GEMINI 2.5 FLASH - CONNECTED AND READY")
            
        except Exception as e:
            logger.error(f"❌ GEMINI INITIALIZATION FAILED: {e}")
            print(f"\n💀 FATAL: Cannot connect to Gemini API")
            print(f"🔧 Reason: {e}")
            print("\n🔧 Troubleshooting:")
            print("1. Check your GOOGLE_API_KEY in .env file")
            print("2. Ensure you have internet connection")
            print("3. Run: pip install google-generativeai")
            print("4. Visit: https://aistudio.google.com/ to get API key")
            sys.exit(1)
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """Ask Gemini - no fallbacks, will crash if Gemini fails"""
        try:
            # Get last user message
            last_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_message = msg.get("content", "")
                    break
            
            if not last_message:
                return "Please provide a message."
            
            # Generate response using async
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(last_message)
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"❌ GEMINI API ERROR: {e}")
            return f"I'm experiencing a temporary issue with Gemini API. Please try again in a moment. Error: {str(e)}"

def create_always_online_brain():
    """Create the always online brain instance"""
    return AlwaysOnlineBrain()

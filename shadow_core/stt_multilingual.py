# shadow_core/stt_multilingual.py
"""
Multilingual Speech-to-Text module with Urdu and Pashto support
"""

import logging
import speech_recognition as sr
import asyncio
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class MultilingualSTT:
    """
    Speech-to-Text with Urdu, Pashto, and English support
    """
    
    def __init__(self, multilingual_manager):
        self.multilingual_manager = multilingual_manager
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        logger.info("Adjusting for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        logger.info("Multilingual STT initialized")
    
    async def listen(self, timeout: int = 10, phrase_time_limit: int = 15) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen for speech and convert to text with language detection
        Returns: (text, detected_language)
        """
        try:
            logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for speech with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try Urdu first (default language)
            try:
                text = self.recognizer.recognize_google(audio, language='ur-PK')
                detected_lang = await self.multilingual_manager.detect_language(text)
                logger.info(f"Speech recognized in Urdu: {text}")
                return text, detected_lang
            except sr.UnknownValueError:
                pass
            
            # Try Pashto
            try:
                text = self.recognizer.recognize_google(audio, language='ps-AF')
                detected_lang = await self.multilingual_manager.detect_language(text)
                logger.info(f"Speech recognized in Pashto: {text}")
                return text, detected_lang
            except sr.UnknownValueError:
                pass
            
            # Try English
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                detected_lang = await self.multilingual_manager.detect_language(text)
                logger.info(f"Speech recognized in English: {text}")
                return text, detected_lang
            except sr.UnknownValueError:
                pass
            
            logger.warning("Could not understand speech in any supported language")
            return None, None
            
        except sr.WaitTimeoutError:
            logger.info("Listening timeout - no speech detected")
            return None, None
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None, None
    
    async def listen_with_language_hint(self, language: str, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen with specific language preference
        """
        try:
            language_codes = {
                'ur': 'ur-PK',
                'ps': 'ps-AF', 
                'en': 'en-US'
            }
            
            sr_language = language_codes.get(language, 'ur-PK')
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            
            text = self.recognizer.recognize_google(audio, language=sr_language)
            detected_lang = await self.multilingual_manager.detect_language(text)
            
            logger.info(f"Speech recognized in {language}: {text}")
            return text, detected_lang
            
        except sr.UnknownValueError:
            logger.warning(f"Could not understand {language} speech")
            return None, None
        except sr.WaitTimeoutError:
            return None, None
        except Exception as e:
            logger.error(f"Language-specific STT error: {e}")
            return None, None
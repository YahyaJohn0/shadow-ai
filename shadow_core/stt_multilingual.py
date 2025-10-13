# shadow_core/stt_multilingual.py
"""
Multilingual Speech-to-Text module with Urdu, Pashto, and Roman script support
"""

import logging
import speech_recognition as sr
import asyncio
from typing import Tuple, Optional
import re
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class MultilingualSTT:
    """
    Speech-to-Text with Urdu, Pashto, English, and Roman script support
    """
    
    def __init__(self, multilingual_manager):
        self.multilingual_manager = multilingual_manager
        self.recognizer = sr.Recognizer()
        self.thread_pool = ThreadPoolExecutor(max_workers=1)
        
        # Initialize microphone with error handling
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            logger.info("Adjusting for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Multilingual STT initialized with microphone")
        except Exception as e:
            logger.warning(f"Microphone initialization failed: {e}")
            self.microphone = None
        
        # Roman script detection patterns
        self.roman_urdu_patterns = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'thi', 'the', 'kyun', 'kahan', 'kaun',
            'acha', 'theek', 'bilkul', 'zaroor', 'salam', 'alaikum'
        ]
        
        self.roman_pashto_patterns = [
            'sta', 'yast', 'kaw', 'kawi', 'kawam', 'kawalai', 'kawale', 
            'sham', 'dera', 'khaire', 'kha', 'manana', 'mehrbani', 'sara',
            'lag', 'de', 'da', 'pa', 'po', 'kaw', 'ka', 'komak', 'murajat'
        ]
    
    async def _recognize_speech_async(self, language: str = 'en-US') -> Optional[str]:
        """Run speech recognition in thread pool to avoid blocking"""
        try:
            def recognize():
                if not self.microphone:
                    return None
                
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(
                            source, 
                            timeout=5,
                            phrase_time_limit=10
                        )
                        return self.recognizer.recognize_google(audio, language=language)
                    except sr.WaitTimeoutError:
                        return None
                    except sr.UnknownValueError:
                        return None
                    except Exception as e:
                        logger.error(f"Recognition error: {e}")
                        return None
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(self.thread_pool, recognize)
            return text
            
        except Exception as e:
            logger.error(f"Async recognition error: {e}")
            return None
    
    async def listen(self, timeout: int = 10, phrase_time_limit: int = 15) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen for speech and convert to text with language detection
        Returns: (text, detected_language)
        """
        if not self.microphone:
            logger.warning("No microphone available")
            return None, None
            
        try:
            logger.info("🎤 Listening for speech...")
            
            # Try English first (most common)
            text = await self._recognize_speech_async('en-US')
            if text:
                logger.info(f"🎯 Recognized English: {text}")
                return text, 'en'
            
            # Try Urdu
            text = await self._recognize_speech_async('ur-PK')
            if text:
                logger.info(f"🎯 Recognized Urdu: {text}")
                # Check if it's Roman Urdu
                if await self.is_roman_input(text):
                    return text, 'ur'
                else:
                    roman_text = self._urdu_to_roman(text)
                    return roman_text, 'ur'
            
            # Try Pashto
            text = await self._recognize_speech_async('ps-AF')
            if text:
                logger.info(f"🎯 Recognized Pashto: {text}")
                if await self.is_roman_input(text):
                    return text, 'ps'
                else:
                    roman_text = self._pashto_to_roman(text)
                    return roman_text, 'ps'
            
            logger.info("❌ No speech recognized")
            return None, None
            
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None, None
    
    async def listen_with_language_hint(self, language: str, timeout: int = 10) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen with specific language preference
        """
        language_codes = {
            'ur': 'ur-PK',
            'ps': 'ps-AF', 
            'en': 'en-US',
            'hi': 'hi-IN'
        }
        
        sr_language = language_codes.get(language, 'en-US')
        
        try:
            text = await self._recognize_speech_async(sr_language)
            if text:
                logger.info(f"🎯 Recognized {language}: {text}")
                
                # Convert to Roman script if needed
                if language in ['ur', 'ps'] and not await self.is_roman_input(text):
                    if language == 'ur':
                        text = self._urdu_to_roman(text)
                    elif language == 'ps':
                        text = self._pashto_to_roman(text)
                
                return text, language
            else:
                return None, None
            
        except Exception as e:
            logger.error(f"Language-specific STT error: {e}")
            return None, None
    
    async def listen_simple(self, language: str = 'en-US') -> Optional[str]:
        """
        Simple speech recognition without complex processing
        """
        try:
            return await self._recognize_speech_async(language)
        except Exception as e:
            logger.error(f"Simple listen error: {e}")
            return None
    
    def _contains_urdu_script(self, text: str) -> bool:
        """Check if text contains Urdu script characters"""
        return bool(re.search(r'[\u0600-\u06FF]', text))
    
    def _contains_pashto_script(self, text: str) -> bool:
        """Check if text contains Pashto script characters"""
        return bool(re.search(r'[\u0600-\u06FF\u0671-\u06D3]', text))
    
    def _contains_hindi_script(self, text: str) -> bool:
        """Check if text contains Hindi script characters"""
        return bool(re.search(r'[\u0900-\u097F]', text))
    
    def _urdu_to_roman(self, urdu_text: str) -> str:
        """Convert Urdu script to Roman Urdu"""
        # Basic Urdu to Roman conversion mapping
        urdu_roman_map = {
            'میں': 'main', 'ہوں': 'hoon', 'ہے': 'hai', 'ہیں': 'hain',
            'آپ': 'aap', 'کیسے': 'kaise', 'ہو': 'ho', 'ٹھیک': 'theek',
            'شکریہ': 'shukriya', 'کیا': 'kya', 'کر': 'kar', 'سکتے': 'sakte',
            'میری': 'meri', 'مدد': 'madad', 'سن': 'sun', 'رہے': 'rahe',
            'جواب': 'jawab', 'دو': 'do', 'السلام': 'salam', 'علیکم': 'alaikum',
            'اور': 'aur', 'لیکن': 'lekin', 'اگر': 'agar', 'تو': 'to',
            'بہت': 'bahut', 'اچھا': 'acha', 'برا': 'bura', 'اب': 'ab',
            'پھر': 'phir', 'کب': 'kab', 'کہاں': 'kahan', 'کیوں': 'kyun',
            'کون': 'kaun', 'جی': 'ji', 'نہیں': 'nahi', 'ہاں': 'haan',
            'ضرور': 'zaroor', 'آج': 'aaj', 'کل': 'kal', 'شام': 'shaam'
        }
        
        roman_text = urdu_text
        for urdu, roman in urdu_roman_map.items():
            roman_text = roman_text.replace(urdu, roman)
        
        return roman_text
    
    def _pashto_to_roman(self, pashto_text: str) -> str:
        """Convert Pashto script to Roman Pashto"""
        pashto_roman_map = {
            'سته': 'sta', 'یاست': 'yast', 'کولی': 'kaw', 'کولی شم': 'kawam',
            'شئ': 'she', 'مه': 'ma', 'ته': 'ta', 'دی': 'de', 'مو': 'mo',
            'ستا': 'sta', 'زما': 'zma', 'د': 'da', 'په': 'pa', 'کې': 'ke',
            'نه': 'na', 'سلام': 'salam', 'مننه': 'manana', 'مهرباني': 'mehrbani',
            'څنګه': 'tsanga', 'څه': 'tse', 'ولې': 'wale', 'چېرې': 'chere',
            'چا': 'cha', 'کله': 'kala', 'ښه': 'kha', 'بد': 'bad', 'اوس': 'os',
            'بیا': 'bya', 'لږ': 'lag', 'ډیر': 'der', 'مرسته': 'marasta',
            'کومک': 'komak', 'مرسته کوه': 'marasta kawa', 'کومک کوه': 'komak kawa'
        }
        
        roman_text = pashto_text
        for pashto, roman in pashto_roman_map.items():
            roman_text = roman_text.replace(pashto, roman)
        
        return roman_text
    
    async def is_roman_input(self, text: str) -> bool:
        """Check if input appears to be in Roman script"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for Roman Urdu patterns
        urdu_score = sum(1 for pattern in self.roman_urdu_patterns if pattern in text_lower)
        
        # Check for Roman Pashto patterns  
        pashto_score = sum(1 for pattern in self.roman_pashto_patterns if pattern in text_lower)
        
        # Check for absence of native script characters
        has_native_script = (
            self._contains_urdu_script(text) or 
            self._contains_pashto_script(text) or
            self._contains_hindi_script(text)
        )
        
        return (urdu_score >= 1 or pashto_score >= 1) and not has_native_script
    
    def get_available_languages(self) -> list:
        """Get list of available languages for speech recognition"""
        return [
            {'code': 'ur', 'name': 'Urdu', 'roman_support': True},
            {'code': 'ps', 'name': 'Pashto', 'roman_support': True},
            {'code': 'en', 'name': 'English', 'roman_support': True}
        ]
    
    async def test_microphone(self) -> bool:
        """Test if microphone is working"""
        if not self.microphone:
            return False
            
        try:
            # Quick test by trying to listen with short timeout
            result = await self.listen_simple(timeout=2)
            return result is not None
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False

# Utility function for quick speech recognition
async def quick_listen(timeout: int = 5) -> Optional[str]:
    """
    Quick utility function for simple speech recognition
    """
    try:
        stt = MultilingualSTT(None)
        return await stt.listen_simple('en-US')
    except Exception as e:
        logger.warning(f"Quick listen failed: {e}")
        return None
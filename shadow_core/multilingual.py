"""
FIXED Multilingual support for Shadow AI Agent
Roman Urdu and Pashto language support with speech recognition and synthesis
Enhanced with guaranteed response system
"""

import logging
import asyncio
import speech_recognition as sr
from typing import Dict, Any, Optional, Tuple, List
import pyttsx3
import edge_tts
import os
from langdetect import detect, LangDetectException
import re
import random

logger = logging.getLogger(__name__)

class MultilingualManager:
    """Enhanced multilingual manager with Gemini responses"""
    
    def __init__(self):
        self.supported_languages = ['en', 'ur', 'hi', 'ps']
        self.language_detection_cache = {}
        
        # Language configurations
        self.language_configs = {
            'en': {'name': 'English', 'voice': 'en-US-ChristopherNeural', 'rtl': False},
            'ur': {'name': 'Roman Urdu', 'voice': 'ur-PK-AsadNeural', 'rtl': False},  # Changed to Roman Urdu
            'ps': {'name': 'Pashto', 'voice': 'ps-AF-GulNawazNeural', 'rtl': True},
            'hi': {'name': 'Hindi', 'voice': 'hi-IN-MadhurNeural', 'rtl': False}
        }
        
        self.current_language = 'ur'  # Default to Roman Urdu
        self.recognizer = sr.Recognizer()
        self.voice_engine = None
        
        self._initialize_tts()
        logger.info("Enhanced Multilingual Manager initialized")
    
    def _initialize_tts(self):
        """Initialize text-to-speech engines"""
        try:
            # Initialize pyttsx3 for offline TTS
            self.voice_engine = pyttsx3.init()
            self.voice_engine.setProperty('rate', 150)
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.warning(f"Could not initialize TTS engine: {e}")
            self.voice_engine = None

    async def detect_language(self, text: str) -> str:
        """Detect language with enhanced patterns for Roman Urdu"""
        if not text or len(text.strip()) < 2:
            return self.current_language
        
        text_lower = text.lower().strip()
        
        # Check cache first
        if text_lower in self.language_detection_cache:
            return self.language_detection_cache[text_lower]
        
        # Roman Urdu detection patterns (English letters)
        roman_urdu_indicators = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'thi', 'the', 'kyun', 'kahan', 'kaun',
            'acha', 'theek', 'bilkul', 'zaroor', 'yaqeen', 'sach', 'jhoot'
        ]
        
        # Pashto detection patterns  
        pashto_indicators = [
            'سته', 'کولی', 'مې', 'مرسته', 'کړی', 'شئ'
        ]
        
        # Hindi detection patterns
        hindi_indicators = [
            'क्या', 'है', 'में', 'आप', 'कर', 'सकते', 'हो', 'मेरी', 'मदद',
            'mujhe', 'karo', 'sakta', 'kyun', 'kaise'
        ]
        
        # English detection
        english_indicators = [
            'the', 'and', 'you', 'are', 'how', 'what', 'when', 'where',
            'can', 'will', 'help', 'please', 'thank', 'hello', 'hi'
        ]
        
        # Count language indicators
        roman_urdu_score = sum(1 for indicator in roman_urdu_indicators if indicator in text_lower)
        pashto_score = sum(1 for indicator in pashto_indicators if indicator in text_lower)
        hindi_score = sum(1 for indicator in hindi_indicators if indicator in text_lower)
        english_score = sum(1 for indicator in english_indicators if indicator in text_lower)
        
        # Determine language
        if roman_urdu_score > english_score and roman_urdu_score > hindi_score and roman_urdu_score > pashto_score:
            detected_lang = 'ur'
        elif hindi_score > roman_urdu_score and hindi_score > pashto_score:
            detected_lang = 'hi'
        elif pashto_score > roman_urdu_score and pashto_score > hindi_score:
            detected_lang = 'ps'
        elif english_score > roman_urdu_score and english_score > hindi_score:
            detected_lang = 'en'
        else:
            # Default to Roman Urdu if mixed
            detected_lang = 'ur'
        
        # Cache the result
        self.language_detection_cache[text_lower] = detected_lang
        
        logger.info(f"Detected language: {detected_lang} for text: {text_lower[:50]}...")
        return detected_lang
    
    def get_immediate_response(self, text: str, detected_lang: str) -> Optional[str]:
        """Get immediate response without AI processing"""
        text_lower = text.lower().strip()
        
        # Presence detection responses - UPDATED TO ROMAN URDU
        presence_indicators = {
            'en': ['are you there', 'you there', 'hello', 'hi', 'hey', 'can you hear me'],
            'ur': ['aap hain', 'hello', 'sun rahe ho', 'meri awaz sun rahe ho', 'jawab do', 'kya aap ho'],
            'hi': ['क्या आप हो', 'हैलो', 'सुन रहे हो', 'मेरी आवाज सुन रहे हो', 'जवाब दो'],
            'ps': ['ایا تاسو هلته یاست', 'سلام', 'اور', 'زما غږ اور', 'ځواب راکړئ']
        }
        
        # Check for presence detection in all languages
        for lang, indicators in presence_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return self._get_presence_response(detected_lang)
        
        # Help requests
        help_indicators = {
            'en': ['help', 'can you help', 'what can you do', 'kya kar sakte ho'],
            'ur': ['madad', 'kya aap madad kar sakte hain', 'kya kar sakte ho', 'help'],
            'hi': ['मदद', 'क्या आप मदद कर सकते हैं', 'क्या कर सकते हो'],
            'ps': ['مرسته', 'ایا تاسو مرسته کولی شئ', 'څه کولی شئ']
        }
        
        for lang, indicators in help_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return self._get_help_response(detected_lang)
        
        return None
    
    def _get_presence_response(self, lang: str) -> str:
        """Get presence confirmation response - UPDATED TO ROMAN URDU"""
        responses = {
            'en': [
                "Yes, I'm here and listening! How can I help you?",
                "I'm here and ready to assist! What would you like me to do?",
                "Yes, I can hear you perfectly! What can I help you with?",
                "I'm listening! Feel free to ask me anything.",
                "Hello! I'm here and ready to help. What can I do for you?"
            ],
            'ur': [  # ROMAN URDU RESPONSES
                "Ji haan, main yahan hoon aur sun raha hoon! Main aap ki kis tarah madad kar sakta hoon?",
                "Main yahan hoon aur madad ke liye tayyar hoon! Aap mujh se kya karana chahenge?",
                "Haan, main aap ki awaaz bilkul wazeh sun raha hoon! Main aap ki kis tarah madad kar sakta hoon?",
                "Main sun raha hoon! Barah e karam mujh se kuch bhi poochain.",
                "Hello! Main yahan hoon aur madad ke liye tayyar hoon. Main aap ke liye kya kar sakta hoon?"
            ],
            'hi': [
                "हाँ, मैं यहाँ हूँ और सुन रहा हूँ! मैं आपकी कैसे मदद कर सकता हूँ?",
                "मैं यहाँ हूँ और सहायता के लिए तैयार हूँ! आप मुझसे क्या कराना चाहेंगे?",
                "हाँ, मैं आपकी आवाज़ बिल्कुल साफ सुन रहा हूँ! मैं आपकी कैसे मदद कर सकता हूँ?",
                "मैं सुन रहा हूँ! कृपया मुझसे कुछ भी पूछें।",
                "नमस्ते! मैं यहाँ हूँ और मदद के लिए तैयार हूँ। मैं आपके लिए क्या कर सकता हूँ?"
            ],
            'ps': [
                "هو، زم دلته یم او اورم! زه تاسو سره څنګه مرسته کولی شم؟",
                "زم دلته یم او د مرستې لپاره چمتو یم! تاسو څه غواړئ چې زه وکړم؟",
                "هو، زه ستاسو غږ په کامل ډول اورم! زه تاسو سره څنګه مرسته کولی شم؟",
                "زه اورم! مهرباني وکړئ زما څخه هرڅه وپوښتئ.",
                "سلام! زم دلته یم او د مرستې لپاره چمتو یم. زه تاسو لپاره څه کولی شم؟"
            ]
        }
        
        return random.choice(responses.get(lang, responses['en']))
    
    def _get_help_response(self, lang: str) -> str:
        """Get help response - UPDATED TO ROMAN URDU"""
        responses = {
            'en': """
🤖 **I can help you with:**

📱 **Messaging:** Send WhatsApp/SMS messages
⏰ **Scheduling:** Set reminders, alarms, timers  
🌤️ **Information:** Weather, news, stock prices
🔍 **Search:** Web searches and information
💬 **Conversation:** Answer questions and chat

Just tell me what you'd like me to do!
""",
            'ur': """  # ROMAN URDU HELP
🤖 **Main aap ki in cheezon mein madad kar sakta hoon:**

📱 **Messaging:** WhatsApp/SMS message bhejna
⏰ **Scheduling:** Yaad dahaniyan, alarms, timer set karna
🌤️ **Information:** Mausam, khabrain, stock ki qeemtein
🔍 **Search:** Web search aur information
💬 **Conversation:** Sawalon ke jawab aur baat cheet

Bas mujhe batain ke aap mujh se kya karana chahte hain!
""",
            'hi': """
🤖 **मैं आपकी इन चीजों में मदद कर सकता हूँ:**

📱 **मैसेजिंग:** व्हाट्सएप/एसएमएस मैसेज भेजना
⏰ **शेड्यूलिंग:** रिमाइंडर, अलार्म, टाइमर सेट करना
🌤️ **जानकारी:** मौसम, खबरें, स्टॉक कीमतें
🔍 **खोज:** वेब खोज और जानकारी
💬 **बातचीत:** सवालों के जवाब और चैट

बस मुझे बताएं कि आप मुझसे क्या कराना चाहते हैं!
""",
            'ps': """
🤖 **زه کولی شم تاسو سره په دې شیانو کې مرسته وکړم:**

📱 **رسالي:** WhatsApp/SMS رسالي لیږل
⏰ **مهالویش:** یادونې، الخبار، ټایمر تنظیم کول
🌤️ **معلومات:** هوا، خبرې، د سهم قیمتونه
🔍 **لټون:** ویب لټون او معلومات
💬 **خبرې اترې:** پوښتنو ته ځوابونه او خبرې

یوازې ما ته ووایاست چې تاسو څه غواړئ چې زه وکړم!
"""
        }
        
        return responses.get(lang, responses['en'])

    async def speech_to_text(self, audio_data=None, language: str = None) -> Tuple[str, str]:
        """
        Convert speech to text with automatic language detection
        Returns: (text, detected_language)
        """
        try:
            if not language:
                language = self.current_language
            
            # Map language codes to speech recognition languages
            sr_languages = {
                'ur': 'ur-PK',  # Urdu Pakistan
                'ps': 'ps-AF',  # Pashto Afghanistan  
                'en': 'en-US',  # English US
                'hi': 'hi-IN'   # Hindi India
            }
            
            sr_lang = sr_languages.get(language, 'ur-PK')
            
            if audio_data is None:
                # Use microphone input
                with sr.Microphone() as source:
                    logger.info(f"Listening for {language} speech...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=10)
            else:
                audio = audio_data
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio, language=sr_lang)
            
            # Convert Urdu script to Roman Urdu if detected
            if language == 'ur':
                text = self._convert_urdu_to_roman(text)
            
            # Detect actual language of spoken text
            detected_lang = await self.detect_language(text)
            
            logger.info(f"Speech recognized: '{text}' in {detected_lang}")
            return text, detected_lang
            
        except sr.WaitTimeoutError:
            logger.warning("Speech recognition timeout")
            return "", self.current_language
        except sr.UnknownValueError:
            logger.warning("Could not understand speech")
            return "", self.current_language
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return "", self.current_language
        except Exception as e:
            logger.error(f"Unexpected speech recognition error: {e}")
            return "", self.current_language

    def _convert_urdu_to_roman(self, urdu_text: str) -> str:
        """Convert Urdu script to Roman Urdu"""
        # Basic Urdu to Roman conversion mapping
        urdu_roman_map = {
            'کیا': 'kya',
            'ہے': 'hai',
            'میں': 'main',
            'آپ': 'aap',
            'کر': 'kar',
            'سکتے': 'sakte',
            'ہو': 'ho',
            'میری': 'meri',
            'مدد': 'madad',
            'سن': 'sun',
            'رہے': 'rahe',
            'جواب': 'jawab',
            'دو': 'do',
            'ہوں': 'hoon',
            'شکریہ': 'shukriya',
            'السلام': 'salam',
            'علیکم': 'alaikum',
            'ٹھیک': 'theek',
            'خدا': 'khuda',
            'حافظ': 'hafiz'
        }
        
        roman_text = urdu_text
        for urdu, roman in urdu_roman_map.items():
            roman_text = roman_text.replace(urdu, roman)
        
        return roman_text

    async def text_to_speech(self, text: str, language: str = None) -> bool:
        """
        Convert text to speech in specified language
        Uses edge-tts for online or pyttsx3 for offline
        """
        try:
            if not language:
                language = self.current_language
            
            if not text or len(text.strip()) == 0:
                return False
            
            # For Roman Urdu, we need to convert to Urdu script for TTS
            if language == 'ur':
                text = self._convert_roman_to_urdu(text)
            
            lang_config = self.language_configs.get(language, self.language_configs['ur'])
            voice = lang_config['voice']
            
            # Try online TTS first (better quality)
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save("temp_speech.mp3")
                
                # Play the audio file
                if os.name == 'nt':  # Windows
                    os.system("start temp_speech.mp3")
                else:  # macOS/Linux
                    os.system("afplay temp_speech.mp3" if os.name == 'posix' else "mpg123 temp_speech.mp3")
                
                logger.info(f"Spoke text in {language}: {text[:50]}...")
                return True
                
            except Exception as e:
                logger.warning(f"Online TTS failed, falling back to offline: {e}")
                
                # Fallback to offline TTS
                if self.voice_engine:
                    self.voice_engine.say(text)
                    self.voice_engine.runAndWait()
                    logger.info(f"Spoke text offline in {language}: {text[:50]}...")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return False

    def _convert_roman_to_urdu(self, roman_text: str) -> str:
        """Convert Roman Urdu to Urdu script for TTS"""
        # Basic Roman to Urdu conversion mapping
        roman_urdu_map = {
            'kya': 'کیا',
            'hai': 'ہے',
            'main': 'میں', 
            'aap': 'آپ',
            'kar': 'کر',
            'sakte': 'سکتے',
            'ho': 'ہو',
            'meri': 'میری',
            'madad': 'مدد',
            'sun': 'سن',
            'rahe': 'رہے',
            'jawab': 'جواب',
            'do': 'دو',
            'hoon': 'ہوں',
            'shukriya': 'شکریہ',
            'salam': 'السلام',
            'alaikum': 'علیکم',
            'theek': 'ٹھیک',
            'khuda': 'خدا',
            'hafiz': 'حافظ'
        }
        
        urdu_text = roman_text
        for roman, urdu in roman_urdu_map.items():
            urdu_text = urdu_text.replace(roman, urdu)
        
        return urdu_text

    def set_language(self, language: str) -> bool:
        """Set current language for input/output"""
        if language in self.language_configs:
            self.current_language = language
            logger.info(f"Language set to: {self.language_configs[language]['name']}")
            return True
        return False

    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a supported language"""
        return self.language_configs.get(language, {})

    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with names"""
        return {code: info['name'] for code, info in self.language_configs.items()}

    def is_rtl_language(self, language: str = None) -> bool:
        """Check if language is right-to-left"""
        if not language:
            language = self.current_language
        return self.language_configs.get(language, {}).get('rtl', False)


class UrduPashtoTranslator:
    """
    Translation support between Roman Urdu, Pashto, and English
    Uses AI for context-aware translation
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.translation_cache = {}
        
        # Common phrases and greetings - UPDATED TO ROMAN URDU
        self.common_phrases = {
            'ur': {  # ROMAN URDU PHRASES
                'greeting': 'Salam alaikum',
                'how_are_you': 'Aap kaise hain?',
                'thank_you': 'Shukriya',
                'goodbye': 'Khuda hafiz',
                'yes': 'Ji haan',
                'no': 'Nahi',
                'please': 'Barah e karam',
                'sorry': 'Maaf kijiye'
            },
            'ps': {
                'greeting': 'سلام',
                'how_are_you': 'تاسو څنګه یاست؟',
                'thank_you': 'مننه',
                'goodbye': 'خداى پامان',
                'yes': 'هو',
                'no': 'نه',
                'please': 'لطفاً',
                'sorry': 'وبخښئ'
            },
            'en': {
                'greeting': 'Hello',
                'how_are_you': 'How are you?',
                'thank_you': 'Thank you',
                'goodbye': 'Goodbye',
                'yes': 'Yes',
                'no': 'No',
                'please': 'Please',
                'sorry': 'Sorry'
            },
            'hi': {
                'greeting': 'नमस्ते',
                'how_are_you': 'आप कैसे हैं?',
                'thank_you': 'धन्यवाद',
                'goodbye': 'अलविदा',
                'yes': 'हाँ',
                'no': 'नहीं',
                'please': 'कृपया',
                'sorry': 'माफ़ कीजिए'
            }
        }
    
    async def translate_text(self, text: str, target_lang: str, source_lang: str = None) -> str:
        """
        Translate text between supported languages using AI
        """
        try:
            if not source_lang:
                source_lang = await self.detect_language_simple(text)
            
            if source_lang == target_lang:
                return text
            
            # Check cache first
            cache_key = f"{source_lang}_{target_lang}_{hash(text)}"
            if cache_key in self.translation_cache:
                return self.translation_cache[cache_key]
            
            # Use AI for translation
            prompt = f"""
            Translate the following text from {self.get_language_name(source_lang)} to {self.get_language_name(target_lang)}.
            Maintain the meaning, tone, and cultural context.
            
            Text to translate: "{text}"
            
            Provide only the translation without any additional text.
            """
            
            # FIX: Use proper brain call
            if hasattr(self.brain, 'ask'):
                translation = await self.brain.ask([{"role": "system", "content": prompt}])
            else:
                # Fallback translation
                translation = self._simple_translation_fallback(text, source_lang, target_lang)
            
            translation = translation.strip()
            
            # Cache the translation
            self.translation_cache[cache_key] = translation
            
            logger.info(f"Translated from {source_lang} to {target_lang}: {text[:30]}... -> {translation[:30]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original text on error
    
    def _simple_translation_fallback(self, text: str, source_lang: str, target_lang: str) -> str:
        """Simple fallback translation"""
        # Basic translation mappings including Roman Urdu
        translations = {
            ('ur', 'en'): {
                'salam alaikum': 'Hello',
                'shukriya': 'Thank you',
                'aap kaise ho': 'How are you',
                'main theek hoon': 'I am fine',
                'madad': 'Help'
            },
            ('en', 'ur'): {
                'hello': 'Salam alaikum',
                'thank you': 'Shukriya', 
                'how are you': 'Aap kaise hain',
                'i am fine': 'Main theek hoon',
                'help': 'Madad'
            },
            ('hi', 'en'): {
                'नमस्ते': 'Hello',
                'धन्यवाद': 'Thank you',
                'कैसे हो': 'How are you',
            },
            ('en', 'hi'): {
                'hello': 'नमस्ते',
                'thank you': 'धन्यवाद',
                'how are you': 'कैसे हो',
            }
        }
        
        key = (source_lang, target_lang)
        if key in translations:
            text_lower = text.lower()
            for original, translated in translations[key].items():
                if original.lower() in text_lower:
                    return translated
        
        return text
    
    def detect_language_simple(self, text: str) -> str:
        """Simple language detection for translation"""
        # Check for Roman Urdu patterns
        roman_urdu_patterns = ['aap', 'main', 'kaise', 'ho', 'hai', 'hain', 'theek', 'shukriya', 'madad']
        roman_urdu_score = sum(1 for pattern in roman_urdu_patterns if pattern in text.lower())
        
        urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        pashto_chars = len(re.findall(r'[ښړګڼ]', text))
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if roman_urdu_score > 2:
            return 'ur'
        elif urdu_chars > english_chars and urdu_chars > pashto_chars and urdu_chars > hindi_chars:
            return 'ur'
        elif pashto_chars > english_chars and pashto_chars > urdu_chars and pashto_chars > hindi_chars:
            return 'ps'
        elif hindi_chars > english_chars and hindi_chars > urdu_chars and hindi_chars > pashto_chars:
            return 'hi'
        else:
            return 'en'
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        names = {'ur': 'Roman Urdu', 'ps': 'Pashto', 'en': 'English', 'hi': 'Hindi'}
        return names.get(lang_code, 'Unknown')
    
    def get_common_phrase(self, phrase_key: str, language: str) -> str:
        """Get common phrase in specified language"""
        return self.common_phrases.get(language, {}).get(phrase_key, phrase_key)


class GuaranteedResponseBrain:
    """Brain that guarantees responses even when AI fails"""
    
    def __init__(self, original_brain, multilingual_manager):
        self.original_brain = original_brain
        self.multilingual_manager = multilingual_manager
        self.response_count = 0
        logger.info("Guaranteed Response Brain initialized")
    
    async def ask(self, messages: List[Dict[str, str]]) -> str:
        """Ask with guaranteed response"""
        self.response_count += 1
        
        # Get the last user message
        last_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg.get("content", "")
                break
        
        if not last_message:
            return self._get_fallback_response('en')
        
        # Try to get immediate response first
        detected_lang = await self.multilingual_manager.detect_language(last_message)
        immediate_response = self.multilingual_manager.get_immediate_response(last_message, detected_lang)
        
        if immediate_response:
            return immediate_response
        
        # Try original brain with timeout
        try:
            response = await asyncio.wait_for(
                self.original_brain.ask(messages), 
                timeout=10.0  # 10 second timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning("AI response timeout, using fallback")
        except Exception as e:
            logger.error(f"AI brain error: {e}")
        
        # Final fallback
        return self._get_fallback_response(detected_lang)
    
    def _get_fallback_response(self, lang: str) -> str:
        """Get fallback response when everything else fails - UPDATED TO ROMAN URDU"""
        fallbacks = {
            'en': [
                "I'm here! How can I help you today?",
                "I'm listening. What would you like me to do?",
                "Hello! I'm ready to assist you.",
                "I'm available to help with messages, reminders, or information.",
                "Yes, I'm here! You can ask me to send messages, set reminders, or search for information."
            ],
            'ur': [  # ROMAN URDU FALLBACKS
                "Main yahan hoon! Aaj main aap ki kis tarah madad kar sakta hoon?",
                "Main sun raha hoon. Aap mujh se kya karana chahenge?",
                "Hello! Main aap ki madad ke liye tayyar hoon.",
                "Main message bhejne, yaad dahaniyan set karne ya information dene ke liye available hoon.",
                "Ji haan, main yahan hoon! Aap mujh se message bhejne, yaad dahaniyan set karne ya information dhundhne ke liye keh sakte hain."
            ],
            'hi': [
                "मैं यहाँ हूँ! आज मैं आपकी कैसे मदद कर सकता हूँ?",
                "मैं सुन रहा हूँ। आप मुझसे क्या कराना चाहेंगे?",
                "नमस्ते! मैं आपकी सहायता के लिए तैयार हूँ।",
                "मैं संदेश भेजने, रिमाइंडर सेट करने या जानकारी देने के लिए उपलब्ध हूँ।",
                "हाँ, मैं यहाँ हूँ! आप मुझसे संदेश भेजने, रिमाइंडर सेट करने या जानकारी खोजने के लिए कह सकते हैं।"
            ],
            'ps': [
                "زم دلته یم! نن زه تاسو سره څنګه مرسته کولی شم؟",
                "زه اورم. تاسو څه غواړئ چې زه وکړم؟",
                "سلام! زه د تاسو د مرستې لپاره چمتو یم.",
                "زه د رسالي لیږلو، د یادونو تنظیمولو یا د معلوماتو ورکولو لپاره شتون لرم.",
                "هو، زم دلته یم! تاسو کولی شئ ما ته ووایاست چې رسالي لیږل، یادونې تنظیم کول یا معلومات موندل."
            ]
        }
        
        return random.choice(fallbacks.get(lang, fallbacks['en']))


class MultilingualBrain:
    """
    FIXED: AI brain with multilingual understanding and response generation
    """
    
    def __init__(self, brain, multilingual_manager, translator):
        self.brain = brain
        self.multilingual_manager = multilingual_manager
        self.translator = translator
        self.conversation_context = {}
        
        # Ensure brain has ask method
        if not hasattr(self.brain, 'ask'):
            self._add_fallback_ask_method()
    
    def _add_fallback_ask_method(self):
        """Add fallback ask method if brain doesn't have one"""
        async def fallback_ask(messages):
            last_message = messages[-1]['content'] if messages else ""
            return f"I understand you said: {last_message}. How can I help you?"
        
        self.brain.ask = fallback_ask
        logger.info("Added fallback ask method to brain")
    
    async def ask(self, messages):
        """
        Main ask method that delegates to the underlying brain
        This fixes the 'MultilingualBrain' object has no attribute 'ask' error
        """
        try:
            response = await self.brain.ask(messages)
            
            # CONVERSION: If input was Roman Urdu, convert response to Roman Urdu
            if messages and len(messages) > 0:
                last_user_message = messages[-1].get('content', '')
                if await self._is_roman_urdu_input(last_user_message):
                    response = self._convert_urdu_to_roman(response)
            
            return response
        except Exception as e:
            logger.error(f"Brain ask failed: {e}")
            # Return a simple fallback response
            last_message = messages[-1]['content'] if messages else "Hello"
            fallback_response = f"I understand: {last_message}. How can I assist you?"
            
            # Convert to Roman Urdu if needed
            if messages and len(messages) > 0:
                last_user_message = messages[-1].get('content', '')
                if await self._is_roman_urdu_input(last_user_message):
                    fallback_response = self._convert_english_to_roman_urdu(fallback_response)
            
            return fallback_response
    
    async def _is_roman_urdu_input(self, text: str) -> bool:
        """Check if input appears to be Roman Urdu"""
        if not text:
            return False
        
        # Roman Urdu indicators
        roman_urdu_indicators = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'kyun', 'kahan', 'kaun', 'acha', 'bilkul'
        ]
        
        text_lower = text.lower()
        score = sum(1 for indicator in roman_urdu_indicators if indicator in text_lower)
        
        # Also check for absence of Urdu script characters
        has_urdu_script = bool(re.search(r'[\u0600-\u06FF]', text))
        
        return score >= 2 and not has_urdu_script
    
    def _convert_urdu_to_roman(self, urdu_text: str) -> str:
        """Convert Urdu script to Roman Urdu"""
        # Extended Urdu to Roman conversion mapping
        urdu_roman_map = {
            'میں': 'main',
            'ہوں': 'hoon',
            'ٹھیک': 'theek',
            'شکریہ': 'shukriya',
            'آپ': 'aap',
            'کیسے': 'kaise',
            'ہیں': 'hain',
            'کیا': 'kya',
            'کر': 'kar',
            'سکتے': 'sakte',
            'سکتا': 'sakta',
            'سکتی': 'sakti',
            'ہو': 'ho',
            'میری': 'meri',
            'مدد': 'madad',
            'سن': 'sun',
            'رہے': 'rahe',
            'جواب': 'jawab',
            'دو': 'do',
            'السلام': 'salam',
            'علیکم': 'alaikum',
            'خدا': 'khuda',
            'حافظ': 'hafiz',
            'ہے': 'hai',
            'تھا': 'tha',
            'تھی': 'thi',
            'تھے': 'the',
            'اور': 'aur',
            'لیکن': 'lekin',
            'اگر': 'agar',
            'تو': 'to',
            'بہت': 'bahut',
            'اچھا': 'acha',
            'برا': 'bura',
            'اب': 'ab',
            'پھر': 'phir',
            'کب': 'kab',
            'کہاں': 'kahan',
            'کیوں': 'kyun',
            'کون': 'kaun',
            'کیا': 'kya',
            'جی': 'ji',
            'نہیں': 'nahi',
            'ہاں': 'haan',
            'شاید': 'shayad',
            'ضرور': 'zaroor',
            'پہلے': 'pehle',
            'بعد': 'baad',
            'ساتھ': 'sath',
            'کے': 'ke',
            'کی': 'ki',
            'کا': 'ka',
            'سے': 'se',
            'پر': 'par',
            'مےں': 'mein',
            'اوپر': 'upar',
            'نیچے': 'neeche',
            'دائیں': 'dayein',
            'بائیں': 'bayein',
            'آگے': 'aage',
            'پیچھے': 'peeche'
        }
        
        roman_text = urdu_text
        for urdu, roman in urdu_roman_map.items():
            roman_text = roman_text.replace(urdu, roman)
        
        return roman_text
    
    def _convert_english_to_roman_urdu(self, english_text: str) -> str:
        """Convert English responses to Roman Urdu equivalents"""
        english_roman_map = {
            "i'm fine": "main theek hoon",
            "thank you": "shukriya",
            "how are you": "aap kaise hain",
            "i can help": "main madad kar sakta hoon",
            "hello": "salam alaikum",
            "goodbye": "khuda hafiz",
            "yes": "ji haan",
            "no": "nahi",
            "please": "barah e karam",
            "sorry": "maaf kijiye",
            "i understand": "main samjha",
            "how can i help": "main kis tarah madad kar sakta hoon",
            "what can i do": "main kya kar sakta hoon"
        }
        
        roman_text = english_text.lower()
        for english, roman in english_roman_map.items():
            roman_text = roman_text.replace(english, roman)
        
        # Capitalize first letter
        if roman_text:
            roman_text = roman_text[0].upper() + roman_text[1:]
        
        return roman_text
    
    async def ask_multilingual(self, text: str, input_language: str, output_language: str = None) -> str:
        """
        Process query in any language and respond in appropriate language
        """
        try:
            if not output_language:
                output_language = input_language
            
            # Build context-aware prompt
            prompt = self._build_multilingual_prompt(text, input_language, output_language)
            
            # Get AI response - FIXED: Use our own ask method
            try:
                response = await self.ask([{"role": "system", "content": prompt}])
            except Exception as e:
                logger.warning(f"Brain ask failed, using fallback: {e}")
                response = self._get_fallback_response(text, input_language)
            
            # Clean and return response
            cleaned_response = self._clean_ai_response(response)
            
            logger.info(f"Multilingual response: {input_language}->{output_language}")
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Multilingual processing error: {e}")
            return self.translator.get_common_phrase('sorry', output_language or input_language)
    
    def _build_multilingual_prompt(self, text: str, input_lang: str, output_lang: str) -> str:
        """Build prompt for multilingual AI interaction"""
        
        input_lang_name = self.translator.get_language_name(input_lang)
        output_lang_name = self.translator.get_language_name(output_lang)
        
        # Special instruction for Roman Urdu
        extra_instruction = ""
        if output_lang == 'ur':
            extra_instruction = "IMPORTANT: For Urdu, respond in ROMAN URDU (English letters) not Urdu script. Use words like 'main', 'aap', 'kaise', 'hoon', 'theek', 'shukriya' etc."
        
        return f"""
        You are Shadow AI, a helpful assistant that understands multiple languages.
        
        USER'S LANGUAGE: {input_lang_name}
        RESPONSE LANGUAGE: {output_lang_name}
        {extra_instruction}
        
        USER QUERY: "{text}"
        
        INSTRUCTIONS:
        1. Understand the user's query in {input_lang_name}
        2. Respond naturally in {output_lang_name}
        3. Maintain cultural appropriateness for the language
        4. Be helpful, accurate, and conversational
        5. {extra_instruction}
        
        IMPORTANT: Respond ONLY in {output_lang_name}.
        
        Respond naturally and helpfully in {output_lang_name}:
        """
    
    def _get_fallback_response(self, text: str, language: str) -> str:
        """Get fallback response when brain fails - UPDATED TO ROMAN URDU"""
        fallback_responses = {
            'ur': "Salam alaikum! Main Shadow AI hoon. Aap kaise madad kar sakta hoon?",  # ROMAN URDU
            'ps': "سلام! زه شاڈو AI یم۔ تاسو څنګه مرسته کولی شم؟",
            'en': "Hello! I'm Shadow AI. How can I help you today?",
            'hi': "नमस्ते! मैं शैडो AI हूँ। मैं आपकी कैसे मदद कर सकता हूँ?"
        }
        
        return fallback_responses.get(language, fallback_responses['en'])
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response and remove any meta-commentary"""
        import re
        # Remove common AI disclaimers and meta-text
        clean_response = re.sub(r'^(As an AI assistant|I am an AI|As a language model).*?\.\s*', '', response, flags=re.IGNORECASE)
        clean_response = re.sub(r'\s*\([^)]*\)', '', clean_response)
        clean_response = clean_response.strip()
        
        return clean_response if clean_response else response
    
    def update_conversation_context(self, user_input: str, ai_response: str, language: str):
        """Update conversation context for continuity"""
        from datetime import datetime
        self.conversation_context = {
            'last_user_input': user_input[:100],
            'last_ai_response': ai_response[:100],
            'language': language,
            'timestamp': datetime.now().isoformat()
        }


def create_enhanced_multilingual_system(brain):
    """Create enhanced multilingual system with guaranteed responses"""
    multilingual_manager = MultilingualManager()
    guaranteed_brain = GuaranteedResponseBrain(brain, multilingual_manager)
    translator = UrduPashtoTranslator(guaranteed_brain)
    multilingual_brain = MultilingualBrain(guaranteed_brain, multilingual_manager, translator)
    
    return multilingual_manager, translator, multilingual_brain


# Backward compatibility function
def create_multilingual_system(brain):
    """Legacy function for backward compatibility"""
    return create_enhanced_multilingual_system(brain)
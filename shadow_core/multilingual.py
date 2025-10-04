# shadow_core/multilingual.py
"""
Multilingual support for Shadow AI Agent
Urdu and Pashto language support with speech recognition and synthesis
"""

import logging
import asyncio
import speech_recognition as sr
from typing import Dict, Any, Optional, Tuple
import pyttsx3
import edge_tts
import os
from langdetect import detect, LangDetectException
import re
from shadow_core.urdu_nlp import AdvancedUrduNLP
from shadow_core.urdu_speech_enhancer import UrduSpeechEnhancer

logger = logging.getLogger(__name__)

class MultilingualManager:
    """
    Manages multilingual support for Urdu, Pashto, and English
    Handles speech recognition, text-to-speech, and language detection
    """
    
    def __init__(self):
        self.supported_languages = {
            'en': {'name': 'English', 'voice': 'en-US-ChristopherNeural', 'rtl': False},
            'ur': {'name': 'Urdu', 'voice': 'ur-PK-AsadNeural', 'rtl': True},
            'ps': {'name': 'Pashto', 'voice': 'ps-AF-GulNawazNeural', 'rtl': True}
        }
        
        self.urdu_nlp = None  # Will be set when brain is available
        self.urdu_speech_enhancer = None
        self.default_language = 'ur'  # Urdu as default
        self.current_language = self.default_language
        self.voice_engine = None
        self.recognizer = sr.Recognizer()
        
        # Language detection patterns
        self.language_patterns = {
            'ur': [
                r'[\u0600-\u06FF]',  # Arabic script for Urdu
                r'[ہےۓ]',  # Common Urdu characters
            ],
            'ps': [
                r'[\u0600-\u06FF]',  # Arabic script for Pashto
                r'[ښړګڼ]',  # Pashto-specific characters
            ],
            'en': [
                r'[a-zA-Z]',  # English letters
            ]
        }
        
        self._initialize_tts()
        logger.info("Multilingual Manager initialized")
        
    def set_brain(self, brain):
        """Set brain for Urdu NLP (called after brain initialization)"""
        self.urdu_nlp = AdvancedUrduNLP(brain)
        self.urdu_speech_enhancer = UrduSpeechEnhancer(self.urdu_nlp)
        logger.info("Enhanced Urdu NLP and Speech modules initialized")
    
    async def super_understand_urdu(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Super intelligent Urdu understanding with enhanced NLP
        """
        if not self.urdu_nlp:
            return await self.detect_language(text)
        
        return await self.urdu_nlp.super_understand(text, context)
    
    async def enhanced_urdu_listen(self, timeout: int = 10) -> Tuple[Optional[str], float]:
        """
        Enhanced Urdu speech recognition
        """
        if not self.urdu_speech_enhancer:
            # Fallback to basic listening
            return await self.speech_to_text(language='ur')
        
        return await self.urdu_speech_enhancer.enhanced_urdu_listen(timeout)    
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
        """
        Detect language of input text with high accuracy
        Returns: language code ('ur', 'ps', 'en')
        """
        if not text or len(text.strip()) == 0:
            return self.current_language
        
        # Clean text for detection
        clean_text = text.strip()
        
        # Method 1: Check for script patterns
        script_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, clean_text)
                score += len(matches)
            script_scores[lang] = score
        
        # Find language with highest script score
        best_script_lang = max(script_scores.items(), key=lambda x: x[1])
        if best_script_lang[1] > 0:
            return best_script_lang[0]
        
        # Method 2: Use langdetect for ambiguous cases
        try:
            detected_lang = detect(clean_text)
            if detected_lang in self.supported_languages:
                return detected_lang
        except LangDetectException:
            pass
        
        # Method 3: Fallback to current language
        return self.current_language
    
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
                'en': 'en-US'   # English US
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
            
            lang_config = self.supported_languages.get(language, self.supported_languages['ur'])
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
    
    def set_language(self, language: str) -> bool:
        """Set current language for input/output"""
        if language in self.supported_languages:
            self.current_language = language
            logger.info(f"Language set to: {self.supported_languages[language]['name']}")
            return True
        return False
    
    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get information about a supported language"""
        return self.supported_languages.get(language, {})
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages with names"""
        return {code: info['name'] for code, info in self.supported_languages.items()}
    
    def is_rtl_language(self, language: str = None) -> bool:
        """Check if language is right-to-left"""
        if not language:
            language = self.current_language
        return self.supported_languages.get(language, {}).get('rtl', False)


class UrduPashtoTranslator:
    """
    Translation support between Urdu, Pashto, and English
    Uses AI for context-aware translation
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.translation_cache = {}
        
        # Common phrases and greetings
        self.common_phrases = {
            'ur': {
                'greeting': 'السلام علیکم',
                'how_are_you': 'آپ کیسے ہیں؟',
                'thank_you': 'شکریہ',
                'goodbye': 'خدا حافظ',
                'yes': 'جی ہاں',
                'no': 'نہیں',
                'please': 'براہ کرم',
                'sorry': 'معاف کیجئے گا'
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
            
            translation = await self.brain.ask([{"role": "system", "content": prompt}])
            translation = translation.strip()
            
            # Cache the translation
            self.translation_cache[cache_key] = translation
            
            logger.info(f"Translated from {source_lang} to {target_lang}: {text[:30]}... -> {translation[:30]}...")
            return translation
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text  # Return original text on error
    
    def detect_language_simple(self, text: str) -> str:
        """Simple language detection for translation"""
        urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        pashto_chars = len(re.findall(r'[ښړګڼ]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if urdu_chars > english_chars and urdu_chars > pashto_chars:
            return 'ur'
        elif pashto_chars > english_chars and pashto_chars > urdu_chars:
            return 'ps'
        else:
            return 'en'
    
    def get_language_name(self, lang_code: str) -> str:
        """Get language name from code"""
        names = {'ur': 'Urdu', 'ps': 'Pashto', 'en': 'English'}
        return names.get(lang_code, 'Unknown')
    
    def get_common_phrase(self, phrase_key: str, language: str) -> str:
        """Get common phrase in specified language"""
        return self.common_phrases.get(language, {}).get(phrase_key, phrase_key)


class MultilingualBrain:
    """
    AI brain with multilingual understanding and response generation
    """
    
    def __init__(self, brain, multilingual_manager, translator):
        self.brain = brain
        self.multilingual_manager = multilingual_manager
        self.translator = translator
        self.conversation_context = {}
        
    async def ask(self, messages):
        """
        Compatibility method that works with the existing brain interface
        This allows MultilingualBrain to be used anywhere the original brain is used
        """
        try:
            # Extract the user's message from the messages
            user_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "")
                    break
            
            if not user_message:
                # If no user message found, use the last message
                user_message = messages[-1].get("content", "") if messages else ""
            
            # Detect input language
            input_language = await self.multilingual_manager.detect_language(user_message)
            
            # Use multilingual processing
            response = await self.ask_multilingual(user_message, input_language, input_language)
            
            return response
            
        except Exception as e:
            logger.error(f"MultilingualBrain.ask error: {e}")
            # Fallback to original brain
            return await self.brain.ask(messages)    
    
    async def ask_multilingual(self, text: str, input_language: str, output_language: str = None) -> str:
        """
        Process query in any language and respond in appropriate language
        """
        try:
            if not output_language:
                output_language = input_language
            
            # Build context-aware prompt
            prompt = self._build_multilingual_prompt(text, input_language, output_language)
            
            # Get AI response
            response = await self.brain.ask([{"role": "system", "content": prompt}])
            
            # Clean and return response
            cleaned_response = self._clean_ai_response(response)
            
            logger.info(f"Multilingual response: {input_language}->{output_language}")
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Multilingual brain error: {e}")
            return self.translator.get_common_phrase('sorry', output_language or input_language)
    
    def _build_multilingual_prompt(self, text: str, input_lang: str, output_lang: str) -> str:
        """Build prompt for multilingual AI interaction"""
        
        input_lang_name = self.translator.get_language_name(input_lang)
        output_lang_name = self.translator.get_language_name(output_lang)
        
        return f"""
        You are Shadow AI, a helpful assistant that understands multiple languages.
        
        USER'S LANGUAGE: {input_lang_name}
        RESPONSE LANGUAGE: {output_lang_name}
        
        USER QUERY: "{text}"
        
        INSTRUCTIONS:
        1. Understand the user's query in {input_lang_name}
        2. Respond naturally in {output_lang_name}
        3. Maintain cultural appropriateness for the language
        4. Be helpful, accurate, and conversational
        5. If the query is in a mix of languages, respond in the dominant language
        
        IMPORTANT: Respond ONLY in {output_lang_name}. Do not include any English or other language text unless specifically requested.
        
        For Urdu responses: Use proper Urdu script and cultural context
        For Pashto responses: Use proper Pashto script and cultural context  
        For English responses: Use natural English
        
        Current conversation context: {self.conversation_context}
        
        Respond naturally and helpfully in {output_lang_name}:
        """
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response and remove any meta-commentary"""
        # Remove common AI disclaimers and meta-text
        clean_response = re.sub(r'^(As an AI assistant|I am an AI|As a language model).*?\.\s*', '', response, flags=re.IGNORECASE)
        clean_response = re.sub(r'\s*\([^)]*\)', '', clean_response)  # Remove parentheses content
        clean_response = clean_response.strip()
        
        return clean_response if clean_response else response
    
    def update_conversation_context(self, user_input: str, ai_response: str, language: str):
        """Update conversation context for continuity"""
        self.conversation_context = {
            'last_user_input': user_input[:100],
            'last_ai_response': ai_response[:100],
            'language': language,
            'timestamp': self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
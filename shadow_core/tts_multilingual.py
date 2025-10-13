# shadow_core/tts_multilingual.py
"""
Multilingual Text-to-Speech module with Urdu, Pashto, and Roman script support
"""

import logging
import asyncio
import edge_tts
import pyttsx3
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

class MultilingualTTS:
    """
    Text-to-Speech with Urdu, Pashto, English, and Roman script support
    Uses edge-tts for online and pyttsx3 for offline
    """
    
    def __init__(self, multilingual_manager):
        self.multilingual_manager = multilingual_manager
        self.online_voices = {
            'ur': 'ur-PK-AsadNeural',      # Urdu male voice
            'ps': 'ps-AF-GulNawazNeural',  # Pashto male voice  
            'en': 'en-US-ChristopherNeural', # English male voice
            'hi': 'hi-IN-MadhurNeural'      # Hindi male voice
        }
        self.offline_engine = None
        self._initialize_offline_tts()
        
        # Roman to native script conversion mappings
        self.roman_to_urdu_map = {
            'main': 'میں',
            'hoon': 'ہوں',
            'hai': 'ہے',
            'hain': 'ہیں',
            'ho': 'ہو',
            'theek': 'ٹھیک',
            'shukriya': 'شکریہ',
            'aap': 'آپ',
            'kaise': 'کیسے',
            'kya': 'کیا',
            'kar': 'کر',
            'sakte': 'سکتے',
            'sakta': 'سکتا',
            'sakti': 'سکتی',
            'mujhe': 'مجھے',
            'meri': 'میری',
            'madad': 'مدد',
            'sun': 'سن',
            'rahe': 'رہے',
            'jawab': 'جواب',
            'do': 'دو',
            'salam': 'السلام',
            'alaikum': 'علیکم',
            'khuda': 'خدا',
            'hafiz': 'حافظ',
            'aur': 'اور',
            'lekin': 'لیکن',
            'agar': 'اگر',
            'to': 'تو',
            'bahut': 'بہت',
            'acha': 'اچھا',
            'bura': 'برا',
            'ab': 'اب',
            'phir': 'پھر',
            'kab': 'کب',
            'kahan': 'کہاں',
            'kyun': 'کیوں',
            'kaun': 'کون',
            'ji': 'جی',
            'nahi': 'نہیں',
            'haan': 'ہاں',
            'shayad': 'شاید',
            'zaroor': 'ضرور',
            'pehle': 'پہلے',
            'baad': 'بعد',
            'sath': 'ساتھ',
            'aaj': 'آج',
            'kal': 'کل',
            'savere': 'سویرے',
            'shaam': 'شام',
            'raat': 'رات'
        }
        
        self.roman_to_pashto_map = {
            'sta': 'سته',
            'yast': 'یاست',
            'kaw': 'کولی',
            'kawam': 'کولی شم',
            'kawu': 'کولی شو',
            'kawalai': 'کولای',
            'kawalam': 'کولای شم',
            'she': 'شئ',
            'ma': 'مه',
            'ta': 'ته',
            'de': 'دی',
            'mo': 'مو',
            'sta': 'ستا',
            'zma': 'زما',
            'da': 'د',
            'pa': 'په',
            'ke': 'کې',
            'na': 'نه',
            'si': 'سی',
            'shi': 'شی',
            'yi': 'یی',
            'wi': 'وی',
            'shi': 'شي',
            'kare': 'کړی',
            'kare': 'کړئ',
            'kram': 'کړم',
            'kru': 'کړو',
            'kre': 'کړې',
            'kri': 'کړي',
            'salam': 'سلام',
            'manana': 'مننه',
            'mehrbani': 'مهرباني',
            'khudai paman': 'خدای پامان',
            'tsanga': 'څنګه',
            'tse': 'څه',
            'wale': 'ولې',
            'chere': 'چېرې',
            'cha': 'چا',
            'kala': 'کله',
            'kha': 'ښه',
            'bad': 'بد',
            'os': 'اوس',
            'bya': 'بیا',
            'lag': 'لږ',
            'der': 'ډیر',
            'dera': 'ډېر',
            'marasta': 'مرسته',
            'komak': 'کومک',
            'marasta kawa': 'مرسته کوه',
            'komak kawa': 'کومک کوه',
            'pokhtana': 'پوښتنه',
            'zwab': 'ځواب',
            'wwaya': 'ووايه',
            'or': 'اور',
            'orma': 'اورمه'
        }
    
    def _initialize_offline_tts(self):
        """Initialize offline TTS engine"""
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty('rate', 150)
            self.offline_engine.setProperty('volume', 0.8)
            logger.info("Offline TTS engine initialized")
        except Exception as e:
            logger.warning(f"Could not initialize offline TTS: {e}")
            self.offline_engine = None
    
    async def speak(self, text: str, language: str = None) -> bool:
        """
        Speak text in specified language
        Returns: success status
        """
        if not language:
            language = self.multilingual_manager.current_language
        
        if not text or len(text.strip()) == 0:
            return False
        
        # Convert Roman script to native script for TTS
        processed_text = await self._convert_roman_to_native(text, language)
        
        # Try online TTS first (better quality)
        online_success = await self._speak_online(processed_text, language)
        if online_success:
            return True
        
        # Fallback to offline TTS
        offline_success = self._speak_offline(processed_text, language)
        return offline_success
    
    async def _convert_roman_to_native(self, text: str, language: str) -> str:
        """
        Convert Roman script text to native script for better TTS pronunciation
        """
        if not text:
            return text
        
        # Check if text is in Roman script
        if await self._is_roman_script(text, language):
            if language == 'ur':
                return self._roman_to_urdu(text)
            elif language == 'ps':
                return self._roman_to_pashto(text)
        
        return text
    
    async def _is_roman_script(self, text: str, language: str) -> bool:
        """Check if text appears to be in Roman script"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Roman Urdu indicators
        roman_urdu_indicators = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'thi', 'the', 'kyun', 'kahan', 'kaun'
        ]
        
        # Roman Pashto indicators
        roman_pashto_indicators = [
            'sta', 'yast', 'kaw', 'kawi', 'kawam', 'kawalai', 'kawale', 
            'sham', 'dera', 'khaire', 'kha', 'manana', 'mehrbani', 'sara'
        ]
        
        # Check for absence of native script characters
        has_native_script = False
        if language == 'ur':
            has_native_script = bool(re.search(r'[\u0600-\u06FF]', text))
            score = sum(1 for indicator in roman_urdu_indicators if indicator in text_lower)
            return score >= 2 and not has_native_script
        elif language == 'ps':
            has_native_script = bool(re.search(r'[\u0600-\u06FF\u0671-\u06D3]', text))
            score = sum(1 for indicator in roman_pashto_indicators if indicator in text_lower)
            return score >= 2 and not has_native_script
        
        return False
    
    def _roman_to_urdu(self, roman_text: str) -> str:
        """Convert Roman Urdu to Urdu script"""
        urdu_text = roman_text
        for roman, urdu in self.roman_to_urdu_map.items():
            # Use word boundaries to avoid partial replacements
            urdu_text = re.sub(r'\b' + re.escape(roman) + r'\b', urdu, urdu_text, flags=re.IGNORECASE)
        
        return urdu_text
    
    def _roman_to_pashto(self, roman_text: str) -> str:
        """Convert Roman Pashto to Pashto script"""
        pashto_text = roman_text
        for roman, pashto in self.roman_to_pashto_map.items():
            # Use word boundaries to avoid partial replacements
            pashto_text = re.sub(r'\b' + re.escape(roman) + r'\b', pashto, pashto_text, flags=re.IGNORECASE)
        
        return pashto_text
    
    async def _speak_online(self, text: str, language: str) -> bool:
        """Use edge-tts for online speech synthesis"""
        try:
            voice = self.online_voices.get(language, self.online_voices['ur'])
            
            # Use SSML for better pronunciation of mixed content
            ssml_text = self._create_ssml(text, language, voice)
            
            communicate = edge_tts.Communicate(ssml_text, voice)
            
            # Save to temporary file
            temp_file = "temp_speech.mp3"
            await communicate.save(temp_file)
            
            # Play the audio file
            if os.path.exists(temp_file):
                if os.name == 'nt':  # Windows
                    os.system(f"start {temp_file}")
                else:  # macOS/Linux
                    os.system(f"afplay {temp_file}" if os.name == 'posix' else f"mpg123 {temp_file}")
                
                # Clean up temp file after a delay
                await asyncio.sleep(2)
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                logger.info(f"Spoke online in {language}: {text[:50]}...")
                return True
                
        except Exception as e:
            logger.warning(f"Online TTS failed for {language}: {e}")
        
        return False
    
    def _create_ssml(self, text: str, language: str, voice: str) -> str:
        """Create SSML for better speech synthesis"""
        # Basic SSML wrapper for improved pronunciation
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{language}">
            <voice name="{voice}">
                <prosody rate="medium" pitch="default">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        return ssml
    
    def _speak_offline(self, text: str, language: str) -> bool:
        """Use pyttsx3 for offline speech synthesis"""
        try:
            if not self.offline_engine:
                return False
            
            # Note: Offline TTS has limited language support
            # It will attempt to speak the text as-is
            self.offline_engine.say(text)
            self.offline_engine.runAndWait()
            
            logger.info(f"Spoke offline in {language}: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Offline TTS error: {e}")
            return False
    
    async def speak_roman_directly(self, roman_text: str, language: str) -> bool:
        """
        Speak Roman script text directly without conversion
        Useful for mixed content or when native script conversion isn't desired
        """
        try:
            voice = self.online_voices.get(language, self.online_voices['ur'])
            
            # For Roman text, we might want to use a different approach
            # or add pronunciation hints in SSML
            communicate = edge_tts.Communicate(roman_text, voice)
            
            temp_file = "temp_speech.mp3"
            await communicate.save(temp_file)
            
            if os.path.exists(temp_file):
                if os.name == 'nt':
                    os.system(f"start {temp_file}")
                else:
                    os.system(f"afplay {temp_file}" if os.name == 'posix' else f"mpg123 {temp_file}")
                
                await asyncio.sleep(2)
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                logger.info(f"Spoke Roman {language} directly: {roman_text[:50]}...")
                return True
                
        except Exception as e:
            logger.warning(f"Roman direct TTS failed: {e}")
        
        return False
    
    async def speak_with_emotion(self, text: str, language: str, emotion: str = "neutral") -> bool:
        """
        Speak text with emotional tone
        Emotions: neutral, happy, sad, excited, calm
        """
        try:
            # Convert Roman to native first
            processed_text = await self._convert_roman_to_native(text, language)
            
            # Add emotional context to text for better TTS
            emotional_text = self._add_emotional_context(processed_text, emotion, language)
            return await self.speak(emotional_text, language)
            
        except Exception as e:
            logger.error(f"Emotional TTS error: {e}")
            return await self.speak(text, language)
    
    def _add_emotional_context(self, text: str, emotion: str, language: str) -> str:
        """Add emotional context to text for better TTS expression"""
        # Enhanced emotional prefixes with SSML-like expressions
        emotional_prefixes = {
            'ur': {
                'happy': 'خوشی سے، ',
                'sad': 'افسوس سے، ',
                'excited': 'پر جوش انداز میں، ',
                'calm': 'پرسکون طریقے سے، ',
                'friendly': 'دوستانہ انداز میں، '
            },
            'ps': {
                'happy': 'د خوښۍ سره، ',
                'sad': 'د غمجنۍ سره، ',
                'excited': 'د ډېرې زړه سره، ',
                'calm': 'د آرامۍ سره، ',
                'friendly': 'د ملګرۍ سره، '
            },
            'en': {
                'happy': 'Happily, ',
                'sad': 'Sadly, ',
                'excited': 'Excitedly, ',
                'calm': 'Calmly, ',
                'friendly': 'In a friendly way, '
            }
        }
        
        if emotion != 'neutral' and emotion in emotional_prefixes.get(language, {}):
            prefix = emotional_prefixes[language][emotion]
            return prefix + text
        
        return text
    
    async def test_tts(self, language: str = 'ur') -> bool:
        """Test TTS functionality with a sample phrase"""
        test_phrases = {
            'ur': 'السلام علیکم، میں شاڈو AI ہوں',
            'ps': 'سلام، زه شاڈو AI یم',
            'en': 'Hello, I am Shadow AI',
            'hi': 'नमस्ते, मैं शैडो AI हूँ'
        }
        
        test_text = test_phrases.get(language, test_phrases['ur'])
        return await self.speak(test_text, language)
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for TTS"""
        return [
            {'code': 'ur', 'name': 'Urdu', 'roman_support': True, 'online_voice': 'AsadNeural'},
            {'code': 'ps', 'name': 'Pashto', 'roman_support': True, 'online_voice': 'GulNawazNeural'},
            {'code': 'en', 'name': 'English', 'roman_support': True, 'online_voice': 'ChristopherNeural'},
            {'code': 'hi', 'name': 'Hindi', 'roman_support': False, 'online_voice': 'MadhurNeural'}
        ]
    
    def set_speech_rate(self, rate: int):
        """Set speech rate for offline TTS"""
        if self.offline_engine:
            self.offline_engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume for offline TTS (0.0 to 1.0)"""
        if self.offline_engine:
            self.offline_engine.setProperty('volume', volume)
    
    def stop_speaking(self):
        """Stop any ongoing speech"""
        if self.offline_engine:
            self.offline_engine.stop()

# Utility function for quick TTS
async def quick_speak(text: str, language: str = 'en'):
    """Quick utility function for simple TTS"""
    try:
        from shadow_core.multilingual import MultilingualManager
        manager = MultilingualManager()
        tts = MultilingualTTS(manager)
        return await tts.speak(text, language)
    except Exception as e:
        logger.error(f"Quick speak failed: {e}")
        return False
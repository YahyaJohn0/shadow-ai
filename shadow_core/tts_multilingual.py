# shadow_core/tts_multilingual.py
"""
Multilingual Text-to-Speech module with Urdu and Pashto support
"""

import logging
import asyncio
import edge_tts
import pyttsx3
import os
from typing import Optional

logger = logging.getLogger(__name__)

class MultilingualTTS:
    """
    Text-to-Speech with Urdu, Pashto, and English support
    Uses edge-tts for online and pyttsx3 for offline
    """
    
    def __init__(self, multilingual_manager):
        self.multilingual_manager = multilingual_manager
        self.online_voices = {
            'ur': 'ur-PK-AsadNeural',      # Urdu male voice
            'ps': 'ps-AF-GulNawazNeural',  # Pashto male voice  
            'en': 'en-US-ChristopherNeural' # English male voice
        }
        self.offline_engine = None
        self._initialize_offline_tts()
    
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
        
        # Try online TTS first (better quality)
        online_success = await self._speak_online(text, language)
        if online_success:
            return True
        
        # Fallback to offline TTS
        offline_success = self._speak_offline(text, language)
        return offline_success
    
    async def _speak_online(self, text: str, language: str) -> bool:
        """Use edge-tts for online speech synthesis"""
        try:
            voice = self.online_voices.get(language, self.online_voices['ur'])
            
            communicate = edge_tts.Communicate(text, voice)
            
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
    
    async def speak_with_emotion(self, text: str, language: str, emotion: str = "neutral") -> bool:
        """
        Speak text with emotional tone
        Emotions: neutral, happy, sad, excited, calm
        """
        try:
            # Add emotional context to text for better TTS
            emotional_text = self._add_emotional_context(text, emotion, language)
            return await self.speak(emotional_text, language)
            
        except Exception as e:
            logger.error(f"Emotional TTS error: {e}")
            return await self.speak(text, language)
    
    def _add_emotional_context(self, text: str, emotion: str, language: str) -> str:
        """Add emotional context to text for better TTS expression"""
        # This is a simple implementation - could be enhanced with SSML
        emotional_prefixes = {
            'ur': {
                'happy': 'خوشی سے، ',
                'sad': 'افسوس سے، ',
                'excited': 'پر جوش انداز میں، ',
                'calm': 'پرسکون طریقے سے، '
            },
            'ps': {
                'happy': 'د خوښۍ سره، ',
                'sad': 'د غمجنۍ سره، ',
                'excited': 'د ډېرې زړه سره، ',
                'calm': 'د آرامۍ سره، '
            },
            'en': {
                'happy': 'Happily, ',
                'sad': 'Sadly, ',
                'excited': 'Excitedly, ',
                'calm': 'Calmly, '
            }
        }
        
        if emotion != 'neutral' and emotion in emotional_prefixes.get(language, {}):
            prefix = emotional_prefixes[language][emotion]
            return prefix + text
        
        return text
    
    def set_speech_rate(self, rate: int):
        """Set speech rate for offline TTS"""
        if self.offline_engine:
            self.offline_engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume for offline TTS (0.0 to 1.0)"""
        if self.offline_engine:
            self.offline_engine.setProperty('volume', volume)
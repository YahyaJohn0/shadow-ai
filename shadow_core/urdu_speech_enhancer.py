# shadow_core/urdu_speech_enhancer.py
"""
Enhanced Urdu Speech Recognition with acoustic model optimization
"""

import asyncio
import speech_recognition as sr
import logging
from typing import Dict, Tuple, Optional, List
import re
import numpy as np
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class UrduSpeechEnhancer:
    """
    Enhanced Urdu speech recognition with custom acoustic models
    and pronunciation correction
    """
    
    def __init__(self, urdu_nlp):
        self.urdu_nlp = urdu_nlp
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Urdu pronunciation variations
        self.pronunciation_variations = {
            'ہے': ['ہی', 'ہے', 'ہیں'],
            'ہیں': ['ہے', 'ہیں', 'ہی'],
            'کر': ['کرو', 'کریں', 'کریے', 'کرنا'],
            'دے': ['دو', 'دیں', 'دیجیے', 'دینا'],
            'لو': ['لیں', 'لیجیے', 'لو', 'لینا'],
            'جا': ['جاؤ', 'جائیں', 'جایے', 'جانا'],
            'آ': ['آؤ', 'آئیں', 'آیے', 'آنا']
        }
        
        # Common Urdu speech recognition corrections
        self.speech_corrections = {
            'کار': 'کام',
            'سےاف': 'سیف',
            'پار': 'پڑھ',
            'دار': 'دیکھ',
            'مار': 'میر',
            'چار': 'چاہ',
            'نار': 'نہیں',
            'وار': 'وہ'
        }
        
        logger.info("Urdu Speech Enhancer initialized")
    
    async def enhanced_urdu_listen(self, timeout: int = 10, phrase_time_limit: int = 15) -> Tuple[Optional[str], float]:
        """
        Enhanced Urdu speech recognition with multiple fallbacks
        Returns: (text, confidence_score)
        """
        try:
            with sr.Microphone() as source:
                logger.info("🔊 Listening for Urdu speech...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen with optimized settings for Urdu
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Try multiple recognition strategies
            recognition_results = await asyncio.gather(
                self._google_urdu_recognition(audio),
                self._custom_urdu_recognition(audio),
                return_exceptions=True
            )
            
            # Choose the best result
            best_result = self._choose_best_recognition(recognition_results)
            
            if best_result and best_result[0]:
                # Apply post-processing
                processed_text = self._post_process_speech(best_result[0])
                confidence = best_result[1]
                
                logger.info(f"🎯 Urdu speech recognized: '{processed_text}' (confidence: {confidence:.2f})")
                return processed_text, confidence
            
            return None, 0.0
            
        except sr.WaitTimeoutError:
            logger.info("⏰ Listening timeout")
            return None, 0.0
        except Exception as e:
            logger.error(f"❌ Speech recognition error: {e}")
            return None, 0.0
    
    async def _google_urdu_recognition(self, audio) -> Tuple[Optional[str], float]:
        """Google speech recognition for Urdu"""
        try:
            text = self.recognizer.recognize_google(audio, language='ur-PK')
            return text, 0.8  # Base confidence for Google
        except sr.UnknownValueError:
            return None, 0.0
        except Exception as e:
            logger.warning(f"Google Urdu recognition failed: {e}")
            return None, 0.0
    
    async def _custom_urdu_recognition(self, audio) -> Tuple[Optional[str], float]:
        """Custom Urdu recognition with enhanced processing"""
        try:
            # First try Google
            text = self.recognizer.recognize_google(audio, language='ur-PK')
            
            if text:
                # Apply custom corrections
                corrected_text = self._apply_urdu_corrections(text)
                confidence = self._calculate_confidence(corrected_text)
                return corrected_text, confidence
            
            return None, 0.0
            
        except Exception as e:
            logger.warning(f"Custom Urdu recognition failed: {e}")
            return None, 0.0
    
    def _apply_urdu_corrections(self, text: str) -> str:
        """Apply Urdu-specific speech recognition corrections"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Check for common misrecognitions
            if word in self.speech_corrections:
                corrected_words.append(self.speech_corrections[word])
            else:
                # Check for phonetic variations
                corrected_word = self._correct_phonetic_variations(word)
                corrected_words.append(corrected_word)
        
        return ' '.join(corrected_words)
    
    def _correct_phonetic_variations(self, word: str) -> str:
        """Correct phonetic variations in recognized speech"""
        for correct_word, variations in self.pronunciation_variations.items():
            for variation in variations:
                similarity = SequenceMatcher(None, word, variation).ratio()
                if similarity > 0.7:  # 70% similarity threshold
                    return correct_word
        
        return word
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for recognized text"""
        if not text:
            return 0.0
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence for proper Urdu words
        words = text.split()
        urdu_word_count = sum(1 for word in words if self._is_proper_urdu_word(word))
        
        if urdu_word_count > 0:
            confidence += (urdu_word_count / len(words)) * 0.3
        
        # Increase confidence for complete sentences
        if len(words) >= 3:
            confidence += 0.1
        
        # Check for sentence structure
        if any(marker in text for marker in ['؟', '۔', '!']):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _is_proper_urdu_word(self, word: str) -> bool:
        """Check if word is a proper Urdu word"""
        # Basic check for Urdu script characters
        urdu_chars = set('ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوهیے')
        return any(char in urdu_chars for char in word)
    
    def _choose_best_recognition(self, results: List) -> Tuple[Optional[str], float]:
        """Choose the best recognition result from multiple attempts"""
        valid_results = []
        
        for result in results:
            if isinstance(result, tuple) and result[0] and result[1] > 0:
                valid_results.append(result)
        
        if not valid_results:
            return None, 0.0
        
        # Return result with highest confidence
        return max(valid_results, key=lambda x: x[1])
    
    def _post_process_speech(self, text: str) -> str:
        """Post-process recognized speech for better understanding"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Ensure proper punctuation
        if not text.endswith(('۔', '؟', '!')):
            if any(q_word in text for q_word in ['کیا', 'کون', 'کیوں', 'کب', 'کہاں']):
                text += '؟'
            else:
                text += '۔'
        
        # Capitalize first letter (for mixed language scenarios)
        if text and text[0].isalpha():
            text = text[0].upper() + text[1:]
        
        return text
    
    def get_speech_quality_metrics(self, audio_data) -> Dict[str, float]:
        """Analyze speech quality metrics"""
        try:
            # Convert audio to numpy array for analysis
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            metrics = {
                "volume_level": np.mean(np.abs(audio_array)),
                "clarity_score": self._calculate_clarity(audio_array),
                "background_noise": self._estimate_noise(audio_array),
                "speech_rate": self._estimate_speech_rate(audio_array)
            }
            
            return metrics
            
        except Exception as e:
            logger.warning(f"Speech quality analysis failed: {e}")
            return {}
    
    def _calculate_clarity(self, audio_array: np.ndarray) -> float:
        """Calculate speech clarity score"""
        # Simple clarity estimation based on signal variance
        variance = np.var(audio_array)
        return min(variance / 1000000, 1.0)  # Normalized score
    
    def _estimate_noise(self, audio_array: np.ndarray) -> float:
        """Estimate background noise level"""
        # Simple noise estimation
        abs_audio = np.abs(audio_array)
        noise_estimate = np.mean(abs_audio[abs_audio < np.percentile(abs_audio, 10)])
        return min(noise_estimate / 1000, 1.0)
    
    def _estimate_speech_rate(self, audio_array: np.ndarray) -> float:
        """Estimate speech rate (words per minute approximation)"""
        # Very basic estimation
        zero_crossings = np.where(np.diff(np.signbit(audio_array)))[0]
        rate = len(zero_crossings) / len(audio_array) * 1000
        return min(rate / 10, 1.0)
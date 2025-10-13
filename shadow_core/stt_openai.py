# shadow_core/stt_openai.py
"""
OpenAI/ChatGPT Speech-to-Text module
"""
import logging
import threading
import time
import speech_recognition as sr
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import openai
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class OpenAISTT:
    """
    OpenAI Whisper API for Speech-to-Text
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self._stop_listening = None
        self._is_listening = False
        
        # Initialize OpenAI client
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found in config.py")
        
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("OpenAI STT initialized with microphone")
        except Exception as e:
            logger.warning(f"Microphone initialization failed: {e}")
            self.microphone = None

    async def listen_once_async(self, timeout=5, phrase_time_limit=10) -> Optional[str]:
        """Async single-shot listen using OpenAI Whisper"""
        if not self.microphone:
            return None

        def recognize():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout, 
                        phrase_time_limit=phrase_time_limit
                    )
                    
                    # Convert audio to WAV data
                    audio_data = audio.get_wav_data()
                    
                    # Use OpenAI Whisper API
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=("audio.wav", audio_data, "audio/wav"),
                        language="en"  # Can be adjusted for multilingual support
                    )
                    
                    return response.text.strip() if response.text else None
                    
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                logger.error(f"OpenAI recognition error: {e}")
                return None

        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(self.thread_pool, recognize)
            if text:
                logger.info(f"OpenAI Recognized: {text}")
            return text
        except Exception as e:
            logger.error(f"OpenAI async listen error: {e}")
            return None

    def listen_continuous(self, callback, event_loop=None, timeout=5, phrase_time_limit=10):
        """Start continuous listening with OpenAI"""
        if not self.microphone:
            logger.warning("No microphone available")
            return lambda: None

        stop_flag = threading.Event()
        self._is_listening = True

        def listen_worker():
            while not stop_flag.is_set() and self._is_listening:
                try:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = self.recognizer.listen(
                                source, 
                                timeout=2,  # Short timeout for responsiveness
                                phrase_time_limit=phrase_time_limit
                            )
                            
                            # Convert audio to WAV data
                            audio_data = audio.get_wav_data()
                            
                            # Use OpenAI Whisper API
                            response = self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=("audio.wav", audio_data, "audio/wav"),
                                language="en"
                            )
                            
                            text = response.text.strip() if response.text else None
                            
                            if text:
                                logger.info(f"OpenAI Continuous: {text}")
                                
                                # Check for stop commands
                                if text.lower().strip() in ["stop listening", "exit", "stop", "quit"]:
                                    logger.info("Stop command detected")
                                    if stop_flag:
                                        stop_flag.set()
                                    break
                                
                                # Execute callback
                                if callback:
                                    if event_loop:
                                        if asyncio.iscoroutinefunction(callback):
                                            asyncio.run_coroutine_threadsafe(callback(text), event_loop)
                                        else:
                                            async def async_callback_wrapper():
                                                try:
                                                    callback(text)
                                                except Exception as e:
                                                    logger.error(f"Callback error: {e}")
                                            asyncio.run_coroutine_threadsafe(async_callback_wrapper(), event_loop)
                                    else:
                                        try:
                                            callback(text)
                                        except Exception as e:
                                            logger.error(f"Callback error: {e}")
                                            
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"OpenAI listen error: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"OpenAI worker error: {e}")
                    if not stop_flag.is_set():
                        time.sleep(0.1)

            logger.info("OpenAI continuous listening stopped")

        worker_thread = threading.Thread(target=listen_worker, daemon=True)
        worker_thread.start()

        def stop_listening():
            logger.info("Stopping OpenAI continuous listening...")
            stop_flag.set()
            self._is_listening = False
            self._stop_listening = None
            try:
                worker_thread.join(timeout=2.0)
            except Exception:
                pass

        self._stop_listening = stop_listening
        logger.info("OpenAI continuous STT started")
        return stop_listening

    def listen_once(self, timeout=5, phrase_time_limit=10):
        """Blocking single-shot listen"""
        try:
            with self.microphone as source:
                logger.info(f"Listening with OpenAI... (timeout: {timeout}s)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                audio_data = audio.get_wav_data()
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=("audio.wav", audio_data, "audio/wav"),
                    language="en"
                )
                
                text = response.text.strip() if response.text else None
                if text:
                    logger.info(f"OpenAI Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.info("OpenAI listening timed out")
            return None
        except Exception as e:
            logger.error(f"OpenAI listen error: {e}")
            return None

    def stop(self):
        """Stop any ongoing listening"""
        if self._stop_listening:
            self._stop_listening()
            self._stop_listening = None

    def is_listening(self):
        """Check if currently listening"""
        return self._is_listening
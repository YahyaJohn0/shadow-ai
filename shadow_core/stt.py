import speech_recognition as sr
import whisper
import sounddevice as sd
import numpy as np
import threading
import traceback
import asyncio
import time
import tempfile
import soundfile as sf
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class ShadowSTT:
    """
    Unified Speech-to-Text (STT) system for Shadow AI.
    Supports:
      - Google Web Speech API (online)
      - Whisper (offline)
    """

    def __init__(self,
                 mode: str = "google",
                 whisper_model: str = "base",
                 energy_threshold: int = 300,
                 pause_threshold: float = 0.8,
                 language: str = "en-US"):
        """
        mode: 'google' (default, requires internet) or 'whisper' (offline)
        whisper_model: "tiny", "base", "small", "medium", "large"
        language: STT language code (e.g. "en-US", "ur-PK", "ps-AF")
        """
        self.mode = mode.lower()
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = None
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        self._stop_listening = None
        self._is_listening = False

        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            logger.info("Microphone initialized successfully")
        except Exception as e:
            logger.warning(f"Microphone initialization failed: {e}")
            self.microphone = None

        # Initialize Whisper (if selected)
        self.whisper = None
        if self.mode == "whisper":
            logger.info(f"Loading Whisper model: {whisper_model}")
            try:
                self.whisper = whisper.load_model(whisper_model)
                logger.info("Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.whisper = None

    # ------------------------------
    # Utility
    # ------------------------------
    def check_microphone(self) -> bool:
        """Ensure microphone is initialized before use."""
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone()
                logger.info("Microphone reinitialized successfully")
            except Exception as e:
                logger.error(f"Microphone check failed: {e}")
                return False
        return True

    # ------------------------------
    # Language control
    # ------------------------------
    def set_language(self, lang_code: str = "en-US"):
        """Change STT language dynamically."""
        self.language = lang_code
        logger.info(f"STT language switched to {lang_code}")

    # ------------------------------
    # GOOGLE STT
    # ------------------------------
    def _google_stt_from_audio(self, audio) -> str | None:
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text.strip() if text else None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.error(f"Google API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Google STT unexpected error: {e}")
            return None

    # ------------------------------
    # WHISPER STT
    # ------------------------------
    def _whisper_transcribe_recording(self, duration: int = 5, fs: int = 16000) -> str | None:
        """Record audio and transcribe using Whisper."""
        try:
            logger.info(f"Recording for {duration}s...")
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
            sd.wait()
            audio = np.squeeze(recording)

            if self.whisper is None:
                logger.warning("Whisper model not loaded.")
                return None

            # Save temp file for compatibility
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                sf.write(tmp.name, audio, fs)
                result = self.whisper.transcribe(tmp.name, fp16=False, language=self.language)

            text = result.get("text", "").strip()
            return text if text else None

        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return None

    # ------------------------------
    # Async Single Listen
    # ------------------------------
    async def listen_once_async(self, timeout: int = 5, phrase_time_limit: int = 10) -> str | None:
        """Async single-shot listen -> return recognized text."""
        if not self.check_microphone():
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
                    return self._google_stt_from_audio(audio)
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                logger.error(f"Recognition error: {e}")
                return None

        try:
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(self.thread_pool, recognize)
            if text:
                logger.info(f"Recognized: {text}")
            return text
        except Exception as e:
            logger.error(f"Async listen error: {e}")
            return None

    # ------------------------------
    # Continuous listening
    # ------------------------------
    def listen_continuous(self, callback, event_loop=None, timeout: int = 5, phrase_time_limit: int = 10):
        """Start continuous listening in background. Returns stop() function."""
        if not self.check_microphone():
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
                                timeout=2,
                                phrase_time_limit=phrase_time_limit
                            )
                            text = self._google_stt_from_audio(audio)
                            if text:
                                logger.info(f"Continuous recognition: {text}")

                                # Stop command check
                                if text.lower().strip() in ["stop listening", "exit", "stop", "quit"]:
                                    logger.info("Stop command detected")
                                    stop_flag.set()
                                    break

                                # Execute callback
                                if callback:
                                    if event_loop and event_loop.is_running():
                                        if asyncio.iscoroutinefunction(callback):
                                            asyncio.run_coroutine_threadsafe(callback(text), event_loop)
                                        else:
                                            async def async_wrapper():
                                                try:
                                                    callback(text)
                                                except Exception as e:
                                                    logger.error(f"Callback error: {e}")
                                            asyncio.run_coroutine_threadsafe(async_wrapper(), event_loop)
                                    else:
                                        try:
                                            callback(text)
                                        except Exception as e:
                                            logger.error(f"Callback error: {e}")
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            logger.error(f"Listen error: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    if not stop_flag.is_set():
                        time.sleep(0.1)

            logger.info("Continuous listening stopped")

        worker_thread = threading.Thread(target=listen_worker, daemon=True)
        worker_thread.start()

        def stop_listening():
            logger.info("Stopping continuous listening...")
            stop_flag.set()
            self._is_listening = False
            try:
                worker_thread.join(timeout=2.0)
            except Exception:
                pass
            self._stop_listening = None

        self._stop_listening = stop_listening
        logger.info(f"Continuous STT started (language: {self.language})")
        return stop_listening

    # ------------------------------
    # Simple blocking listen
    # ------------------------------
    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10, whisper_duration: int = 5) -> str | None:
        """Single-shot listen -> return recognized text."""
        if self.mode == "google":
            if not self.check_microphone():
                return None
            try:
                with self.microphone as source:
                    logger.info(f"Listening... (timeout: {timeout}s)")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    text = self._google_stt_from_audio(audio)
                    if text:
                        logger.info(f"Recognized: {text}")
                    return text
            except sr.WaitTimeoutError:
                logger.info("Listening timed out")
                return None
            except Exception as e:
                logger.error(f"Listen error: {e}")
                return None
        else:
            return self._whisper_transcribe_recording(duration=whisper_duration)

    # ------------------------------
    # Stop / Status
    # ------------------------------
    def stop(self):
        """Stop any ongoing listening."""
        if self._stop_listening:
            try:
                self._stop_listening()
            except Exception as e:
                logger.error(f"Stop failed: {e}")
            finally:
                self._stop_listening = None
                self._is_listening = False

    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._is_listening

    # ------------------------------
    # Test Microphone
    # ------------------------------
    async def test_microphone(self) -> bool:
        """Test if microphone is working."""
        if not self.check_microphone():
            return False
        try:
            text = await self.listen_once_async(timeout=2)
            return text is not None
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False


# ------------------------------
# Quick utility
# ------------------------------
async def quick_listen(timeout: int = 3) -> str | None:
    """Quick utility for simple speech recognition."""
    try:
        stt = ShadowSTT()
        return await stt.listen_once_async(timeout=timeout)
    except Exception as e:
        logger.error(f"Quick listen failed: {e}")
        return None

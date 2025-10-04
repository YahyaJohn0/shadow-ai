# shadow_core/stt.py
import speech_recognition as sr
import whisper
import sounddevice as sd
import numpy as np
import threading
import traceback
import asyncio


class ShadowSTT:
    """
    Unified Speech-to-Text (STT) system for Shadow AI.
    Supports:
      - Google Web Speech API (online)
      - Whisper (offline)
    """

    def __init__(self, mode="google", whisper_model="base",
                 energy_threshold=300, pause_threshold=0.8,
                 language="en-US"):
        """
        mode: 'google' (default, requires internet) or 'whisper' (offline)
        whisper_model: which Whisper model to load ("tiny", "base", "small", "medium", "large")
        language: default STT language code (ISO like "en-US", "ur-PK", "ps-AF")
        """
        self.mode = mode.lower()
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.microphone = None

        try:
            self.microphone = sr.Microphone()
        except Exception:
            self.microphone = None

        self.whisper = None
        if self.mode == "whisper":
            print(f"🔊 Loading Whisper ({whisper_model}) model (this may take a while)...")
            try:
                self.whisper = whisper.load_model(whisper_model)
            except Exception as e:
                print("⚠️ Failed to load Whisper model:", e)
                traceback.print_exc()
                self.whisper = None

    # ------------------------------
    # Language control
    # ------------------------------
    def set_language(self, lang_code="en-US"):
        """
        Change STT language dynamically (affects both Google & Whisper).
        Examples:
          - English: "en-US"
          - Urdu: "ur-PK"
          - Pashto: "ps-AF"
        """
        self.language = lang_code
        print(f"[STT] Language switched to {lang_code}")

    # ------------------------------
    # GOOGLE STT
    # ------------------------------
    def _google_stt_from_audio(self, audio):
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"⚠️ Google API error: {e}")
            return None
        except Exception as e:
            print("⚠️ Google STT unexpected error:", e)
            return None

    # ------------------------------
    # WHISPER STT
    # ------------------------------
    def _whisper_transcribe_recording(self, duration=5, fs=16000):
        """
        Record audio with sounddevice and pass to Whisper.
        """
        try:
            print(f"🎙️ (Whisper) Recording for {duration}s...")
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
            sd.wait()
            audio = np.squeeze(recording)

            if self.whisper is None:
                print("⚠️ Whisper model not loaded.")
                return None

            result = self.whisper.transcribe(audio, fp16=False, language=self.language)
            text = result.get("text", "").strip()
            return text
        except Exception as e:
            print("⚠️ Whisper transcription error:", e)
            traceback.print_exc()
            return None

    # ------------------------------
    # Listen once
    # ------------------------------
    def listen_once(self, timeout=5, phrase_time_limit=10, whisper_duration=5):
        """
        Single-shot listen -> return recognized text.
        """
        if self.mode == "google":
            if not self.microphone:
                try:
                    self.microphone = sr.Microphone()
                except Exception as e:
                    print("⚠️ Microphone init failed:", e)
                    return None

            with self.microphone as source:
                print(f"🎤 Listening... (Google STT, lang={self.language})")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    print("🔎 Processing (Google)...")
                    text = self._google_stt_from_audio(audio)
                    if text:
                        print("✅ Recognized:", text)
                    return text
                except sr.WaitTimeoutError:
                    print("⌛ Listening timed out (no speech).")
                    return None
                except Exception as e:
                    print("⚠️ STT listen_once error:", e)
                    traceback.print_exc()
                    return None
        else:
            return self._whisper_transcribe_recording(duration=whisper_duration)

    # ------------------------------
    # Continuous listening
    # ------------------------------
    def listen_continuous(self, callback, event_loop=None, timeout=5, phrase_time_limit=10, whisper_duration=5):
        """
        Start continuous listening in background.
        - callback(text) is called when speech is recognized.
        - Returns a stop() function to stop listening.
        """

        # GOOGLE MODE
        if self.mode == "google":
            if not self.microphone:
                try:
                    self.microphone = sr.Microphone()
                except Exception as e:
                    print("⚠️ Microphone init failed:", e)
                    return lambda: None

            stop_holder = {"fn": None}

            def handler(recognizer, audio):
                try:
                    text = self._google_stt_from_audio(audio)
                    if not text:
                        return
                    print("✅ Recognized:", text)

                    if text.lower().strip() in ["stop listening", "exit", "stop"]:
                        print("🛑 Stop phrase detected (Google).")
                        if stop_holder["fn"]:
                            stop_holder["fn"]()
                        return

                    if event_loop:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                asyncio.run_coroutine_threadsafe(callback(text), event_loop)
                            else:
                                asyncio.run_coroutine_threadsafe(self._call_sync_callback(callback, text), event_loop)
                        except Exception as e:
                            print("⚠️ Error scheduling callback:", e)
                    else:
                        callback(text)

                except Exception as e:
                    print("⚠️ Google handler error:", e)
                    traceback.print_exc()

            stop_listening = self.recognizer.listen_in_background(
                self.microphone, handler, phrase_time_limit=phrase_time_limit
            )
            stop_holder["fn"] = stop_listening
            print(f"🎙️ Continuous STT (Google, lang={self.language}) started.")
            return stop_listening

        # WHISPER MODE
        stop_flag = threading.Event()

        def whisper_loop():
            while not stop_flag.is_set():
                text = self._whisper_transcribe_recording(duration=whisper_duration)
                if not text:
                    continue
                print("✅ Whisper Recognized:", text)
                if text.lower().strip() in ["stop listening", "exit", "stop"]:
                    print("🛑 Stop phrase detected (Whisper).")
                    stop_flag.set()
                    break
                if event_loop:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            asyncio.run_coroutine_threadsafe(callback(text), event_loop)
                        else:
                            asyncio.run_coroutine_threadsafe(self._call_sync_callback(callback, text), event_loop)
                    except Exception as e:
                        print("⚠️ Error scheduling callback:", e)
                else:
                    callback(text)
            print("🎙️ Whisper background thread exiting.")

        t = threading.Thread(target=whisper_loop, daemon=True)
        t.start()

        def stopper():
            stop_flag.set()
            try:
                t.join(timeout=1.0)
            except Exception:
                pass

        print(f"🎙️ Continuous STT (Whisper, lang={self.language}) started.")
        return stopper

    async def _call_sync_callback(self, callback, text):
        """
        Utility: call synchronous callback inside async context.
        """
        try:
            callback(text)
        except Exception as e:
            print("⚠️ callback error:", e)

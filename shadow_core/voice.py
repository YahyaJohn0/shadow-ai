import pyttsx3
import speech_recognition as sr

class ShadowVoice:
    """
    Handles real-time Text-to-Speech (TTS) and Speech-to-Text (STT)
    for the Shadow assistant, with multi-language support.
    """

    def __init__(self, voice_name="en-US"):
        # ------------------------------
        # Initialize TTS engine
        # ------------------------------
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)  # speaking speed
        self.engine.setProperty("volume", 1.0)

        self.current_language = voice_name  # <- keep track of active language

        # Select voice if available
        voices = self.engine.getProperty("voices")
        for v in voices:
            if voice_name.lower() in v.id.lower():
                self.engine.setProperty("voice", v.id)
                break

        # ------------------------------
        # Initialize STT
        # ------------------------------
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    # ------------------------------
    # Change language dynamically
    # ------------------------------
    def set_language(self, lang_code="en-US"):
        """
        Update TTS + STT language dynamically.
        """
        self.current_language = lang_code
        print(f"[Voice] Language switched to {lang_code}")

        # Try to switch TTS voice
        voices = self.engine.getProperty("voices")
        for v in voices:
            if lang_code.lower() in v.id.lower():
                self.engine.setProperty("voice", v.id)
                break

    # ------------------------------
    # Speak text in real-time
    # ------------------------------
    def speak(self, text):
        """
        Speak text immediately using pyttsx3.
        """
        if not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()  # blocks until finished

    # ------------------------------
    # Listen from microphone
    # ------------------------------
    def listen(self, timeout=5, phrase_time_limit=8):
        """
        Listen from microphone and return recognized text.
        """
        try:
            with self.mic as source:
                print(f"🎙️ Listening ({self.current_language})...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            text = self.recognizer.recognize_google(audio, language=self.current_language)
            return text
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"[STT ERROR] {e}")
            return None

    # ------------------------------
    # Synchronous helper
    # ------------------------------
    def speak_sync(self, text):
        """
        Helper function to call speak() in synchronous code.
        """
        self.speak(text)

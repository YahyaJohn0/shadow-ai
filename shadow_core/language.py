# shadow_core/language.py
from shadow_core.voice import ShadowVoice

class LanguageManager:
    """
    Handles multilingual support for Shadow AI.
    Supports TTS and STT in multiple languages.
    """
    SUPPORTED_LANGUAGES = {
        "english": {"tts": "en-US", "stt": "en-US"},
        "urdu": {"tts": "ur-PK", "stt": "ur-PK"},
        "pashto": {"tts": "ps-AF", "stt": "ps-AF"},
    }

    def __init__(self, default="english"):
        self.current_language = default.lower()
        if self.current_language not in self.SUPPORTED_LANGUAGES:
            self.current_language = "english"
        self.voice = ShadowVoice(voice_name=self.SUPPORTED_LANGUAGES[self.current_language]["tts"])

    def set_language(self, lang_name):
        lang_name = lang_name.lower()
        if lang_name in self.SUPPORTED_LANGUAGES:
            self.current_language = lang_name
            # re-initialize TTS engine with new language
            self.voice = ShadowVoice(voice_name=self.SUPPORTED_LANGUAGES[self.current_language]["tts"])
            return True
        return False

    def speak(self, text):
        if self.voice and text:
            self.voice.speak(text)

    def listen(self, timeout=5, phrase_time_limit=8):
        if self.voice:
            return self.voice.listen(timeout=timeout, phrase_time_limit=phrase_time_limit,
                                     language=self.SUPPORTED_LANGUAGES[self.current_language]["stt"])
        return None

    # -----------------------------
    # NEW: Translate / Generate text in current language
    # -----------------------------
    def generate_text_in_current_language(self, text):
        """
        Placeholder: returns text as-is for now.
        Can integrate with translation API later if needed.
        """
        return text

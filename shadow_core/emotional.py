# emotional.py
from textblob import TextBlob
from config import VOICE_STYLE_MAP

class EmotionalEngine:
    """
    Basic sentiment detection with TextBlob.
    Returns a tone and a suggested voice_override (based on VOICE_STYLE_MAP).
    """
    def __init__(self):
        pass

    def analyze_text(self, text):
        tb = TextBlob(text)
        polarity = tb.sentiment.polarity  # -1..1
        subjectivity = tb.sentiment.subjectivity  # 0..1
        tone = "neutral"
        if polarity <= -0.4:
            tone = "sad"
        elif polarity <= -0.05:
            tone = "concerned"
        elif polarity >= 0.4:
            tone = "very_happy"
        elif polarity >= 0.05:
            tone = "positive"
        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "tone": tone
        }

    def select_response_style(self, analysis):
        tone = analysis.get("tone", "neutral")
        if tone == "sad":
            return {"voice_style": "soft", "tone": "comforting", "voice_override": VOICE_STYLE_MAP.get("comforting")}
        if tone == "concerned":
            return {"voice_style": "calm", "tone": "encouraging", "voice_override": VOICE_STYLE_MAP.get("calm")}
        if tone in ("very_happy", "positive"):
            return {"voice_style": "energetic", "tone": "cheerful", "voice_override": VOICE_STYLE_MAP.get("energetic")}
        # default
        return {"voice_style": "neutral", "tone": "neutral", "voice_override": VOICE_STYLE_MAP.get("neutral")}

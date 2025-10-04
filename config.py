# config.py
import os
from dotenv import load_dotenv

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

# ------------------------------
# API Keys
# ------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Knowledge Module API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ------------------------------
# Knowledge Module Settings
# ------------------------------
USE_FREE_APIS = os.getenv("USE_FREE_APIS", "true").lower() == "true"
WEATHER_UNIT = os.getenv("WEATHER_UNIT", "metric")  # metric or imperial
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

# ------------------------------
# Voices & user
# ------------------------------
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US-GuyNeural")
USER_NAME = os.getenv("USER_NAME", "Yahya")

# Map emotion styles to preferred voices (customizable via env)
VOICE_STYLE_MAP = {
    "comforting": os.getenv("VOICE_COMFORTING", "en-US-AriaNeural"),
    "calm": os.getenv("VOICE_CALM", DEFAULT_VOICE),
    "energetic": os.getenv("VOICE_ENERGETIC", "en-US-JennyNeural"),
    "neutral": DEFAULT_VOICE
}

# ------------------------------
# Local paths
# ------------------------------
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMORY_DB = os.path.join(DATA_DIR, "memory.db")
USER_PROFILE = os.path.join(DATA_DIR, "user_profile.json")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------
# Optional: Other settings
# ------------------------------
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "3"))

# ------------------------------
# Knowledge Module Constants
# ------------------------------
SUPPORTED_STOCK_SYMBOLS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX", 
    "BTC", "ETH", "DOGE", "SPY", "QQQ", "BTC-USD", "ETH-USD"
]

SUPPORTED_CITIES = [
    "London", "New York", "Paris", "Tokyo", "Sydney", "Berlin", "Mumbai",
    "Dubai", "Singapore", "Toronto", "Moscow", "Cairo", "Rome", "Madrid"
]

# ------------------------------
# API Endpoints
# ------------------------------
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
YAHOO_FINANCE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
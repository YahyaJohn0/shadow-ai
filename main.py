# main.py
import asyncio
import sys
import threading
import time
import os
from typing import Dict, Optional, Tuple

# Suppress verbose Google logging
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------
# Core Modules
# ------------------------------
from shadow_core.brain import ShadowBrain
from shadow_core.memory import ShadowMemory
from shadow_core.voice import ShadowVoice
from shadow_core.emotional import EmotionalEngine
from shadow_core.tasks import TaskManager
from shadow_core.gui import ShadowGUI
from shadow_core.personality import Personality
from shadow_core.integrations import Integrations
from shadow_core.scheduler import Scheduler, MockScheduler
from shadow_core.decision_engine import DecisionEngine
from shadow_core.safety import Safety
from shadow_core.stt import ShadowSTT
from shadow_core.messaging import Messaging, MockMessaging
from shadow_core.language import LanguageManager
from shadow_core.knowledge import FreeKnowledge
from shadow_core.automation import AutomationManager
from shadow_core.clean_output import CleanOutput

# Multilingual imports
from shadow_core.multilingual import MultilingualManager, UrduPashtoTranslator, MultilingualBrain
from shadow_core.stt_multilingual import MultilingualSTT
from shadow_core.tts_multilingual import MultilingualTTS
from shadow_core.dynamic_nlu import ContextAwareInterpreter

from config import DEFAULT_VOICE, OPENWEATHER_API_KEY, ALPHA_VANTAGE_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------
# Shadow AI Class
# ------------------------------
class Shadow:
    """Main Shadow AI class with multilingual capabilities"""
    
    def __init__(self):
        """Initialize Shadow AI with all components"""
        logger.info("Initializing Shadow AI...")
        
        # Initialize Brain FIRST
        try:
            self.brain = ShadowBrain()
            logger.info("🎯 SHADOW AI - GEMINI 2.5 FLASH ONLINE")
            
            # Show usage stats
            stats = self.brain.get_usage_stats()
            logger.info(f"🤖 Model: {stats.get('model', 'Gemini 2.5 Flash')}")
            logger.info(f"📊 Free requests remaining: {stats.get('remaining_daily', '?')}")
            
        except Exception as e:
            logger.error(f"❌ GEMINI BRAIN FAILED: {e}")
            # Don't fallback - just crash with clear error
            raise SystemExit(f"Cannot start Shadow AI: {e}")
        
        # Initialize core components that don't have dependencies
        self.memory = ShadowMemory()
        self.personality = Personality()
        self.emotional_engine = EmotionalEngine()
        self.task_manager = TaskManager(self.memory)
        self.integrations = Integrations()
        self.safety = Safety()
        self.language_manager = LanguageManager()
        self.automation = AutomationManager()
        self.clean_output = CleanOutput(show_technical_logs=False)
        
        # Initialize Multilingual Manager before components that depend on it
        self.multilingual_manager = MultilingualManager()
        
        # Now initialize components that depend on multilingual_manager
        self.multilingual_stt = MultilingualSTT(self.multilingual_manager)
        self.multilingual_tts = MultilingualTTS(self.multilingual_manager)
        self.multilingual_brain = MultilingualBrain(self.brain, self.multilingual_manager, UrduPashtoTranslator)
        
        # Now initialize Decision Engine (depends on brain and memory)
        self.decision_engine = DecisionEngine(self.brain, self.memory)
        
        # Voice and STT - Use ChatGPT/OpenAI for STT
        self.voice = ShadowVoice()
        
        # Try to initialize OpenAI STT, fallback to Google if not available
        try:
            from shadow_core.stt_openai import OpenAISTT
            self.stt = OpenAISTT()
            self.stt_mode = "openai"
            logger.info("🎤 Using OpenAI/ChatGPT for Speech Recognition")
        except ImportError:
            logger.warning("OpenAI STT not available, falling back to Google STT")
            self.stt = ShadowSTT(mode="google")
            self.stt_mode = "google"
        except Exception as e:
            logger.warning(f"OpenAI STT failed: {e}, falling back to Google STT")
            self.stt = ShadowSTT(mode="google")
            self.stt_mode = "google"

        # Scheduler
        self.scheduler = MockScheduler()  # Use mock for now
        
        # Messaging
        self.messaging = MockMessaging()  # Use mock for now
        self.message_queue = asyncio.Queue()
        
        # TTS engine for direct speech
        self.tts_engine = None
        self.setup_output_system()
        
        logger.info("Shadow AI initialization complete")
    
    async def super_understand_urdu(self, text: str) -> str:
        """
        Super intelligent Urdu understanding
        """
        understanding = await self.multilingual_manager.super_understand_urdu(text)
        
        if understanding.get('confidence', 0) > 0.7:
            # Use the understanding to generate better response
            response_suggestions = understanding.get('response_suggestions', [])
            if response_suggestions:
                return response_suggestions[0]
        
        # Fallback to normal processing
        return await self.process_multilingual_query(text, 'ur')
        
    async def start_services(self):
        """Start all background services that need event loop"""
        try:
            # Start scheduler background task
            await self.scheduler.start()
            logger.info("All background services started")
        except Exception as e:
            logger.error(f"Error starting background services: {e}")
    
    async def shutdown(self):
        """Clean shutdown of all components"""
        logger.info("Shutting down Shadow AI...")
        try:
            # Stop scheduler
            if hasattr(self.scheduler, 'stop'):
                await self.scheduler.stop()
            
            # Cleanup voice
            if hasattr(self.voice, 'cleanup'):
                await self.voice.cleanup()
            
            # Cleanup automation
            if self.automation and hasattr(self.automation, 'cleanup'):
                await self.automation.cleanup()
                
            logger.info("Shadow AI shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def listen_multilingual(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Listen for speech in any supported language
        Returns: (text, detected_language)
        """
        return await self.multilingual_stt.listen()
    
    async def speak_multilingual(self, text: str, language: str = None) -> bool:
        """
        Speak text in specified language
        """
        return await self.multilingual_tts.speak(text, language)
    
    async def process_multilingual_query(self, text: str, input_language: str) -> str:
        """
        Process query in any language and return response in same language
        """
        # Get response from multilingual brain
        response = await self.multilingual_brain.ask_multilingual(
            text, 
            input_language, 
            input_language  # Respond in same language
        )
        
        # Update conversation context
        self.multilingual_brain.update_conversation_context(text, response, input_language)
        
        return response
    
    async def handle_query(self, text: str, gui=None) -> str:
        """
        Handle user query using the Decision Engine with multilingual support
        """
        if not text or text.strip() == "":
            return "I didn't catch anything. Please try again."
        
        try:
            # Use Decision Engine to process the query directly
            # Let the multilingual brain handle language detection internally
            response = await self.decision_engine.handle_query(text, gui)
            return self.clean_output.clean_response_text(response)
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            error_msg = "I encountered an error processing your request."
            return await self.multilingual_brain.ask_multilingual(
                error_msg, 'en', self.multilingual_manager.current_language
            )
    
    async def safe_handle_query(self, text: str, gui=None, retries: int = 2) -> str:
        """Wrapper with retry logic for handling queries"""
        for attempt in range(retries):
            try:
                return await self.handle_query(text, gui)
            except Exception as e:
                if attempt == retries - 1:  # Last attempt
                    raise
                logger.warning(f"Query failed, retrying... Attempt {attempt + 1}")
                await asyncio.sleep(1)
    
    async def run_multilingual_voice_loop(self):
        """
        Main voice interaction loop with multilingual support
        """
        logger.info("Starting multilingual voice loop...")
        
        await self.speak_multilingual("hey how can i help you today", 'en')
        
        while True:
            try:
                # Listen for speech
                text, detected_lang = await self.listen_multilingual()
                
                if text:
                    logger.info(f"Detected language: {detected_lang}, Text: {text}")
                    
                    # Process the query
                    response = await self.process_multilingual_query(text, detected_lang)
                    
                    # Speak the response
                    await self.speak_multilingual(response, detected_lang)
                    
                # Short delay before next listen
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Multilingual voice loop stopped by user")
                break
            except Exception as e:
                logger.error(f"Multilingual loop error: {e}")
                await asyncio.sleep(2)
    
    def set_preferred_language(self, language: str) -> bool:
        """Set preferred language for interactions"""
        success = self.multilingual_manager.set_language(language)
        if success:
            lang_name = self.multilingual_manager.get_language_info(language)['name']
            logger.info(f"Preferred language set to: {lang_name}")
        return success
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.multilingual_manager.get_supported_languages()
    
    def get_conversation_history(self, limit=10):
        """Get recent conversation history"""
        return self.memory.get_conversation_history(limit)
    
    def setup_output_system(self):
        """Setup proper output and TTS system"""
        try:
            # Initialize TTS for direct speech
            self.tts_engine = self._setup_tts()
            logger.info("TTS system initialized for direct speech")
        except Exception as e:
            logger.warning(f"TTS setup failed: {e}")
            self.tts_engine = None
    
    def _setup_tts(self):
        """Setup TTS engine for direct speech"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Configure voice properties
            voices = engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            engine.setProperty('rate', 180)  # Words per minute
            engine.setProperty('volume', 0.8)  # Volume level
            
            return engine
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {e}")
            return None

# ------------------------------
# Global Shadow Instance
# ------------------------------
SHADOW = Shadow()

# Initialize personality and safety
PERSONALITY = Personality()
SAFETY = Safety()

# ------------------------------
# Background asyncio loop
# ------------------------------
def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

BG_LOOP = asyncio.new_event_loop()
_bg_thread = threading.Thread(target=start_background_loop, args=(BG_LOOP,), daemon=True)
_bg_thread.start()
time.sleep(0.05)  # ensure loop starts

def schedule_handle_query(text, gui=None):
    """Schedule query handling in background loop"""
    if not text:
        return
    fut = asyncio.run_coroutine_threadsafe(SHADOW.safe_handle_query(text, gui=gui), BG_LOOP)
    def done_cb(f):
        try:
            f.result()
        except Exception as e:
            print(f"[handle_query error] {e}")
    fut.add_done_callback(done_cb)
    return fut

# ------------------------------
# Background Message Worker
# ------------------------------
async def message_worker():
    while True:
        platform, contact, msg, gui = await SHADOW.message_queue.get()
        if not platform:
            platform = "whatsapp"  # default platform
        reply = await SHADOW.messaging.send_message(platform, contact, msg)
        if gui:
            gui.write_shadow(reply)
        await SHADOW.voice.speak(reply)
        SHADOW.message_queue.task_done()

asyncio.run_coroutine_threadsafe(message_worker(), BG_LOOP)

# ------------------------------
# ROBUST query handler with network error handling
# ------------------------------
async def handle_query(query, gui=None):
    """Robust query handler with network error handling"""
    if not query or query.strip() == "":
        return "I didn't catch anything. Please try again."
    
    # Safety check
    safe, message = SAFETY.check_request(query)
    if not safe:
        if gui:
            gui.write_shadow(message)
        await SHADOW.voice.speak(message)
        return message

    # Messaging automation
    if any(word in query.lower() for word in ["send", "message"]):
        platform, contact, msg = SHADOW.messaging.parse_command(query)
        if contact and msg:
            # Convert message to current language
            msg_in_lang = SHADOW.language_manager.generate_text_in_current_language(msg)
            await SHADOW.message_queue.put((platform, contact, msg_in_lang, gui))
            reply = f"📩 Queued message to {contact} via {platform or 'WhatsApp'}."
            if gui:
                gui.write_shadow(reply)
            await SHADOW.voice.speak(reply)
            return reply

    # Emotion analysis & style
    analysis = SHADOW.emotional_engine.analyze_text(query)
    style = SHADOW.emotional_engine.select_response_style(analysis)
    voice_override = style.get("voice_override") or DEFAULT_VOICE

    # Scheduler commands
    if query.lower().startswith("set timer"):
        import re
        match = re.search(r"(\d+)", query)
        if match:
            seconds = int(match.group(1))
            task = asyncio.create_task(
                SHADOW.scheduler._run_task(seconds, f"⏰ Timer finished: {seconds} sec", callback=SHADOW.voice.speak)
            )
            SHADOW.scheduler.tasks.append(task)
            reply = f"✅ Timer set for {seconds} seconds."
            if gui:
                gui.write_shadow(reply)
            await SHADOW.voice.speak(reply)
            return reply

    # Default AI response with robust error handling
    try:
        response = await asyncio.wait_for(
            SHADOW.safe_handle_query(query, gui),
            timeout=25  # Reasonable timeout for online processing
        )
        
        if gui:
            gui.write_shadow(response)
            gui.set_mode("Speaking")
        await SHADOW.voice.speak(response)
        if gui:
            gui.set_mode("Idle")
        return response
        
    except asyncio.TimeoutError:
        error_msg = "⚠️ Network timeout - The request took too long. Please check your internet connection and try again."
        if gui:
            gui.write_shadow(error_msg)
        await SHADOW.voice.speak(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"⚠️ Network error: {str(e)}. Please check your internet connection."
        if gui:
            gui.write_shadow(error_msg)
        await SHADOW.voice.speak(error_msg)
        return error_msg

# ------------------------------
# CLI Mode - OPENAI STT WITH FALLBACK
# ------------------------------
def run_cli_mode():
    _bg_stop_listening = None

    print("🌌 Shadow CLI Online")
    print(f"🔧 Mode: {SHADOW.stt_mode.upper()} STT | Gemini AI")
    print("💡 Commands: 'voice', 'stoplisten', 'language ur', 'language en', 'exit'")
    print("🎯 Make sure you have stable internet connection")
    print("=" * 60)

    def voice_callback(spoken_text):
        """Voice callback with network error handling"""
        if not spoken_text or spoken_text.strip() == "":
            return
            
        print(f"\n🎤 Voice: {spoken_text}")
        
        # Quick stop command check
        if spoken_text.lower().strip() in ["stop listening", "stop", "exit"]:
            print("🛑 Stopping voice mode...")
            if _bg_stop_listening:
                _bg_stop_listening()
            return
        
        # Process with network error handling
        try:
            response = asyncio.run_coroutine_threadsafe(
                handle_query(spoken_text), 
                BG_LOOP
            ).result(timeout=20)
            
            print(f"🤖 Shadow: {response}")
            
            # Speak response
            asyncio.run_coroutine_threadsafe(
                SHADOW.voice.speak(response),
                BG_LOOP
            )
            
        except asyncio.TimeoutError:
            print("🤖 Shadow: ⚠️ Network timeout - Voice processing took too long.")
        except Exception as e:
            print(f"🤖 Shadow: ⚠️ Network error - {str(e)}")

    while True:
        try:
            q = input("\nYou: ").strip()
            if not q:
                continue
            cmd = q.lower()

            if cmd in ("exit", "quit"):
                if _bg_stop_listening:
                    _bg_stop_listening()
                print("👋 Goodbye!")
                asyncio.run_coroutine_threadsafe(SHADOW.shutdown(), BG_LOOP)
                break

            if cmd == "stop":
                SHADOW.voice.stop()
                continue

            if cmd == "voice":
                if _bg_stop_listening:
                    print("Already listening. Type 'stoplisten' to stop.")
                    continue
                print(f"🎤 Starting {SHADOW.stt_mode.upper()} Speech Recognition...")
                print("💡 Make sure you have internet connection for voice recognition")
                print("💡 Say 'stop listening' to exit voice mode")
                _bg_stop_listening = SHADOW.stt.listen_continuous(
                    callback=voice_callback,
                    event_loop=BG_LOOP
                )
                continue

            if cmd in ("stoplisten", "stop listening"):
                if _bg_stop_listening:
                    _bg_stop_listening()
                    _bg_stop_listening = None
                    print("✅ Voice listening stopped.")
                else:
                    print("No active voice listening.")
                continue

            if cmd.startswith("language "):
                lang_code = cmd.split(" ")[1] if len(cmd.split(" ")) > 1 else "ur"
                if SHADOW.set_preferred_language(lang_code):
                    print(f"✅ Language set to: {SHADOW.multilingual_manager.get_language_info(lang_code)['name']}")
                else:
                    print("❌ Invalid language code. Supported: ur, ps, en")
                continue

            # Process text input with network handling
            print("🤖 Processing...", end=' ', flush=True)
            
            try:
                response = asyncio.run_coroutine_threadsafe(
                    handle_query(q), 
                    BG_LOOP
                ).result(timeout=25)
                
                print(f"\r🤖 Shadow: {response}")
                
            except asyncio.TimeoutError:
                print(f"\r🤖 Shadow: ⚠️ Network timeout - Request took too long. Check your internet.")
            except Exception as e:
                print(f"\r🤖 Shadow: ⚠️ Error - {str(e)}")

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"\n❌ Error: {e}")

# ------------------------------
# GUI Mode - OPENAI STT
# ------------------------------
def run_gui_mode():
    gui = ShadowGUI(on_user_input_callback=None)
    gui.write_shadow("🌌 Shadow AI Online")
    gui.write_shadow(f"🔧 {SHADOW.stt_mode.upper()} STT | Gemini AI")
    gui.write_shadow("💡 Requires internet connection")

    gui._bg_stop = None

    def on_user_input(text):
        if text.strip().lower() == "stop":
            SHADOW.voice.stop()
            return
        if text.strip().lower() == "voice":
            if gui._bg_stop:
                gui.write_shadow("⚠️ Already in speech mode.")
                return
            gui.write_shadow(f"🎤 Starting {SHADOW.stt_mode.upper()} Speech Recognition...")
            gui.write_shadow("💡 Requires internet connection")

            def voice_callback(spoken_text):
                if spoken_text.lower() in ("stop listening", "stop"):
                    gui.write_shadow("🛑 Speech mode stopped.")
                    if gui._bg_stop:
                        gui._bg_stop()
                        gui._bg_stop = None
                    return
                schedule_handle_query(spoken_text, gui=gui)

            gui._bg_stop = SHADOW.stt.listen_continuous(callback=voice_callback, event_loop=BG_LOOP)
            return

        if text.strip().lower().startswith("language "):
            lang_code = text.strip().lower().split(" ")[1] if len(text.strip().lower().split(" ")) > 1 else "ur"
            if SHADOW.set_preferred_language(lang_code):
                gui.write_shadow(f"✅ Language set to: {SHADOW.multilingual_manager.get_language_info(lang_code)['name']}")
            else:
                gui.write_shadow("❌ Invalid language code. Supported: ur, ps, en")
            return

        asyncio.run_coroutine_threadsafe(handle_query(text, gui=gui), BG_LOOP)

    gui.on_user_input = on_user_input
    gui.run()

# ------------------------------
# Multilingual Voice Mode - OPENAI STT
# ------------------------------
def run_multilingual_voice_mode():
    print("🎤 Starting Multilingual Voice Mode...")
    print("🌍 Supported languages: Urdu, Pashto, English")
    print("🗣️ Default language: Urdu")
    print(f"🔧 Using {SHADOW.stt_mode.upper()} for Speech Recognition")
    print("💡 Requires stable internet connection")
    print("⏹️ Press Ctrl+C to stop")
    
    try:
        # Run the multilingual voice loop
        asyncio.run(SHADOW.run_multilingual_voice_loop())
    except KeyboardInterrupt:
        print("\n🛑 Multilingual voice mode stopped")
    except Exception as e:
        print(f"❌ Error in multilingual mode: {e}")

# ------------------------------
# Main Async Entry Point
# ------------------------------
async def main():
    """Main async entry point"""
    try:
        # Start background services
        await SHADOW.start_services()
        
        # Determine mode
        mode = "cli"
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()

        print(f"🚀 Starting Shadow AI in {mode.upper()} mode...")
        print(f"🔧 {SHADOW.stt_mode.upper()} STT & Gemini AI")
        print("💡 Make sure you have stable internet connection")
        
        if mode == "gui":
            run_gui_mode()
        elif mode == "voice":
            run_multilingual_voice_mode()
        else:
            run_cli_mode()
            
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"❌ Fatal error: {e}")
    finally:
        await SHADOW.shutdown()

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
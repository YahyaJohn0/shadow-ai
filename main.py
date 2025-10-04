# main.py
import asyncio
import logging
import sys
import threading
import time
import os
from typing import Dict, Optional, Tuple

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

# Multilingual imports
from shadow_core.multilingual import MultilingualManager, UrduPashtoTranslator, MultilingualBrain
from shadow_core.stt_multilingual import MultilingualSTT
from shadow_core.tts_multilingual import MultilingualTTS

from config import DEFAULT_VOICE, OPENWEATHER_API_KEY, ALPHA_VANTAGE_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ------------------------------
# Initialize Personality & Safety
# ------------------------------
PERSONALITY = Personality()
SYSTEM_PROMPT = PERSONALITY.system_prompt()
SAFETY = Safety()

class Shadow:
    """
    Main Shadow AI Agent class with multilingual support
    """
    
    def __init__(self):
        logger.info("Initializing Shadow AI Agent...")
        
        try:
            # Initialize core components
            self.brain = ShadowBrain()
            self.memory = ShadowMemory()
            self.voice = ShadowVoice()
            self.emo = EmotionalEngine()
            self.tasks = TaskManager(self.memory)
            self.integr = Integrations()
            
            # Initialize Scheduler
            try:
                self.scheduler = Scheduler()
                logger.info("Scheduler module initialized (background task not started)")
            except Exception as e:
                logger.warning(f"Scheduler initialization failed: {e}. Using mock scheduler.")
                self.scheduler = MockScheduler()
            
            # Initialize Knowledge
            try:
                if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_openweather_api_key_here':
                    from shadow_core.knowledge import Knowledge
                    self.knowledge = Knowledge(
                        openweather_api_key=OPENWEATHER_API_KEY,
                        alpha_vantage_api_key=ALPHA_VANTAGE_API_KEY
                    )
                    logger.info("Knowledge module initialized with API keys")
                else:
                    self.knowledge = FreeKnowledge()
                    logger.info("Knowledge module initialized (free version)")
            except Exception as e:
                logger.error(f"Knowledge module initialization failed: {e}")
                self.knowledge = FreeKnowledge()

            # Initialize Automation
            try:
                self.automation = AutomationManager()
                logger.info("Automation module initialized with full computer control")
            except Exception as e:
                logger.warning(f"Automation initialization failed: {e}")
                self.automation = None
            
            # Initialize Messaging
            try:
                self.messaging = Messaging(voice_module=self.voice)
                logger.info("Messaging module initialized")
            except Exception as e:
                logger.warning(f"Messaging initialization failed: {e}")
                self.messaging = MockMessaging()
           
        
             # Initialize brain first
            self.brain = ...  # Your brain initialization
            self.multilingual_manager = MultilingualManager()
        
             # Set brain for multilingual manager (IMPORTANT!)
            self.multilingual_manager.set_brain(self.brain)
            # Initialize Multilingual System
            
            self.translator = UrduPashtoTranslator(self.brain)
            self.multilingual_brain = MultilingualBrain(
                self.brain, 
                self.multilingual_manager, 
                self.translator
            )
            
            # Initialize multilingual STT and TTS
            self.multilingual_stt = MultilingualSTT(self.multilingual_manager)
            self.multilingual_tts = MultilingualTTS(self.multilingual_manager)
            
            # Initialize Language Manager
            self.lang = LanguageManager(default="english")
            
            # Initialize STT
            self.stt_mode = "google"
            if len(sys.argv) > 2 and sys.argv[2].lower() in ("google", "whisper"):
                self.stt_mode = sys.argv[2].lower()
            self.stt = ShadowSTT(mode=self.stt_mode, whisper_model="base", energy_threshold=300)
            
            # Set Urdu as default
            self.multilingual_manager.set_language('ur')
            
            # Initialize Decision Engine with all modules
            self.decision_engine = DecisionEngine(
                brain=self.multilingual_brain,  # Use multilingual brain
                memory=self.memory,
                messaging=self.messaging,
                scheduler=self.scheduler,
                knowledge=self.knowledge,
                automation=self.automation
            )
            
            # Initialize message queue
            self.message_queue = asyncio.Queue()
            
            logger.info("Shadow AI initialized with Urdu/Pashto/English multilingual support")
            
        except Exception as e:
            logger.error(f"Failed to initialize Shadow AI: {e}")
            raise
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
            return response
            
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
        
        # Greet in Urdu (default)
        await self.speak_multilingual("السلام علیکم! میں شاڈو AI ہوں۔ آپ کیسے مدد کر سکتا ہوں؟", 'ur')
        
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

# ------------------------------
# Global Shadow Instance
# ------------------------------
SHADOW = Shadow()

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
    if not text:
        return
    fut = asyncio.run_coroutine_threadsafe(SHADOW.safe_handle_query(text, gui=gui), BG_LOOP)
    def done_cb(f):
        try:
            f.result()
        except Exception as e:
            print("[handle_query error]", e)
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
# Main query handler (legacy compatibility)
# ------------------------------
async def handle_query(query, gui=None):
    if not query:
        return None

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
            msg_in_lang = SHADOW.lang.generate_text_in_current_language(msg)
            await SHADOW.message_queue.put((platform, contact, msg_in_lang, gui))
            reply = f"📩 Queued message to {contact} via {platform or 'WhatsApp'}."
            if gui:
                gui.write_shadow(reply)
            await SHADOW.voice.speak(reply)
            return reply

    # Emotion analysis & style
    analysis = SHADOW.emo.analyze_text(query)
    style = SHADOW.emo.select_response_style(analysis)
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

    # Default AI response using Shadow's multilingual handler
    response = await SHADOW.safe_handle_query(query, gui)
    if gui:
        gui.write_shadow(response)
        gui.set_mode("Speaking")
    await SHADOW.voice.speak(response)
    if gui:
        gui.set_mode("Idle")
    return response

# ------------------------------
# CLI Mode
# ------------------------------
def run_cli_mode():
    _bg_stop_listening = None

    print(PERSONALITY.greeting())
    print("🌌 Shadow CLI online.")
    print("💡 Commands: 'exit', 'quit', 'stop', 'voice', 'stoplisten'")
    print(f"🎙️ STT Mode: {SHADOW.stt_mode.upper()}")
    print(f"🌍 Default Language: {SHADOW.multilingual_manager.get_language_info('ur')['name']}")

    while True:
        q = input("You: ").strip()
        if not q:
            continue
        cmd = q.lower()

        if cmd in ("exit", "quit"):
            if _bg_stop_listening:
                _bg_stop_listening()
            print("Shutting down Shadow. Goodbye.")
            # Schedule shutdown
            asyncio.run_coroutine_threadsafe(SHADOW.shutdown(), BG_LOOP)
            break

        if cmd == "stop":
            SHADOW.voice.stop()
            continue

        if cmd == "voice":
            if _bg_stop_listening:
                print("Already listening in background. Type 'stoplisten' to stop.")
                continue
            print(f"🎤 Background listening started ({SHADOW.stt_mode})")
            _bg_stop_listening = SHADOW.stt.listen_continuous(
                callback=lambda text: schedule_handle_query(text),
                event_loop=BG_LOOP
            )
            continue

        if cmd in ("stoplisten", "stop listening"):
            if _bg_stop_listening:
                _bg_stop_listening()
                _bg_stop_listening = None
                print("✅ Background listening stopped.")
            else:
                print("No background listener running.")
            continue

        if cmd.startswith("language "):
            lang_code = cmd.split(" ")[1] if len(cmd.split(" ")) > 1 else "ur"
            if SHADOW.set_preferred_language(lang_code):
                print(f"✅ Language set to: {SHADOW.multilingual_manager.get_language_info(lang_code)['name']}")
            else:
                print("❌ Invalid language code. Supported: ur, ps, en")
            continue

        # Normal AI handling
        schedule_handle_query(q)

# ------------------------------
# GUI Mode
# ------------------------------
def run_gui_mode():
    gui = ShadowGUI(on_user_input_callback=None)
    gui.write_shadow(f"🎙️ STT Mode: {SHADOW.stt_mode.upper()}")
    gui.write_shadow(PERSONALITY.greeting())
    gui.write_shadow(f"🌍 Default Language: {SHADOW.multilingual_manager.get_language_info('ur')['name']}")

    gui._bg_stop = None

    def on_user_input(text):
        if text.strip().lower() == "stop":
            SHADOW.voice.stop()
            return
        if text.strip().lower() == "voice":
            if gui._bg_stop:
                gui.write_shadow("⚠️ Already in speech mode.")
                return
            gui.write_shadow("🎤 Listening (say 'stop listening' to exit)...")

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
# Multilingual Voice Mode
# ------------------------------
def run_multilingual_voice_mode():
    print("🎤 Starting Multilingual Voice Mode...")
    print("🌍 Supported languages: Urdu, Pashto, English")
    print("🗣️ Default language: Urdu")
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

        if mode == "gui":
            run_gui_mode()
        elif mode == "voice":
            run_multilingual_voice_mode()
        else:
            run_cli_mode()
            
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
    finally:
        await SHADOW.shutdown()

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
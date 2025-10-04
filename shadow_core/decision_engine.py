# shadow_core/decision_engine.py
"""
Decision Engine - Core routing and intent handling for Shadow AI Agent
Routes user queries to appropriate handlers (messaging, knowledge, automation, etc.)
"""
from datetime import datetime
from shadow_core.nlu import NLU, SimpleNLU
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
import re
from shadow_core.knowledge import Knowledge, FreeKnowledge
# Add this import at the top
from shadow_core.enhanced_knowledge import EnhancedKnowledge
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, OPENWEATHER_API_KEY, ALPHA_VANTAGE_API_KEY
from shadow_core.scheduler import Scheduler, MockScheduler, TaskType
from shadow_core.dynamic_nlu import ContextAwareInterpreter, DynamicIntent, IntentType
from shadow_core.multilingual_reminder import MultilingualReminderParser



logger = logging.getLogger(__name__)

# Update imports
from shadow_core.dynamic_nlu import ContextAwareInterpreter, IntentType

# Replace the DecisionEngine class:
class DecisionEngine:
    """
    Enhanced Decision Engine with dynamic AI interpretation
    No keyword dependencies - understands natural language meaning
    """
    
    def __init__(self, brain, memory, messaging=None, scheduler=None, knowledge=None, automation=None):
        self.brain = brain
        self.memory = memory
        self.messaging = messaging
        self.scheduler = scheduler
        self.knowledge = knowledge
        self.automation = automation
        
        # Initialize Dynamic AI Interpreter
        self.interpreter = ContextAwareInterpreter(brain)
        
        # Initialize modules
        self._initialize_modules()
        self.reminder_parser = MultilingualReminderParser(brain)
        
        logger.info("Decision Engine initialized with Dynamic AI Interpretation")
    
    def _initialize_modules(self):
        """Initialize all capability modules"""
        try:
            from shadow_core.messaging import Messaging
            self.messaging = self.messaging or Messaging()
        except:
            from shadow_core.messaging import MockMessaging
            self.messaging = self.messaging or MockMessaging()
        
        try:
            from shadow_core.scheduler import Scheduler
            self.scheduler = self.scheduler or Scheduler()
        except:
            from shadow_core.scheduler import MockScheduler
            self.scheduler = self.scheduler or MockScheduler()
        
        try:
            from shadow_core.knowledge import FreeKnowledge
            self.knowledge = self.knowledge or FreeKnowledge()
        except:
            self.knowledge = None
        
        try:
            from shadow_core.automation import AutomationManager
            self.automation = self.automation or AutomationManager()
        except:
            self.automation = None
    
    async def handle_query(self, text: str, gui=None) -> str:
        """
        Handle user query with dynamic AI interpretation
        Understands meaning and context, not just keywords
        """
       
        
        if not text or text.strip() == "":
            return "I didn't catch that. Could you please repeat?"
        
        logger.info(f"Dynamic interpretation of: {text}")
        
        if gui:
            gui.update_status("Understanding your request...")
        
        try:
            # Step 1: Dynamic AI Interpretation
            intent = await self.interpreter.interpret_with_context(text)
            
            logger.info(f"Interpreted as: {intent.action} -> {intent.target} (confidence: {intent.confidence})")

            reminder_intent = await self._detect_reminder_intent(text, intent)
            if reminder_intent:
                return await self._handle_reminder_request(text, reminder_intent, gui)
            
           
            result = await self._execute_dynamic_intent(intent, text, gui)
            
           
            self.memory.save_chat(text, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Dynamic handling error: {e}")
            error_msg = "I encountered an error understanding your request. Please try again."
            self.memory.save_chat(text, error_msg)
            return error_msg
    
    async def _detect_reminder_intent(self, text: str, existing_intent: DynamicIntent) -> Optional[Dict[str, Any]]:
        """Detect if the query is a reminder request"""
        text_lower = text.lower()
        
        # Check for reminder keywords in all languages
        reminder_keywords = {
            'ur': ['یاد', 'یاد دہانی', 'یاد دلاؤ', 'نوٹ', 'الارم'],
            'ps': ['یادونه', 'یاد راکړه', 'یاد کړه', 'یادول'],
            'en': ['remind', 'remember', 'alert', 'reminder', 'alarm']
        }
        
        # Detect language of input
        detected_lang = await self.interpreter.multilingual_manager.detect_language(text)
        
        # Check if text contains reminder keywords for detected language
        keywords = reminder_keywords.get(detected_lang, [])
        if any(keyword in text_lower for keyword in keywords):
            return {
                'is_reminder': True,
                'language': detected_lang,
                'confidence': 0.8
            }
        
        return None
    
    async def _handle_reminder_request(self, text: str, reminder_intent: Dict[str, Any], gui=None) -> str:
        """Handle reminder requests in any language"""
        try:
            language = reminder_intent['language']
            
            if gui:
                gui.update_status(f"Setting reminder in {language}...")
            
            # Use the scheduler to set reminder
            result = await self.scheduler.set_multilingual_reminder(text, language)
            
            if result['success']:
                # Return user-friendly message in their language
                return result.get('user_message', 'Reminder set successfully!')
            else:
                error_messages = {
                    'ur': f"یاد دہانی سیٹ کرنے میں مسئلہ: {result.get('error', 'نامعلوم خرابی')}",
                    'ps': f"د یادونه سیٹ کولو کې ستونزه: {result.get('error', 'نامعلومه ستونزه')}",
                    'en': f"Problem setting reminder: {result.get('error', 'Unknown error')}"
                }
                return error_messages.get(language, error_messages['en'])
                
        except Exception as e:
            logger.error(f"Reminder handling error: {e}")
            
            error_messages = {
                'ur': "یاد دہانی سیٹ کرنے میں خرابی آ گئی۔",
                'ps': "د یادونه سیٹ کولو کې تېروتنه راغله۔",
                'en': "Error setting reminder."
            }
            
            language = reminder_intent.get('language', 'en')
            return error_messages.get(language, error_messages['en'])
    async def _execute_dynamic_intent(self, intent, original_text: str, gui=None) -> str:
        """
        Execute action based on dynamically interpreted intent
        """
        # Low confidence fallback
        if intent.confidence < 0.3:
            return await self._handle_chat(original_text, gui)
        
        try:
            # Route based on interpreted intent type
            if intent.intent_type == IntentType.MESSAGING:
                return await self._handle_dynamic_messaging(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.KNOWLEDGE:
                return await self._handle_dynamic_knowledge(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.SCHEDULING:
                return await self._handle_dynamic_scheduling(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.AUTOMATION:
                return await self._handle_dynamic_automation(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.SYSTEM:
                return await self._handle_dynamic_system(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.FILE_OPS:
                return await self._handle_dynamic_files(intent, original_text, gui)
            
            elif intent.intent_type == IntentType.WEB:
                return await self._handle_dynamic_web(intent, original_text, gui)
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            logger.error(f"Dynamic execution error: {e}")
            return f"I understood you wanted {intent.action}, but encountered an error: {str(e)}"
    
    async def _handle_dynamic_messaging(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted messaging requests"""
        if not self.messaging:
            return "Messaging is not available right now."
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            if "send_message" in action:
                contact = target or params.get("contact")
                message = params.get("message")
                platform = params.get("platform", "whatsapp")
                
                if not contact:
                    return "Who would you like to message?"
                if not message:
                    return f"What would you like to say to {contact}?"
                
                success = await self.messaging.send_message(platform, contact, message)
                return f"Message sent to {contact}!" if success else f"Failed to send message to {contact}"
            
            elif "add_contact" in action:
                # Extract contact details from parameters
                name = target or params.get("name")
                phone = params.get("phone")
                
                if name and phone:
                    self.messaging.add_contact(name, phone)
                    return f"Added {name} to contacts!"
                else:
                    return "I need a name and phone number to add a contact."
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"Messaging error: {str(e)}"
    
    async def _handle_dynamic_knowledge(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted knowledge requests"""
        if not self.knowledge:
            return await self._handle_chat(original_text, gui)
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            if "get_weather" in action:
                location = target or params.get("location", "current location")
                return await self.knowledge.get_weather(location)
            
            elif "get_stock" in action or "stock_price" in action:
                symbol = target or params.get("symbol")
                if symbol:
                    return await self.knowledge.get_stock_price(symbol)
                else:
                    return "Which stock would you like information about?"
            
            elif "search" in action or "look_up" in action:
                query = target or params.get("query", original_text)
                return await self.knowledge.web_search(query)
            
            elif "news" in action:
                topic = target or params.get("topic", "general")
                return await self.knowledge.get_news(topic)
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"Knowledge error: {str(e)}"
    
    async def _handle_dynamic_scheduling(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted scheduling requests"""
        if not self.scheduler:
            return "Scheduling is not available right now."
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            if "remind" in action:
                message = target or params.get("message", "Reminder")
                time_expr = params.get("time")
                
                if time_expr:
                    task_id = await self.scheduler.set_alarm(time_expr, message)
                    return f"Reminder set for {time_expr}! (ID: {task_id})"
                else:
                    return "When would you like to be reminded?"
            
            elif "timer" in action:
                duration = params.get("duration", 5)
                unit = params.get("unit", "minute")
                
                task_id = await self.scheduler.set_timer(
                    duration_minutes=duration if unit in ["minute", "min"] else 0,
                    duration_seconds=0,
                    title=f"Timer for {duration} {unit}s"
                )
                return f"Timer set for {duration} {unit}s! (ID: {task_id})"
            
            elif "alarm" in action:
                time_str = target or params.get("time")
                if time_str:
                    task_id = await self.scheduler.set_alarm(time_str, "Alarm")
                    return f"Alarm set for {time_str}! (ID: {task_id})"
                else:
                    return "What time should I set the alarm for?"
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"Scheduling error: {str(e)}"
    
    async def _handle_dynamic_automation(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted automation requests"""
        if not self.automation:
            return "Automation is not available right now."
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            # Map dynamic actions to automation commands
            action_map = {
                "open_app": "open_app",
                "close_app": "close_app",
                "open_file": "open_file",
                "read_file": "read_file",
                "list_files": "list_files",
                "click": "click",
                "type": "type",
                "screenshot": "screenshot"
            }
            
            automation_command = action_map.get(action)
            if automation_command:
                result = await self.automation.automate(automation_command, {
                    "name": target,
                    "path": target,
                    "text": params.get("text"),
                    "x": params.get("x"),
                    "y": params.get("y")
                })
                
                if result.get("success"):
                    return result.get("message", f"Completed {action}")
                else:
                    return f"Automation failed: {result.get('error')}"
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"Automation error: {str(e)}"
    
    async def _handle_dynamic_system(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted system operations"""
        if not self.automation:
            return "System control is not available right now."
        
        action = intent.action
        params = intent.parameters
        
        try:
            if "shutdown" in action:
                result = await self.automation.automate("shutdown", params)
                return result.get("message", "Shutting down system") if result.get("success") else "Shutdown failed"
            
            elif "restart" in action:
                result = await self.automation.automate("restart", params)
                return result.get("message", "Restarting system") if result.get("success") else "Restart failed"
            
            elif "volume" in action:
                level = params.get("level")
                action_type = "increase" if "increase" in action else "decrease" if "decrease" in action else "set"
                result = await self.automation.automate("volume", {"level": level, "action": action_type})
                return result.get("message", "Volume adjusted") if result.get("success") else "Volume control failed"
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"System control error: {str(e)}"
    
    async def _handle_dynamic_files(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted file operations"""
        if not self.automation:
            return "File operations are not available right now."
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            if "open_file" in action or "open_folder" in action:
                result = await self.automation.automate("open_file", {"path": target})
                return result.get("message", f"Opened {target}") if result.get("success") else f"Could not open {target}"
            
            elif "list_files" in action or "show_files" in action:
                result = await self.automation.automate("list_files", {"path": target or "."})
                if result.get("success"):
                    count = result.get("count", 0)
                    return f"Found {count} items in {target or 'current folder'}"
                else:
                    return "Could not list files"
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"File operation error: {str(e)}"
    
    async def _handle_dynamic_web(self, intent, original_text: str, gui=None) -> str:
        """Handle dynamically interpreted web operations"""
        if not self.automation:
            return "Web operations are not available right now."
        
        action = intent.action
        target = intent.target
        params = intent.parameters
        
        try:
            if "search" in action or "look_up" in action:
                query = target or params.get("query", original_text)
                result = await self.automation.automate("web_search", {"query": query})
                return result.get("message", f"Searching for {query}") if result.get("success") else "Search failed"
            
            elif "open_url" in action or "browse" in action:
                url = target or params.get("url")
                if url:
                    result = await self.automation.automate("open_url", {"url": url})
                    return result.get("message", f"Opened {url}") if result.get("success") else "Could not open URL"
                else:
                    return "Which website would you like to visit?"
            
            else:
                return await self._handle_chat(original_text, gui)
                
        except Exception as e:
            return f"Web operation error: {str(e)}"
    
    async def _handle_chat(self, text: str, gui=None) -> str:
        """Handle general chat with context awareness"""
        try:
            if gui:
                gui.update_status("Thinking...")
            
            # Get conversation context
            context = self.interpreter.get_conversation_state()
            
            # Prepare messages with context
            messages = [
                {
                    "role": "system", 
                    "content": f"""You are Shadow, a helpful AI assistant. 
                    Current context: {context}
                    Be conversational and helpful."""
                }
            ]
            
            # Add recent memory
            memory_context = self.memory.get_recent(2)
            for role, content in memory_context:
                messages.append({"role": role, "content": content})
            
            # Add current query
            messages.append({"role": "user", "content": text})
            
            # Get AI response
            response = await self.brain.ask(messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm having trouble thinking right now. Please try again."
    
    def get_conversation_insights(self) -> Dict[str, Any]:
        """Get insights about current conversation"""
        return self.interpreter.get_conversation_state()

class BasicNLU:
    """
    Basic NLU using simple rule-based matching
    """
    
    async def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Basic intent classification using keyword matching"""
        text_lower = text.lower()
        
        # Messaging intents
        if any(word in text_lower for word in ["send", "message", "text"]) and any(word in text_lower for word in ["whatsapp", "message", "sms"]):
            return "send_message", self._extract_message_entities(text)
        
        # Weather intents
        if any(word in text_lower for word in ["weather", "temperature", "forecast", "rain", "sunny"]):
            return "get_weather", self._extract_weather_entities(text)
        
        # Stock intents
        if any(word in text_lower for word in ["stock", "price", "share", "crypto", "bitcoin"]):
            return "get_stock", self._extract_stock_entities(text)
        
        # Search intents
        if any(word in text_lower for word in ["search", "google", "look up", "find information", "search for"]):
            return "search_web", self._extract_search_entities(text)
        
        # Scheduling intents
        if any(word in text_lower for word in ["remind", "reminder", "schedule", "timer", "alarm"]):
            return "set_reminder", self._extract_scheduling_entities(text)
        
        # Translation intents
        if any(word in text_lower for word in ["translate", "translation", "in spanish", "in french"]):
            return "translate", self._extract_translation_entities(text)
        
        # Default to chat
        return "chat", {}
    
    def _extract_message_entities(self, text: str) -> Dict[str, Any]:
        """Extract messaging entities from text"""
        text_lower = text.lower()
        entities = {"platform": "whatsapp", "message": ""}
        
        # Extract platform
        if "whatsapp" in text_lower:
            entities["platform"] = "whatsapp"
        elif "sms" in text_lower or "text" in text_lower:
            entities["platform"] = "sms"
        
        # Extract contact and message using regex
        contact_match = re.search(r'(?:to|for|contact)\s+(\w+)', text_lower)
        if contact_match:
            entities["contact"] = contact_match.group(1)
        
        # Extract message content (text after "saying" or "message")
        message_match = re.search(r'(?:saying|message|text)\s+(.+)', text_lower)
        if message_match:
            entities["message"] = message_match.group(1)
        else:
            # Fallback: use last part of sentence
            words = text.split()
            if len(words) > 3:
                entities["message"] = " ".join(words[-5:])
        
        return entities
    
    def _extract_weather_entities(self, text: str) -> Dict[str, Any]:
        """Extract weather-related entities"""
        text_lower = text.lower()
        entities = {"location": "current location"}
        
        # Look for location mentions
        location_match = re.search(r'(?:in|at|for)\s+(\w+)', text_lower)
        if location_match:
            entities["location"] = location_match.group(1)
        
        # Check for city names (basic)
        cities = ["london", "new york", "paris", "tokyo", "mumbai", "delhi"]
        for city in cities:
            if city in text_lower:
                entities["location"] = city
                break
        
        return entities
    
    def _extract_stock_entities(self, text: str) -> Dict[str, Any]:
        """Extract stock-related entities"""
        text_lower = text.lower()
        entities = {}
        
        # Look for stock symbols (uppercase words 1-5 chars)
        words = text.split()
        for word in words:
            if 1 <= len(word) <= 5 and word.isupper() and word.isalpha():
                entities["symbol"] = word
                break
        
        # Look for crypto
        cryptos = {"bitcoin": "BTC", "ethereum": "ETH", "dogecoin": "DOGE"}
        for crypto_name, symbol in cryptos.items():
            if crypto_name in text_lower:
                entities["symbol"] = symbol
                break
        
        return entities
    
    def _extract_search_entities(self, text: str) -> Dict[str, Any]:
        """Extract search query entities"""
        text_lower = text.lower()
        
        # Remove search keywords
        search_keywords = ["search", "look up", "find", "information about", "google"]
        query = text_lower
        for keyword in search_keywords:
            query = query.replace(keyword, "")
        
        return {"query": query.strip()}
    
    def _extract_scheduling_entities(self, text: str) -> Dict[str, Any]:
        """Extract scheduling entities"""
        entities = {}
        text_lower = text.lower()
        
        # Extract time references (very basic)
        time_patterns = [
            r'(\d+)\s*(?:minute|min|hour|hr|second|sec)',
            r'in\s+(\d+)\s*(?:minute|min|hour|hr)',
            r'at\s+(\d+:\d+)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities["time"] = match.group(1)
                break
        
        return entities
    
    def _extract_translation_entities(self, text: str) -> Dict[str, Any]:
        """Extract translation entities"""
        entities = {}
        text_lower = text.lower()
        
        # Extract target language
        languages = {
            "spanish": "es", "french": "fr", "german": "de", 
            "italian": "it", "japanese": "ja", "chinese": "zh"
        }
        
        for lang_name, lang_code in languages.items():
            if lang_name in text_lower:
                entities["target_language"] = lang_code
                break
        
        return entities
    
    
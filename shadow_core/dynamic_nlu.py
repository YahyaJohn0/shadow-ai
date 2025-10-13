# shadow_core/dynamic_nlu.py
"""
Simplified NLU system that directly understands intent without JSON
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    MESSAGING = "messaging"
    KNOWLEDGE = "knowledge" 
    SCHEDULING = "scheduling"
    AUTOMATION = "automation"
    SYSTEM = "system"
    FILE_OPS = "file_operations"
    WEB = "web_operations"
    CHAT = "chat"
    UNKNOWN = "unknown"

@dataclass
class DynamicIntent:
    intent_type: IntentType
    confidence: float
    action: str
    target: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    reasoning: str

class SimpleInterpreter:
    """
    Simple interpreter that directly understands natural language
    No JSON, no complex parsing - just direct understanding
    """
    
    def __init__(self, brain, multilingual_manager=None):
        self.brain = brain
        self.multilingual_manager = multilingual_manager
        self.conversation_context = {
            "current_topic": None,
            "recent_intents": [],
            "user_preferences": {},
            "active_tasks": []
        }
        logger.info("Simple Interpreter initialized")
    
    async def interpret(self, text: str, user_context: Dict[str, Any] = None) -> DynamicIntent:
        """
        Direct interpretation using AI understanding
        """
        try:
            # Detect language
            detected_lang = await self._detect_language(text)
            
            # Build context
            full_context = {
                **self.conversation_context,
                **(user_context or {}),
                "detected_language": detected_lang
            }
            
            # Use AI to directly understand intent
            intent = await self._direct_intent_analysis(text, detected_lang, full_context)
            
            # Update conversation context
            self._update_context(text, intent)
            
            return intent
            
        except Exception as e:
            logger.error(f"Interpretation error: {e}")
            return self._create_fallback_intent(text)
    
    async def _direct_intent_analysis(self, text: str, language: str, context: Dict[str, Any]) -> DynamicIntent:
        """Direct intent analysis using AI without JSON"""
        
        prompt = f"""
        Analyze this user message and determine the intent. Respond with a simple classification.
        
        User: "{text}"
        Language: {language}
        
        What is the user trying to do? Choose from:
        - greeting (hello, hi, hey, greetings)
        - question (what, how, when, where, why questions)  
        - request_help (help, assist, support needed)
        - weather_inquiry (weather, temperature, forecast)
        - reminder (remind, remember, alert me)
        - message (send message, tell someone, contact)
        - system (shutdown, volume, computer control)
        - automation (open app, start program, show files)
        - search (search for, find information, look up)
        - general_chat (casual conversation, chatting)
        
        Respond in this format:
        INTENT: [intent_name]
        CONFIDENCE: [0.0-1.0]
        ACTION: [specific_action]
        TARGET: [primary_target]
        REASONING: [brief explanation]
        
        Examples:
        
        User: "hello"
        INTENT: greeting
        CONFIDENCE: 0.98
        ACTION: greet
        TARGET: user
        REASONING: simple greeting
        
        User: "what's the weather like?"
        INTENT: weather_inquiry  
        CONFIDENCE: 0.95
        ACTION: get_weather
        TARGET: current location
        REASONING: asking about weather conditions
        
        User: "help me today"
        INTENT: request_help
        CONFIDENCE: 0.90
        ACTION: provide_assistance
        TARGET: user
        REASONING: requesting help or support
        
        User: "remind me to call mom"
        INTENT: reminder
        CONFIDENCE: 0.96
        ACTION: set_reminder
        TARGET: call mom
        REASONING: reminder request
        
        Now analyze this user message:
        User: "{text}"
        """
        
        response = await self.brain.ask([{"role": "system", "content": prompt}])
        return self._parse_direct_response(response, text, language)
    
    def _parse_direct_response(self, response: str, original_text: str, language: str) -> DynamicIntent:
        """Parse direct AI response without JSON"""
        try:
            lines = response.strip().split('\n')
            intent_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    intent_data[key.strip().lower()] = value.strip()
            
            # Map to our intent types
            intent_map = {
                'greeting': (IntentType.CHAT, 'greet', 0.95),
                'question': (IntentType.CHAT, 'answer', 0.85),
                'request_help': (IntentType.CHAT, 'provide_assistance', 0.90),
                'weather_inquiry': (IntentType.KNOWLEDGE, 'get_weather', 0.95),
                'reminder': (IntentType.SCHEDULING, 'set_reminder', 0.96),
                'message': (IntentType.MESSAGING, 'send_message', 0.94),
                'system': (IntentType.SYSTEM, 'system_command', 0.88),
                'automation': (IntentType.AUTOMATION, 'open_app', 0.87),
                'search': (IntentType.KNOWLEDGE, 'search_web', 0.89),
                'general_chat': (IntentType.CHAT, 'respond', 0.80)
            }
            
            intent_key = intent_data.get('intent', 'general_chat').lower()
            intent_type, default_action, default_confidence = intent_map.get(intent_key, (IntentType.CHAT, 'respond', 0.8))
            
            confidence = float(intent_data.get('confidence', default_confidence))
            action = intent_data.get('action', default_action)
            target = intent_data.get('target', 'user')
            reasoning = intent_data.get('reasoning', 'AI direct analysis')
            
            logger.info(f"Direct interpretation: {intent_type.value} -> {action} (confidence: {confidence})")
            
            return DynamicIntent(
                intent_type=intent_type,
                confidence=confidence,
                action=action,
                target=target,
                parameters={"query": original_text, "language": language},
                context={"language": language},
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Direct response parsing error: {e}")
            return self._create_fallback_intent(original_text)
    
    async def _detect_language(self, text: str) -> str:
        """Detect language of the text"""
        try:
            if self.multilingual_manager:
                return await self.multilingual_manager.detect_language(text)
            else:
                # Basic detection
                text_lower = text.lower()
                if any(word in text_lower for word in ['aap', 'mujhe', 'sun', 'rahe', 'ho', 'ہے', 'کیا']):
                    return 'ur'
                elif any(word in text_lower for word in ['ستا', 'زه', 'اور', 'دی']):
                    return 'ps'
                else:
                    return 'en'
        except:
            return 'en'
    
    def _create_fallback_intent(self, text: str) -> DynamicIntent:
        """Simple fallback intent"""
        text_lower = text.lower().strip()
        
        # Simple pattern matching
        if text_lower in ['hello', 'hi', 'hey', 'greetings']:
            return DynamicIntent(
                intent_type=IntentType.CHAT,
                confidence=0.95,
                action="greet",
                target="user",
                parameters={"query": text},
                context={},
                reasoning="Simple greeting"
            )
        elif any(word in text_lower for word in ['help', 'assist', 'support']):
            return DynamicIntent(
                intent_type=IntentType.CHAT,
                confidence=0.90,
                action="provide_assistance", 
                target="user",
                parameters={"query": text},
                context={},
                reasoning="Help request"
            )
        elif any(word in text_lower for word in ['weather', 'temperature']):
            return DynamicIntent(
                intent_type=IntentType.KNOWLEDGE,
                confidence=0.92,
                action="get_weather",
                target="current location",
                parameters={"query": text},
                context={},
                reasoning="Weather inquiry"
            )
        else:
            return DynamicIntent(
                intent_type=IntentType.CHAT,
                confidence=0.85,
                action="respond",
                target="user",
                parameters={"query": text},
                context={},
                reasoning="General conversation"
            )
    
    def _update_context(self, text: str, intent: DynamicIntent):
        """Update conversation context"""
        if intent.target and intent.target != "user":
            self.conversation_context["current_topic"] = intent.target
        
        self.conversation_context["recent_intents"].append({
            "intent": intent.intent_type.value,
            "action": intent.action,
            "target": intent.target,
            "timestamp": self._get_timestamp()
        })
        
        if len(self.conversation_context["recent_intents"]) > 5:
            self.conversation_context["recent_intents"].pop(0)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

class ContextAwareInterpreter:
    """
    Simplified context-aware interpreter
    """
    
    def __init__(self, brain, multilingual_manager=None):
        self.brain = brain
        self.multilingual_manager = multilingual_manager
        self.interpreter = SimpleInterpreter(brain, multilingual_manager)
        self.conversation_context = {
            "current_topic": None,
            "recent_intents": [],
            "active_tasks": []
        }
        logger.info("ContextAwareInterpreter initialized")
    
    async def interpret_with_context(self, text: str, user_context: Dict[str, Any] = None) -> DynamicIntent:
        """Interpret with context"""
        full_context = {
            **self.conversation_context,
            **(user_context or {})
        }
        
        intent = await self.interpreter.interpret(text, full_context)
        self._update_context(text, intent)
        
        return intent
    
    def _update_context(self, text: str, intent: DynamicIntent):
        """Update context"""
        if intent.intent_type != IntentType.CHAT:
            self.conversation_context["current_topic"] = intent.target
        
        self.conversation_context["recent_intents"].append({
            "intent": intent.intent_type.value,
            "action": intent.action,
            "target": intent.target,
            "timestamp": self._get_timestamp()
        })
        
        if len(self.conversation_context["recent_intents"]) > 5:
            self.conversation_context["recent_intents"].pop(0)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_state(self) -> Dict[str, Any]:
        return {
            "topic": self.conversation_context["current_topic"],
            "recent_actions": [f"{item['action']}->{item['target']}" 
                              for item in self.conversation_context["recent_intents"][-3:]]
        }
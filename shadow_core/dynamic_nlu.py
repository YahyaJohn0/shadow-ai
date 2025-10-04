# shadow_core/dynamic_nlu.py
"""
Dynamic NLU system with real AI interpretation - No fixed patterns
Uses advanced prompting and context understanding
"""

import logging
import json
import re
import asyncio
from typing import Dict, Any, List, Tuple, Optional
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

class AdvancedInterpreter:
    """
    Advanced AI interpreter that truly understands natural language
    without relying on keyword patterns
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.conversation_context = {
            "current_topic": None,
            "recent_intents": [],
            "user_preferences": {},
            "active_tasks": []
        }
        logger.info("Advanced AI Interpreter initialized")
    
    async def interpret(self, text: str, user_context: Dict[str, Any] = None) -> DynamicIntent:
        """
        Advanced interpretation using deep semantic understanding
        """
        try:
            # Build comprehensive context
            full_context = {
                **self.conversation_context,
                **(user_context or {}),
                "text_analysis": self._analyze_text_structure(text)
            }
            
            # Get AI interpretation with advanced prompting
            prompt = self._build_advanced_prompt(text, full_context)
            response = await self.brain.ask([{"role": "system", "content": prompt}])
            
            # Parse and validate interpretation
            intent = self._parse_advanced_response(response, text)
            
            # Update conversation context
            self._update_advanced_context(text, intent)
            
            return intent
            
        except Exception as e:
            logger.error(f"Advanced interpretation error: {e}")
            return self._create_fallback_intent(text)
    
    def _build_advanced_prompt(self, text: str, context: Dict[str, Any]) -> str:
        """Build sophisticated interpretation prompt"""
        
        return f"""
        You are an advanced intent interpreter. Deeply analyze the user's query to understand:
        
        1. CORE INTENT: What is the fundamental goal or need behind the words?
        2. CONTEXTUAL MEANING: How does context affect interpretation?
        3. IMPLIED ACTIONS: What actions are implicitly requested?
        4. ENTITY EXTRACTION: What specific entities are mentioned?
        
        QUERY: "{text}"
        
        CONTEXT:
        - Current Topic: {context.get('current_topic', 'None')}
        - Recent Actions: {context.get('recent_intents', [])[-3:]}
        - Text Analysis: {context.get('text_analysis', {})}
        
        ANALYZE THESE ASPECTS:
        - Urgency level (casual, normal, urgent)
        - Specificity (vague, specific, very specific)
        - Action type (retrieval, creation, modification, communication)
        - Domain (personal, work, entertainment, system)
        
        RESPONSE FORMAT (JSON only):
        {{
            "intent_type": "messaging|knowledge|scheduling|automation|system|file_operations|web_operations|chat|unknown",
            "confidence": 0.0-1.0,
            "action": "specific_technical_action",
            "target": "primary_target_entity", 
            "parameters": {{
                "key1": "value1",
                "key2": "value2"
            }},
            "reasoning": "detailed_analysis_of_meaning_and_context",
            "urgency": "casual|normal|urgent",
            "specificity": "vague|specific|very_specific"
        }}
        
        INTERPRETATION GUIDELINES:
        
        MESSAGING INTENT (communication with people):
        - "Let John know..." → messaging, action: "send_message", target: "John"
        - "Tell Sarah that..." → messaging, action: "send_message", target: "Sarah" 
        - "Message the team..." → messaging, action: "send_group_message", target: "team"
        
        KNOWLEDGE INTENT (information seeking):
        - "What's the weather..." → knowledge, action: "get_weather", target: location
        - "Stock price of..." → knowledge, action: "get_stock", target: symbol
        - "Tell me about..." → knowledge, action: "search_web", target: topic
        
        SCHEDULING INTENT (time-based actions):
        - "Remind me to..." → scheduling, action: "set_reminder", target: task
        - "Set alarm for..." → scheduling, action: "set_alarm", target: time
        - "I need to remember..." → scheduling, action: "set_reminder", target: task
        
        AUTOMATION INTENT (computer control):
        - "Open my documents" → automation, action: "open_folder", target: "documents"
        - "Show me files in..." → automation, action: "list_files", target: folder
        - "Start Chrome" → automation, action: "open_app", target: "Chrome"
        
        SYSTEM INTENT (system operations):
        - "Shutdown computer" → system, action: "shutdown", target: "system"
        - "Make it quieter" → system, action: "volume_down", target: "audio"
        - "Brighten screen" → system, action: "brightness_up", target: "display"
        
        FILE OPERATIONS (file management):
        - "Find my project file" → file_operations, action: "search_files", target: "project file"
        - "Read the document" → file_operations, action: "read_file", target: document_path
        - "Create a new file" → file_operations, action: "create_file", target: file_name
        
        WEB OPERATIONS (online actions):
        - "Search for python tutorials" → web_operations, action: "web_search", target: "python tutorials"
        - "Open google.com" → web_operations, action: "open_url", target: "google.com"
        - "Browse to my email" → web_operations, action: "open_url", target: "email provider"
        
        CHAT INTENT (conversation):
        - General questions, explanations, casual conversation
        - "How does this work?" → chat, action: "explain", target: topic
        - "Tell me a joke" → chat, action: "entertain", target: "user"
        
        EXAMPLES:
        
        Query: "Can you give John a heads-up that I'm running behind schedule?"
        {{
            "intent_type": "messaging",
            "confidence": 0.95,
            "action": "send_message", 
            "target": "John",
            "parameters": {{"message": "I'm running behind schedule", "urgency": "normal"}},
            "reasoning": "User wants to notify John about being late, implied urgency but not critical",
            "urgency": "normal",
            "specificity": "specific"
        }}
        
        Query: "What's it like outside in Tokyo right now?"
        {{
            "intent_type": "knowledge",
            "confidence": 0.98, 
            "action": "get_weather",
            "target": "Tokyo",
            "parameters": {{"location": "Tokyo", "timeframe": "current"}},
            "reasoning": "User is asking for current weather conditions in Tokyo",
            "urgency": "normal", 
            "specificity": "specific"
        }}
        
        Query: "I need to remember the team sync at 2 PM"
        {{
            "intent_type": "scheduling",
            "confidence": 0.96,
            "action": "set_reminder",
            "target": "team sync",
            "parameters": {{"time": "14:00", "message": "Team sync meeting"}},
            "reasoning": "User wants to create a reminder for a scheduled team meeting",
            "urgency": "normal",
            "specificity": "very_specific"
        }}
        
        Query: "Could you show me what's in my documents?"
        {{
            "intent_type": "automation", 
            "confidence": 0.92,
            "action": "list_files",
            "target": "documents folder",
            "parameters": {{"folder": "documents"}},
            "reasoning": "User wants to view contents of documents directory",
            "urgency": "casual",
            "specificity": "specific"
        }}
        
        Query: "Make the computer ready for bed"
        {{
            "intent_type": "system",
            "confidence": 0.89,
            "action": "sleep_system",
            "target": "computer",
            "parameters": {{}},
            "reasoning": "User wants to put system to sleep mode, implied end of work session",
            "urgency": "casual", 
            "specificity": "vague"
        }}
        
        Query: "How do I fix this issue with my code?"
        {{
            "intent_type": "chat",
            "confidence": 0.88,
            "action": "explain_solution",
            "target": "code issue",
            "parameters": {{"topic": "programming help"}},
            "reasoning": "User is asking for help with a coding problem, needs explanation",
            "urgency": "normal",
            "specificity": "vague"
        }}
        
        Query: "Let Sarah know the project is approved"
        {{
            "intent_type": "messaging",
            "confidence": 0.94,
            "action": "send_message",
            "target": "Sarah", 
            "parameters": {{"message": "The project is approved"}},
            "reasoning": "User wants to notify Sarah about project approval",
            "urgency": "normal",
            "specificity": "specific"
        }}
        
        Query: "What's the latest with Tesla stock?"
        {{
            "intent_type": "knowledge",
            "confidence": 0.97,
            "action": "get_stock",
            "target": "TSLA",
            "parameters": {{"symbol": "TSLA", "info_type": "latest"}},
            "reasoning": "User wants current stock information for Tesla",
            "urgency": "normal",
            "specificity": "specific"
        }}
        
        Query: "I want to wake up at 7 tomorrow"
        {{
            "intent_type": "scheduling",
            "confidence": 0.95,
            "action": "set_alarm", 
            "target": "wake up",
            "parameters": {{"time": "07:00", "date": "tomorrow"}},
            "reasoning": "User wants to set a wake-up alarm for tomorrow morning",
            "urgency": "normal",
            "specificity": "very_specific"
        }}
        
        Query: "Can you find that file I was working on yesterday?"
        {{
            "intent_type": "file_operations",
            "confidence": 0.90,
            "action": "search_recent_files",
            "target": "recent work file",
            "parameters": {{"timeframe": "yesterday", "file_type": "work"}},
            "reasoning": "User wants to locate a recently edited file from yesterday",
            "urgency": "normal",
            "specificity": "vague"
        }}
        """
    
    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure for contextual clues"""
        text_lower = text.lower()
        
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "has_question_words": any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why']),
            "has_actions": any(word in text_lower for word in ['open', 'close', 'send', 'set', 'get', 'find']),
            "has_people": any(word in text_lower for word in ['john', 'sarah', 'team', 'mom', 'dad']),
            "has_times": any(word in text_lower for word in ['now', 'later', 'tomorrow', 'today', 'minutes', 'hours']),
            "has_locations": any(word in text_lower for word in ['london', 'tokyo', 'paris', 'here', 'there']),
            "urgency_indicators": sum(1 for word in ['urgent', 'now', 'quick', 'asap', 'emergency'] if word in text_lower)
        }
    
    def _parse_advanced_response(self, response: str, original_text: str) -> DynamicIntent:
        """Parse AI response with validation"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|{[^{}]*}', response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON found in AI response")
                return self._create_fallback_intent(original_text)
            
            data = json.loads(json_match.group())
            
            # Validate required fields
            required_fields = ['intent_type', 'confidence', 'action', 'target', 'parameters', 'reasoning']
            if not all(field in data for field in required_fields):
                logger.warning("Missing required fields in AI response")
                return self._create_fallback_intent(original_text)
            
            # Validate confidence range
            confidence = float(data['confidence'])
            if not 0 <= confidence <= 1:
                confidence = 0.5
            
            return DynamicIntent(
                intent_type=IntentType(data['intent_type']),
                confidence=confidence,
                action=data['action'],
                target=data['target'],
                parameters=data['parameters'],
                context={},
                reasoning=data['reasoning']
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._create_fallback_intent(original_text)
        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return self._create_fallback_intent(original_text)
    
    def _create_fallback_intent(self, text: str) -> DynamicIntent:
        """Create fallback intent with basic analysis"""
        # Simple fallback analysis
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['weather', 'temperature', 'forecast']):
            intent_type = IntentType.KNOWLEDGE
            action = "get_weather"
            target = "current location"
        elif any(word in text_lower for word in ['message', 'tell', 'send', 'notify']):
            intent_type = IntentType.MESSAGING
            action = "send_message"
            target = "contact"
        elif any(word in text_lower for word in ['remind', 'alarm', 'timer', 'schedule']):
            intent_type = IntentType.SCHEDULING
            action = "set_reminder"
            target = "task"
        elif any(word in text_lower for word in ['open', 'close', 'start', 'run']):
            intent_type = IntentType.AUTOMATION
            action = "open_app"
            target = "application"
        else:
            intent_type = IntentType.CHAT
            action = "respond"
            target = "user"
        
        return DynamicIntent(
            intent_type=intent_type,
            confidence=0.3,  # Low confidence for fallback
            action=action,
            target=target,
            parameters={"query": text},
            context={},
            reasoning="Fallback analysis based on basic keyword detection"
        )
    
    def _update_advanced_context(self, text: str, intent: DynamicIntent):
        """Update conversation context with new interaction"""
        # Update current topic
        if intent.target and intent.target != "user":
            self.conversation_context["current_topic"] = intent.target
        
        # Track recent intents
        self.conversation_context["recent_intents"].append({
            "intent": intent.intent_type.value,
            "action": intent.action,
            "target": intent.target,
            "timestamp": self._get_timestamp()
        })
        
        # Keep only last 5 intents
        if len(self.conversation_context["recent_intents"]) > 5:
            self.conversation_context["recent_intents"].pop(0)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return {
            "current_topic": self.conversation_context["current_topic"],
            "recent_actions": [f"{item['action']}->{item['target']}" 
                              for item in self.conversation_context["recent_intents"][-3:]],
            "interaction_count": len(self.conversation_context["recent_intents"])
        }

# Add this class to shadow_core/dynamic_nlu.py after the AdvancedInterpreter class

class ContextAwareInterpreter:
    """
    Enhanced interpreter that maintains conversation context and user preferences
    Uses AdvancedInterpreter internally
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.interpreter = AdvancedInterpreter(brain)
        self.conversation_context = {
            "current_topic": None,
            "recent_intents": [],
            "user_preferences": {},
            "active_tasks": []
        }
        
    async def interpret_with_context(self, text: str, user_context: Dict[str, Any] = None) -> DynamicIntent:
        """Interpret with full contextual awareness"""
        
        # Build comprehensive context
        full_context = {
            **self.conversation_context,
            **(user_context or {}),
            "timestamp": self._get_current_time_context()
        }
        
        # Get interpretation
        intent = await self.interpreter.interpret(text, full_context)
        
        # Update conversation context
        self._update_conversation_context(text, intent)
        
        return intent
    
    def _get_current_time_context(self) -> Dict[str, str]:
        """Get time-based context"""
        from datetime import datetime
        now = datetime.now()
        
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        return {
            "time_of_day": time_of_day,
            "day_of_week": now.strftime("%A"),
            "is_weekend": now.weekday() >= 5
        }
    
    def _update_conversation_context(self, text: str, intent: DynamicIntent):
        """Update conversation context based on new interaction"""
        
        # Update current topic
        if intent.intent_type != IntentType.CHAT:
            self.conversation_context["current_topic"] = intent.target
        
        # Track recent intents
        self.conversation_context["recent_intents"].append({
            "intent": intent.intent_type.value,
            "action": intent.action,
            "target": intent.target,
            "timestamp": self._get_timestamp()
        })
        
        # Keep only last 5 intents
        if len(self.conversation_context["recent_intents"]) > 5:
            self.conversation_context["recent_intents"].pop(0)
        
        # Infer user mood from text and intent (basic)
        mood_indicators = {
            "urgent": ["now", "quick", "immediately", "asap", "emergency"],
            "casual": ["maybe", "perhaps", "when you can", "no rush"],
            "frustrated": ["why", "not working", "error", "problem", "fix"],
            "happy": ["thanks", "thank you", "great", "awesome", "perfect"]
        }
        
        text_lower = text.lower()
        for mood, indicators in mood_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                self.conversation_context["user_mood"] = mood
                break
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def set_user_preference(self, key: str, value: Any):
        """Set user preference for context"""
        self.conversation_context["user_preferences"][key] = value
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state"""
        return {
            "topic": self.conversation_context["current_topic"],
            "mood": self.conversation_context.get("user_mood", "neutral"),
            "recent_actions": [f"{item['action']}->{item['target']}" 
                              for item in self.conversation_context["recent_intents"][-3:]],
            "active_tasks": self.conversation_context["active_tasks"]
        }
class SmartNLU:
    """
    Smart NLU that combines AI interpretation with pattern fallbacks
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.interpreter = AdvancedInterpreter(brain)
        self.fallback_patterns = self._initialize_fallback_patterns()
    
    async def interpret(self, text: str, context: Dict[str, Any] = None) -> DynamicIntent:
        """Interpret with AI and fallback patterns"""
        try:
            # Try AI interpretation first
            intent = await self.interpreter.interpret(text, context)
            
            # If low confidence, try pattern matching
            if intent.confidence < 0.4:
                pattern_intent = self._pattern_fallback(text)
                if pattern_intent.confidence > intent.confidence:
                    return pattern_intent
            
            return intent
            
        except Exception as e:
            logger.error(f"Smart interpretation error: {e}")
            return self._pattern_fallback(text)
    
    def _initialize_fallback_patterns(self) -> Dict[str, Any]:
        """Initialize fallback patterns (used only when AI fails)"""
        return {
            "weather_queries": [
                r"(weather|temperature|forecast).*(in|at|for)\s+([\w\s]+)",
                r"how.*weather.*in\s+([\w\s]+)",
                r"what.*temperature.*in\s+([\w\s]+)"
            ],
            "messaging_queries": [
                r"(message|tell|send|notify)\s+(\w+).*",
                r"let\s+(\w+)\s+know.*",
                r"contact\s+(\w+).*"
            ],
            "scheduling_queries": [
                r"(remind|alarm|timer).*at\s+(\d+:\d+)",
                r"set.*(alarm|reminder).*for\s+(\d+:\d+)",
                r"wake.*up.*at\s+(\d+:\d+)"
            ]
        }
    
    def _pattern_fallback(self, text: str) -> DynamicIntent:
        """Pattern-based fallback when AI fails"""
        text_lower = text.lower()
        
        # Weather patterns
        for pattern in self.fallback_patterns["weather_queries"]:
            match = re.search(pattern, text_lower)
            if match:
                location = match.group(3) if match.lastindex >= 3 else "current location"
                return DynamicIntent(
                    intent_type=IntentType.KNOWLEDGE,
                    confidence=0.6,
                    action="get_weather",
                    target=location,
                    parameters={"location": location},
                    context={},
                    reasoning="Pattern matched weather query"
                )
        
        # Messaging patterns
        for pattern in self.fallback_patterns["messaging_queries"]:
            match = re.search(pattern, text_lower)
            if match:
                contact = match.group(2) if match.lastindex >= 2 else "contact"
                return DynamicIntent(
                    intent_type=IntentType.MESSAGING,
                    confidence=0.6,
                    action="send_message",
                    target=contact,
                    parameters={"contact": contact},
                    context={},
                    reasoning="Pattern matched messaging query"
                )
        
        # Default to chat
        return DynamicIntent(
            intent_type=IntentType.CHAT,
            confidence=0.5,
            action="respond",
            target="user",
            parameters={"query": text},
            context={},
            reasoning="Fallback to general chat"
        )
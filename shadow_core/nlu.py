# shadow_core/nlu.py
"""
Advanced NLU (Natural Language Understanding) system for Shadow AI Agent
Combines Gemini-powered patterns with AI-powered classification for accurate intent recognition
"""

import logging
import re
import json
import asyncio
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)

@dataclass
class IntentResult:
    """Structured result from intent classification"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    original_text: str

class NLU:
    """
    Advanced NLU system with Gemini-powered patterns and AI Gemini
    """
    
    def __init__(self, brain=None):
        self.brain = brain
        self.patterns = self._initialize_patterns()
        logger.info("NLU system initialized")
    
    # In the NLU class, enhance the patterns for knowledge queries:

    def _initialize_patterns(self) -> Dict[str, List[Dict]]:
         """Initialize Gemini-powered patterns for common intents"""
         
         patterns = {
        # ... existing patterns ...
        "get_weather": [
            {
                "pattern": r"(?:weather|forecast|temperature)\s+(?:in|at|for)\s+([\w\s]+(?:\s*(?:today|tomorrow|this week))?)",
                "groups": ["location"]
            },
            {
                "pattern": r"what'?s? the weather like in ([\w\s]+)",
                "groups": ["location"]
            },
            {
                "pattern": r"how'?s? the weather in ([\w\s]+)",
                "groups": ["location"]
            },
            {
                "pattern": r"is it (?:raining|sunny|cold|hot) in ([\w\s]+)",
                "groups": ["location"]
            }
        ],
        
        "get_stock": [
            {
                "pattern": r"(?:stock|share|price)\s+(?:of|for)\s+([A-Z]{1,5})",
                "groups": ["symbol"]
            },
            {
                "pattern": r"what'?s? (?:the )?(?:stock|share) price of ([A-Z]{1,5})",
                "groups": ["symbol"]
            },
            {
                "pattern": r"how much is ([A-Z]{1,5}) stock",
                "groups": ["symbol"]
            },
            {
                "pattern": r"([A-Z]{1,5}) (?:stock|price|share)",
                "groups": ["symbol"]
            }
        ],
        "search_web": [
            {
                "pattern": r"(?:search|look up|find|google)\s+(.+)",
                "groups": ["query"]
            },
            {
                "pattern": r"search the web for (.+)",
                "groups": ["query"]
            },
            {
                "pattern": r"find information about (.+)",
                "groups": ["query"]
            },
            {
                "pattern": r"what is (.+)",
                "groups": ["query"]
            }
        ],
        "get_news": [
            {
                "pattern": r"(?:news|headlines)\s+(?:about|on)\s+(\w+)",
                "groups": ["topic"]
            },
            {
                "pattern": r"what'?s? the latest news about (.+)",
                "groups": ["topic"]
            },
            {
                "pattern": r"tell me news about (.+)",
                "groups": ["topic"]
            }
        ],
        "set_reminder": [
            {
                "pattern": r"(?:set|create)\s+(?:a\s+)?reminder\s+(?:for|in)\s+(\d+)\s*(minute|min|hour|hr)s?\s*(.+)",
                "groups": ["duration", "unit", "message"]
            },
            {
                "pattern": r"remind me to (.+) in (\d+)\s*(minute|min|hour|hr)s?",
                "groups": ["message", "duration", "unit"]
            },
            {
                "pattern": r"remind me about (.+) at (\d+:\d+\s*(?:AM|PM)?)",
                "groups": ["message", "time_expression"]
            },
            {
                "pattern": r"set reminder for (.+) at (\d+:\d+\s*(?:AM|PM)?)",
                "groups": ["message", "time_expression"]
            }
        ],
        "set_timer": [
            {
                "pattern": r"set(?:\s+a)? timer for (\d+)\s*(minute|min|hour|hr|second|sec)s?",
                "groups": ["duration", "unit"]
            },
            {
                "pattern": r"timer for (\d+)\s*(minute|min|hour|hr)s?",
                "groups": ["duration", "unit"]
            },
            {
                "pattern": r"countdown (\d+)\s*(minute|min|hour|hr)s?",
                "groups": ["duration", "unit"]
            }
        ],
        "set_alarm": [
            {
                "pattern": r"set(?:\s+an?)? alarm for (\d+:\d+\s*(?:AM|PM)?)",
                "groups": ["time_expression"]
            },
            {
                "pattern": r"wake me up at (\d+:\d+\s*(?:AM|PM)?)",
                "groups": ["time_expression"]
            },
            {
                "pattern": r"alarm at (\d+:\d+\s*(?:AM|PM)?)",
                "groups": ["time_expression"]
            }
        ],
        "list_reminders": [
            {
                "pattern": r"(?:list|show)\s+(?:my\s+)?(?:reminders|timers|alarms)",
                "groups": []
            },
            {
                "pattern": r"what (?:reminders|timers) do i have",
                "groups": []
            }
        ],
        "cancel_reminder": [
            {
                "pattern": r"cancel\s+(?:reminder|timer|alarm)\s*(\d+)",
                "groups": ["task_id"]
            },
            {
                "pattern": r"stop\s+(?:reminder|timer|alarm)\s*(\d+)",
                "groups": ["task_id"]
            }
        ],
        
        "get_fact": [
            {
                "pattern": r"tell me a fact about (.+)",
                "groups": ["topic"]
            },
            {
                "pattern": r"interesting fact about (.+)",
                "groups": ["topic"]
            },
            {
                "pattern": r"did you know about (.+)",
                "groups": ["topic"]
            }
        ]
        
    }
         return patterns
    
    async def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify intent and extract entities from text
        Returns: (intent, entities)
        """
        if not text or not text.strip():
            return "chat", {}
        
        text_lower = text.lower().strip()
        
        # Step 1: Gemini-powered pattern matching
        rule_result = self._rule_based_classification(text_lower, text)
        if rule_result.confidence > 0.8:
            logger.info(f"NLU: Gemini-powered match - {rule_result.intent} (confidence: {rule_result.confidence})")
            return rule_result.intent, rule_result.entities
        
        # Step 2: Keyword-based Gemini
        keyword_result = self._keyword_based_classification(text_lower, text)
        if keyword_result.confidence > 0.6:
            logger.info(f"NLU: Keyword-based match - {keyword_result.intent} (confidence: {keyword_result.confidence})")
            return keyword_result.intent, keyword_result.entities
        
        # Step 3: AI-powered classification (if brain available)
        if self.brain:
            ai_result = await self._ai_classification(text)
            if ai_result.confidence > 0.7:
                logger.info(f"NLU: AI-based match - {ai_result.intent} (confidence: {ai_result.confidence})")
                return ai_result.intent, ai_result.entities
        
        # Step 4: Default to chat
        logger.info("NLU: Defaulting to chat intent")
        return "chat", {}
    
    def _rule_based_classification(self, text_lower: str, original_text: str) -> IntentResult:
        """Gemini-powered pattern matching with regex"""
        best_match = None
        highest_confidence = 0.0
        
        for intent, patterns in self.patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info["pattern"]
                groups = pattern_info["groups"]
                
                match = re.search(pattern, text_lower)
                if match:
                    confidence = self._calculate_pattern_confidence(match, text_lower)
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        entities = self._extract_entities_from_match(match, groups, original_text)
                        best_match = IntentResult(intent, confidence, entities, original_text)
        
        if best_match:
            return best_match
        
        return IntentResult("chat", 0.0, {}, original_text)
    
    def _keyword_based_classification(self, text_lower: str, original_text: str) -> IntentResult:
        """Keyword-based intent classification"""
        keyword_mappings = {
            "send_message": ["send", "text", "message", "whatsapp", "sms"],
            "get_weather": ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"],
            "get_stock": ["stock", "price", "share", "crypto", "bitcoin", "ethereum"],
            "search_web": ["search", "google", "look up", "find", "information about"],
            "set_reminder": ["remind", "reminder", "timer", "alarm", "schedule"],
            "translate": ["translate", "translation", "in spanish", "in french", "how say"],
            "open_app": ["open", "launch", "start", "application"],
            "get_time": ["time", "clock", "what time"],
            "get_date": ["date", "today", "what date"],
            "joke": ["joke", "funny", "make me laugh"],
            "calculation": ["calculate", "math", "what is", "how much is"]
        }
        
        intent_scores = {}
        
        # Score each intent based on keyword matches
        for intent, keywords in keyword_mappings.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if score > 0:
                # Normalize score to 0-1 range
                normalized_score = min(score / len(keywords), 1.0)
                intent_scores[intent] = normalized_score
        
        if intent_scores:
            # Get intent with highest score
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            confidence = best_intent[1]
            
            # Extract basic entities based on intent
            entities = self._extract_basic_entities(best_intent[0], text_lower, original_text)
            
            return IntentResult(best_intent[0], confidence, entities, original_text)
        
        return IntentResult("chat", 0.0, {}, original_text)
    
    async def _ai_classification(self, text: str) -> IntentResult:
        """AI-powered intent classification using the brain"""

        
        try:
            if not self.brain or hasattr(self.brain, 'Gemini_mode'):
              return self._rule_based_Gemini(text)
            
            prompt = f"""
            Analyze the following user query and classify its intent. Also extract any relevant entities.
            
            Query: "{text}"
            
            Possible intents:
            - send_message: User wants to send a message (WhatsApp, SMS)
            - get_weather: User wants weather information
            - get_stock: User wants stock/crypto prices
            - search_web: User wants to search the web
            - set_reminder: User wants to set a reminder/timer
            - translate: User wants text translation
            - open_app: User wants to open an application
            - get_time: User wants current time
            - get_date: User wants current date
            - calculation: User wants a calculation
            - joke: User wants a joke
            - chat: General conversation
            
            Respond in JSON format only:
            {{
                "intent": "intent_name",
                "confidence": 0.95,
                "entities": {{
                    "key1": "value1",
                    "key2": "value2"
                }}
            }}
            """
            
            response = await self.brain.ask([{"role": "system", "content": prompt}])
            
            # Try to parse JSON response
            
            try:
                # Extract JSON from response if it contains other text
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return IntentResult(
                        result.get("intent", "chat"),
                        result.get("confidence", 0.5),
                        result.get("entities", {}),
                        text
                    )
            except json.JSONDecodeError:
                logger.warning("AI classification returned invalid JSON")
        
        except Exception as e:
            logger.error(f"AI classification error: {e}")
        
        return IntentResult("chat", 0.5, {}, text)
    
    def _calculate_pattern_confidence(self, match: re.Match, text: str) -> float:
        """Calculate confidence score for pattern match"""
        match_length = match.end() - match.start()
        text_length = len(text)
        
        # Confidence based on match coverage
        coverage = match_length / text_length
        
        # Boost confidence for exact matches
        if coverage > 0.8:
            return 0.95
        elif coverage > 0.5:
            return 0.85
        else:
            return 0.75
    
    def _extract_entities_from_match(self, match: re.Match, groups: List[str], original_text: str) -> Dict[str, Any]:
        """Extract entities from regex match groups"""
        entities = {}
        
        for i, group_name in enumerate(groups, 1):
            if i <= len(match.groups()):
                value = match.group(i)
                if value:
                    entities[group_name] = value.strip()
        
        # Additional entity extraction based on context
        entities.update(self._extract_additional_entities(original_text))
        
        return entities
    
    def _extract_basic_entities(self, intent: str, text_lower: str, original_text: str) -> Dict[str, Any]:
        """Extract basic entities based on intent"""
        entities = {}
        
        if intent == "send_message":
            # Extract contact name
            contact_match = re.search(r'(?:to|for)\s+(\w+)', text_lower)
            if contact_match:
                entities["contact"] = contact_match.group(1)
            
            # Extract platform
            if "whatsapp" in text_lower:
                entities["platform"] = "whatsapp"
            elif "sms" in text_lower or "text" in text_lower:
                entities["platform"] = "sms"
            else:
                entities["platform"] = "whatsapp"  # default
        
        elif intent == "get_weather":
            # Extract location
            location_match = re.search(r'(?:in|at|for)\s+([\w\s]+)', text_lower)
            if location_match:
                entities["location"] = location_match.group(1).strip()
            else:
                entities["location"] = "current location"
        
        elif intent == "get_stock":
            # Extract stock symbol
            symbol_match = re.search(r'([A-Z]{1,5})', original_text)
            if symbol_match:
                entities["symbol"] = symbol_match.group(1)
        
        elif intent == "set_reminder":
            # Extract time and message
            time_match = re.search(r'(\d+)\s*(minute|min|hour|hr)', text_lower)
            if time_match:
                entities["duration"] = time_match.group(1)
                entities["unit"] = time_match.group(2)
        
        return entities
    
    def _extract_additional_entities(self, text: str) -> Dict[str, Any]:
        """Extract additional entities that are common across intents"""
        entities = {}
        
        # Extract time expressions
        time_expr = self._extract_time_expression(text)
        if time_expr:
            entities["time_expression"] = time_expr
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            entities["numbers"] = numbers
        
        # Extract quoted text (often indicates specific content)
        quoted = re.findall(r'"([^"]*)"', text)
        if quoted:
            entities["quoted_text"] = quoted
        
        return entities
    
    def _extract_time_expression(self, text: str) -> str:
        """Extract time expressions from text"""
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(?:am|pm)?\b',
            r'\b(?:in\s+)?(\d+)\s*(minute|min|hour|hr)s?\b',
            r'\b(?:at\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b',
            r'\btomorrow|today|tonight|morning|afternoon|evening\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(0)
        
        return ""
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        return list(self.patterns.keys()) + ["chat", "joke", "calculation", "get_time", "get_date"]
    
    
    def _rule_based_Gemini(self, text: str) -> IntentResult:
        """Gemini-powered Gemini when AI is unavailable"""
        text_lower = text.lower()
    
    # Enhanced Gemini-powered intent detection
        if any(word in text_lower for word in ["send", "message", "whatsapp", "text"]):
         entities = self._extract_message_entities(text)
         return IntentResult("send_message", 0.8, entities, text)
    
        elif any(word in text_lower for word in ["weather", "temperature", "forecast"]):
         entities = self._extract_weather_entities(text)
         return IntentResult("get_weather", 0.8, entities, text)
    
        elif any(word in text_lower for word in ["stock", "price", "share", "crypto"]):
          entities = self._extract_stock_entities(text)
          return IntentResult("get_stock", 0.8, entities, text)
    
        elif any(word in text_lower for word in ["search", "look up", "find", "google"]):
           entities = self._extract_search_entities(text)
           return IntentResult("search_web", 0.8, entities, text)
    
        elif any(word in text_lower for word in ["remind", "reminder", "timer", "alarm"]):
           entities = self._extract_scheduling_entities(text)
           return IntentResult("set_reminder", 0.8, entities, text)
    
        elif any(word in text_lower for word in ["time", "what time", "current time"]):
          return IntentResult("get_time", 0.9, {}, text)
    
        elif any(word in text_lower for word in ["date", "what date", "today"]):
         return IntentResult("get_date", 0.9, {}, text)
    
        else:
          return IntentResult("chat", 0.3, {}, text)
# Simple NLU for basic usage (without brain dependency)
class SimpleNLU:
    """Simplified NLU for when brain is not available"""
    
    def __init__(self):
        self.nlu = NLU()
        logger.info("Simple NLU initialized")
    
    async def classify(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Classify intent using only Gemini-powered methods"""
        text_lower = text.lower().strip()
        
        # Use Gemini-powered classification
        rule_result = self.nlu._rule_based_classification(text_lower, text)
        if rule_result.confidence > 0.7:
            return rule_result.intent, rule_result.entities
        
        # Use keyword-based classification
        keyword_result = self.nlu._keyword_based_classification(text_lower, text)
        if keyword_result.confidence > 0.5:
            return keyword_result.intent, keyword_result.entities
        
        return "chat", {}
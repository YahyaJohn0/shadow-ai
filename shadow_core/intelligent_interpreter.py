# shadow_core/intelligent_interpreter.py
"""
Intelligent interpreter that dynamically understands user intent through context and conversation
"""

import logging
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    SCHEDULING = "scheduling"
    MESSAGING = "messaging" 
    INFORMATION = "information"
    AUTOMATION = "automation"
    UNKNOWN = "unknown"

@dataclass
class InterpretedIntent:
    intent_type: IntentType
    confidence: float
    extracted_content: Dict[str, Any]
    needs_clarification: bool
    clarification_question: str = ""
    action_plan: str = ""

class IntelligentInterpreter:
    """
    Dynamically interprets user intent through conversation context and intelligent parsing
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.conversation_context = []
        self.user_preferences = {}
        logger.info("Intelligent Interpreter initialized")
    
    async def interpret(self, text: str, context: List[Dict] = None) -> InterpretedIntent:
        """
        Intelligently interpret user intent without predefined patterns
        """
        if context:
            self.conversation_context = context[-5:]  # Keep last 5 exchanges
        
        # Analyze the text for natural language patterns
        analysis = await self._analyze_text(text)
        
        # Determine intent based on analysis
        intent = await self._determine_intent(analysis, text)
        
        return intent
    
    async def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text for natural language patterns and context"""
        analysis = {
            "has_action_verb": False,
            "has_time_reference": False,
            "has_target": False,
            "has_content": False,
            "question_type": None,
            "urgency_level": "low",
            "extracted_entities": {}
        }
        
        text_lower = text.lower()
        
        # Check for action verbs (dynamically)
        action_verbs = ["set", "create", "make", "schedule", "plan", "organize", 
                       "arrange", "setup", "configure", "prepare", "remind"]
        analysis["has_action_verb"] = any(verb in text_lower for verb in action_verbs)
        
        # Check for time references
        time_patterns = [
            r'\b(today|tomorrow|tonight|this week|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(at\s+\d+:\d+|\d+\s*(?:am|pm)|in\s+\d+\s*(?:minute|hour|day)s?)\b',
            r'\b(now|soon|later|asap|immediately)\b'
        ]
        analysis["has_time_reference"] = any(re.search(pattern, text_lower) for pattern in time_patterns)
        
        # Check for targets (what the user wants to set)
        analysis["has_target"] = self._extract_target(text)
        analysis["extracted_entities"]["target"] = analysis["has_target"]
        
        # Check for content (the actual thing to be set)
        analysis["has_content"] = self._extract_content(text)
        analysis["extracted_entities"]["content"] = analysis["has_content"]
        
        # Determine question type
        analysis["question_type"] = self._determine_question_type(text)
        
        # Determine urgency
        analysis["urgency_level"] = self._determine_urgency(text)
        
        return analysis
    
    def _extract_target(self, text: str) -> Optional[str]:
        """Dynamically extract what the user wants to set/organize"""
        text_lower = text.lower()
        
        # Look for possessive patterns ("my X", "our Y")
        possessive_match = re.search(r'(?:my|our|the)\s+(\w+(?:\s+\w+)*)', text_lower)
        if possessive_match:
            target = possessive_match.group(1).strip()
            
            # Common targets people want to set/organize
            common_targets = {
                "schedule": "schedule",
                "calendar": "calendar", 
                "day": "daily schedule",
                "today": "today's schedule",
                "week": "weekly schedule",
                "reminder": "reminder",
                "alarm": "alarm",
                "meeting": "meeting",
                "appointment": "appointment",
                "task": "task",
                "plan": "plan",
                "routine": "routine",
                "agenda": "agenda"
            }
            
            # Return the most relevant target
            for key, value in common_targets.items():
                if key in target:
                    return value
            
            return target  # Return the raw target if no common match
        
        return None
    
    def _extract_content(self, text: str) -> Optional[str]:
        """Extract the actual content the user wants to set"""
        # Remove common setup phrases to get to the actual content
        phrases_to_remove = [
            r'how can i set my',
            r'how do i set my', 
            r'can you help me set',
            r'i want to set my',
            r'i need to set my',
            r'set my',
            r'create my',
            r'make my'
        ]
        
        content = text.lower()
        for phrase in phrases_to_remove:
            content = re.sub(phrase, '', content)
        
        content = content.strip()
        
        # If we have meaningful content left, return it
        if content and len(content) > 3 and content not in ['my', 'the', 'a']:
            return content
        
        return None
    
    def _determine_question_type(self, text: str) -> str:
        """Determine what type of question this is"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['how', 'can you', 'could you']):
            return "how_to"
        elif any(word in text_lower for word in ['what', 'which']):
            return "what_is" 
        elif any(word in text_lower for word in ['when', 'what time']):
            return "when"
        elif any(word in text_lower for word in ['help', 'assist']):
            return "help_request"
        else:
            return "action_request"
    
    def _determine_urgency(self, text: str) -> str:
        """Determine urgency level from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['now', 'immediately', 'asap', 'urgent', 'emergency']):
            return "high"
        elif any(word in text_lower for word in ['soon', 'today', 'quick', 'fast']):
            return "medium"
        else:
            return "low"
    
    async def _determine_intent(self, analysis: Dict[str, Any], original_text: str) -> InterpretedIntent:
        """Dynamically determine intent based on analysis"""
        
        # If user is asking "how to set" something
        if (analysis["question_type"] == "how_to" and 
            analysis["has_action_verb"] and 
            analysis["has_target"]):
            
            target = analysis["extracted_entities"]["target"]
            content = analysis["extracted_entities"]["content"]
            
            return InterpretedIntent(
                intent_type=IntentType.SCHEDULING,
                confidence=0.85,
                extracted_content={
                    "target": target,
                    "content": content,
                    "question_type": "how_to"
                },
                needs_clarification=not content,  # Need clarification if no specific content
                clarification_question=self._generate_clarification_question(target, content),
                action_plan=f"Explain how to set up {target} and offer to create it"
            )
        
        # If user wants to actually create/set something
        elif (analysis["has_action_verb"] and 
              analysis["has_target"] and
              analysis["question_type"] == "action_request"):
            
            target = analysis["extracted_entities"]["target"]
            content = analysis["extracted_entities"]["content"]
            
            return InterpretedIntent(
                intent_type=IntentType.SCHEDULING,
                confidence=0.90,
                extracted_content={
                    "target": target,
                    "content": content,
                    "urgency": analysis["urgency_level"]
                },
                needs_clarification=not content,
                clarification_question=self._generate_clarification_question(target, content),
                action_plan=f"Help user set up {target} with provided content"
            )
        
        # Default to information intent
        else:
            return InterpretedIntent(
                intent_type=IntentType.INFORMATION,
                confidence=0.6,
                extracted_content={"original_text": original_text},
                needs_clarification=False,
                action_plan="Provide general help and information"
            )
    
    def _generate_clarification_question(self, target: str, content: Optional[str]) -> str:
        """Generate intelligent clarification questions"""
        if not content:
            if target:
                return f"What specific {target} would you like me to help you set up? For example, 'meetings for today' or 'reminders for this week'?"
            else:
                return "What would you like me to help you set up? For example, your schedule, reminders, tasks, or something else?"
        
        # If we have some content but it might need more details
        if content and len(content.split()) < 3:  # Very brief content
            return f"Could you tell me more about the {content} you'd like to set up? What details should I include?"
        
        return ""  # No clarification needed
    
    def update_context(self, user_input: str, assistant_response: str):
        """Update conversation context for better understanding"""
        context_entry = {
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.conversation_context.append(context_entry)
        
        # Keep only last 5 exchanges
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)
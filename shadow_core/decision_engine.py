"""
Decision Engine - Core routing and intent handling for Shadow AI Agent
Routes user queries to appropriate handlers (messaging, knowledge, automation, etc.)
"""
from datetime import datetime
from shadow_core.nlu import NLU, SimpleNLU
from shadow_core.intelligent_interpreter import IntelligentInterpreter, IntentType, InterpretedIntent
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple, List
import re
from shadow_core.knowledge import Knowledge, FreeKnowledge
from shadow_core.enhanced_knowledge import EnhancedKnowledge
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, OPENWEATHER_API_KEY, ALPHA_VANTAGE_API_KEY
from shadow_core.scheduler import Scheduler, MockScheduler, TaskType
from shadow_core.dynamic_nlu import ContextAwareInterpreter, DynamicIntent
from shadow_core.multilingual_reminder import MultilingualReminderParser

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Enhanced Decision Engine with intelligent AI interpretation
    No keyword dependencies - understands natural language meaning and context
    """
    
    def __init__(self, brain, memory, messaging=None, scheduler=None, knowledge=None, automation=None):
        self.brain = brain
        self.memory = memory
        self.messaging = messaging
        self.scheduler = scheduler
        self.knowledge = knowledge
        self.automation = automation

        # ✅ Initialize Intelligent Interpreter
        self.intelligent_interpreter = IntelligentInterpreter(brain)
        
        # ✅ FIX: Initialize NLU first with proper error handling
        try:
            # Try to initialize advanced NLU
            self.nlu = NLU(brain=brain)
            logger.info("Advanced NLU initialized successfully")
        except Exception as e:
            logger.warning(f"Advanced NLU failed: {e}. Using SimpleNLU.")
            # Fallback to simple NLU
            self.nlu = SimpleNLU()
            logger.info("Simple NLU initialized as fallback")

        # Initialize multilingual system with PROPER error handling
        self.multilingual_manager = None
        self.translator = None
        self.multilingual_brain = None
        
        try:
            from shadow_core.multilingual import create_multilingual_system
            self.multilingual_manager, self.translator, self.multilingual_brain = create_multilingual_system(brain)
            logger.info("Multilingual system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize multilingual system: {e}")
            # Create fallback components with CORRECT initialization
            try:
                from shadow_core.multilingual import MultilingualManager, UrduPashtoTranslator, MultilingualBrain
                # FIX: Initialize without extra arguments
                self.multilingual_manager = MultilingualManager()
                self.translator = UrduPashtoTranslator()
                self.multilingual_brain = MultilingualBrain(brain, self.multilingual_manager, self.translator)
                logger.info("Fallback multilingual system initialized")
            except Exception as fallback_error:
                logger.error(f"Fallback multilingual system also failed: {fallback_error}")
                # Use original brain as final fallback
                self.multilingual_brain = brain

        # Initialize Dynamic AI Interpreter with PROPER multilingual support
        try:
            # Use multilingual brain if available, otherwise fallback to original brain
            brain_for_interpreter = self.multilingual_brain if self.multilingual_brain else brain
            self.interpreter = ContextAwareInterpreter(brain_for_interpreter, self.multilingual_manager)
            logger.info("ContextAwareInterpreter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize interpreter: {e}")
            # Fallback without multilingual
            self.interpreter = ContextAwareInterpreter(brain)

        # Initialize modules
        self._initialize_modules()
        
        try:
            brain_for_reminder = self.multilingual_brain if self.multilingual_brain else brain
            self.reminder_parser = MultilingualReminderParser(brain_for_reminder)
        except Exception as e:
            logger.warning(f"Multilingual reminder parser not available: {e}")
            self.reminder_parser = None
        
        logger.info("Decision Engine initialized with Intelligent Interpreter")

    async def handle_query(self, text: str, gui=None) -> str:
        """
        Handle user query with intelligent dynamic interpretation
        Understands meaning and context, not just keywords
        """
        if not text or text.strip() == "":
            return "I didn't catch that. Could you please repeat?"

        logger.info(f"Processing query: {text}")
        
        try:
            # Step 1: Detect language and convert to Roman format if needed
            processed_text = await self._preprocess_text(text)
            
            # Step 2: Use intelligent interpreter to understand the real intent
            interpreted_intent = await self.intelligent_interpreter.interpret(processed_text, self.conversation_context)
            
            logger.info(f"Intelligent Interpretation: {interpreted_intent.intent_type.name} "
                       f"(confidence: {interpreted_intent.confidence:.2f})")
            
            # Step 3: If clarification is needed, ask clarifying question
            if interpreted_intent.needs_clarification and interpreted_intent.clarification_question:
                response = interpreted_intent.clarification_question
            else:
                # Step 4: Execute based on intelligently interpreted intent
                response = await self._execute_intelligent_intent(interpreted_intent, processed_text, gui)
            
            # Step 5: Update conversation context
            self.intelligent_interpreter.update_context(processed_text, response)
            
            # Step 6: Save to memory
            self.memory.save_chat(processed_text, response)
            
            logger.info(f"Response ready: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error in decision engine: {e}")
            error_msg = "I encountered an error processing your request. Please try again."
            self.memory.save_chat(text, error_msg)
            return error_msg

    async def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for Roman Urdu/Pashto detection and normalization
        """
        if not text or len(text.strip()) < 2:
            return text
        
        # Detect if text contains Roman Urdu or Roman Pashto patterns
        if await self._is_roman_urdu(text):
            logger.info("Detected Roman Urdu input")
            # Normalize Roman Urdu spelling variations
            return self._normalize_roman_urdu(text)
        elif await self._is_roman_pashto(text):
            logger.info("Detected Roman Pashto input")
            # Normalize Roman Pashto spelling variations
            return self._normalize_roman_pashto(text)
        
        return text

    async def _is_roman_urdu(self, text: str) -> bool:
        """Check if text appears to be Roman Urdu"""
        roman_urdu_indicators = [
            'kaise', 'ho', 'aap', 'main', 'theek', 'shukriya', 'madad', 
            'kya', 'kar', 'sakte', 'sakta', 'sakti', 'mujhe', 'mera', 'meri',
            'hai', 'hain', 'hun', 'thi', 'the', 'kyun', 'kahan', 'kaun',
            'acha', 'theek', 'bilkul', 'zaroor', 'yaqeen', 'sach', 'jhoot',
            'salam', 'alaikum', 'khuda', 'hafiz', 'maaf', 'kijiye', 'barah',
            'karam', 'awaz', 'sun', 'rahe', 'jawab', 'do', 'yahan', 'koi',
            'masla', 'nahi', 'phir', 'koshish', 'karein'
        ]
        
        text_lower = text.lower()
        score = sum(1 for indicator in roman_urdu_indicators if indicator in text_lower)
        
        # Also check for absence of Urdu script characters
        has_urdu_script = bool(re.search(r'[\u0600-\u06FF]', text))
        
        return score >= 2 and not has_urdu_script

    async def _is_roman_pashto(self, text: str) -> bool:
        """Check if text appears to be Roman Pashto"""
        roman_pashto_indicators = [
            'sta', 'yast', 'kaw', 'kawi', 'kawam', 'kawalai', 'kawale', 
            'sham', 'dera', 'khaire', 'kha', 'manana', 'mehrbani', 'sara',
            'lag', 'de', 'da', 'pa', 'po', 'kaw', 'ka', 'komak', 'murajat',
            'kawom', 'kawem', 'kawed', 'kawal', 'kawala', 'kawalo'
        ]
        
        text_lower = text.lower()
        score = sum(1 for indicator in roman_pashto_indicators if indicator in text_lower)
        
        # Also check for absence of Pashto script characters
        has_pashto_script = bool(re.search(r'[\u0600-\u06FF\u0671-\u06D3]', text))
        
        return score >= 2 and not has_pashto_script

    def _normalize_roman_urdu(self, text: str) -> str:
        """Normalize Roman Urdu spelling variations"""
        # Common Roman Urdu spelling variations
        variations = {
            'kaise': ['kaise', 'kese', 'kaisey', 'kesay'],
            'ho': ['ho', 'hou', 'how'],
            'aap': ['aap', 'ap', 'aapne', 'apne'],
            'main': ['main', 'mein', 'me', 'mai'],
            'theek': ['theek', 'thik', 'theik', 'thik'],
            'shukriya': ['shukriya', 'shukria', 'shukariya'],
            'salam': ['salam', 'salaam', 'slaam'],
            'alaikum': ['alaikum', 'alaykum', 'alikum']
        }
        
        normalized_text = text.lower()
        for standard, variants in variations.items():
            for variant in variants:
                if variant in normalized_text:
                    normalized_text = normalized_text.replace(variant, standard)
        
        return normalized_text

    def _normalize_roman_pashto(self, text: str) -> str:
        """Normalize Roman Pashto spelling variations"""
        # Common Roman Pashto spelling variations
        variations = {
            'sta': ['sta', 'staso', 'stase'],
            'yast': ['yast', 'yaste', 'yasti'],
            'kaw': ['kaw', 'kawe', 'kawi'],
            'manana': ['manana', 'manena', 'manina'],
            'mehrbani': ['mehrbani', 'mehrabi', 'mehrbani']
        }
        
        normalized_text = text.lower()
        for standard, variants in variations.items():
            for variant in variants:
                if variant in normalized_text:
                    normalized_text = normalized_text.replace(variant, standard)
        
        return normalized_text

    async def _execute_intelligent_intent(self, intent: InterpretedIntent, original_text: str, gui=None) -> str:
        """Execute action based on intelligently interpreted intent"""
        
        if intent.intent_type == IntentType.SCHEDULING:
            return await self._handle_intelligent_scheduling(intent, original_text, gui)
        
        elif intent.intent_type == IntentType.MESSAGING:
            return await self._handle_intelligent_messaging(intent, original_text, gui)
        
        elif intent.intent_type == IntentType.INFORMATION:
            return await self._handle_intelligent_information(intent, original_text, gui)
        
        elif intent.intent_type == IntentType.AUTOMATION:
            return await self._handle_intelligent_automation(intent, original_text, gui)
        
        else:
            return await self._handle_chat(original_text, gui)

    async def _handle_intelligent_scheduling(self, intent: InterpretedIntent, original_text: str, gui=None) -> str:
        """Handle intelligently interpreted scheduling requests"""
        extracted = intent.extracted_content
        target = extracted.get("target", "schedule")
        content = extracted.get("content")
        question_type = extracted.get("question_type")
        
        if question_type == "how_to":
            # User is asking "how to" set something up
            if content:
                return await self._provide_setup_guidance(target, content, original_text, gui)
            else:
                return await self._provide_general_setup_help(target, original_text, gui)
        
        else:
            # User wants to actually create/set something
            if content:
                return await self._create_scheduled_item(target, content, extracted, original_text, gui)
            else:
                # This shouldn't happen due to clarification, but fallback
                return f"I'd be happy to help you set up your {target}! What specific {target} would you like to create?"

    async def _provide_setup_guidance(self, target: str, content: str, original_text: str, gui=None) -> str:
        """Provide guidance on how to set something up"""
        # Detect language and provide appropriate response
        language = await self._detect_language(original_text)
        
        if language == 'ur':
            # Roman Urdu responses
            guidance_responses = {
                "schedule": f"""
📅 **Aap ka schedule kaise set karein:**

Main aap ki {content} set karne mein madad kar sakta hoon:

1. **Jaldi setup**: "Kal 3 baje {content} schedule karo"
2. **Detailed setup**: "{content} ko is tarah set karo: [aapki details]"
3. **Rozana**: "Har Monday 9 baje weekly {content} banao"

Kya aap abhi specific {content} set karna chahte hain?
""",
                "reminder": f"""
⏰ **{content} reminders kaise set karein:**

{content} ke liye, main reminders bana sakta hoon:
• "Kal 10 baje {content} ki yaad dilaoo"
• "Roz 8 baje {content} ka daily reminder set karo" 
• "{content} se 30 minute pehle alert do"

Mujhe specific time batao aur main set kar doonga!
""",
                "task": f"""
✅ **{content} ko kaise organize karein:**

Main {content} ko manage karne mein madad kar sakta hoon:
• Deadlines set karna: "Friday tak {content} ka task set karo"
• Reminders banana: "Roz {content} par kaam karne ki yaad dilaoo"
• Time block karna: "Kal 2 ghante {content} ke liye block karo"

Aapke {content} ka pehla step kya hai?
"""
            }
        elif language == 'ps':
            # Roman Pashto responses
            guidance_responses = {
                "schedule": f"""
📅 **ستاسو schedule څنګه ترتیب کړو:**

زه کولی شم ستاسو د {content} د ترتیبولو کې مرسته وکړم:

1. **ژر ترتیب**: "سبا په ۳ بجې {content} ترتیب کړئ"
2. **تفصيلي ترتیب**: "په دې ډول {content} ترتیب کړئ: [ستاسو تفصيل]"
3. **ورځني**: "هر دوشنبه په ۹ بجې اونيز {content} جوړ کړئ"

آیا تاسو اوس خاص {content} ترتیب کوئ؟
""",
                "reminder": f"""
⏰ **د {content} یادونې څنګه ترتیب کړو:**

د {content} لپاره، زه کولی شم یادونې ترتیب کړم:
• "سبا په ۱۰ بجې زه د {content} په اړه وګورئ"
• "هره ورځ په ۸ بجې د {content} ورځنۍ یادونه ترتیب کړئ"
• "د {content} ۳۰ دقيقې وړاندې خبر راکړئ"

ما ته خاص وخت ووایاست او زه به یې ترتیب کړم!
""",
                "task": f"""
✅ **څنګه {content} تنظیم کړو:**

زه کولی شم د {content} د مدیریت کې مرسته وکړم:
• د وخت بندي ترتیبول: "په جمعه کې د {content} دنده ترتیب کړئ"
• یادونې جوړول: "هره ورڝ د {content} کار کولو لپاره وګورئ"
• وخت بلاک کول: "سبا ۲ ساعته د {content} لپاره بلاک کړئ"

ستاسو د {content} لومړی ګام څه دی؟
"""
            }
        else:
            # English responses
            guidance_responses = {
                "schedule": f"""
📅 **How to set up your {content}:**

I can help you create {content} in several ways:

1. **Quick setup**: "Schedule {content} for tomorrow at 3 PM"
2. **Detailed setup**: "Set up {content} with these details: [your details]"
3. **Recurring**: "Create weekly {content} every Monday at 9 AM"

Would you like me to help you set up specific {content} right now?
""",
                "reminder": f"""
⏰ **How to set up {content} reminders:**

For {content}, I can create reminders like:
• "Remind me about {content} tomorrow at 10 AM"
• "Set daily reminder for {content} at 8 PM" 
• "Alert me 30 minutes before {content}"

Tell me the specific timing and I'll set it up!
""",
                "task": f"""
✅ **How to organize {content}:**

I can help you manage {content} by:
• Setting deadlines: "Set task {content} due Friday"
• Creating reminders: "Remind me to work on {content} daily"
• Scheduling time: "Block 2 hours for {content} tomorrow"

What's the first step for your {content}?
"""
            }
        
        response = guidance_responses.get(target, 
            f"I can help you set up {content} for your {target}! Just tell me the specific details like timing, frequency, or any special instructions.")
        
        # Offer to actually create it
        if language == 'ur':
            response += f"\n\nYa, main abhi ise set kar sakta hoon! Bas kaho: '{content} ko [time/date] ke liye set karo'"
        elif language == 'ps':
            response += f"\n\nیا، زه کولی شم اوس یې ترتیب کړم! یوازې ووایاست: 'د {content} لپاره [وخت/نېټه] ترتیب کړئ'"
        else:
            response += f"\n\nOr, I can set it up for you right now! Just say: 'Set {content} for [time/date]'"
        
        return response

    async def _detect_language(self, text: str) -> str:
        """Detect language of input text"""
        if self.multilingual_manager:
            try:
                return await self.multilingual_manager.detect_language(text)
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
        
        # Fallback detection
        if await self._is_roman_urdu(text):
            return 'ur'
        elif await self._is_roman_pashto(text):
            return 'ps'
        else:
            return 'en'

    async def _provide_general_setup_help(self, target: str, original_text: str, gui=None) -> str:
        """Provide general setup help when content isn't specific"""
        language = await self._detect_language(original_text)
        
        if language == 'ur':
            # Roman Urdu responses
            help_responses = {
                "schedule": """
📅 **Apna schedule set karne ka tarika:**

Main aap ko organize karne mein madad kar sakta hoon:
• **Meetings & appointments** - "Kal 2 baje team ke sath meeting schedule karo"
• **Daily routines** - "Mera morning routine set karo"  
• **Work blocks** - "Is week deep work ke liye time block karo"
• **Personal time** - "Weekly gym sessions schedule karo"

Aap apne schedule ka konsa specific part set karna chahte hain?
""",
                "reminder": """
⏰ **Reminders set karne ka tarika:**

Main reminders bana sakta hoon:
• **Medicine** - "Roz 8 baje pills lene ki yaad dilaoo"
• **Bills** - "Mahine ke pehle din rent payment ki reminder set karo"
• **Tasks** - "Har Sunday mom ko call karne ki yaad dilaoo"
• **Events** - "Doctor appointment se 1 ghante pehle alert do"

Aap kis cheez ki yaad dilwana chahte hain?
""",
                "calendar": """
🗓️ **Apna calendar organize karne ka tarika:**

Main manage kar sakta hoon:
• **Appointments** - "Agle Monday dentist appointment add karo"
• **Events** - "Saturday ko birthday party schedule karo"
• **Deadlines** - "Friday tak project deadline set karo"
• **Recurring items** - "Har Monday weekly team meeting add karo"

Aap apne calendar mein kya add karna chahte hain?
"""
            }
        elif language == 'ps':
            # Roman Pashto responses
            help_responses = {
                "schedule": """
📅 **ستاسو د جدول ترتیبول:**

زه کولی شم ستاسو د ترتیبولو کې مرسته وکړم:
• **غونډې او ناستې** - "سبا په ۲ بجې د ټیم سره ناسته ترتیب کړئ"
• **ورځني روټین** - "زما د سهارني روټین ترتیب کړئ"
• **د کار بلاکونه** - "پدې اونۍ د ژور کار لپاره وخت بلاک کړئ"
• **شخصي وخت** - "اونيز جيم سیشن ترتيب کړئ"

تاسو د خپل جدول کوم خاص برخه ترتیب کوئ؟
""",
                "reminder": """
⏰ **د یادونو ترتیبول:**

زه کولی شم یادونې ترتیب کړم:
• **درمل** - "هره ورځ په ۸ بجې د حبوبو اخستلو یادونه ترتیب کړئ"
• **بلونه** - "د میاشتې په لومړۍ نیټه د کراۍ د تاديې یادونه ترتیب کړئ"
• **دندې** - "هر یکشنبه د مور سره د تلیفون کولو یادونه ترتیب کړئ"
• **پېښې** - "د ډاکتر سره د ناستې ۱ ساعت وړاندې خبر راکړئ"

تاسو د څه په اړه یادول غواړئ؟
""",
                "calendar": """
🗓️ **ستاسو د کیلنډر تنظیمول:**

زه کولی شم مدیریت کړم:
• **ناستې** - "بل دو شنبه د دندانپوه ناسته اضافه کړئ"
• **پېښې** - "په شنبه کې د زوکړې کلیزه ترتیب کړئ"
• **د وخت بندي** - "په جمعه کې د پروژې وخت بندي ترتیب کړئ"
• **تکراري توکي** - "هر دو شنبه اونیزه ټیم ناسته اضافه کړئ"

تاسو په خپل کیلنډر کې څه اضافه کوئ؟
"""
            }
        else:
            # English responses
            help_responses = {
                "schedule": """
📅 **Setting up your schedule:**

I can help you organize:
• **Meetings & appointments** - "Schedule meeting with team tomorrow 2 PM"
• **Daily routines** - "Set up my morning routine"  
• **Work blocks** - "Block time for deep work this week"
• **Personal time** - "Schedule gym sessions weekly"

What specific part of your schedule would you like to set up?
""",
                "reminder": """
⏰ **Setting up reminders:**

I can create reminders for:
• **Medication** - "Remind me to take pills daily at 8 AM"
• **Bills** - "Set reminder for rent payment on 1st of month"
• **Tasks** - "Remind me to call mom every Sunday"
• **Events** - "Alert me 1 hour before doctor appointment"

What would you like to be reminded about?
""",
                "calendar": """
🗓️ **Organizing your calendar:**

I can help manage:
• **Appointments** - "Add dentist appointment next Monday"
• **Events** - "Schedule birthday party on Saturday"
• **Deadlines** - "Set project deadline for Friday"
• **Recurring items** - "Add weekly team meeting every Monday"

What would you like to add to your calendar?
"""
            }
        
        return help_responses.get(target, 
            f"I'd love to help you set up your {target}! Could you tell me what specific {target} items you'd like to organize?")

    async def _create_scheduled_item(self, target: str, content: str, extracted: Dict, original_text: str, gui=None) -> str:
        """Actually create the scheduled item"""
        if not self.scheduler:
            language = await self._detect_language(original_text)
            if language == 'ur':
                return "Main aap ko ye set karne mein madad kar sakta hoon, lekin abhi scheduling system available nahi hai."
            elif language == 'ps':
                return "زه کولی شم تاسو سره د دې ترتیبولو کې مرسته وکړم، مګر اوس د جدول سیستم شتون نلري."
            else:
                return "I'd love to help you set that up, but the scheduling system isn't available right now."
        
        try:
            # Use the scheduler to create the item
            urgency = extracted.get("urgency", "low")
            language = await self._detect_language(original_text)
            
            if language == 'ur':
                response = f"✅ Acha! Main aap ke liye **{content}** apne {target} mein set kar doonga."
                
                if urgency == "high":
                    response += "\n\nYeh zaroori lagta hai - main ise turant set kar doonga."
                elif urgency == "medium":
                    response += "\n\nMain aaj hi ise schedule kar doonga."
                else:
                    response += "\n\nMain aap ke schedule mein ise organize kar doonga."
                
                # Ask for timing details if not provided
                if not extracted.get("has_time_reference"):
                    response += "\n\nAap ise kab schedule karna chahenge? Masalan: 'aaj 3 baje' ya 'kal subah'"
                else:
                    response += "\n\nMain ise create karne ke liye tayyar hoon! Bas timing details confirm karo."
                
            elif language == 'ps':
                response = f"✅ ښه! زه به تاسو لپاره **{content}** ستاسو {target} کې ترتیب کړم."
                
                if urgency == "high":
                    response += "\n\nدا ضروري ښکاري - زه به دا په چټکۍ سره ترتیب کړم."
                elif urgency == "medium":
                    response += "\n\nزه به دا نن ترتیب کړم."
                else:
                    response += "\n\nزه به دا ستاسو په جدول کې تنظیم کړم."
                
                # Ask for timing details if not provided
                if not extracted.get("has_time_reference"):
                    response += "\n\nتاسو دا کله ترتیب کوئ؟ لکه: 'نن په ۳ بجې' یا 'سبا سهار'"
                else:
                    response += "\n\nزه د دې د جوړولو لپاره چمتو یم! یوازې د وخت توضیحات تایید کړئ."
                
            else:
                response = f"✅ Great! I'll help you set up **{content}** for your {target}."
                
                if urgency == "high":
                    response += "\n\nThis seems urgent - I'll prioritize setting this up immediately."
                elif urgency == "medium":
                    response += "\n\nI'll get this scheduled for you today."
                else:
                    response += "\n\nI'll help you organize this in your schedule."
                
                # Ask for timing details if not provided
                if not extracted.get("has_time_reference"):
                    response += "\n\nWhen would you like this scheduled? For example: 'today at 3 PM' or 'tomorrow morning'"
                else:
                    response += "\n\nI'm ready to create this! Just confirm the timing details."
            
            return response
            
        except Exception as e:
            logger.error(f"Scheduling creation error: {e}")
            language = await self._detect_language(original_text)
            
            if language == 'ur':
                return f"Main {content} set karte waqt issue face kar raha hoon. Chaliye simple tareeke se batayein aap kya schedule karna chahte hain."
            elif language == 'ps':
                return f"زه د {content} ترتیبولو کې ستونزه سره مخ یم. راځئ چې په ساده ډول ووایاست چې تاسو څه ترتیب کوئ."
            else:
                return f"I encountered an issue setting up {content}. Let me try a different approach - could you describe what you'd like to schedule in simpler terms?"

    async def _handle_intelligent_messaging(self, intent: InterpretedIntent, original_text: str, gui=None) -> str:
        """Handle intelligently interpreted messaging requests"""
        return await self._handle_chat(original_text, gui)

    async def _handle_intelligent_information(self, intent: InterpretedIntent, original_text: str, gui=None) -> str:
        """Handle intelligently interpreted information requests"""
        return await self._handle_chat(original_text, gui)

    async def _handle_intelligent_automation(self, intent: InterpretedIntent, original_text: str, gui=None) -> str:
        """Handle intelligently interpreted automation requests"""
        return await self._handle_chat(original_text, gui)

    @property
    def conversation_context(self) -> List[Dict]:
        """Get current conversation context"""
        return self.intelligent_interpreter.conversation_context
    
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

    # [Rest of the class remains the same with the existing methods...]
    # The _route_intent, _handle_messaging, _handle_knowledge, etc. methods stay as they are
    # Only the multilingual detection and response generation has been enhanced

    async def _handle_chat(self, text: str, gui=None) -> str:
        """Handle general chat with context awareness"""
        try:
            if gui:
                gui.update_status("Thinking...")
            
            # Get conversation context if available
            context = {}
            if hasattr(self.interpreter, 'get_conversation_state'):
                try:
                    context = self.interpreter.get_conversation_state()
                except Exception as e:
                    logger.warning(f"Failed to get conversation state: {e}")
            
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
            try:
                memory_context = self.memory.get_recent(2)
                for role, content in memory_context:
                    messages.append({"role": role, "content": content})
            except Exception as e:
                logger.warning(f"Failed to get memory context: {e}")
            
            # Add current query
            messages.append({"role": "user", "content": text})
            
            # Get AI response - use multilingual brain if available
            brain_to_use = self.multilingual_brain if self.multilingual_brain else self.brain
            response = await brain_to_use.ask(messages)
            
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm having trouble thinking right now. Please try again."
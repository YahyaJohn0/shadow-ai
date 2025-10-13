# shadow_core/decision_engine.py (updated __init__ method)
from asyncio.log import logger
from dynamic_nlu import ContextAwareInterpreter
from multilingual_reminder import MultilingualReminderParser
def __init__(self, brain, memory, messaging=None, scheduler=None, knowledge=None, automation=None):
    self.brain = brain
    self.memory = memory
    self.messaging = messaging
    self.scheduler = scheduler
    self.knowledge = knowledge
    self.automation = automation

    # Initialize multilingual system SAFELY
    try:
        from shadow_core.multilingual_factory import create_multilingual_system
        self.multilingual_manager, self.translator, self.working_brain = create_multilingual_system(brain)
        
        # Use working_brain for all AI operations
        if hasattr(self.working_brain, 'multilingual_manager'):
            logger.info("Multilingual brain initialized successfully")
        else:
            logger.warning("Using fallback brain without full multilingual support")
            self.working_brain = brain  # Fallback to original
                
    except Exception as e:
        logger.error(f"Multilingual initialization failed: {e}")
        self.multilingual_manager = None
        self.translator = None
        self.working_brain = brain  # Use original brain as fallback

    # Initialize Dynamic AI Interpreter with the working brain
    try:
        self.interpreter = ContextAwareInterpreter(self.working_brain)
        # Pass multilingual manager to interpreter if available
        if hasattr(self.interpreter, 'multilingual_manager') and self.multilingual_manager:
            self.interpreter.multilingual_manager = self.multilingual_manager
    except Exception as e:
        logger.error(f"Interpreter initialization failed: {e}")
        # Create basic interpreter as fallback
        self.interpreter = ContextAwareInterpreter(brain)

    # Initialize modules with working brain
    self._initialize_modules()
    
    # Initialize reminder parser safely
    try:
        self.reminder_parser = MultilingualReminderParser(self.working_brain)
    except Exception as e:
        logger.warning(f"Multilingual reminder parser not available: {e}")
        self.reminder_parser = None
        
    logger.info("Decision Engine initialized")
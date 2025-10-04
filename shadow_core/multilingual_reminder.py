# shadow_core/multilingual_reminder.py
"""
Multilingual reminder parser for Urdu, Pashto, and English
Understands natural language time expressions in all supported languages
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from dateparser import parse as date_parse
import asyncio

logger = logging.getLogger(__name__)

class MultilingualReminderParser:
    """
    Parses natural language reminders in Urdu, Pashto, and English
    Extracts time, date, and reminder content from speech/text
    """
    
    def __init__(self, brain):
        self.brain = brain
        
        # Time patterns for different languages
        self.time_patterns = {
            'ur': {
                'minutes': r'(\d+)\s*(منٹ|مِنِٹ)',
                'hours': r'(\d+)\s*(گھنٹے|گھنٹہ|آور)',
                'days': r'(\d+)\s*(دن|ڈے)',
                'time': r'(\d{1,2}):(\d{2})',
                'am_pm': r'(صبح|شام|رات)',
                'tomorrow': r'کل',
                'today': r'آج',
                'now': r'ابھی|اب'
            },
            'ps': {
                'minutes': r'(\d+)\s*(دقيقې|مينټ)',
                'hours': r'(\d+)\s*(ساعت|گھنٹے)',
                'days': r'(\d+)\s*(ورځې|ورځ)',
                'time': r'(\d{1,2}):(\d{2})',
                'am_pm': r'(سهار|ماښام|شپه)',
                'tomorrow': r'سبا',
                'today': r'نن',
                'now': r'اوس|همالہ'
            },
            'en': {
                'minutes': r'(\d+)\s*(minute|min)',
                'hours': r'(\d+)\s*(hour|hr)',
                'days': r'(\d+)\s*(day)',
                'time': r'(\d{1,2}):(\d{2})',
                'am_pm': r'(am|pm|morning|evening)',
                'tomorrow': r'tomorrow',
                'today': r'today',
                'now': r'now'
            }
        }
        
        # Common reminder phrases in different languages
        self.reminder_phrases = {
            'ur': [
                r'یاد دہانی|یاد دلاؤ|یاد رکھنا|نوٹ کرو|الارم لگاؤ',
                r'مجھے یاد دلاؤ کہ',
                r'یاد دہانی سیٹ کرو',
                r'میرے لیے نوٹ کرو'
            ],
            'ps': {
                r'یادونه|یاد راکړه|یاد کړه|یادول',
                r'ما ته یاد راکړه چې',
                r'یادونه موږه',
                r'زما لپاره یادونه کړه'
            },
            'en': {
                r'remind me|set reminder|remember|alert me',
                r'remind me to',
                r'set a reminder for',
                r'alert me about'
            }
        }
    
    async def parse_reminder(self, text: str, language: str) -> Dict[str, Any]:
        """
        Parse reminder from natural language text
        Returns: dict with time, message, and parsed components
        """
        try:
            # First, use AI to understand the reminder intent
            ai_parsed = await self._ai_parse_reminder(text, language)
            if ai_parsed:
                return ai_parsed
            
            # Fallback to pattern matching
            return self._pattern_parse_reminder(text, language)
            
        except Exception as e:
            logger.error(f"Reminder parsing error: {e}")
            return self._create_fallback_reminder(text, language)
    
    async def _ai_parse_reminder(self, text: str, language: str) -> Optional[Dict[str, Any]]:
        """Use AI to parse reminder with high accuracy"""
        try:
            prompt = self._build_reminder_parsing_prompt(text, language)
            response = await self.brain.ask([{"role": "system", "content": prompt}])
            
            # Parse AI response
            return self._parse_ai_reminder_response(response, text, language)
            
        except Exception as e:
            logger.warning(f"AI reminder parsing failed: {e}")
            return None
    
    def _build_reminder_parsing_prompt(self, text: str, language: str) -> str:
        """Build prompt for AI reminder parsing"""
        
        language_names = {'ur': 'Urdu', 'ps': 'Pashto', 'en': 'English'}
        lang_name = language_names.get(language, 'Urdu')
        
        return f"""
        Parse the following {lang_name} reminder request and extract:
        1. REMINDER MESSAGE: What should be remembered
        2. TIME: When should the reminder trigger
        3. DATE: Specific date if mentioned
        4. RELATIVE_TIME: Relative time like "in 5 minutes"
        
        TEXT: "{text}"
        LANGUAGE: {lang_name}
        
        Respond in JSON format only:
        {{
            "message": "the reminder content",
            "time": "HH:MM or null",
            "date": "YYYY-MM-DD or null", 
            "relative_minutes": 0,
            "relative_hours": 0,
            "relative_days": 0,
            "confidence": 0.95,
            "reasoning": "explanation of parsing"
        }}
        
        Examples:
        
        Urdu: "مجھے 5 منٹ بعد میٹنگ کی یاد دہانی کرو"
        {{
            "message": "میٹنگ",
            "time": null,
            "date": null,
            "relative_minutes": 5,
            "relative_hours": 0,
            "relative_days": 0,
            "confidence": 0.96,
            "reasoning": "User wants reminder about meeting in 5 minutes"
        }}
        
        Pashto: "ما ته په 2 گھنٹو کې د پروژې یادونه راکړه"
        {{
            "message": "پروژه",
            "time": null, 
            "date": null,
            "relative_minutes": 0,
            "relative_hours": 2,
            "relative_days": 0,
            "confidence": 0.94,
            "reasoning": "User wants project reminder in 2 hours"
        }}
        
        English: "Remind me tomorrow at 3 PM about the doctor appointment"
        {{
            "message": "doctor appointment",
            "time": "15:00",
            "date": "tomorrow",
            "relative_minutes": 0,
            "relative_hours": 0,
            "relative_days": 1,
            "confidence": 0.97,
            "reasoning": "User wants reminder for doctor appointment tomorrow at 3 PM"
        }}
        
        Respond with JSON only:
        """
    
    def _parse_ai_reminder_response(self, response: str, original_text: str, language: str) -> Dict[str, Any]:
        """Parse AI response for reminder data"""
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return self._create_fallback_reminder(original_text, language)
            
            data = json.loads(json_match.group())
            
            # Calculate actual reminder time
            reminder_time = self._calculate_reminder_time(data)
            
            return {
                'success': True,
                'message': data.get('message', 'Reminder'),
                'scheduled_time': reminder_time,
                'relative_minutes': data.get('relative_minutes', 0),
                'relative_hours': data.get('relative_hours', 0),
                'relative_days': data.get('relative_days', 0),
                'specific_time': data.get('time'),
                'specific_date': data.get('date'),
                'confidence': data.get('confidence', 0.5),
                'reasoning': data.get('reasoning', 'AI parsed reminder'),
                'original_text': original_text
            }
            
        except Exception as e:
            logger.error(f"AI response parsing error: {e}")
            return self._create_fallback_reminder(original_text, language)
    
    def _pattern_parse_reminder(self, text: str, language: str) -> Dict[str, Any]:
        """Fallback pattern-based reminder parsing"""
        patterns = self.time_patterns.get(language, self.time_patterns['ur'])
        text_lower = text.lower()
        
        # Extract relative time
        minutes = self._extract_pattern(text_lower, patterns['minutes'])
        hours = self._extract_pattern(text_lower, patterns['hours']) 
        days = self._extract_pattern(text_lower, patterns['days'])
        
        # Extract specific time
        time_match = re.search(patterns['time'], text)
        specific_time = time_match.group() if time_match else None
        
        # Calculate reminder time
        reminder_time = self._calculate_reminder_time({
            'relative_minutes': minutes,
            'relative_hours': hours,
            'relative_days': days,
            'time': specific_time
        })
        
        # Extract reminder message (remove time phrases)
        message = self._extract_reminder_message(text, language)
        
        return {
            'success': True,
            'message': message,
            'scheduled_time': reminder_time,
            'relative_minutes': minutes,
            'relative_hours': hours,
            'relative_days': days,
            'specific_time': specific_time,
            'confidence': 0.6,
            'reasoning': 'Pattern-based parsing',
            'original_text': text
        }
    
    def _extract_pattern(self, text: str, pattern: str) -> int:
        """Extract numeric value from pattern"""
        match = re.search(pattern, text)
        return int(match.group(1)) if match else 0
    
    def _extract_reminder_message(self, text: str, language: str) -> str:
        """Extract reminder message by removing time phrases"""
        # Remove common time phrases
        time_phrases = []
        patterns = self.time_patterns.get(language, self.time_patterns['ur'])
        
        for pattern in patterns.values():
            matches = re.finditer(pattern, text)
            for match in matches:
                time_phrases.append(match.group())
        
        # Remove time phrases from text
        message = text
        for phrase in time_phrases:
            message = message.replace(phrase, '')
        
        # Clean up the message
        message = re.sub(r'\s+', ' ', message).strip()
        
        # Remove reminder trigger words
        reminder_words = ['remind', 'remember', 'alert', 'یاد', 'یادونه']
        for word in reminder_words:
            message = message.replace(word, '')
        
        return message.strip() or 'Reminder'
    
    def _calculate_reminder_time(self, data: Dict[str, Any]) -> float:
        """Calculate actual reminder timestamp"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Handle relative time
        if data.get('relative_minutes') or data.get('relative_hours') or data.get('relative_days'):
            delta = timedelta(
                minutes=data.get('relative_minutes', 0),
                hours=data.get('relative_hours', 0),
                days=data.get('relative_days', 0)
            )
            return (now + delta).timestamp()
        
        # Handle specific time
        if data.get('time'):
            # Parse specific time (simplified)
            time_str = data.get('time')
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
                reminder_dt = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                
                # If time has passed, schedule for tomorrow
                if reminder_dt < now:
                    reminder_dt += timedelta(days=1)
                
                return reminder_dt.timestamp()
        
        # Default: 1 hour from now
        return (now + timedelta(hours=1)).timestamp()
    
    def _create_fallback_reminder(self, text: str, language: str) -> Dict[str, Any]:
        """Create fallback reminder when parsing fails"""
        from datetime import datetime, timedelta
        
        return {
            'success': True,
            'message': text,
            'scheduled_time': (datetime.now() + timedelta(hours=1)).timestamp(),
            'relative_minutes': 0,
            'relative_hours': 1,
            'relative_days': 0,
            'confidence': 0.3,
            'reasoning': 'Fallback reminder',
            'original_text': text
        }
    
    def get_reminder_examples(self, language: str) -> list:
        """Get example reminder phrases for a language"""
        examples = {
            'ur': [
                "مجھے 5 منٹ بعد میٹنگ کی یاد دہانی کرو",
                "کل صبح 9 بجے دفتر جانے کی یاد دلاؤ", 
                "2 گھنٹے بعد دوائی کھانی ہے",
                "آج شام 6 بجے فون کرنا ہے"
            ],
            'ps': [
                "ما ته په 5 دقيقو کې د غونډې یادونه راکړه",
                "سبا په 9 بجو دفتر ته لاړ شه",
                "په 2 گھنٹو کې درمل وخوره", 
                "نن ماښام په 6 بجو زنگ وهوه"
            ],
            'en': [
                "Remind me in 5 minutes about the meeting",
                "Set reminder for tomorrow at 9 AM for office",
                "Alert me in 2 hours to take medicine",
                "Remember to call at 6 PM today"
            ]
        }
        
        return examples.get(language, examples['ur'])
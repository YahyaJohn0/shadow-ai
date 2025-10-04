# shadow_core/urdu_nlp_fixed.py
"""
Fixed Urdu NLP Engine - No unhashable type errors
"""

import logging
import re
import json
import asyncio
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter
import requests
import numpy as np
from difflib import SequenceMatcher
import pickle
import os

logger = logging.getLogger(__name__)

class AdvancedUrduNLP:
    """
    Fixed Advanced Urdu Natural Language Processing
    """
    
    def __init__(self, brain):
        self.brain = brain
        self.urdu_dictionary = self._load_urdu_dictionary()
        self.slang_mapping = self._load_urdu_slang()
        self.context_memory = {}
        self.conversation_history = []
        
        # FIXED: Use tuples instead of lists for patterns
        self.urdu_patterns = {
            'greetings': (
                'السلام علیکم', 'سلام', 'ہیلو', 'ہائے', 'کیا حال ہے', 'آپ کیسے ہیں'
            ),
            'questions': (
                'کیا', 'کون', 'کیوں', 'کب', 'کہاں', 'کس طرح', 'کتنا', 'کیسے'
            ),
            'commands': (
                'کرو', 'بناؤ', 'دکھاؤ', 'کھولو', 'بند کرو', 'لکھو', 'پڑھو', 'بولو'
            ),
            'time_expressions': (
                'ابھی', 'اب', 'کل', 'آج', 'پرسوں', 'صبح', 'شام', 'رات', 'دن'
            )
        }
        
        # FIXED: Use tuples for phonetic variations
        self.phonetic_variations = {
            'ہے': ('ہیں', 'ہے', 'ہی'),
            'ہیں': ('ہے', 'ہیں', 'ہی'),
            'کر': ('کرو', 'کریں', 'کریے'),
            'دے': ('دو', 'دیں', 'دیجیے'),
            'لو': ('لیں', 'لیجیے', 'لو')
        }
        
        logger.info("Fixed Advanced Urdu NLP Engine initialized")
    
    def _load_urdu_dictionary(self) -> Dict[str, Any]:
        """Load comprehensive Urdu dictionary"""
        return {
            # Common words with multiple meanings
            'کرو': ('do', 'execute', 'perform'),
            'بناؤ': ('make', 'create', 'build'),
            'دکھاؤ': ('show', 'display', 'demonstrate'),
            'کھولو': ('open', 'unlock', 'start'),
            'بند': ('close', 'shut', 'stop'),
            'لکھو': ('write', 'type', 'compose'),
            'پڑھو': ('read', 'study', 'recite'),
            'بولو': ('speak', 'talk', 'say'),
            
            # Time-related words
            'ابھی': ('now', 'immediately', 'right away'),
            'کل': ('tomorrow', 'yesterday'),
            'آج': ('today',),
            'صبح': ('morning', 'dawn'),
            'شام': ('evening', 'dusk'),
            'رات': ('night',),
            
            # Question words
            'کیا': ('what', 'did', 'whether'),
            'کون': ('who',),
            'کیوں': ('why',),
            'کب': ('when',),
            'کہاں': ('where',),
            'کس': ('which',),
            'کتنا': ('how much',),
            'کیسے': ('how',),
            
            # Common verbs
            'جا': ('go',),
            'آ': ('come',),
            'دو': ('give',),
            'لو': ('take',),
            'کھا': ('eat',),
            'پی': ('drink',),
            'سو': ('sleep',)
        }
    
    def _load_urdu_slang(self) -> Dict[str, str]:
        """Load Urdu slang and colloquial mappings"""
        return {
            'پلیز': 'براہ کرم',
            'تھینکس': 'شکریہ',
            'وائیٹ': 'انتظار',
            'اوکے': 'ٹھیک',
            'ہائے': 'سلام',
            'بائے': 'خدا حافظ',
            'واؤ': 'واہ',
            'کول': 'ٹھنڈا',
            'ہاٹ': 'گرم',
            'فاسٹ': 'تیز',
            'سلو': 'آہستہ'
        }
    
    async def super_understand(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Super intelligent Urdu understanding with multiple AI models
        """
        try:
            # Step 1: Pre-process text
            cleaned_text = self._advanced_preprocess(text)
            
            # Step 2: Multiple understanding approaches
            understanding_results = []
            
            # Run each understanding method separately to catch errors
            try:
                ai_result = await self._ai_deep_understanding(cleaned_text, context)
                understanding_results.append(ai_result)
            except Exception as e:
                logger.warning(f"AI understanding failed: {e}")
                understanding_results.append({"method": "ai", "confidence": 0.0, "error": str(e)})
            
            try:
                pattern_result = self._pattern_based_understanding(cleaned_text)
                understanding_results.append(pattern_result)
            except Exception as e:
                logger.warning(f"Pattern understanding failed: {e}")
                understanding_results.append({"method": "pattern", "confidence": 0.0, "error": str(e)})
            
            try:
                context_result = self._contextual_understanding(cleaned_text, context)
                understanding_results.append(context_result)
            except Exception as e:
                logger.warning(f"Context understanding failed: {e}")
                understanding_results.append({"method": "context", "confidence": 0.0, "error": str(e)})
            
            try:
                semantic_result = await self._semantic_understanding(cleaned_text)
                understanding_results.append(semantic_result)
            except Exception as e:
                logger.warning(f"Semantic understanding failed: {e}")
                understanding_results.append({"method": "semantic", "confidence": 0.0, "error": str(e)})
            
            # Step 3: Combine results with confidence scoring
            final_understanding = self._combine_understandings(understanding_results, cleaned_text)
            
            # Step 4: Update conversation context
            self._update_context(cleaned_text, final_understanding)
            
            logger.info(f"Super Urdu Understanding: {final_understanding.get('user_intent', 'unknown')}")
            return final_understanding
            
        except Exception as e:
            logger.error(f"Super understanding error: {e}")
            return self._fallback_understanding(text)
    
    def _advanced_preprocess(self, text: str) -> str:
        """Advanced text preprocessing for Urdu"""
        try:
            # Normalize text
            text = text.strip()
            
            # Replace common variations
            text = self._normalize_urdu_variations(text)
            
            # Fix common spelling mistakes
            text = self._fix_common_spelling(text)
            
            # Expand contractions and slang
            text = self._expand_urdu_contractions(text)
            
            # Remove extra spaces
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        except Exception as e:
            logger.warning(f"Text preprocessing failed: {e}")
            return text
    
    def _normalize_urdu_variations(self, text: str) -> str:
        """Normalize Urdu text variations"""
        try:
            # Normalize common character variations
            variations = {
                'ي': 'ی',  # Arabic yeh to Urdu yeh
                'ك': 'ک',  # Arabic kaf to Urdu kaf
                'ۂ': 'ہ',  # Alternate heh
                'ۃ': 'ہ',  # Alternate heh
                'ؤ': 'و',  # Hamza to wow
            }
            
            for old, new in variations.items():
                text = text.replace(old, new)
            
            return text
        except Exception as e:
            logger.warning(f"Text normalization failed: {e}")
            return text
    
    def _fix_common_spelling(self, text: str) -> str:
        """Fix common Urdu spelling mistakes"""
        try:
            corrections = {
                'کرون': 'کروں',
                'کرین': 'کریں',
                'ہون': 'ہوں',
                'ہین': 'ہیں',
                'جائین': 'جائیں',
                'آیین': 'آئیں',
                'دیکه': 'دیکھ',
                'سکه': 'سکھ',
                'لیکه': 'لکھ'
            }
            
            for wrong, correct in corrections.items():
                text = text.replace(wrong, correct)
            
            return text
        except Exception as e:
            logger.warning(f"Spelling correction failed: {e}")
            return text
    
    def _expand_urdu_contractions(self, text: str) -> str:
        """Expand Urdu contractions and slang"""
        try:
            for slang, formal in self.slang_mapping.items():
                text = text.replace(slang, formal)
            
            return text
        except Exception as e:
            logger.warning(f"Contraction expansion failed: {e}")
            return text
    
    async def _ai_deep_understanding(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI for deep semantic understanding"""
        try:
            prompt = self._build_deep_understanding_prompt(text, context)
            response = await self.brain.ask([{"role": "system", "content": prompt}])
            
            return self._parse_ai_understanding(response, text)
            
        except Exception as e:
            logger.warning(f"AI deep understanding failed: {e}")
            return {"method": "ai", "confidence": 0.0, "error": str(e)}
    
    def _build_deep_understanding_prompt(self, text: str, context: Dict[str, Any]) -> str:
        """Build prompt for deep Urdu understanding"""
        
        context_str = json.dumps(context, ensure_ascii=False) if context else "No context"
        
        return f"""
        You are an expert in Urdu language understanding. Analyze the Urdu text and provide comprehensive understanding.
        
        URDU TEXT: "{text}"
        CONTEXT: {context_str}
        
        Analyze these aspects:
        1. GRAMMATICAL STRUCTURE: Sentence type, verb forms, tense
        2. SEMANTIC MEANING: Core message and intent
        3. CONTEXTUAL MEANING: How context affects understanding
        4. CULTURAL NUANCES: Cultural references and implications
        5. USER INTENT: What the user wants to achieve
        6. EMOTIONAL TONE: Emotional context of the message
        
        Respond in JSON format:
        {{
            "grammatical_analysis": {{
                "sentence_type": "declarative|interrogative|imperative|exclamatory",
                "tense": "present|past|future|imperative",
                "verb_forms": ["list of verbs"],
                "subject": "main subject",
                "object": "main object"
            }},
            "semantic_meaning": "core meaning in Urdu",
            "contextual_meaning": "context-aware meaning", 
            "user_intent": "what user wants",
            "emotional_tone": "neutral|happy|sad|angry|excited|formal|casual",
            "confidence": 0.95,
            "cultural_notes": "any cultural references",
            "response_suggestions": ["suggested responses in Urdu"]
        }}
        
        Provide detailed analysis:
        """
    
    def _parse_ai_understanding(self, response: str, original_text: str) -> Dict[str, Any]:
        """Parse AI understanding response"""
        try:
            import json
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                data["method"] = "ai_deep"
                return data
        except Exception as e:
            logger.warning(f"AI response parsing failed: {e}")
        
        return {"method": "ai", "confidence": 0.0, "error": "Parse failed"}
    
    def _pattern_based_understanding(self, text: str) -> Dict[str, Any]:
        """Pattern-based understanding as fallback"""
        try:
            text_lower = text.lower()
            
            # Check for patterns using tuple iteration (FIXED)
            intent = "unknown"
            confidence = 0.7
            
            # Greeting detection
            if any(pattern in text_lower for pattern in self.urdu_patterns['greetings']):
                intent = "greeting"
                confidence = 0.9
            
            # Question detection
            elif any(pattern in text_lower for pattern in self.urdu_patterns['questions']):
                intent = "question"
                confidence = 0.85
            
            # Command detection
            elif any(pattern in text_lower for pattern in self.urdu_patterns['commands']):
                intent = "command"
                confidence = 0.8
            
            # Time expression detection
            elif any(pattern in text_lower for pattern in self.urdu_patterns['time_expressions']):
                intent = "time_related"
                confidence = 0.75
            
            return {
                "method": "pattern",
                "intent": intent,
                "confidence": confidence,
                "keywords": self._extract_keywords(text),
                "sentence_structure": self._analyze_sentence_structure(text)
            }
        except Exception as e:
            logger.warning(f"Pattern understanding failed: {e}")
            return {"method": "pattern", "confidence": 0.0, "error": str(e)}
    
    def _contextual_understanding(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Context-aware understanding"""
        try:
            if not context:
                return {"method": "context", "confidence": 0.0, "error": "No context"}
            
            # Use conversation history for better understanding
            recent_context = self.conversation_history[-3:] if self.conversation_history else []
            
            return {
                "method": "context",
                "confidence": 0.8,
                "context_match": self._match_with_context(text, recent_context),
                "topic_continuity": self._check_topic_continuity(text),
                "previous_intent": context.get('last_intent', 'unknown')
            }
        except Exception as e:
            logger.warning(f"Context understanding failed: {e}")
            return {"method": "context", "confidence": 0.0, "error": str(e)}
    
    async def _semantic_understanding(self, text: str) -> Dict[str, Any]:
        """Semantic understanding using word embeddings"""
        try:
            # This would use word2vec or similar models
            # For now, using simple semantic analysis
            
            return {
                "method": "semantic",
                "confidence": 0.7,
                "semantic_similarity": self._calculate_semantic_similarity(text),
                "word_relationships": self._analyze_word_relationships(text)
            }
        except Exception as e:
            logger.warning(f"Semantic understanding failed: {e}")
            return {"method": "semantic", "confidence": 0.0, "error": str(e)}
    
    def _combine_understandings(self, understandings: List[Dict], original_text: str) -> Dict[str, Any]:
        """Combine multiple understanding approaches"""
        try:
            # Filter valid understandings
            valid_understandings = []
            for u in understandings:
                if isinstance(u, dict) and u.get('confidence', 0) > 0.3:  # Lowered threshold
                    valid_understandings.append(u)
            
            if not valid_understandings:
                return self._fallback_understanding(original_text)
            
            # Take the understanding with highest confidence
            best_understanding = max(valid_understandings, key=lambda x: x.get('confidence', 0))
            
            # Add combined analysis (FIXED: Use string representation for methods)
            best_understanding["combined_confidence"] = best_understanding.get('confidence', 0)
            best_understanding["methods_used"] = [str(u.get('method', 'unknown')) for u in valid_understandings]
            best_understanding["original_text"] = original_text
            
            return best_understanding
        except Exception as e:
            logger.warning(f"Understanding combination failed: {e}")
            return self._fallback_understanding(original_text)
    
    def _fallback_understanding(self, text: str) -> Dict[str, Any]:
        """Fallback understanding when all methods fail"""
        return {
            "method": "fallback",
            "confidence": 0.3,
            "user_intent": "unknown",
            "semantic_meaning": text,
            "suggested_action": "ask_clarification",
            "response_suggestions": [
                "معاف کیجئے، میں سمجھ نہیں سکا۔ براہ کرم دوبارہ کہیں۔",
                "کیا آپ اسے مختلف الفاظ میں بیان کر سکتے ہیں؟",
                "میں آپ کی بات پوری طرح نہیں سمجھ سکا۔"
            ]
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from Urdu text"""
        try:
            words = text.split()
            keywords = []
            
            # FIXED: Use tuple for common particles
            common_particles = ('میں', 'نے', 'کو', 'سے', 'پر', 'کا', 'کی', 'کے')
            
            for word in words:
                # Remove common particles
                if word not in common_particles:
                    if len(word) > 2:  # Meaningful words usually have more than 2 characters
                        keywords.append(word)
            
            return keywords
        except Exception as e:
            logger.warning(f"Keyword extraction failed: {e}")
            return []
    
    def _analyze_sentence_structure(self, text: str) -> Dict[str, Any]:
        """Analyze Urdu sentence structure"""
        try:
            words = text.split()
            
            # FIXED: Convert patterns to tuple for iteration
            question_words = tuple(self.urdu_patterns['questions'])
            
            return {
                "word_count": len(words),
                "has_question_word": any(word in question_words for word in words),
                "has_verb": any(word in self.urdu_dictionary for word in words),
                "sentence_type": "question" if '؟' in text else "statement"
            }
        except Exception as e:
            logger.warning(f"Sentence analysis failed: {e}")
            return {"word_count": 0, "has_question_word": False, "has_verb": False, "sentence_type": "unknown"}
    
    def _match_with_context(self, text: str, context: List[Dict]) -> float:
        """Calculate how well text matches conversation context"""
        try:
            if not context:
                return 0.0
            
            # Simple similarity calculation
            recent_texts = [ctx.get('text', '') for ctx in context[-2:]]
            similarities = [self._text_similarity(text, ctx_text) for ctx_text in recent_texts]
            
            return max(similarities) if similarities else 0.0
        except Exception as e:
            logger.warning(f"Context matching failed: {e}")
            return 0.0
    
    def _check_topic_continuity(self, text: str) -> bool:
        """Check if text continues the current topic"""
        try:
            if not self.conversation_history:
                return False
            
            last_text = self.conversation_history[-1].get('text', '')
            similarity = self._text_similarity(text, last_text)
            
            return similarity > 0.6
        except Exception as e:
            logger.warning(f"Topic continuity check failed: {e}")
            return False
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        try:
            return SequenceMatcher(None, text1, text2).ratio()
        except:
            return 0.0
    
    def _calculate_semantic_similarity(self, text: str) -> Dict[str, float]:
        """Calculate semantic similarity with common phrases"""
        try:
            common_phrases = {
                "greeting": "السلام علیکم",
                "question": "کیا آپ میری مدد کر سکتے ہیں",
                "command": "یہ کام کرو",
                "thanks": "شکریہ"
            }
            
            similarities = {}
            for intent, phrase in common_phrases.items():
                similarities[intent] = self._text_similarity(text, phrase)
            
            return similarities
        except Exception as e:
            logger.warning(f"Semantic similarity calculation failed: {e}")
            return {}
    
    def _analyze_word_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Analyze relationships between words"""
        try:
            words = text.split()
            relationships = []
            
            for i, word in enumerate(words):
                if word in self.urdu_dictionary:
                    relationships.append({
                        "word": word,
                        "meanings": list(self.urdu_dictionary[word]),  # Convert tuple to list for JSON
                        "position": i,
                        "importance": "high" if word in self.urdu_patterns['commands'] else "medium"
                    })
            
            return relationships
        except Exception as e:
            logger.warning(f"Word relationship analysis failed: {e}")
            return []
    
    def _update_context(self, text: str, understanding: Dict[str, Any]):
        """Update conversation context"""
        try:
            self.conversation_history.append({
                "text": text,
                "understanding": understanding,
                "timestamp": self._get_timestamp()
            })
            
            # Keep only last 10 conversations
            if len(self.conversation_history) > 10:
                self.conversation_history.pop(0)
        except Exception as e:
            logger.warning(f"Context update failed: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        try:
            if not self.conversation_history:
                return {"topic": "unknown", "mood": "neutral", "interaction_count": 0}
            
            recent_intents = [ctx['understanding'].get('user_intent', 'unknown') for ctx in self.conversation_history[-5:]]
            
            return {
                "topic": self._detect_current_topic(),
                "mood": self._detect_conversation_mood(),
                "interaction_count": len(self.conversation_history),
                "recent_intents": recent_intents
            }
        except Exception as e:
            logger.warning(f"Conversation summary failed: {e}")
            return {"topic": "unknown", "mood": "neutral", "interaction_count": 0}
    
    def _detect_current_topic(self) -> str:
        """Detect current conversation topic"""
        try:
            if not self.conversation_history:
                return "general"
            
            # Simple topic detection based on keywords
            recent_texts = [ctx['text'] for ctx in self.conversation_history[-3:]]
            combined_text = ' '.join(recent_texts)
            
            # FIXED: Use tuples for topic keywords
            topics = {
                "weather": ('موسم', 'بارش', 'گرمی', 'سردی', 'ہوا'),
                "work": ('کام', 'دفتر', 'میٹنگ', 'پروجیکٹ', 'ملازم'),
                "personal": ('خاندان', 'دوست', 'گھر', 'تعطیل', 'سفر'),
                "technology": ('کمپیوٹر', 'فون', 'انٹرنیٹ', 'اپلیکیشن', 'سافٹ ویئر')
            }
            
            for topic, keywords in topics.items():
                if any(keyword in combined_text for keyword in keywords):
                    return topic
            
            return "general"
        except Exception as e:
            logger.warning(f"Topic detection failed: {e}")
            return "general"
    
    def _detect_conversation_mood(self) -> str:
        """Detect overall conversation mood"""
        try:
            if not self.conversation_history:
                return "neutral"
            
            # FIXED: Use tuples for mood keywords
            mood_keywords = {
                "happy": ('شکریہ', 'اچھا', 'بہت', 'زبردست', 'واہ'),
                "urgent": ('جلدی', 'فوری', 'ابھی', 'تاکید', 'ضروری'),
                "formal": ('براہ کرم', 'آپ', 'حضور', 'جناب'),
                "casual": ('یار', 'بھائی', 'ارے', 'سنو')
            }
            
            recent_texts = [ctx['text'] for ctx in self.conversation_history[-3:]]
            combined_text = ' '.join(recent_texts).lower()
            
            for mood, keywords in mood_keywords.items():
                if any(keyword in combined_text for keyword in keywords):
                    return mood
            
            return "neutral"
        except Exception as e:
            logger.warning(f"Mood detection failed: {e}")
            return "neutral"
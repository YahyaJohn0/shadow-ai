# shadow_core/memory.py
"""
Memory system for Shadow AI Agent - Basic in-memory version with SQLite placeholder
"""

import time
import logging
import json
from collections import deque
import sqlite3
import os

logger = logging.getLogger(__name__)

class ShadowMemory:
    """Memory system for conversation history and user preferences"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # In-memory storage (will be replaced with SQLite)
        self.conversations = deque(maxlen=100)
        self.user_preferences = {}
        
        # Initialize SQLite connection for future use
        self.db_path = os.path.join(data_dir, "memory.db")
        self._init_database()
        
        logger.info("Shadow Memory initialized")
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            ''')
            
            # Create user_preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def save_chat(self, user_text: str, assistant_reply: str):
        """Save conversation turn to memory"""
        timestamp = time.time()
        
        # Save to in-memory storage
        self.conversations.append({
            'timestamp': timestamp,
            'user': user_text,
            'assistant': assistant_reply
        })
        
        # Also save to SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO conversations (timestamp, role, content) VALUES (?, ?, ?)",
                (timestamp, "user", user_text)
            )
            cursor.execute(
                "INSERT INTO conversations (timestamp, role, content) VALUES (?, ?, ?)",
                (timestamp, "assistant", assistant_reply)
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
        
        logger.debug(f"Conversation saved to memory: {user_text[:50]}...")
    
    def get_recent(self, n: int = 5):
        """Get recent conversation history"""
        # Try to get from database first
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT role, content FROM conversations ORDER BY timestamp DESC LIMIT ?",
                (n * 2,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            if rows:
                # Format and return database results
                formatted = [(role, content) for role, content in rows[::-1]]
                return formatted[-n*2:]  # Return last n pairs
            
        except Exception as e:
            logger.error(f"Error reading from database: {e}")
        
        # Fallback to in-memory storage
        recent = list(self.conversations)[-n:]
        formatted = []
        for conv in recent:
            formatted.append(("user", conv['user']))
            formatted.append(("assistant", conv['assistant']))
        return formatted
    
    def get_conversation_history(self, limit: int = 20):
        """Get full conversation history from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT role, content, timestamp FROM conversations ORDER BY timestamp ASC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return rows
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def get_user_preference(self, key: str, default=None):
        """Get user preference"""
        # Try database first
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
                
        except Exception as e:
            logger.error(f"Error reading preference from database: {e}")
        
        # Fallback to in-memory
        return self.user_preferences.get(key, default)
    
    def set_user_preference(self, key: str, value):
        """Set user preference"""
        self.user_preferences[key] = value
        
        # Also save to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key, str(value))
            )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving preference to database: {e}")
        
        logger.debug(f"User preference set: {key} = {value}")
    
    def clear_conversation_history(self):
        """Clear all conversation history"""
        self.conversations.clear()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM conversations")
            conn.commit()
            conn.close()
            
            logger.info("Conversation history cleared")
            
        except Exception as e:
            logger.error(f"Error clearing conversation history: {e}")
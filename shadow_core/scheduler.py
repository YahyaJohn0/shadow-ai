# shadow_core/scheduler.py
"""
Scheduler module for Shadow AI Agent - Reminders, timers, and automated task scheduling
"""

import logging
import asyncio
import time
import sqlite3
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
from shadow_core.multilingual_reminder import MultilingualReminderParser

logger = logging.getLogger(__name__)

class TaskType(Enum):
    REMINDER = "reminder"
    TIMER = "timer"
    ALARM = "alarm"
    SCHEDULED_TASK = "scheduled_task"

class TaskStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

@dataclass
class ScheduledTask:
    """Scheduled task data structure"""
    id: Optional[int]
    task_type: TaskType
    title: str
    description: str
    scheduled_time: float  # Unix timestamp
    created_time: float
    status: TaskStatus
    user_id: str = "default"
    recurrence: str = None  # "daily", "weekly", "monthly", or cron pattern
    metadata: Dict[str, Any] = None

class Scheduler:
    """
    Scheduler module for managing reminders, timers, and scheduled tasks
    """
    
    def __init__(self, data_dir: str = "data", brain=None):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.reminder_parser = MultilingualReminderParser(brain) if brain else None
        # Initialize database
        self.db_path = os.path.join(data_dir, "scheduler.db")
        self._init_database()
        
        # Active tasks and callbacks
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.callbacks: Dict[str, Callable] = {}
        
        # Background task for checking scheduled items
        self.background_task = None
        self.is_running = False  # Don't start immediately
        
        logger.info("Scheduler module initialized (background task not started yet)")
    
    async def set_reminder_from_natural_language(self, text: str, language: str) -> Dict[str, Any]:
        """
        Set reminder from natural language in any supported language
        """
        try:
            if not self.reminder_parser:
                return {"success": False, "error": "Reminder parser not available"}
            
            # Parse the natural language reminder
            parsed = await self.reminder_parser.parse_reminder(text, language)
            
            if not parsed.get('success'):
                return {"success": False, "error": "Could not parse reminder"}
            
            # Create the reminder task
            task_id = await self.schedule_task(
                title=parsed['message'],
                description=f"Reminder: {parsed['message']}",
                scheduled_time=parsed['scheduled_time'],
                task_type=TaskType.REMINDER
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "message": parsed['message'],
                "scheduled_time": parsed['scheduled_time'],
                "confidence": parsed.get('confidence', 0.5),
                "reasoning": parsed.get('reasoning', 'Reminder set')
            }
            
        except Exception as e:
            logger.error(f"Natural language reminder error: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_multilingual_reminder(self, text: str, input_language: str) -> Dict[str, Any]:
        """
        Set reminder from multilingual input (speech or text)
        """
        try:
            # Parse and set reminder
            result = await self.set_reminder_from_natural_language(text, input_language)
            
            if result['success']:
                # Format success message based on language
                success_messages = {
                    'ur': f"یاد دہانی سیٹ ہو گئی! میں آپ کو یاد دلاؤں گا: {result['message']}",
                    'ps': f"یادونه موږه شوه! زه به تاسو ته یاد راکړم: {result['message']}",
                    'en': f"Reminder set! I'll remind you: {result['message']}"
                }
                
                result['user_message'] = success_messages.get(input_language, success_messages['en'])
            
            return result
            
        except Exception as e:
            error_messages = {
                'ur': "معاف کیجئے، میں یہ یاد دہانی سیٹ نہیں کر سکا۔",
                'ps': "وبخښئ، زه دا یادونه نشو کولی سیٹ کړی.",
                'en': "Sorry, I couldn't set this reminder."
            }
            
            return {
                "success": False,
                "error": str(e),
                "user_message": error_messages.get(input_language, error_messages['en'])
            }    
    async def start(self):
        """Start the background scheduler - call this when event loop is running"""
        if self.is_running:
            return
        
        self.is_running = True
        self._start_background_scheduler()
        logger.info("Scheduler background task started")
    
    def _init_database(self):
        """Initialize scheduler database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    scheduled_time REAL NOT NULL,
                    created_time REAL NOT NULL,
                    status TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    recurrence TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Scheduler database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _start_background_scheduler(self):
        """Start background task for checking scheduled items"""
        async def background_check():
            while self.is_running:
                try:
                    await self._check_pending_tasks()
                    await asyncio.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Background scheduler error: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        
        # Only create task if there's a running event loop
        try:
            self.background_task = asyncio.create_task(background_check())
        except RuntimeError:
            logger.warning("No running event loop - scheduler will be started manually")
    
    async def _check_pending_tasks(self):
        """Check and execute pending tasks that are due"""
        try:
            pending_tasks = self._get_pending_tasks()
            current_time = time.time()
            
            for task in pending_tasks:
                if task.scheduled_time <= current_time:
                    await self._execute_task(task)
                    
        except Exception as e:
            logger.error(f"Error checking pending tasks: {e}")
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        try:
            logger.info(f"Executing task: {task.title}")
            
            # Update task status to active
            self._update_task_status(task.id, TaskStatus.ACTIVE)
            
            # Execute based on task type
            if task.task_type == TaskType.REMINDER:
                await self._execute_reminder(task)
            elif task.task_type == TaskType.TIMER:
                await self._execute_timer(task)
            elif task.task_type == TaskType.ALARM:
                await self._execute_alarm(task)
            elif task.task_type == TaskType.SCHEDULED_TASK:
                await self._execute_scheduled_task(task)
            
            # Handle recurrence
            if task.recurrence and task.status != TaskStatus.CANCELLED:
                await self._handle_recurrence(task)
            else:
                self._update_task_status(task.id, TaskStatus.COMPLETED)
                
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            self._update_task_status(task.id, TaskStatus.FAILED)
    
    async def _execute_reminder(self, task: ScheduledTask):
        """Execute a reminder task"""
        # Notify user via callback
        if "on_reminder" in self.callbacks:
            await self.callbacks["on_reminder"](task)
        else:
            logger.info(f"🔔 REMINDER: {task.title} - {task.description}")
    
    async def _execute_timer(self, task: ScheduledTask):
        """Execute a timer task"""
        if "on_timer" in self.callbacks:
            await self.callbacks["on_timer"](task)
        else:
            logger.info(f"⏰ TIMER: {task.title} - Time's up!")
    
    async def _execute_alarm(self, task: ScheduledTask):
        """Execute an alarm task"""
        if "on_alarm" in self.callbacks:
            await self.callbacks["on_alarm"](task)
        else:
            logger.info(f"🚨 ALARM: {task.title} - Wake up!")
    
    async def _execute_scheduled_task(self, task: ScheduledTask):
        """Execute a general scheduled task"""
        if "on_scheduled_task" in self.callbacks:
            await self.callbacks["on_scheduled_task"](task)
        else:
            logger.info(f"📅 TASK: {task.title} - {task.description}")
    
    async def _handle_recurrence(self, task: ScheduledTask):
        """Handle recurring tasks"""
        try:
            if task.recurrence == "daily":
                new_time = task.scheduled_time + 24 * 60 * 60  # Add 24 hours
            elif task.recurrence == "weekly":
                new_time = task.scheduled_time + 7 * 24 * 60 * 60  # Add 7 days
            elif task.recurrence == "monthly":
                # Approximate 30 days for simplicity
                new_time = task.scheduled_time + 30 * 24 * 60 * 60
            else:
                # Custom cron-like pattern or no recurrence
                return
            
            # Create new task for next occurrence
            new_task = ScheduledTask(
                id=None,
                task_type=task.task_type,
                title=task.title,
                description=task.description,
                scheduled_time=new_time,
                created_time=time.time(),
                status=TaskStatus.PENDING,
                user_id=task.user_id,
                recurrence=task.recurrence,
                metadata=task.metadata
            )
            
            self._save_task(new_task)
            
        except Exception as e:
            logger.error(f"Recurrence handling error: {e}")
    
    def set_callback(self, event_type: str, callback: Callable):
        """Set callback for task events"""
        self.callbacks[event_type] = callback
        logger.info(f"Callback set for {event_type}")
    
    async def set_reminder(self, title: str, description: str, delay_minutes: int = 0, 
                          delay_seconds: int = 0, recurrence: str = None) -> int:
        """Set a reminder"""
        scheduled_time = time.time() + (delay_minutes * 60) + delay_seconds
        return await self._create_task(TaskType.REMINDER, title, description, scheduled_time, recurrence)
    
    async def set_timer(self, duration_minutes: int = 0, duration_seconds: int = 0, 
                       title: str = "Timer") -> int:
        """Set a timer"""
        scheduled_time = time.time() + (duration_minutes * 60) + duration_seconds
        description = f"Timer for {duration_minutes} minutes {duration_seconds} seconds"
        return await self._create_task(TaskType.TIMER, title, description, scheduled_time)
    
    async def set_alarm(self, alarm_time: str, title: str = "Alarm", recurrence: str = None) -> int:
        """Set an alarm for a specific time"""
        scheduled_time = self._parse_time_string(alarm_time)
        return await self._create_task(TaskType.ALARM, title, f"Alarm for {alarm_time}", scheduled_time, recurrence)
    
    async def schedule_task(self, title: str, description: str, scheduled_time: float, 
                           task_type: TaskType = TaskType.SCHEDULED_TASK) -> int:
        """Schedule a general task"""
        return await self._create_task(task_type, title, description, scheduled_time)
    
    async def _create_task(self, task_type: TaskType, title: str, description: str, 
                          scheduled_time: float, recurrence: str = None) -> int:
        """Create a new scheduled task"""
        task = ScheduledTask(
            id=None,
            task_type=task_type,
            title=title,
            description=description,
            scheduled_time=scheduled_time,
            created_time=time.time(),
            status=TaskStatus.PENDING,
            user_id="default",
            recurrence=recurrence
        )
        
        task_id = self._save_task(task)
        logger.info(f"Task created: {title} (ID: {task_id})")
        
        # Schedule the task for execution
        await self._schedule_task_execution(task)
        
        return task_id
    
    def _save_task(self, task: ScheduledTask) -> int:
        """Save task to database and return ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks 
                (task_type, title, description, scheduled_time, created_time, status, user_id, recurrence, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task.task_type.value,
                task.title,
                task.description,
                task.scheduled_time,
                task.created_time,
                task.status.value,
                task.user_id,
                task.recurrence,
                str(task.metadata) if task.metadata else None
            ))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return task_id
            
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            return -1
    
    async def _schedule_task_execution(self, task: ScheduledTask):
        """Schedule task for execution at the appropriate time"""
        delay = max(0, task.scheduled_time - time.time())
        
        async def execute_with_delay():
            await asyncio.sleep(delay)
            await self._execute_task(task)
        
        if delay > 0:
            self.active_tasks[task.id] = asyncio.create_task(execute_with_delay())
    
    def _get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending tasks from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, task_type, title, description, scheduled_time, created_time, status, user_id, recurrence, metadata
                FROM tasks 
                WHERE status = ? AND scheduled_time <= ?
                ORDER BY scheduled_time ASC
            ''', (TaskStatus.PENDING.value, time.time() + 60))  # Tasks due in next minute
            
            tasks = []
            for row in cursor.fetchall():
                task = ScheduledTask(
                    id=row[0],
                    task_type=TaskType(row[1]),
                    title=row[2],
                    description=row[3],
                    scheduled_time=row[4],
                    created_time=row[5],
                    status=TaskStatus(row[6]),
                    user_id=row[7],
                    recurrence=row[8],
                    metadata=eval(row[9]) if row[9] else None
                )
                tasks.append(task)
            
            conn.close()
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting pending tasks: {e}")
            return []
    
    def get_upcoming_tasks(self, limit: int = 10) -> List[ScheduledTask]:
        """Get upcoming tasks (pending and active)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, task_type, title, description, scheduled_time, created_time, status, user_id, recurrence, metadata
                FROM tasks 
                WHERE status IN (?, ?) AND scheduled_time >= ?
                ORDER BY scheduled_time ASC
                LIMIT ?
            ''', (TaskStatus.PENDING.value, TaskStatus.ACTIVE.value, time.time(), limit))
            
            tasks = []
            for row in cursor.fetchall():
                task = ScheduledTask(
                    id=row[0],
                    task_type=TaskType(row[1]),
                    title=row[2],
                    description=row[3],
                    scheduled_time=row[4],
                    created_time=row[5],
                    status=TaskStatus(row[6]),
                    user_id=row[7],
                    recurrence=row[8],
                    metadata=eval(row[9]) if row[9] else None
                )
                tasks.append(task)
            
            conn.close()
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting upcoming tasks: {e}")
            return []
    
    def cancel_task(self, task_id: int) -> bool:
        """Cancel a scheduled task"""
        try:
            # Cancel the asyncio task if it's active
            if task_id in self.active_tasks:
                self.active_tasks[task_id].cancel()
                del self.active_tasks[task_id]
            
            # Update database status
            self._update_task_status(task_id, TaskStatus.CANCELLED)
            logger.info(f"Task {task_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False
    
    def _update_task_status(self, task_id: int, status: TaskStatus):
        """Update task status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE tasks SET status = ? WHERE id = ?
            ''', (status.value, task_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
    
    def _parse_time_string(self, time_str: str) -> float:
        """Parse time string like '14:30' or '2:30 PM' into timestamp"""
        try:
            # Handle relative times
            if 'minute' in time_str or 'hour' in time_str:
                return self._parse_relative_time(time_str)
            
            # Handle absolute times
            time_patterns = [
                r'(\d{1,2}):(\d{2})\s*(AM|PM)?',
                r'(\d{1,2})\s*(AM|PM)',
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, time_str.upper())
                if match:
                    if ':' in time_str:
                        hour = int(match.group(1))
                        minute = int(match.group(2))
                        period = match.group(3) if match.group(3) else None
                    else:
                        hour = int(match.group(1))
                        minute = 0
                        period = match.group(2)
                    
                    # Convert to 24-hour format
                    if period == 'PM' and hour < 12:
                        hour += 12
                    elif period == 'AM' and hour == 12:
                        hour = 0
                    
                    # Get today's date with the specified time
                    now = datetime.now()
                    scheduled_dt = datetime(now.year, now.month, now.day, hour, minute)
                    
                    # If time has already passed today, schedule for tomorrow
                    if scheduled_dt < now:
                        scheduled_dt += timedelta(days=1)
                    
                    return scheduled_dt.timestamp()
            
            # Default: if parsing fails, schedule for 1 hour from now
            return time.time() + 3600
            
        except Exception as e:
            logger.error(f"Time parsing error: {e}")
            return time.time() + 3600  # Default to 1 hour from now
    
    def _parse_relative_time(self, time_str: str) -> float:
        """Parse relative time like 'in 5 minutes' or 'in 2 hours'"""
        try:
            time_str = time_str.lower()
            current_time = time.time()
            
            # Minutes
            minute_match = re.search(r'(\d+)\s*minute', time_str)
            if minute_match:
                minutes = int(minute_match.group(1))
                return current_time + (minutes * 60)
            
            # Hours
            hour_match = re.search(r'(\d+)\s*hour', time_str)
            if hour_match:
                hours = int(hour_match.group(1))
                return current_time + (hours * 3600)
            
            # Days
            day_match = re.search(r'(\d+)\s*day', time_str)
            if day_match:
                days = int(day_match.group(1))
                return current_time + (days * 86400)
            
            return current_time + 300  # Default: 5 minutes
            
        except Exception as e:
            logger.error(f"Relative time parsing error: {e}")
            return time.time() + 300
    
    async def shutdown(self):
        """Clean shutdown of the scheduler"""
        self.is_running = False
        
        # Cancel all active tasks
        for task_id, task in self.active_tasks.items():
            task.cancel()
        
        if self.background_task:
            self.background_task.cancel()
        
        logger.info("Scheduler shutdown completed")


# Mock scheduler for testing
class MockScheduler(Scheduler):
    """Mock scheduler for testing without real task execution"""
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(data_dir)
        # Don't start background task for mock
        self.is_running = False
        logger.info("MockScheduler initialized (no background tasks)")
    
    async def _execute_task(self, task: ScheduledTask):
        """Mock task execution - just log instead of actually executing"""
        logger.info(f"[MOCK] Would execute task: {task.title}")
        self._update_task_status(task.id, TaskStatus.COMPLETED)
    
    async def start(self):
        """Mock start - do nothing"""
        logger.info("[MOCK] Scheduler 'started' (no background tasks)")
        self.is_running = True
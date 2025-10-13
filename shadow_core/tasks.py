import threading
import time
from datetime import datetime, timedelta
from typing import Tuple
from googleapiclient.discovery import build
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, MAX_SEARCH_RESULTS

class TaskManager:
    """
    Enhanced Task & Lead Manager.
    Handles:
      - Reminders
      - Tasks & Leads (add/list/update/remove)
      - Real Google searches
      - Time queries
    """
    def __init__(self, memory):
        self.memory = memory
        self.reminders = []
        self.tasks = []  # In-memory list for tasks/leads
        self._stop = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    # ------------------------------
    # Reminder Management
    # ------------------------------
    def add_reminder(self, message: str, when: datetime):
        reminder = {"message": message, "when": when.isoformat()}
        self.reminders.append(reminder)
        self.memory.save("reminder", reminder, type_="task")
        print(f"[TaskManager] Reminder added: '{message}' at {when}")

    def _run_loop(self):
        """Background loop to check reminders and fire them."""
        while not self._stop:
            now = datetime.utcnow()
            to_fire = []
            for r in list(self.reminders):
                rtime = datetime.fromisoformat(r["when"])
                if rtime <= now:
                    to_fire.append(r)
                    self.reminders.remove(r)
            for r in to_fire:
                print(f"[Reminder] {r['message']}")
            time.sleep(1)

    def stop(self):
        self._stop = True
        if self._thread.is_alive():
            self._thread.join(timeout=1)

    # ------------------------------
    # Task & Lead Management
    # ------------------------------
    def add_task(self, title: str, description: str = "", type_: str = "task"):
        """Add a task or client lead."""
        task = {
            "id": len(self.tasks) + 1,
            "type": type_,
            "title": title,
            "description": description,
            "status": "pending",
            "date_created": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.memory.save("task", task)
        return f"{type_.capitalize()} '{title}' added successfully."

    def list_tasks(self, type_: str = None, status: str = None):
        filtered = self.tasks
        if type_:
            filtered = [t for t in filtered if t["type"] == type_]
        if status:
            filtered = [t for t in filtered if t["status"] == status]
        return filtered if filtered else []

    def update_task(self, task_id: int, title: str = None, description: str = None, status: str = None):
        for t in self.tasks:
            if t["id"] == task_id:
                if title:
                    t["title"] = title
                if description:
                    t["description"] = description
                if status:
                    t["status"] = status
                self.memory.save("task", t)
                return f"Task/Lead {task_id} updated successfully."
        return f"Task/Lead {task_id} not found."

    def remove_task(self, task_id: int):
        for t in self.tasks:
            if t["id"] == task_id:
                self.tasks.remove(t)
                self.memory.save("task_removed", {"id": task_id})
                return f"Task/Lead {task_id} removed successfully."
        return f"Task/Lead {task_id} not found."

    # ------------------------------
    # Detect & Execute Tasks
    # ------------------------------
    def detect_and_execute(self, query: str, integr=None) -> Tuple[bool, str]:
        query_lower = query.lower().strip()

        # Google Search
        if query_lower.startswith("search "):
            topic = query[7:].strip()
            result = self.google_search(topic)
            summary = self.summarize_search(result)
            return True, summary

        # Get current time
        if "time" in query_lower or "current time" in query_lower:
            now = datetime.now().strftime("%H:%M:%S")
            return True, f"⏰ Current time is {now}"

        # Set simple reminder
        if query_lower.startswith("remind me to "):
            try:
                parts = query_lower.replace("remind me to ", "").split(" in ")
                message = parts[0].strip()
                delay = int(parts[1].split()[0])
                fire_time = datetime.utcnow() + timedelta(seconds=delay)
                self.add_reminder(message, fire_time)
                return True, f"⏰ Reminder set for {delay} seconds from now: {message}"
            except Exception:
                return True, "⚠️ Could not parse reminder. Use: 'remind me to <task> in <seconds>'"

        # No task detected
        return False, None

    # ------------------------------
    # Google Search
    # ------------------------------
    def google_search(self, query: str, num_results: int = MAX_SEARCH_RESULTS):
        try:
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()
            items = res.get("items", [])
            if not items:
                return ["No results found."]
            results = []
            for item in items:
                title = item.get("title")
                snippet = item.get("snippet")
                results.append(f"{title}: {snippet}")
            return results
        except Exception as e:
            return [f"[Search Error] {e}"]

    # ------------------------------
    # Summarize Search Results
    # ------------------------------
    def summarize_search(self, search_results):
        if not search_results or isinstance(search_results, str):
            return search_results or "No results found."
        summaries = []
        for i, res in enumerate(search_results[:MAX_SEARCH_RESULTS], start=1):
            summaries.append(f"{i}. {res}")
        return " Here are the top results: " + " ".join(summaries)

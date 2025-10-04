# shadow_core/gui.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import asyncio
import time

class ShadowGUI:
    def __init__(self, on_user_input_callback=None):
        self.root = tk.Tk()
        self.root.title("Shadow — Master System Prompt")
        self.root.geometry("900x560")
        self.on_user_input = on_user_input_callback

        # Frames
        self.left = tk.Frame(self.root, bg="#0f0f0f", width=300)
        self.center = tk.Frame(self.root, bg="#111111")
        self.right = tk.Frame(self.root, bg="#0f0f0f", width=300)
        self.left.pack(side="left", fill="y")
        self.center.pack(side="left", fill="both", expand=True)
        self.right.pack(side="left", fill="y")

        # Left: Tasks & reminders
        tk.Label(self.left, text="Tasks & Reminders", fg="white", bg="#0f0f0f", font=("Helvetica", 12, "bold")).pack(pady=8)
        self.tasks_txt = ScrolledText(self.left, height=30, width=35, bg="#111111", fg="white")
        self.tasks_txt.pack(padx=6, pady=6)

        # Center: Conversation + input
        tk.Label(self.center, text="Shadow — Conversation", fg="white", bg="#111111", font=("Helvetica", 14, "bold")).pack(pady=8)
        self.log = ScrolledText(self.center, height=24, bg="#0b0b0b", fg="white")
        self.log.pack(fill="both", padx=8, pady=4, expand=True)

        self.user_entry = tk.Entry(self.center, bg="#222222", fg="white")
        self.user_entry.pack(fill="x", padx=8, pady=6)
        self.user_entry.bind("<Return>", self._on_enter)

        # Right: Mode indicator
        tk.Label(self.right, text="Status", fg="white", bg="#0f0f0f", font=("Helvetica", 12, "bold")).pack(pady=8)
        self.mode_label = tk.Label(self.right, text="Idle", fg="white", bg="#333333", width=20, height=2)
        self.mode_label.pack(padx=8, pady=6)

        # Asyncio loop for background tasks
        self.loop = asyncio.new_event_loop()
        self._running = True
        self._ui_thread = threading.Thread(target=self._loop, daemon=True)
        self._ui_thread.start()

    def _on_enter(self, event):
        text = self.user_entry.get().strip()
        if not text:
            return
        self.log.insert("end", f"You: {text}\n")
        self.user_entry.delete(0, "end")
        if self.on_user_input:
            res = self.on_user_input(text)
            if asyncio.iscoroutine(res):
                # Schedule coroutine in the dedicated loop
                asyncio.run_coroutine_threadsafe(res, self.loop)

    def write_shadow(self, text):
        """Append Shadow's reply to the log."""
        self.log.insert("end", f"Shadow: {text}\n")
        self.log.see("end")

    def add_task(self, text):
        self.tasks_txt.insert("end", f"{text}\n")
        self.tasks_txt.see("end")

    def set_mode(self, mode_text):
        self.mode_label.config(text=mode_text)

    def _loop(self):
        """Run GUI updates + asyncio loop."""
        asyncio.set_event_loop(self.loop)
        while self._running:
            try:
                self.root.update()
            except tk.TclError:
                break
            # Run pending async tasks
            self.loop.call_soon(self.loop.stop)
            self.loop.run_forever()
            time.sleep(0.03)

    def run(self):
        self.root.mainloop()
        self._running = False

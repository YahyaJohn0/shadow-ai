# shadow_gui/main_window.py
"""
Modern GUI for Shadow AI Agent with multilingual support
Dark theme with voice visualization and real-time status
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
import threading
import asyncio
import queue
import time
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk
import os
import sys

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ShadowGUI:
    """
    Modern GUI for Shadow AI Agent with voice visualization and multilingual support
    """
    
    def __init__(self, shadow_agent):
        self.shadow = shadow_agent
        self.root = ctk.CTk()
        self.setup_window()
        
        # Message queue for thread-safe GUI updates
        self.message_queue = queue.Queue()
        
        # Voice visualization data
        self.voice_data = []
        self.is_listening = False
        self.is_speaking = False
        
        # Current language
        self.current_language = 'ur'  # Urdu default
        
        # Initialize all GUI components
        self.setup_gui()
        
        # Start message processing
        self.process_messages()
        self.reminder_parser = None

        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Shadow AI - Intelligent Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self):
        """Setup all GUI components"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
        self.setup_reminder_section()

    def setup_reminder_section(self):
        """Setup reminder controls in automation tab"""
        reminder_frame = ctk.CTkFrame(self.automation_tab)
        reminder_frame.pack(fill=tk.X, pady=5)
    
        reminder_label = ctk.CTkLabel(reminder_frame, text="⏰ Quick Reminders", font=ctk.CTkFont(weight="bold"))
        reminder_label.pack(anchor="w", pady=5)
    
        # Reminder input
        reminder_input_frame = ctk.CTkFrame(reminder_frame)
        reminder_input_frame.pack(fill=tk.X, pady=5)
    
        self.reminder_input = ctk.CTkEntry(
            reminder_input_frame,
            placeholder_text="Type reminder in any language...",
            font=ctk.CTkFont(size=12)
        )
        self.reminder_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.reminder_input.bind("<Return>", self.set_reminder)
    
        self.reminder_button = ctk.CTkButton(
            reminder_input_frame,
            text="Set Reminder",
            command=self.set_reminder,
            fg_color="#FF8C00",
            hover_color="#FFA500",
            width=100
        )
        self.reminder_button.pack(side=tk.RIGHT)
    
        # Quick reminder buttons - FIXED VERSION
        quick_frame = ctk.CTkFrame(reminder_frame)
        quick_frame.pack(fill=tk.X, pady=5)
    
        quick_label = ctk.CTkLabel(quick_frame, text="Quick Set:", font=ctk.CTkFont(size=12))
        quick_label.pack(anchor="w", pady=2)
    
        quick_buttons = [
            ("5 منٹ بعد", "5 minutes", "ur"),
            ("1 گھنٹے بعد", "1 hour", "ur"), 
            ("2 گھنٹے بعد", "2 hours", "ur"),
            ("5 minutes", "5 minutes", "en"),
            ("1 hour", "1 hour", "en")
        ]
    
        # Create a separate frame just for the buttons that will use grid
        buttons_frame = ctk.CTkFrame(quick_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
    
        for i, (text, command, lang) in enumerate(quick_buttons):
                btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=lambda cmd=command, l=lang: self.quick_reminder(cmd, l),
                width=100,
                height=25
                 )
                btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
    
      # Configure grid columns for equal distribution
        for i in range(3):
            buttons_frame.grid_columnconfigure(i, weight=1)
    
    def set_reminder(self, event=None):
        """Set reminder from text input"""
        reminder_text = self.reminder_input.get().strip()
        if not reminder_text:
            return
            
        self.reminder_input.delete(0, tk.END)
        
        # Process reminder in background
        threading.Thread(target=self.process_reminder, args=(reminder_text,), daemon=True).start()
    
    def process_reminder(self, reminder_text):
        """Process reminder in background"""
        async def async_process():
            try:
                # Detect language
                lang = await self.shadow.multilingual_manager.detect_language(reminder_text)
                
                # Set reminder using decision engine
                response = await self.shadow.decision_engine._handle_reminder_request(
                    reminder_text, 
                    {'is_reminder': True, 'language': lang, 'confidence': 0.9},
                    self
                )
                
                # Show success message
                self.add_chat_message("Reminder", response, "ai")
                
            except Exception as e:
                self.add_chat_message("Error", f"Failed to set reminder: {str(e)}", "ai")
                
        asyncio.run(async_process())
    
    def quick_reminder(self, reminder_text, language):
        """Set quick reminder"""
        self.reminder_input.delete(0, tk.END)
        self.reminder_input.insert(0, reminder_text)
        self.set_reminder()
                
    def create_sidebar(self):
        """Create the sidebar with controls"""
        self.sidebar = ctk.CTkFrame(self.main_container, width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Logo and title
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=20)
        
        # Create logo label (text-based for now)
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text="🤖 Shadow AI",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack()
        
        # Language selection
        self.create_language_controls()
        
        # Voice controls
        self.create_voice_controls()
        
        # Agent capabilities
        self.create_capabilities_section()
        
        # System info
        self.create_system_info()
        
    def create_language_controls(self):
        """Create language selection controls"""
        lang_frame = ctk.CTkFrame(self.sidebar)
        lang_frame.pack(fill=tk.X, padx=10, pady=10)
        
        lang_label = ctk.CTkLabel(lang_frame, text="🌍 Language", font=ctk.CTkFont(weight="bold"))
        lang_label.pack(pady=(10, 5))
        
        # Language buttons
        self.lang_var = tk.StringVar(value="ur")
        
        lang_urdu = ctk.CTkRadioButton(
            lang_frame, 
            text="اردو (Urdu)", 
            variable=self.lang_var, 
            value="ur",
            command=self.on_language_change
        )
        lang_urdu.pack(anchor="w", pady=2)
        
        lang_pashto = ctk.CTkRadioButton(
            lang_frame, 
            text="پښتو (Pashto)", 
            variable=self.lang_var, 
            value="ps",
            command=self.on_language_change
        )
        lang_pashto.pack(anchor="w", pady=2)
        
        lang_english = ctk.CTkRadioButton(
            lang_frame, 
            text="English", 
            variable=self.lang_var, 
            value="en",
            command=self.on_language_change
        )
        lang_english.pack(anchor="w", pady=2)
        
    def create_voice_controls(self):
        """Create voice control buttons"""
        voice_frame = ctk.CTkFrame(self.sidebar)
        voice_frame.pack(fill=tk.X, padx=10, pady=10)
        
        voice_label = ctk.CTkLabel(voice_frame, text="🎤 Voice Controls", font=ctk.CTkFont(weight="bold"))
        voice_label.pack(pady=(10, 5))
        
        # Voice buttons
        self.voice_button = ctk.CTkButton(
            voice_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        )
        self.voice_button.pack(fill=tk.X, pady=5)
        
        self.speak_button = ctk.CTkButton(
            voice_frame,
            text="🔊 Test Voice",
            command=self.test_voice,
            fg_color="#4169E1",
            hover_color="#5A7DE1"
        )
        self.speak_button.pack(fill=tk.X, pady=5)
        
    def create_capabilities_section(self):
        """Create agent capabilities display"""
        caps_frame = ctk.CTkFrame(self.sidebar)
        caps_frame.pack(fill=tk.X, padx=10, pady=10)
        
        caps_label = ctk.CTkLabel(caps_frame, text="🚀 Capabilities", font=ctk.CTkFont(weight="bold"))
        caps_label.pack(pady=(10, 5))
        
        capabilities = [
            "💬 Multilingual Chat",
            "📱 Messaging",
            "🌤️ Weather Info",
            "📈 Stock Data",
            "⏰ Reminders",
            "🖥️ Computer Control",
            "📁 File Management",
            "🌐 Web Search"
        ]
        
        for cap in capabilities:
            cap_label = ctk.CTkLabel(caps_frame, text=cap, font=ctk.CTkFont(size=12))
            cap_label.pack(anchor="w", pady=1)
            
    def create_system_info(self):
        """Create system information display"""
        info_frame = ctk.CTkFrame(self.sidebar)
        info_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        
        info_label = ctk.CTkLabel(info_frame, text="⚙️ System", font=ctk.CTkFont(weight="bold"))
        info_label.pack(pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(info_frame, text="🟢 Ready", text_color="green")
        self.status_label.pack()
        
        self.memory_label = ctk.CTkLabel(info_frame, text="Memory: 0 conversations")
        self.memory_label.pack()
        
    def create_main_content(self):
        """Create the main content area"""
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_tabs()
        
    def create_tabs(self):
        """Create tabbed interface"""
        self.tab_view = ctk.CTkTabview(self.content_frame)
        self.tab_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add tabs
        self.chat_tab = self.tab_view.add("💬 Chat")
        self.voice_tab = self.tab_view.add("🎤 Voice")
        self.automation_tab = self.tab_view.add("🖥️ Automation")
        self.settings_tab = self.tab_view.add("⚙️ Settings")
        
        # Setup each tab
        self.setup_chat_tab()
        self.setup_voice_tab()
        self.setup_automation_tab()
        self.setup_settings_tab()
        
    def setup_chat_tab(self):
        """Setup the chat interface"""
        # Chat display area
        self.chat_frame = ctk.CTkFrame(self.chat_tab)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat history
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame, 
            wrap=tk.WORD,
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input area
        input_frame = ctk.CTkFrame(self.chat_frame)
        input_frame.pack(fill=tk.X)
        
        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            font=ctk.CTkFont(size=12)
        )
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind("<Return>", self.send_chat_message)
        
        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            width=80
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Add welcome message
        self.add_chat_message("Shadow AI", "السلام علیکم! میں شاڈو AI ہوں۔ آپ کیسے مدد کر سکتا ہوں؟", "ai")
        
    def setup_voice_tab(self):
        """Setup voice visualization and controls"""
        # Voice visualization frame
        viz_frame = ctk.CTkFrame(self.voice_tab)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Voice visualization
        self.setup_voice_visualization(viz_frame)
        
        # Voice controls
        voice_controls_frame = ctk.CTkFrame(viz_frame)
        voice_controls_frame.pack(fill=tk.X, pady=10)
        
        self.voice_status = ctk.CTkLabel(
            voice_controls_frame, 
            text="🎤 Ready to listen...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.voice_status.pack(pady=5)
        
        # Voice activity log
        self.voice_log = ctk.CTkTextbox(
            viz_frame,
            height=150,
            wrap=tk.WORD,
            font=ctk.CTkFont(size=11)
        )
        self.voice_log.pack(fill=tk.X, pady=(10, 0))
        self.voice_log.insert("1.0", "Voice activity log:\n" + "="*50 + "\n")
        self.voice_log.configure(state="disabled")
        
    def setup_voice_visualization(self, parent):
        """Setup real-time voice visualization"""
        viz_container = ctk.CTkFrame(parent)
        viz_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create matplotlib figure for voice visualization
        self.fig, self.ax = plt.subplots(figsize=(8, 3), facecolor='#2B2B2B')
        self.ax.set_facecolor('#2B2B2B')
        
        # Initialize plot
        x = np.arange(100)
        y = np.zeros(100)
        self.line, = self.ax.plot(x, y, color='#00FFAA', linewidth=2)
        
        # Configure plot
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 100)
        self.ax.axis('off')  # Hide axes
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, viz_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def setup_automation_tab(self):
        """Setup automation controls"""
        auto_frame = ctk.CTkFrame(self.automation_tab)
        auto_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create automation controls grid
        self.create_automation_grid(auto_frame)
        
    def create_automation_grid(self, parent):
        """Create grid of automation controls"""
        # System controls
        sys_frame = ctk.CTkFrame(parent)
        sys_frame.pack(fill=tk.X, pady=5)
        
        sys_label = ctk.CTkLabel(sys_frame, text="🖥️ System Controls", font=ctk.CTkFont(weight="bold"))
        sys_label.pack(anchor="w", pady=5)
        
        sys_buttons_frame = ctk.CTkFrame(sys_frame)
        sys_buttons_frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("🔍 System Info", self.show_system_info, "#4169E1"),
            ("📊 Open Task Manager", self.open_task_manager, "#FF6347"),
            ("📁 Open Documents", self.open_documents, "#32CD32"),
            ("🌐 Open Browser", self.open_browser, "#FFD700")
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = ctk.CTkButton(
                sys_buttons_frame,
                text=text,
                command=command,
                fg_color=color,
                hover_color=self.adjust_color(color, -20)
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            sys_buttons_frame.grid_columnconfigure(i%2, weight=1)
        
        # File operations
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill=tk.X, pady=5)
        
        file_label = ctk.CTkLabel(file_frame, text="📁 File Operations", font=ctk.CTkFont(weight="bold"))
        file_label.pack(anchor="w", pady=5)
        
        # File controls
        file_controls = ctk.CTkFrame(file_frame)
        file_controls.pack(fill=tk.X, pady=5)
        
        self.file_path = ctk.CTkEntry(
            file_controls,
            placeholder_text="Enter file/folder path...",
            font=ctk.CTkFont(size=12)
        )
        self.file_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        file_btn_frame = ctk.CTkFrame(file_controls)
        file_btn_frame.pack(side=tk.RIGHT)
        
        ctk.CTkButton(file_btn_frame, text="List Files", command=self.list_files, width=80).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(file_btn_frame, text="Open", command=self.open_file, width=80).pack(side=tk.LEFT, padx=2)
        
    def setup_settings_tab(self):
        """Setup settings and preferences"""
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Appearance
        appear_frame = ctk.CTkFrame(settings_frame)
        appear_frame.pack(fill=tk.X, pady=5)
        
        appear_label = ctk.CTkLabel(appear_frame, text="🎨 Appearance", font=ctk.CTkFont(weight="bold"))
        appear_label.pack(anchor="w", pady=5)
        
        self.theme_var = tk.StringVar(value="dark")
        ctk.CTkRadioButton(appear_frame, text="Dark Mode", variable=self.theme_var, value="dark", command=self.change_theme).pack(anchor="w")
        ctk.CTkRadioButton(appear_frame, text="Light Mode", variable=self.theme_var, value="light", command=self.change_theme).pack(anchor="w")
        
        # Voice settings
        voice_frame = ctk.CTkFrame(settings_frame)
        voice_frame.pack(fill=tk.X, pady=5)
        
        voice_label = ctk.CTkLabel(voice_frame, text="🔊 Voice Settings", font=ctk.CTkFont(weight="bold"))
        voice_label.pack(anchor="w", pady=5)
        
        ctk.CTkLabel(voice_frame, text="Speech Rate:").pack(anchor="w")
        self.speech_rate = ctk.CTkSlider(voice_frame, from_=50, to=300, number_of_steps=25)
        self.speech_rate.set(150)
        self.speech_rate.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(voice_frame, text="Volume:").pack(anchor="w")
        self.volume = ctk.CTkSlider(voice_frame, from_=0, to=100, number_of_steps=100)
        self.volume.set(80)
        self.volume.pack(fill=tk.X, pady=5)
        
    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = ctk.CTkLabel(
            self.status_bar, 
            text="🟢 Shadow AI is ready | Urdu (اردو) | Voice: Available",
            font=ctk.CTkFont(size=11)
        )
        self.status_text.pack(side=tk.LEFT, padx=10)
        
        # Current time
        self.time_label = ctk.CTkLabel(self.status_bar, text="", font=ctk.CTkFont(size=11))
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        # Update time
        self.update_time()
        
    def update_time(self):
        """Update current time in status bar"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
        
    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        # Simple color adjustment for hover effects
        return color
        
    # Event Handlers
    def on_language_change(self):
        """Handle language change"""
        new_lang = self.lang_var.get()
        if new_lang != self.current_language:
            self.current_language = new_lang
            self.shadow.set_preferred_language(new_lang)
            
            lang_name = self.shadow.multilingual_manager.get_language_info(new_lang)['name']
            self.update_status(f"Language changed to {lang_name}")
            
            # Update status bar
            self.status_text.configure(
                text=f"🟢 Shadow AI is ready | {lang_name} | Voice: Available"
            )
            
    def toggle_listening(self):
        """Toggle voice listening state"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Start voice listening"""
        self.is_listening = True
        self.voice_button.configure(
            text="⏹️ Stop Listening", 
            fg_color="#FF6347",
            hover_color="#FF4500"
        )
        self.voice_status.configure(text="🎤 Listening... Speak now")
        self.update_voice_visualization(True)
        
        # Start listening in background thread
        threading.Thread(target=self.listen_loop, daemon=True).start()
        
    def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.voice_button.configure(
            text="🎤 Start Listening",
            fg_color="#2E8B57", 
            hover_color="#3CB371"
        )
        self.voice_status.configure(text="🎤 Ready to listen...")
        self.update_voice_visualization(False)
        
    def listen_loop(self):
        """Background listening loop"""
        async def async_listen():
            while self.is_listening:
                try:
                    text, lang = await self.shadow.listen_multilingual()
                    if text:
                        self.add_voice_activity(f"You ({lang}): {text}")
                        
                        # Process and get response
                        response = await self.shadow.process_multilingual_query(text, lang)
                        self.add_voice_activity(f"Shadow ({lang}): {response}")
                        
                        # Speak response
                        await self.shadow.speak_multilingual(response, lang)
                        
                except Exception as e:
                    self.add_voice_activity(f"Error: {str(e)}")
                    
                await asyncio.sleep(0.1)
                
        asyncio.run(async_listen())
        
    def test_voice(self):
        """Test voice synthesis"""
        test_messages = {
            'ur': 'السلام علیکم! یہ شاڈو AI کی آواز کا ٹیسٹ ہے۔',
            'ps': 'سلام! دا د شاڈو AI د غږ ازموینه ده۔',
            'en': 'Hello! This is a voice test of Shadow AI.'
        }
        
        message = test_messages.get(self.current_language, test_messages['ur'])
        
        async def async_speak():
            await self.shadow.speak_multilingual(message, self.current_language)
            self.add_voice_activity(f"Voice test: {message}")
            
        threading.Thread(target=lambda: asyncio.run(async_speak()), daemon=True).start()
        
    def send_chat_message(self, event=None):
        """Send chat message"""
        message = self.chat_input.get().strip()
        if not message:
            return
            
        self.chat_input.delete(0, tk.END)
        self.add_chat_message("You", message, "user")
        
        # Process message in background
        threading.Thread(target=self.process_chat_message, args=(message,), daemon=True).start()
        
    def process_chat_message(self, message):
        """Process chat message in background"""
        async def async_process():
            # Detect language
            lang = await self.shadow.multilingual_manager.detect_language(message)
            
            # Get response
            response = await self.shadow.process_multilingual_query(message, lang)
            self.add_chat_message("Shadow AI", response, "ai")
            
        asyncio.run(async_process())
        
    def add_chat_message(self, sender, message, msg_type):
        """Add message to chat display"""
        self.root.after(0, lambda: self._add_chat_message_threadsafe(sender, message, msg_type))
        
    def _add_chat_message_threadsafe(self, sender, message, msg_type):
        """Thread-safe chat message addition"""
        self.chat_display.configure(state="normal")
        
        # Configure tags for different message types
        if not self.chat_display.tag_names():
            self.chat_display.tag_config("user", foreground="#87CEEB")
            self.chat_display.tag_config("ai", foreground="#90EE90")
            self.chat_display.tag_config("bold", font=ctk.CTkFont(weight="bold"))
            
        # Add message
        self.chat_display.insert(tk.END, f"{sender}: ", "bold")
        self.chat_display.insert(tk.END, f"{message}\n\n", msg_type)
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.configure(state="disabled")
        
    def add_voice_activity(self, activity):
        """Add voice activity to log"""
        self.root.after(0, lambda: self._add_voice_activity_threadsafe(activity))
        
    def _add_voice_activity_threadsafe(self, activity):
        """Thread-safe voice activity addition"""
        self.voice_log.configure(state="normal")
        self.voice_log.insert(tk.END, f"{activity}\n")
        self.voice_log.see(tk.END)
        self.voice_log.configure(state="disabled")
        
    def update_voice_visualization(self, active):
        """Update voice visualization"""
        def update():
            if active:
                # Generate random voice data for visualization
                new_data = np.random.randn(100) * 0.5
                self.voice_data = new_data
                self.line.set_ydata(new_data)
                self.canvas.draw_idle()
            else:
                # Clear visualization
                self.line.set_ydata(np.zeros(100))
                self.canvas.draw_idle()
                
        self.root.after(0, update)
        
    def update_status(self, message):
        """Update status message"""
        self.root.after(0, lambda: self.status_label.configure(text=message))
        
    def process_messages(self):
        """Process messages from queue"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                # Process message if needed
                pass
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_messages)
            
    # Automation Methods
    def show_system_info(self):
        """Show system information"""
        async def async_show():
            if self.shadow.automation:
                result = await self.shadow.automation.automate("system_info", {})
                if result.get("success"):
                    info = result
                    self.add_chat_message("System", f"CPU: {info.get('cpu', {}).get('usage_percent', 0)}% | Memory: {info.get('memory', {}).get('used_percent', 0)}%", "ai")
                    
        threading.Thread(target=lambda: asyncio.run(async_show()), daemon=True).start()
        
    def open_task_manager(self):
        """Open task manager"""
        self.run_automation_command("open_app", {"name": "Task Manager"})
        
    def open_documents(self):
        """Open documents folder"""
        self.run_automation_command("open_file", {"path": "Documents"})
        
    def open_browser(self):
        """Open web browser"""
        self.run_automation_command("open_app", {"name": "chrome"})
        
    def list_files(self):
        """List files in specified path"""
        path = self.file_path.get().strip() or "."
        self.run_automation_command("list_files", {"path": path})
        
    def open_file(self):
        """Open specified file"""
        path = self.file_path.get().strip()
        if path:
            self.run_automation_command("open_file", {"path": path})
            
    def run_automation_command(self, command, parameters):
        """Run automation command"""
        async def async_run():
            if self.shadow.automation:
                result = await self.shadow.automation.automate(command, parameters)
                if result.get("success"):
                    self.add_chat_message("Automation", result.get("message", "Command executed"), "ai")
                else:
                    self.add_chat_message("Automation", f"Error: {result.get('error', 'Unknown error')}", "ai")
                    
        threading.Thread(target=lambda: asyncio.run(async_run()), daemon=True).start()
        
    def change_theme(self):
        """Change application theme"""
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
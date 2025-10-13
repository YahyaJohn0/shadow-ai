# graphical_installer.py
"""
Graphical Installer for Shadow AI - Professional installation experience
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import os
import shutil
import sys
from pathlib import Path
import threading
import time

class ShadowAInstaller:
    """Graphical installer for Shadow AI application"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        
        # Installation variables
        self.install_path = ""
        self.create_desktop_shortcut = True
        self.create_start_menu_shortcut = True
        self.launch_after_install = True
        
        # Setup GUI
        self.setup_gui()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Shadow AI Setup")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Center window
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
        """Setup the installer GUI"""
        # Create main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create notebook for different pages
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create pages
        self.create_welcome_page()
        self.create_license_page()
        self.create_installation_path_page()
        self.create_components_page()
        self.create_installation_page()
        self.create_finish_page()
        
        # Disable all tabs except first
        self.disable_tabs()
        
    def create_welcome_page(self):
        """Create welcome page"""
        self.welcome_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.welcome_frame, text="Welcome")
        
        # Welcome content
        welcome_content = ctk.CTkFrame(self.welcome_frame, fg_color="transparent")
        welcome_content.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(welcome_content, fg_color="transparent")
        title_frame.pack(pady=(0, 30))
        
        ctk.CTkLabel(
            title_frame, 
            text="🤖", 
            font=ctk.CTkFont(size=60)
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Shadow AI",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Intelligent Multilingual Assistant",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        ).pack()
        
        # Features
        features_frame = ctk.CTkFrame(welcome_content, fg_color="transparent")
        features_frame.pack(fill=tk.X, pady=20)
        
        features = [
            "🎯 Multilingual Support (Urdu, Pashto, English)",
            "🎤 Voice Recognition & Synthesis", 
            "💬 Natural Language Processing",
            "🖥️ Computer Automation",
            "📁 File Management",
            "🌐 Web Search Integration",
            "⏰ Smart Reminders",
            "🔒 Local & Private"
        ]
        
        for feature in features:
            feature_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_frame.pack(fill=tk.X, pady=2)
            ctk.CTkLabel(
                feature_frame, 
                text=feature,
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w")
        
        # System requirements
        req_frame = ctk.CTkFrame(welcome_content)
        req_frame.pack(fill=tk.X, pady=20)
        
        ctk.CTkLabel(
            req_frame,
            text="System Requirements:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        requirements = [
            "• Windows 10/11 (64-bit)",
            "• 4GB RAM minimum, 8GB recommended", 
            "• 500MB free disk space",
            "• Microphone (for voice features)",
            "• Internet connection (optional)"
        ]
        
        for req in requirements:
            ctk.CTkLabel(req_frame, text=req).pack(anchor="w")
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(welcome_content, fg_color="transparent")
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        ctk.CTkButton(
            nav_frame,
            text="Next >",
            command=lambda: self.notebook.select(1),
            width=120,
            height=35
        ).pack(side=tk.RIGHT)
        
    def create_license_page(self):
        """Create license agreement page"""
        self.license_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.license_frame, text="License")
        
        # License content
        license_content = ctk.CTkFrame(self.license_frame, fg_color="transparent")
        license_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ctk.CTkLabel(
            license_content,
            text="License Agreement",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 10))
        
        # License text
        license_text = """
SHADOW AI END USER LICENSE AGREEMENT

1. GRANT OF LICENSE
This agreement grants you the right to install and use Shadow AI on your personal computer.

2. RESTRICTIONS
You may not:
- Reverse engineer, decompile, or disassemble the software
- Redistribute the software without permission
- Use the software for illegal purposes

3. PRIVACY
Shadow AI operates locally on your computer. Your conversations and data remain on your device.

4. DISCLAIMER
This software is provided "as is" without warranties of any kind.

By clicking "I Agree", you accept the terms of this agreement.
"""
        
        license_scroll = ctk.CTkScrollableFrame(license_content)
        license_scroll.pack(fill=tk.BOTH, expand=True, pady=10)
        
        license_label = ctk.CTkLabel(
            license_scroll,
            text=license_text,
            font=ctk.CTkFont(size=12),
            justify=tk.LEFT,
            wraplength=700
        )
        license_label.pack(anchor="w", padx=10, pady=10)
        
        # Agreement checkbox
        self.agree_var = tk.BooleanVar()
        agree_check = ctk.CTkCheckBox(
            license_content,
            text="I accept the license agreement",
            variable=self.agree_var,
            command=self.on_license_agree
        )
        agree_check.pack(anchor="w", pady=10)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(license_content, fg_color="transparent")
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        ctk.CTkButton(
            nav_frame,
            text="< Back",
            command=lambda: self.notebook.select(0),
            width=120,
            height=35
        ).pack(side=tk.LEFT)
        
        self.license_next_btn = ctk.CTkButton(
            nav_frame,
            text="Next >",
            command=lambda: self.notebook.select(2),
            width=120,
            height=35,
            state="disabled"
        )
        self.license_next_btn.pack(side=tk.RIGHT)
        
    def create_installation_path_page(self):
        """Create installation path selection page"""
        self.path_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.path_frame, text="Installation Location")
        
        # Path content
        path_content = ctk.CTkFrame(self.path_frame, fg_color="transparent")
        path_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ctk.CTkLabel(
            path_content,
            text="Choose Install Location",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # Default installation path
        default_path = os.path.join(os.environ['PROGRAMFILES'], 'Shadow AI')
        self.install_path = default_path
        
        # Path selection frame
        path_selection_frame = ctk.CTkFrame(path_content)
        path_selection_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(
            path_selection_frame,
            text="Install Shadow AI to:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        path_input_frame = ctk.CTkFrame(path_selection_frame, fg_color="transparent")
        path_input_frame.pack(fill=tk.X, pady=5)
        
        self.path_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=tk.StringVar(value=default_path),
            font=ctk.CTkFont(size=12)
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            path_input_frame,
            text="Browse...",
            command=self.browse_install_path,
            width=80
        ).pack(side=tk.RIGHT)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(path_content, fg_color="transparent")
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        ctk.CTkButton(
            nav_frame,
            text="< Back",
            command=lambda: self.notebook.select(1),
            width=120,
            height=35
        ).pack(side=tk.LEFT)
        
        ctk.CTkButton(
            nav_frame,
            text="Next >",
            command=lambda: self.notebook.select(3),
            width=120,
            height=35
        ).pack(side=tk.RIGHT)
        
    def create_components_page(self):
        """Create components selection page"""
        self.components_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.components_frame, text="Components")
        
        # Components content
        components_content = ctk.CTkFrame(self.components_frame, fg_color="transparent")
        components_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ctk.CTkLabel(
            components_content,
            text="Select Components",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # Components list
        comp_frame = ctk.CTkFrame(components_content)
        comp_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Required components
        ctk.CTkLabel(
            comp_frame,
            text="Required Components:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        required_components = [
            "Core AI Engine",
            "Multilingual Support", 
            "Graphical Interface",
            "Voice Recognition Engine"
        ]
        
        for comp in required_components:
            comp_item = ctk.CTkFrame(comp_frame, fg_color="transparent")
            comp_item.pack(fill=tk.X, pady=2)
            ctk.CTkCheckBox(
                comp_item,
                text=comp,
                state="disabled",
                checkbox_width=20,
                checkbox_height=20
            ).pack(anchor="w")
        
        # Optional components
        ctk.CTkLabel(
            comp_frame,
            text="Optional Components:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(20, 5))
        
        self.create_desktop_var = tk.BooleanVar(value=True)
        self.create_start_menu_var = tk.BooleanVar(value=True)
        
        optional_components = [
            ("Create Desktop Shortcut", self.create_desktop_var),
            ("Create Start Menu Entry", self.create_start_menu_var),
        ]
        
        for text, var in optional_components:
            ctk.CTkCheckBox(
                comp_frame,
                text=text,
                variable=var,
                checkbox_width=20,
                checkbox_height=20
            ).pack(anchor="w", pady=2)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(components_content, fg_color="transparent")
        nav_frame.pack(fill=tk.X, pady=(20, 0))
        
        ctk.CTkButton(
            nav_frame,
            text="< Back",
            command=lambda: self.notebook.select(2),
            width=120,
            height=35
        ).pack(side=tk.LEFT)
        
        ctk.CTkButton(
            nav_frame,
            text="Next >",
            command=lambda: self.notebook.select(4),
            width=120,
            height=35
        ).pack(side=tk.RIGHT)
        
    def create_installation_page(self):
        """Create installation progress page - FIXED TYPO HERE"""
        self.install_frame = ctk.CTkFrame(self.notebook)  # FIXED: CTkFrame not CkFrame
        self.notebook.add(self.install_frame, text="Installing")
        
        # Installation content
        install_content = ctk.CTkFrame(self.install_frame, fg_color="transparent")
        install_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        ctk.CTkLabel(
            install_content,
            text="Installing Shadow AI",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(install_content)
        self.progress_bar.pack(fill=tk.X, pady=20)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            install_content,
            text="Preparing installation...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(anchor="w", pady=5)
        
        # Log output
        log_frame = ctk.CTkFrame(install_content)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        ctk.CTkLabel(
            log_frame,
            text="Installation Log:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=150,
            font=ctk.CTkFont(size=10, family="Consolas")
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.log_text.configure(state="disabled")
        
        # Navigation buttons
        self.install_nav_frame = ctk.CTkFrame(install_content, fg_color="transparent")
        self.install_nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_back_btn = ctk.CTkButton(
            self.install_nav_frame,
            text="< Back",
            command=lambda: self.notebook.select(3),
            width=120,
            height=35
        )
        
        self.install_next_btn = ctk.CTkButton(
            self.install_nav_frame,
            text="Next >",
            command=lambda: self.notebook.select(5),
            width=120,
            height=35,
            state="disabled"
        )
        
    def create_finish_page(self):
        """Create installation complete page"""
        self.finish_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.finish_frame, text="Complete")
        
        # Finish content
        finish_content = ctk.CTkFrame(self.finish_frame, fg_color="transparent")
        finish_content.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        
        # Success icon
        ctk.CTkLabel(
            finish_content, 
            text="✅", 
            font=ctk.CTkFont(size=60)
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            finish_content,
            text="Installation Complete!",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            finish_content,
            text="Shadow AI has been successfully installed on your computer.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=(0, 30))
        
        # Options frame
        options_frame = ctk.CTkFrame(finish_content)
        options_frame.pack(fill=tk.X, pady=20)
        
        self.launch_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Launch Shadow AI now",
            variable=self.launch_var,
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=15)
        
        # Final buttons
        button_frame = ctk.CTkFrame(finish_content, fg_color="transparent")
        button_frame.pack(fill=tk.X, pady=(30, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Finish",
            command=self.finish_installation,
            width=120,
            height=40,
            fg_color="#2E8B57",
            hover_color="#3CB371"
        ).pack(side=tk.RIGHT)
        
    def disable_tabs(self):
        """Disable all tabs except the first one"""
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
            
    def enable_next_tab(self, current_index):
        """Enable the next tab"""
        if current_index < self.notebook.index("end") - 1:
            self.notebook.tab(current_index + 1, state="normal")
            
    def on_license_agree(self):
        """Enable next button when license is agreed"""
        if self.agree_var.get():
            self.license_next_btn.configure(state="normal")
        else:
            self.license_next_btn.configure(state="disabled")
            
    def browse_install_path(self):
        """Browse for installation path"""
        path = filedialog.askdirectory(
            title="Select Installation Directory",
            mustexist=False
        )
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)
            self.install_path = path
            
    def log_message(self, message):
        """Add message to installation log"""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update()
        
    def update_progress(self, value, status, detail=""):
        """Update progress bar and status"""
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
        if detail:
            self.detail_label.configure(text=detail)
        self.root.update()
        
    def start_installation(self):
        """Start the installation process"""
        # Show navigation buttons
        self.install_back_btn.pack(side=tk.LEFT)
        self.install_next_btn.pack(side=tk.RIGHT)
        
        # Disable back button during installation
        self.install_back_btn.configure(state="disabled")
        
        # Start installation in separate thread
        thread = threading.Thread(target=self.install_thread)
        thread.daemon = True
        thread.start()
        
    def install_thread(self):
        """Installation process in separate thread"""
        try:
            self.update_progress(0.1, "Preparing installation...")
            self.log_message("Starting Shadow AI installation...")
            
            # Create installation directory
            self.update_progress(0.2, "Creating directories...")
            install_dir = Path(self.install_path)
            install_dir.mkdir(parents=True, exist_ok=True)
            self.log_message(f"Created installation directory: {install_dir}")
            
            # Simulate file copy
            self.update_progress(0.6, "Copying application files...")
            time.sleep(2)
            self.log_message("Copied core application files")
            
            # Create shortcuts
            if self.create_desktop_var.get():
                self.update_progress(0.8, "Creating desktop shortcut...")
                self.log_message("Created desktop shortcut")
                
            if self.create_start_menu_var.get():
                self.update_progress(0.9, "Creating start menu entry...")
                self.log_message("Created start menu entry")
            
            # Finalize installation
            self.update_progress(1.0, "Installation complete!")
            self.log_message("Shadow AI installation completed successfully!")
            
            # Enable next button
            self.install_next_btn.configure(state="normal")
            
        except Exception as e:
            self.log_message(f"Installation error: {str(e)}")
            messagebox.showerror("Installation Error", f"Failed to install Shadow AI: {str(e)}")
            
    def finish_installation(self):
        """Finish installation and optionally launch application"""
        if self.launch_var.get():
            messagebox.showinfo(
                "Shadow AI", 
                "Installation completed successfully!\n\n"
                "Shadow AI would launch now in a real installation."
            )
        
        self.root.destroy()
        
    def run(self):
        """Run the installer"""
        # Bind tab changes to enable next tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.root.mainloop()
        
    def on_tab_changed(self, event):
        """Handle tab changes"""
        current_tab = self.notebook.index("current")
        
        # Enable next tab when moving forward
        if current_tab < self.notebook.index("end") - 1:
            self.notebook.tab(current_tab + 1, state="normal")
            
        # Start installation when reaching installation tab
        if current_tab == 4:  # Installation tab
            self.start_installation()

def main():
    """Main function to run the installer"""
    installer = ShadowAInstaller()
    installer.run()

if __name__ == "__main__":
    main()
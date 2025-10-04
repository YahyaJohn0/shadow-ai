# minimal_installer.py
"""
Minimal installer for quick testing - Much faster build
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import os
import shutil
import sys
from pathlib import Path

class MinimalInstaller:
    """Minimal installer for quick testing"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_gui()
        
    def setup_window(self):
        """Setup window"""
        self.root.title("Shadow AI - Quick Install")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        ctk.set_appearance_mode("dark")
        self.center_window()
        
    def center_window(self):
        """Center window"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_gui(self):
        """Setup minimal GUI"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="🤖 Shadow AI",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Quick Installation",
            font=ctk.CTkFont(size=16)
        ).pack(pady=(0, 20))
        
        # Progress area
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)
        
        self.status_label = ctk.CTkLabel(main_frame, text="Ready to install...")
        self.status_label.pack(pady=5)
        
        # Install button
        ctk.CTkButton(
            main_frame,
            text="Install Now",
            command=self.install,
            width=200,
            height=40,
            fg_color="#2E8B57"
        ).pack(pady=20)
        
    def install(self):
        """Quick installation"""
        self.progress.start()
        self.status_label.configure(text="Installing...")
        
        try:
            # Simple file copy (for demo)
            install_dir = Path.home() / "ShadowAI"
            install_dir.mkdir(exist_ok=True)
            
            # Create a simple launcher
            launcher_content = '''print("Shadow AI - Installation Complete!")
input("Press Enter to exit...")
'''
            
            (install_dir / "launcher.py").write_text(launcher_content)
            
            self.progress.stop()
            self.status_label.configure(text="Installation Complete!")
            
            messagebox.showinfo(
                "Success", 
                "Shadow AI has been installed!\n\n"
                "Location: " + str(install_dir)
            )
            
        except Exception as e:
            self.progress.stop()
            self.status_label.configure(text="Installation Failed!")
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
            
    def run(self):
        """Run installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = MinimalInstaller()
    installer.run()
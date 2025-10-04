# run_shadow_gui.py
"""
Main launcher for Shadow AI with GUI - Enhanced for distribution
"""

import sys
import os
import asyncio
import threading
import traceback
from pathlib import Path

def setup_environment():
    """Setup environment for distributed application"""
    # Add project root to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Create necessary directories
    data_dir = current_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    logs_dir = current_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Set environment variables
    os.environ['SHADOW_AI_HOME'] = str(current_dir)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    required_packages = [
        'customtkinter',
        'matplotlib',
        'PIL',
        'speech_recognition',
        'pyaudio',
        'edge_tts',
        'pyttsx3',
        'psutil',
        'pyautogui',
        'pyperclip',
        'langdetect'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_deps.append(package)
    
    return missing_deps

def show_error_dialog(message):
    """Show error dialog for missing dependencies"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        messagebox.showerror(
            "Shadow AI - Missing Dependencies",
            f"{message}\n\nPlease install missing packages and restart the application."
        )
        root.destroy()
    except:
        print(f"Error: {message}")

def main():
    """Main application entry point"""
    try:
        print("🚀 Starting Shadow AI...")
        setup_environment()
        
        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            error_msg = f"Missing dependencies: {', '.join(missing_deps)}"
            show_error_dialog(error_msg)
            return
        
        # Import after environment setup
        from main import Shadow
        from shadow_core.main_window import ShadowGUI
        
        print("✅ Shadow AI initialized successfully!")
        print("🌍 Supported languages: Urdu, Pashto, English")
        print("🎯 Capabilities: Voice, Chat, Automation, Multilingual")
        
        # Initialize Shadow AI agent
        shadow_agent = Shadow()
        
        # Start GUI
        print("🖥️  Launching GUI...")
        app = ShadowGUI(shadow_agent)
        app.run()
        
    except Exception as e:
        error_msg = f"Failed to start Shadow AI: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        show_error_dialog(error_msg)

if __name__ == "__main__":
    main()
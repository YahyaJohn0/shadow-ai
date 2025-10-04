# shadow_ai_optimized.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import os

current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

block_cipher = None

# EXCLUDES - Reduce build time by excluding unnecessary modules
excludes = [
    'tkinter', 'tcl', 'tk', '_tkinter', 'Tkinter', 'Tkconstants',
    'test', 'unittest', 'pytest', 'distutils',
    'setuptools', 'pip', 'wheel', 'certifi',
    'notebook', 'jupyter', 'ipykernel', 'ipython',
    'matplotlib.tests', 'numpy.tests', 'PIL._tkinter_finder',
    'lib2to3', 'ensurepip', 'idlelib', 'pydoc_data',
    'multiprocessing', 'concurrent.futures',
]

# HIDDEN IMPORTS - Only include what's absolutely necessary
hiddenimports = [
    # CustomTkinter and GUI
    'customtkinter',
    'matplotlib.backends.backend_tkagg',
    'PIL.Image', 'PIL.ImageTk', 'PIL.ImageOps',
    
    # Voice and Audio
    'speech_recognition', 'pyaudio', 'wave', 'audioop',
    'edge_tts', 'pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.dummy',
    
    # Core AI and Automation
    'psutil', 'pyautogui', 'pyperclip', 'selenium', 'webdriver_manager',
    
    # Language Processing
    'langdetect',
    
    # Networking and Web
    'aiohttp', 'requests', 'urllib3', 'ssl', 'http',
    
    # Data Processing
    'numpy', 'pandas', 'json', 'xml', 'csv',
    
    # System and OS
    'os', 'sys', 'pathlib', 'platform', 'subprocess', 'shutil',
    'ctypes', 'win32api', 'win32con', 'win32gui',
]

a = Analysis(
    ['run_shadow_gui.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        # Only include essential data files
        ('data', 'data'),
        ('config.py', '.'),
        ('.env', '.'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Use UPX compression to reduce executable size
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ShadowAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols
    upx=True,    # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
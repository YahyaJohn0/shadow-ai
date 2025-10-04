# shadow_ai.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import os

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

block_cipher = None

# Include all necessary data files and hidden imports
a = Analysis(
    ['run_shadow_gui.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        # Include data directory
        ('data', 'data'),
        # Include config files
        ('config.py', '.'),
        ('.env', '.'),
        # Include all Python files in shadow_core
        (str(current_dir / 'shadow_core' / '*.py'), 'shadow_core'),
        # Include all Python files in shadow_gui
        (str(current_dir / 'shadow_gui' / '*.py'), 'shadow_gui'),
    ],
    hiddenimports=[
        'customtkinter',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'PIL',
        'PIL._tkinter_finder',
        'speech_recognition',
        'pyaudio',
        'edge_tts',
        'pyttsx3',
        'psutil',
        'pyautogui',
        'pyperclip',
        'selenium',
        'webdriver_manager',
        'langdetect',
        'asyncio',
        'aiohttp',
        'sqlite3',
        'json',
        're',
        'threading',
        'queue',
        'time',
        'datetime',
        'os',
        'sys',
        'pathlib',
        'numpy',
        'platform',
        'subprocess',
        'webbrowser',
        'urllib',
        'ssl',
        'http',
        'email',
        'base64',
        'hashlib',
        'hmac',
        'socket',
        'selectors',
        'concurrent',
        'ctypes',
        'win32api',  # For Windows
        'win32con',  # For Windows
        'win32gui',  # For Windows
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # We use customtkinter instead
        'test',
        'unittest',
        'pytest',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add necessary DLLs and binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Create executable
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
    strip=False,
    upx=True,  # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # We'll create this
)
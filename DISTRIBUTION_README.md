# Shadow AI - Distribution Guide

## 📦 Creating Installers

### Windows
1. Install Inno Setup from https://jrsoftware.org/isdl.php
2. Run: `python create_installer.py`
3. The installer will be created in the `installer` folder

### macOS
1. Run: `python create_mac_app.py`
2. The .app bundle will be created in the `dist` folder
3. You can codesign and notarize for distribution

### Linux
1. Run: `python create_linux_desktop.py`
2. Run the install script: `./dist/install.sh`

## 🔧 Quick Build (All Platforms)
Run: `python build_all.py`

## 📋 Prerequisites
- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Platform-specific tools (see above)

## 🎯 Features Included
- ✅ Multilingual support (Urdu, Pashto, English)
- ✅ Voice recognition and synthesis
- ✅ GUI interface
- ✅ File system automation
- ✅ Web search capabilities
- ✅ Reminder system
- ✅ Computer control features

## 🔒 Security Notes
- The application runs locally
- No data is sent to external servers
- All conversations are stored locally
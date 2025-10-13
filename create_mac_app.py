# create_mac_app.py
"""
Create macOS .app bundle for Shadow AI
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_mac_app():
    """Create macOS application bundle"""
    print("🍎 Creating macOS Application Bundle...")
    
    current_dir = Path(__file__).parent
    dist_dir = current_dir / 'dist'
    app_name = "Shadow AI.app"
    app_path = dist_dir / app_name
    contents_path = app_path / "Contents"
    macos_path = contents_path / "MacOS"
    resources_path = contents_path / "Resources"
    
    # Clean previous app
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # Create directory structure
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Build with PyInstaller for macOS
        print("📦 Building executable...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',  # No terminal window
            '--name=Shadow AI',
            '--icon=assets/icon.icns',
            'run_shadow_gui.py'
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
        
        # Move executable to app bundle
        executable_src = dist_dir / "Shadow AI" / "Shadow AI"
        executable_dest = macos_path / "Shadow AI"
        
        if executable_src.exists():
            shutil.copy2(executable_src, executable_dest)
            
            # Make executable
            os.chmod(executable_dest, 0o755)
        else:
            print(f"❌ Executable not found: {executable_src}")
            return False
        
        # Create Info.plist
        create_info_plist(contents_path, current_dir)
        
        # Copy resources
        copy_resources(current_dir, resources_path)
        
        print("✅ macOS Application Bundle created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create macOS app: {e}")
        return False

def create_info_plist(contents_path, current_dir):
    """Create Info.plist for macOS app"""
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>Shadow AI</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundleIdentifier</key>
    <string>com.shadowai.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Shadow AI</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 Shadow AI Team. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>"""
    
    plist_file = contents_path / "Info.plist"
    with open(plist_file, 'w', encoding='utf-8') as f:
        f.write(plist_content)

def copy_resources(current_dir, resources_path):
    """Copy resource files to app bundle"""
    # Copy icon
    icon_src = current_dir / "assets" / "icon.icns"
    if icon_src.exists():
        shutil.copy2(icon_src, resources_path / "icon.icns")
    
    # Copy data directory
    data_src = current_dir / "data"
    data_dest = resources_path / "data"
    if data_src.exists():
        shutil.copytree(data_src, data_dest, dirs_exist_ok=True)

if __name__ == "__main__":
    if sys.platform != "darwin":
        print("❌ This script is for macOS only")
        sys.exit(1)
    
    success = create_mac_app()
    if success:
        print("\n🎊 macOS Application Bundle ready!")
        print("📦 The app can be found in the 'dist' folder")
    else:
        print("\n❌ Failed to create macOS app")
        sys.exit(1)
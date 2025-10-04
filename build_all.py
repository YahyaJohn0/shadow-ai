# build_all.py
"""
Build Shadow AI for all platforms
"""

import os
import sys
import platform
from pathlib import Path

def build_for_current_platform():
    """Build for current platform"""
    current_platform = platform.system().lower()
    
    print(f"🏗️  Building Shadow AI for {current_platform.capitalize()}...")
    
    if current_platform == "windows":
        from create_installer import create_installer
        return create_installer()
    
    elif current_platform == "darwin":
        from create_mac_app import create_mac_app
        return create_mac_app()
    
    elif current_platform == "linux":
        from create_linux_desktop import create_linux_package
        return create_linux_package()
    
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return False

def main():
    """Main build function"""
    print("🚀 Shadow AI Build System")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully!")
    
    # Build for current platform
    success = build_for_current_platform()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("📦 Check the 'dist' or 'installer' folder for your package")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
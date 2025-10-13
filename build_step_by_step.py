# build_step_by_step.py
"""
Simple step-by-step build process
"""

import os
import subprocess
import sys
from pathlib import Path

def run_step(command, description):
    """Run a build step"""
    print(f"\n🔧 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Success")
            return True
        else:
            print(f"   ❌ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Shadow AI - Step by Step Build")
    print("=" * 50)
    
    # Step 1: Build main application
    if not run_step([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--windowed',
        '--name=ShadowAI',
        '--icon=assets/icon.ico',
        'run_shadow_gui.py'
    ], "Building main application"):
        print("\n❌ Main application build failed!")
        return
    
    # Step 2: Build installer
    if not run_step([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--windowed', 
        '--name=ShadowAI_Setup',
        '--icon=assets/icon.ico',
        'graphical_installer.py'
    ], "Building graphical installer"):
        print("\n⚠️  Installer build failed, but main app is ready")
    
    print("\n🎉 Build completed!")
    print("📁 Check 'dist' folder for:")
    print("   - ShadowAI/ (main application)")
    print("   - ShadowAI_Setup.exe (installer)")

if __name__ == "__main__":
    main()
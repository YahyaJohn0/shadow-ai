# build_with_installer.py
"""
Build Shadow AI with graphical installer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_complete_package():
    """Build complete Shadow AI package with installer"""
    print("🏗️ Building Shadow AI Complete Package...")
    
    current_dir = Path(__file__).parent
    
    try:
        # Step 1: Build the main application
        print("📦 Building main application...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--windowed',
            '--name=ShadowAI',
            '--icon=assets/icon.ico',
            'run_shadow_gui.py'
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode != 0:
            print(f"❌ Application build failed: {result.stderr}")
            return False
        
        # Step 2: Build the installer
        print("🔧 Building graphical installer...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean', 
            '--noconfirm',
            '--onefile',
            '--name=ShadowAI_Setup',
            '--icon=assets/icon.ico',
            'graphical_installer.py'
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode != 0:
            print(f"❌ Installer build failed: {result.stderr}")
            return False
        
        # Step 3: Create distribution package
        print("📁 Creating distribution package...")
        dist_dir = current_dir / "dist"
        package_dir = current_dir / "ShadowAI_Package"
        
        if package_dir.exists():
            shutil.rmtree(package_dir)
        package_dir.mkdir()
        
        # Copy installer
        installer_src = dist_dir / "ShadowAI_Setup.exe"
        installer_dest = package_dir / "Setup_ShadowAI.exe"
        if installer_src.exists():
            shutil.copy2(installer_src, installer_dest)
        
        # Copy README
        readme_content = """
Shadow AI - Installation Guide

1. Run "Setup_ShadowAI.exe" as Administrator
2. Follow the installation wizard
3. Launch Shadow AI from desktop or start menu

Features:
• Multilingual AI Assistant (Urdu, Pashto, English)
• Voice Recognition & Synthesis
• Computer Automation
• File Management
• Web Search Integration

System Requirements:
• Windows 10/11 (64-bit)
• 4GB RAM minimum
• 500MB free disk space
• Microphone (for voice features)

Support: Contact support@shadow-ai.com
"""
        
        with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("✅ Package created successfully!")
        print(f"📦 Distribution package: {package_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    success = build_complete_package()
    if success:
        print("\n🎉 Shadow AI distribution package is ready!")
        print("🚀 Users can run 'Setup_ShadowAI.exe' to install")
    else:
        print("\n❌ Failed to create distribution package")
        sys.exit(1)
# create_linux_desktop.py
"""
Create Linux desktop entry and package for Shadow AI
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_linux_package():
    """Create Linux package with desktop entry"""
    print("🐧 Creating Linux Package...")
    
    current_dir = Path(__file__).parent
    dist_dir = current_dir / 'dist'
    
    try:
        # Build with PyInstaller for Linux
        print("📦 Building executable...")
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            '--name=shadow-ai',
            '--add-data=assets:assets',
            '--add-data=data:data',
            'run_shadow_gui.py'
        ], capture_output=True, text=True, cwd=current_dir)
        
        if result.returncode != 0:
            print(f"❌ PyInstaller failed: {result.stderr}")
            return False
        
        # Create desktop entry
        create_desktop_entry(current_dir, dist_dir)
        
        # Create install script
        create_install_script(current_dir, dist_dir)
        
        print("✅ Linux package created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create Linux package: {e}")
        return False

def create_desktop_entry(current_dir, dist_dir):
    """Create .desktop file for Linux"""
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Shadow AI
Comment=Intelligent Multilingual AI Assistant
Exec={dist_dir}/shadow-ai/shadow-ai
Icon={current_dir}/assets/icon.png
Categories=Office;Education;Utility;
Terminal=false
StartupWMClass=ShadowAI
"""
    
    desktop_file = dist_dir / "shadow-ai.desktop"
    with open(desktop_file, 'w', encoding='utf-8') as f:
        f.write(desktop_content)
    
    # Make executable
    os.chmod(desktop_file, 0o755)

def create_install_script(current_dir, dist_dir):
    """Create installation script for Linux"""
    install_script = f"""#!/bin/bash
# Shadow AI Installation Script

echo "Installing Shadow AI..."

# Copy application files
sudo cp -r {dist_dir}/shadow-ai /opt/shadow-ai

# Copy desktop entry
sudo cp {dist_dir}/shadow-ai.desktop /usr/share/applications/

# Create symlink in /usr/local/bin
sudo ln -sf /opt/shadow-ai/shadow-ai /usr/local/bin/shadow-ai

# Set permissions
sudo chmod +x /opt/shadow-ai/shadow-ai

echo "Installation complete! You can now run 'shadow-ai' from terminal or find it in your applications menu."
"""
    
    script_file = dist_dir / "install.sh"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    os.chmod(script_file, 0o755)

if __name__ == "__main__":
    if sys.platform == "win32":
        print("❌ This script is for Linux only")
        sys.exit(1)
    
    success = create_linux_package()
    if success:
        print("\n🎊 Linux package ready!")
        print("📦 Run 'install.sh' in the 'dist' folder to install")
    else:
        print("\n❌ Failed to create Linux package")
        sys.exit(1)
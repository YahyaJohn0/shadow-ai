# ci_build.py
"""
Build script optimized for CI/CD environments
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def detect_ci_environment():
    """Detect CI environment and adjust build accordingly"""
    ci_vars = {
        'GITHUB_ACTIONS': 'GitHub Actions',
        'GITLAB_CI': 'GitLab CI',
        'TRAVIS': 'Travis CI',
        'CIRCLECI': 'CircleCI'
    }
    
    for var, name in ci_vars.items():
        if os.getenv(var):
            return name
    return 'Local'

def build_for_platform():
    """Build for current platform"""
    current_platform = platform.system().lower()
    ci_env = detect_ci_environment()
    
    print(f"🏗️  Building Shadow AI on {ci_env} ({current_platform})")
    
    # Platform-specific build commands
    if current_platform == 'windows':
        commands = [
            [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--windowed', '--name=ShadowAI', 'run_shadow_gui.py'],
            [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--onefile', '--windowed', '--name=ShadowAI_Setup', 'graphical_installer.py']
        ]
    elif current_platform == 'darwin':  # macOS
        commands = [
            [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--windowed', '--name=ShadowAI', '--icon=assets/icon.icns', 'run_shadow_gui.py']
        ]
    else:  # Linux
        commands = [
            [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', '--name=shadow-ai', 'run_shadow_gui.py']
        ]
    
    # Execute build commands
    for i, command in enumerate(commands):
        print(f"🔧 Step {i+1}/{len(commands)}: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print("✅ Success")
            else:
                print(f"❌ Failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("⏰ Timeout")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return True

def main():
    """Main CI build function"""
    print("🚀 Shadow AI - CI Build System")
    print("=" * 50)
    
    success = build_for_platform()
    
    if success:
        print("\n🎉 CI Build completed successfully!")
        print("📦 Artifacts available in 'dist' folder")
    else:
        print("\n❌ CI Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
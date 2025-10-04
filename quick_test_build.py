# quick_test_build.py
"""
Quick test build - Builds only the essentials
"""

import subprocess
import sys

def quick_build():
    print("🚀 Shadow AI - Quick Test Build")
    print("=" * 40)
    
    # Build just the main app quickly
    print("\n📦 Building main application only...")
    
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--windowed',
        '--name=ShadowAI_Test',
        'run_shadow_gui.py'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print("📁 Test application: dist/ShadowAI_Test/ShadowAI_Test.exe")
        print("💡 Run this file to test your application")
    else:
        print("❌ Build failed!")
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    quick_build()
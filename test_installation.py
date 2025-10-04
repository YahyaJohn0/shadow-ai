# test_installation.py
"""
Quick test to verify Shadow AI installation
"""

import sys
import os

def test_dependencies():
    """Test if all dependencies are available"""
    dependencies = [
        'customtkinter',
        'matplotlib', 
        'PIL',
        'speech_recognition',
        'pyaudio',
        'edge_tts',
        'pyttsx3',
        'psutil',
        'pyautogui',
        'pyperclip',
        'langdetect'
    ]
    
    print("🔍 Testing dependencies...")
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError as e:
            print(f"❌ {dep} - {e}")
            missing.append(dep)
    
    return missing

def test_imports():
    """Test if core modules can be imported"""
    print("\n🔍 Testing core modules...")
    
    try:
        from main import Shadow
        print("✅ shadow_core.main")
    except Exception as e:
        print(f"❌ shadow_core.main - {e}")
        return False
        
    try:
        from shadow_core.main_window import ShadowGUI
        print("✅ shadow_gui.main_window")
    except Exception as e:
        print(f"❌ shadow_gui.main_window - {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("🚀 Shadow AI Installation Test")
    print("=" * 40)
    
    # Test dependencies
    missing_deps = test_dependencies()
    
    # Test imports
    imports_ok = test_imports()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"✅ Dependencies: {len(missing_deps)} missing")
    print(f"✅ Core imports: {'OK' if imports_ok else 'FAILED'}")
    
    if not missing_deps and imports_ok:
        print("\n🎉 All tests passed! You can run Shadow AI.")
        print("💡 Run: python run_shadow_gui.py")
    else:
        print("\n❌ Some tests failed. Please install missing dependencies.")
# setup_gemini.py
import os
import sys
from dotenv import load_dotenv, set_key

def setup_gemini():
    """Quick setup for Gemini API"""
    print("🚀 Setting up Shadow AI with Google Gemini (Free API)...")
    print("=" * 60)
    
    # Load current .env
    load_dotenv()
    
    # Get Gemini API key
    current_key = os.getenv('GOOGLE_API_KEY', '')
    
    if not current_key or current_key == 'your_actual_gemini_api_key_here':
        print("🔑 To get your FREE Gemini API key:")
        print("1. Go to: https://aistudio.google.com/")
        print("2. Sign in with Google account")
        print("3. Click 'Get API key' in sidebar")
        print("4. Create API key and copy it")
        
        api_key = input("\n📝 Paste your Gemini API key here: ").strip()
        
        if api_key:
            # Update .env file
            set_key('.env', 'GOOGLE_API_KEY', api_key)
            set_key('.env', 'OFFLINE_MODE', 'false')
            set_key('.env', 'OPENAI_API_KEY', 'not_used')  # Disable OpenAI
            
            print("✅ Gemini API key saved!")
            print("✅ Set OFFLINE_MODE to false")
        else:
            print("❌ No API key provided")
            return False
    else:
        print(f"✅ Gemini API key found: {current_key[:10]}...")
        set_key('.env', 'OFFLINE_MODE', 'false')
        print("✅ Set OFFLINE_MODE to false")
    
    # Test Gemini installation
    print("\n🔧 Testing Gemini setup...")
    try:
        import google.generativeai
        print("✅ google-generativeai package is installed")
    except ImportError:
        print("❌ google-generativeai not installed")
        print("💡 Run: pip install google-generativeai")
        return False
    
    print("\n🎉 Setup complete! Shadow AI is ready with Gemini API")
    print("🤖 Features now available:")
    print("   • Intelligent GPT-like responses")
    print("   • Full multilingual support") 
    print("   • Messaging, scheduling, knowledge")
    print("   • Completely FREE API usage")
    
    return True

if __name__ == "__main__":
    if setup_gemini():
        print("\n🔄 Now restart Shadow AI:")
        print("python main.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
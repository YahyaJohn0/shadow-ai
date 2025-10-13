# setup_flash.py
import os
import sys
from dotenv import load_dotenv, set_key

def setup_gemini_flash():
    """Setup Shadow AI with Gemini 2.5 Flash"""
    print("🚀 SETUP: GEMINI 2.5 FLASH - FREE FOREVER")
    print("=" * 60)
    
    load_dotenv()
    
    print("🎯 Benefits of Gemini 2.5 Flash:")
    print("   • 🆓 COMPLETELY FREE forever")
    print("   • ⚡ Fastest response times")
    print("   • 🧠 Latest AI model from Google")
    print("   • 🌍 Multilingual support")
    print("   • 📊 1,500 free requests per day")
    print("   • 🔄 Multiple keys = more free requests!")
    print()
    
    print("🔑 Step 1: Get your FREE Gemini API key")
    print("   Visit: https://aistudio.google.com/")
    print("   Sign in with Google account")
    print("   Click 'Get API key'")
    print("   Create API key (starts with AIza...)")
    print()
    
    primary_key = input("📝 Paste your Gemini API key: ").strip()
    
    if not primary_key or not primary_key.startswith('AIza'):
        print("❌ Invalid API key. Should start with 'AIza'")
        return False
    
    # Save configuration
    set_key('.env', 'GOOGLE_API_KEY', primary_key)
    set_key('.env', 'OFFLINE_MODE', 'false')
    set_key('.env', 'OPENAI_API_KEY', 'not_used')
    
    print("✅ Primary API key saved!")
    
    # Ask for backup keys
    print("\n🔄 Optional: Add backup API keys (recommended)")
    print("   Create more free keys with different Google accounts")
    
    backup_count = 0
    for i in range(2, 5):
        backup_key = input(f"📝 Backup key {i-1} (or Enter to skip): ").strip()
        if backup_key and backup_key.startswith('AIza'):
            set_key('.env', f'GOOGLE_API_KEY_{i}', backup_key)
            backup_count += 1
        else:
            break
    
    print(f"\n✅ Setup complete!")
    print(f"✅ Saved {1 + backup_count} API keys")
    print(f"✅ Configured for Gemini 2.5 Flash")
    
    print(f"\n📊 Your free power:")
    total_requests = (1 + backup_count) * 1500
    print(f"   • Total free requests per day: {total_requests}")
    print(f"   • That's {total_requests // 24} requests per hour!")
    print(f"   • More than enough for personal use!")
    
    print("\n🚀 Next steps:")
    print("   1. pip install --upgrade google-generativeai")
    print("   2. python test_flash.py")
    print("   3. python main.py")
    
    return True

if __name__ == "__main__":
    if setup_gemini_flash():
        print("\n🎊 Your AI assistant is now powered by Gemini 2.5 Flash!")
        print("💫 Fast, free, and forever!")
    else:
        print("\n❌ Setup failed. Please try again.")
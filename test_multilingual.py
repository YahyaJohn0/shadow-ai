# test_multilingual.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.multilingual import MultilingualManager, UrduPashtoTranslator, MultilingualBrain

class MockBrain:
    async def ask(self, messages):
        # Simulate AI responses in different languages
        prompt = messages[0]["content"] if messages else ""
        
        if "Urdu" in prompt and "RESPONSE LANGUAGE: Urdu" in prompt:
            return "السلام علیکم! میں شاڈو AI ہوں۔ آپ کیسے مدد کر سکتا ہوں؟"
        elif "Pashto" in prompt and "RESPONSE LANGUAGE: Pashto" in prompt:
            return "سلام! زه شاڈو AI یم۔ تاسو څنګه مرسته کولی شم؟"
        else:
            return "Hello! I'm Shadow AI. How can I help you?"

async def test_multilingual_support():
    print("🌍 Testing Multilingual Support (Urdu, Pashto, English)")
    print("=" * 70)
    
    brain = MockBrain()
    multilingual_manager = MultilingualManager()
    translator = UrduPashtoTranslator(brain)
    multilingual_brain = MultilingualBrain(brain, multilingual_manager, translator)
    
    # Test language detection
    print("\n1. Testing Language Detection:")
    
    test_texts = [
        ("السلام علیکم", "ur"),
        ("سلام علیکم", "ps"), 
        ("Hello world", "en"),
        ("تاسو څنګه یاست؟", "ps"),
        ("How are you?", "en")
    ]
    
    for text, expected_lang in test_texts:
        detected_lang = await multilingual_manager.detect_language(text)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"   {status} '{text}' -> {detected_lang} (expected: {expected_lang})")
    
    # Test multilingual responses
    print("\n2. Testing Multilingual Responses:")
    
    test_queries = [
        ("Hello, how are you?", "en"),
        ("السلام علیکم، آپ کیسے ہیں؟", "ur"),
        ("سلام، تاسو څنګه یاست؟", "ps")
    ]
    
    for query, lang in test_queries:
        print(f"\n   Query ({lang}): {query}")
        response = await multilingual_brain.ask_multilingual(query, lang, lang)
        print(f"   Response: {response}")
    
    # Test language switching
    print("\n3. Testing Language Switching:")
    
    languages = ['ur', 'ps', 'en']
    for lang in languages:
        success = multilingual_manager.set_language(lang)
        lang_name = multilingual_manager.get_language_info(lang)['name']
        status = "✅" if success else "❌"
        print(f"   {status} Set language to: {lang_name}")
    
    # Test common phrases
    print("\n4. Testing Common Phrases:")
    
    phrases = ['greeting', 'thank_you', 'goodbye']
    for lang in ['ur', 'ps', 'en']:
        print(f"\n   {multilingual_manager.get_language_info(lang)['name']}:")
        for phrase in phrases:
            phrase_text = translator.get_common_phrase(phrase, lang)
            print(f"     {phrase}: {phrase_text}")
    
    print("\n" + "=" * 70)
    print("✅ Multilingual support test completed!")

async def main():
    await test_multilingual_support()
    
    print("\n🎯 Multilingual Features:")
    print("  • Urdu speech recognition and synthesis")
    print("  • Pashto speech recognition and synthesis") 
    print("  • English speech recognition and synthesis")
    print("  • Automatic language detection")
    print("  • Context-aware responses in each language")
    print("  • Cultural appropriateness")
    print("  • Urdu as default language")

if __name__ == "__main__":
    asyncio.run(main())
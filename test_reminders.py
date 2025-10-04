# test_reminders.py
"""
Test multilingual reminder functionality
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.multilingual_reminder import MultilingualReminderParser

class MockBrain:
    async def ask(self, messages):
        # Simulate AI responses for reminder parsing
        prompt = messages[0]["content"] if messages else ""
        
        if "Urdu" in prompt and "یاد" in prompt:
            return '''
            {
                "message": "میٹنگ",
                "time": null,
                "date": null, 
                "relative_minutes": 5,
                "relative_hours": 0,
                "relative_days": 0,
                "confidence": 0.96,
                "reasoning": "User wants reminder about meeting in 5 minutes"
            }
            '''
        elif "Pashto" in prompt and "یادونه" in prompt:
            return '''
            {
                "message": "پروژه",
                "time": null,
                "date": null,
                "relative_minutes": 0, 
                "relative_hours": 2,
                "relative_days": 0,
                "confidence": 0.94,
                "reasoning": "User wants project reminder in 2 hours"
            }
            '''
        else:
            return '''
            {
                "message": "Reminder",
                "time": null,
                "date": null,
                "relative_minutes": 60,
                "relative_hours": 0,
                "relative_days": 0,
                "confidence": 0.85,
                "reasoning": "General reminder"
            }
            '''

async def test_multilingual_reminders():
    print("⏰ Testing Multilingual Reminder System")
    print("=" * 70)
    
    brain = MockBrain()
    parser = MultilingualReminderParser(brain)
    
    # Test cases for different languages
    test_cases = [
        ("مجھے 5 منٹ بعد میٹنگ کی یاد دہانی کرو", "ur"),
        ("ما ته په 2 گھنٹو کې د پروژې یادونه راکړه", "ps"),
        ("Remind me in 30 minutes about the appointment", "en"),
        ("کل صبح 9 بجے دفتر جانے کی یاد دلاؤ", "ur"),
        ("سبا په 10 بجو زنگ وهوه", "ps"),
        ("Set reminder for tomorrow at 3 PM", "en")
    ]
    
    print("Testing Reminder Parsing:\n")
    
    for text, expected_lang in test_cases:
        print(f"Input: '{text}'")
        print(f"Expected Language: {expected_lang}")
        
        result = await parser.parse_reminder(text, expected_lang)
        
        if result['success']:
            print(f"✅ Parsed: {result['message']}")
            print(f"   Time: {result.get('relative_minutes', 0)} min, {result.get('relative_hours', 0)} hr")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Reasoning: {result['reasoning']}")
        else:
            print(f"❌ Failed to parse")
        
        print()
    
    # Test example phrases
    print("\n" + "=" * 70)
    print("Example Reminder Phrases:")
    
    for lang in ['ur', 'ps', 'en']:
        print(f"\n{lang.upper()} Examples:")
        examples = parser.get_reminder_examples(lang)
        for example in examples[:3]:
            print(f"  • {example}")

async def main():
    await test_multilingual_reminders()
    
    print("\n" + "=" * 70)
    print("✅ Multilingual reminder system is ready!")
    print("\n🎯 You can now set reminders using:")
    print("  • Urdu speech: '5 منٹ بعد میٹنگ کی یاد دہانی کرو'")
    print("  • Pashto speech: 'په 2 گھنٹو کې د پروژې یادونه راکړه'") 
    print("  • English speech: 'Remind me in 30 minutes'")
    print("  • Text input in any language")
    print("  • Quick reminder buttons in GUI")

if __name__ == "__main__":
    asyncio.run(main())
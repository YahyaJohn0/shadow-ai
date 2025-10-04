# test_nlu.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.nlu import NLU, SimpleNLU

# Mock brain for testing
class MockBrain:
    async def ask(self, messages):
        return '''
        {
            "intent": "get_weather",
            "confidence": 0.92,
            "entities": {
                "location": "London",
                "unit": "celsius"
            }
        }
        '''

async def test_advanced_nlu():
    print("🧠 Testing Advanced NLU System...")
    print("=" * 60)
    
    brain = MockBrain()
    nlu = NLU(brain=brain)
    
    test_cases = [
        "Send a WhatsApp message to John saying hello there",
        "What's the weather like in London?",
        "Set a timer for 5 minutes for my meeting",
        "Translate 'good morning' to Spanish",
        "What's the stock price of AAPL?",
        "Search for artificial intelligence news",
        "Open Chrome browser",
        "What time is it?",
        "Tell me a joke",
        "How much is 25 times 43?",
        "Just have a normal conversation with me"
    ]
    
    print("Testing Advanced NLU with AI fallback:\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"{i}. Query: {text}")
        intent, entities = await nlu.classify(text)
        print(f"   Intent: {intent}")
        print(f"   Entities: {entities}")
        print(f"   Confidence: High" if len(entities) > 0 else "   Confidence: Medium")
        print()

async def test_simple_nlu():
    print("\n" + "=" * 60)
    print("Testing Simple NLU (rule-based only):\n")
    
    nlu = SimpleNLU()
    
    test_cases = [
        "Send message to Alice on WhatsApp saying hello",
        "Weather in Paris",
        "Set reminder for 10 minutes",
        "What is Tesla stock price"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"{i}. Query: {text}")
        intent, entities = await nlu.classify(text)
        print(f"   Intent: {intent}")
        print(f"   Entities: {entities}")
        print()

async def main():
    await test_advanced_nlu()
    await test_simple_nlu()
    
    print("=" * 60)
    print("✅ NLU testing completed!")

if __name__ == "__main__":
    asyncio.run(main())
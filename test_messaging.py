# test_decision_engine.py
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from shadow_core.decision_engine import DecisionEngine
from shadow_core.memory import ShadowMemory

# Mock brain for testing
# Update the MockBrain in test_decision_engine.py to support NLU:

class MockBrain:
    async def ask(self, messages):
        # Check if this is an NLU classification request
        if any("classify its intent" in msg.get("content", "") for msg in messages):
            return '''
            {
                "intent": "chat",
                "confidence": 0.9,
                "entities": {}
            }
            '''
        
        # Extract the last user message
        user_message = messages[-1]["content"] if messages else "Hello"
        return f"Mock AI response to: {user_message}"


async def test_decision_engine():
    print("🤖 Testing Shadow Decision Engine...")
    print("=" * 60)
    
    # Initialize components
    memory = ShadowMemory()
    brain = MockBrain()
    
    # Create decision engine
    de = DecisionEngine(brain=brain, memory=memory)
    
    # Test queries with different intents
    test_queries = [
        "Hello, how are you?",
        "What's the weather like in London?",
        "Send a WhatsApp message to John saying hello there",
        "What's the stock price of Tesla?",
        "Search for artificial intelligence news",
        "Set a timer for 5 minutes",
        "Translate this to Spanish: Good morning",
        "How does machine learning work?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] Query: {query}")
        print("-" * 40)
        
        response = await de.handle_query(query)
        print(f"Response: {response}")
        
        # Show memory effect
        recent = memory.get_recent(1)
        if recent:
            print(f"Memory: {len(recent)} conversation turns stored")
    
    print("\n" + "=" * 60)
    print("✅ Decision Engine test completed!")
    
    # Show conversation history
    history = memory.get_conversation_history(5)
    print(f"\n📝 Conversation history ({len(history)} entries):")
    for role, content, timestamp in history:
        print(f"  {role}: {content[:50]}...")

if __name__ == "__main__":
    asyncio.run(test_decision_engine())
# test_google_search.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import GOOGLE_API_KEY, GOOGLE_CSE_ID
from shadow_core.enhanced_knowledge import EnhancedKnowledge

async def test_google_search():
    print("🔍 Testing Google Search Integration...")
    print("=" * 60)
    
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_google_api_key_here':
        print("❌ Google API key not configured in .env file")
        print("Please add your Google API keys to .env:")
        print("GOOGLE_API_KEY=your_actual_key_here")
        print("GOOGLE_CSE_ID=your_actual_cse_id_here")
        return
    
    knowledge = EnhancedKnowledge(
        google_api_key=GOOGLE_API_KEY,
        google_cse_id=GOOGLE_CSE_ID
    )
    
    test_queries = [
        "artificial intelligence",
        "latest Python programming news",
        "weather forecasting technology"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        try:
            result = await knowledge.web_search(query, num_results=2)
            print(f"✅ Results found! First 200 chars:")
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" + "=" * 60)
    print("✅ Google Search test completed!")

if __name__ == "__main__":
    asyncio.run(test_google_search())
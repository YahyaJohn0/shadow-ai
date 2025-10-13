# shadow_core/enhanced_knowledge.py
"""
Enhanced Knowledge module that uses Google Custom Search for real web results
"""

import logging
import aiohttp
import asyncio
from typing import List, Optional
from shadow_core.knowledge import Knowledge, SearchResult

logger = logging.getLogger(__name__)

class EnhancedKnowledge(Knowledge):
    """
    Enhanced knowledge module with real Google Search integration
    """
    
    def __init__(self, openweather_api_key: str = None, alpha_vantage_api_key: str = None, 
                 google_api_key: str = None, google_cse_id: str = None):
        super().__init__(openweather_api_key, alpha_vantage_api_key)
        
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        
        logger.info("Enhanced Knowledge module initialized with Google Search")
    
    async def web_search(self, query: str, num_results: int = 3) -> str:
        """
        Perform real web search using Google Custom Search API
        """
        try:
            if not query or len(query.strip()) < 2:
                return "Please provide a more specific search query."
            
            # Check cache
            cache_key = f"search_{hash(query)}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            # Use Google Custom Search for real results
            search_results = await self._google_web_search(query, num_results)
            
            if search_results:
                response = self._format_search_response(query, search_results)
                self._set_cached(cache_key, response, ttl=600)  # 10 minutes for search
                return response
            else:
                # Fallback to mock search
                fallback_results = await self._mock_web_search(query, num_results)
                if fallback_results:
                    response = self._format_search_response(query, fallback_results)
                    response += "\n\n(Note: Using simulated results - configure Google Search API for real-time data)"
                    return response
                else:
                    return f"I couldn't find relevant results for '{query}'. Try rephrasing your search."
                
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Sorry, I encountered an error searching for '{query}'."
    
    async def _google_web_search(self, query: str, num_results: int = 3) -> List[SearchResult]:
        """Use Google Custom Search API for real web search results"""
        try:
            if not self.google_api_key or not self.google_cse_id:
                logger.warning("Google API keys not configured")
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': min(num_results, 10)  # Google allows max 10 results per request
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('items', []):
                            results.append(SearchResult(
                                title=item.get('title', 'No title'),
                                url=item.get('link', ''),
                                snippet=item.get('snippet', 'No description available'),
                                source=item.get('displayLink', 'Unknown source')
                            ))
                        
                        logger.info(f"Google Search found {len(results)} results for '{query}'")
                        return results
                    else:
                        error_text = await response.text()
                        logger.error(f"Google Search API error: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Google Search API exception: {e}")
            return []
    
    async def get_news(self, topic: str = "general", num_articles: int = 3) -> str:
        """
        Get news using web search as fallback if NewsAPI not available
        """
        try:
            # First try parent's news method (if NewsAPI available)
            if hasattr(self, 'news_api_key') and self.news_api_key:
                return await super().get_news(topic, num_articles)
            
            # Fallback to web search for news
            search_query = f"latest news about {topic}" if topic != "general" else "latest news"
            search_results = await self._google_web_search(search_query, num_articles)
            
            if search_results:
                response = f"Latest news about {topic}:\n\n"
                for i, result in enumerate(search_results, 1):
                    response += f"{i}. {result.title}\n"
                    response += f"   {result.snippet}\n"
                    response += f"   Source: {result.source}\n\n"
                return response.strip()
            else:
                return await super().get_news(topic, num_articles)  # Use mock news as final fallback
                
        except Exception as e:
            logger.error(f"News search error: {e}")
            return f"Sorry, I couldn't fetch news about {topic}."
# shadow_core/knowledge.py
"""
Knowledge module for Shadow AI Agent - Provides real-world data via web APIs
Weather, stock prices, web search, news, and general knowledge
"""

import logging
import requests
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import re
from urllib.parse import quote


logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Structured weather data"""
    location: str
    temperature: float
    description: str
    humidity: int
    wind_speed: float
    condition: str
    feels_like: float
    unit: str = "metric"

@dataclass
class StockData:
    """Structured stock data"""
    symbol: str
    price: float
    change: float
    change_percent: float
    company_name: str = ""
    currency: str = "USD"

@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    snippet: str
    source: str = ""

class Knowledge:
    """
    Knowledge module for accessing real-world data via APIs
    """
    
    def __init__(self, openweather_api_key: str = None, alpha_vantage_api_key: str = None):
        self.openweather_api_key = openweather_api_key
        self.alpha_vantage_api_key = alpha_vantage_api_key
        
        # Cache to avoid excessive API calls
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # API endpoints
        self.weather_base_url = "http://api.openweathermap.org/data/2.5"
        self.alpha_vantage_url = "https://www.alphavantage.co/query"
        
        # Free APIs that don't require keys
        self.yahoo_finance_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.news_api_url = "https://newsapi.org/v2/top-headlines"
        
        logger.info("Knowledge module initialized")
    
    async def get_weather(self, location: str, unit: str = "metric") -> str:
        """
        Get weather information for a location
        Returns: Formatted weather string
        """
        try:
            if not location or location.lower() in ["here", "current location", "my location"]:
                location = "London"  # Default fallback
            
            # Check cache first
            cache_key = f"weather_{location}_{unit}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            if self.openweather_api_key:
                weather_data = await self._get_weather_openweather(location, unit)
            else:
                weather_data = await self._get_weather_fallback(location, unit)
            
            if weather_data:
                response = self._format_weather_response(weather_data)
                self._set_cached(cache_key, response)
                return response
            else:
                return f"I couldn't get weather information for {location}. Please try again later."
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return f"Sorry, I encountered an error getting weather for {location}."
    
    async def _get_weather_openweather(self, location: str, unit: str) -> Optional[WeatherData]:
        """Get weather data from OpenWeatherMap API"""
        try:
            # First, geocode the location to get coordinates
            geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.openweather_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geocode_url) as response:
                    if response.status == 200:
                        geo_data = await response.json()
                        if geo_data:
                            lat = geo_data[0]['lat']
                            lon = geo_data[0]['lon']
                            
                            # Now get weather data
                            weather_url = f"{self.weather_base_url}/weather?lat={lat}&lon={lon}&appid={self.openweather_api_key}&units={unit}"
                            
                            async with session.get(weather_url) as weather_response:
                                if weather_response.status == 200:
                                    data = await weather_response.json()
                                    return WeatherData(
                                        location=location,
                                        temperature=data['main']['temp'],
                                        description=data['weather'][0]['description'],
                                        humidity=data['main']['humidity'],
                                        wind_speed=data['wind']['speed'],
                                        condition=data['weather'][0]['main'],
                                        feels_like=data['main']['feels_like'],
                                        unit=unit
                                    )
        except Exception as e:
            logger.error(f"OpenWeather API error: {e}")
        
        return None
    
    async def _get_weather_fallback(self, location: str, unit: str) -> Optional[WeatherData]:
        """Fallback weather using free services"""
        try:
            # Use a simple free weather API (example)
            # Note: This is a mock implementation - you'd replace with actual free API
            temp = 20 + (hash(location) % 15)  # Mock temperature based on location hash
            conditions = ["sunny", "cloudy", "partly cloudy", "rainy"]
            condition = conditions[hash(location) % len(conditions)]
            
            return WeatherData(
                location=location,
                temperature=temp,
                description=condition,
                humidity=50 + (hash(location) % 30),
                wind_speed=5 + (hash(location) % 10),
                condition=condition,
                feels_like=temp + (hash(location) % 3) - 1,
                unit=unit
            )
        except Exception as e:
            logger.error(f"Fallback weather error: {e}")
            return None
    
    def _format_weather_response(self, weather: WeatherData) -> str:
        """Format weather data into a natural response"""
        unit_symbol = "°C" if weather.unit == "metric" else "°F"
        wind_unit = "m/s" if weather.unit == "metric" else "mph"
        
        response = f"Weather in {weather.location.title()}: "
        response += f"{weather.temperature:.1f}{unit_symbol}, {weather.description}. "
        response += f"Feels like {weather.feels_like:.1f}{unit_symbol}. "
        response += f"Humidity: {weather.humidity}%, Wind: {weather.wind_speed} {wind_unit}."
        
        return response
    
    async def get_stock_price(self, symbol: str) -> str:
        """
        Get stock price information
        Returns: Formatted stock price string
        """
        try:
            symbol = symbol.upper().strip()
            
            # Check cache
            cache_key = f"stock_{symbol}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            stock_data = None
            
            # Try Alpha Vantage first if API key available
            if self.alpha_vantage_api_key:
                stock_data = await self._get_stock_alphavantage(symbol)
            
            # Fallback to Yahoo Finance
            if not stock_data:
                stock_data = await self._get_stock_yahoo(symbol)
            
            if stock_data:
                response = self._format_stock_response(stock_data)
                self._set_cached(cache_key, response, ttl=60)  # Shorter cache for stocks
                return response
            else:
                return f"I couldn't find stock information for {symbol}."
                
        except Exception as e:
            logger.error(f"Stock API error: {e}")
            return f"Sorry, I encountered an error getting stock price for {symbol}."
    
    async def _get_stock_alphavantage(self, symbol: str) -> Optional[StockData]:
        """Get stock data from Alpha Vantage"""
        try:
            url = f"{self.alpha_vantage_url}?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'Global Quote' in data:
                            quote = data['Global Quote']
                            return StockData(
                                symbol=symbol,
                                price=float(quote['05. price']),
                                change=float(quote['09. change']),
                                change_percent=float(quote['10. change percent'].rstrip('%'))
                            )
        except Exception as e:
            logger.error(f"Alpha Vantage API error: {e}")
        
        return None
    
    async def _get_stock_yahoo(self, symbol: str) -> Optional[StockData]:
        """Get stock data from Yahoo Finance (free)"""
        try:
            url = f"{self.yahoo_finance_url}{symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'chart' in data and 'result' in data['chart']:
                            result = data['chart']['result'][0]
                            meta = result['meta']
                            indicators = result['indicators']['quote'][0]
                            
                            # Get the latest price
                            prices = indicators['close']
                            current_price = prices[-1] if prices else 0
                            
                            # Calculate change from previous close
                            previous_close = meta.get('previousClose', current_price)
                            change = current_price - previous_close
                            change_percent = (change / previous_close) * 100 if previous_close else 0
                            
                            return StockData(
                                symbol=symbol,
                                price=current_price,
                                change=change,
                                change_percent=change_percent,
                                company_name=meta.get('exchangeName', '')
                            )
        except Exception as e:
            logger.error(f"Yahoo Finance API error: {e}")
        
        return None
    
    def _format_stock_response(self, stock: StockData) -> str:
        """Format stock data into a natural response"""
        change_symbol = "📈" if stock.change >= 0 else "📉"
        change_direction = "up" if stock.change >= 0 else "down"
        
        response = f"{stock.symbol} {change_symbol}: ${stock.price:.2f} "
        response += f"({change_direction} ${abs(stock.change):.2f}, {abs(stock.change_percent):.2f}%)"
        
        if stock.company_name:
            response += f" - {stock.company_name}"
        
        return response
    
    
    async def web_search(self, query: str, num_results: int = 3) -> str:
        """
        Perform web search and return summarized results
        Returns: Formatted search results string
        """
        try:
            if not query or len(query.strip()) < 2:
                return "Please provide a more specific search query."
            
            # Check cache
            cache_key = f"search_{hash(query)}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            # For now, use a mock search implementation
            # In production, you'd integrate with Google Custom Search, Bing, or DuckDuckGo
            search_results = await self._mock_web_search(query, num_results)
            
            if search_results:
                response = self._format_search_response(query, search_results)
                self._set_cached(cache_key, response, ttl=600)  # 10 minutes for search
                return response
            else:
                return f"I couldn't find relevant results for '{query}'. Try rephrasing your search."
                
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return f"Sorry, I encountered an error searching for '{query}'."
    
    async def _mock_web_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Mock web search - replace with actual API in production"""
        # This is a mock implementation that returns simulated results
        # Replace this with actual search API integration
        
        mock_results = [
            SearchResult(
                title=f"Understanding {query} - Comprehensive Guide",
                url=f"https://example.com/{quote(query)}",
                snippet=f"Learn everything about {query} with our detailed guide covering all aspects and recent developments.",
                source="Example.com"
            ),
            SearchResult(
                title=f"Latest News on {query}",
                url=f"https://news.example.com/{quote(query)}",
                snippet=f"Breaking news and recent developments related to {query}. Stay updated with the latest information.",
                source="News Example"
            ),
            SearchResult(
                title=f"{query} - Wikipedia",
                url=f"https://wikipedia.org/wiki/{quote(query)}",
                snippet=f"Wikipedia article providing overview and detailed information about {query}.",
                source="Wikipedia"
            )
        ]
        
        await asyncio.sleep(0.1)  # Simulate API delay
        return mock_results[:num_results]
    
    def _format_search_response(self, query: str, results: List[SearchResult]) -> str:
        """Format search results into a natural response"""
        response = f"Here's what I found for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            response += f"{i}. {result.title}\n"
            response += f"   {result.snippet}\n"
            if result.source:
                response += f"   Source: {result.source}\n"
            response += "\n"
        
        return response.strip()
    
    async def get_news(self, topic: str = "general", num_articles: int = 3) -> str:
        """
        Get latest news headlines
        Returns: Formatted news string
        """
        try:
            # Check cache
            cache_key = f"news_{topic}"
            cached = self._get_cached(cache_key)
            if cached:
                return cached
            
            # Mock news implementation - replace with NewsAPI or similar
            news_results = await self._mock_get_news(topic, num_articles)
            
            if news_results:
                response = self._format_news_response(topic, news_results)
                self._set_cached(cache_key, response, ttl=300)  # 5 minutes for news
                return response
            else:
                return f"I couldn't find recent news about {topic}."
                
        except Exception as e:
            logger.error(f"News API error: {e}")
            return f"Sorry, I encountered an error getting news about {topic}."
    
    async def _mock_get_news(self, topic: str, num_articles: int) -> List[SearchResult]:
        """Mock news retrieval - replace with actual API"""
        topics = {
            "technology": ["AI", "Programming", "Innovation"],
            "sports": ["Football", "Basketball", "Tennis"],
            "business": ["Stocks", "Economy", "Startups"],
            "general": ["Current Events", "World News", "Politics"]
        }
        
        topic_keywords = topics.get(topic.lower(), topics["general"])
        
        mock_articles = []
        for i in range(num_articles):
            keyword = topic_keywords[i % len(topic_keywords)]
            mock_articles.append(
                SearchResult(
                    title=f"Breaking: New Developments in {keyword}",
                    url=f"https://news.example.com/{quote(keyword)}",
                    snippet=f"Latest updates and important news about {keyword}. Significant developments reported recently.",
                    source="News Service"
                )
            )
        
        await asyncio.sleep(0.1)
        return mock_articles
    
    def _format_news_response(self, topic: str, articles: List[SearchResult]) -> str:
        """Format news articles into a natural response"""
        response = f"Latest news about {topic}:\n\n"
        
        for i, article in enumerate(articles, 1):
            response += f"{i}. {article.title}\n"
            response += f"   {article.snippet}\n\n"
        
        return response.strip()
    
    async def get_fact(self, topic: str = None) -> str:
        """Get an interesting fact"""
        facts = [
            "The shortest war in history was between Britain and Zanzibar in 1896. Zanzibar surrendered after 38 minutes.",
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
            "Octopuses have three hearts. Two pump blood to the gills, while the third pumps it to the rest of the body.",
            "The world's oldest known recipe is for beer. It dates back about 4,000 years and was written on a clay tablet in ancient Mesopotamia.",
            "Bananas are berries, but strawberries aren't. Botanically, bananas qualify as berries while strawberries do not.",
            "The Eiffel Tower can be 15 cm taller during the summer. When a substance is heated up, its particles move more and it takes up a larger volume.",
        ]
        
        if topic:
            # Filter facts by topic (simple keyword matching)
            topic_facts = [fact for fact in facts if topic.lower() in fact.lower()]
            if topic_facts:
                return topic_facts[0]
        
        return facts[len(topic or "") % len(facts)]
    
    def _get_cached(self, key: str) -> Optional[str]:
        """Get value from cache if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    def _set_cached(self, key: str, data: str, ttl: int = None):
        """Set value in cache"""
        ttl = ttl or self.cache_ttl
        self.cache[key] = (data, time.time())
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Knowledge cache cleared")

    # Add this method to the Knowledge class in shadow_core/knowledge.py:

async def _google_web_search(self, query: str, num_results: int = 3) -> List[SearchResult]:
    """Use Google Custom Search API for real web search"""
    try:
        if not hasattr(self, 'google_api_key') or not hasattr(self, 'google_cse_id'):
            return await self._mock_web_search(query, num_results)
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': query,
            'num': num_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('items', []):
                        results.append(SearchResult(
                            title=item.get('title', ''),
                            url=item.get('link', ''),
                            snippet=item.get('snippet', ''),
                            source=item.get('displayLink', '')
                        ))
                    
                    return results
                else:
                    logger.warning(f"Google Search API returned status {response.status}")
                    return await self._mock_web_search(query, num_results)
                    
    except Exception as e:
        logger.error(f"Google Search API error: {e}")
        return await self._mock_web_search(query, num_results)

# Update the web_search method to use Google API:
async def web_search(self, query: str, num_results: int = 3) -> str:
    # ... existing code ...
    
    # Use Google Custom Search if available
    if hasattr(self, 'google_api_key') and self.google_api_key:
        search_results = await self._google_web_search(query, num_results)
    else:
        search_results = await self._mock_web_search(query, num_results)
    
    # ... rest of the method ...

# Free API version that doesn't require API keys
class FreeKnowledge(Knowledge):
    """
    Knowledge module using only free APIs and services
    """
    
    def __init__(self):
        # No API keys needed for free version
        super().__init__()
        logger.info("Free Knowledge module initialized")
    
    async def get_weather(self, location: str, unit: str = "metric") -> str:
        """Get weather using free services"""
        # Use a free weather API or web scraping
        # For now, use the mock implementation from parent
        return await super().get_weather(location, unit)
    
    async def get_stock_price(self, symbol: str) -> str:
        """Get stock prices using Yahoo Finance"""
        try:
            stock_data = await self._get_stock_yahoo(symbol)
            if stock_data:
                return self._format_stock_response(stock_data)
            else:
                return f"Could not find stock data for {symbol}. Please check the symbol."
        except Exception as e:
            logger.error(f"Free stock API error: {e}")
            return f"Error getting stock price for {symbol}."
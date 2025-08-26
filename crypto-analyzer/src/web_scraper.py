"""
Free Web Scraper - Fallback for when premium APIs are unavailable
Ethical web scraping with rate limiting and proper headers
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import os
from pathlib import Path
import threading
from dataclasses import dataclass
import random
from textblob import TextBlob


@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    snippet: str
    published_date: Optional[str]
    source: str
    sentiment_score: float
    relevance_score: float


@dataclass
class ScrapedContent:
    """Full scraped content from a URL"""
    url: str
    title: str
    content: str
    published_date: Optional[str]
    author: Optional[str]
    source_domain: str
    word_count: int
    extraction_quality: float


class WebScraper:
    """Free web scraping with rate limiting and ethical practices"""
    
    def __init__(self, cache_dir: str = "data/web_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting
        self._last_request_time = 0
        self._min_delay = float(os.getenv('WEB_SCRAPER_DELAY', '2.0'))  # 2 seconds default
        self._lock = threading.Lock()
        
        # Setup session with retries and proper headers
        self.session = self._setup_session()
        
        # Trusted crypto news sources
        self.crypto_sources = {
            'cointelegraph.com': {'weight': 9, 'rss': 'https://cointelegraph.com/rss'},
            'coindesk.com': {'weight': 9, 'rss': 'https://www.coindesk.com/arc/outboundfeeds/rss/'},
            'decrypt.co': {'weight': 8, 'rss': 'https://decrypt.co/feed'},
            'theblock.co': {'weight': 8, 'rss': None},
            'bitcoinmagazine.com': {'weight': 7, 'rss': 'https://bitcoinmagazine.com/feed'},
            'crypto.news': {'weight': 6, 'rss': 'https://crypto.news/feed/'},
            'u.today': {'weight': 6, 'rss': 'https://u.today/rss'},
            'cryptonews.com': {'weight': 5, 'rss': 'https://cryptonews.com/news/feed/'},
            'coingape.com': {'weight': 5, 'rss': 'https://coingape.com/feed/'}
        }
        
        # Search engines for fallback
        self.search_engines = [
            {
                'name': 'DuckDuckGo',
                'search_url': 'https://html.duckduckgo.com/html/',
                'params': {'q': '{query}'},
                'parser': self._parse_duckduckgo_results
            }
        ]
    
    def _setup_session(self) -> requests.Session:
        """Setup requests session with proper configuration"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Realistic headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            
            if time_since_last < self._min_delay:
                sleep_time = self._min_delay - time_since_last
                # Add small random jitter
                sleep_time += random.uniform(0, 0.5)
                time.sleep(sleep_time)
            
            self._last_request_time = time.time()
    
    def _get_cache_key(self, query: str, source: str = '') -> str:
        """Generate cache key for query"""
        content = f"{query}_{source}_{datetime.now().date()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str, max_age_hours: int = 6) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check age
                cached_time = datetime.fromisoformat(data.get('timestamp', ''))
                if datetime.now() - cached_time < timedelta(hours=max_age_hours):
                    return data.get('results')
        
        except Exception as e:
            print(f"Warning: Could not load cache {cache_key}: {e}")
        
        return None
    
    def _cache_result(self, cache_key: str, results: Dict[str, Any]):
        """Cache search results"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"Warning: Could not cache results: {e}")
    
    def search_crypto_news(self, token: str, query_terms: List[str] = None, 
                          max_results: int = 10) -> List[SearchResult]:
        """Search crypto news using RSS feeds and targeted searches"""
        
        if query_terms is None:
            query_terms = ['price', 'analysis', 'update', 'news']
        
        # Check cache first
        cache_key = self._get_cache_key(f"{token}_news_{'_'.join(query_terms)}")
        cached = self._get_cached_result(cache_key, max_age_hours=2)
        if cached:
            return [SearchResult(**result) for result in cached.get('search_results', [])]
        
        all_results = []
        
        # Search RSS feeds
        rss_results = self._search_rss_feeds(token, query_terms)
        all_results.extend(rss_results)
        
        # If not enough results, try web search
        if len(all_results) < max_results:
            web_results = self._search_web_engines(token, query_terms, max_results - len(all_results))
            all_results.extend(web_results)
        
        # Sort by relevance and recency
        all_results.sort(key=lambda x: (x.relevance_score, x.sentiment_score), reverse=True)
        
        # Limit results
        final_results = all_results[:max_results]
        
        # Cache results
        cache_data = {
            'search_results': [
                {
                    'title': r.title,
                    'url': r.url,
                    'snippet': r.snippet,
                    'published_date': r.published_date,
                    'source': r.source,
                    'sentiment_score': r.sentiment_score,
                    'relevance_score': r.relevance_score
                }
                for r in final_results
            ]
        }
        self._cache_result(cache_key, cache_data)
        
        return final_results
    
    def _search_rss_feeds(self, token: str, query_terms: List[str]) -> List[SearchResult]:
        """Search RSS feeds for token-related news"""
        results = []
        
        for domain, info in self.crypto_sources.items():
            rss_url = info.get('rss')
            if not rss_url:
                continue
            
            try:
                self._enforce_rate_limit()
                
                # Parse RSS feed
                feed = feedparser.parse(rss_url)
                
                if feed.bozo:
                    continue
                
                # Search entries
                for entry in feed.entries[:20]:  # Check last 20 entries
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    link = entry.get('link', '')
                    
                    # Check if relevant to token
                    relevance = self._calculate_relevance(token, title, summary, query_terms)
                    
                    if relevance > 0.3:  # Minimum relevance threshold
                        # Calculate sentiment
                        sentiment = self._calculate_sentiment(f"{title} {summary}")
                        
                        # Parse published date
                        pub_date = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                        elif hasattr(entry, 'published'):
                            pub_date = entry.published
                        
                        result = SearchResult(
                            title=title,
                            url=link,
                            snippet=summary[:300] + "..." if len(summary) > 300 else summary,
                            published_date=pub_date,
                            source=domain,
                            sentiment_score=sentiment,
                            relevance_score=relevance * info['weight'] / 10  # Weight by source quality
                        )
                        
                        results.append(result)
            
            except Exception as e:
                print(f"Warning: Error parsing RSS from {domain}: {e}")
                continue
        
        return results
    
    def _search_web_engines(self, token: str, query_terms: List[str], max_results: int) -> List[SearchResult]:
        """Search web engines as fallback"""
        results = []
        
        # Construct search query
        query = f"{token} cryptocurrency {' OR '.join(query_terms)}"
        
        for engine in self.search_engines:
            try:
                engine_results = engine['parser'](query, max_results)
                results.extend(engine_results)
                
                if len(results) >= max_results:
                    break
            
            except Exception as e:
                print(f"Warning: Error searching {engine['name']}: {e}")
                continue
        
        return results[:max_results]
    
    def _parse_duckduckgo_results(self, query: str, max_results: int) -> List[SearchResult]:
        """Parse DuckDuckGo search results"""
        results = []
        
        try:
            self._enforce_rate_limit()
            
            params = {'q': query, 'b': ''}  # b parameter for pagination
            response = self.session.get(
                'https://html.duckduckgo.com/html/',
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find result elements
            result_elements = soup.find_all('div', class_='result')
            
            for elem in result_elements[:max_results]:
                try:
                    # Extract title and URL
                    title_elem = elem.find('a', class_='result__a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    
                    # Extract snippet
                    snippet_elem = elem.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    # Calculate relevance and sentiment
                    relevance = self._calculate_relevance(query, title, snippet, [])
                    sentiment = self._calculate_sentiment(f"{title} {snippet}")
                    
                    # Determine source domain
                    source = urlparse(url).netloc if url else 'unknown'
                    
                    result = SearchResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                        published_date=None,
                        source=source,
                        sentiment_score=sentiment,
                        relevance_score=relevance
                    )
                    
                    results.append(result)
                
                except Exception as e:
                    print(f"Warning: Error parsing search result: {e}")
                    continue
        
        except Exception as e:
            print(f"Warning: Error searching DuckDuckGo: {e}")
        
        return results
    
    def _calculate_relevance(self, token: str, title: str, content: str, 
                           query_terms: List[str]) -> float:
        """Calculate relevance score for content"""
        
        text = f"{title} {content}".lower()
        token_lower = token.lower()
        
        score = 0.0
        
        # Token name matches
        if token_lower in text:
            score += 1.0
        
        # Common token aliases
        aliases = {
            'bitcoin': ['btc', 'bitcoin'],
            'ethereum': ['eth', 'ethereum'],
            'binancecoin': ['bnb', 'binance coin', 'binance'],
            'solana': ['sol', 'solana'],
            'cardano': ['ada', 'cardano'],
            'ripple': ['xrp', 'ripple'],
            'dogecoin': ['doge', 'dogecoin'],
            'polygon': ['matic', 'polygon'],
            'polkadot': ['dot', 'polkadot'],
            'chainlink': ['link', 'chainlink']
        }
        
        for canonical, alias_list in aliases.items():
            if token_lower in alias_list or canonical == token_lower:
                for alias in alias_list:
                    if alias in text:
                        score += 0.8
                        break
        
        # Query terms
        for term in query_terms:
            if term.lower() in text:
                score += 0.3
        
        # Crypto-related keywords
        crypto_keywords = [
            'cryptocurrency', 'crypto', 'blockchain', 'trading', 'price',
            'market', 'analysis', 'investment', 'defi', 'nft', 'altcoin'
        ]
        
        for keyword in crypto_keywords:
            if keyword in text:
                score += 0.1
        
        # Normalize score
        return min(score / 3.0, 1.0)
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using TextBlob"""
        try:
            blob = TextBlob(text)
            # Convert to 0-1 scale (from -1 to 1)
            return (blob.sentiment.polarity + 1) / 2
        except:
            return 0.5  # Neutral if analysis fails
    
    def scrape_article_content(self, url: str) -> Optional[ScrapedContent]:
        """Scrape full content from article URL"""
        
        # Check cache
        cache_key = self._get_cache_key(url, 'article')
        cached = self._get_cached_result(cache_key, max_age_hours=24)
        if cached:
            return ScrapedContent(**cached)
        
        try:
            self._enforce_rate_limit()
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Try multiple content selectors
            content_selectors = [
                'article',
                '.entry-content',
                '.post-content',
                '.article-body',
                '.content',
                '[class*="article"]',
                '[class*="post"]',
                'main'
            ]
            
            content = ''
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    content = content_elem.get_text(separator=' ', strip=True)
                    if len(content) > 200:  # Minimum content length
                        break
            
            # Extract metadata
            author = None
            author_selectors = [
                '[rel="author"]',
                '.author',
                '[class*="author"]',
                '.byline'
            ]
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            # Extract published date
            pub_date = None
            date_selectors = [
                'time[datetime]',
                '[class*="date"]',
                '.published',
                '.post-date'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    if date_elem.has_attr('datetime'):
                        pub_date = date_elem.get('datetime')
                    else:
                        pub_date = date_elem.get_text(strip=True)
                    break
            
            # Quality assessment
            word_count = len(content.split())
            quality = self._assess_content_quality(title, content, word_count)
            
            scraped_content = ScrapedContent(
                url=url,
                title=title,
                content=content[:5000],  # Limit content length
                published_date=pub_date,
                author=author,
                source_domain=urlparse(url).netloc,
                word_count=word_count,
                extraction_quality=quality
            )
            
            # Cache if quality is decent
            if quality > 0.3:
                self._cache_result(cache_key, {
                    'url': scraped_content.url,
                    'title': scraped_content.title,
                    'content': scraped_content.content,
                    'published_date': scraped_content.published_date,
                    'author': scraped_content.author,
                    'source_domain': scraped_content.source_domain,
                    'word_count': scraped_content.word_count,
                    'extraction_quality': scraped_content.extraction_quality
                })
            
            return scraped_content
        
        except Exception as e:
            print(f"Warning: Error scraping {url}: {e}")
            return None
    
    def _assess_content_quality(self, title: str, content: str, word_count: int) -> float:
        """Assess quality of scraped content"""
        
        quality_score = 0.0
        
        # Word count (optimal range)
        if 100 <= word_count <= 3000:
            quality_score += 0.3
        elif word_count > 50:
            quality_score += 0.1
        
        # Title quality
        if title and len(title) > 10:
            quality_score += 0.2
        
        # Content structure
        if content:
            sentences = content.split('.')
            if len(sentences) > 3:
                quality_score += 0.2
            
            # Check for common noise
            noise_indicators = [
                'click here', 'subscribe', 'advertisement', 'cookie policy',
                'terms of service', '404', 'page not found'
            ]
            
            noise_count = sum(1 for noise in noise_indicators if noise.lower() in content.lower())
            if noise_count == 0:
                quality_score += 0.2
            elif noise_count < 3:
                quality_score += 0.1
        
        # Content/title relevance
        if title and content:
            title_words = set(title.lower().split())
            content_words = set(content.lower().split()[:100])  # First 100 words
            
            overlap = len(title_words.intersection(content_words))
            if overlap > 2:
                quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def search_sentiment_indicators(self, token: str) -> Dict[str, Any]:
        """Search for sentiment indicators and market mood"""
        
        cache_key = self._get_cache_key(f"{token}_sentiment", 'indicators')
        cached = self._get_cached_result(cache_key, max_age_hours=1)
        if cached:
            return cached
        
        # Search for sentiment-related content
        sentiment_queries = [
            f"{token} bullish bearish sentiment",
            f"{token} price prediction analysis",
            f"{token} market sentiment mood"
        ]
        
        all_results = []
        for query in sentiment_queries:
            results = self.search_crypto_news(token, query.split(), max_results=5)
            all_results.extend(results)
        
        # Analyze sentiment
        sentiment_data = self._analyze_sentiment_from_results(all_results)
        
        # Cache results
        self._cache_result(cache_key, sentiment_data)
        
        return sentiment_data
    
    def _analyze_sentiment_from_results(self, results: List[SearchResult]) -> Dict[str, Any]:
        """Analyze sentiment from search results"""
        
        if not results:
            return {
                'overall_sentiment': 0.5,
                'sentiment_label': 'Neutral',
                'confidence': 0.0,
                'positive_signals': [],
                'negative_signals': [],
                'analysis_count': 0
            }
        
        sentiments = [r.sentiment_score for r in results]
        overall_sentiment = sum(sentiments) / len(sentiments)
        
        # Categorize signals
        positive_signals = []
        negative_signals = []
        
        for result in results:
            text = f"{result.title} {result.snippet}".lower()
            
            # Positive indicators
            if any(word in text for word in ['bullish', 'rally', 'surge', 'pump', 'moon', 'breakthrough']):
                positive_signals.append({
                    'source': result.source,
                    'signal': result.title[:100],
                    'confidence': result.sentiment_score
                })
            
            # Negative indicators
            elif any(word in text for word in ['bearish', 'crash', 'dump', 'decline', 'sell-off', 'correction']):
                negative_signals.append({
                    'source': result.source,
                    'signal': result.title[:100],
                    'confidence': 1 - result.sentiment_score
                })
        
        # Determine label
        if overall_sentiment > 0.6:
            sentiment_label = 'Bullish'
        elif overall_sentiment > 0.55:
            sentiment_label = 'Slightly Bullish'
        elif overall_sentiment > 0.45:
            sentiment_label = 'Neutral'
        elif overall_sentiment > 0.4:
            sentiment_label = 'Slightly Bearish'
        else:
            sentiment_label = 'Bearish'
        
        # Confidence based on number of sources and agreement
        confidence = min(len(results) / 10, 1.0)  # More sources = higher confidence
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_label': sentiment_label,
            'confidence': confidence,
            'positive_signals': positive_signals[:5],  # Top 5
            'negative_signals': negative_signals[:5],  # Top 5
            'analysis_count': len(results)
        }
    
    def cleanup_cache(self, max_age_days: int = 7):
        """Clean up old cache files"""
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                if cache_file.stat().st_mtime < cutoff_time.timestamp():
                    cache_file.unlink()
        except Exception as e:
            print(f"Warning: Could not cleanup cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        try:
            cache_files = list(self.cache_dir.glob('*.json'))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'total_files': len(cache_files),
                'total_size_mb': total_size / (1024 * 1024),
                'cache_directory': str(self.cache_dir)
            }
        except Exception:
            return {'total_files': 0, 'total_size_mb': 0, 'cache_directory': str(self.cache_dir)}


# Global instance
web_scraper = WebScraper()
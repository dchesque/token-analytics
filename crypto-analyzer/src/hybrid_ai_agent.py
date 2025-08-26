"""
Hybrid AI Agent - Combines quantitative analysis with intelligent web research
Uses multiple premium APIs with smart fallbacks and context synthesis
"""

import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import threading
from dataclasses import dataclass, asdict
import os
import re
from pathlib import Path

# Import API clients (with fallbacks)
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("Tavily not available - install with: pip install tavily-python")

try:
    import requests
    YOU_AVAILABLE = True
except ImportError:
    YOU_AVAILABLE = False

try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    print("SerpAPI not available - install with: pip install google-search-results")

# Local imports
from quota_manager import quota_manager, APIProvider, TokenPriority
from web_scraper import web_scraper, SearchResult


@dataclass
class WebResearchResult:
    """Structured web research result"""
    success: bool
    provider_used: str
    query: str
    results_count: int
    processing_time: float
    news_articles: List[Dict[str, Any]]
    sentiment_analysis: Dict[str, Any]
    recent_developments: List[Dict[str, Any]]
    market_context: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class HybridAnalysisResult:
    """Complete hybrid analysis combining quantitative + web research"""
    token: str
    timestamp: str
    quantitative_analysis: Dict[str, Any]
    web_research: Optional[WebResearchResult]
    hybrid_insights: Dict[str, Any]
    contextual_score_adjustment: float
    final_recommendation: Dict[str, Any]
    confidence_level: float
    processing_time: float


class HybridAIAgent:
    """Main hybrid AI agent combining quantitative analysis with web research"""
    
    def __init__(self):
        self.quota_manager = quota_manager
        self.web_scraper = web_scraper
        
        # Initialize API clients
        self.clients = {}
        self._initialize_api_clients()
        
        # Configuration
        self.config = {
            'max_articles_per_query': int(os.getenv('MAX_ARTICLES_PER_QUERY', '10')),
            'web_search_timeout': int(os.getenv('WEB_SEARCH_TIMEOUT', '60')),
            'sentiment_weight': float(os.getenv('SENTIMENT_WEIGHT', '0.3')),
            'news_recency_hours': int(os.getenv('NEWS_RECENCY_HOURS', '48')),
            'min_confidence_threshold': float(os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.4'))
        }
        
        # Cache for research results
        self._cache = {}
        self._cache_lock = threading.Lock()
        
    def _initialize_api_clients(self):
        """Initialize premium API clients with error handling"""
        
        # Tavily Search AI
        if TAVILY_AVAILABLE:
            api_key = os.getenv('TAVILY_API_KEY')
            if api_key:
                try:
                    self.clients[APIProvider.TAVILY] = TavilyClient(api_key=api_key)
                except Exception as e:
                    print(f"Warning: Could not initialize Tavily client: {e}")
        
        # You.com Search
        if YOU_AVAILABLE:
            api_key = os.getenv('YOU_API_KEY')
            if api_key:
                self.clients[APIProvider.YOU] = {
                    'api_key': api_key,
                    'base_url': 'https://api.ydc-index.io'
                }
        
        # SerpAPI
        if SERPAPI_AVAILABLE:
            api_key = os.getenv('SERPAPI_KEY')
            if api_key:
                self.clients[APIProvider.SERPAPI] = api_key
    
    def search_with_intelligent_fallback(self, query: str, token: str, 
                                       max_results: int = 10) -> Tuple[List[SearchResult], str]:
        """
        Search with intelligent fallback chain
        Returns: (results, provider_used)
        """
        
        start_time = time.time()
        
        # Get best provider for this token
        provider, reason = self.quota_manager.get_best_provider(token)
        
        if not provider:
            # Use free scraping as ultimate fallback
            results = self.web_scraper.search_crypto_news(token, query.split(), max_results)
            self.quota_manager.record_usage(APIProvider.FREE_SCRAPING, token, query, 
                                          len(results) > 0, time.time() - start_time)
            return results, APIProvider.FREE_SCRAPING.value
        
        # Try the selected provider
        results = self._search_with_provider(provider, query, token, max_results)
        
        if results:
            self.quota_manager.record_usage(provider, token, query, True, time.time() - start_time)
            return results, provider.value
        
        # If primary provider failed, try fallback chain
        exclude = [provider]
        
        while True:
            fallback_provider, fallback_reason = self.quota_manager.get_best_provider(token, exclude)
            
            if not fallback_provider:
                break
            
            results = self._search_with_provider(fallback_provider, query, token, max_results)
            
            if results:
                self.quota_manager.record_usage(fallback_provider, token, query, True, time.time() - start_time)
                return results, fallback_provider.value
            
            exclude.append(fallback_provider)
        
        # Ultimate fallback to free scraping
        results = self.web_scraper.search_crypto_news(token, query.split(), max_results)
        self.quota_manager.record_usage(APIProvider.FREE_SCRAPING, token, query, 
                                      len(results) > 0, time.time() - start_time)
        return results, APIProvider.FREE_SCRAPING.value
    
    def _search_with_provider(self, provider: APIProvider, query: str, 
                            token: str, max_results: int) -> List[SearchResult]:
        """Search using specific provider"""
        
        try:
            if provider == APIProvider.TAVILY:
                return self._search_tavily(query, max_results)
            elif provider == APIProvider.YOU:
                return self._search_you(query, max_results)
            elif provider == APIProvider.SERPAPI:
                return self._search_serpapi(query, max_results)
            elif provider == APIProvider.FREE_SCRAPING:
                return self.web_scraper.search_crypto_news(token, query.split(), max_results)
            
        except Exception as e:
            print(f"Warning: Search failed with {provider.value}: {e}")
            return []
        
        return []
    
    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using Tavily API"""
        
        if APIProvider.TAVILY not in self.clients:
            return []
        
        try:
            client = self.clients[APIProvider.TAVILY]
            
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
                include_domains=["cointelegraph.com", "coindesk.com", "decrypt.co", 
                               "theblock.co", "bitcoinmagazine.com"]
            )
            
            results = []
            for item in response.get('results', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('content', '')[:300],
                    published_date=item.get('published_date'),
                    source=self._extract_domain(item.get('url', '')),
                    sentiment_score=0.5,  # Will be calculated later
                    relevance_score=item.get('score', 0.5)
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []
    
    def _search_you(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using You.com API"""
        
        if APIProvider.YOU not in self.clients:
            return []
        
        try:
            client_config = self.clients[APIProvider.YOU]
            
            headers = {
                'X-API-Key': client_config['api_key']
            }
            
            params = {
                'query': query,
                'num_web_results': max_results,
                'safesearch': 'moderate'
            }
            
            response = requests.get(
                f"{client_config['base_url']}/search",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('web', {}).get('results', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('description', '')[:300],
                    published_date=None,
                    source=self._extract_domain(item.get('url', '')),
                    sentiment_score=0.5,
                    relevance_score=0.7  # You.com generally has good relevance
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"You.com search error: {e}")
            return []
    
    def _search_serpapi(self, query: str, max_results: int) -> List[SearchResult]:
        """Search using SerpAPI"""
        
        if APIProvider.SERPAPI not in self.clients:
            return []
        
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.clients[APIProvider.SERPAPI],
                "num": min(max_results, 10)
            }
            
            search = GoogleSearch(params)
            search_results = search.get_dict()
            
            results = []
            
            for item in search_results.get("organic_results", []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', '')[:300],
                    published_date=item.get('date'),
                    source=self._extract_domain(item.get('link', '')),
                    sentiment_score=0.5,
                    relevance_score=0.8  # Google results are usually highly relevant
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            print(f"SerpAPI search error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return 'unknown'
    
    def analyze_with_web_context(self, token: str, existing_analysis: Dict[str, Any]) -> HybridAnalysisResult:
        """
        Perform hybrid analysis combining quantitative data with web research
        """
        
        start_time = time.time()
        timestamp = datetime.now().isoformat()
        
        # Check cache first
        cache_key = f"{token}_{datetime.now().date()}"
        cached_research = self._get_cached_research(cache_key)
        
        if cached_research:
            web_research = cached_research
        else:
            # Perform web research
            web_research = self._perform_web_research(token)
            self._cache_research(cache_key, web_research)
        
        # Generate hybrid insights
        hybrid_insights = self._generate_hybrid_insights(existing_analysis, web_research)
        
        # Calculate contextual score adjustment
        score_adjustment = self._calculate_score_adjustment(existing_analysis, web_research, hybrid_insights)
        
        # Generate final recommendation
        final_recommendation = self._generate_final_recommendation(
            existing_analysis, web_research, hybrid_insights, score_adjustment
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(existing_analysis, web_research, hybrid_insights)
        
        processing_time = time.time() - start_time
        
        return HybridAnalysisResult(
            token=token,
            timestamp=timestamp,
            quantitative_analysis=existing_analysis,
            web_research=web_research,
            hybrid_insights=hybrid_insights,
            contextual_score_adjustment=score_adjustment,
            final_recommendation=final_recommendation,
            confidence_level=confidence,
            processing_time=processing_time
        )
    
    def _perform_web_research(self, token: str) -> WebResearchResult:
        """Perform comprehensive web research for token"""
        
        start_time = time.time()
        
        # Research queries
        queries = [
            f"{token} cryptocurrency news analysis",
            f"{token} price prediction market sentiment",
            f"{token} development updates partnership",
            f"{token} trading signals technical analysis"
        ]
        
        all_articles = []
        provider_used = None
        
        # Perform searches
        for query in queries:
            try:
                results, provider = self.search_with_intelligent_fallback(query, token, max_results=5)
                all_articles.extend(results)
                
                if not provider_used:
                    provider_used = provider
                
                # Small delay between queries
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Warning: Query '{query}' failed: {e}")
                continue
        
        # Remove duplicates and sort by relevance
        unique_articles = self._deduplicate_articles(all_articles)
        unique_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to most relevant articles
        final_articles = unique_articles[:self.config['max_articles_per_query']]
        
        # Analyze sentiment
        sentiment_analysis = self._analyze_collective_sentiment(final_articles)
        
        # Extract recent developments
        recent_developments = self._extract_recent_developments(final_articles)
        
        # Generate market context
        market_context = self._generate_market_context(final_articles, sentiment_analysis)
        
        processing_time = time.time() - start_time
        
        return WebResearchResult(
            success=len(final_articles) > 0,
            provider_used=provider_used or 'none',
            query=f"{token} comprehensive research",
            results_count=len(final_articles),
            processing_time=processing_time,
            news_articles=[self._format_article(article) for article in final_articles],
            sentiment_analysis=sentiment_analysis,
            recent_developments=recent_developments,
            market_context=market_context
        )
    
    def _deduplicate_articles(self, articles: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate articles based on URL and title similarity"""
        
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            # Skip if exact URL already seen
            if article.url in seen_urls:
                continue
            
            # Check for very similar titles (simple heuristic)
            is_duplicate = False
            for existing in unique_articles:
                title_similarity = self._calculate_title_similarity(article.title, existing.title)
                if title_similarity > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_urls.add(article.url)
        
        return unique_articles
    
    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate simple title similarity"""
        
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _format_article(self, article: SearchResult) -> Dict[str, Any]:
        """Format article for output"""
        
        return {
            'title': article.title,
            'url': article.url,
            'snippet': article.snippet,
            'source': article.source,
            'published_date': article.published_date,
            'sentiment_score': article.sentiment_score,
            'relevance_score': article.relevance_score
        }
    
    def _analyze_collective_sentiment(self, articles: List[SearchResult]) -> Dict[str, Any]:
        """Analyze collective sentiment from articles"""
        
        if not articles:
            return {
                'overall_sentiment': 0.5,
                'sentiment_label': 'Neutral',
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        # Update sentiment scores for articles
        for article in articles:
            article.sentiment_score = self._calculate_article_sentiment(article)
        
        sentiments = [article.sentiment_score for article in articles]
        overall_sentiment = sum(sentiments) / len(sentiments)
        
        # Categorize articles
        positive_count = len([s for s in sentiments if s > 0.6])
        negative_count = len([s for s in sentiments if s < 0.4])
        neutral_count = len(sentiments) - positive_count - negative_count
        
        # Determine label
        if overall_sentiment > 0.65:
            sentiment_label = 'Strongly Bullish'
        elif overall_sentiment > 0.55:
            sentiment_label = 'Bullish'
        elif overall_sentiment > 0.45:
            sentiment_label = 'Neutral'
        elif overall_sentiment > 0.35:
            sentiment_label = 'Bearish'
        else:
            sentiment_label = 'Strongly Bearish'
        
        # Calculate confidence based on agreement and article count
        sentiment_variance = sum((s - overall_sentiment) ** 2 for s in sentiments) / len(sentiments)
        confidence = min((1 - sentiment_variance) * (len(articles) / 10), 1.0)
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_label': sentiment_label,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sample_size': len(articles)
        }
    
    def _calculate_article_sentiment(self, article: SearchResult) -> float:
        """Calculate sentiment for individual article"""
        
        from textblob import TextBlob
        
        try:
            text = f"{article.title} {article.snippet}"
            blob = TextBlob(text)
            
            # Convert from -1,1 to 0,1 scale
            sentiment = (blob.sentiment.polarity + 1) / 2
            
            # Boost/penalize based on crypto-specific keywords
            text_lower = text.lower()
            
            bullish_keywords = ['bullish', 'rally', 'surge', 'moon', 'pump', 'breakthrough', 'adoption', 'partnership']
            bearish_keywords = ['bearish', 'crash', 'dump', 'decline', 'sell-off', 'correction', 'regulation', 'ban']
            
            bullish_count = sum(1 for word in bullish_keywords if word in text_lower)
            bearish_count = sum(1 for word in bearish_keywords if word in text_lower)
            
            # Adjust sentiment based on keyword presence
            if bullish_count > bearish_count:
                sentiment = min(sentiment + 0.1 * (bullish_count - bearish_count), 1.0)
            elif bearish_count > bullish_count:
                sentiment = max(sentiment - 0.1 * (bearish_count - bullish_count), 0.0)
            
            return sentiment
            
        except:
            return 0.5  # Neutral if analysis fails
    
    def _extract_recent_developments(self, articles: List[SearchResult]) -> List[Dict[str, Any]]:
        """Extract key recent developments from articles"""
        
        developments = []
        
        # Keywords that indicate important developments
        dev_keywords = [
            'partnership', 'acquisition', 'merger', 'launch', 'upgrade', 'fork',
            'listing', 'integration', 'announcement', 'release', 'update',
            'regulation', 'sec', 'etf', 'institutional', 'investment'
        ]
        
        for article in articles:
            text_lower = f"{article.title} {article.snippet}".lower()
            
            # Check for development keywords
            found_keywords = [kw for kw in dev_keywords if kw in text_lower]
            
            if found_keywords:
                # Extract key information
                development = {
                    'title': article.title,
                    'url': article.url,
                    'source': article.source,
                    'published_date': article.published_date,
                    'keywords': found_keywords,
                    'importance_score': len(found_keywords) * article.relevance_score,
                    'snippet': article.snippet[:200]
                }
                
                developments.append(development)
        
        # Sort by importance and return top developments
        developments.sort(key=lambda x: x['importance_score'], reverse=True)
        return developments[:5]
    
    def _generate_market_context(self, articles: List[SearchResult], 
                                sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market context from articles and sentiment"""
        
        # Extract themes and trends
        all_text = ' '.join([f"{article.title} {article.snippet}" for article in articles])
        
        # Key themes analysis
        themes = self._extract_themes(all_text)
        
        # Market phase detection
        market_phase = self._detect_market_phase(sentiment_analysis, articles)
        
        # Risk factors
        risk_factors = self._identify_risk_factors(articles)
        
        # Opportunities
        opportunities = self._identify_opportunities(articles)
        
        return {
            'dominant_themes': themes,
            'market_phase': market_phase,
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'narrative_strength': self._calculate_narrative_strength(articles),
            'media_attention': len(articles),
            'sentiment_momentum': sentiment_analysis.get('overall_sentiment', 0.5)
        }
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract dominant themes from text"""
        
        theme_keywords = {
            'DeFi': ['defi', 'decentralized finance', 'yield farming', 'liquidity', 'staking'],
            'NFTs': ['nft', 'non-fungible', 'digital art', 'collectible', 'metaverse'],
            'Gaming': ['gaming', 'play-to-earn', 'game', 'virtual world'],
            'Payments': ['payment', 'transaction', 'remittance', 'cross-border'],
            'Infrastructure': ['blockchain', 'scalability', 'layer 2', 'consensus'],
            'Regulation': ['regulation', 'sec', 'regulatory', 'compliance', 'legal'],
            'Institutional': ['institutional', 'wall street', 'bank', 'fund', 'etf'],
            'Technical': ['upgrade', 'fork', 'development', 'github', 'protocol']
        }
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme, keywords in theme_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        # Return themes sorted by relevance
        return sorted(theme_scores.keys(), key=lambda x: theme_scores[x], reverse=True)[:3]
    
    def _detect_market_phase(self, sentiment_analysis: Dict[str, Any], 
                           articles: List[SearchResult]) -> str:
        """Detect current market phase"""
        
        sentiment = sentiment_analysis.get('overall_sentiment', 0.5)
        confidence = sentiment_analysis.get('confidence', 0.0)
        
        # Simple phase detection based on sentiment and confidence
        if sentiment > 0.7 and confidence > 0.6:
            return 'Bull Market'
        elif sentiment > 0.6:
            return 'Recovery/Optimism'
        elif sentiment > 0.4:
            return 'Consolidation'
        elif sentiment > 0.3:
            return 'Correction/Caution'
        else:
            return 'Bear Market'
    
    def _identify_risk_factors(self, articles: List[SearchResult]) -> List[str]:
        """Identify potential risk factors from articles"""
        
        risk_keywords = [
            'regulation', 'ban', 'sec investigation', 'lawsuit', 'hack',
            'volatility', 'correction', 'sell-off', 'delisting', 'security'
        ]
        
        risks = []
        all_text = ' '.join([f"{article.title} {article.snippet}" for article in articles]).lower()
        
        for keyword in risk_keywords:
            if keyword in all_text:
                risks.append(keyword.title())
        
        return list(set(risks))[:5]  # Remove duplicates and limit
    
    def _identify_opportunities(self, articles: List[SearchResult]) -> List[str]:
        """Identify potential opportunities from articles"""
        
        opportunity_keywords = [
            'partnership', 'adoption', 'integration', 'upgrade', 'launch',
            'listing', 'institutional interest', 'etf approval', 'mainstream adoption'
        ]
        
        opportunities = []
        all_text = ' '.join([f"{article.title} {article.snippet}" for article in articles]).lower()
        
        for keyword in opportunity_keywords:
            if keyword in all_text:
                opportunities.append(keyword.title())
        
        return list(set(opportunities))[:5]  # Remove duplicates and limit
    
    def _calculate_narrative_strength(self, articles: List[SearchResult]) -> float:
        """Calculate strength of dominant narrative"""
        
        if not articles:
            return 0.0
        
        # Simple metric based on article count, relevance, and source quality
        total_relevance = sum(article.relevance_score for article in articles)
        avg_relevance = total_relevance / len(articles)
        
        # Bonus for high-quality sources
        quality_sources = ['coindesk.com', 'cointelegraph.com', 'theblock.co']
        quality_bonus = sum(1 for article in articles if any(source in article.source for source in quality_sources))
        
        narrative_strength = (avg_relevance * 0.7) + (quality_bonus / len(articles) * 0.3)
        
        return min(narrative_strength, 1.0)
    
    def _generate_hybrid_insights(self, quantitative_analysis: Dict[str, Any], 
                                web_research: Optional[WebResearchResult]) -> Dict[str, Any]:
        """Generate insights by combining quantitative and web research data"""
        
        insights = {
            'convergence_analysis': {},
            'divergence_warnings': [],
            'contextual_factors': [],
            'timing_insights': {},
            'risk_reward_assessment': {}
        }
        
        if not web_research or not web_research.success:
            insights['convergence_analysis']['status'] = 'quantitative_only'
            insights['convergence_analysis']['note'] = 'Web research unavailable - using quantitative analysis only'
            return insights
        
        # Convergence analysis
        quant_score = quantitative_analysis.get('score', 5.0)
        sentiment = web_research.sentiment_analysis.get('overall_sentiment', 0.5)
        
        # Convert sentiment to 0-10 scale for comparison
        sentiment_score = sentiment * 10
        
        convergence_diff = abs(quant_score - sentiment_score)
        
        insights['convergence_analysis'] = {
            'quantitative_score': quant_score,
            'sentiment_score': sentiment_score,
            'convergence_strength': 1.0 - (convergence_diff / 10),
            'agreement_level': self._get_agreement_level(convergence_diff)
        }
        
        # Divergence warnings
        if convergence_diff > 3.0:
            if quant_score > sentiment_score:
                insights['divergence_warnings'].append(
                    f"Strong fundamentals ({quant_score:.1f}) vs negative sentiment ({sentiment_score:.1f}) - potential value opportunity"
                )
            else:
                insights['divergence_warnings'].append(
                    f"Weak fundamentals ({quant_score:.1f}) vs positive sentiment ({sentiment_score:.1f}) - possible overvaluation"
                )
        
        # Contextual factors
        market_context = web_research.market_context
        insights['contextual_factors'] = [
            f"Market Phase: {market_context.get('market_phase', 'Unknown')}",
            f"Media Attention: {market_context.get('media_attention', 0)} recent articles",
            f"Dominant Themes: {', '.join(market_context.get('dominant_themes', [])[:2])}"
        ]
        
        # Add risk factors and opportunities
        if market_context.get('risk_factors'):
            insights['contextual_factors'].extend([
                f"Key Risks: {', '.join(market_context['risk_factors'][:2])}"
            ])
        
        if market_context.get('opportunities'):
            insights['contextual_factors'].extend([
                f"Opportunities: {', '.join(market_context['opportunities'][:2])}"
            ])
        
        # Timing insights
        developments = web_research.recent_developments
        insights['timing_insights'] = {
            'recent_catalysts': len(developments),
            'narrative_strength': market_context.get('narrative_strength', 0.5),
            'timing_assessment': self._assess_timing(sentiment, developments, quant_score)
        }
        
        # Risk-reward assessment
        insights['risk_reward_assessment'] = self._assess_risk_reward(
            quantitative_analysis, web_research, convergence_diff
        )
        
        return insights
    
    def _get_agreement_level(self, convergence_diff: float) -> str:
        """Get agreement level description"""
        if convergence_diff < 1.0:
            return 'Strong Agreement'
        elif convergence_diff < 2.0:
            return 'Good Agreement'
        elif convergence_diff < 3.0:
            return 'Moderate Agreement'
        elif convergence_diff < 4.0:
            return 'Weak Agreement'
        else:
            return 'Strong Disagreement'
    
    def _assess_timing(self, sentiment: float, developments: List[Dict], quant_score: float) -> str:
        """Assess market timing"""
        
        # Simple timing logic
        if len(developments) > 2 and sentiment > 0.6:
            return 'Strong momentum - good entry timing'
        elif quant_score > 7 and sentiment < 0.4:
            return 'Value opportunity - contrarian timing'
        elif sentiment > 0.7:
            return 'High optimism - exercise caution'
        elif sentiment < 0.3:
            return 'Pessimistic sentiment - potential bottom'
        else:
            return 'Neutral timing - wait for clearer signals'
    
    def _assess_risk_reward(self, quantitative_analysis: Dict[str, Any], 
                          web_research: WebResearchResult, convergence_diff: float) -> Dict[str, Any]:
        """Assess risk-reward profile"""
        
        base_score = quantitative_analysis.get('score', 5.0)
        sentiment = web_research.sentiment_analysis.get('overall_sentiment', 0.5)
        confidence = web_research.sentiment_analysis.get('confidence', 0.5)
        
        # Risk assessment
        risk_level = 'Medium'
        if convergence_diff > 4.0:
            risk_level = 'High'
        elif confidence < 0.3:
            risk_level = 'High'
        elif base_score > 8 and sentiment > 0.7:
            risk_level = 'Low'
        
        # Reward potential
        reward_potential = 'Medium'
        if base_score > 7 and sentiment < 0.4:
            reward_potential = 'High'  # Undervalued
        elif base_score < 4:
            reward_potential = 'Low'
        elif sentiment > 0.8:
            reward_potential = 'Low'  # Potentially overpriced
        
        return {
            'risk_level': risk_level,
            'reward_potential': reward_potential,
            'confidence': confidence,
            'key_factor': self._identify_key_factor(quantitative_analysis, web_research)
        }
    
    def _identify_key_factor(self, quantitative_analysis: Dict[str, Any], 
                           web_research: WebResearchResult) -> str:
        """Identify the key factor driving the analysis"""
        
        base_score = quantitative_analysis.get('score', 5.0)
        sentiment = web_research.sentiment_analysis.get('overall_sentiment', 0.5)
        
        if base_score > 8:
            return 'Strong fundamentals'
        elif sentiment > 0.7:
            return 'Positive market sentiment'
        elif sentiment < 0.3:
            return 'Negative sentiment concerns'
        elif len(web_research.recent_developments) > 3:
            return 'Recent developments'
        else:
            return 'Market dynamics'
    
    def _calculate_score_adjustment(self, quantitative_analysis: Dict[str, Any], 
                                  web_research: Optional[WebResearchResult], 
                                  hybrid_insights: Dict[str, Any]) -> float:
        """Calculate contextual score adjustment based on web research"""
        
        if not web_research or not web_research.success:
            return 0.0
        
        base_score = quantitative_analysis.get('score', 5.0)
        sentiment = web_research.sentiment_analysis.get('overall_sentiment', 0.5)
        confidence = web_research.sentiment_analysis.get('confidence', 0.5)
        
        # Weight for sentiment adjustment (configurable)
        sentiment_weight = self.config['sentiment_weight']
        
        # Calculate sentiment-based adjustment
        sentiment_adjustment = (sentiment - 0.5) * 2 * sentiment_weight  # -0.6 to +0.6 range
        
        # Apply confidence weighting
        confidence_weighted_adjustment = sentiment_adjustment * confidence
        
        # Recent developments boost
        developments_boost = min(len(web_research.recent_developments) * 0.1, 0.5)
        
        # Risk factors penalty
        risk_penalty = len(web_research.market_context.get('risk_factors', [])) * -0.1
        
        # Total adjustment
        total_adjustment = confidence_weighted_adjustment + developments_boost + risk_penalty
        
        # Limit adjustment to reasonable range (-2 to +2)
        return max(min(total_adjustment, 2.0), -2.0)
    
    def _generate_final_recommendation(self, quantitative_analysis: Dict[str, Any], 
                                     web_research: Optional[WebResearchResult],
                                     hybrid_insights: Dict[str, Any], 
                                     score_adjustment: float) -> Dict[str, Any]:
        """Generate final hybrid recommendation"""
        
        base_score = quantitative_analysis.get('score', 5.0)
        adjusted_score = base_score + score_adjustment
        
        # Determine recommendation
        if adjusted_score >= 8.5:
            recommendation = 'STRONG BUY'
            action = 'Consider significant position with risk management'
        elif adjusted_score >= 7:
            recommendation = 'BUY'
            action = 'Good opportunity for position building'
        elif adjusted_score >= 6:
            recommendation = 'WEAK BUY'
            action = 'Small position or DCA strategy'
        elif adjusted_score >= 4:
            recommendation = 'HOLD'
            action = 'Wait for better entry or more clarity'
        elif adjusted_score >= 3:
            recommendation = 'WEAK SELL'
            action = 'Consider reducing position'
        else:
            recommendation = 'STRONG SELL'
            action = 'Avoid or exit position'
        
        # Strategy insights
        strategy = self._generate_strategy_insights(adjusted_score, hybrid_insights, web_research)
        
        return {
            'recommendation': recommendation,
            'adjusted_score': adjusted_score,
            'score_adjustment': score_adjustment,
            'action': action,
            'strategy': strategy,
            'key_factors': self._get_key_factors(quantitative_analysis, web_research, hybrid_insights),
            'timeline': self._estimate_timeline(hybrid_insights, web_research)
        }
    
    def _generate_strategy_insights(self, adjusted_score: float, 
                                  hybrid_insights: Dict[str, Any], 
                                  web_research: Optional[WebResearchResult]) -> List[str]:
        """Generate strategic insights"""
        
        strategies = []
        
        # Score-based strategies
        if adjusted_score > 8:
            strategies.append("High conviction play - consider larger position size")
        elif adjusted_score < 4:
            strategies.append("High risk asset - avoid or minimal exposure")
        
        # Convergence-based strategies
        convergence = hybrid_insights.get('convergence_analysis', {})
        agreement = convergence.get('agreement_level', 'Unknown')
        
        if 'Strong Disagreement' in agreement:
            strategies.append("Mixed signals - use position sizing to manage uncertainty")
        elif 'Strong Agreement' in agreement:
            strategies.append("High confidence signals - normal position sizing appropriate")
        
        # Timing-based strategies
        timing = hybrid_insights.get('timing_insights', {})
        timing_assessment = timing.get('timing_assessment', '')
        
        if 'contrarian' in timing_assessment:
            strategies.append("Contrarian opportunity - consider phased entry")
        elif 'momentum' in timing_assessment:
            strategies.append("Momentum play - watch for entry on pullbacks")
        elif 'caution' in timing_assessment:
            strategies.append("Exercise patience - wait for better risk/reward")
        
        # Risk management
        risk_assessment = hybrid_insights.get('risk_reward_assessment', {})
        risk_level = risk_assessment.get('risk_level', 'Medium')
        
        if risk_level == 'High':
            strategies.append("High risk profile - use strict stop losses")
        elif risk_level == 'Low':
            strategies.append("Lower risk profile - suitable for larger allocations")
        
        return strategies[:4]  # Limit to top 4 strategies
    
    def _get_key_factors(self, quantitative_analysis: Dict[str, Any], 
                        web_research: Optional[WebResearchResult], 
                        hybrid_insights: Dict[str, Any]) -> List[str]:
        """Get key factors influencing the analysis"""
        
        factors = []
        
        # Quantitative factors
        strengths = quantitative_analysis.get('strengths', [])
        factors.extend(strengths[:2])  # Top 2 strengths
        
        if web_research and web_research.success:
            # Web research factors
            market_context = web_research.market_context
            
            if market_context.get('dominant_themes'):
                factors.append(f"Theme: {market_context['dominant_themes'][0]}")
            
            if web_research.recent_developments:
                factors.append(f"Recent: {web_research.recent_developments[0]['keywords'][0]}")
            
            # Sentiment factor
            sentiment_label = web_research.sentiment_analysis.get('sentiment_label', 'Neutral')
            factors.append(f"Sentiment: {sentiment_label}")
        
        return factors[:5]  # Limit to 5 key factors
    
    def _estimate_timeline(self, hybrid_insights: Dict[str, Any], 
                          web_research: Optional[WebResearchResult]) -> str:
        """Estimate investment timeline"""
        
        if not web_research:
            return "3-6 months (quantitative analysis only)"
        
        # Check for catalysts
        developments = web_research.recent_developments
        market_phase = web_research.market_context.get('market_phase', 'Unknown')
        
        if len(developments) > 3:
            return "1-3 months (multiple near-term catalysts)"
        elif 'Bull Market' in market_phase:
            return "6-12 months (bull market cycle)"
        elif 'Bear Market' in market_phase:
            return "12-24 months (bear market recovery)"
        else:
            return "3-6 months (consolidation phase)"
    
    def _calculate_confidence(self, quantitative_analysis: Dict[str, Any], 
                            web_research: Optional[WebResearchResult], 
                            hybrid_insights: Dict[str, Any]) -> float:
        """Calculate overall confidence in the analysis"""
        
        # Base confidence from quantitative analysis
        base_confidence = 0.7  # Default for quantitative analysis
        
        if not web_research or not web_research.success:
            return base_confidence * 0.8  # Penalize for lack of web context
        
        # Web research confidence factors
        web_confidence = web_research.sentiment_analysis.get('confidence', 0.5)
        results_count = web_research.results_count
        
        # Convergence confidence
        convergence = hybrid_insights.get('convergence_analysis', {})
        convergence_strength = convergence.get('convergence_strength', 0.5)
        
        # Combine factors
        data_quality_factor = min(results_count / 10, 1.0)  # More articles = higher confidence
        convergence_factor = convergence_strength
        web_factor = web_confidence
        
        # Weighted combination
        final_confidence = (
            base_confidence * 0.4 +
            web_factor * 0.3 +
            convergence_factor * 0.2 +
            data_quality_factor * 0.1
        )
        
        return min(final_confidence, 1.0)
    
    def _get_cached_research(self, cache_key: str) -> Optional[WebResearchResult]:
        """Get cached research result"""
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached and cached.get('timestamp'):
                # Check if cache is still valid (6 hours)
                cache_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cache_time < timedelta(hours=6):
                    return WebResearchResult(**cached['data'])
        return None
    
    def _cache_research(self, cache_key: str, research_result: WebResearchResult):
        """Cache research result"""
        with self._cache_lock:
            self._cache[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'data': asdict(research_result)
            }
            
            # Clean old cache entries
            if len(self._cache) > 100:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k]['timestamp'])
                del self._cache[oldest_key]
    
    def research_recent_developments(self, token: str) -> Dict[str, Any]:
        """Focus on recent developments for a token"""
        
        query = f"{token} latest news developments partnerships upgrades"
        results, provider = self.search_with_intelligent_fallback(query, token, max_results=8)
        
        # Filter for recency (last 7 days ideally)
        recent_results = []
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for result in results:
            if result.published_date:
                try:
                    pub_date = datetime.fromisoformat(result.published_date.replace('Z', '+00:00'))
                    if pub_date >= cutoff_date:
                        recent_results.append(result)
                except:
                    recent_results.append(result)  # Include if can't parse date
            else:
                recent_results.append(result)  # Include if no date
        
        return {
            'developments': [self._format_article(r) for r in recent_results[:5]],
            'provider_used': provider,
            'search_query': query,
            'total_found': len(results),
            'recent_count': len(recent_results)
        }
    
    def analyze_market_sentiment_context(self, token: str) -> Dict[str, Any]:
        """Deep dive into market sentiment context"""
        
        # Multiple sentiment-focused queries
        queries = [
            f"{token} market sentiment analysis",
            f"{token} bullish bearish outlook",
            f"{token} investor sentiment mood"
        ]
        
        all_results = []
        
        for query in queries:
            results, _ = self.search_with_intelligent_fallback(query, token, max_results=5)
            all_results.extend(results)
        
        # Deduplicate
        unique_results = self._deduplicate_articles(all_results)
        
        # Analyze sentiment patterns
        sentiment_analysis = self._analyze_collective_sentiment(unique_results)
        
        # Additional sentiment context from web scraper
        scraper_sentiment = self.web_scraper.search_sentiment_indicators(token)
        
        return {
            'search_based_sentiment': sentiment_analysis,
            'web_scraper_sentiment': scraper_sentiment,
            'article_count': len(unique_results),
            'sentiment_sources': list(set([r.source for r in unique_results]))
        }
    
    def detect_narrative_shifts(self, token: str) -> Dict[str, Any]:
        """Detect shifts in dominant narratives"""
        
        # Search for different time periods
        current_query = f"{token} news analysis 2024"
        historical_query = f"{token} narrative theme trend analysis"
        
        current_results, _ = self.search_with_intelligent_fallback(current_query, token, max_results=10)
        historical_results, _ = self.search_with_intelligent_fallback(historical_query, token, max_results=10)
        
        # Extract themes from both periods
        current_themes = self._extract_themes(' '.join([f"{r.title} {r.snippet}" for r in current_results]))
        historical_themes = self._extract_themes(' '.join([f"{r.title} {r.snippet}" for r in historical_results]))
        
        # Compare themes
        emerging_themes = [theme for theme in current_themes if theme not in historical_themes]
        declining_themes = [theme for theme in historical_themes if theme not in current_themes]
        persistent_themes = [theme for theme in current_themes if theme in historical_themes]
        
        return {
            'current_themes': current_themes,
            'historical_themes': historical_themes,
            'emerging_themes': emerging_themes,
            'declining_themes': declining_themes,
            'persistent_themes': persistent_themes,
            'narrative_shift_detected': len(emerging_themes) > 0 or len(declining_themes) > 0,
            'analysis_confidence': min(len(current_results) / 10, 1.0)
        }
    
    def generate_contextual_insights(self, combined_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level contextual insights from combined data"""
        
        insights = {
            'executive_summary': '',
            'key_opportunities': [],
            'primary_risks': [],
            'strategic_implications': [],
            'market_positioning': '',
            'outlook_assessment': ''
        }
        
        # Extract key information
        quant_score = combined_data.get('quantitative_analysis', {}).get('score', 5.0)
        web_research = combined_data.get('web_research')
        hybrid_insights = combined_data.get('hybrid_insights', {})
        
        if web_research and web_research.success:
            sentiment_label = web_research.sentiment_analysis.get('sentiment_label', 'Neutral')
            market_phase = web_research.market_context.get('market_phase', 'Unknown')
            
            # Executive summary
            insights['executive_summary'] = (
                f"Analysis shows {sentiment_label.lower()} sentiment with "
                f"quantitative score of {quant_score:.1f}/10 in a {market_phase.lower()} environment."
            )
            
            # Key opportunities
            opportunities = web_research.market_context.get('opportunities', [])
            insights['key_opportunities'] = opportunities[:3]
            
            # Primary risks
            risk_factors = web_research.market_context.get('risk_factors', [])
            insights['primary_risks'] = risk_factors[:3]
            
            # Market positioning
            themes = web_research.market_context.get('dominant_themes', [])
            if themes:
                insights['market_positioning'] = f"Positioned in {', '.join(themes[:2]).lower()} narrative(s)"
            
            # Outlook assessment
            recommendation = combined_data.get('final_recommendation', {})
            timeline = recommendation.get('timeline', '3-6 months')
            
            insights['outlook_assessment'] = f"Overall outlook: {recommendation.get('recommendation', 'HOLD')} with {timeline} timeline"
        
        else:
            insights['executive_summary'] = f"Quantitative analysis shows score of {quant_score:.1f}/10 (web context unavailable)"
            insights['market_positioning'] = 'Limited context available'
            insights['outlook_assessment'] = 'Assessment based on quantitative metrics only'
        
        # Strategic implications
        convergence_analysis = hybrid_insights.get('convergence_analysis', {})
        agreement_level = convergence_analysis.get('agreement_level', 'Unknown')
        
        if 'Strong Agreement' in agreement_level:
            insights['strategic_implications'].append("High confidence - signals align across data sources")
        elif 'Strong Disagreement' in agreement_level:
            insights['strategic_implications'].append("Mixed signals - requires careful position sizing")
        
        risk_reward = hybrid_insights.get('risk_reward_assessment', {})
        if risk_reward.get('risk_level') == 'High':
            insights['strategic_implications'].append("High risk profile - use strict risk management")
        elif risk_reward.get('reward_potential') == 'High':
            insights['strategic_implications'].append("High reward potential - consider larger allocation")
        
        return insights
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status across all APIs"""
        return self.quota_manager.get_quota_status()
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.quota_manager.get_usage_stats(days)
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old cached data"""
        self.quota_manager.cleanup_old_data(days)
        self.web_scraper.cleanup_cache(days // 7)  # Web cache older than weeks


# Global instance
hybrid_ai_agent = HybridAIAgent()
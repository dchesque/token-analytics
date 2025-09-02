"""
DEX Screener API Client
Public API without authentication required
Rate limits: 300 rpm (pairs), 60 rpm (profiles)
"""

import requests
import time
from typing import Dict, List, Optional, Any
from functools import lru_cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DexScreenerClient:
    """
    Client for DEX Screener API
    Docs: https://docs.dexscreener.com/api/reference
    """
    
    BASE_URL = "https://api.dexscreener.com"
    
    # Rate limiting
    PAIRS_RPM = 300  # 300 requests per minute for pairs
    PROFILES_RPM = 60  # 60 requests per minute for profiles
    
    def __init__(self, cache_ttl: int = 60):
        """
        Initialize DEX Screener client
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 60)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'CryptoAnalyzer/1.0'
        })
        self.cache_ttl = cache_ttl
        self._last_request_time = 0
        self._request_count = 0
        self._cache = {}
        self._cache_timestamps = {}
    
    def _rate_limit(self, endpoint_type: str = 'pairs'):
        """Handle rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self._last_request_time > 60:
            self._request_count = 0
            self._last_request_time = current_time
        
        # Check rate limit
        max_rpm = self.PAIRS_RPM if endpoint_type == 'pairs' else self.PROFILES_RPM
        if self._request_count >= max_rpm:
            sleep_time = 60 - (current_time - self._last_request_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)
                self._request_count = 0
                self._last_request_time = time.time()
        
        self._request_count += 1
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached response if still valid"""
        if cache_key in self._cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {cache_key}")
                return self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """Set cache with timestamp"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     endpoint_type: str = 'pairs') -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        url = f"{self.BASE_URL}{endpoint}"
        cache_key = f"{url}:{str(params)}"
        
        # Check cache first
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Rate limiting
        self._rate_limit(endpoint_type)
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Cache successful response
                self._set_cache(cache_key, data)
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
    
    def search_pairs(self, query: str) -> Optional[List[Dict]]:
        """
        Search for pairs by token symbol, name, or address
        Returns up to 30 pairs
        
        Args:
            query: Search query (token symbol, name, or address)
            
        Returns:
            List of pair objects or None if error
        """
        logger.info(f"Searching pairs for: {query}")
        
        result = self._make_request(
            "/latest/dex/search",
            params={"q": query}
        )
        
        if result and 'pairs' in result:
            return result['pairs']
        return None
    
    def token_pairs(self, chain_id: str, token_address: str) -> Optional[List[Dict]]:
        """
        Get all pairs for a specific token on a chain
        
        Args:
            chain_id: Chain identifier (e.g., 'ethereum', 'bsc', 'polygon')
            token_address: Token contract address
            
        Returns:
            List of pair objects or None if error
        """
        logger.info(f"Fetching pairs for token {token_address} on {chain_id}")
        
        result = self._make_request(
            f"/token-pairs/v1/{chain_id}/{token_address}"
        )
        
        if result and 'pairs' in result:
            return result['pairs']
        return None
    
    def pair_by_id(self, chain_id: str, pair_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific pair
        
        Args:
            chain_id: Chain identifier
            pair_id: Pair address/ID
            
        Returns:
            Pair object or None if error
        """
        logger.info(f"Fetching pair {pair_id} on {chain_id}")
        
        result = self._make_request(
            f"/latest/dex/pairs/{chain_id}/{pair_id}"
        )
        
        if result and 'pair' in result:
            return result['pair']
        return None
    
    def latest_token_profiles(self) -> Optional[List[Dict]]:
        """
        Get latest token profiles (limited to 30)
        
        Returns:
            List of token profiles or None if error
        """
        logger.info("Fetching latest token profiles")
        
        result = self._make_request(
            "/token-profiles/latest/v1",
            endpoint_type='profiles'
        )
        
        return result if isinstance(result, list) else None
    
    def get_top_pairs_by_chain(self, chain_id: str, limit: int = 20) -> Optional[List[Dict]]:
        """
        Get top pairs by volume for a specific chain
        
        Args:
            chain_id: Chain identifier
            limit: Maximum number of pairs to return
            
        Returns:
            List of top pairs or None if error
        """
        logger.info(f"Fetching top pairs for {chain_id}")
        
        # This is a convenience method using search
        # You might need to adjust based on actual API capabilities
        result = self._make_request(
            f"/latest/dex/pairs/{chain_id}",
            params={"limit": limit}
        )
        
        if result and 'pairs' in result:
            return result['pairs'][:limit]
        return None
    
    def normalize_pair_data(self, pair: Dict) -> Dict:
        """
        Normalize pair data to consistent format
        
        Args:
            pair: Raw pair data from API
            
        Returns:
            Normalized pair dictionary
        """
        return {
            'pair_address': pair.get('pairAddress', ''),
            'chain_id': pair.get('chainId', ''),
            'dex_id': pair.get('dexId', ''),
            'base_token': {
                'address': pair.get('baseToken', {}).get('address', ''),
                'name': pair.get('baseToken', {}).get('name', ''),
                'symbol': pair.get('baseToken', {}).get('symbol', '')
            },
            'quote_token': {
                'address': pair.get('quoteToken', {}).get('address', ''),
                'name': pair.get('quoteToken', {}).get('name', ''),
                'symbol': pair.get('quoteToken', {}).get('symbol', '')
            },
            'price_native': pair.get('priceNative', '0'),
            'price_usd': pair.get('priceUsd', '0'),
            'liquidity': {
                'usd': pair.get('liquidity', {}).get('usd', 0),
                'base': pair.get('liquidity', {}).get('base', 0),
                'quote': pair.get('liquidity', {}).get('quote', 0)
            },
            'volume': {
                'h24': pair.get('volume', {}).get('h24', 0),
                'h6': pair.get('volume', {}).get('h6', 0),
                'h1': pair.get('volume', {}).get('h1', 0),
                'm5': pair.get('volume', {}).get('m5', 0)
            },
            'price_change': {
                'h24': pair.get('priceChange', {}).get('h24', 0),
                'h6': pair.get('priceChange', {}).get('h6', 0),
                'h1': pair.get('priceChange', {}).get('h1', 0),
                'm5': pair.get('priceChange', {}).get('m5', 0)
            },
            'txns': {
                'h24': {
                    'buys': pair.get('txns', {}).get('h24', {}).get('buys', 0),
                    'sells': pair.get('txns', {}).get('h24', {}).get('sells', 0)
                },
                'h6': {
                    'buys': pair.get('txns', {}).get('h6', {}).get('buys', 0),
                    'sells': pair.get('txns', {}).get('h6', {}).get('sells', 0)
                },
                'h1': {
                    'buys': pair.get('txns', {}).get('h1', {}).get('buys', 0),
                    'sells': pair.get('txns', {}).get('h1', {}).get('sells', 0)
                },
                'm5': {
                    'buys': pair.get('txns', {}).get('m5', {}).get('buys', 0),
                    'sells': pair.get('txns', {}).get('m5', {}).get('sells', 0)
                }
            },
            'created_at': pair.get('pairCreatedAt', 0),
            'info': {
                'image_url': pair.get('info', {}).get('imageUrl', ''),
                'websites': pair.get('info', {}).get('websites', []),
                'socials': pair.get('info', {}).get('socials', [])
            }
        }


# Example usage
if __name__ == "__main__":
    client = DexScreenerClient()
    
    # Search for Bitcoin pairs
    pairs = client.search_pairs("BTC")
    if pairs:
        print(f"Found {len(pairs)} pairs")
        for pair in pairs[:3]:
            normalized = client.normalize_pair_data(pair)
            print(f"Pair: {normalized['base_token']['symbol']}/{normalized['quote_token']['symbol']}")
            print(f"  Price USD: ${normalized['price_usd']}")
            print(f"  Liquidity: ${normalized['liquidity']['usd']:,.2f}")
            print(f"  Volume 24h: ${normalized['volume']['h24']:,.2f}")
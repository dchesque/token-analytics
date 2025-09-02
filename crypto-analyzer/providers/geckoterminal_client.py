"""
GeckoTerminal API Client
Public/free API for OHLCV data from decentralized exchanges
Global cache: 1 min, updates 2-3s after transaction
"""

import requests
import time
from typing import Dict, List, Optional, Any, Tuple
from functools import lru_cache
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GeckoTerminalClient:
    """
    Client for GeckoTerminal API
    Docs: https://www.geckoterminal.com/api/docs
    """
    
    BASE_URL = "https://api.geckoterminal.com/api/v2"
    
    # Rate limiting (conservative approach)
    MAX_RPM = 60  # Conservative rate limit
    
    def __init__(self, cache_ttl: int = 60):
        """
        Initialize GeckoTerminal client
        
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
    
    def _rate_limit(self):
        """Handle rate limiting"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self._last_request_time > 60:
            self._request_count = 0
            self._last_request_time = current_time
        
        # Check rate limit
        if self._request_count >= self.MAX_RPM:
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
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request with retry logic"""
        url = f"{self.BASE_URL}{endpoint}"
        cache_key = f"{url}:{str(params)}"
        
        # Check cache first
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        # Rate limiting
        self._rate_limit()
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
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
    
    def get_ohlcv_by_pool(self, network: str, pool: str, timeframe: str = "5m", 
                         aggregate: int = 1, limit: int = 500) -> Optional[List[List]]:
        """
        Get OHLCV data for a specific pool
        
        Args:
            network: Network name (e.g., 'ethereum', 'bsc', 'polygon')
            pool: Pool address
            timeframe: Timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            aggregate: Aggregation (1 for 1x timeframe, 2 for 2x, etc.)
            limit: Maximum candles to return (max 1000)
            
        Returns:
            List of OHLCV candles in format: [timestamp, open, high, low, close, volume]
        """
        logger.info(f"Fetching OHLCV for pool {pool} on {network}")
        
        params = {
            'timeframe': timeframe,
            'aggregate': aggregate,
            'limit': min(limit, 1000)  # API max is 1000
        }
        
        result = self._make_request(
            f"/networks/{network}/pools/{pool}/ohlcv",
            params=params
        )
        
        if result and 'data' in result and 'attributes' in result['data']:
            ohlcv_list = result['data']['attributes'].get('ohlcv_list', [])
            
            # Convert to standard format: [timestamp, open, high, low, close, volume]
            normalized_candles = []
            for candle in ohlcv_list:
                if len(candle) >= 6:  # Ensure we have all required fields
                    normalized_candles.append([
                        int(candle[0]),      # timestamp (unix)
                        float(candle[1]),    # open
                        float(candle[2]),    # high
                        float(candle[3]),    # low
                        float(candle[4]),    # close
                        float(candle[5])     # volume
                    ])
            
            return normalized_candles
        
        return None
    
    def get_pool_info(self, network: str, pool: str) -> Optional[Dict]:
        """
        Get detailed information about a pool
        
        Args:
            network: Network name
            pool: Pool address
            
        Returns:
            Pool information dictionary or None if error
        """
        logger.info(f"Fetching pool info for {pool} on {network}")
        
        result = self._make_request(
            f"/networks/{network}/pools/{pool}"
        )
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def get_network_pools(self, network: str, page: int = 1) -> Optional[List[Dict]]:
        """
        Get pools for a specific network
        
        Args:
            network: Network name
            page: Page number (1-based)
            
        Returns:
            List of pool objects or None if error
        """
        logger.info(f"Fetching pools for network {network}")
        
        params = {'page': page}
        
        result = self._make_request(
            f"/networks/{network}/pools",
            params=params
        )
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def search_pools(self, query: str) -> Optional[List[Dict]]:
        """
        Search pools by token symbol or name
        
        Args:
            query: Search query
            
        Returns:
            List of matching pools or None if error
        """
        logger.info(f"Searching pools for: {query}")
        
        params = {'query': query}
        
        result = self._make_request(
            "/search/pools",
            params=params
        )
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def get_trending_pools(self) -> Optional[List[Dict]]:
        """
        Get trending pools across all networks
        
        Returns:
            List of trending pools or None if error
        """
        logger.info("Fetching trending pools")
        
        result = self._make_request("/networks/trending_pools")
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def get_new_pools(self) -> Optional[List[Dict]]:
        """
        Get new pools across all networks
        
        Returns:
            List of new pools or None if error
        """
        logger.info("Fetching new pools")
        
        result = self._make_request("/networks/new_pools")
        
        if result and 'data' in result:
            return result['data']
        return None
    
    def normalize_pool_data(self, pool: Dict) -> Dict:
        """
        Normalize pool data to consistent format
        
        Args:
            pool: Raw pool data from API
            
        Returns:
            Normalized pool dictionary
        """
        attributes = pool.get('attributes', {})
        
        return {
            'id': pool.get('id', ''),
            'type': pool.get('type', ''),
            'address': attributes.get('address', ''),
            'name': attributes.get('name', ''),
            'pool_created_at': attributes.get('pool_created_at', ''),
            'token_price_usd': attributes.get('token_price_usd', '0'),
            'base_token_price_usd': attributes.get('base_token_price_usd', '0'),
            'quote_token_price_usd': attributes.get('quote_token_price_usd', '0'),
            'base_token_price_native_currency': attributes.get('base_token_price_native_currency', '0'),
            'quote_token_price_native_currency': attributes.get('quote_token_price_native_currency', '0'),
            'price_change_percentage': {
                'h1': attributes.get('price_change_percentage', {}).get('h1', 0),
                'h24': attributes.get('price_change_percentage', {}).get('h24', 0)
            },
            'transactions': {
                'h1': {
                    'buys': attributes.get('transactions', {}).get('h1', {}).get('buys', 0),
                    'sells': attributes.get('transactions', {}).get('h1', {}).get('sells', 0)
                },
                'h24': {
                    'buys': attributes.get('transactions', {}).get('h24', {}).get('buys', 0),
                    'sells': attributes.get('transactions', {}).get('h24', {}).get('sells', 0)
                }
            },
            'volume_usd': {
                'h1': attributes.get('volume_usd', {}).get('h1', 0),
                'h24': attributes.get('volume_usd', {}).get('h24', 0)
            },
            'reserve_in_usd': attributes.get('reserve_in_usd', 0),
            'market_cap_usd': attributes.get('market_cap_usd', 0),
            'fdv_usd': attributes.get('fdv_usd', 0)
        }
    
    @staticmethod
    def get_supported_networks() -> List[str]:
        """
        Get list of supported networks
        
        Returns:
            List of supported network identifiers
        """
        return [
            'ethereum',
            'bsc',
            'polygon',
            'arbitrum',
            'optimism',
            'avalanche',
            'fantom',
            'cronos',
            'aurora',
            'harmony',
            'moonbeam',
            'moonriver',
            'celo',
            'fuse',
            'dogechain',
            'evmos',
            'milkomeda',
            'kava',
            'metis',
            'smartbch',
            'syscoin',
            'oasis',
            'xdai',
            'heco',
            'okexchain',
            'solana',
            'near'
        ]
    
    @staticmethod
    def get_supported_timeframes() -> List[str]:
        """
        Get list of supported timeframes
        
        Returns:
            List of supported timeframe strings
        """
        return ['1m', '5m', '15m', '1h', '4h', '1d']
    
    def get_multiple_pools_ohlcv(self, pool_configs: List[Tuple[str, str]], 
                                timeframe: str = "5m", limit: int = 100) -> Dict[str, List]:
        """
        Get OHLCV data for multiple pools efficiently
        
        Args:
            pool_configs: List of (network, pool_address) tuples
            timeframe: Timeframe for all pools
            limit: Limit for all pools
            
        Returns:
            Dictionary mapping "network:pool" to OHLCV data
        """
        results = {}
        
        for network, pool_address in pool_configs:
            pool_key = f"{network}:{pool_address}"
            
            try:
                ohlcv = self.get_ohlcv_by_pool(network, pool_address, timeframe, limit=limit)
                if ohlcv:
                    results[pool_key] = ohlcv
                    logger.info(f"Successfully fetched OHLCV for {pool_key}")
                else:
                    logger.warning(f"No OHLCV data for {pool_key}")
                    
            except Exception as e:
                logger.error(f"Error fetching OHLCV for {pool_key}: {e}")
        
        return results


# Example usage
if __name__ == "__main__":
    client = GeckoTerminalClient()
    
    # Get OHLCV data for a Ethereum pool
    ohlcv = client.get_ohlcv_by_pool(
        network="ethereum",
        pool="0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",  # USDC/ETH pool
        timeframe="5m",
        limit=100
    )
    
    if ohlcv:
        print(f"Retrieved {len(ohlcv)} candles")
        latest_candle = ohlcv[-1]
        print(f"Latest candle: O:{latest_candle[1]}, H:{latest_candle[2]}, L:{latest_candle[3]}, C:{latest_candle[4]}")
    else:
        print("No OHLCV data retrieved")
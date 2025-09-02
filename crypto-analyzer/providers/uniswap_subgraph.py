"""
Uniswap Subgraph Client using The Graph
GraphQL endpoints for pools, swaps, volume, liquidity
Used for metrics and OHLCV fallback
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class UniswapSubgraph:
    """
    Client for Uniswap V3 Subgraph on The Graph
    """
    
    # The Graph endpoints
    ENDPOINTS = {
        'v3_ethereum': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
        'v2_ethereum': 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2',
        'v3_arbitrum': 'https://api.thegraph.com/subgraphs/name/ianlapham/arbitrum-minimal',
        'v3_optimism': 'https://api.thegraph.com/subgraphs/name/ianlapham/optimism-post-regenesis',
        'v3_polygon': 'https://api.thegraph.com/subgraphs/name/ianlapham/uniswap-v3-polygon'
    }
    
    def __init__(self, network: str = 'v3_ethereum', cache_ttl: int = 300):
        """
        Initialize Uniswap Subgraph client
        
        Args:
            network: Network identifier (v3_ethereum, v2_ethereum, etc.)
            cache_ttl: Cache time-to-live in seconds (default 300)
        """
        if network not in self.ENDPOINTS:
            raise ValueError(f"Unsupported network: {network}. Available: {list(self.ENDPOINTS.keys())}")
        
        self.network = network
        self.endpoint = self.ENDPOINTS[network]
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CryptoAnalyzer/1.0'
        })
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}
    
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
    
    def _query_subgraph(self, query: str, variables: Optional[Dict] = None) -> Optional[Dict]:
        """
        Execute GraphQL query against subgraph
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            Query result data or None if error
        """
        cache_key = f"{query}:{str(variables)}"
        
        # Check cache first
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.session.post(
                    self.endpoint,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                
                if 'errors' in data:
                    logger.error(f"GraphQL errors: {data['errors']}")
                    return None
                
                result = data.get('data')
                if result:
                    # Cache successful response
                    self._set_cache(cache_key, result)
                
                return result
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Subgraph request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
    
    def get_pool_by_id(self, pool_id: str) -> Optional[Dict]:
        """
        Get pool information by ID
        
        Args:
            pool_id: Pool contract address (lowercase)
            
        Returns:
            Pool data or None if error
        """
        query = """
        query GetPool($poolId: ID!) {
            pool(id: $poolId) {
                id
                token0 {
                    id
                    symbol
                    name
                    decimals
                }
                token1 {
                    id
                    symbol
                    name
                    decimals
                }
                feeTier
                liquidity
                sqrtPrice
                token0Price
                token1Price
                volumeUSD
                txCount
                totalValueLockedUSD
                totalValueLockedToken0
                totalValueLockedToken1
                createdAtTimestamp
            }
        }
        """
        
        result = self._query_subgraph(query, {'poolId': pool_id.lower()})
        return result.get('pool') if result else None
    
    def get_pools_by_tokens(self, token0: str, token1: str = None, 
                           limit: int = 10) -> Optional[List[Dict]]:
        """
        Get pools containing specific tokens
        
        Args:
            token0: First token address
            token1: Second token address (optional)
            limit: Maximum pools to return
            
        Returns:
            List of pools or None if error
        """
        if token1:
            # Search for specific pair
            query = """
            query GetPools($token0: String!, $token1: String!, $limit: Int!) {
                pools(
                    where: {
                        or: [
                            {token0: $token0, token1: $token1},
                            {token0: $token1, token1: $token0}
                        ]
                    },
                    orderBy: totalValueLockedUSD,
                    orderDirection: desc,
                    first: $limit
                ) {
                    id
                    token0 { id symbol name }
                    token1 { id symbol name }
                    feeTier
                    liquidity
                    totalValueLockedUSD
                    volumeUSD
                    token0Price
                    token1Price
                }
            }
            """
            variables = {'token0': token0.lower(), 'token1': token1.lower(), 'limit': limit}
        else:
            # Search for pools with token0
            query = """
            query GetPools($token: String!, $limit: Int!) {
                pools(
                    where: {
                        or: [
                            {token0: $token},
                            {token1: $token}
                        ]
                    },
                    orderBy: totalValueLockedUSD,
                    orderDirection: desc,
                    first: $limit
                ) {
                    id
                    token0 { id symbol name }
                    token1 { id symbol name }
                    feeTier
                    liquidity
                    totalValueLockedUSD
                    volumeUSD
                    token0Price
                    token1Price
                }
            }
            """
            variables = {'token': token0.lower(), 'limit': limit}
        
        result = self._query_subgraph(query, variables)
        return result.get('pools') if result else None
    
    def get_pool_metrics(self, pool_id: str, from_timestamp: int, 
                        to_timestamp: int, bucket: str = "DAY") -> Optional[Dict]:
        """
        Get pool metrics over time period
        
        Args:
            pool_id: Pool contract address
            from_timestamp: Start timestamp
            to_timestamp: End timestamp
            bucket: Time bucket (DAY, HOUR)
            
        Returns:
            Pool metrics data or None if error
        """
        # For daily data
        if bucket == "DAY":
            query = """
            query GetPoolMetrics($poolId: String!, $fromTime: Int!, $toTime: Int!) {
                poolDayDatas(
                    where: {
                        pool: $poolId,
                        date_gte: $fromTime,
                        date_lte: $toTime
                    },
                    orderBy: date,
                    orderDirection: asc
                ) {
                    id
                    date
                    liquidity
                    sqrtPrice
                    token0Price
                    token1Price
                    volumeUSD
                    volumeToken0
                    volumeToken1
                    txCount
                    open
                    high
                    low
                    close
                }
            }
            """
        else:
            # Hourly data
            query = """
            query GetPoolMetrics($poolId: String!, $fromTime: Int!, $toTime: Int!) {
                poolHourDatas(
                    where: {
                        pool: $poolId,
                        periodStartUnix_gte: $fromTime,
                        periodStartUnix_lte: $toTime
                    },
                    orderBy: periodStartUnix,
                    orderDirection: asc
                ) {
                    id
                    periodStartUnix
                    liquidity
                    sqrtPrice
                    token0Price
                    token1Price
                    volumeUSD
                    volumeToken0
                    volumeToken1
                    txCount
                    open
                    high
                    low
                    close
                }
            }
            """
        
        result = self._query_subgraph(query, {
            'poolId': pool_id.lower(),
            'fromTime': from_timestamp,
            'toTime': to_timestamp
        })
        
        data_key = 'poolDayDatas' if bucket == "DAY" else 'poolHourDatas'
        return result.get(data_key) if result else None
    
    def get_recent_swaps(self, pool_id: str, limit: int = 100) -> Optional[List[Dict]]:
        """
        Get recent swaps for a pool
        
        Args:
            pool_id: Pool contract address
            limit: Maximum swaps to return
            
        Returns:
            List of recent swaps or None if error
        """
        query = """
        query GetSwaps($poolId: String!, $limit: Int!) {
            swaps(
                where: { pool: $poolId },
                orderBy: timestamp,
                orderDirection: desc,
                first: $limit
            ) {
                id
                timestamp
                amount0
                amount1
                amountUSD
                sqrtPriceX96
                tick
                transaction {
                    id
                    blockNumber
                }
            }
        }
        """
        
        result = self._query_subgraph(query, {
            'poolId': pool_id.lower(),
            'limit': limit
        })
        
        return result.get('swaps') if result else None
    
    def swaps_to_candles(self, pool_id: str, from_timestamp: int, 
                        to_timestamp: int, bucket_minutes: int = 5) -> Optional[List[List]]:
        """
        Convert swaps to OHLCV candles (fallback method)
        
        Args:
            pool_id: Pool contract address
            from_timestamp: Start timestamp
            to_timestamp: End timestamp
            bucket_minutes: Minutes per candle (5, 15, 60, etc.)
            
        Returns:
            List of OHLCV candles: [timestamp, open, high, low, close, volume]
        """
        # Get swaps in the time range
        query = """
        query GetSwaps($poolId: String!, $fromTime: Int!, $toTime: Int!) {
            swaps(
                where: {
                    pool: $poolId,
                    timestamp_gte: $fromTime,
                    timestamp_lte: $toTime
                },
                orderBy: timestamp,
                orderDirection: asc,
                first: 1000
            ) {
                timestamp
                sqrtPriceX96
                amountUSD
            }
        }
        """
        
        result = self._query_subgraph(query, {
            'poolId': pool_id.lower(),
            'fromTime': from_timestamp,
            'toTime': to_timestamp
        })
        
        if not result or 'swaps' not in result:
            return None
        
        swaps = result['swaps']
        if not swaps:
            return None
        
        # Convert to OHLCV
        bucket_seconds = bucket_minutes * 60
        candles = []
        
        # Group swaps by time buckets
        current_bucket_start = (from_timestamp // bucket_seconds) * bucket_seconds
        bucket_swaps = []
        
        for swap in swaps:
            swap_time = int(swap['timestamp'])
            
            # Check if swap belongs to current bucket
            if current_bucket_start <= swap_time < current_bucket_start + bucket_seconds:
                bucket_swaps.append(swap)
            else:
                # Process current bucket if it has swaps
                if bucket_swaps:
                    candle = self._create_candle_from_swaps(
                        current_bucket_start, 
                        bucket_swaps
                    )
                    if candle:
                        candles.append(candle)
                
                # Start new bucket
                current_bucket_start = (swap_time // bucket_seconds) * bucket_seconds
                bucket_swaps = [swap]
        
        # Process final bucket
        if bucket_swaps:
            candle = self._create_candle_from_swaps(current_bucket_start, bucket_swaps)
            if candle:
                candles.append(candle)
        
        return candles if candles else None
    
    def _create_candle_from_swaps(self, timestamp: int, swaps: List[Dict]) -> Optional[List]:
        """
        Create OHLCV candle from list of swaps
        
        Args:
            timestamp: Candle timestamp
            swaps: List of swaps in time period
            
        Returns:
            OHLCV candle: [timestamp, open, high, low, close, volume]
        """
        if not swaps:
            return None
        
        # Convert sqrtPriceX96 to price
        prices = []
        total_volume = 0
        
        for swap in swaps:
            try:
                sqrt_price = int(swap['sqrtPriceX96'])
                # Convert sqrtPriceX96 to price: (sqrtPrice/2^96)^2
                price = (sqrt_price / (2 ** 96)) ** 2
                prices.append(price)
                total_volume += float(swap.get('amountUSD', 0))
            except (ValueError, TypeError):
                continue
        
        if not prices:
            return None
        
        return [
            timestamp,           # timestamp
            prices[0],          # open (first price)
            max(prices),        # high
            min(prices),        # low
            prices[-1],         # close (last price)
            total_volume        # volume in USD
        ]
    
    def get_top_pools(self, limit: int = 20) -> Optional[List[Dict]]:
        """
        Get top pools by TVL
        
        Args:
            limit: Maximum pools to return
            
        Returns:
            List of top pools or None if error
        """
        query = """
        query GetTopPools($limit: Int!) {
            pools(
                orderBy: totalValueLockedUSD,
                orderDirection: desc,
                first: $limit
            ) {
                id
                token0 {
                    id
                    symbol
                    name
                }
                token1 {
                    id
                    symbol
                    name
                }
                feeTier
                totalValueLockedUSD
                volumeUSD
                token0Price
                token1Price
                txCount
            }
        }
        """
        
        result = self._query_subgraph(query, {'limit': limit})
        return result.get('pools') if result else None
    
    @staticmethod
    def get_supported_networks() -> List[str]:
        """Get list of supported networks"""
        return list(UniswapSubgraph.ENDPOINTS.keys())
    
    def normalize_pool_data(self, pool: Dict) -> Dict:
        """
        Normalize pool data to consistent format
        
        Args:
            pool: Raw pool data from subgraph
            
        Returns:
            Normalized pool dictionary
        """
        return {
            'id': pool.get('id', ''),
            'address': pool.get('id', ''),
            'token0': {
                'address': pool.get('token0', {}).get('id', ''),
                'symbol': pool.get('token0', {}).get('symbol', ''),
                'name': pool.get('token0', {}).get('name', ''),
                'decimals': pool.get('token0', {}).get('decimals', 18)
            },
            'token1': {
                'address': pool.get('token1', {}).get('id', ''),
                'symbol': pool.get('token1', {}).get('symbol', ''),
                'name': pool.get('token1', {}).get('name', ''),
                'decimals': pool.get('token1', {}).get('decimals', 18)
            },
            'fee_tier': pool.get('feeTier', 0),
            'liquidity': float(pool.get('liquidity', 0)),
            'sqrt_price': pool.get('sqrtPrice', '0'),
            'token0_price': float(pool.get('token0Price', 0)),
            'token1_price': float(pool.get('token1Price', 0)),
            'volume_usd': float(pool.get('volumeUSD', 0)),
            'tvl_usd': float(pool.get('totalValueLockedUSD', 0)),
            'tx_count': int(pool.get('txCount', 0)),
            'created_at': pool.get('createdAtTimestamp', 0)
        }


# Example usage
if __name__ == "__main__":
    # Initialize client for Ethereum mainnet
    client = UniswapSubgraph('v3_ethereum')
    
    # Get WETH address
    WETH = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    USDC = "0xa0b86a33e6441c67b2e3a4e2fc4c69861f8f3ec6"
    
    # Find pools with WETH
    pools = client.get_pools_by_tokens(WETH, limit=5)
    if pools:
        print(f"Found {len(pools)} WETH pools")
        for pool in pools:
            normalized = client.normalize_pool_data(pool)
            print(f"Pool: {normalized['token0']['symbol']}/{normalized['token1']['symbol']}")
            print(f"  TVL: ${normalized['tvl_usd']:,.2f}")
            print(f"  Volume: ${normalized['volume_usd']:,.2f}")
    
    # Try to create candles from swaps (example)
    if pools:
        pool_id = pools[0]['id']
        now = int(time.time())
        yesterday = now - 86400
        
        candles = client.swaps_to_candles(pool_id, yesterday, now, bucket_minutes=60)
        if candles:
            print(f"\nGenerated {len(candles)} hourly candles from swaps")
            latest = candles[-1]
            print(f"Latest candle: O:{latest[1]:.6f}, H:{latest[2]:.6f}, L:{latest[3]:.6f}, C:{latest[4]:.6f}")
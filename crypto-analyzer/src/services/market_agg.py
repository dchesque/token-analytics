"""
Market Aggregation Service
Coordinates DEX Screener, GeckoTerminal, and Uniswap Subgraph
Provides unified interface for pool data and OHLCV candles
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

# Add providers to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'providers'))

from dexscreener_client import DexScreenerClient
from geckoterminal_client import GeckoTerminalClient  
from uniswap_subgraph import UniswapSubgraph

logger = logging.getLogger(__name__)

class MarketAggregationService:
    """
    Service to aggregate market data from multiple DEX sources
    """
    
    def __init__(self):
        """Initialize all clients"""
        self.dexscreener = DexScreenerClient()
        self.geckoterminal = GeckoTerminalClient()
        self.uniswap_subgraph = UniswapSubgraph()
        
        # Chain ID mappings between services
        self.chain_mappings = {
            'dexscreener_to_gecko': {
                'ethereum': 'ethereum',
                'bsc': 'bsc', 
                'polygon': 'polygon',
                'arbitrum': 'arbitrum',
                'optimism': 'optimism',
                'avalanche': 'avalanche'
            },
            'dexscreener_to_uniswap': {
                'ethereum': 'v3_ethereum',
                'arbitrum': 'v3_arbitrum',
                'optimism': 'v3_optimism',
                'polygon': 'v3_polygon'
            }
        }
    
    def select_primary_pool(self, pools: List[Dict]) -> Optional[Dict]:
        """
        Select primary pool based on liquidity and volume
        
        Args:
            pools: List of normalized pool data
            
        Returns:
            Best pool or None if no pools
        """
        if not pools:
            return None
        
        # Score pools based on liquidity and volume
        scored_pools = []
        
        for pool in pools:
            liquidity = float(pool.get('liquidity_usd', 0))
            volume_24h = float(pool.get('volume_24h', 0))
            
            # Calculate composite score
            # Liquidity is weighted more heavily than volume
            score = (liquidity * 0.7) + (volume_24h * 0.3)
            
            scored_pools.append((score, pool))
        
        # Return pool with highest score
        scored_pools.sort(key=lambda x: x[0], reverse=True)
        return scored_pools[0][1]
    
    def get_token_pools_snapshot(self, chain_id: str, token_address: str) -> Optional[Dict]:
        """
        Get comprehensive pool data for a token using DEX Screener
        
        Args:
            chain_id: Chain identifier (ethereum, bsc, polygon, etc.)
            token_address: Token contract address
            
        Returns:
            Normalized pool data with primary pool selected
        """
        try:
            logger.info(f"Fetching pools for {token_address} on {chain_id}")
            
            # Get pools from DEX Screener
            raw_pools = self.dexscreener.token_pairs(chain_id, token_address)
            
            if not raw_pools:
                logger.warning(f"No pools found for {token_address} on {chain_id}")
                return None
            
            # Normalize pool data
            normalized_pools = []
            for pool in raw_pools:
                normalized = self._normalize_dexscreener_pool(pool)
                if normalized:
                    normalized_pools.append(normalized)
            
            if not normalized_pools:
                return None
            
            # Select primary pool
            primary_pool = self.select_primary_pool(normalized_pools)
            
            return {
                'token_address': token_address,
                'chain_id': chain_id,
                'total_pools': len(normalized_pools),
                'primary_pool': primary_pool,
                'all_pools': normalized_pools[:10],  # Limit to top 10
                'timestamp': datetime.now().isoformat(),
                'source': 'dexscreener'
            }
            
        except Exception as e:
            logger.error(f"Error getting token pools: {e}")
            return None
    
    def get_pool_ohlcv(self, network: str, pool: str, timeframe: str = "5m", 
                      aggregate: int = 1, limit: int = 500) -> Optional[List[List]]:
        """
        Get OHLCV data with GeckoTerminal -> Uniswap Subgraph fallback
        
        Args:
            network: Network name
            pool: Pool address
            timeframe: Timeframe (5m, 15m, 1h, 4h, 1d)
            aggregate: Aggregation multiplier
            limit: Maximum candles to return
            
        Returns:
            OHLCV candles: [timestamp, open, high, low, close, volume]
        """
        try:
            # Try GeckoTerminal first
            logger.info(f"Attempting GeckoTerminal OHLCV for {pool} on {network}")
            
            geckoterminal_network = self.chain_mappings['dexscreener_to_gecko'].get(network)
            if geckoterminal_network:
                candles = self.geckoterminal.get_ohlcv_by_pool(
                    geckoterminal_network, pool, timeframe, aggregate, limit
                )
                
                if candles and len(candles) > 0:
                    logger.info(f"GeckoTerminal returned {len(candles)} candles")
                    return candles
            
            # Fallback to Uniswap Subgraph
            logger.info(f"Falling back to Uniswap Subgraph for {pool}")
            
            uniswap_network = self.chain_mappings['dexscreener_to_uniswap'].get(network)
            if uniswap_network:
                # Initialize subgraph client for specific network
                subgraph = UniswapSubgraph(uniswap_network)
                
                # Convert timeframe to minutes
                timeframe_minutes = self._timeframe_to_minutes(timeframe) * aggregate
                
                # Get last N hours of data
                hours_back = min(limit * timeframe_minutes // 60, 168)  # Max 1 week
                to_timestamp = int(time.time())
                from_timestamp = to_timestamp - (hours_back * 3600)
                
                candles = subgraph.swaps_to_candles(
                    pool, from_timestamp, to_timestamp, timeframe_minutes
                )
                
                if candles and len(candles) > 0:
                    logger.info(f"Uniswap Subgraph generated {len(candles)} candles")
                    return candles[-limit:]  # Return most recent candles
            
            logger.warning(f"No OHLCV data available for {pool} on {network}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting OHLCV data: {e}")
            return None
    
    def search_token_pools(self, query: str) -> Optional[Dict]:
        """
        Search for token pools across all supported DEXs
        
        Args:
            query: Token symbol, name, or address
            
        Returns:
            Search results with normalized pool data
        """
        try:
            logger.info(f"Searching pools for: {query}")
            
            # Search DEX Screener
            search_results = self.dexscreener.search_pairs(query)
            
            if not search_results:
                return None
            
            # Normalize and categorize results
            pools_by_chain = {}
            all_pools = []
            
            for pair in search_results:
                normalized = self._normalize_dexscreener_pool(pair)
                if normalized:
                    chain_id = normalized['chain_id']
                    
                    if chain_id not in pools_by_chain:
                        pools_by_chain[chain_id] = []
                    
                    pools_by_chain[chain_id].append(normalized)
                    all_pools.append(normalized)
            
            # Select best pools per chain
            primary_pools = {}
            for chain_id, pools in pools_by_chain.items():
                primary = self.select_primary_pool(pools)
                if primary:
                    primary_pools[chain_id] = primary
            
            return {
                'query': query,
                'total_results': len(all_pools),
                'chains_found': list(pools_by_chain.keys()),
                'primary_pools': primary_pools,
                'pools_by_chain': pools_by_chain,
                'timestamp': datetime.now().isoformat(),
                'source': 'dexscreener_search'
            }
            
        except Exception as e:
            logger.error(f"Error searching token pools: {e}")
            return None
    
    def get_multi_chain_overview(self, token_symbol: str) -> Optional[Dict]:
        """
        Get comprehensive multi-chain overview for a token
        
        Args:
            token_symbol: Token symbol (e.g., 'USDC', 'WETH')
            
        Returns:
            Multi-chain token overview
        """
        try:
            logger.info(f"Getting multi-chain overview for {token_symbol}")
            
            search_results = self.search_token_pools(token_symbol)
            if not search_results:
                return None
            
            chains_data = {}
            total_liquidity = 0
            total_volume_24h = 0
            
            # Aggregate data by chain
            for chain_id, primary_pool in search_results['primary_pools'].items():
                liquidity = float(primary_pool.get('liquidity_usd', 0))
                volume = float(primary_pool.get('volume_24h', 0))
                
                total_liquidity += liquidity
                total_volume_24h += volume
                
                chains_data[chain_id] = {
                    'primary_pool': primary_pool,
                    'pool_count': len(search_results['pools_by_chain'].get(chain_id, [])),
                    'liquidity_usd': liquidity,
                    'volume_24h_usd': volume,
                    'price_usd': primary_pool.get('price_usd', 0)
                }
            
            # Calculate market share by liquidity
            for chain_data in chains_data.values():
                liquidity = chain_data['liquidity_usd']
                chain_data['liquidity_share'] = (liquidity / total_liquidity * 100) if total_liquidity > 0 else 0
            
            return {
                'token_symbol': token_symbol,
                'chains_active': list(chains_data.keys()),
                'total_liquidity_usd': total_liquidity,
                'total_volume_24h_usd': total_volume_24h,
                'chains_data': chains_data,
                'dominant_chain': max(chains_data.keys(), key=lambda k: chains_data[k]['liquidity_usd']) if chains_data else None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting multi-chain overview: {e}")
            return None
    
    def _normalize_dexscreener_pool(self, pool: Dict) -> Optional[Dict]:
        """
        Normalize DEX Screener pool data to standard format
        
        Args:
            pool: Raw pool data from DEX Screener
            
        Returns:
            Normalized pool dictionary
        """
        try:
            liquidity = pool.get('liquidity', {})
            volume = pool.get('volume', {})
            price_change = pool.get('priceChange', {})
            base_token = pool.get('baseToken', {})
            quote_token = pool.get('quoteToken', {})
            
            return {
                'pool_address': pool.get('pairAddress', ''),
                'chain_id': pool.get('chainId', ''),
                'dex_id': pool.get('dexId', ''),
                'base_token': {
                    'address': base_token.get('address', ''),
                    'symbol': base_token.get('symbol', ''),
                    'name': base_token.get('name', '')
                },
                'quote_token': {
                    'address': quote_token.get('address', ''),
                    'symbol': quote_token.get('symbol', ''),
                    'name': quote_token.get('name', '')
                },
                'price_usd': float(pool.get('priceUsd', 0)),
                'price_native': float(pool.get('priceNative', 0)),
                'liquidity_usd': float(liquidity.get('usd', 0)),
                'volume_24h': float(volume.get('h24', 0)),
                'volume_1h': float(volume.get('h1', 0)),
                'price_change_24h': float(price_change.get('h24', 0)),
                'price_change_1h': float(price_change.get('h1', 0)),
                'created_at': pool.get('pairCreatedAt', 0),
                'info': pool.get('info', {}),
                'source': 'dexscreener'
            }
            
        except Exception as e:
            logger.error(f"Error normalizing pool data: {e}")
            return None
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        return timeframe_map.get(timeframe, 5)
    
    def get_supported_chains(self) -> List[str]:
        """Get list of supported chain IDs"""
        return list(self.chain_mappings['dexscreener_to_gecko'].keys())
    
    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes"""
        return ['1m', '5m', '15m', '1h', '4h', '1d']
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of all integrated services
        
        Returns:
            Health status of each service
        """
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # Test DEX Screener
        try:
            test_search = self.dexscreener.search_pairs('BTC')
            health_status['services']['dexscreener'] = {
                'status': 'healthy' if test_search else 'degraded',
                'last_test': 'search_pairs',
                'error': None
            }
        except Exception as e:
            health_status['services']['dexscreener'] = {
                'status': 'error',
                'last_test': 'search_pairs',
                'error': str(e)
            }
        
        # Test GeckoTerminal  
        try:
            test_networks = self.geckoterminal.get_supported_networks()
            health_status['services']['geckoterminal'] = {
                'status': 'healthy' if test_networks else 'degraded',
                'last_test': 'get_supported_networks',
                'error': None
            }
        except Exception as e:
            health_status['services']['geckoterminal'] = {
                'status': 'error',
                'last_test': 'get_supported_networks', 
                'error': str(e)
            }
        
        # Test Uniswap Subgraph
        try:
            test_pools = self.uniswap_subgraph.get_top_pools(limit=1)
            health_status['services']['uniswap_subgraph'] = {
                'status': 'healthy' if test_pools else 'degraded',
                'last_test': 'get_top_pools',
                'error': None
            }
        except Exception as e:
            health_status['services']['uniswap_subgraph'] = {
                'status': 'error',
                'last_test': 'get_top_pools',
                'error': str(e)
            }
        
        return health_status


# Singleton instance
market_aggregator = MarketAggregationService()

# Example usage
if __name__ == "__main__":
    # Test the service
    service = MarketAggregationService()
    
    # Health check
    health = service.health_check()
    print("Health Check:")
    for service_name, status in health['services'].items():
        print(f"  {service_name}: {status['status']}")
    
    # Search for WETH pools
    weth_search = service.search_token_pools("WETH")
    if weth_search:
        print(f"\nFound WETH pools on {len(weth_search['chains_found'])} chains")
        for chain in weth_search['primary_pools']:
            pool = weth_search['primary_pools'][chain]
            print(f"  {chain}: ${pool['liquidity_usd']:,.2f} liquidity")
    
    # Get multi-chain overview
    overview = service.get_multi_chain_overview("USDC")
    if overview:
        print(f"\nUSDC Multi-chain Overview:")
        print(f"  Total Liquidity: ${overview['total_liquidity_usd']:,.2f}")
        print(f"  Dominant Chain: {overview['dominant_chain']}")
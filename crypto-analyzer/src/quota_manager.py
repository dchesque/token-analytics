"""
Intelligent Quota Management for Web Research APIs
Manages API usage, priorities, and smart fallbacks
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
from enum import Enum


class APIProvider(Enum):
    """Available API providers for web research"""
    TAVILY = "tavily"
    YOU = "you"
    SERPAPI = "serpapi"
    FREE_SCRAPING = "free_scraping"


class TokenPriority(Enum):
    """Token priority levels for API usage"""
    HIGH = "high"      # BTC, ETH, BNB, SOL, ADA - use premium APIs
    MEDIUM = "medium"  # Top 20 tokens - balanced usage
    LOW = "low"        # Other tokens - prefer free methods


@dataclass
class APIQuota:
    """API quota configuration and tracking"""
    provider: str
    monthly_limit: int
    current_usage: int
    last_reset: str
    cost_per_request: float
    priority_reserved: int  # Quota reserved for high-priority tokens
    rate_limit_per_hour: int
    hourly_usage: int
    last_hour_reset: str


@dataclass
class SearchRequest:
    """Search request tracking"""
    timestamp: float
    provider: str
    token: str
    query: str
    success: bool
    response_time: float
    priority: str


class QuotaManager:
    """Intelligent quota management for web research APIs"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.quota_file = self.data_dir / "api_quotas.json"
        self.usage_file = self.data_dir / "api_usage_log.json"
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Priority tokens (can be configured)
        self.priority_tokens = self._load_priority_tokens()
        
        # API configurations (must be defined before _load_quotas)
        self.api_configs = {
            APIProvider.TAVILY: {
                'monthly_limit': 1000,
                'cost_per_request': 0.001,
                'priority_reserved': 200,  # 20% reserved for high priority
                'rate_limit_per_hour': 50,
                'timeout': 30,
                'quality_score': 9  # Highest quality
            },
            APIProvider.YOU: {
                'monthly_limit': 200,
                'cost_per_request': 0.005,
                'priority_reserved': 50,   # 25% reserved
                'rate_limit_per_hour': 20,
                'timeout': 25,
                'quality_score': 7
            },
            APIProvider.SERPAPI: {
                'monthly_limit': 100,
                'cost_per_request': 0.01,
                'priority_reserved': 30,   # 30% reserved
                'rate_limit_per_hour': 10,
                'timeout': 20,
                'quality_score': 8
            },
            APIProvider.FREE_SCRAPING: {
                'monthly_limit': 999999,  # Unlimited
                'cost_per_request': 0,
                'priority_reserved': 0,
                'rate_limit_per_hour': 30,  # Conservative rate limiting
                'timeout': 60,
                'quality_score': 4  # Lower quality but always available
            }
        }
        
        # Initialize API quotas (now that api_configs is defined)
        self.quotas = self._load_quotas()
        
        # Usage history
        self.usage_history: List[SearchRequest] = self._load_usage_history()
    
    def _load_priority_tokens(self) -> Dict[str, TokenPriority]:
        """Load token priorities from environment or defaults"""
        priority_str = os.getenv('PRIORITY_TOKENS', 'bitcoin,ethereum,binancecoin,solana,cardano')
        priority_tokens = {}
        
        # High priority tokens
        high_priority = priority_str.lower().split(',')
        for token in high_priority:
            priority_tokens[token.strip()] = TokenPriority.HIGH
        
        # Medium priority - top 50 tokens (simplified)
        medium_priority = [
            'ripple', 'dogecoin', 'polygon', 'chainlink', 'polkadot', 
            'litecoin', 'avalanche', 'uniswap', 'cosmos', 'algorand'
        ]
        
        for token in medium_priority:
            if token not in priority_tokens:
                priority_tokens[token] = TokenPriority.MEDIUM
        
        return priority_tokens
    
    def _load_quotas(self) -> Dict[APIProvider, APIQuota]:
        """Load quota data from file or create defaults"""
        try:
            if self.quota_file.exists():
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                
                quotas = {}
                for provider_str, quota_data in data.items():
                    provider = APIProvider(provider_str)
                    quotas[provider] = APIQuota(**quota_data)
                
                return quotas
            
        except Exception as e:
            print(f"Warning: Could not load quota data: {e}")
        
        # Create default quotas (always executed if file doesn't exist or on error)
        return self._create_default_quotas()
    
    def _create_default_quotas(self) -> Dict[APIProvider, APIQuota]:
        """Create default quota configuration"""
        quotas = {}
        for provider, config in self.api_configs.items():
            quotas[provider] = APIQuota(
                provider=provider.value,
                monthly_limit=config['monthly_limit'],
                current_usage=0,
                last_reset=datetime.now().replace(day=1).isoformat(),
                cost_per_request=config['cost_per_request'],
                priority_reserved=config['priority_reserved'],
                rate_limit_per_hour=config['rate_limit_per_hour'],
                hourly_usage=0,
                last_hour_reset=datetime.now().replace(minute=0, second=0).isoformat()
            )
        
        self._save_quotas_dict(quotas)
        return quotas
    
    def _save_quotas_dict(self, quotas: Dict[APIProvider, APIQuota]):
        """Save quotas dictionary to file"""
        try:
            data = {}
            for provider, quota in quotas.items():
                data[provider.value] = asdict(quota)
            
            with open(self.quota_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save quota data: {e}")
    
    def _load_usage_history(self) -> List[SearchRequest]:
        """Load usage history from file"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                
                return [SearchRequest(**req) for req in data[-1000:]]  # Keep last 1000
            
        except Exception as e:
            print(f"Warning: Could not load usage history: {e}")
        
        return []
    
    def _save_quotas(self):
        """Save quota data to file"""
        try:
            with self._lock:
                data = {}
                for provider, quota in self.quotas.items():
                    data[provider.value] = asdict(quota)
                
                with open(self.quota_file, 'w') as f:
                    json.dump(data, f, indent=2)
        
        except Exception as e:
            print(f"Warning: Could not save quota data: {e}")
    
    def _save_usage_history(self):
        """Save usage history to file"""
        try:
            with self._lock:
                # Keep only last 1000 entries
                recent_history = self.usage_history[-1000:]
                
                with open(self.usage_file, 'w') as f:
                    json.dump([asdict(req) for req in recent_history], f, indent=2)
                
                self.usage_history = recent_history
        
        except Exception as e:
            print(f"Warning: Could not save usage history: {e}")
    
    def get_token_priority(self, token: str) -> TokenPriority:
        """Get priority level for a token"""
        token_clean = token.lower().replace('-', '').replace('_', '')
        
        # Check direct matches
        if token_clean in self.priority_tokens:
            return self.priority_tokens[token_clean]
        
        # Check common aliases
        aliases = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'bnb': 'binancecoin',
            'sol': 'solana',
            'ada': 'cardano',
            'xrp': 'ripple',
            'doge': 'dogecoin',
            'matic': 'polygon',
            'dot': 'polkadot',
            'avax': 'avalanche'
        }
        
        if token_clean in aliases:
            canonical = aliases[token_clean]
            if canonical in self.priority_tokens:
                return self.priority_tokens[canonical]
        
        # Default to low priority
        return TokenPriority.LOW
    
    def _reset_monthly_quotas(self):
        """Reset quotas if new month"""
        now = datetime.now()
        current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        for provider, quota in self.quotas.items():
            last_reset = datetime.fromisoformat(quota.last_reset)
            
            if last_reset < current_month:
                quota.current_usage = 0
                quota.last_reset = current_month.isoformat()
        
        self._save_quotas()
    
    def _reset_hourly_quotas(self):
        """Reset hourly quotas if new hour"""
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        for provider, quota in self.quotas.items():
            last_hour_reset = datetime.fromisoformat(quota.last_hour_reset)
            
            if last_hour_reset < current_hour:
                quota.hourly_usage = 0
                quota.last_hour_reset = current_hour.isoformat()
        
        self._save_quotas()
    
    def can_use_api(self, provider: APIProvider, token: str, force_check: bool = False) -> Tuple[bool, str]:
        """Check if we can use specific API for a token"""
        
        # Always reset quotas first
        self._reset_monthly_quotas()
        self._reset_hourly_quotas()
        
        quota = self.quotas.get(provider)
        if not quota:
            return False, f"No quota configuration for {provider.value}"
        
        config = self.api_configs.get(provider, {})
        priority = self.get_token_priority(token)
        
        # Free scraping is always available (with rate limits)
        if provider == APIProvider.FREE_SCRAPING:
            if quota.hourly_usage >= quota.rate_limit_per_hour:
                return False, f"Hourly rate limit reached for {provider.value}"
            return True, "Free scraping available"
        
        # Check if API key is available
        api_key = self._get_api_key(provider)
        if not api_key:
            return False, f"No API key configured for {provider.value}"
        
        # Check monthly limits
        available_quota = quota.monthly_limit - quota.current_usage
        
        # For high priority tokens, check if we have quota including reserved
        if priority == TokenPriority.HIGH:
            if available_quota <= 0:
                return False, f"Monthly quota exhausted for {provider.value}"
        else:
            # For lower priority tokens, exclude reserved quota
            reserved = quota.priority_reserved
            if available_quota <= reserved:
                return False, f"Only priority quota remaining for {provider.value}"
        
        # Check hourly rate limits
        if quota.hourly_usage >= quota.rate_limit_per_hour:
            return False, f"Hourly rate limit reached for {provider.value}"
        
        return True, f"API {provider.value} available"
    
    def _get_api_key(self, provider: APIProvider) -> Optional[str]:
        """Get API key for provider"""
        key_mapping = {
            APIProvider.TAVILY: 'TAVILY_API_KEY',
            APIProvider.YOU: 'YOU_API_KEY',
            APIProvider.SERPAPI: 'SERPAPI_KEY'
        }
        
        env_var = key_mapping.get(provider)
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def get_best_provider(self, token: str, exclude: List[APIProvider] = None) -> Tuple[Optional[APIProvider], str]:
        """Get the best available provider for a token"""
        
        if exclude is None:
            exclude = []
        
        priority = self.get_token_priority(token)
        
        # Priority order based on token importance and API quality
        if priority == TokenPriority.HIGH:
            provider_order = [APIProvider.TAVILY, APIProvider.SERPAPI, APIProvider.YOU, APIProvider.FREE_SCRAPING]
        elif priority == TokenPriority.MEDIUM:
            provider_order = [APIProvider.TAVILY, APIProvider.YOU, APIProvider.SERPAPI, APIProvider.FREE_SCRAPING]
        else:
            provider_order = [APIProvider.YOU, APIProvider.TAVILY, APIProvider.FREE_SCRAPING, APIProvider.SERPAPI]
        
        # Try each provider in order
        for provider in provider_order:
            if provider in exclude:
                continue
            
            can_use, reason = self.can_use_api(provider, token)
            if can_use:
                return provider, f"Selected {provider.value}: {reason}"
        
        return None, "No providers available"
    
    def record_usage(self, provider: APIProvider, token: str, query: str, 
                    success: bool, response_time: float):
        """Record API usage"""
        
        # Update quota usage
        if provider in self.quotas:
            quota = self.quotas[provider]
            quota.current_usage += 1
            quota.hourly_usage += 1
            self._save_quotas()
        
        # Record in history
        request = SearchRequest(
            timestamp=time.time(),
            provider=provider.value,
            token=token,
            query=query,
            success=success,
            response_time=response_time,
            priority=self.get_token_priority(token).value
        )
        
        self.usage_history.append(request)
        
        # Save periodically
        if len(self.usage_history) % 10 == 0:
            self._save_usage_history()
    
    def get_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        
        cutoff_time = time.time() - (days * 24 * 3600)
        recent_requests = [req for req in self.usage_history if req.timestamp >= cutoff_time]
        
        stats = {
            'period_days': days,
            'total_requests': len(recent_requests),
            'successful_requests': len([r for r in recent_requests if r.success]),
            'failed_requests': len([r for r in recent_requests if not r.success]),
            'average_response_time': 0,
            'by_provider': {},
            'by_priority': {},
            'monthly_quotas': {},
            'estimated_monthly_cost': 0
        }
        
        if recent_requests:
            stats['average_response_time'] = sum(r.response_time for r in recent_requests) / len(recent_requests)
        
        # Stats by provider
        for provider in APIProvider:
            provider_requests = [r for r in recent_requests if r.provider == provider.value]
            stats['by_provider'][provider.value] = {
                'requests': len(provider_requests),
                'success_rate': len([r for r in provider_requests if r.success]) / max(1, len(provider_requests)),
                'avg_response_time': sum(r.response_time for r in provider_requests) / max(1, len(provider_requests))
            }
        
        # Stats by priority
        for priority in TokenPriority:
            priority_requests = [r for r in recent_requests if r.priority == priority.value]
            stats['by_priority'][priority.value] = len(priority_requests)
        
        # Monthly quota status
        for provider, quota in self.quotas.items():
            stats['monthly_quotas'][provider.value] = {
                'used': quota.current_usage,
                'limit': quota.monthly_limit,
                'remaining': quota.monthly_limit - quota.current_usage,
                'usage_percentage': (quota.current_usage / quota.monthly_limit) * 100
            }
            
            # Estimated cost
            config = self.api_configs.get(provider, {})
            cost = quota.current_usage * config.get('cost_per_request', 0)
            stats['estimated_monthly_cost'] += cost
        
        return stats
    
    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status for all providers"""
        
        self._reset_monthly_quotas()
        self._reset_hourly_quotas()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'providers': {}
        }
        
        for provider, quota in self.quotas.items():
            config = self.api_configs.get(provider, {})
            api_key_available = bool(self._get_api_key(provider)) or provider == APIProvider.FREE_SCRAPING
            
            status['providers'][provider.value] = {
                'api_key_configured': api_key_available,
                'monthly_usage': quota.current_usage,
                'monthly_limit': quota.monthly_limit,
                'monthly_remaining': quota.monthly_limit - quota.current_usage,
                'hourly_usage': quota.hourly_usage,
                'hourly_limit': quota.rate_limit_per_hour,
                'hourly_remaining': quota.rate_limit_per_hour - quota.hourly_usage,
                'priority_reserved': quota.priority_reserved,
                'cost_per_request': quota.cost_per_request,
                'quality_score': config.get('quality_score', 0),
                'estimated_monthly_cost': quota.current_usage * quota.cost_per_request
            }
        
        return status
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old usage data"""
        
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        with self._lock:
            # Keep only recent usage history
            self.usage_history = [
                req for req in self.usage_history 
                if req.timestamp >= cutoff_time
            ]
            
            self._save_usage_history()
    
    def force_reset_quotas(self, provider: APIProvider = None):
        """Force reset quotas (admin function)"""
        
        if provider:
            providers = [provider]
        else:
            providers = list(self.quotas.keys())
        
        for prov in providers:
            if prov in self.quotas:
                self.quotas[prov].current_usage = 0
                self.quotas[prov].hourly_usage = 0
                self.quotas[prov].last_reset = datetime.now().isoformat()
                self.quotas[prov].last_hour_reset = datetime.now().isoformat()
        
        self._save_quotas()
    
    def adjust_priority_tokens(self, high_priority: List[str] = None, 
                             medium_priority: List[str] = None):
        """Adjust token priorities"""
        
        if high_priority:
            for token in high_priority:
                self.priority_tokens[token.lower()] = TokenPriority.HIGH
        
        if medium_priority:
            for token in medium_priority:
                self.priority_tokens[token.lower()] = TokenPriority.MEDIUM
    
    def get_recommendation(self, token: str) -> Dict[str, Any]:
        """Get recommendation for token analysis approach"""
        
        priority = self.get_token_priority(token)
        provider, reason = self.get_best_provider(token)
        
        recommendation = {
            'token': token,
            'priority': priority.value,
            'recommended_provider': provider.value if provider else None,
            'reason': reason,
            'fallback_available': provider != APIProvider.FREE_SCRAPING,
            'estimated_quality': 0,
            'estimated_cost': 0
        }
        
        if provider:
            config = self.api_configs.get(provider, {})
            recommendation['estimated_quality'] = config.get('quality_score', 0)
            recommendation['estimated_cost'] = config.get('cost_per_request', 0)
        
        return recommendation


# Global instance
quota_manager = QuotaManager()
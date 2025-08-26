"""
AI Configuration for OpenRouter Integration
Manages models, pricing, rate limits, and tier configurations
"""

import os
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AITier(Enum):
    """User tier levels for AI access"""
    FREE = "free"
    BUDGET = "budget"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ModelTier(Enum):
    """Model performance/cost tiers"""
    FREE = "free"
    BUDGET = "budget"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ModelConfig:
    """Configuration for an OpenRouter model"""
    name: str
    display_name: str
    tier: ModelTier
    cost_per_1m_tokens: float
    max_tokens: int
    context_window: int
    capabilities: List[str]
    fallback_model: Optional[str] = None


@dataclass
class TierLimits:
    """Rate limits and quotas for each user tier"""
    daily_requests: int
    hourly_requests: int
    concurrent_requests: int
    max_tokens_per_request: int
    allowed_models: List[ModelTier]
    cache_duration: int  # seconds


class AIConfig:
    """Central configuration for AI integration"""
    
    # OpenRouter API configuration
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
    
    # Available models with configurations
    MODELS = {
        # Free tier models
        "meta-llama/llama-3.1-8b-instruct:free": ModelConfig(
            name="meta-llama/llama-3.1-8b-instruct:free",
            display_name="Llama 3.1 8B (Free)",
            tier=ModelTier.FREE,
            cost_per_1m_tokens=0.0,
            max_tokens=4096,
            context_window=131072,
            capabilities=["general_analysis", "basic_trading"],
            fallback_model=None
        ),
        
        # Budget tier models
        "meta-llama/llama-3.1-70b-instruct": ModelConfig(
            name="meta-llama/llama-3.1-70b-instruct",
            display_name="Llama 3.1 70B",
            tier=ModelTier.BUDGET,
            cost_per_1m_tokens=0.59,
            max_tokens=4096,
            context_window=131072,
            capabilities=["advanced_analysis", "technical_indicators", "trading_signals"],
            fallback_model="meta-llama/llama-3.1-8b-instruct:free"
        ),
        
        # Premium tier models
        "openai/gpt-4o-mini": ModelConfig(
            name="openai/gpt-4o-mini",
            display_name="GPT-4o Mini",
            tier=ModelTier.PREMIUM,
            cost_per_1m_tokens=0.15,
            max_tokens=16384,
            context_window=128000,
            capabilities=["expert_analysis", "complex_reasoning", "risk_assessment"],
            fallback_model="meta-llama/llama-3.1-70b-instruct"
        ),
        
        "deepseek/deepseek-chat-v3.1": ModelConfig(
    name="deepseek/deepseek-chat-v3.1",
    display_name="DeepSeek V3.1",
    tier=ModelTier.ENTERPRISE,
    cost_per_1m_tokens=0.20,  # ← CORRIGIR: Era 3.0, mas é 0.20
    max_tokens=8192,
    context_window=200000,
    capabilities=["expert_analysis", "complex_reasoning", "comprehensive_reports"],
    fallback_model="openai/gpt-4o-mini"
)
    }
    
    # User tier configurations
    TIER_LIMITS = {
        AITier.FREE: TierLimits(
            daily_requests=5,
            hourly_requests=2,
            concurrent_requests=1,
            max_tokens_per_request=2048,
            allowed_models=[ModelTier.FREE],
            cache_duration=1800  # 30 minutes
        ),
        
        AITier.BUDGET: TierLimits(
            daily_requests=25,
            hourly_requests=10,
            concurrent_requests=2,
            max_tokens_per_request=4096,
            allowed_models=[ModelTier.FREE, ModelTier.BUDGET],
            cache_duration=600  # 10 minutes
        ),
        
        AITier.PREMIUM: TierLimits(
            daily_requests=100,
            hourly_requests=30,
            concurrent_requests=3,
            max_tokens_per_request=8192,
            allowed_models=[ModelTier.FREE, ModelTier.BUDGET, ModelTier.PREMIUM],
            cache_duration=300  # 5 minutes
        ),
        
        AITier.ENTERPRISE: TierLimits(
            daily_requests=1000,
            hourly_requests=100,
            concurrent_requests=5,
            max_tokens_per_request=16384,
            allowed_models=[ModelTier.FREE, ModelTier.BUDGET, ModelTier.PREMIUM, ModelTier.ENTERPRISE],
            cache_duration=60  # 1 minute
        )
    }
    
    # Model selection preferences by tier
    PREFERRED_MODELS = {
        AITier.FREE: "meta-llama/llama-3.1-8b-instruct:free",
        AITier.BUDGET: "meta-llama/llama-3.1-70b-instruct",
        AITier.PREMIUM: "openai/gpt-4o-mini",
        AITier.ENTERPRISE: "anthropic/claude-3.5-sonnet"
    }
    
    # Cache configuration
    CACHE_CONFIG = {
        'default_duration': 600,  # 10 minutes
        'max_cache_size': 1000,   # Maximum cached responses
        'cleanup_interval': 3600  # Clean old cache every hour
    }
    
    # Rate limiting configuration
    RATE_LIMIT_CONFIG = {
        'window_size': 3600,      # 1 hour window
        'cleanup_interval': 300,  # Clean old records every 5 minutes
        'burst_multiplier': 1.5   # Allow short bursts up to 1.5x limit
    }
    
    # Feature flags
    FEATURES = {
        'ai_analysis': True,
        'trading_signals': True,
        'risk_assessment': True,
        'comparative_analysis': True,
        'market_context': True,
        'technical_analysis': True,
        'fallback_enabled': True,
        'cache_enabled': True,
        'rate_limiting': True,
        'cost_tracking': True
    }
    
    # Error handling configuration
    ERROR_CONFIG = {
        'max_retries': 3,
        'retry_delay': 1,          # seconds
        'backoff_multiplier': 2,
        'timeout': 30,             # seconds
        'fallback_timeout': 10     # seconds for fallback models
    }

    @classmethod
    def get_api_key(cls) -> str:
        """Get OpenRouter API key from environment"""
        return os.getenv('OPENROUTER_API_KEY', '')
    
    @classmethod
    def get_user_tier(cls) -> AITier:
        """Get user's AI tier from environment"""
        tier_str = os.getenv('AI_TIER', 'budget').lower()
        try:
            return AITier(tier_str)
        except ValueError:
            return AITier.BUDGET
    
    @classmethod
    def get_preferred_model(cls, tier: AITier) -> str:
        """Get preferred model for user tier"""
        return cls.PREFERRED_MODELS.get(tier, cls.PREFERRED_MODELS[AITier.BUDGET])
    
    @classmethod
    def get_tier_limits(cls, tier: AITier) -> TierLimits:
        """Get limits for specific tier"""
        return cls.TIER_LIMITS[tier]
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[ModelConfig]:
        """Get configuration for specific model"""
        return cls.MODELS.get(model_name)
    
    @classmethod
    def get_fallback_chain(cls, model_name: str) -> List[str]:
        """Get fallback chain for a model"""
        chain = [model_name]
        current = model_name
        
        while current and current in cls.MODELS:
            fallback = cls.MODELS[current].fallback_model
            if fallback and fallback not in chain:
                chain.append(fallback)
                current = fallback
            else:
                break
        
        return chain
    
    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if a feature is enabled"""
        env_key = f"ENABLE_{feature.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        
        return cls.FEATURES.get(feature, False)
    
    @classmethod
    def get_cache_duration(cls, tier: AITier) -> int:
        """Get cache duration for tier"""
        env_duration = os.getenv('AI_CACHE_DURATION')
        if env_duration:
            try:
                return int(env_duration)
            except ValueError:
                pass
        
        return cls.get_tier_limits(tier).cache_duration
    
    @classmethod
    def validate_config(cls) -> Tuple[bool, List[str]]:
        """Validate configuration and return issues"""
        issues = []
        
        # Check API key
        if not cls.get_api_key():
            issues.append("OPENROUTER_API_KEY not set in environment")
        
        # Check model configurations
        for model_name, config in cls.MODELS.items():
            if config.fallback_model and config.fallback_model not in cls.MODELS:
                issues.append(f"Invalid fallback model for {model_name}: {config.fallback_model}")
        
        # Check tier configurations
        for tier, limits in cls.TIER_LIMITS.items():
            if limits.daily_requests <= 0:
                issues.append(f"Invalid daily_requests for tier {tier.value}")
            
            if limits.max_tokens_per_request <= 0:
                issues.append(f"Invalid max_tokens_per_request for tier {tier.value}")
        
        return len(issues) == 0, issues
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get headers for OpenRouter API requests"""
        return {
            "Authorization": f"Bearer {cls.get_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://crypto-analyzer.local",
            "X-Title": "Crypto Analyzer AI"
        }


# Usage tracking utilities
class UsageTracker:
    """Track API usage and costs"""
    
    def __init__(self):
        self.usage_log = {}
        self.cost_log = {}
    
    def log_request(self, model: str, tokens_used: int, user_id: str = "default"):
        """Log a request for usage tracking"""
        timestamp = int(time.time())
        key = f"{user_id}:{model}"
        
        if key not in self.usage_log:
            self.usage_log[key] = []
        
        self.usage_log[key].append({
            'timestamp': timestamp,
            'tokens': tokens_used,
            'model': model
        })
        
        # Calculate cost
        model_config = AIConfig.get_model_config(model)
        if model_config:
            cost = (tokens_used / 1_000_000) * model_config.cost_per_1m_tokens
            
            if key not in self.cost_log:
                self.cost_log[key] = 0
            self.cost_log[key] += cost
    
    def get_daily_usage(self, user_id: str = "default", days: int = 1) -> Dict:
        """Get usage statistics for recent days"""
        cutoff = int(time.time()) - (days * 24 * 3600)
        stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0,
            'by_model': {}
        }
        
        for key, requests in self.usage_log.items():
            if not key.startswith(f"{user_id}:"):
                continue
            
            model = key.split(':', 1)[1]
            recent_requests = [r for r in requests if r['timestamp'] >= cutoff]
            
            if recent_requests:
                model_tokens = sum(r['tokens'] for r in recent_requests)
                stats['total_requests'] += len(recent_requests)
                stats['total_tokens'] += model_tokens
                stats['by_model'][model] = {
                    'requests': len(recent_requests),
                    'tokens': model_tokens
                }
        
        # Calculate total cost
        for key, cost in self.cost_log.items():
            if key.startswith(f"{user_id}:"):
                stats['total_cost'] += cost
        
        return stats
    
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Remove old usage logs"""
        cutoff = int(time.time()) - (days_to_keep * 24 * 3600)
        
        for key in list(self.usage_log.keys()):
            self.usage_log[key] = [
                r for r in self.usage_log[key] 
                if r['timestamp'] >= cutoff
            ]
            
            if not self.usage_log[key]:
                del self.usage_log[key]


# Global usage tracker instance
usage_tracker = UsageTracker()
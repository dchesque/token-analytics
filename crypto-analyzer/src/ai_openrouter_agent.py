"""
OpenRouter AI Agent for Cryptocurrency Analysis
Handles AI-powered analysis using OpenRouter API with multiple model tiers
"""

import json
import time
import asyncio
import requests
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import hashlib
import threading
from dataclasses import dataclass, asdict

from ai_config import AIConfig, AITier, ModelTier, usage_tracker
from prompts.crypto_analysis_prompts import CryptoAnalysisPrompts, AnalysisType


@dataclass
class AIResponse:
    """Standardized AI response structure"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    cached: bool = False
    processing_time: Optional[float] = None
    confidence: Optional[float] = None


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self):
        self.requests = {}
        self.lock = threading.Lock()
    
    def can_make_request(self, user_id: str, tier: AITier) -> Tuple[bool, str]:
        """Check if user can make a request"""
        with self.lock:
            now = int(time.time())
            limits = AIConfig.get_tier_limits(tier)
            
            # Initialize user tracking
            if user_id not in self.requests:
                self.requests[user_id] = {'hourly': [], 'daily': []}
            
            user_requests = self.requests[user_id]
            
            # Clean old requests
            hour_ago = now - 3600
            day_ago = now - 86400
            
            user_requests['hourly'] = [t for t in user_requests['hourly'] if t > hour_ago]
            user_requests['daily'] = [t for t in user_requests['daily'] if t > day_ago]
            
            # Check limits
            if len(user_requests['hourly']) >= limits.hourly_requests:
                return False, f"Hourly limit exceeded ({limits.hourly_requests} requests/hour)"
            
            if len(user_requests['daily']) >= limits.daily_requests:
                return False, f"Daily limit exceeded ({limits.daily_requests} requests/day)"
            
            return True, ""
    
    def record_request(self, user_id: str):
        """Record a request"""
        with self.lock:
            now = int(time.time())
            if user_id not in self.requests:
                self.requests[user_id] = {'hourly': [], 'daily': []}
            
            self.requests[user_id]['hourly'].append(now)
            self.requests[user_id]['daily'].append(now)


class ResponseCache:
    """Cache for AI responses to reduce costs and improve performance"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def _generate_key(self, prompt: str, model: str, analysis_type: str) -> str:
        """Generate cache key"""
        content = f"{prompt}{model}{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, analysis_type: str, 
            max_age: int = 600) -> Optional[AIResponse]:
        """Get cached response"""
        with self.lock:
            key = self._generate_key(prompt, model, analysis_type)
            
            if key not in self.cache:
                return None
            
            cached_data, timestamp = self.cache[key]
            
            # Check if cache is still valid
            if time.time() - timestamp > max_age:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return None
            
            # Update access time
            self.access_times[key] = time.time()
            
            # Mark response as cached
            response = AIResponse(**cached_data)
            response.cached = True
            return response
    
    def set(self, prompt: str, model: str, analysis_type: str, response: AIResponse):
        """Cache response"""
        with self.lock:
            key = self._generate_key(prompt, model, analysis_type)
            
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), 
                               key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            # Store response (without the cached flag)
            response_data = asdict(response)
            response_data['cached'] = False
            
            self.cache[key] = (response_data, time.time())
            self.access_times[key] = time.time()
    
    def clear_expired(self, max_age: int = 600):
        """Clear expired cache entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > max_age:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]


class OpenRouterAgent:
    """Main AI agent for OpenRouter integration"""
    
    def __init__(self, user_tier: AITier = None):
        self.user_tier = user_tier or AIConfig.get_user_tier()
        self.rate_limiter = RateLimiter()
        self.cache = ResponseCache(max_size=AIConfig.CACHE_CONFIG['max_cache_size'])
        self.session = requests.Session()
        self.session.headers.update(AIConfig.get_headers())
        
        # Validate configuration
        is_valid, issues = AIConfig.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid AI configuration: {'; '.join(issues)}")
    
    def analyze_token(self, token_data: Dict[str, Any], 
                     analysis_type: AnalysisType = AnalysisType.TECHNICAL,
                     user_id: str = "default",
                     preferred_model: str = None) -> AIResponse:
        """
        Analyze token using AI with specified analysis type
        
        Args:
            token_data: Token market and social data
            analysis_type: Type of analysis to perform
            user_id: User identifier for rate limiting
            preferred_model: Specific model to use (optional)
        
        Returns:
            AIResponse with analysis results
        """
        start_time = time.time()
        
        # Check if AI analysis is enabled
        if not AIConfig.is_feature_enabled('ai_analysis'):
            return AIResponse(
                success=False,
                error="AI analysis is currently disabled"
            )
        
        # Rate limiting check
        can_request, limit_message = self.rate_limiter.can_make_request(user_id, self.user_tier)
        if not can_request:
            return AIResponse(
                success=False,
                error=f"Rate limit exceeded: {limit_message}"
            )
        
        # Determine model to use
        model_name = self._select_model(preferred_model, analysis_type)
        model_config = AIConfig.get_model_config(model_name)
        
        if not model_config:
            return AIResponse(
                success=False,
                error=f"Invalid model configuration: {model_name}"
            )
        
        # Generate prompts
        try:
            system_prompt = CryptoAnalysisPrompts.get_system_prompt(analysis_type)
            user_prompt = CryptoAnalysisPrompts.get_user_prompt(
                analysis_type, **CryptoAnalysisPrompts.format_token_data(token_data)
            )
            
            # Optimize prompt for model
            user_prompt = CryptoAnalysisPrompts.optimize_prompt_for_model(
                user_prompt, model_config
            )
            
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"Error generating prompts: {str(e)}"
            )
        
        # Check cache first
        if AIConfig.is_feature_enabled('cache_enabled'):
            cache_duration = AIConfig.get_cache_duration(self.user_tier)
            cached_response = self.cache.get(
                user_prompt, model_name, analysis_type.value, cache_duration
            )
            if cached_response:
                return cached_response
        
        # Make API request
        response = self._make_api_request(
            system_prompt, user_prompt, model_name, model_config
        )
        
        if response.success:
            # Record request for rate limiting and usage tracking
            self.rate_limiter.record_request(user_id)
            if response.tokens_used:
                usage_tracker.log_request(model_name, response.tokens_used, user_id)
            
            # Cache successful response
            if AIConfig.is_feature_enabled('cache_enabled') and not response.cached:
                self.cache.set(user_prompt, model_name, analysis_type.value, response)
        
        # Add processing time
        response.processing_time = time.time() - start_time
        
        return response
    
    def _select_model(self, preferred_model: str, analysis_type: AnalysisType) -> str:
        """Select appropriate model for analysis"""
        tier_limits = AIConfig.get_tier_limits(self.user_tier)
        available_models = tier_limits.allowed_models
        
        # If preferred model is specified and allowed, use it
        if preferred_model:
            model_config = AIConfig.get_model_config(preferred_model)
            if model_config and model_config.tier in available_models:
                return preferred_model
        
        # Select default model for tier
        preferred_for_tier = AIConfig.get_preferred_model(self.user_tier)
        model_config = AIConfig.get_model_config(preferred_for_tier)
        
        if model_config and model_config.tier in available_models:
            return preferred_for_tier
        
        # Fallback to highest available model tier
        for model_tier in [ModelTier.ENTERPRISE, ModelTier.PREMIUM, ModelTier.BUDGET, ModelTier.FREE]:
            if model_tier in available_models:
                for model_name, config in AIConfig.MODELS.items():
                    if config.tier == model_tier:
                        return model_name
        
        # Ultimate fallback
        return "meta-llama/llama-3.1-8b-instruct:free"
    
    def _make_api_request(self, system_prompt: str, user_prompt: str, 
                         model_name: str, model_config) -> AIResponse:
        """Make request to OpenRouter API with fallbacks"""
        
        # Try primary model first
        response = self._single_api_request(system_prompt, user_prompt, model_name, model_config)
        
        if response.success or not AIConfig.is_feature_enabled('fallback_enabled'):
            return response
        
        # Try fallback chain
        fallback_chain = AIConfig.get_fallback_chain(model_name)[1:]  # Skip primary model
        
        for fallback_model in fallback_chain:
            fallback_config = AIConfig.get_model_config(fallback_model)
            if not fallback_config:
                continue
            
            # Check if fallback model is allowed for user tier
            tier_limits = AIConfig.get_tier_limits(self.user_tier)
            if fallback_config.tier not in tier_limits.allowed_models:
                continue
            
            print(f"Trying fallback model: {fallback_model}")
            
            response = self._single_api_request(
                system_prompt, user_prompt, fallback_model, fallback_config
            )
            
            if response.success:
                return response
        
        return AIResponse(
            success=False,
            error="All models in fallback chain failed",
            model_used=model_name
        )
    
    def _single_api_request(self, system_prompt: str, user_prompt: str,
                           model_name: str, model_config) -> AIResponse:
        """Make single API request to OpenRouter"""
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": min(
                model_config.max_tokens,
                AIConfig.get_tier_limits(self.user_tier).max_tokens_per_request
            ),
            "temperature": 0.1,  # Low temperature for consistent analysis
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            response = self.session.post(
                AIConfig.OPENROUTER_BASE_URL,
                json=payload,
                timeout=AIConfig.ERROR_CONFIG['timeout']
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            # Extract response content
            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0]['message']['content']
                
                # Try to parse as JSON first
                try:
                    parsed_content = json.loads(content)
                    if isinstance(parsed_content, dict):
                        analysis_data = parsed_content
                    else:
                        analysis_data = {"analysis": content, "raw_response": parsed_content}
                except json.JSONDecodeError:
                    # If not JSON, structure as text analysis
                    analysis_data = {"analysis": content, "format": "text"}
                
                # Extract usage information
                usage = response_data.get('usage', {})
                tokens_used = usage.get('total_tokens', 0)
                cost = (tokens_used / 1_000_000) * model_config.cost_per_1m_tokens if model_config else 0
                
                return AIResponse(
                    success=True,
                    data=analysis_data,
                    model_used=model_name,
                    tokens_used=tokens_used,
                    cost=cost,
                    confidence=self._extract_confidence(analysis_data)
                )
            else:
                return AIResponse(
                    success=False,
                    error="No response content from API",
                    model_used=model_name
                )
                
        except requests.exceptions.Timeout:
            return AIResponse(
                success=False,
                error="Request timeout",
                model_used=model_name
            )
        except requests.exceptions.HTTPError as e:
            return AIResponse(
                success=False,
                error=f"HTTP error: {e.response.status_code} - {e.response.text}",
                model_used=model_name
            )
        except requests.exceptions.RequestException as e:
            return AIResponse(
                success=False,
                error=f"Request error: {str(e)}",
                model_used=model_name
            )
        except json.JSONDecodeError:
            return AIResponse(
                success=False,
                error="Invalid JSON response from API",
                model_used=model_name
            )
        except Exception as e:
            return AIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                model_used=model_name
            )
    
    def _extract_confidence(self, analysis_data: Dict[str, Any]) -> Optional[float]:
        """Extract confidence score from analysis data"""
        if not isinstance(analysis_data, dict):
            return None
        
        # Look for confidence in common locations
        confidence_keys = [
            'confidence', 'confidence_score', 'confidence_level',
            'certainty', 'accuracy'
        ]
        
        for key in confidence_keys:
            if key in analysis_data:
                try:
                    return float(analysis_data[key])
                except (ValueError, TypeError):
                    continue
        
        # Look in nested structures
        for section in analysis_data.values():
            if isinstance(section, dict):
                for key in confidence_keys:
                    if key in section:
                        try:
                            return float(section[key])
                        except (ValueError, TypeError):
                            continue
        
        return None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of models available for current user tier"""
        tier_limits = AIConfig.get_tier_limits(self.user_tier)
        available_models = []
        
        for model_name, config in AIConfig.MODELS.items():
            if config.tier in tier_limits.allowed_models:
                available_models.append({
                    'name': model_name,
                    'display_name': config.display_name,
                    'tier': config.tier.value,
                    'cost_per_1m_tokens': config.cost_per_1m_tokens,
                    'max_tokens': config.max_tokens,
                    'capabilities': config.capabilities
                })
        
        return available_models
    
    def get_usage_stats(self, user_id: str = "default", days: int = 1) -> Dict[str, Any]:
        """Get usage statistics for user"""
        return usage_tracker.get_daily_usage(user_id, days)
    
    def compare_tokens(self, tokens_data: List[Dict[str, Any]], 
                      user_id: str = "default") -> AIResponse:
        """Compare multiple tokens using AI"""
        if not tokens_data or len(tokens_data) < 2:
            return AIResponse(
                success=False,
                error="At least 2 tokens required for comparison"
            )
        
        # Format comparison data
        comparison_data = {
            'tokens': tokens_data,
            'comparison_type': 'multi_token',
            'analysis_focus': 'comparative_analysis'
        }
        
        return self.analyze_token(
            comparison_data,
            AnalysisType.COMPARATIVE,
            user_id
        )
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        max_age = AIConfig.CACHE_CONFIG['default_duration']
        self.cache.clear_expired(max_age)
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of AI service"""
        try:
            # Test with a simple request
            test_response = self._single_api_request(
                "You are a test assistant.",
                "Respond with 'OK' if you can process this request.",
                self._select_model(None, AnalysisType.TECHNICAL),
                AIConfig.get_model_config(self._select_model(None, AnalysisType.TECHNICAL))
            )
            
            return {
                'status': 'healthy' if test_response.success else 'degraded',
                'api_accessible': test_response.success,
                'error': test_response.error if not test_response.success else None,
                'model_tested': test_response.model_used,
                'response_time': test_response.processing_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'api_accessible': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Utility functions for easy integration

def create_ai_agent(user_tier: str = None) -> OpenRouterAgent:
    """Create AI agent with specified user tier"""
    if user_tier:
        try:
            tier = AITier(user_tier.lower())
        except ValueError:
            tier = AIConfig.get_user_tier()
    else:
        tier = AIConfig.get_user_tier()
    
    return OpenRouterAgent(tier)


def quick_analysis(token_data: Dict[str, Any], 
                  analysis_type: str = "technical",
                  user_tier: str = None) -> AIResponse:
    """Quick analysis function for simple use cases"""
    try:
        analysis_enum = AnalysisType(analysis_type.lower())
    except ValueError:
        analysis_enum = AnalysisType.TECHNICAL
    
    agent = create_ai_agent(user_tier)
    return agent.analyze_token(token_data, analysis_enum)


def get_ai_health() -> Dict[str, Any]:
    """Get AI service health status"""
    try:
        agent = create_ai_agent()
        return agent.health_check()
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': f"Failed to create AI agent: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }
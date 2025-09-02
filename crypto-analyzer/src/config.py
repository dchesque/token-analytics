import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Tenta carregar .env se disponível
try:
    from dotenv import load_dotenv
    # Carrega .env do diretório raiz do projeto
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        # Debug silencioso - sem prints
    else:
        # Arquivo .env não encontrado - usa defaults
        pass
except ImportError:
    # python-dotenv não instalado, usa apenas variáveis de ambiente
    pass
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'reports'

DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# APIs gratuitas (sem key necessária)
COINGECKO_API = "https://api.coingecko.com/api/v3"
FEAR_GREED_API = "https://api.alternative.me/fng/"
DEFILLAMA_API = "https://api.llama.fi"
DEFILLAMA_API_V2 = "https://api.llama.fi"

# APIs opcionais (requerem key)
LUNARCRUSH_API_KEY = os.getenv('LUNARCRUSH_API_KEY', None)
MESSARI_API_KEY = os.getenv('MESSARI_API_KEY', None)

# URLs das APIs v4/autenticadas
LUNARCRUSH_API_V4 = "https://lunarcrush.com/api4"
MESSARI_API = "https://data.messari.io/api/v1"
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data"

# Status das APIs
LUNARCRUSH_STATUS = "REQUIRES_PAID_SUBSCRIPTION"  # v4 requer plano Individual+ ($29+/mês)

# Flags de features baseadas nas keys disponíveis
ENABLE_LUNARCRUSH = False  # Desabilitar por padrão até ter assinatura paga
ENABLE_MESSARI = MESSARI_API_KEY is not None
USE_ALTERNATIVE_SOCIAL = True  # Usa alternativas quando LunarCrush não disponível

# Thresholds para Hype Detection
HYPE_THRESHOLDS = {
    'extreme': 300,      # 300% de aumento = hype extremo
    'high': 150,         # 150% de aumento = hype alto
    'moderate': 75,      # 75% de aumento = hype moderado
    'normal': 30         # <30% = variação normal
}

# Cache durations
CACHE_DURATION = 300
CACHE_SOCIAL = 300       # 5 minutos para dados sociais
CACHE_DEFI = 600        # 10 minutos para DeFi
CACHE_FUNDAMENTAL = 900  # 15 minutos para fundamentais

# Rate limiting para novas APIs
REQUESTS_PER_MINUTE = 30

MIN_MARKET_CAP = 1_000_000
MIN_VOLUME = 100_000

STRONG_BUY_SCORE = 8
RESEARCH_SCORE = 5

# ==============================================
# HYBRID AI MODE CONFIGURATION v2024.2.1
# ==============================================

# Hybrid Mode Feature Flags
HYBRID_MODE_ENABLED = os.getenv('HYBRID_MODE_ENABLED', 'false').lower() == 'true'

# Web Research API Keys (Premium APIs with Fallbacks)
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', None)
YOU_API_KEY = os.getenv('YOU_API_KEY', None) 
SERPAPI_KEY = os.getenv('SERPAPI_KEY', None)

# Web Research Configuration
WEB_SEARCH_TIMEOUT = int(os.getenv('WEB_SEARCH_TIMEOUT', '60'))
MAX_ARTICLES_PER_QUERY = int(os.getenv('MAX_ARTICLES_PER_QUERY', '10'))
NEWS_RECENCY_HOURS = int(os.getenv('NEWS_RECENCY_HOURS', '48'))

# Priority Tokens (get premium API access)
PRIORITY_TOKENS = [
    token.strip().lower() 
    for token in os.getenv('PRIORITY_TOKENS', 'bitcoin,ethereum,binancecoin,solana,cardano').split(',')
]

# Hybrid Analysis Weights
SENTIMENT_WEIGHT = float(os.getenv('SENTIMENT_WEIGHT', '0.3'))  # 30% weight for sentiment
WEB_CONTEXT_WEIGHT = float(os.getenv('WEB_CONTEXT_WEIGHT', '0.2'))  # 20% for web context
MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', '0.4'))

# Web Scraper Configuration
WEB_SCRAPER_DELAY = float(os.getenv('WEB_SCRAPER_DELAY', '2.0'))  # 2 seconds between requests
ENABLE_WEB_SCRAPING = os.getenv('ENABLE_WEB_SCRAPING', 'true').lower() == 'true'

# API Status and Availability Checks
API_AVAILABILITY = {
    'tavily': TAVILY_API_KEY is not None,
    'you': YOU_API_KEY is not None,
    'serpapi': SERPAPI_KEY is not None,
    'free_scraping': ENABLE_WEB_SCRAPING
}

# Cache Configuration for Web Research
CACHE_WEB_RESEARCH = int(os.getenv('CACHE_WEB_RESEARCH', '21600'))  # 6 hours
CACHE_SENTIMENT = int(os.getenv('CACHE_SENTIMENT', '7200'))        # 2 hours
CACHE_NEWS = int(os.getenv('CACHE_NEWS', '3600'))                  # 1 hour

# Quota Management
DAILY_API_LIMITS = {
    'tavily': int(os.getenv('TAVILY_DAILY_LIMIT', '1000')),
    'you': int(os.getenv('YOU_DAILY_LIMIT', '200')),
    'serpapi': int(os.getenv('SERPAPI_DAILY_LIMIT', '100')),
    'free_scraping': 9999  # Unlimited but rate limited
}

# Rate Limiting for APIs (requests per hour)
HOURLY_API_LIMITS = {
    'tavily': int(os.getenv('TAVILY_HOURLY_LIMIT', '50')),
    'you': int(os.getenv('YOU_HOURLY_LIMIT', '20')),
    'serpapi': int(os.getenv('SERPAPI_HOURLY_LIMIT', '10')),
    'free_scraping': int(os.getenv('WEB_SCRAPER_HOURLY_LIMIT', '30'))
}

# Hybrid Analysis Feature Flags
HYBRID_FEATURES = {
    'sentiment_analysis': os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true',
    'recent_developments': os.getenv('ENABLE_RECENT_DEVELOPMENTS', 'true').lower() == 'true',
    'market_context': os.getenv('ENABLE_MARKET_CONTEXT', 'true').lower() == 'true',
    'narrative_detection': os.getenv('ENABLE_NARRATIVE_DETECTION', 'true').lower() == 'true',
    'contextual_scoring': os.getenv('ENABLE_CONTEXTUAL_SCORING', 'true').lower() == 'true'
}

# Quality Thresholds
MIN_ARTICLE_QUALITY = float(os.getenv('MIN_ARTICLE_QUALITY', '0.3'))
MIN_SENTIMENT_CONFIDENCE = float(os.getenv('MIN_SENTIMENT_CONFIDENCE', '0.4'))
MIN_RELEVANCE_SCORE = float(os.getenv('MIN_RELEVANCE_SCORE', '0.3'))

# Trusted News Sources (with quality weights)
TRUSTED_CRYPTO_SOURCES = {
    'cointelegraph.com': 9,
    'coindesk.com': 9,
    'decrypt.co': 8,
    'theblock.co': 8,
    'bitcoinmagazine.com': 7,
    'crypto.news': 6,
    'u.today': 6,
    'cryptonews.com': 5,
    'coingape.com': 5,
    'ambcrypto.com': 4,
    'cryptopotato.com': 4
}

# Error Handling and Fallback Configuration
ENABLE_GRACEFUL_DEGRADATION = True
FALLBACK_TO_QUANTITATIVE_ONLY = True
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1

# Debug and Logging
HYBRID_DEBUG_MODE = os.getenv('HYBRID_DEBUG_MODE', 'false').lower() == 'true'
LOG_WEB_REQUESTS = os.getenv('LOG_WEB_REQUESTS', 'false').lower() == 'true'
LOG_API_USAGE = os.getenv('LOG_API_USAGE', 'true').lower() == 'true'

class HybridConfig:
    """Hybrid AI configuration helper class"""
    
    @staticmethod
    def is_hybrid_enabled() -> bool:
        """Check if hybrid mode is enabled and at least one API is available"""
        if not HYBRID_MODE_ENABLED:
            return False
        
        # Check if at least one API source is available
        return any(API_AVAILABILITY.values())
    
    @staticmethod
    def get_available_apis() -> list:
        """Get list of available API providers"""
        return [api for api, available in API_AVAILABILITY.items() if available]
    
    @staticmethod
    def is_priority_token(token: str) -> bool:
        """Check if token is in priority list"""
        return token.lower() in PRIORITY_TOKENS
    
    @staticmethod
    def get_api_limits(api_name: str) -> dict:
        """Get API limits for specific provider"""
        return {
            'daily': DAILY_API_LIMITS.get(api_name, 0),
            'hourly': HOURLY_API_LIMITS.get(api_name, 0)
        }
    
    @staticmethod
    def should_use_premium_api(token: str) -> bool:
        """Determine if should use premium APIs for this token"""
        if HybridConfig.is_priority_token(token):
            return True
        
        # Use premium APIs for high-value tokens even if not in priority list
        high_value_indicators = ['bitcoin', 'ethereum', 'btc', 'eth']
        return any(indicator in token.lower() for indicator in high_value_indicators)
    
    @staticmethod
    def validate_configuration() -> dict:
        """Validate hybrid configuration and return status"""
        status = {
            'hybrid_enabled': HYBRID_MODE_ENABLED,
            'apis_configured': sum(API_AVAILABILITY.values()),
            'issues': [],
            'warnings': []
        }
        
        # Check for configuration issues
        if HYBRID_MODE_ENABLED and not any(API_AVAILABILITY.values()):
            status['issues'].append('Hybrid mode enabled but no APIs available')
        
        if not ENABLE_WEB_SCRAPING and not any([TAVILY_API_KEY, YOU_API_KEY, SERPAPI_KEY]):
            status['warnings'].append('No fallback web scraping and no premium APIs - limited functionality')
        
        # Check rate limits
        if WEB_SCRAPER_DELAY < 1.0:
            status['warnings'].append('Web scraper delay < 1.0 seconds may cause rate limiting issues')
        
        return status
    
    @staticmethod
    def get_hybrid_status() -> dict:
        """Get comprehensive status of hybrid system"""
        return {
            'enabled': HybridConfig.is_hybrid_enabled(),
            'available_apis': HybridConfig.get_available_apis(),
            'priority_tokens': PRIORITY_TOKENS,
            'configuration': HybridConfig.validate_configuration(),
            'features': HYBRID_FEATURES,
            'cache_settings': {
                'web_research': CACHE_WEB_RESEARCH,
                'sentiment': CACHE_SENTIMENT,
                'news': CACHE_NEWS
            }
        }

class Config:
    """Configuration class for web application"""
    
    def __init__(self):
        # Load constants from this module
        import os
        
        # Basic thresholds
        self.MIN_MARKET_CAP = MIN_MARKET_CAP
        self.MIN_VOLUME = MIN_VOLUME
        self.STRONG_BUY_SCORE = STRONG_BUY_SCORE
        self.RESEARCH_SCORE = RESEARCH_SCORE
        
        # Environment variables
        self.WEB_MODE = os.getenv('WEB_MODE', 'true').lower() == 'true'
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        self.PORT = int(os.getenv('PORT', 8000))
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.CACHE_DURATION = int(os.getenv('CACHE_DURATION', 300))
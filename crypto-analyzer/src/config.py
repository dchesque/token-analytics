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
LUNARCRUSH_API_V4 = "https://lunarcrush.com/api/v4"
MESSARI_API = "https://data.messari.io/api/v1"
CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data"

# Flags de features baseadas nas keys disponíveis
ENABLE_LUNARCRUSH = LUNARCRUSH_API_KEY is not None
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
MIN_AGE_DAYS = 180

STRONG_BUY_SCORE = 8
RESEARCH_SCORE = 5
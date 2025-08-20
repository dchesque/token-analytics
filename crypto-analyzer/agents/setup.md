# ⚙️ Agente: Setup e Configuração

## 📋 Objetivo
Configurar a estrutura completa do projeto Crypto Analyzer com todas as dependências e configurações necessárias.

## 🎯 Responsabilidades

### **1. Estrutura do Projeto**

#### **Diretórios Principais**
```
crypto-analyzer/
├── src/                    # Código fonte principal
│   ├── __init__.py
│   ├── analyzer.py        # Motor de análise
│   ├── fetcher.py         # Coleta de dados APIs
│   ├── config.py          # Configurações centralizadas
│   ├── main.py            # Interface CLI
│   ├── utils.py           # Utilitários gerais
│   └── enhanced_features.py # Funcionalidades avançadas
├── docs/                  # Documentação técnica
├── agents/               # Documentação dos agentes
├── data/                # Dados de análise (cache, histórico)
├── reports/             # Relatórios gerados
├── tests/              # Testes unitários
├── requirements.txt    # Dependências Python
├── README.md          # Documentação principal
├── .gitignore        # Arquivos ignorados pelo Git
├── install.bat       # Script de instalação Windows
└── install.sh        # Script de instalação Unix/Linux
```

### **2. Dependências Python**

#### **requirements.txt**
```txt
# Core dependencies
requests>=2.31.0,<3.0.0
pandas>=2.0.0,<2.2.0
rich>=13.5.0,<14.0.0

# Utilities
python-dotenv>=1.0.0,<2.0.0
click>=8.1.0,<9.0.0

# Development (optional)
pytest>=7.4.0,<8.0.0
black>=23.0.0,<24.0.0
flake8>=6.0.0,<7.0.0

# Documentation (optional)
mkdocs>=1.5.0,<2.0.0
mkdocs-material>=9.0.0,<10.0.0
```

### **3. Configurações Centralizadas**

#### **src/config.py**
```python
"""
Configurações centralizadas do Crypto Analyzer
Todas as configurações e constantes do sistema
"""

import os
from pathlib import Path

# ==================== ESTRUTURA DE DIRETÓRIOS ====================

BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / 'src'
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'reports'
DOCS_DIR = BASE_DIR / 'docs'
AGENTS_DIR = BASE_DIR / 'agents'

# Criar diretórios se não existirem
for directory in [DATA_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# ==================== APIs E ENDPOINTS ====================

# CoinGecko API (Free Tier)
COINGECKO_API = "https://api.coingecko.com/api/v3"
COINGECKO_ENDPOINTS = {
    'search': f"{COINGECKO_API}/search",
    'coins': f"{COINGECKO_API}/coins",
    'coin_data': f"{COINGECKO_API}/coins/{{id}}",
    'market_chart': f"{COINGECKO_API}/coins/{{id}}/market_chart",
    'global': f"{COINGECKO_API}/global"
}

# Fear & Greed Index
FEAR_GREED_API = "https://api.alternative.me/fng/"

# DeFiLlama (Optional)
DEFILLAMA_API = "https://api.llama.fi"

# ==================== RATE LIMITING ====================

# CoinGecko Free Tier Limits
REQUESTS_PER_MINUTE = 30
REQUESTS_PER_HOUR = 1000
MIN_REQUEST_DELAY = 2  # Segundos entre requests

# Cache Settings
CACHE_DURATION = 300  # 5 minutos em segundos
ENABLE_CACHE = True

# ==================== CRITÉRIOS DE ANÁLISE ====================

# Camada 1: Eliminatória
MIN_MARKET_CAP = 1_000_000      # $1M
MIN_VOLUME = 100_000            # $100K
MIN_AGE_DAYS = 180              # 6 meses
MIN_LIQUIDITY_RATIO = 0.001     # Volume/Market Cap mínimo

# Camada 2: Pontuação (0-10)
SCORING_WEIGHTS = {
    'market_cap': 2,      # 0-2 pontos
    'liquidity': 2,       # 0-2 pontos  
    'development': 2,     # 0-2 pontos
    'community': 2,       # 0-2 pontos
    'performance': 2      # 0-2 pontos
}

# Camada 3: Thresholds de Classificação
CLASSIFICATION_THRESHOLDS = {
    'strong_buy': 8,      # Score >= 8
    'buy': 6,             # Score >= 6
    'research': 5,        # Score >= 5
    'caution': 3,         # Score >= 3
    'avoid': 0            # Score < 3
}

# ==================== CLASSIFICAÇÕES CRYPTO ====================

# Estrutura de mercado crypto
MARKET_STRUCTURE = {
    'MAJORS': {
        'tokens': ['bitcoin', 'ethereum'],
        'description': 'Ativos principais do mercado',
        'allocation': '40-60% do portfolio crypto'
    },
    'LARGE_CAPS': {
        'rank_range': (3, 10),
        'description': 'Top 10 estabelecidos',
        'allocation': '20-30% do portfolio'
    },
    'MID_CAPS': {
        'rank_range': (11, 50),
        'description': 'Projetos sólidos com potencial',
        'allocation': '10-20% do portfolio'
    },
    'SMALL_CAPS': {
        'rank_range': (51, 100),
        'description': 'Alto risco, alto retorno potencial',
        'allocation': '5-10% do portfolio'
    },
    'MICRO_CAPS': {
        'rank_range': (101, 500),
        'description': 'Projetos pequenos',
        'allocation': '2-5% do portfolio'
    },
    'NANO_CAPS': {
        'rank_range': (501, float('inf')),
        'description': 'Projetos muito pequenos',
        'allocation': '0-2% do portfolio'
    }
}

# Categorias especiais
SPECIAL_CATEGORIES = {
    'MEME_COINS': ['meme-token', 'meme'],
    'STABLECOINS': ['stablecoin', 'stablecoins'],
    'DEFI_TOKENS': ['defi', 'decentralized-finance'],
    'LAYER_2': ['layer-2', 'scaling'],
    'GAMING': ['gaming', 'metaverse'],
    'AI_TOKENS': ['artificial-intelligence', 'ai']
}

# ==================== ANÁLISE TÉCNICA ====================

# Períodos para análise de momentum
MOMENTUM_PERIODS = {
    'short_term': 7,      # 7 dias
    'medium_term': 30,    # 30 dias
    'long_term': 90       # 90 dias
}

# Indicadores técnicos
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ==================== MÉTRICAS DOS MAJORS ====================

# Bitcoin (Digital Gold)
BITCOIN_METRICS = {
    'narrative': 'Digital Gold',
    'adoption_metric': 'Reserva de valor digital',
    'key_features': [
        'Supply limitado: 21M BTC',
        'Halving a cada 4 anos',
        'Rede mais segura (PoW)',
        'Primeira criptomoeda'
    ]
}

# Ethereum (World Computer)
ETHEREUM_METRICS = {
    'narrative': 'World Computer',
    'adoption_metric': 'Plataforma de smart contracts',
    'key_features': [
        'Maior ecossistema DeFi/NFT',
        'Proof of Stake desde 2022',
        'L2s para escalabilidade',
        'EVM padrão da indústria'
    ]
}

# ==================== INTERFACE E DISPLAY ====================

# Cores por classificação
CLASSIFICATION_COLORS = {
    'MAJOR': 'bright_yellow',
    'LARGE CAP': 'bright_blue',
    'MID CAP': 'blue',
    'SMALL CAP': 'cyan',
    'MICRO CAP': 'magenta',
    'NANO CAP': 'red',
    'MEME COIN': 'yellow',
    'STABLECOIN': 'green',
    'LAYER 2': 'bright_cyan',
    'DEFI': 'bright_magenta',
    'GAMING': 'bright_green',
    'AI': 'bright_white'
}

# Emojis por classificação
CLASSIFICATION_EMOJIS = {
    'MAJOR': '👑',
    'LARGE CAP': '💎',
    'MID CAP': '⭐',
    'SMALL CAP': '🔹',
    'MICRO CAP': '🔸',
    'NANO CAP': '⚡',
    'MEME COIN': '🐕',
    'STABLECOIN': '💵',
    'LAYER 2': '⚡',
    'DEFI': '🏦',
    'GAMING': '🎮',
    'AI': '🤖'
}

# ==================== LOGS E DEBUG ====================

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = DATA_DIR / 'crypto_analyzer.log'

# Debug mode
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
VERBOSE_OUTPUT = os.getenv('VERBOSE', 'False').lower() == 'true'

# ==================== VALIDAÇÃO E SANIDADE ====================

# Limites de sanidade para validação de dados
SANITY_CHECKS = {
    'max_market_cap': 10_000_000_000_000,  # $10T
    'max_price': 1_000_000,                # $1M por token
    'max_volume_ratio': 10,                # 1000% do market cap
    'max_age_days': 365 * 20,              # 20 anos
    'min_age_days': 0                      # 0 dias
}

# ==================== DISCLAIMERS E AVISOS ====================

DISCLAIMER = """
⚠️ AVISO IMPORTANTE:
Este sistema é puramente educacional e informativo.
NÃO constitui consultoria financeira ou recomendação de investimento.
Sempre faça sua própria pesquisa (DYOR) antes de tomar decisões financeiras.
Criptomoedas são ativos de alto risco e podem resultar em perdas totais.
"""

FOOTER_TEXT = """
🤖 Gerado pelo Crypto Analyzer
📚 Sistema educacional - Não é consultoria financeira
🔗 Dados via APIs públicas gratuitas
"""

# ==================== VERSIONING ====================

VERSION = "2024.1.0"
BUILD_DATE = "2024-01-15"
AUTHOR = "Crypto Analyzer Team"
LICENSE = "MIT"

# ==================== ENVIRONMENT VARIABLES ====================

# Variáveis de ambiente opcionais
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Para métricas de desenvolvimento
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # Para notificações
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')  # Para relatórios

# ==================== FEATURE FLAGS ====================

# Funcionalidades opcionais
FEATURES = {
    'enable_momentum_analysis': True,
    'enable_social_metrics': True,
    'enable_github_metrics': True,
    'enable_defi_metrics': False,  # Requer APIs adicionais
    'enable_news_sentiment': False,  # Requer APIs pagas
    'enable_on_chain_metrics': False  # Requer APIs especializadas
}

# ==================== EXPORT PARA OUTROS MÓDULOS ====================

__all__ = [
    'BASE_DIR', 'DATA_DIR', 'REPORTS_DIR',
    'COINGECKO_API', 'FEAR_GREED_API',
    'MIN_MARKET_CAP', 'MIN_VOLUME', 'MIN_AGE_DAYS',
    'REQUESTS_PER_MINUTE', 'CACHE_DURATION',
    'MARKET_STRUCTURE', 'CLASSIFICATION_COLORS', 'CLASSIFICATION_EMOJIS',
    'BITCOIN_METRICS', 'ETHEREUM_METRICS',
    'DISCLAIMER', 'VERSION'
]
```

### **4. Scripts de Instalação**

#### **install.sh (Linux/macOS)**
```bash
#!/bin/bash
# Crypto Analyzer - Script de Instalação Unix

echo "🚀 Instalando Crypto Analyzer..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.7+ primeiro."
    exit 1
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "⬇️ Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p data reports

# Verificar instalação
echo "🧪 Verificando instalação..."
python -c "from src.config import VERSION; print(f'✅ Crypto Analyzer v{VERSION} instalado com sucesso!')"

echo "🎉 Instalação concluída!"
echo "📋 Para usar:"
echo "   source venv/bin/activate"
echo "   python src/main.py bitcoin"
```

#### **install.bat (Windows)**
```bat
@echo off
echo 🚀 Instalando Crypto Analyzer...

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.7+ primeiro.
    pause
    exit /b 1
)

:: Criar ambiente virtual
echo 📦 Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate.bat

:: Instalar dependências
echo ⬇️ Instalando dependências...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Criar diretórios
echo 📁 Criando estrutura de diretórios...
if not exist data mkdir data
if not exist reports mkdir reports

:: Verificar instalação
echo 🧪 Verificando instalação...
python -c "from src.config import VERSION; print(f'✅ Crypto Analyzer v{VERSION} instalado com sucesso!')"

echo 🎉 Instalação concluída!
echo 📋 Para usar:
echo    venv\Scripts\activate.bat
echo    python src\main.py bitcoin
pause
```

### **5. Controle de Versão**

#### **.gitignore**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
.env
.env.local
.env.*.local

# Data and reports (keep structure, ignore content)
data/*.json
data/*.csv
data/*.log
reports/*.json
reports/*.md
reports/*.html
reports/*.csv

# Temporary files
*.tmp
*.temp
*.cache

# Logs
*.log
logs/

# API keys and secrets
secrets.py
config.local.py
.secrets

# Test coverage
htmlcov/
.coverage
.pytest_cache/
.tox/

# Documentation build
docs/_build/
site/
```

## 🧪 Validação e Testes

### **Verificação de Setup**
```python
#!/usr/bin/env python3
"""
Script de verificação do setup
Valida se todas as configurações estão corretas
"""

def validate_setup():
    print("🔍 Validando setup do Crypto Analyzer...")
    
    # 1. Verificar imports
    try:
        from src.config import VERSION, BASE_DIR, DATA_DIR, REPORTS_DIR
        print(f"✅ Configurações importadas (v{VERSION})")
    except ImportError as e:
        print(f"❌ Erro ao importar configurações: {e}")
        return False
    
    # 2. Verificar diretórios
    for dir_name, dir_path in [("data", DATA_DIR), ("reports", REPORTS_DIR)]:
        if dir_path.exists():
            print(f"✅ Diretório {dir_name}/ existe")
        else:
            print(f"❌ Diretório {dir_name}/ não encontrado")
            return False
    
    # 3. Verificar dependências
    required_packages = ['requests', 'pandas', 'rich']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} não instalado")
            return False
    
    # 4. Testar conectividade APIs
    try:
        import requests
        from src.config import COINGECKO_API, FEAR_GREED_API
        
        # Teste CoinGecko
        response = requests.get(f"{COINGECKO_API}/ping", timeout=5)
        if response.status_code == 200:
            print("✅ CoinGecko API acessível")
        else:
            print("⚠️ CoinGecko API com problemas")
        
        # Teste Fear & Greed
        response = requests.get(FEAR_GREED_API, timeout=5)
        if response.status_code == 200:
            print("✅ Fear & Greed API acessível")
        else:
            print("⚠️ Fear & Greed API com problemas")
            
    except Exception as e:
        print(f"⚠️ Erro ao testar APIs: {e}")
    
    print("\n🎉 Setup validado com sucesso!")
    print(f"📋 Crypto Analyzer v{VERSION} pronto para uso!")
    return True

if __name__ == "__main__":
    validate_setup()
```

## ⚠️ Considerações Importantes

### **Compatibilidade**
- Python 3.7+ obrigatório
- Compatível com Windows, macOS e Linux
- Dependências mantidas em versões estáveis
- Fallbacks para funcionalidades opcionais

### **Segurança**
- Nenhuma API key obrigatória
- Todas as APIs usadas são públicas e gratuitas
- .env e secrets excluídos do controle de versão
- Validação de entrada em todos os endpoints

### **Performance**
- Cache configurável para otimização
- Rate limiting respeitado automaticamente
- Estrutura de diretórios otimizada
- Imports lazy quando possível

### **Manutenibilidade**
- Configurações centralizadas
- Constantes bem documentadas
- Feature flags para funcionalidades experimentais
- Versionamento semântico

---

**🎯 Objetivo Final:** Setup completo e robusto que permite instalação e uso imediato do Crypto Analyzer
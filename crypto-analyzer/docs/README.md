# 📚 Documentação do Crypto Analyzer

## 📁 Estrutura do Projeto

```
crypto-analyzer/
├── src/                    # Código principal
│   ├── analyzer.py        # Motor de análise crypto
│   ├── fetcher.py         # Coleta de dados APIs
│   ├── config.py          # Configurações
│   ├── main.py           # Interface CLI
│   ├── utils.py          # Utilitários
│   └── enhanced_features.py # Funcionalidades avançadas
├── docs/                  # Documentação
├── agents/               # Documentação dos agentes
├── data/                # Dados de análise
├── reports/             # Relatórios gerados
├── tests/              # Testes unitários
└── requirements.txt    # Dependências
```

## 🔧 Componentes Principais

### 1. **CryptoAnalyzer** (`src/analyzer.py`)

Motor principal de análise que implementa sistema de 3 camadas:

#### **Camada 1: Eliminatória**
```python
def check_elimination(self, data):
    # Critérios mínimos de qualidade
    # - Market Cap > $1M
    # - Volume 24h > $100K  
    # - Token existe há > 180 dias
    # - Liquidez verificável
```

#### **Camada 2: Pontuação (0-10)**
```python
def calculate_score(self, data):
    # 5 critérios (0-2 pontos cada):
    # - Market Cap/Ranking
    # - Liquidez (Volume/Market Cap)
    # - Desenvolvimento ativo
    # - Comunidade ativa
    # - Performance/Estabilidade
```

#### **Camada 3: Classificação Crypto**
```python
def classify_token(self, score, market_data):
    # Terminologia correta do mercado crypto:
    # 👑 MAJOR: Bitcoin, Ethereum
    # 💎 LARGE CAP: Top 10 do mercado
    # ⭐ MID CAP: Projetos estabelecidos
    # 🔹 SMALL CAP: Capitalização menor
    # 🔸 MICRO CAP: Projetos pequenos
    # ⚡ NANO CAP: Projetos muito pequenos
    # 🐕 MEME COIN: Tokens meme/comunidade
    # 💵 STABLECOIN: Moedas estáveis
    # 🏦 DEFI: Tokens DeFi
    # ⚡ LAYER 2: Soluções de escalabilidade
```

### 2. **DataFetcher** (`src/fetcher.py`)

Responsável pela coleta de dados de múltiplas APIs:

#### **APIs Integradas**
- **CoinGecko API**: Dados de mercado, preços, rankings
- **Fear & Greed Index**: Sentimento do mercado
- **GitHub API**: Métricas de desenvolvimento
- **Social APIs**: Métricas de comunidade

#### **Funcionalidades**
```python
def search_token(self, query):       # Busca tokens por nome/símbolo
def get_token_data(self, token_id):  # Dados completos do token
def get_fear_greed(self):           # Índice Fear & Greed
def get_price_history(self, token_id, days): # Histórico de preços
```

#### **Rate Limiting Inteligente**
- Limite de 30 requests/minuto para CoinGecko
- Sistema de retry automático
- Cache local para otimização

### 3. **Interface CLI** (`src/main.py`)

Interface de linha de comando com funcionalidades completas:

```bash
# Análise básica
python src/main.py bitcoin

# Comparação múltipla
python src/main.py --compare bitcoin ethereum cardano

# Análise em lote
python src/main.py --batch tokens.txt

# Relatório completo
python src/main.py bitcoin --detailed --save-report
```

## 🎯 Sistema de Classificação

### **Estrutura de Mercado Crypto**

| Categoria | Descrição | Alocação Típica |
|-----------|-----------|----------------|
| **MAJORS** | Bitcoin, Ethereum | 40-60% do portfolio |
| **LARGE CAPS** | Top 10 estabelecidos | 20-30% do portfolio |
| **MID CAPS** | Projetos sólidos | 10-20% do portfolio |
| **SMALL CAPS** | Alto risco/retorno | 5-10% do portfolio |
| **SPECULATIVE** | Memes, Micro caps | 0-5% do portfolio |

### **Métricas Especiais para Majors**

#### **Bitcoin (Digital Gold)**
- Dominância de mercado
- Ciclos de halving
- Supply limitado (21M)
- Segurança da rede PoW

#### **Ethereum (World Computer)**
- Ecossistema DeFi/NFT
- TVL (Total Value Locked)
- Proof of Stake
- Layer 2 solutions

## 📊 Análise Técnica

### **Momentum de Preço**
```python
def analyze_price_momentum(self, token_id, current_data):
    # Indicadores técnicos:
    # - Posição vs médias móveis (7d, 30d)
    # - RSI simplificado
    # - Posição no range de 90 dias
    # - Análise de volume
```

### **Contexto de Mercado**
```python
def check_market_context(self):
    # Fear & Greed Index:
    # - 0-25: Extreme Fear (oportunidade)
    # - 25-45: Fear (cautela)
    # - 45-55: Neutral (equilibrado)
    # - 55-75: Greed (atenção)
    # - 75-100: Extreme Greed (risco alto)
```

## 🔧 Configuração

### **Arquivo `config.py`**
```python
# Critérios eliminatórios
MIN_MARKET_CAP = 1_000_000      # $1M
MIN_VOLUME = 100_000            # $100K
MIN_AGE_DAYS = 180              # 6 meses

# Thresholds de decisão
STRONG_BUY_SCORE = 8           # Score para "Considerar Compra"
RESEARCH_SCORE = 5             # Score para "Estudar Mais"

# Rate limiting
REQUESTS_PER_MINUTE = 30       # CoinGecko free tier
```

## 🧪 Testes

### **Testes Disponíveis**
```bash
# Teste completo do analyzer
python test_analyzer.py

# Teste das novas classificações crypto
python test_crypto_classification.py

# Teste do fetcher
python test_fetcher.py
```

### **Validação de Componentes**
- ✅ Sistema de 3 camadas funcionando
- ✅ Classificações crypto corretas
- ✅ Rate limiting implementado
- ✅ Cálculo de idade robusto
- ✅ Análise de momentum técnico

## 📝 Logs e Relatórios

### **Estrutura de Saída**
```
data/
├── analysis_history.json    # Histórico de análises
└── ...

reports/
├── bitcoin_analysis.md     # Relatórios individuais
├── portfolio_comparison.md # Comparações
└── ...
```

### **Formato de Análise**
```json
{
  "token": "BTC",
  "token_name": "Bitcoin",
  "passed_elimination": true,
  "score": 9,
  "classification": "MAJOR",
  "classification_info": {
    "classification": "MAJOR",
    "description": "Ativo principal do mercado crypto",
    "risk_level": "Estabelecido",
    "emoji": "👑"
  },
  "market_context": {...},
  "momentum_analysis": {...}
}
```

## 🚀 Uso Avançado

### **Análise Programática**
```python
from src.analyzer import CryptoAnalyzer

analyzer = CryptoAnalyzer()

# Análise individual
result = analyzer.analyze("bitcoin")

# Análise múltipla
results = analyzer.analyze_multiple(["bitcoin", "ethereum", "cardano"])

# Classificação customizada
classification = analyzer.classify_token(score=8, market_data={...})
```

### **Integração com APIs**
```python
from src.fetcher import DataFetcher

fetcher = DataFetcher()

# Busca inteligente
token_id = fetcher.search_token("BTC")  # Encontra "bitcoin"

# Dados completos
data = fetcher.get_token_data(token_id)

# Contexto de mercado
context = fetcher.get_fear_greed()
```

## ⚠️ Importante

### **Não é Consultoria Financeira**
- Sistema é **educacional e informativo**
- **NÃO constitui recomendação de investimento**
- Sempre faça sua própria pesquisa (DYOR)
- Considere sua tolerância ao risco

### **Limitações**
- Baseado em dados públicos disponíveis
- Mercado crypto é altamente volátil
- Análise técnica não garante resultados futuros
- APIs podem ter limitações de rate limiting

## 🔗 Links Úteis

- [CoinGecko API Docs](https://www.coingecko.com/en/api)
- [Fear & Greed Index](https://alternative.me/crypto/fear-and-greed-index/)
- [Crypto Market Structure](https://coinmarketcap.com/)

---

**📋 Documentação atualizada para versão final do Crypto Analyzer**
*Sistema de análise crypto com terminologia correta e funcionalidades completas*
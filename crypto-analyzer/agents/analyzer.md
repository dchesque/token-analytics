# 🧠 Agente: CryptoAnalyzer

## 📋 Objetivo
Implementar o motor principal de análise crypto com sistema de 3 camadas e classificações corretas do mercado.

## 🎯 Responsabilidades

### **1. Sistema de Análise em 3 Camadas**

#### **Camada 1: Eliminatória**
```python
def check_elimination(self, data):
    # Critérios mínimos obrigatórios:
    # - Market Cap > $1M
    # - Volume 24h > $100K
    # - Token existe há > 180 dias
    # - Liquidez verificável
```

#### **Camada 2: Pontuação (0-10)**
```python
def calculate_score(self, data):
    # 5 critérios (0-2 pontos cada):
    # - Market Cap/Ranking (estabelecimento)
    # - Liquidez (Volume/Market Cap ratio)
    # - Desenvolvimento ativo (GitHub)
    # - Comunidade ativa (Social)
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

### **2. Análise Técnica de Momentum**
```python
def analyze_price_momentum(self, token_id, current_data):
    # Indicadores técnicos:
    # - Posição vs médias móveis (7d, 30d)
    # - RSI simplificado (14 dias)
    # - Posição no range de 90 dias
    # - Análise de volume
    # - Tendência (FORTE ALTA, ALTA, NEUTRO, BAIXA, FORTE BAIXA)
```

### **3. Métricas Especiais para Majors**
```python
def analyze_major_metrics(self, token_id, data):
    # Bitcoin: Digital Gold
    # - Dominância de mercado
    # - Ciclos de halving
    # - Supply limitado
    # - Segurança PoW
    
    # Ethereum: World Computer
    # - Ecossistema DeFi/NFT
    # - TVL (Total Value Locked)
    # - Proof of Stake
    # - Layer 2 solutions
```

## 🔧 Implementação

### **Estrutura Principal**
```python
class CryptoAnalyzer:
    def __init__(self):
        self.fetcher = DataFetcher()
    
    def analyze(self, token_query):
        # Fluxo completo de análise
        token_id = self.fetcher.search_token(token_query)
        token_data = self.fetcher.get_token_data(token_id)
        
        # Camada 1: Eliminatória
        elimination_result = self.check_elimination(token_data)
        if not elimination_result['passed']:
            return rejection_result
        
        # Camada 2: Pontuação
        score_result = self.calculate_score(token_data)
        
        # Camada 3: Classificação + Contexto
        market_context = self.check_market_context()
        classification = self.classify_token(score_result['score'], token_data)
        momentum = self.analyze_price_momentum(token_id, token_data)
        
        return complete_analysis
```

### **Sistema de Pontuação Detalhado**
```python
def calculate_score(self, data):
    score = 0
    breakdown = {}
    
    # 1. MARKET CAP SCORING (0-2 pontos)
    market_cap = data.get('market_cap', 0)
    market_cap_rank = data.get('market_cap_rank', 9999)
    
    if market_cap >= 100_000_000_000:  # >= $100B (Bitcoin, Ethereum)
        breakdown['market_cap'] = 2
        score += 2
    elif market_cap >= 10_000_000_000:  # >= $10B (Top ~20)
        breakdown['market_cap'] = 2
        score += 2
    elif market_cap >= 1_000_000_000:  # >= $1B (Top ~100)
        breakdown['market_cap'] = 1
        score += 1
    else:
        breakdown['market_cap'] = 0
    
    # 2. LIQUIDEZ (0-2 pontos)
    volume = data.get('volume', 0)
    if market_cap > 0:
        volume_ratio = volume / market_cap
        if market_cap_rank <= 50 and volume > 1_000_000_000:
            breakdown['liquidity'] = 2
            score += 2
        elif volume_ratio > 0.02 or volume > 500_000_000:
            breakdown['liquidity'] = 1
            score += 1
    
    # 3. DESENVOLVIMENTO (0-2 pontos)
    github_commits = data.get('github_commits', 0)
    github_stars = data.get('github_stars', 0)
    
    if market_cap_rank <= 10 and market_cap >= 50_000_000_000:
        breakdown['development'] = 2  # Blue chips estabelecidos
        score += 2
    elif github_commits > 50 or github_stars > 1000:
        breakdown['development'] = 2
        score += 2
    elif github_commits > 10 or github_stars > 100:
        breakdown['development'] = 1
        score += 1
    
    # 4. COMUNIDADE (0-2 pontos)
    twitter_followers = data.get('twitter_followers', 0)
    reddit_subscribers = data.get('reddit_subscribers', 0)
    
    if market_cap_rank <= 5:
        breakdown['community'] = 2  # Top 5 global
        score += 2
    elif twitter_followers > 300_000 or reddit_subscribers > 500_000:
        breakdown['community'] = 2
        score += 2
    elif twitter_followers > 30_000 or reddit_subscribers > 50_000:
        breakdown['community'] = 1
        score += 1
    
    # 5. PERFORMANCE (0-2 pontos)
    price_change_30d = data.get('price_change_30d', 0)
    age_days = data.get('age_days', 0)
    
    if age_days > 730:  # Tokens estabelecidos (>2 anos)
        if price_change_30d > -30:
            breakdown['performance'] = 1
            score += 1
            if price_change_30d > 5:
                breakdown['performance'] = 2
                score += 1
    else:  # Tokens novos
        if price_change_30d > 10:
            breakdown['performance'] = 2
            score += 2
        elif price_change_30d > 0:
            breakdown['performance'] = 1
            score += 1
    
    return {'score': min(score, 10), 'breakdown': breakdown}
```

## 📊 Formato de Saída

### **Resultado Completo**
```json
{
  "token": "BTC",
  "token_name": "Bitcoin",
  "passed_elimination": true,
  "score": 9,
  "score_breakdown": {
    "market_cap": 2,
    "liquidity": 2,
    "development": 2,
    "community": 2,
    "performance": 1
  },
  "classification": "MAJOR",
  "classification_info": {
    "classification": "MAJOR",
    "description": "Ativo principal do mercado crypto",
    "risk_level": "Estabelecido",
    "emoji": "👑",
    "major_metrics": {
      "narrative": "Digital Gold",
      "key_metrics": [
        "Dominância: 58.5%",
        "Halving a cada 4 anos",
        "Supply máximo: 21M BTC",
        "Rede desde 2009"
      ]
    }
  },
  "market_context": {
    "fear_greed_index": 45,
    "market_sentiment": "Fear",
    "recommendation": "Cautela recomendada"
  },
  "momentum_analysis": {
    "trend": "ALTA",
    "emoji": "📈",
    "score": 3,
    "signals": [...],
    "technical_analysis": [...]
  },
  "strengths": [...],
  "weaknesses": [...],
  "price": 67500.00,
  "market_cap": 1350000000000,
  "volume": 25000000000
}
```

## 🧪 Validação e Testes

### **Casos de Teste Obrigatórios**
1. **Bitcoin**: Deve ser classificado como MAJOR (👑)
2. **Ethereum**: Deve ser classificado como MAJOR (👑)
3. **Cardano**: Deve ser classificado como LARGE CAP (💎)
4. **Shiba Inu**: Deve ser classificado como MEME COIN (🐕)
5. **USDC**: Deve ser classificado como STABLECOIN (💵)

### **Validação de Scores**
- Bitcoin/Ethereum: Score >= 7 (com ajuste se necessário)
- Large Caps: Score 6-8
- Mid Caps: Score 5-7
- Small Caps: Score 4-6
- Micro/Nano: Score 2-5
- Meme Coins: Score 1-4

### **Testes de Integração**
```python
# Teste completo do analyzer
python test_analyzer.py

# Teste das classificações crypto
python test_crypto_classification.py

# Análise real
python src/main.py bitcoin
```

## 🔗 Dependências

### **Módulos Necessários**
```python
from fetcher import DataFetcher
from config import MIN_MARKET_CAP, MIN_VOLUME, MIN_AGE_DAYS, STRONG_BUY_SCORE, RESEARCH_SCORE
import time
```

### **APIs Utilizadas**
- CoinGecko API (via DataFetcher)
- Fear & Greed Index (via DataFetcher)
- GitHub API (opcional, via DataFetcher)

## 📈 Funcionalidades Avançadas

### **Análise de Múltiplos Tokens**
```python
def analyze_multiple(self, tokens: list, delay_seconds: int = 3):
    # Análise em batch com rate limiting
    # Delay entre requests para evitar bloqueios
    # Relatório comparativo final
```

### **Análise de Portfolio**
```python
def analyze_portfolio(self, portfolio: dict):
    # Análise de diversificação
    # Risk/Return por categoria
    # Recomendações de rebalanceamento
```

## ⚠️ Considerações Importantes

### **Rate Limiting**
- Respeitar limite de 30 requests/minuto do CoinGecko
- Implementar delays entre análises múltiplas
- Sistema de retry em caso de falha

### **Tratamento de Erros**
- Fallbacks para dados indisponíveis
- Estimativas inteligentes quando necessário
- Logs detalhados para debugging

### **Responsabilidade**
- Sistema é puramente educacional/informativo
- NÃO constitui consultoria financeira
- Sempre incluir disclaimers apropriados

---

**🎯 Objetivo Final:** Motor de análise crypto robusto, preciso e com terminologia correta do mercado
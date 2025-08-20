# 🔍 Agente: DataFetcher

## 📋 Objetivo
Implementar o sistema de coleta de dados de múltiplas APIs crypto com rate limiting inteligente e robustez.

## 🎯 Responsabilidades

### **1. Integração com APIs Crypto**

#### **CoinGecko API (Principal)**
```python
# Endpoints utilizados:
# - /search: Busca de tokens por nome/símbolo
# - /coins/{id}: Dados completos do token
# - /coins/{id}/market_chart: Histórico de preços
# - /global: Dados globais do mercado
```

#### **Fear & Greed Index**
```python
# Alternative.me API
# - /fng/: Índice de medo e ganância do mercado
```

#### **APIs Sociais (Opcionais)**
```python
# GitHub API: Métricas de desenvolvimento
# Twitter API: Métricas de comunidade
# Reddit API: Métricas de comunidade
```

### **2. Funcionalidades Principais**

#### **Busca Inteligente de Tokens**
```python
def search_token(self, query):
    # Busca flexível:
    # - "BTC" → "bitcoin"
    # - "ETH" → "ethereum"  
    # - "Bitcoin" → "bitcoin"
    # - "Ethereum" → "ethereum"
    # - Suporte a variações e sinônimos
```

#### **Coleta de Dados Completos**
```python
def get_token_data(self, token_id):
    # Dados coletados:
    # - Preço atual e variações (24h, 7d, 30d)
    # - Market cap e ranking
    # - Volume de negociação
    # - Dados de desenvolvimento (GitHub)
    # - Métricas de comunidade (Social)
    # - Idade do token (genesis_date)
    # - Categorias e tags
```

#### **Histórico de Preços**
```python
def get_price_history(self, token_id, days):
    # Dados históricos:
    # - Preços diários
    # - Volumes
    # - Market caps
    # - Cálculo de médias móveis
    # - Identificação de extremos
```

### **3. Cálculo Robusto de Idade**

#### **Múltiplas Estratégias**
```python
def calculate_age_days(self, token_id, genesis_date, market_data):
    # Estratégia 1: Genesis date direto
    if genesis_date:
        return parse_genesis_date(genesis_date)
    
    # Estratégia 2: Histórico de preços
    age_from_history = self.get_age_from_history(token_id)
    if age_from_history > 0:
        return age_from_history
    
    # Estratégia 3: Estimativa por métricas
    return self.estimate_age_by_metrics(market_data)
```

#### **Parsing Robusto de Datas**
```python
def parse_genesis_date(self, genesis_date):
    # Formatos suportados:
    # - "2009-01-03"
    # - "2009-01-03T18:15:05"
    # - "2009-01-03T18:15:05.000Z"
    # - Limpeza automática de timezone
    # - Fallback para estimativas
```

## 🔧 Implementação

### **Estrutura Principal**
```python
class DataFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
    def _rate_limit(self):
        # Rate limiting inteligente
        # 30 requests/minuto para CoinGecko
        # Delay automático quando necessário
```

### **Rate Limiting Avançado**
```python
def _rate_limit(self):
    current_time = time.time()
    
    # Reset contador a cada minuto
    if current_time - self.request_window_start >= 60:
        self.request_count = 0
        self.request_window_start = current_time
    
    # Verificar limite
    if self.request_count >= REQUESTS_PER_MINUTE:
        sleep_time = 60 - (current_time - self.request_window_start)
        if sleep_time > 0:
            print(f"⏳ Rate limit: aguardando {sleep_time:.1f}s...")
            time.sleep(sleep_time)
            self.request_count = 0
            self.request_window_start = time.time()
    
    # Delay mínimo entre requests
    time_since_last = current_time - self.last_request_time
    if time_since_last < 2:  # Mínimo 2s entre requests
        time.sleep(2 - time_since_last)
    
    self.last_request_time = time.time()
    self.request_count += 1
```

### **Tratamento de Erros Robusto**
```python
def _make_request(self, url, params=None, retries=3):
    for attempt in range(retries):
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                wait_time = 60 * (attempt + 1)
                print(f"⏳ Rate limited. Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"⚠️ HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erro de rede (tentativa {attempt + 1}): {e}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    
    return None
```

## 📊 Estrutura de Dados

### **Token Data Completo**
```python
{
    "id": "bitcoin",
    "symbol": "BTC",
    "name": "Bitcoin",
    "price": 67500.00,
    "market_cap": 1350000000000,
    "market_cap_rank": 1,
    "volume": 25000000000,
    "price_change_24h": 2.5,
    "price_change_7d": -1.2,
    "price_change_30d": 15.8,
    "age_days": 5475,
    "genesis_date": "2009-01-03",
    "categories": ["cryptocurrency"],
    "github_commits": 150,
    "github_stars": 45000,
    "twitter_followers": 5000000,
    "reddit_subscribers": 3500000,
    "total_supply": 21000000,
    "circulating_supply": 19750000,
    "ath": 69000,
    "atl": 0.05
}
```

### **Histórico de Preços**
```python
{
    "prices": [[timestamp, price], ...],
    "volumes": [[timestamp, volume], ...],
    "market_caps": [[timestamp, market_cap], ...],
    "current_price": 67500.00,
    "avg_7d": 66800.00,
    "avg_30d": 65200.00,
    "max_90d": 70000.00,
    "min_90d": 58000.00,
    "volatility_30d": 0.12
}
```

### **Context de Mercado**
```python
{
    "fear_greed_index": 45,
    "fear_greed_classification": "Fear",
    "btc_dominance": 58.5,
    "total_market_cap": 2350000000000,
    "total_volume_24h": 85000000000,
    "active_cryptocurrencies": 12000
}
```

## 🧪 Validação e Testes

### **Casos de Teste Críticos**
```python
# Teste de busca
def test_search_functionality():
    fetcher = DataFetcher()
    
    # Testes de busca flexível
    assert fetcher.search_token("BTC") == "bitcoin"
    assert fetcher.search_token("Bitcoin") == "bitcoin"
    assert fetcher.search_token("ETH") == "ethereum"
    assert fetcher.search_token("Ethereum") == "ethereum"

# Teste de cálculo de idade
def test_age_calculation():
    fetcher = DataFetcher()
    
    # Tokens conhecidos
    pendle_data = fetcher.get_token_data("pendle")
    assert pendle_data['age_days'] > 800  # > 2 anos
    
    chainlink_data = fetcher.get_token_data("chainlink")
    assert chainlink_data['age_days'] > 2000  # > 5 anos

# Teste de rate limiting
def test_rate_limiting():
    fetcher = DataFetcher()
    
    start_time = time.time()
    
    # Fazer múltiplas requests
    for i in range(5):
        fetcher.get_token_data("bitcoin")
    
    elapsed = time.time() - start_time
    assert elapsed >= 8  # Mínimo 2s entre cada request
```

### **Validação de Dados**
```python
def validate_token_data(data):
    required_fields = [
        'id', 'symbol', 'name', 'price', 'market_cap', 
        'market_cap_rank', 'volume', 'age_days'
    ]
    
    for field in required_fields:
        assert field in data, f"Campo obrigatório ausente: {field}"
        assert data[field] is not None, f"Campo não pode ser None: {field}"
    
    # Validações específicas
    assert data['price'] > 0, "Preço deve ser positivo"
    assert data['market_cap'] > 0, "Market cap deve ser positivo"
    assert data['volume'] >= 0, "Volume não pode ser negativo"
    assert data['age_days'] >= 0, "Idade não pode ser negativa"
```

## 🔗 APIs e Endpoints

### **CoinGecko API**
```python
BASE_URL = "https://api.coingecko.com/api/v3"

ENDPOINTS = {
    'search': f"{BASE_URL}/search",
    'coin_data': f"{BASE_URL}/coins/{{id}}",
    'market_chart': f"{BASE_URL}/coins/{{id}}/market_chart",
    'global': f"{BASE_URL}/global"
}
```

### **Fear & Greed Index**
```python
FEAR_GREED_URL = "https://api.alternative.me/fng/"
```

### **Rate Limits**
```python
COINGECKO_LIMITS = {
    'requests_per_minute': 30,  # Free tier
    'requests_per_hour': 1000,  # Free tier
    'min_delay_between_requests': 2  # Seconds
}
```

## ⚠️ Considerações Importantes

### **Rate Limiting**
- CoinGecko free tier: 30 requests/minuto
- Implementar delays inteligentes
- Sistema de retry em caso de rate limiting
- Cache local para otimização

### **Tratamento de Erros**
- Timeout de 10 segundos por request
- Retry automático com backoff exponencial
- Fallbacks para dados indisponíveis
- Logs detalhados para debugging

### **Cálculo de Idade**
- Múltiplas estratégias em cascata
- Estimativas inteligentes quando necessário
- Validação de sanidade dos resultados
- Suporte a diferentes formatos de data

### **Performance**
- Session reutilizável para conexões
- Cache de resultados quando apropriado
- Otimização de requests em lote
- Monitoramento de performance

---

**🎯 Objetivo Final:** Sistema robusto e confiável de coleta de dados crypto com rate limiting inteligente
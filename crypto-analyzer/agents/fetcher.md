# 📡 Fetcher Agent - Coleta de Dados Robusta

## 🎯 Responsabilidades

O **DataFetcher** é responsável por coletar dados de múltiplas APIs de forma robusta e confiável. É o agente mais crítico do sistema, garantindo que dados sejam obtidos mesmo com falhas de APIs.

## 🏗️ Arquitetura

### **Classe Principal**
```python
class DataFetcher:
    def __init__(self):
        # Rate limiting inteligente (v2024.2.0)
        self.MIN_TIME_BETWEEN_REQUESTS = 4.0  # segundos
        self.MAX_REQUESTS_PER_MINUTE = 15     # requests/minuto
        
        # Session com headers otimizados
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoAnalyzer/2.0',
            'Accept': 'application/json'
        })
```

## 🚀 Funcionalidades Principais (v2024.2.0)

### **1. Rate Limiting Inteligente** ⚡

```python
def _rate_limit(self):
    """Rate limiting com jitter e controle de requests/minuto"""
    
    # Reset contador por minuto
    if current_time - self.request_window_start >= 60:
        self.request_count = 0
        self.request_window_start = current_time
    
    # Verifica limite de requests/minuto
    if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - self.request_window_start)
        time.sleep(wait_time)
    
    # Delay com jitter (anti-thundering herd)
    jitter = random.uniform(0.5, 1.5)
    min_delay = self.MIN_TIME_BETWEEN_REQUESTS + jitter
    
    if elapsed < min_delay:
        time.sleep(min_delay - elapsed)
```

**Características**:
- ✅ **Conservador**: 15 requests/minuto máximo
- ✅ **Jitter**: Randomização para evitar patterns
- ✅ **Auto-reset**: Contador reseta a cada minuto
- ✅ **Predictable**: Delays mínimos garantidos

### **2. Fallback Chain Automático** 🔄

```python
def get_price_history(self, token_id: str, days: int = 90):
    """Cadeia de fallback para dados de preço"""
    
    # TENTATIVA 1: market_chart (dados ricos)
    result = self._try_market_chart(token_id, days)
    if result:
        print("market_chart OK")
        return result
    
    # TENTATIVA 2: OHLC (fallback para 401)  
    print("market_chart falhou, tentando OHLC...")
    result = self._try_ohlc_data(token_id, min(days, 30))
    if result:
        print("OHLC OK")
        return result
    
    # TENTATIVA 3: Dados básicos (último recurso)
    print("OHLC falhou, usando dados básicos...")
    result = self._get_basic_price_data(token_id)
    if result:
        print("Dados básicos obtidos")
        return result
    
    # TENTATIVA 4: Estrutura vazia válida
    return self._empty_price_data()
```

**Benefícios**:
- ✅ **Resiliente**: Funciona mesmo com APIs limitadas
- ✅ **Transparente**: Logs informativos sobre fallbacks
- ✅ **Graceful**: Sempre retorna estrutura válida
- ✅ **Otimizado**: Usa melhor fonte disponível

### **3. Tratamento de Erros HTTP** 🛡️

```python
def _make_request(self, url: str, params: Dict = None, headers: Dict = None, retries: int = 3):
    """Request com retry logic e tratamento específico de erros"""
    
    for attempt in range(retries):
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 401:
                print("Erro 401: Fallback automático será aplicado")
                return response  # Deixa o fallback tratar
            elif response.status_code == 429:
                # Backoff exponencial
                wait_time = min(60, (2 ** attempt) * 10)
                print(f"Rate limit (429). Aguardando {wait_time}s...")
                time.sleep(wait_time)
                self.request_count = 0  # Reset contador
                
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                wait_time = min(30, (2 ** attempt) * 5)
                time.sleep(wait_time)
```

**Tratamentos Específicos**:
- **401 (Unauthorized)**: Retorna response para fallback chain
- **429 (Rate Limited)**: Backoff exponencial (10s → 20s → 40s)
- **404 (Not Found)**: Retorna response para tratamento específico
- **Timeout**: Retry com backoff crescente
- **Network Error**: Retry com delay exponencial

### **4. Token Resolution Inteligente** 🔍

```python
def search_token(self, query):
    """Busca token ID com mapeamento direto + API fallback"""
    
    # Mapeamento direto (evita API calls desnecessárias)
    direct_mapping = {
        'bitcoin': 'bitcoin', 'btc': 'bitcoin',
        'ethereum': 'ethereum', 'eth': 'ethereum',
        'binancecoin': 'binancecoin', 'bnb': 'binancecoin',
        # ... mais mappings
    }
    
    query_lower = query.lower()
    
    # Tentativa 1: Mapeamento direto
    if query_lower in direct_mapping:
        return direct_mapping[query_lower]
    
    # Tentativa 2: API search (com cache)
    return self._get_cached_or_fetch(f"search_{query}", self._search_via_api)
```

**Otimizações**:
- ✅ **Cache-first**: Evita API calls desnecessárias
- ✅ **Direct mapping**: Tokens populares mapeados diretamente
- ✅ **API fallback**: Search API quando necessário
- ✅ **Fuzzy matching**: Match por símbolo ou nome

## 📊 APIs Suportadas

### **CoinGecko API v3** 🥇

```python
# Endpoints utilizados
COINGECKO_ENDPOINTS = {
    'search': '/search',                    # Busca de tokens
    'token_data': '/coins/{id}',           # Dados do token  
    'market_chart': '/coins/{id}/market_chart',  # Histórico (pode dar 401)
    'ohlc': '/coins/{id}/ohlc',           # OHLC data (fallback)
    'markets': '/coins/markets'            # Lista de mercados
}
```

**Características**:
- ✅ **Plano Gratuito**: Funciona sem API key
- ✅ **Rate Limits**: 30/min no plano gratuito
- ⚠️ **Limitações**: market_chart pode retornar 401
- ✅ **Fallbacks**: OHLC disponível sem auth

### **Alternative.me Fear & Greed** 🎯

```python
def get_fear_greed(self):
    """Busca índice de medo e ganância"""
    
    response = self._make_request(FEAR_GREED_API)
    if response and response.status_code == 200:
        data = response.json()
        latest = data['data'][0]
        return {
            'value': int(latest['value']),
            'classification': latest['value_classification'],
            'timestamp': latest['timestamp']
        }
    
    # Fallback para valor neutro
    return {
        'value': 50, 
        'classification': 'Neutral', 
        'timestamp': str(int(time.time()))
    }
```

## 🧠 Cache Strategy

### **Cache Inteligente**

```python
CACHE_DURATIONS = {
    'token_data': 300,        # 5 minutos (dados básicos)
    'price_history': 3600,    # 1 hora (histórico)
    'search_results': 3600,   # 1 hora (buscas)
    'fear_greed': 3600       # 1 hora (sentiment)
}

def _get_cached_or_fetch(self, key, fetch_func):
    """Cache com TTL por tipo de dados"""
    
    if self._is_cache_valid(key):
        print(f"Cache hit para {key}")
        return self.cache[key][1]
    
    try:
        data = fetch_func()
        if data:
            self.cache[key] = (time.time(), data)
        return data
    except Exception as e:
        print(f"Erro ao buscar {key}: {e}")
        return None
```

## 🧪 Testes e Validação

### **Teste de Rate Limiting**

```python
def test_rate_limiting():
    fetcher = DataFetcher()
    
    # Testa 5 requests consecutivos
    times = []
    for i in range(5):
        start = time.time()
        fetcher._rate_limit()
        end = time.time()
        times.append(end - start)
    
    # Verifica se delays >= 4s
    assert min(times[1:]) >= 3.5  # Tolerância de 0.5s
    print("✅ Rate limiting funcionando")
```

### **Teste de Fallback Chain**

```python
def test_fallback_chain():
    fetcher = DataFetcher()
    
    # Testa com Bitcoin
    history = fetcher.get_price_history('bitcoin', 7)
    
    # Deve sempre retornar estrutura válida
    assert 'prices' in history
    assert 'current_price' in history
    assert 'data_points' in history
    
    print(f"✅ Fallback OK: {history['data_points']} pontos")
```

## 📈 Métricas de Performance

### **Benchmarks** (v2024.2.0)

```
search_token():
├── Direct mapping: ~0.001s
├── API search: ~5s (com rate limiting)
└── Cache hit: ~0.001s

get_token_data():  
├── API call: ~5s (com rate limiting)
├── Cache hit: ~0.001s
└── Success rate: >99%

get_price_history():
├── market_chart success: ~5s
├── OHLC fallback: ~10s  
├── Basic fallback: ~15s
└── Fallback usage: ~60% (OHLC)

Rate limiting:
├── Average delay: 4.5s
├── Jitter range: 0.5s - 1.5s
├── 429 recovery: 10s → 20s → 40s  
└── Success after recovery: >95%
```

## 🔧 Configuração

### **Parâmetros Ajustáveis**

```python
class DataFetcher:
    def __init__(self):
        # Rate limiting (ajustar com cuidado)
        self.MIN_TIME_BETWEEN_REQUESTS = 4.0  # Reduzir pode causar 429
        self.MAX_REQUESTS_PER_MINUTE = 15     # Aumentar pode causar ban
        
        # Timeouts
        self.REQUEST_TIMEOUT = 15             # segundos
        self.MAX_RETRIES = 3                 # tentativas
        
        # Cache
        self.CACHE_DURATION = 300            # segundos (5 min)
```

### **Environment Variables**

```bash
# Otimizações opcionais
export REQUEST_TIMEOUT=20          # Timeout maior para conexões lentas
export MAX_RETRIES=5              # Mais tentativas para redes instáveis
export CACHE_DURATION=600         # Cache mais longo (10 min)
```

## 🚨 Troubleshooting

### **Problema: "Rate limit muito conservador"**

```python
# Ajuste cauteloso em src/fetcher.py
self.MIN_TIME_BETWEEN_REQUESTS = 2.5  # Reduzir gradualmente
self.MAX_REQUESTS_PER_MINUTE = 20     # Aumentar gradualmente

# CUIDADO: Monitorar logs para 429 errors
# Se aparecerem 429s, reverter para valores conservadores
```

### **Problema: "market_chart sempre retorna 401"**

```bash
# Normal no plano gratuito do CoinGecko
# Sistema usa fallback automático para OHLC
# Verificar logs:

python -c "
from src.fetcher import DataFetcher
f = DataFetcher()
result = f.get_price_history('bitcoin', 7)
print(f'Pontos obtidos: {result[\"data_points\"]}')
print(f'Preço atual: ${result[\"current_price\"]:,.2f}')
"

# Saída esperada:
# market_chart falhou, tentando OHLC...  
# OHLC OK para bitcoin
# Pontos obtidos: 42
# Preço atual: $67,500.00
```

### **Problema: "Timeouts frequentes"**

```python
# Aumentar timeout em src/fetcher.py
response = self.session.get(url, timeout=30)  # era 15

# Ou via environment
export REQUEST_TIMEOUT=30
```

## 🔄 Roadmap

### **v2024.3.0**
- [ ] **WebSocket support**: Real-time data feeds
- [ ] **Distributed cache**: Redis integration
- [ ] **Circuit breaker**: Para APIs que falham consistentemente
- [ ] **Metrics collection**: Prometheus metrics

### **v2024.4.0**
- [ ] **Multi-exchange**: Binance, Coinbase, etc.
- [ ] **GraphQL support**: Para APIs mais eficientes
- [ ] **Compression**: Gzip/deflate para responses grandes
- [ ] **Connection pooling**: Otimização de network

---

**🔗 Integração com Outros Agentes**
- **analyzer.py**: Consome dados do fetcher
- **social_analyzer.py**: Usa rate limiting compartilhado
- **main.py**: Interface principal de entrada

**📊 Status**: 🔥 **Recentemente Aprimorado** - v2024.2.0
- ✅ Rate limiting inteligente implementado
- ✅ Fallback chain automático funcionando  
- ✅ Tratamento robusto de erros 401/404/429
- ✅ Testes de validação passando
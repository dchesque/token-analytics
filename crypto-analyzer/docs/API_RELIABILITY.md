# 🛡️ API Reliability Guide - Crypto Analyzer v2024.2.0

## 📋 Visão Geral

Este documento detalha como o Crypto Analyzer v2024.2.0 alcança alta confiabilidade através de estratégias robustas de tratamento de APIs, incluindo fallbacks automáticos, rate limiting inteligente e tratamento de erros.

## 🏗️ Arquitetura de Confiabilidade

### **Principios Fundamentais**

1. **Graceful Degradation**: Sistema continua funcionando mesmo com APIs limitadas
2. **Fallback Chains**: Múltiplas fontes para cada tipo de dado
3. **Smart Rate Limiting**: Evita banimentos e otimiza performance
4. **Error Recovery**: Recuperação automática de falhas temporárias

## 🔄 Estratégias de Fallback

### **CoinGecko API Fallback Chain**

```python
# Cadeia de Fallback para Histórico de Preços
1. market_chart (dados ricos, pode retornar 401)
   ↓ FALHA (401 Authentication Error)
2. OHLC (dados OHLC, limitado a 30 dias)
   ↓ FALHA (429 Rate Limit ou 404)
3. basic_price (preço atual apenas)
   ↓ FALHA (network error)
4. empty_structure (estrutura vazia válida)

# Implementação
def get_price_history(self, token_id: str, days: int = 90):
    # Primeira tentativa: market_chart
    result = self._try_market_chart(token_id, days)
    if result: return result
    
    # Segunda tentativa: OHLC
    result = self._try_ohlc_data(token_id, min(days, 30))
    if result: return result
    
    # Terceira tentativa: dados básicos
    result = self._get_basic_price_data(token_id)
    if result: return result
    
    # Fallback final: estrutura vazia
    return self._empty_price_data()
```

### **LunarCrush v4 Strategy Pattern**

```python
# Estratégia Tripla para LunarCrush
1. insights_endpoint (dados específicos do token)
   ↓ FALHA (404 Not Found)
2. time_series_endpoint (dados históricos)
   ↓ FALHA (401 API Key Invalid)  
3. list_endpoint (busca em lista geral)
   ↓ FALHA (429 Rate Limited)
4. alternative_social_data (CryptoCompare/CoinGecko)

# Implementação
def get_lunarcrush_data(self, symbol: str):
    # Estratégia 1: Endpoint insights
    if data := self._try_insights_endpoint(symbol):
        return data
    
    # Estratégia 2: Endpoint time-series  
    if data := self._try_timeseries_endpoint(symbol):
        return data
        
    # Estratégia 3: Lista filtrada
    if data := self._try_list_endpoint(symbol):
        return data
    
    # Fallback: Dados alternativos
    return self._get_alternative_social_data(symbol)
```

## ⚡ Rate Limiting Inteligente

### **Configuração Otimizada**

```python
# Parâmetros Conservadores (v2024.2.0)
MIN_TIME_BETWEEN_REQUESTS = 4.0    # segundos
MAX_REQUESTS_PER_MINUTE = 15       # requests/min  
JITTER_RANGE = (0.5, 1.5)         # randomização
BACKOFF_MULTIPLIER = 2             # crescimento exponencial
MAX_BACKOFF_TIME = 60              # máximo 1 minuto
```

### **Algoritmo de Rate Limiting**

```python
def _rate_limit(self):
    current_time = time.time()
    
    # Reset contador por minuto
    if current_time - self.request_window_start >= 60:
        self.request_count = 0
        self.request_window_start = current_time
    
    # Verificar limite por minuto
    if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
        wait_time = 60 - (current_time - self.request_window_start)
        if wait_time > 0:
            time.sleep(wait_time)
            self.request_count = 0
            self.request_window_start = time.time()
    
    # Delay com jitter (evita thundering herd)
    elapsed = current_time - self.last_request_time
    jitter = random.uniform(*JITTER_RANGE)
    min_delay = self.MIN_TIME_BETWEEN_REQUESTS + jitter
    
    if elapsed < min_delay:
        sleep_time = min_delay - elapsed
        time.sleep(sleep_time)
    
    self.last_request_time = time.time()
    self.request_count += 1
```

## 🚨 Tratamento de Erros Específicos

### **HTTP 401 (Authentication Error)**

**Cenário**: CoinGecko market_chart retorna 401 (requer API key premium)

```python
# Detecção e Resposta
if response.status_code == 401:
    print("market_chart retornou 401 (sem autenticação)")
    # Fallback automático para OHLC (não requer auth)
    return self._try_ohlc_data(token_id, days)
```

**Resultado**: ✅ Sistema obtém dados via OHLC sem interrupção

### **HTTP 404 (Not Found)**

**Cenário**: LunarCrush v4 endpoints retornam 404

```python
# Estratégia Multi-Endpoint
endpoints = [
    f"/public/insights/{coin_id}",
    f"/public/coins/{coin_id}/time-series", 
    f"/public/coins/list?symbol={symbol}"
]

for endpoint in endpoints:
    try:
        response = self._make_request(base_url + endpoint)
        if response.status_code == 200:
            return self._parse_response(response)
    except RequestError:
        continue  # Próximo endpoint

# Se todos falharam, usar dados alternativos
return self._get_alternative_social_data(symbol)
```

**Resultado**: ✅ Dados sociais obtidos via CoinGecko community data

### **HTTP 429 (Rate Limited)**

**Cenário**: APIs retornam 429 (muitos requests)

```python
# Backoff Exponencial
def _handle_rate_limit(self, attempt: int):
    base_wait = 10  # segundos base
    wait_time = min(60, base_wait * (2 ** attempt))
    
    print(f"Rate limit (429). Aguardando {wait_time}s...")
    time.sleep(wait_time)
    
    # Reset contadores para nova janela
    self.request_count = 0
    self.request_window_start = time.time()
```

**Sequência**: 10s → 20s → 40s → 60s (máximo)

## 📊 Monitoramento e Métricas

### **Métricas de Confiabilidade**

```python
RELIABILITY_METRICS = {
    # Taxa de sucesso por API
    'coingecko_success_rate': 0.0,
    'lunarcrush_success_rate': 0.0,
    
    # Uso de fallbacks
    'fallback_usage': {
        'market_chart_to_ohlc': 0,
        'ohlc_to_basic': 0,
        'lunarcrush_to_alternative': 0
    },
    
    # Rate limiting
    'rate_limit_hits': 0,
    'average_request_delay': 0.0,
    
    # Error recovery
    'automatic_recoveries': 0,
    'failed_requests_total': 0
}
```

### **Health Check System**

```python
def perform_health_check():
    results = {}
    
    # Teste CoinGecko
    try:
        response = requests.get('https://api.coingecko.com/api/v3/ping')
        results['coingecko'] = response.status_code == 200
    except:
        results['coingecko'] = False
    
    # Teste Fear & Greed
    try:
        response = requests.get('https://api.alternative.me/fng/')
        results['fear_greed'] = response.status_code == 200
    except:
        results['fear_greed'] = False
    
    return results
```

## 🧪 Testes de Validação

### **Teste de Fallback Chain**

```bash
# Executa teste completo de fallbacks
python test_corrections.py

# Saída esperada:
# ✅ market_chart falhou, OHLC OK  
# ✅ LunarCrush falhou, alternative data OK
# ✅ Rate limiting funcionando (4s+ delays)
```

### **Teste de Rate Limiting**

```bash
# Teste específico de rate limiting
python test_rate_limit.py

# Saída esperada:
# Request 1: 0.00s (primeiro)
# Request 2: 4.64s (delay aplicado)
# Request 3: 4.61s (delay aplicado)
# ✅ Rate limiting FUNCIONANDO
```

## 🔧 Troubleshooting Guide

### **Problema: "Todas APIs falharam"**

**Diagnóstico**:
```bash
# 1. Testar conectividade
curl -s https://api.coingecko.com/api/v3/ping
curl -s https://api.alternative.me/fng/

# 2. Verificar rate limiting
python -c "
from src.fetcher import DataFetcher
f = DataFetcher()
print(f'Requests/min: {f.MAX_REQUESTS_PER_MINUTE}')
print(f'Min delay: {f.MIN_TIME_BETWEEN_REQUESTS}s')
"

# 3. Executar diagnóstico completo
python test_corrections.py
```

**Soluções**:
- ✅ Verificar conexão com internet
- ✅ Aguardar reset de rate limit (1 minuto)
- ✅ Verificar se APIs estão online (status pages)

### **Problema: "Dados sociais limitados"**

**Causa**: LunarCrush API key não configurada ou inválida

**Solução**:
```bash
# 1. Verificar configuração
echo $LUNARCRUSH_API_KEY

# 2. Configurar API key (opcional)
export LUNARCRUSH_API_KEY=your_key_here

# 3. Sistema funciona sem API key (usa fallbacks)
python src/main.py bitcoin  # Funcionará com dados limitados
```

### **Problema: "Rate limit muito restritivo"**

**Ajuste personalizado**:
```python
# Em src/fetcher.py, ajustar conforme necessário:
self.MIN_TIME_BETWEEN_REQUESTS = 2.0  # Reduzir para 2s
self.MAX_REQUESTS_PER_MINUTE = 25     # Aumentar para 25/min

# CUIDADO: Pode causar banimento se muito agressivo
```

## 📈 Performance Benchmarks

### **Tempos Esperados** (v2024.2.0)

```
Análise Bitcoin (com cache frio):
├── Token search: ~1s
├── Token data: ~5s (com rate limiting)  
├── Price history: ~10s (fallback para OHLC)
├── Social data: ~8s (fallback para alternative)
└── Total: ~25s

Análise Bitcoin (com cache quente):
└── Total: ~2s

Rate Limiting:
├── Delay médio: 4.5s entre requests
├── Jitter range: 0.5s - 1.5s  
├── Recovery 429: 10s → 20s → 40s
└── Success rate: >95%
```

## 🛡️ Best Practices

### **Para Desenvolvedores**

1. **Sempre usar fallbacks**: Nunca depender de uma única API
2. **Rate limiting conservador**: Melhor lento que banido
3. **Error handling granular**: Tratar cada erro especificamente  
4. **Monitoring**: Log métricas e taxa de sucesso
5. **Testing**: Validar fallbacks regularmente

### **Para Usuários**

1. **Configurar API keys** (opcional): Melhora qualidade dos dados
2. **Ser paciente**: Rate limiting garante estabilidade
3. **Verificar logs**: Sistema informa sobre fallbacks usados
4. **Reportar problemas**: Com outputs dos testes de diagnóstico

---

**📊 Status de Confiabilidade v2024.2.0**: 🟢 ROBUSTO
- ✅ Fallbacks automáticos funcionando
- ✅ Rate limiting inteligente ativo  
- ✅ Recovery de erros implementado
- ✅ Testes de validação passando
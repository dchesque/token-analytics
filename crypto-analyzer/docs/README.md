# 📚 Documentação Técnica - Crypto Analyzer v2024.2.0

## 🎯 Visão Geral

O Crypto Analyzer é um sistema robusto de análise de criptomoedas que combina análise fundamental, técnica e social. Esta versão 2024.2.0 inclui importantes melhorias de estabilidade e confiabilidade das APIs.

## 🏗️ Arquitetura do Sistema

### **Componentes Principais**

```
crypto-analyzer/
├── src/
│   ├── main.py              # Interface CLI principal
│   ├── analyzer.py          # Motor de análise (3 camadas)
│   ├── fetcher.py           # Coleta de dados robusta
│   ├── social_analyzer.py   # Análise social avançada
│   ├── config.py            # Configurações e constantes
│   ├── utils.py             # Utilitários e helpers
│   └── enhanced_features.py # Funcionalidades avançadas
├── docs/                    # Documentação técnica
├── agents/                  # Documentação dos agentes
├── data/                    # Cache e dados temporários
└── reports/                 # Relatórios gerados
```

### **Fluxo de Processamento**

1. **Input Processing**: Recebe query do usuário (símbolo, nome, etc.)
2. **Token Resolution**: Busca inteligente com mapeamento direto
3. **Data Collection**: APIs com fallback automático
4. **Analysis Engine**: Sistema de 3 camadas
5. **Output Generation**: Formatação rica com Rich Console

## 🔧 APIs e Integração

### **Sistema de APIs Robusto v2.1**

#### **CoinGecko API v3** 🥇
```python
# Estratégia de Fallback Automático
market_chart → OHLC → basic_price

# Tratamento de Erros
401: Fallback automático para OHLC
429: Backoff exponencial (10s → 20s → 40s)
404: Graceful degradation
```

#### **LunarCrush API v4** 🌙
```python
# Estratégia Tripla
insights → time-series → lista

# Fallback Inteligente
LunarCrush → CryptoCompare → CoinGecko Community
```

#### **Rate Limiting Inteligente**
```python
# Configuração Robusta
MIN_TIME_BETWEEN_REQUESTS = 4.0s
MAX_REQUESTS_PER_MINUTE = 15
JITTER = random(0.5, 1.5)s
BACKOFF = exponential(10, 20, 40)s
```

## 📊 Sistema de Análise

### **Camada 1: Eliminatória** ❌✅
```python
CRITERIOS_ELIMINATORIOS = {
    'market_cap_min': 1_000_000,      # $1M+
    'volume_24h_min': 100_000,        # $100K+
    'age_days_min': 180,              # 6 meses+
    'liquidity_check': True           # Verificação de liquidez
}
```

### **Camada 2: Pontuação (0-10)** 📊
```python
WEIGHTS = {
    'market_cap_rank': 2.0,    # Estabelecimento no mercado
    'liquidity': 2.0,          # Volume/Market Cap ratio
    'development': 2.0,        # Atividade no GitHub
    'community': 2.0,          # Métricas sociais
    'performance': 2.0         # Estabilidade de preço
}
```

### **Camada 3: Contexto** 🌍
- Fear & Greed Index (0-100)
- Análise de momentum técnico (RSI, médias)
- Sentimento social (se disponível)

## 🛡️ Tratamento de Erros e Robustez

### **Error Handling Strategy**

```python
# Hierarquia de Tratamento
try:
    # Primeira tentativa
    primary_api_call()
except AuthenticationError:
    # Fallback automático
    secondary_api_call()
except RateLimitError:
    # Backoff exponencial
    exponential_backoff()
except NetworkError:
    # Cache ou dados alternativos
    fallback_to_cache()
```

### **Resilience Patterns**

1. **Circuit Breaker**: Para APIs que falham repetidamente
2. **Retry Logic**: Com backoff exponencial
3. **Fallback Chain**: Múltiplas fontes de dados
4. **Graceful Degradation**: Sistema funciona mesmo com APIs limitadas

## 🚀 Performance e Otimização

### **Cache Strategy**
```python
CACHE_DURATIONS = {
    'token_data': 300,       # 5 min
    'price_history': 3600,   # 1 hora
    'social_data': 1800,     # 30 min
    'fear_greed': 3600       # 1 hora
}
```

### **Rate Limiting Otimizado**
- **Predictive Timing**: Calcula delays ideais
- **Jitter Implementation**: Evita thundering herd
- **Endpoint-Specific**: Delays diferentes por tipo de API

## 🧪 Testing Framework

### **Testes Disponíveis**
```bash
# Testes de Validação (NOVOS em v2024.2.0)
python test_corrections.py      # Valida correções de API
python test_rate_limit.py       # Testa rate limiting específico

# Testes Tradicionais  
python test_crypto_classification.py  # Classificações corretas
python test_analyzer.py              # Sistema completo
python test_fetcher.py               # Coleta de dados
```

### **Casos de Teste Críticos**
1. **API Fallbacks**: market_chart 401 → OHLC success
2. **Rate Limiting**: Delays de 4s+ com jitter
3. **Error Recovery**: 429 → exponential backoff
4. **Data Integrity**: Validação de estruturas de dados

## 🔐 Configuração e Segurança

### **Environment Variables**
```bash
# APIs Opcionais (melhoram análise)
LUNARCRUSH_API_KEY=your_key_here
MESSARI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# Configurações de Sistema
PYTHONIOENCODING=utf-8  # Para emojis no Windows
CACHE_DIR=./data/cache
LOG_LEVEL=INFO
```

### **Security Best Practices**
- API keys em variáveis de ambiente
- Rate limiting para evitar banimento
- Validação de input do usuário
- Sanitização de dados de saída

## 📈 Métricas e Monitoramento

### **Métricas Coletadas**
```python
METRICS = {
    'api_calls_total': Counter,
    'api_call_duration': Histogram,
    'error_rate_by_endpoint': Gauge,
    'cache_hit_ratio': Gauge,
    'analysis_success_rate': Gauge
}
```

### **Health Checks**
- Conectividade das APIs
- Performance do cache
- Taxa de sucesso das análises
- Tempo de resposta médio

## 🛠️ Troubleshooting

### **Problemas Comuns**

#### **"API returning 401"**
```bash
# Solução: Sistema usa fallback automático
✓ market_chart (401) → OHLC → basic_price
✓ Verificar logs para confirmação do fallback
```

#### **"Rate limit exceeded (429)"**
```bash
# Solução: Backoff exponencial implementado
✓ Aguarda automaticamente: 10s → 20s → 40s
✓ Reset de contadores após sucesso
```

#### **"LunarCrush returning 404"**
```bash
# Solução: Estratégia tripla + fallback
✓ insights → time-series → lista → alternative_data
✓ Sistema continua funcionando com dados limitados
```

### **Diagnostic Tools**
```bash
# Teste de conectividade
python -c "
import requests
print('CoinGecko:', requests.get('https://api.coingecko.com/api/v3/ping').status_code)
print('Fear & Greed:', requests.get('https://api.alternative.me/fng/').status_code)
"

# Validação completa
python test_corrections.py
```

## 🔄 Versionamento e Changelog

### **v2024.2.0 (Current)**
- ✅ Rate limiting inteligente (4s delays + jitter)
- ✅ CoinGecko fallback chain (market_chart → OHLC → basic)  
- ✅ LunarCrush v4 endpoints (estratégia tripla)
- ✅ Tratamento robusto de erros 401/404/429
- ✅ Backoff exponencial para rate limits
- ✅ Testes de validação automatizados

### **v2024.1.0 (Previous)**
- Sistema de classificação crypto correto
- Análise de 3 camadas
- Interface CLI rica
- APIs básicas funcionais

## 🚀 Roadmap Técnico

### **v2024.3.0 (Planned)**
- [ ] WebSocket support para dados real-time
- [ ] Análise on-chain básica
- [ ] Cache distribuído (Redis)
- [ ] Métricas Prometheus
- [ ] API REST opcional

### **v2024.4.0 (Future)**
- [ ] Machine Learning para predições
- [ ] Alertas inteligentes
- [ ] Dashboard web
- [ ] Multi-exchange support

---

**📧 Suporte Técnico**
- Documentação completa: `/docs` e `/agents`  
- Testes de validação: `python test_corrections.py`
- Issues conhecidos: Verifique logs e fallbacks automáticos

**🔧 Desenvolvimento**
- Python 3.8+
- Dependencies: `pip install -r requirements.txt`
- Testing: pytest-compatible
- Code style: PEP 8 com Rich formatting
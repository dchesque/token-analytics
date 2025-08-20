# 🚀 Crypto Analyzer v2.0

**Análise Inteligente de Criptomoedas com IA**

Sistema completo de análise fundamental, técnica e social de tokens baseado em múltiplas fontes de dados e algoritmos de inteligência artificial.

## ⭐ Principais Características

- **🎯 Sistema de 3 Camadas**: Eliminatória → Pontuação → Classificação
- **👑 Classificações Crypto Corretas**: MAJOR, LARGE CAP, MID CAP, etc.
- **📊 Análise Técnica de Momentum**: RSI, médias móveis, tendências
- **🌡️ Contexto de Mercado**: Fear & Greed Index integrado
- **🔍 APIs Gratuitas**: CoinGecko, Alternative.me - sem API keys
- **💎 Métricas Especiais**: Bitcoin e Ethereum com análises customizadas
- **📈 Interface CLI Rica**: Cores, emojis, progresso em tempo real

## 🚀 Início Rápido

### 1. **Execução Simples (2 cliques)**
```
Duplo clique em: Crypto-Analyzer.bat
```

### 2. **Instalação Manual**
```bash
# Instale dependências
pip install -r requirements.txt

# Execute
python src/main.py
```

## 💡 Uso

### **Linha de Comando**
```bash
# Análise individual
python src/main.py bitcoin

# Comparar tokens
python src/main.py --compare bitcoin ethereum solana

# Modo monitoramento
python src/main.py --watch bitcoin 5

# Modo interativo
python src/main.py
```

## 📊 Sistema de Classificação

### **👑 Terminologia Crypto Correta**

| Classificação | Emoji | Descrição | Exemplos |
|---------------|-------|-----------|----------|
| **MAJOR** | 👑 | Bitcoin, Ethereum | BTC, ETH |
| **LARGE CAP** | 💎 | Top 10 do mercado | BNB, SOL, XRP, ADA |
| **MID CAP** | ⭐ | Projetos estabelecidos | MATIC, LINK, UNI |
| **SMALL CAP** | 🔹 | Capitalização menor | Tokens rank 51-100 |
| **MICRO CAP** | 🔸 | Projetos pequenos | Tokens rank 101-500 |
| **NANO CAP** | ⚡ | Projetos muito pequenos | Tokens rank >500 |
| **MEME COIN** | 🐕 | Tokens meme/comunidade | DOGE, SHIB, PEPE |
| **STABLECOIN** | 💵 | Moedas estáveis | USDT, USDC, DAI |
| **DEFI** | 🏦 | Tokens DeFi | AAVE, COMP, SUSHI |
| **LAYER 2** | ⚡ | Soluções escalabilidade | ARB, OP, MATIC |

### **📈 Sistema de Pontuação (0-10)**

#### **Camada 1: Eliminatória** ❌✅
- Market Cap > $1M
- Volume 24h > $100K  
- Token existe há > 180 dias
- Liquidez verificável

#### **Camada 2: Pontuação** 📊
- **Market Cap/Ranking** (0-2 pontos): Estabelecimento no mercado
- **Liquidez** (0-2 pontos): Volume/Market Cap ratio
- **Desenvolvimento** (0-2 pontos): Atividade no GitHub
- **Comunidade** (0-2 pontos): Métricas sociais
- **Performance** (0-2 pontos): Estabilidade de preço

#### **Camada 3: Contexto** 🌍
- Fear & Greed Index
- Análise de momentum técnico
- Sentimento do mercado

## 💎 Métricas Especiais para Majors

### **Bitcoin (Digital Gold)** 👑
- Dominância de mercado
- Ciclos de halving (cada 4 anos)
- Supply limitado: 21M BTC
- Rede mais segura (PoW)
- Narrativa: Reserva de valor digital

### **Ethereum (World Computer)** 👑  
- Maior ecossistema DeFi/NFT
- TVL (Total Value Locked)
- Proof of Stake desde 2022
- Layer 2 solutions
- Narrativa: Plataforma de smart contracts

## 📊 Exemplos de Output

### **Bitcoin - MAJOR** 👑
```
┌────────── 📊 ANÁLISE: BITCOIN ──────────┐
│                                          │
│ 👑 CLASSIFICAÇÃO: MAJOR                  │
│ 📝 Ativo principal do mercado crypto     │
│ ⚖️ Nível de Risco: Estabelecido         │
│ 📊 Score de Fundamentos: 9/10           │
│ 🏆 Ranking: #1                          │
│                                          │
│ 💰 Market Cap: $1,350.0B                │
│ 📈 Preço: $67,500.00                    │
│                                          │
│ 🔑 MÉTRICAS PRINCIPAIS:                 │
│ • Dominância: 58.5%                     │
│ • Halving a cada 4 anos                 │
│ • Supply máximo: 21M BTC                │
│ • Rede desde 2009                       │
│                                          │
└──────────────────────────────────────────┘
```

### **Cardano - LARGE CAP** 💎
```
┌────────── 📊 ANÁLISE: CARDANO ──────────┐
│                                          │
│ 💎 CLASSIFICAÇÃO: LARGE CAP              │
│ 📝 Top 10 do mercado                    │
│ ⚖️ Nível de Risco: Baixo-Médio          │
│ 📊 Score de Fundamentos: 7/10           │
│ 🏆 Ranking: #8                          │
│                                          │
│ 💰 Market Cap: $18.2B                   │
│ 📈 Preço: $0.52                         │
│                                          │
└──────────────────────────────────────────┘
```

## 📁 Estrutura de Arquivos

```
crypto-analyzer/
├── src/                    # 🔧 Código principal
│   ├── main.py            # Interface CLI
│   ├── analyzer.py        # Motor de análise
│   ├── fetcher.py         # Coleta de dados
│   ├── config.py          # Configurações
│   ├── utils.py           # Utilitários
│   └── enhanced_features.py # Funcionalidades avançadas
├── docs/                  # 📚 Documentação técnica
├── agents/               # 🤖 Documentação dos agentes
├── data/                # 💾 Cache e histórico
├── reports/             # 📊 Relatórios gerados
├── requirements.txt     # 📦 Dependências
├── test_*.py           # 🧪 Testes essenciais
├── install.bat         # 🪟 Instalador Windows
└── install.sh          # 🐧 Instalador Unix
```

## 🌐 APIs Utilizadas (Robustas e Confiáveis)

### **APIs Principais (100% Gratuitas)**

1. **CoinGecko API v3** 🥇
   - Dados de preço, volume, market cap
   - Rankings e métricas de mercado
   - Histórico de preços com fallback chain
   - **Rate limiting inteligente**: 15 requests/minuto
   - **Fallback automático**: market_chart → OHLC → basic_price

2. **Alternative.me Fear & Greed Index** 🎯
   - Índice de medo e ganância
   - Sentimento do mercado crypto
   - Dados históricos

### **APIs Premium (Opcionais)**

3. **LunarCrush API v4** 🌙
   - Análise social avançada (requer API key)
   - Galaxy Score e métricas sociais
   - **Estratégia tripla**: insights → time-series → lista
   - **Fallback inteligente** para dados gratuitos

4. **Messari API** 📊
   - Dados fundamentais avançados (opcional)
   - Métricas de tokenomics

5. **GitHub API** 🔧
   - Métricas de desenvolvimento
   - Atividade dos repositórios

## 🧪 Testes e Validação

### **Testes Principais**
```bash
# Teste das classificações crypto corretas
python test_crypto_classification.py

# Teste do sistema de análise completo
python test_analyzer.py  

# Teste das correções de API (NOVO)
python test_corrections.py

# Teste específico do rate limiting
python test_rate_limit.py
```

### **Casos de Teste Validados** ✅
- **Classificações**: Bitcoin → 👑 MAJOR, Ethereum → 👑 MAJOR, Cardano → 💎 LARGE CAP
- **APIs Robustas**: Fallback chain testada (market_chart → OHLC → basic_price)
- **Rate Limiting**: 4s+ delays com jitter, backoff exponencial
- **Tratamento de Erros**: 401, 404, 429 tratados adequadamente
- **LunarCrush v4**: Estratégia tripla com fallback funcionando

## 📈 Funcionalidades Avançadas

### **Análise de Momentum** 📊
- RSI simplificado (14 dias)
- Posição vs médias móveis (7d, 30d)
- Posição no range de 90 dias
- Análise de volume
- Tendências: FORTE ALTA, ALTA, NEUTRO, BAIXA, FORTE BAIXA

### **Análise Múltipla** ⚖️
```bash
# Compare portfolio
python src/main.py --compare bitcoin ethereum bnb cardano solana

# Análise em lote com delay
python src/main.py --batch my_tokens.txt
```

### **Relatórios Detalhados** 📄
- JSON com dados técnicos completos
- Markdown com análise formatada
- Histórico de análises
- Métricas de performance

## 🚨 Avisos Importantes

### ⚠️ **Não é Consultoria Financeira**
- Sistema é **puramente educacional e informativo**
- **NÃO constitui recomendação de investimento**
- Sempre faça sua própria pesquisa (DYOR)
- Considere sua tolerância ao risco

### ⚠️ **Limitações**
- Baseado apenas em dados públicos
- Mercado crypto é altamente volátil
- Análise técnica não garante resultados futuros
- APIs podem ter limitações temporárias

### ⚠️ **Responsabilidade**
- Decisões de investimento são 100% suas
- Criptomoedas são ativos de alto risco
- Nunca invista mais do que pode perder

## 🔧 Solução de Problemas

### **Python não encontrado**
- **Windows**: Microsoft Store ou python.org
- **Linux**: `sudo apt install python3 python3-pip`
- **macOS**: `brew install python3`

### **Erro de dependências**
```bash
# Atualize pip
python -m pip install --upgrade pip

# Reinstale dependências
pip install -r requirements.txt
```

### **APIs não funcionando**
```bash
# Teste de conectividade
python -c "
import requests
print('CoinGecko:', requests.get('https://api.coingecko.com/api/v3/ping').status_code)
print('Fear & Greed:', requests.get('https://api.alternative.me/fng/').status_code)
"
```

### **Rate Limiting Inteligente v2.1** ⚡
O sistema implementa rate limiting robusto e inteligente:
- **Delay base**: 4s entre requests (com jitter)
- **Máximo**: 15 requests/minuto (conservador)
- **Backoff exponencial**: 10s → 20s → 40s para 429
- **Detecção de endpoints**: Delays específicos por tipo
- **Retry automático** com circuit breaker

## 📚 Documentação Completa

- **[docs/README.md](docs/README.md)**: Documentação técnica detalhada
- **[agents/analyzer.md](agents/analyzer.md)**: Motor de análise
- **[agents/fetcher.md](agents/fetcher.md)**: coleta de dados  
- **[agents/interface.md](agents/interface.md)**: Interface CLI
- **[agents/setup.md](agents/setup.md)**: Configuração e instalação

## 🏗️ Arquitetura do Sistema

### **Fluxo de Análise**
1. **Input**: Token query (bitcoin, BTC, etc.)
2. **Busca**: Search inteligente no CoinGecko
3. **Coleta**: Dados completos via APIs
4. **Eliminatória**: Critérios mínimos de qualidade
5. **Pontuação**: Score 0-10 baseado em 5 critérios
6. **Classificação**: Terminologia crypto correta
7. **Contexto**: Fear & Greed + momentum técnico
8. **Output**: Análise completa formatada

### **Rate Limiting Inteligente**
- Respeita limites das APIs gratuitas
- Delays automáticos entre requests
- Sistema de retry com backoff
- Cache local para otimização

## 🎯 Roadmap Futuro

- [ ] Integração com mais APIs DeFi
- [ ] Análise on-chain básica
- [ ] Alertas via Telegram/Discord
- [ ] Interface web opcional
- [ ] Análise de correlações
- [ ] Métricas ESG para crypto
- [ ] Integração com portfolio trackers

## 📞 Suporte e Contribuição

### **Testes de Diagnóstico**
```bash
# Validação completa do sistema
python test_crypto_classification.py
```

### **Estrutura para Contribuições**
1. Fork do repositório
2. Crie branch para feature
3. Implemente com testes
4. Documente mudanças
5. Submit pull request

---

**🤖 Crypto Analyzer v2024.2.0**  
*Sistema educacional de análise crypto robusto e confiável com APIs inteligentes*

**⚠️ Disclaimer**: Não constitui consultoria financeira. Sempre faça sua própria pesquisa (DYOR) antes de tomar decisões de investimento.
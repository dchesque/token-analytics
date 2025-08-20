# 🚀 Setup Agent - Instalação e Configuração

## 🎯 Visão Geral

Este guia cobre a instalação completa e configuração do Crypto Analyzer v2024.2.0, incluindo requisitos de sistema, instalação de dependências, configuração de API keys e troubleshooting comum.

## 📋 Requisitos de Sistema

### **Sistema Operacional**
- ✅ **Windows** 10/11 (testado)
- ✅ **macOS** 10.15+ (compatível)
- ✅ **Linux** Ubuntu 18.04+ / Debian 10+ (compatível)

### **Python**
```bash
# Versão mínima: Python 3.8+
# Versão recomendada: Python 3.10+
python --version  # Deve mostrar 3.8+

# No Windows via Microsoft Store ou python.org
# No macOS: brew install python3
# No Linux: sudo apt install python3 python3-pip
```

### **Dependências do Sistema**
```bash
# Windows: Nenhuma adicional necessária
# macOS: 
brew install curl git

# Linux:
sudo apt update
sudo apt install curl git python3-pip python3-venv
```

## 🛠️ Instalação Rápida

### **Método 1: Executáveis (.bat) - Windows** ⚡

```bash
# 1. Duplo clique em qualquer arquivo .bat:
Crypto-Analyzer.bat     # ← RECOMENDADO (interface completa)
start.bat              # Versão simples
start.ps1              # PowerShell (moderno)

# 2. O sistema automaticamente:
# ✅ Verifica Python instalado
# ✅ Instala dependências se necessário  
# ✅ Configura environment
# ✅ Executa aplicação
```

### **Método 2: Instalação Manual** 🔧

```bash
# 1. Clone ou baixe o repositório
git clone <repo-url>
cd crypto-analyzer

# 2. Criar ambiente virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# 3. Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Executar
python src/main.py
```

## 📦 Dependências Principais

### **requirements.txt**
```python
# Core dependencies
requests>=2.31.0          # HTTP requests com Session
rich>=13.0.0              # Rich console output
colorama>=0.4.6           # Windows color support

# Optional but recommended  
python-dotenv>=1.0.0      # .env file support
setuptools>=65.0.0        # Python packaging
urllib3>=2.0.0            # HTTP client

# Development (opcional)
pytest>=7.0.0             # Testing framework
black>=23.0.0             # Code formatting
```

### **Instalação de Dependências Específicas**
```bash
# Instalação básica (mínima)
pip install requests rich colorama

# Instalação completa (recomendada)
pip install -r requirements.txt

# Desenvolvimento (para contribuidores)
pip install -r requirements.txt pytest black
```

## 🔑 Configuração de API Keys

### **APIs Gratuitas (Funcionam sem configuração)**

✅ **CoinGecko API**: Não requer API key (plano gratuito)
✅ **Alternative.me**: Fear & Greed Index (gratuito)
✅ **DeFiLlama**: Dados DeFi (gratuito)

### **APIs Premium (Opcionais - Melhoram a análise)**

#### **LunarCrush v4** 🌙
```bash
# 1. Registrar em: https://lunarcrush.com/developers
# 2. Obter API key v4 (não v3!)
# 3. Configurar:

# Método A: Arquivo .env (recomendado)
cp .env.example .env
# Editar .env:
LUNARCRUSH_API_KEY=your_v4_key_here

# Método B: Variável de ambiente
export LUNARCRUSH_API_KEY=your_v4_key_here

# Windows:
set LUNARCRUSH_API_KEY=your_v4_key_here
```

#### **Messari API** 📊
```bash
# 1. Registrar em: https://messari.io/api
# 2. Configurar:
MESSARI_API_KEY=your_key_here
```

#### **GitHub API** 🔧
```bash
# 1. Criar token em: GitHub Settings > Developer settings > Personal access tokens
# 2. Configurar:
GITHUB_TOKEN=your_token_here
```

### **Arquivo .env Completo**
```bash
# crypto-analyzer/.env

# APIs Premium (opcionais)
LUNARCRUSH_API_KEY=your_lunarcrush_v4_key
MESSARI_API_KEY=your_messari_key  
GITHUB_TOKEN=your_github_token

# Configurações do Sistema (opcionais)
PYTHONIOENCODING=utf-8
REQUEST_TIMEOUT=20
CACHE_DURATION=300
LOG_LEVEL=INFO

# Configurações de Rate Limiting (avançado)
MIN_TIME_BETWEEN_REQUESTS=4.0
MAX_REQUESTS_PER_MINUTE=15
```

## ⚙️ Configuração Avançada

### **config.py - Parâmetros do Sistema**

```python
# src/config.py - Principais configurações

# APIs
COINGECKO_API = "https://api.coingecko.com/api/v3"
LUNARCRUSH_API_V4 = "https://lunarcrush.com/api4"
FEAR_GREED_API = "https://api.alternative.me/fng/"

# Rate Limiting (ajustar com cuidado)
MIN_TIME_BETWEEN_REQUESTS = 4.0    # segundos entre requests
MAX_REQUESTS_PER_MINUTE = 15       # máximo por minuto

# Cache (segundos)
CACHE_DURATION = 300               # 5 minutos
CACHE_SOCIAL = 1800               # 30 minutos
CACHE_DEFI = 3600                 # 1 hora

# Thresholds de Eliminação
MARKET_CAP_MIN = 1_000_000        # $1M mínimo
VOLUME_24H_MIN = 100_000          # $100K mínimo
AGE_DAYS_MIN = 180                # 6 meses mínimo

# Detecção de Hype
HYPE_THRESHOLDS = {
    'moderate': 25,    # +25% em volume social
    'high': 50,        # +50% 
    'extreme': 100     # +100%
}
```

### **Configurações por Ambiente**

```bash
# Desenvolvimento (mais logs, cache menor)
export LOG_LEVEL=DEBUG
export CACHE_DURATION=60
export MIN_TIME_BETWEEN_REQUESTS=2.0

# Produção (conservador, cache maior)
export LOG_LEVEL=INFO  
export CACHE_DURATION=600
export MIN_TIME_BETWEEN_REQUESTS=5.0

# CI/CD (ainda mais conservador)
export MIN_TIME_BETWEEN_REQUESTS=10.0
export MAX_REQUESTS_PER_MINUTE=6
```

## 🧪 Validação da Instalação

### **Teste Rápido**
```bash
# Teste básico
python src/main.py bitcoin

# Saída esperada:
# ✅ APIs conectadas
# ✅ Bitcoin analisado  
# ✅ Classificação: MAJOR 👑
# ✅ Score: 8-10
```

### **Testes Completos**
```bash
# Teste de APIs e fallbacks
python test_corrections.py

# Saída esperada:
# ✅ Rate limiting: FUNCIONANDO
# ✅ CoinGecko fallback: FUNCIONANDO  
# ✅ LunarCrush v4: FUNCIONANDO
# ✅ Error handling: FUNCIONANDO

# Teste específico de rate limiting
python test_rate_limit.py

# Teste de classificações
python test_crypto_classification.py
```

### **Diagnóstico de Conectividade**
```bash
# Teste manual de APIs
python -c "
import requests
print('CoinGecko:', requests.get('https://api.coingecko.com/api/v3/ping').status_code)
print('Fear & Greed:', requests.get('https://api.alternative.me/fng/').status_code)
"

# Saída esperada:
# CoinGecko: 200
# Fear & Greed: 200
```

## 🚨 Troubleshooting Comum

### **Problema: "Python não encontrado"**

```bash
# Windows:
# 1. Instalar via Microsoft Store (recomendado)
# 2. Ou baixar de python.org
# 3. Verificar: python --version

# macOS:
brew install python3
# Ou usar python3 explicitamente

# Linux:
sudo apt install python3 python3-pip
```

### **Problema: "Módulo não encontrado"**

```bash
# Reinstalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Se persistir:
pip cache purge
pip install --no-cache-dir -r requirements.txt

# Verificar ambiente virtual ativo
which python  # Deve mostrar path do venv
```

### **Problema: "UnicodeEncodeError (Windows)"**

```bash
# Solução 1: Set encoding
set PYTHONIOENCODING=utf-8
python src/main.py bitcoin

# Solução 2: Alterar locale
chcp 65001
python src/main.py bitcoin

# Solução 3: Usar executável
# Duplo clique em Crypto-Analyzer.bat
```

### **Problema: "Todas as APIs falham"**

```bash
# 1. Verificar conectividade
ping api.coingecko.com

# 2. Verificar firewall/proxy
curl -I https://api.coingecko.com/api/v3/ping

# 3. Testar com delays maiores
export MIN_TIME_BETWEEN_REQUESTS=10.0
python src/main.py bitcoin

# 4. Verificar se APIs estão online
# https://status.coingecko.com
# https://alternative.me
```

### **Problema: "Rate limit muito restritivo"**

```bash
# ⚠️ CUIDADO: Ajustar gradualmente

# Em src/config.py:
MIN_TIME_BETWEEN_REQUESTS = 2.5  # Era 4.0
MAX_REQUESTS_PER_MINUTE = 20     # Era 15

# Monitorar logs para 429 errors
# Se aparecerem, reverter para valores conservadores
```

### **Problema: "LunarCrush sempre retorna dados limitados"**

```bash
# 1. Verificar API key configurada
echo $LUNARCRUSH_API_KEY

# 2. Verificar se é key v4 (não v3)
# 3. Verificar plano da API key (free/paid)

# 4. Sistema funciona sem API key:
unset LUNARCRUSH_API_KEY
python src/main.py bitcoin
# ✅ Usará dados alternativos (CoinGecko community)
```

## 🐳 Docker (Opcional)

### **Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "src/main.py"]
```

### **docker-compose.yml**
```yaml
version: '3.8'
services:
  crypto-analyzer:
    build: .
    environment:
      - LUNARCRUSH_API_KEY=${LUNARCRUSH_API_KEY}
      - PYTHONIOENCODING=utf-8
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### **Comandos Docker**
```bash
# Build
docker build -t crypto-analyzer .

# Run
docker run -e LUNARCRUSH_API_KEY=your_key crypto-analyzer bitcoin

# Com docker-compose
docker-compose up -d
```

## 🔄 Atualizações

### **Verificar Versão**
```bash
# Versão atual
python -c "
import sys
sys.path.insert(0, 'src')
from config import VERSION
print(f'Crypto Analyzer {VERSION}')
"

# Ou verificar no README.md
grep "v2024" README.md
```

### **Atualizar Sistema**
```bash
# 1. Backup dados (opcional)
cp -r data/ data_backup/

# 2. Atualizar código
git pull origin main

# 3. Atualizar dependências  
pip install --upgrade -r requirements.txt

# 4. Verificar funcionamento
python test_corrections.py
```

## 📊 Monitoramento

### **Logs do Sistema**
```bash
# Habilitar logs detalhados
export LOG_LEVEL=DEBUG
python src/main.py bitcoin 2>&1 | tee analysis.log

# Analisar logs
grep "ERROR" analysis.log
grep "429" analysis.log    # Rate limits
grep "401" analysis.log    # Auth errors
```

### **Métricas de Performance**
```bash
# Benchmark de performance
time python src/main.py bitcoin

# Monitorar uso de cache
grep "Cache hit" analysis.log | wc -l
grep "API Request" analysis.log | wc -l
```

## 🏗️ Ambiente de Desenvolvimento

### **Setup para Desenvolvedores**
```bash
# 1. Clone e setup
git clone <repo>
cd crypto-analyzer
python -m venv dev-env
source dev-env/bin/activate  # ou dev-env\Scripts\activate no Windows

# 2. Dependências de desenvolvimento
pip install -r requirements.txt
pip install pytest black flake8 mypy

# 3. Pre-commit hooks (opcional)
pip install pre-commit
pre-commit install

# 4. Executar testes
pytest tests/
python test_corrections.py
```

### **Estrutura para Desenvolvimento**
```
crypto-analyzer/
├── src/                    # Código principal
├── tests/                  # Testes unitários  
├── docs/                   # Documentação
├── agents/                 # Documentação por agente
├── data/                   # Cache e dados temporários
├── requirements.txt        # Dependências
├── .env.example           # Template de configuração
└── test_*.py              # Testes de validação
```

## 🚀 Deploy

### **Servidor Linux**
```bash
# 1. Setup servidor
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# 2. Deploy aplicação
cd /var/www/
sudo git clone <repo> crypto-analyzer
sudo chown -R $USER:$USER crypto-analyzer
cd crypto-analyzer

# 3. Setup ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configurar service (systemd)
sudo nano /etc/systemd/system/crypto-analyzer.service

# 5. Start service
sudo systemctl enable crypto-analyzer
sudo systemctl start crypto-analyzer
```

---

**🎯 Próximos Passos**

Após a instalação bem-sucedida:

1. **Testar funcionamento**: `python src/main.py bitcoin`
2. **Configurar API keys** (opcional): Seguir seção de configuração
3. **Executar testes**: `python test_corrections.py`
4. **Ler documentação**: Verificar `/docs` e `/agents`
5. **Usar aplicação**: Executar análises de tokens

**📞 Suporte**

- Documentação completa: [docs/README.md](../docs/README.md)
- Testes de diagnóstico: `python test_corrections.py`
- Issues conhecidos: Verificar logs e seção de troubleshooting
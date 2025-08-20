import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import COINGECKO_API, FEAR_GREED_API, CACHE_DURATION

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crypto-Analyzer/1.0'
        })
        
        # Rate limiting configuration
        self.last_request_time = None
        self.request_count = 0
        self.rate_limit_reset = datetime.now()
        self.MIN_TIME_BETWEEN_REQUESTS = 2.5  # segundos entre requests
        self.MAX_REQUESTS_PER_MINUTE = 25     # máximo 25 requests por minuto (conservador)
    
    def _is_cache_valid(self, key):
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return time.time() - timestamp < CACHE_DURATION
    
    def _wait_if_needed(self):
        """Implementa rate limiting para evitar 429"""
        # Reseta contador a cada minuto
        if datetime.now() > self.rate_limit_reset + timedelta(minutes=1):
            self.request_count = 0
            self.rate_limit_reset = datetime.now()
        
        # Se atingiu limite por minuto, espera
        if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (datetime.now() - self.rate_limit_reset).seconds
            if wait_time > 0:
                print(f"⏳ Rate limit atingido. Aguardando {wait_time}s...")
                time.sleep(wait_time)
                self.request_count = 0
                self.rate_limit_reset = datetime.now()
        
        # Espera mínimo entre requests
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.MIN_TIME_BETWEEN_REQUESTS:
                wait_time = self.MIN_TIME_BETWEEN_REQUESTS - elapsed
                print(f"⏳ Aguardando {wait_time:.1f}s entre requests...")
                time.sleep(wait_time)
        
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    def _make_request(self, url: str, params: Dict = None, retries: int = 3) -> Optional[Dict]:
        """Faz request com retry logic e rate limiting"""
        
        for attempt in range(retries):
            try:
                self._wait_if_needed()
                
                print(f"API Request: {url.split('/')[-1]} (tentativa {attempt+1}/{retries})")
                response = self.session.get(url, params=params, timeout=15)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit hit - espera progressivamente mais
                    wait_time = 30 * (attempt + 1)
                    print(f"Rate limit (429). Aguardando {wait_time}s antes de tentar novamente...")
                    time.sleep(wait_time)
                    # Reset rate limit counter
                    self.request_count = 0
                    self.rate_limit_reset = datetime.now()
                elif response.status_code == 404:
                    print(f"Recurso não encontrado (404): {url}")
                    return None
                else:
                    print(f"Erro {response.status_code}: {response.text[:100]}")
                    if attempt == retries - 1:
                        return None
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout na requisição (tentativa {attempt+1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição (tentativa {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(5 * (attempt + 1))
        
        print(f"Falha em todas as tentativas para: {url}")
        return None
    
    def _get_cached_or_fetch(self, key, fetch_func):
        if self._is_cache_valid(key):
            print(f"📦 Usando cache para {key}")
            return self.cache[key][1]
        
        try:
            data = fetch_func()
            if data:
                self.cache[key] = (time.time(), data)
            return data
        except Exception as e:
            print(f"Erro ao buscar {key}: {e}")
            return None
    
    def search_token(self, query):
        """Busca token ID - tenta mapeamento direto primeiro para evitar API calls"""
        
        # Mapeamento direto de símbolos conhecidos para IDs (evita search API)
        direct_mapping = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'binancecoin': 'binancecoin', 'bnb': 'binancecoin',
            'cardano': 'cardano', 'ada': 'cardano',
            'solana': 'solana', 'sol': 'solana',
            'polygon': 'matic-network', 'matic': 'matic-network',
            'chainlink': 'chainlink', 'link': 'chainlink',
            'polkadot': 'polkadot', 'dot': 'polkadot',
            'avalanche-2': 'avalanche-2', 'avax': 'avalanche-2',
            'uniswap': 'uniswap', 'uni': 'uniswap',
            'litecoin': 'litecoin', 'ltc': 'litecoin',
            'dogecoin': 'dogecoin', 'doge': 'dogecoin',
            'shiba-inu': 'shiba-inu', 'shib': 'shiba-inu',
            'arbitrum': 'arbitrum', 'arb': 'arbitrum',
            'optimism': 'optimism', 'op': 'optimism',
            'worldcoin': 'worldcoin', 'wld': 'worldcoin',
            'celestia': 'celestia', 'tia': 'celestia',
            'kaspa': 'kaspa', 'kas': 'kaspa',
            'pendle': 'pendle',
            'ripple': 'ripple', 'xrp': 'ripple',
            'stellar': 'stellar', 'xlm': 'stellar',
            'cosmos': 'cosmos', 'atom': 'cosmos',
            'algorand': 'algorand', 'algo': 'algorand',
            'tezos': 'tezos', 'xtz': 'tezos',
            'monero': 'monero', 'xmr': 'monero'
        }
        
        query_lower = query.lower()
        
        # Tenta mapeamento direto primeiro
        if query_lower in direct_mapping:
            return direct_mapping[query_lower]
        
        # Se não encontrou no mapeamento, tenta a API de search como fallback
        def _search():
            print(f"🔍 Buscando '{query}' via API (não encontrado no mapeamento direto)")
            url = f"{COINGECKO_API}/search"
            params = {'query': query}
            
            data = self._make_request(url, params)
            if not data:
                return None
            
            coins = data.get('coins', [])
            if not coins:
                return None
            
            # Busca match exato por símbolo ou nome
            for coin in coins:
                if (coin['symbol'].lower() == query_lower or 
                    coin['name'].lower() == query_lower):
                    return coin['id']
            
            # Se não encontrou match exato, pega o primeiro
            return coins[0]['id']
        
        return self._get_cached_or_fetch(f"search_{query}", _search)
    
    def get_token_data(self, token_id: str) -> Optional[Dict]:
        """Busca dados do token com rate limiting"""
        
        def _fetch_token():
            if not token_id:
                return None
                
            url = f"{COINGECKO_API}/coins/{token_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'  # Reduz tamanho da resposta
            }
            
            data = self._make_request(url, params)
            if not data:
                return None
            
            return self._process_token_data(data, token_id)
        
        return self._get_cached_or_fetch(f"token_{token_id}", _fetch_token)
    
    def _process_token_data(self, data: Dict, token_id: str) -> Dict:
        """Processa dados do token da API"""
        market_data = data.get('market_data', {})
        community_data = data.get('community_data', {})
        developer_data = data.get('developer_data', {})
        
        # Buscar idade do token - múltiplas fontes
        genesis_date = data.get('genesis_date') or data.get('ico_genesis_date')
        age_days = self.calculate_age_days(token_id, genesis_date, market_data)
        
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'symbol': data.get('symbol', '').upper(),
            'price': market_data.get('current_price', {}).get('usd', 0),
            'market_cap': market_data.get('market_cap', {}).get('usd', 0),
            'volume': market_data.get('total_volume', {}).get('usd', 0),
            'price_change_24h': market_data.get('price_change_percentage_24h', 0),
            'price_change_7d': market_data.get('price_change_percentage_7d', 0),
            'price_change_30d': market_data.get('price_change_percentage_30d', 0),
            'market_cap_rank': market_data.get('market_cap_rank'),
            'circulating_supply': market_data.get('circulating_supply', 0),
            'total_supply': market_data.get('total_supply', 0),
            'max_supply': market_data.get('max_supply'),
            'ath': market_data.get('ath', {}).get('usd', 0),
            'atl': market_data.get('atl', {}).get('usd', 0),
            'category': data.get('categories', ['unknown'])[0] if data.get('categories') else 'unknown',
            'description': data.get('description', {}).get('en', ''),
            'homepage': data.get('links', {}).get('homepage', [''])[0],
            'twitter_followers': community_data.get('twitter_followers', 0),
            'reddit_subscribers': community_data.get('reddit_subscribers', 0),
            'github_commits': developer_data.get('commit_count_4_weeks', 0),
            'github_stars': developer_data.get('stars', 0),
            'age_days': age_days,
            'liquidity_score': market_data.get('liquidity_score', 0)
        }
    
    def get_fear_greed(self):
        def _fetch_fear_greed():
            data = self._make_request(FEAR_GREED_API)
            
            if data and 'data' in data and len(data['data']) > 0:
                latest = data['data'][0]
                return {
                    'value': int(latest['value']),
                    'classification': latest['value_classification'],
                    'timestamp': latest['timestamp']
                }
            
            # Fallback se API falhar
            return {'value': 50, 'classification': 'Neutral', 'timestamp': str(int(time.time()))}
        
        return self._get_cached_or_fetch("fear_greed", _fetch_fear_greed)
    
    def get_token_list(self, limit=100):
        def _fetch_list():
            url = f"{COINGECKO_API}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(limit, 250),  # CoinGecko max
                'page': 1,
                'sparkline': 'false'
            }
            
            return self._make_request(url, params)
        
        return self._get_cached_or_fetch(f"top_tokens_{limit}", _fetch_list)
    
    def calculate_age_days(self, token_id, genesis_date, market_data):
        """Calcula idade do token em dias usando múltiplas estratégias"""
        
        # Estratégia 1: Genesis date direto
        if genesis_date:
            try:
                if isinstance(genesis_date, str):
                    # Diferentes formatos de data que podem vir da API
                    for date_format in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ']:
                        try:
                            if 'T' in genesis_date:
                                # Remove timezone se presente
                                genesis_date_clean = genesis_date.replace('Z', '').split('.')[0]
                                genesis = datetime.strptime(genesis_date_clean, '%Y-%m-%dT%H:%M:%S')
                            else:
                                genesis = datetime.strptime(genesis_date, '%Y-%m-%d')
                            
                            age_days = (datetime.now() - genesis).days
                            if age_days > 0:  # Verificar se é uma data válida
                                return age_days
                            break
                        except ValueError:
                            continue
                else:
                    genesis = genesis_date
                    age_days = (datetime.now() - genesis).days
                    if age_days > 0:
                        return age_days
            except Exception:
                pass
        
        # Estratégia 2: Tentar pelo histórico de preços
        age_from_history = self.get_age_from_history(token_id)
        if age_from_history > 0:
            return age_from_history
        
        # Estratégia 3: Estimativa baseada em market cap e outras métricas
        return self.estimate_age_by_metrics(market_data)
    
    def get_age_from_history(self, token_id):
        """Busca idade através do histórico de preços do CoinGecko"""
        try:
            url = f"{COINGECKO_API}/coins/{token_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': 'max'  # Máximo disponível no plano gratuito
            }
            
            data = self._make_request(url, params, retries=2)  # Menos retries para history
            
            if data and data.get('prices') and len(data['prices']) > 0:
                # Primeira data disponível nos dados históricos
                first_timestamp = data['prices'][0][0]  # timestamp em milliseconds
                first_date = datetime.fromtimestamp(first_timestamp / 1000)
                age_days = (datetime.now() - first_date).days
                
                # Verificar se é uma idade razoável (não no futuro, não muito antiga)
                if 0 < age_days < 20000:  # Não mais de ~55 anos
                    return age_days
            
        except Exception:
            # Falha silenciosa - fallback para outras estratégias
            pass
        
        return 0
    
    def estimate_age_by_metrics(self, market_data):
        """Estimativa de idade baseada em métricas do token"""
        market_cap = market_data.get('market_cap', {}).get('usd', 0)
        market_cap_rank = market_data.get('market_cap_rank', 9999)
        
        # Tokens muito estabelecidos (top 50, market cap alto)
        if market_cap_rank <= 50 and market_cap > 1_000_000_000:  # Top 50 e >$1B
            return 1500  # ~4 anos (tokens bem estabelecidos)
        
        # Tokens estabelecidos (top 100, market cap médio-alto)
        elif market_cap_rank <= 100 and market_cap > 500_000_000:  # Top 100 e >$500M
            return 1000  # ~2.7 anos
        
        # Tokens conhecidos (top 300, market cap médio)
        elif market_cap_rank <= 300 and market_cap > 100_000_000:  # Top 300 e >$100M
            return 730  # ~2 anos
        
        # Tokens em desenvolvimento (market cap baixo mas existente)
        elif market_cap > 10_000_000:  # >$10M
            return 365  # ~1 ano
        
        # Tokens novos ou pequenos
        elif market_cap > 1_000_000:  # >$1M
            return 200  # ~6-7 meses
        
        # Tokens muito novos
        else:
            return 90  # ~3 meses (pode falhar na eliminatória)
    
    def get_price_history(self, token_id: str, days: int = 90):
        """Busca histórico de preços para análise técnica"""
        
        cache_key = f"history_{token_id}_{days}"
        if cache_key in self.cache:
            cache_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cache_time) < timedelta(hours=1):  # Cache por 1 hora
                print(f"📦 Usando cache para histórico de {token_id}")
                return cached_data
        
        url = f"{COINGECKO_API}/coins/{token_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily' if days > 30 else 'hourly'
        }
        
        data = self._make_request(url, params, retries=2)  # Menos retries para histórico
        
        if data and 'prices' in data:
            # Processa em formato útil
            prices = [p[1] for p in data['prices']]
            volumes = [v[1] for v in data.get('total_volumes', [])]
            
            if not prices:
                return None
            
            result = {
                'prices': prices,
                'volumes': volumes,
                'dates': [p[0] for p in data['prices']],
                'current_price': prices[-1] if prices else 0,
                'min_90d': min(prices) if prices else 0,
                'max_90d': max(prices) if prices else 0,
                'avg_30d': sum(prices[-30:]) / len(prices[-30:]) if len(prices) >= 30 else 0,
                'avg_7d': sum(prices[-7:]) / len(prices[-7:]) if len(prices) >= 7 else 0,
                'data_points': len(prices)
            }
            
            self.cache[cache_key] = (datetime.now(), result)
            return result
        
        return None
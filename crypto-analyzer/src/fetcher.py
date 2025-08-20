import requests
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import COINGECKO_API, FEAR_GREED_API, CACHE_DURATION

class DataFetcher:
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoAnalyzer/2.0',
            'Accept': 'application/json'
        })
        
        # Rate limiting configuration AJUSTADO
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        self.MIN_TIME_BETWEEN_REQUESTS = 4.0  # Aumentado de 2.5 para 4.0
        self.MAX_REQUESTS_PER_MINUTE = 15     # Reduzido de 25 para 15 (mais conservador)
        self.last_endpoint = ""  # Para tracking de endpoint
    
    def _is_cache_valid(self, key):
        if key not in self.cache:
            return False
        timestamp, _ = self.cache[key]
        return time.time() - timestamp < CACHE_DURATION
    
    def _rate_limit(self):
        """Rate limiting inteligente para evitar 429"""
        import random
        
        current_time = time.time()
        
        # Reset contador a cada minuto
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Verificar limite por minuto
        if self.request_count >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (current_time - self.request_window_start)
            if wait_time > 0:
                print(f"Rate limit atingido. Aguardando {wait_time:.1f}s...")
                time.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Delay mínimo entre requests com jitter
        elapsed = current_time - self.last_request_time
        jitter = random.uniform(0.5, 1.5)  # Jitter para randomizar timing
        min_delay = self.MIN_TIME_BETWEEN_REQUESTS + jitter
        
        if elapsed < min_delay:
            sleep_time = min_delay - elapsed
            print(f"Aguardando {sleep_time:.1f}s entre requests...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, url: str, params: Dict = None, headers: Dict = None, retries: int = 3) -> Optional[requests.Response]:
        """Faz request com retry logic e rate limiting - retorna Response object"""
        
        # Headers padrão + headers customizados
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        for attempt in range(retries):
            try:
                self._rate_limit()
                
                print(f"API Request: {url.split('/')[-1]} (tentativa {attempt+1}/{retries})")
                response = self.session.get(url, params=params, headers=request_headers, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 401:
                    print(f"Erro de autenticação (401): {url}")
                    print("Pode ser necessário API key ou parâmetros adicionais")
                    return response  # Retorna resposta para tratamento específico
                elif response.status_code == 429:
                    # Rate limit hit - backoff exponencial
                    wait_time = min(60, (2 ** attempt) * 10)  # Max 60s
                    print(f"Rate limit (429). Aguardando {wait_time}s (backoff exponencial)...")
                    time.sleep(wait_time)
                    # Reset contadores
                    self.request_count = 0
                    self.request_window_start = time.time()
                elif response.status_code == 404:
                    print(f"Recurso não encontrado (404): {url}")
                    return response  # Retorna para tratamento específico
                else:
                    print(f"Erro {response.status_code}: {response.text[:100]}")
                    if attempt == retries - 1:
                        return response
                    
            except requests.exceptions.Timeout:
                print(f"Timeout na requisição (tentativa {attempt+1}/{retries})")
                if attempt < retries - 1:
                    # Backoff exponencial para timeouts
                    wait_time = min(30, (2 ** attempt) * 5)
                    time.sleep(wait_time)
            except requests.exceptions.RequestException as e:
                print(f"Erro na requisição (tentativa {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    wait_time = min(30, (2 ** attempt) * 5)
                    time.sleep(wait_time)
        
        print(f"Falha em todas as tentativas para: {url}")
        return None
    
    def _get_cached_or_fetch(self, key, fetch_func):
        if self._is_cache_valid(key):
            print(f"CACHE Usando cache para {key}")
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
            print(f"Buscando '{query}' via API (não encontrado no mapeamento direto)")
            url = f"{COINGECKO_API}/search"
            params = {'query': query}
            
            response = self._make_request(url, params)
            if not response or response.status_code != 200:
                return None
            
            try:
                data = response.json()
            except:
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
            
            response = self._make_request(url, params)
            if not response or response.status_code != 200:
                return None
            
            try:
                data = response.json()
                return self._process_token_data(data, token_id)
            except Exception as e:
                print(f"Erro ao processar dados do token {token_id}: {e}")
                return None
        
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
            response = self._make_request(FEAR_GREED_API)
            
            if not response or response.status_code != 200:
                return None
            
            try:
                data = response.json()
            except:
                return None
            
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
        """Busca histórico com fallback chain: market_chart -> OHLC -> basic_price"""
        
        cache_key = f"history_{token_id}_{days}"
        if cache_key in self.cache:
            cache_time, cached_data = self.cache[cache_key]
            if (datetime.now() - cache_time) < timedelta(hours=1):
                print(f"Cache hit para histórico de {token_id}")
                return cached_data
        
        print(f"Buscando histórico para {token_id} ({days} dias)...")
        
        # TENTATIVA 1: market_chart (dados mais ricos)
        result = self._try_market_chart(token_id, days)
        if result:
            print(f"market_chart OK para {token_id}")
            self.cache[cache_key] = (datetime.now(), result)
            return result
        
        # TENTATIVA 2: OHLC (fallback para 401 no market_chart)
        print(f"market_chart falhou, tentando OHLC...")
        result = self._try_ohlc_data(token_id, min(days, 30))
        if result:
            print(f"OHLC OK para {token_id}")
            self.cache[cache_key] = (datetime.now(), result)
            return result
        
        # TENTATIVA 3: Dados básicos (preço atual)
        print(f"OHLC também falhou, usando dados básicos...")
        result = self._get_basic_price_data(token_id)
        if result:
            print(f"Dados básicos obtidos para {token_id}")
            # Cache por menos tempo (dados limitados)
            cache_time_basic = datetime.now() - timedelta(minutes=30)
            self.cache[cache_key] = (cache_time_basic, result)
            return result
        
        print(f"Todas as tentativas falharam para {token_id}")
        return self._empty_price_data()
    
    def _try_market_chart(self, token_id: str, days: int) -> Optional[Dict]:
        """Tenta buscar dados via market_chart"""
        url = f"{COINGECKO_API}/coins/{token_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily' if days > 30 else 'hourly'
        }
        
        response = self._make_request(url, params, retries=2)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                if 'prices' in data and data['prices']:
                    return self._process_price_data(data)
            except Exception as e:
                print(f"Erro ao processar market_chart: {e}")
        elif response and response.status_code == 401:
            print(f"market_chart retornou 401 (sem autenticação)")
        
        return None
    
    def _try_ohlc_data(self, token_id: str, days: int) -> Optional[Dict]:
        """Tenta buscar dados via OHLC (máx 30 dias)"""
        url = f"{COINGECKO_API}/coins/{token_id}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        response = self._make_request(url, params, retries=2)
        
        if response and response.status_code == 200:
            try:
                ohlc_data = response.json()
                if ohlc_data and len(ohlc_data) > 0:
                    return self._process_ohlc_data(ohlc_data)
            except Exception as e:
                print(f"Erro ao processar OHLC: {e}")
        
        return None
    
    def _empty_price_data(self) -> Dict:
        """Retorna estrutura vazia válida quando tudo falha"""
        return {
            'prices': [],
            'volumes': [],
            'dates': [],
            'current_price': 0,
            'min_90d': 0,
            'max_90d': 0,
            'avg_30d': 0,
            'avg_7d': 0,
            'data_points': 0
        }
    
    def _process_price_data(self, data):
        """Processa dados do market_chart"""
        try:
            prices = [p[1] for p in data['prices']]
            volumes = [v[1] for v in data.get('total_volumes', [])]
            
            if not prices:
                return None
            
            return {
                'prices': prices,
                'volumes': volumes,
                'dates': [p[0] for p in data['prices']],
                'current_price': prices[-1],
                'min_90d': min(prices),
                'max_90d': max(prices),
                'avg_30d': sum(prices[-30:]) / len(prices[-30:]) if len(prices) >= 30 else sum(prices) / len(prices),
                'avg_7d': sum(prices[-7:]) / len(prices[-7:]) if len(prices) >= 7 else sum(prices) / len(prices),
                'data_points': len(prices)
            }
        except Exception as e:
            print(f"Erro ao processar dados de preço: {e}")
            return None
    
    def _process_ohlc_data(self, ohlc_data):
        """Processa dados OHLC (Open, High, Low, Close)"""
        try:
            # OHLC retorna: [timestamp, open, high, low, close]
            prices = [candle[4] for candle in ohlc_data]  # Close prices
            dates = [candle[0] for candle in ohlc_data]
            
            if not prices:
                return None
            
            return {
                'prices': prices,
                'volumes': [],  # OHLC não inclui volume
                'dates': dates,
                'current_price': prices[-1],
                'min_90d': min(prices),
                'max_90d': max(prices),
                'avg_30d': sum(prices[-30:]) / len(prices[-30:]) if len(prices) >= 30 else sum(prices) / len(prices),
                'avg_7d': sum(prices[-7:]) / len(prices[-7:]) if len(prices) >= 7 else sum(prices) / len(prices),
                'data_points': len(prices)
            }
        except Exception as e:
            print(f"Erro ao processar dados OHLC: {e}")
            return None
    
    def _get_basic_price_data(self, token_id):
        """Fallback: dados básicos sem histórico"""
        try:
            # Busca dados atuais do token
            url = f"{COINGECKO_API}/coins/{token_id}"
            response = self._make_request(url, retries=1)
            
            if response and response.status_code == 200:
                data = response.json()
                current_price = data.get('market_data', {}).get('current_price', {}).get('usd', 0)
                
                if current_price > 0:
                    return {
                        'prices': [current_price],
                        'volumes': [],
                        'dates': [int(time.time() * 1000)],
                        'current_price': current_price,
                        'min_90d': current_price,
                        'max_90d': current_price,
                        'avg_30d': current_price,
                        'avg_7d': current_price,
                        'data_points': 1
                    }
        except Exception as e:
            print(f"Erro ao buscar dados básicos: {e}")
        
        # Se tudo falhou, retornar estrutura válida vazia
        print(f"Não foi possível obter histórico completo para {token_id}")
        return {
            'prices': [],
            'volumes': [],
            'dates': [],
            'current_price': 0,
            'min_90d': 0,
            'max_90d': 0,
            'avg_30d': 0,
            'avg_7d': 0,
            'data_points': 0
        }
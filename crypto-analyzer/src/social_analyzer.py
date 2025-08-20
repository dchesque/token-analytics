import requests
import statistics
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import time
from config import (
    LUNARCRUSH_API_KEY, LUNARCRUSH_API_V4, MESSARI_API, DEFILLAMA_API_V2, 
    CRYPTOCOMPARE_API, ENABLE_LUNARCRUSH, USE_ALTERNATIVE_SOCIAL,
    HYPE_THRESHOLDS, CACHE_SOCIAL, CACHE_DEFI, CACHE_FUNDAMENTAL,
    REQUESTS_PER_MINUTE
)

class SocialAnalyzer:
    """Análise social avançada com detecção de hype"""
    
    def __init__(self):
        self.cache = {}
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
    
    def _rate_limit(self):
        """Rate limiting inteligente para evitar bloqueios"""
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
    
    def test_lunarcrush_connection(self) -> Dict:
        """Testa conexão com LunarCrush API v4"""
        if not ENABLE_LUNARCRUSH:
            return {"success": False, "error": "API key não configurada"}
        
        try:
            headers = {
                "Authorization": f"Bearer {LUNARCRUSH_API_KEY}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            # Testar endpoint simples
            url = f"{LUNARCRUSH_API_V4}/public/coins/list"
            params = {"limit": 1}
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True, 
                    "message": f"Conexão OK - {len(data) if isinstance(data, list) else 0} tokens encontrados"
                }
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)[:100]}

    def get_lunarcrush_data(self, symbol: str) -> Dict:
        """Busca dados sociais - LunarCrush v4 com endpoints corretos"""
        
        cache_key = f"lunar_{symbol}"
        if self._check_cache(cache_key, CACHE_SOCIAL):
            return self.cache[cache_key]['data']
        
        # Verifica se tem API key do LunarCrush
        if not ENABLE_LUNARCRUSH:
            print("LunarCrush desabilitado (sem API key) - usando alternativas")
            return self._get_alternative_social_data(symbol)
        
        # Teste de conexão (apenas uma vez por sessão)
        if not hasattr(self, '_lunarcrush_tested'):
            print("Testando conexão com LunarCrush v4...")
            test_result = self.test_lunarcrush_connection()
            if test_result["success"]:
                print(f"OK: {test_result['message']}")
            else:
                print(f"FALHA no teste: {test_result['error']}")
            self._lunarcrush_tested = True
        
        # Mapeamento para coin IDs conhecidos
        coin_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'ADA': 'cardano',
            'AVAX': 'avalanche',
            'XRP': 'xrp',
            'LTC': 'litecoin'
        }
        
        # Converter símbolo para coin ID
        coin_id = coin_mapping.get(symbol.upper(), symbol.lower())
        
        # Headers com autenticação
        headers = {
            "Authorization": f"Bearer {LUNARCRUSH_API_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # ESTRATÉGIA 1: Tentar endpoint de insights específico
        try:
            url = f"{LUNARCRUSH_API_V4}/public/insights/{coin_id}"
            print(f"🔍 Tentando LunarCrush insights: {url}")
            print(f"🔑 Usando API Key: {LUNARCRUSH_API_KEY[:10]}..." if LUNARCRUSH_API_KEY else "❌ Sem API Key")
            
            self._rate_limit()
            response = self.session.get(url, headers=headers, timeout=15)
            
            print(f"📊 Status HTTP: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Erro HTTP: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dados recebidos: {type(data)} com {len(data) if isinstance(data, (list, dict)) else 0} items")
                
                # Processar resposta do endpoint insights
                if isinstance(data, dict):
                    result = self._parse_lunarcrush_v4_data(data, 'insights')
                    print(f"✅ LunarCrush dados obtidos via insights")
                    self._save_cache(cache_key, result, CACHE_SOCIAL)
                    return result
                    
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erro de conexão no endpoint insights: {str(e)[:100]}")
        except Exception as e:
            print(f"❌ Erro no endpoint insights: {str(e)[:100]}")
        
        # ESTRATÉGIA 2: Time-series endpoint
        try:
            url = f"{LUNARCRUSH_API_V4}/public/coins/{coin_id}/time-series"
            params = {
                'interval': '1d',
                'data_points': 7
            }
            
            print(f"📈 Tentando LunarCrush time-series: {url}")
            self._rate_limit()
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            print(f"📊 Status HTTP: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Erro HTTP: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dados recebidos: {type(data)} com {len(data) if isinstance(data, (list, dict)) else 0} items")
                
                # Time-series retorna array, pegar o mais recente
                if isinstance(data, list) and data:
                    result = self._parse_lunarcrush_v4_data(data[-1], 'time-series')
                    print(f"✅ LunarCrush dados obtidos via time-series")
                    self._save_cache(cache_key, result, CACHE_SOCIAL)
                    return result
                    
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erro de conexão no endpoint time-series: {str(e)[:100]}")
        except Exception as e:
            print(f"❌ Erro no endpoint time-series: {str(e)[:100]}")
        
        # ESTRATÉGIA 3: Buscar na lista geral e filtrar
        try:
            url = f"{LUNARCRUSH_API_V4}/public/coins/list"
            params = {
                'sort': 'galaxy_score',
                'limit': 100,
                'fields': 'symbol,name,galaxy_score,alt_rank,social_volume,social_dominance'
            }
            
            print(f"📋 Tentando LunarCrush lista geral: {url}")
            self._rate_limit()
            response = self.session.get(url, headers=headers, params=params, timeout=15)
            
            print(f"📊 Status HTTP: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Erro HTTP: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Lista recebida: {len(data) if isinstance(data, list) else 0} tokens")
                
                # Procurar nosso token na lista
                if isinstance(data, list):
                    for coin in data:
                        if (coin.get('symbol', '').upper() == symbol.upper() or 
                            coin.get('name', '').lower() == coin_id):
                            result = self._parse_lunarcrush_v4_data(coin, 'list')
                            print(f"✅ Token {symbol} encontrado na lista do LunarCrush")
                            self._save_cache(cache_key, result, CACHE_SOCIAL)
                            return result
                    print(f"❌ Token {symbol} não encontrado na lista de 100 tokens")
                    
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erro de conexão no endpoint lista: {str(e)[:100]}")
        except Exception as e:
            print(f"❌ Erro no endpoint lista: {str(e)[:100]}")
        
        print(f"🔄 LunarCrush v4 falhou para {symbol} - usando alternativas")
        return self._get_alternative_social_data(symbol)
    
    def _parse_lunarcrush_v4_data(self, data: Dict, source_type: str) -> Dict:
        """Parse dados LunarCrush v4 com adaptação para diferentes formatos"""
        return {
            # Métricas principais (tentativas múltiplas de campos)
            'galaxy_score': float(data.get('galaxy_score', data.get('gs', data.get('score', 0)))),
            'social_volume': int(data.get('social_volume', data.get('sv', data.get('volume', 0)))),
            'social_engagement': int(data.get('social_engagement', data.get('se', 0))),
            'social_contributors': int(data.get('social_contributors', data.get('sc', 0))),
            'social_dominance': float(data.get('social_dominance', data.get('sd', 0))),
            
            # Atividade social
            'tweets': int(data.get('tweets', data.get('t', data.get('twitter_posts', 0)))),
            'reddit_posts': int(data.get('reddit_posts', data.get('reddit', {}).get('posts', 0))),
            'news_articles': int(data.get('news', data.get('n', data.get('news_articles', 0)))),
            
            # Sentimento (com fallback)
            'sentiment_bullish': self._extract_sentiment(data, 'bullish'),
            'sentiment_bearish': self._extract_sentiment(data, 'bearish'),
            
            # Variações
            'social_volume_change': float(data.get('social_volume_24h_change', 
                                                  data.get('sv24h', 
                                                          data.get('change_24h', 0)))),
            'alt_rank': int(data.get('alt_rank', data.get('rank', data.get('market_cap_rank', 999)))),
            'social_volume_24h': int(data.get('social_volume', data.get('sv24h', 0))),
            'galaxy_score_change': float(data.get('galaxy_score_24h_change', data.get('gs24h', 0))),
            
            # Metadata
            'source': f'lunarcrush_v4_{source_type}',
            'history_7d': []
        }
    
    def _extract_sentiment(self, data: Dict, sentiment_type: str) -> float:
        """Extrai sentimento com múltiplas tentativas de formato"""
        try:
            # Formato 1: sentiment.bullish/bearish
            sentiment_obj = data.get('sentiment', {})
            if isinstance(sentiment_obj, dict) and sentiment_type in sentiment_obj:
                return float(sentiment_obj[sentiment_type])
            
            # Formato 2: sentiment_bullish/sentiment_bearish
            key = f'sentiment_{sentiment_type}'
            if key in data:
                return float(data[key])
            
            # Formato 3: bs/br (bullish score, bearish score)
            short_key = 'bs' if sentiment_type == 'bullish' else 'br'
            if short_key in data:
                return float(data[short_key])
            
            # Formato 4: percent_change_24h_sentiment (v2 legacy)
            if sentiment_type == 'bullish' and 'percent_change_24h_sentiment' in data:
                return float(data['percent_change_24h_sentiment'])
            elif sentiment_type == 'bearish' and 'percent_change_24h_sentiment' in data:
                return 100 - float(data['percent_change_24h_sentiment'])
                
        except (ValueError, TypeError):
            pass
        
        # Default: neutro
        return 50.0
    
    def _get_alternative_social_data(self, symbol: str) -> Dict:
        """Alternativa gratuita para dados sociais usando CryptoCompare e CoinGecko"""
        
        cache_key = f"alt_social_{symbol}"
        if self._check_cache(cache_key, CACHE_SOCIAL):
            return self.cache[cache_key]['data']
        
        try:
            # OPÇÃO A: Tenta CryptoCompare Social Stats (gratuito)
            cryptocompare_data = self._get_cryptocompare_social(symbol)
            if cryptocompare_data.get('social_volume', 0) > 0:
                self._save_cache(cache_key, cryptocompare_data, CACHE_SOCIAL)
                return cryptocompare_data
        except:
            pass
        
        # OPÇÃO B: Usa dados básicos do CoinGecko (já disponível no fetcher)
        try:
            from fetcher import DataFetcher
            fetcher = DataFetcher()
            token_id = fetcher.search_token(symbol)
            
            if token_id:
                token_data = fetcher.get_token_data(token_id)
                if token_data:
                    # Converte dados do CoinGecko para formato social
                    result = {
                        'galaxy_score': 0,  # Não disponível
                        'social_volume': token_data.get('twitter_followers', 0) // 1000,  # Aproximação
                        'social_engagement': token_data.get('reddit_subscribers', 0) // 100,
                        'social_contributors': 0,
                        'social_dominance': 0,
                        'tweets': 0,  # Não disponível
                        'reddit_posts': 0,  # Não disponível
                        'news_articles': 0,  # Não disponível
                        
                        # Sentimento neutro (não disponível)
                        'sentiment_bullish': 50,
                        'sentiment_bearish': 50,
                        
                        # Variações baseadas em preço (aproximação)
                        'social_volume_change': max(-50, min(50, token_data.get('price_change_24h', 0))),
                        'galaxy_score_change': 0,
                        'alt_rank': token_data.get('market_cap_rank', 999),
                        
                        # Metadados
                        'source': 'coingecko_community',
                        'history_7d': []
                    }
                    
                    self._save_cache(cache_key, result, CACHE_SOCIAL)
                    return result
        except:
            pass
        
        # OPÇÃO C: Retorna dados limitados básicos
        result = {
            'galaxy_score': 0,
            'social_volume': 0,
            'social_engagement': 0,
            'social_contributors': 0,
            'social_dominance': 0,
            'tweets': 0,
            'reddit_posts': 0,
            'news_articles': 0,
            'sentiment_bullish': 50,
            'sentiment_bearish': 50,
            'social_volume_change': 0,
            'galaxy_score_change': 0,
            'alt_rank': 999,
            'source': 'limited',
            'history_7d': []
        }
        
        self._save_cache(cache_key, result, CACHE_SOCIAL)
        return result
    
    def _get_cryptocompare_social(self, symbol: str) -> Dict:
        """Busca dados sociais do CryptoCompare (gratuito)"""
        
        try:
            # Primeiro, tenta obter ID do CryptoCompare para o símbolo
            coin_list_url = f"{CRYPTOCOMPARE_API}/all/coinlist"
            response = self.session.get(coin_list_url, timeout=10)
            
            if response.status_code == 200:
                coins = response.json().get('Data', {})
                coin_info = None
                
                # Procura pelo símbolo
                for coin_id, info in coins.items():
                    if info.get('Symbol', '').upper() == symbol.upper():
                        coin_info = info
                        break
                
                if coin_info:
                    coin_id = coin_info.get('Id')
                    
                    # Busca dados sociais
                    social_url = f"{CRYPTOCOMPARE_API}/social/coin/latest"
                    params = {'coinId': coin_id}
                    
                    social_response = self.session.get(social_url, params=params, timeout=10)
                    
                    if social_response.status_code == 200:
                        social_data = social_response.json().get('Data', {})
                        
                        return {
                            'galaxy_score': 0,  # Não disponível no CryptoCompare
                            'social_volume': social_data.get('General', {}).get('Points', 0),
                            'social_engagement': social_data.get('Twitter', {}).get('Points', 0),
                            'social_contributors': social_data.get('Reddit', {}).get('active_users', 0),
                            'social_dominance': 0,
                            'tweets': social_data.get('Twitter', {}).get('statuses', 0),
                            'reddit_posts': social_data.get('Reddit', {}).get('posts_per_day', 0),
                            'news_articles': 0,
                            
                            # Sentimento (não disponível, usa neutro)
                            'sentiment_bullish': 50,
                            'sentiment_bearish': 50,
                            
                            # Variações (não disponível diretamente)
                            'social_volume_change': 0,
                            'galaxy_score_change': 0,
                            'alt_rank': 999,
                            
                            # Metadados
                            'source': 'cryptocompare',
                            'history_7d': []
                        }
        except Exception as e:
            print(f"Erro CryptoCompare: {str(e)[:50]}")
        
        return {}

    def get_messari_data(self, symbol: str) -> Dict:
        """Busca dados fundamentais do Messari"""
        
        cache_key = f"messari_{symbol}"
        if self._check_cache(cache_key, CACHE_FUNDAMENTAL):
            return self.cache[cache_key]['data']
        
        try:
            self._rate_limit()
            
            url = f"{MESSARI_API}/assets/{symbol}/metrics"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                metrics = data.get('metrics', {})
                
                result = {
                    # Market data limpo
                    'real_volume': metrics.get('market_data', {}).get('real_volume_last_24_hours', 0),
                    'volume_turnover': metrics.get('market_data', {}).get('volume_turnover_last_24_hours_percentage', 0),
                    
                    # Supply metrics
                    'y2050_supply': metrics.get('supply', {}).get('y_2050', 0),
                    'liquid_supply': metrics.get('supply', {}).get('liquid', 0),
                    'supply_revived_90d': metrics.get('supply', {}).get('supply_revived_90d', 0),
                    
                    # Tokenomics
                    'annual_inflation': metrics.get('supply', {}).get('annual_inflation_percent', 0),
                    'stock_to_flow': metrics.get('supply', {}).get('stock_to_flow', 0),
                    
                    # Developer activity
                    'developers_count': metrics.get('developer_activity', {}).get('developers_count', 0),
                    'watchers': metrics.get('developer_activity', {}).get('watchers', 0),
                    
                    # Risk metrics
                    'volatility_30d': metrics.get('risk_metrics', {}).get('volatility_last_30_days', 0),
                    'sharpe_ratio_30d': metrics.get('risk_metrics', {}).get('sharpe_ratio_last_30_days', 0)
                }
                
                self._save_cache(cache_key, result, CACHE_FUNDAMENTAL)
                return result
                
        except Exception as e:
            print(f"⚠️ Erro Messari para {symbol}: {e}")
        
        return self._empty_messari_data()
    
    def get_defillama_extended(self, protocol: str) -> Dict:
        """Busca dados DeFi expandidos do DeFiLlama"""
        
        cache_key = f"defi_{protocol}"
        if self._check_cache(cache_key, CACHE_DEFI):
            return self.cache[cache_key]['data']
        
        try:
            self._rate_limit()
            
            # TVL e métricas básicas
            url = f"{DEFILLAMA_API_V2}/protocol/{protocol}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Busca yields se disponível
                yields_data = {}
                try:
                    yields_url = f"{DEFILLAMA_API_V2}/yields/protocol/{protocol}"
                    yields_response = self.session.get(yields_url, timeout=10)
                    if yields_response.status_code == 200:
                        yields_data = yields_response.json()
                except:
                    pass
                
                result = {
                    # TVL metrics
                    'tvl_current': data.get('tvl', 0),
                    'tvl_7d_change': data.get('change_7d', 0),
                    'tvl_30d_change': data.get('change_30d', 0),
                    'mcap_to_tvl': data.get('mcap', 0) / data.get('tvl', 1) if data.get('tvl', 0) > 0 else 999,
                    
                    # Chain breakdown
                    'chains': list(data.get('chainTvls', {}).keys()),
                    'chain_tvls': data.get('chainTvls', {}),
                    'main_chain': max(data.get('chainTvls', {}), key=data.get('chainTvls', {}).get) if data.get('chainTvls') else 'unknown',
                    
                    # Revenue metrics
                    'revenue_24h': data.get('revenue24h', 0),
                    'revenue_7d': data.get('revenue7d', 0),
                    'revenue_30d': data.get('revenue30d', 0),
                    'fees_24h': data.get('fees24h', 0),
                    'fees_7d': data.get('fees7d', 0),
                    
                    # Protocol metrics
                    'user_count': data.get('users', {}).get('total', 0),
                    'user_24h': data.get('users', {}).get('daily', 0),
                    'tx_count_24h': data.get('txs', {}).get('daily', 0),
                    
                    # Yields
                    'apy': yields_data.get('apy', 0) if yields_data else 0,
                    'base_apy': yields_data.get('apyBase', 0) if yields_data else 0,
                    'reward_apy': yields_data.get('apyReward', 0) if yields_data else 0,
                    
                    # Risk
                    'audit_links': data.get('audit_links', []),
                    'hack_history': data.get('hacks', []),
                    'category': data.get('category', 'unknown')
                }
                
                self._save_cache(cache_key, result, CACHE_DEFI)
                return result
                
        except Exception as e:
            print(f"⚠️ Erro DeFiLlama para {protocol}: {e}")
        
        return self._empty_defi_data()
    
    def detect_hype(self, symbol: str, social_data: Dict) -> Dict:
        """Detecta padrões de hype baseado em dados sociais (adaptado para dados limitados)"""
        
        hype_signals = []
        hype_score = 0
        
        # Identifica fonte dos dados
        data_source = social_data.get('source', 'full')
        
        if data_source == 'limited':
            # Análise básica com dados limitados
            return {
                'hype_score': 0,
                'hype_level': 'DADOS SOCIAIS LIMITADOS',
                'hype_risk': 'Análise social não disponível',
                'hype_color': 'grey',
                'signals': ['Configure API key do LunarCrush para análise social completa'],
                'recommendations': ['Baseie-se nos fundamentos e análise técnica', 'Volume e momentum são indicadores disponíveis'],
                'data_source': 'limited'
            }
        
        # Análise completa se tiver dados sociais
        # 1. Análise de volume social
        social_change = social_data.get('social_volume_change', 0)
        
        if social_change > HYPE_THRESHOLDS['extreme']:
            hype_score += 40
            hype_signals.append(f"Volume social +{social_change:.0f}% (EXTREMO)")
        elif social_change > HYPE_THRESHOLDS['high']:
            hype_score += 25
            hype_signals.append(f"Volume social +{social_change:.0f}% (ALTO)")
        elif social_change > HYPE_THRESHOLDS['moderate']:
            hype_score += 15
            hype_signals.append(f"Volume social +{social_change:.0f}% (moderado)")
        
        # 2. Galaxy Score change (se disponível)
        galaxy_change = social_data.get('galaxy_score_change', 0)
        
        if galaxy_change > 50:
            hype_score += 20
            hype_signals.append(f"Galaxy Score subiu {galaxy_change:.0f}%")
        
        # 3. Análise de sentimento
        bullish = social_data.get('sentiment_bullish', 50)
        
        if bullish > 85:
            hype_score += 15
            hype_signals.append(f"Sentimento {bullish:.0f}% bullish (muito alto)")
        elif bullish > 70:
            hype_score += 10
            hype_signals.append(f"Sentimento {bullish:.0f}% bullish")
        
        # 4. Análise de atividade social (adaptada para diferentes fontes)
        social_volume = social_data.get('social_volume', 0)
        tweets = social_data.get('tweets', 0)
        
        if social_volume > 1000 or tweets > 100:
            hype_score += 10
            hype_signals.append(f"Alta atividade social detectada")
        
        # 5. Alt Rank melhoria
        alt_rank = social_data.get('alt_rank', 999)
        
        if alt_rank < 10:
            hype_score += 10
            hype_signals.append(f"Alt Rank #{alt_rank} (top 10)")
        elif alt_rank < 50:
            hype_score += 5
            hype_signals.append(f"Alt Rank #{alt_rank}")
        
        # 6. Bonus para dados do CryptoCompare/CoinGecko (indicadores alternativos)
        if data_source in ['cryptocompare', 'coingecko_community']:
            social_engagement = social_data.get('social_engagement', 0)
            if social_engagement > 50:
                hype_score += 5
                hype_signals.append(f"Engajamento social elevado ({data_source})")
        
        # Classificação do hype
        if hype_score >= 70:
            hype_level = "HYPE EXTREMO"
            hype_risk = "Muito alto risco de FOMO/correção"
            hype_color = "red"
        elif hype_score >= 50:
            hype_level = "HYPE ALTO"
            hype_risk = "Alto risco de volatilidade"
            hype_color = "orange"
        elif hype_score >= 30:
            hype_level = "HYPE MODERADO"
            hype_risk = "Atenção aumentando"
            hype_color = "yellow"
        elif hype_score >= 15:
            hype_level = "INTERESSE CRESCENTE"
            hype_risk = "Momentum inicial"
            hype_color = "blue"
        else:
            hype_level = "NORMAL"
            hype_risk = "Sem sinais de hype"
            hype_color = "green"
        
        # Recomendações baseadas no hype
        recommendations = []
        
        if hype_score >= 70:
            recommendations.append("CUIDADO: Possível topo local")
            recommendations.append("Aguarde correção se quiser entrar")
            recommendations.append("Se já tem posição, considere realizar parcial")
        elif hype_score >= 50:
            recommendations.append("Entre com cautela")
            recommendations.append("Use stops apertados")
            recommendations.append("Posição reduzida recomendada")
        elif hype_score >= 30:
            recommendations.append("Monitore de perto")
            recommendations.append("Possível início de movimento")
            recommendations.append("Prepare estratégia de entrada")
        else:
            recommendations.append("Foque na análise fundamental")
            recommendations.append("Dados sociais limitados - use outras métricas")
        
        # Adiciona informação sobre fonte de dados
        if data_source != 'lunarcrush_v4':
            recommendations.append(f"Dados de: {data_source.replace('_', ' ').title()}")
        
        return {
            'hype_score': hype_score,
            'hype_level': hype_level,
            'hype_risk': hype_risk,
            'hype_color': hype_color,
            'signals': hype_signals,
            'recommendations': recommendations,
            'data_source': data_source
        }
    
    def _check_cache(self, key: str, duration: int) -> bool:
        """Verifica se cache é válido"""
        if key in self.cache:
            cached_time = self.cache[key]['time']
            if datetime.now() - cached_time < timedelta(seconds=duration):
                return True
        return False
    
    def _save_cache(self, key: str, data: Dict, duration: int):
        """Salva no cache"""
        self.cache[key] = {
            'time': datetime.now(),
            'data': data
        }
    
    def _empty_social_data(self) -> Dict:
        """Retorna estrutura vazia para social data"""
        return {
            'galaxy_score': 0,
            'social_volume': 0,
            'social_volume_change': 0,
            'sentiment_bullish': 50,
            'sentiment_bearish': 50,
            'alt_rank': 999,
            'history_7d': []
        }
    
    def _empty_messari_data(self) -> Dict:
        """Retorna estrutura vazia para Messari"""
        return {
            'real_volume': 0,
            'volatility_30d': 0,
            'developers_count': 0,
            'annual_inflation': 0,
            'stock_to_flow': 0
        }
    
    def _empty_defi_data(self) -> Dict:
        """Retorna estrutura vazia para DeFi"""
        return {
            'tvl_current': 0,
            'mcap_to_tvl': 999,
            'revenue_24h': 0,
            'chains': [],
            'category': 'unknown'
        }
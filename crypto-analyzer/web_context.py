# web_context.py
"""
Web Context Module - Busca informações reais da web
Integra com APIs públicas para dados atualizados
"""

import requests
from typing import Dict, Any
from datetime import datetime

class WebContext:
    """Busca contexto real da web sobre o token"""
    
    def __init__(self):
        self.news_api = "https://api.coingecko.com/api/v3"
        self.timeout = 10
    
    def analyze(self, token: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Busca informações reais da web sobre o token
        """
        try:
            # Buscar dados de tendência
            trending = self._get_trending_status(token)
            
            # Buscar informações de desenvolvimento
            dev_activity = self._get_development_activity(token)
            
            # Buscar dados de comunidade
            community = self._get_community_metrics(token)
            
            # Gerar resumo do contexto web
            summary = self._generate_web_summary(
                token,
                trending,
                dev_activity,
                community
            )
            
            return {
                'status': 'completed',
                'summary': summary,
                'trending': trending,
                'development_activity': dev_activity,
                'community_metrics': community,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'partial',
                'error': str(e),
                'summary': 'Contexto web limitado disponível'
            }
    
    def _get_trending_status(self, token: str) -> Dict:
        """Verifica se o token está em tendência"""
        try:
            # Usar API pública para verificar trending
            response = requests.get(
                f"{self.news_api}/search/trending",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                coins = data.get('coins', [])
                
                # Verificar se o token está na lista
                is_trending = any(
                    coin.get('item', {}).get('symbol', '').upper() == token.upper() 
                    for coin in coins
                )
                
                return {
                    'is_trending': is_trending,
                    'position': next(
                        (i+1 for i, coin in enumerate(coins) 
                         if coin.get('item', {}).get('symbol', '').upper() == token.upper()),
                        0
                    )
                }
            
        except:
            pass
        
        return {'is_trending': False, 'position': 0}
    
    def _get_development_activity(self, token: str) -> Dict:
        """Busca atividade de desenvolvimento real"""
        try:
            # Mapear tokens para IDs do CoinGecko
            token_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'SOL': 'solana',
                'MATIC': 'polygon'
            }
            
            token_id = token_map.get(token.upper(), token.lower())
            
            response = requests.get(
                f"{self.news_api}/coins/{token_id}",
                params={'localization': 'false', 'tickers': 'false', 'market_data': 'false'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                dev_data = data.get('developer_data', {})
                
                return {
                    'forks': dev_data.get('forks', 0),
                    'stars': dev_data.get('stars', 0),
                    'subscribers': dev_data.get('subscribers', 0),
                    'total_issues': dev_data.get('total_issues', 0),
                    'closed_issues': dev_data.get('closed_issues', 0),
                    'pull_requests_merged': dev_data.get('pull_requests_merged', 0),
                    'commit_count_4_weeks': dev_data.get('commit_count_4_weeks', 0)
                }
            
        except:
            pass
        
        return {}
    
    def _get_community_metrics(self, token: str) -> Dict:
        """Busca métricas de comunidade reais"""
        try:
            token_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'SOL': 'solana',
                'MATIC': 'polygon'
            }
            
            token_id = token_map.get(token.upper(), token.lower())
            
            response = requests.get(
                f"{self.news_api}/coins/{token_id}",
                params={'localization': 'false', 'tickers': 'false', 'market_data': 'false'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                community = data.get('community_data', {})
                
                return {
                    'twitter_followers': community.get('twitter_followers', 0),
                    'reddit_subscribers': community.get('reddit_subscribers', 0),
                    'telegram_channel_user_count': community.get('telegram_channel_user_count', 0),
                    'facebook_likes': community.get('facebook_likes', 0)
                }
            
        except:
            pass
        
        return {}
    
    def _generate_web_summary(self, token: str, trending: Dict, 
                            dev_activity: Dict, community: Dict) -> str:
        """Gera resumo claro do contexto web"""
        
        parts = []
        
        # Status de tendência
        if trending.get('is_trending'):
            parts.append(f"{token} está em alta (posição #{trending['position']} nas tendências)")
        
        # Atividade de desenvolvimento
        if dev_activity.get('commit_count_4_weeks', 0) > 100:
            parts.append(f"Alta atividade de desenvolvimento ({dev_activity['commit_count_4_weeks']} commits/mês)")
        elif dev_activity.get('commit_count_4_weeks', 0) > 0:
            parts.append(f"Desenvolvimento ativo ({dev_activity['commit_count_4_weeks']} commits/mês)")
        
        # Comunidade
        total_community = sum([
            community.get('twitter_followers', 0),
            community.get('reddit_subscribers', 0)
        ])
        
        if total_community > 1000000:
            parts.append(f"Comunidade massiva ({total_community/1000000:.1f}M seguidores)")
        elif total_community > 100000:
            parts.append(f"Comunidade forte ({total_community/1000:.0f}K seguidores)")
        
        if not parts:
            parts.append(f"Dados web limitados para {token}")
        
        return ". ".join(parts) + "."

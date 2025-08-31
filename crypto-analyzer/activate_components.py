#!/usr/bin/env python3
"""
activate_components.py - Ativa AI Insights e Web Context com dados reais
Melhora a formatação de texto das análises
"""

import os
import sys
from datetime import datetime

def create_ai_insights_module():
    """Cria módulo de AI Insights usando análise estatística real"""
    
    ai_code = '''# ai_insights.py
"""
AI Insights Module - Análise estatística e padrões reais
Sem simulação - apenas processamento de dados reais
"""

import numpy as np
from typing import Dict, Any

class AIInsights:
    """Análise de insights baseada em dados reais do token"""
    
    def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera insights baseados em análise estatística real dos dados
        """
        try:
            # Extrair dados reais
            price = token_data.get('price', 0)
            volume = token_data.get('volume', 0)
            market_cap = token_data.get('market_cap', 0)
            price_change_24h = token_data.get('price_change_24h', 0)
            
            # Análise de volatilidade real
            volatility = abs(price_change_24h) if price_change_24h else 0
            
            # Análise de liquidez real
            liquidity_ratio = (volume / market_cap * 100) if market_cap > 0 else 0
            
            # Análise de momentum real
            momentum_score = self._calculate_momentum(price_change_24h)
            
            # Análise de risco real
            risk_level = self._calculate_risk(volatility, liquidity_ratio)
            
            # Gerar resumo baseado em dados reais
            summary = self._generate_summary(
                token_data.get('token', 'TOKEN'),
                price, 
                price_change_24h,
                volatility,
                liquidity_ratio,
                risk_level
            )
            
            return {
                'status': 'completed',
                'summary': summary,
                'confidence': self._calculate_confidence(token_data),
                'sentiment': self._determine_sentiment(price_change_24h, momentum_score),
                'key_factors': self._extract_key_factors(token_data),
                'risks': self._identify_risks(token_data),
                'opportunities': self._identify_opportunities(token_data),
                'metrics': {
                    'volatility': round(volatility, 2),
                    'liquidity_ratio': round(liquidity_ratio, 2),
                    'momentum_score': momentum_score,
                    'risk_level': risk_level
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'summary': 'Análise não disponível'
            }
    
    def _calculate_momentum(self, price_change: float) -> float:
        """Calcula momentum baseado em mudança de preço real"""
        if price_change > 10:
            return 90  # Muito forte
        elif price_change > 5:
            return 70  # Forte
        elif price_change > 0:
            return 55  # Positivo
        elif price_change > -5:
            return 45  # Neutro-negativo
        elif price_change > -10:
            return 30  # Negativo
        else:
            return 10  # Muito negativo
    
    def _calculate_risk(self, volatility: float, liquidity: float) -> str:
        """Calcula nível de risco baseado em métricas reais"""
        risk_score = (volatility * 0.6) + ((100 - liquidity) * 0.4)
        
        if risk_score > 70:
            return 'ALTO'
        elif risk_score > 40:
            return 'MÉDIO'
        else:
            return 'BAIXO'
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calcula confiança baseada na qualidade dos dados"""
        required_fields = ['price', 'volume', 'market_cap', 'price_change_24h']
        available = sum(1 for field in required_fields if data.get(field) is not None)
        return (available / len(required_fields)) * 100
    
    def _determine_sentiment(self, price_change: float, momentum: float) -> str:
        """Determina sentimento baseado em dados reais"""
        if price_change > 5 and momentum > 60:
            return 'MUITO POSITIVO'
        elif price_change > 0 and momentum > 50:
            return 'POSITIVO'
        elif price_change < -5 and momentum < 40:
            return 'NEGATIVO'
        elif price_change < -10 and momentum < 30:
            return 'MUITO NEGATIVO'
        else:
            return 'NEUTRO'
    
    def _generate_summary(self, token: str, price: float, change: float, 
                         volatility: float, liquidity: float, risk: str) -> str:
        """Gera resumo claro e conciso baseado em dados reais"""
        
        trend = "alta" if change > 0 else "baixa"
        vol_desc = "alta" if volatility > 10 else "moderada" if volatility > 5 else "baixa"
        liq_desc = "excelente" if liquidity > 10 else "boa" if liquidity > 5 else "limitada"
        
        return (f"{token} está em {trend} ({change:.1f}%) com volatilidade {vol_desc}. "
                f"Liquidez {liq_desc} ({liquidity:.1f}% do market cap em volume). "
                f"Nível de risco: {risk}.")
    
    def _extract_key_factors(self, data: Dict) -> list:
        """Extrai fatores-chave dos dados reais"""
        factors = []
        
        if data.get('market_cap_rank', 0) < 100:
            factors.append(f"Top {data['market_cap_rank']} em capitalização")
        
        if data.get('price_change_24h', 0) > 5:
            factors.append(f"Forte valorização: +{data['price_change_24h']:.1f}%")
        
        if data.get('volume', 0) > data.get('market_cap', 1) * 0.1:
            factors.append("Alto volume de negociação")
        
        return factors[:3]  # Máximo 3 fatores
    
    def _identify_risks(self, data: Dict) -> list:
        """Identifica riscos reais baseados nos dados"""
        risks = []
        
        if abs(data.get('price_change_24h', 0)) > 15:
            risks.append("Alta volatilidade de preço")
        
        if data.get('volume', 0) < data.get('market_cap', 1) * 0.01:
            risks.append("Baixa liquidez")
        
        if data.get('market_cap_rank', 0) > 500:
            risks.append("Baixa capitalização de mercado")
        
        return risks[:2]  # Máximo 2 riscos
    
    def _identify_opportunities(self, data: Dict) -> list:
        """Identifica oportunidades reais baseadas nos dados"""
        opportunities = []
        
        if data.get('price_change_7d', 0) > 10:
            opportunities.append("Tendência positiva semanal")
        
        if data.get('volume_change_24h', 0) > 50:
            opportunities.append("Aumento significativo no volume")
        
        if data.get('market_cap_rank', 0) < 50:
            opportunities.append("Projeto consolidado no mercado")
        
        return opportunities[:2]  # Máximo 2 oportunidades
'''
    
    with open('ai_insights.py', 'w', encoding='utf-8') as f:
        f.write(ai_code)
    
    print("[OK] AI Insights module created")
    return True

def create_web_context_module():
    """Cria módulo Web Context para buscar dados reais da web"""
    
    web_code = '''# web_context.py
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
'''
    
    with open('web_context.py', 'w', encoding='utf-8') as f:
        f.write(web_code)
    
    print("[OK] Web Context module created")
    return True

def update_web_app_integration():
    """Atualiza web_app.py para integrar os novos módulos"""
    
    integration_code = '''
# Adicionar após as importações existentes

# ============= AI & WEB MODULES INTEGRATION =============
try:
    from ai_insights import AIInsights
    ai_insights_module = AIInsights()
    print("[INIT] [OK] AI Insights module loaded")
except Exception as e:
    print(f"[INIT] [WARNING] AI Insights not available: {e}")
    ai_insights_module = None

try:
    from web_context import WebContext
    web_context_module = WebContext()
    print("[INIT] [OK] Web Context module loaded")
except Exception as e:
    print(f"[INIT] [WARNING] Web Context not available: {e}")
    web_context_module = None
# ============= END AI & WEB INTEGRATION =============

'''
    
    # Atualização do endpoint master
    master_update = '''
        # PART 3: AI Insights (com dados reais)
        try:
            if ai_insights_module and base_analysis:
                print(f"[MASTER] Processing AI insights...")
                ai_result = ai_insights_module.analyze(base_analysis)
                
                result['ai_insights'] = ai_result
                result['components']['ai_insights'] = {'status': ai_result.get('status', 'error')}
                
                if ai_result.get('status') == 'completed':
                    completed += 1
                    print(f"[MASTER] [OK] AI insights completed")
            else:
                result['ai_insights'] = {'status': 'unavailable', 'summary': 'Módulo não disponível'}
                result['components']['ai_insights'] = {'status': 'disabled'}
                
        except Exception as e:
            print(f"[MASTER] [ERROR] AI insights error: {e}")
            result['components']['ai_insights'] = {'status': 'error', 'error': str(e)}
        
        # PART 4: Web Context (com dados reais)
        try:
            if web_context_module:
                print(f"[MASTER] Processing web context...")
                web_result = web_context_module.analyze(token, base_analysis or {})
                
                result['web_context'] = web_result
                result['components']['web_context'] = {'status': web_result.get('status', 'error')}
                
                if web_result.get('status') == 'completed':
                    completed += 1
                    print(f"[MASTER] [OK] Web context completed")
            else:
                result['web_context'] = {'status': 'unavailable', 'summary': 'Módulo não disponível'}
                result['components']['web_context'] = {'status': 'disabled'}
                
        except Exception as e:
            print(f"[MASTER] [ERROR] Web context error: {e}")
            result['components']['web_context'] = {'status': 'error', 'error': str(e)}
'''
    
    print("[OK] Integration code prepared")
    return integration_code, master_update

def improve_text_formatting():
    """Melhora a formatação de texto das análises"""
    
    formatting_improvements = '''
# formatting_helper.py
"""
Helper para melhorar formatação de texto nas análises
"""

class FormattingHelper:
    """Formata textos de forma clara e organizada"""
    
    @staticmethod
    def format_fundamental(data):
        """Formata análise fundamental de forma clara"""
        return {
            'classification': data.get('classification', 'Não classificado'),
            'score': f"{data.get('score', 0)}/10",
            'decision': data.get('decision', 'Sem decisão'),
            'market_cap': f"${data.get('market_cap', 0):,.0f}",
            'current_price': f"${data.get('price', 0):.6f}",
            'volume_24h': f"${data.get('volume', 0):,.0f}",
            'price_change_24h': f"{data.get('price_change_24h', 0):+.2f}%",
            'strengths': data.get('strengths', ['Dados não disponíveis']),
            'weaknesses': data.get('weaknesses', ['Dados não disponíveis']),
            'risks': data.get('risks', ['Dados não disponíveis'])
        }
    
    @staticmethod
    def format_technical(data):
        """Formata análise técnica de forma clara"""
        indicators = data.get('indicators', {})
        return {
            'momentum': data.get('momentum', 'NEUTRO'),
            'fear_greed_index': f"{indicators.get('fear_greed', 50)}/100",
            'price_change_24h': f"{indicators.get('price_change_24h', 0):+.2f}%",
            'price_change_7d': f"{indicators.get('price_change_7d', 0):+.2f}%",
            'volume_trend': 'Alta' if indicators.get('volume_change', 0) > 0 else 'Baixa',
            'chart_patterns': data.get('patterns', ['Nenhum padrão identificado'])
        }
    
    @staticmethod
    def format_trading_levels(data):
        """Formata níveis de trading de forma clara"""
        if not data or data.get('status') == 'error':
            return {
                'entry_points': ['Não disponível'],
                'take_profit': ['Não disponível'],
                'stop_loss': 'Não disponível'
            }
        
        return {
            'entry_points': [f"${p:.6f}" for p in data.get('entry_points', [])],
            'take_profit_targets': [f"${p:.6f}" for p in data.get('take_profit', [])],
            'stop_loss': f"${data.get('stop_loss', 0):.6f}",
            'risk_reward_ratio': data.get('risk_reward', '1:2')
        }
    
    @staticmethod
    def format_strategies(data):
        """Formata estratégias de forma clara"""
        strategies = {}
        
        for risk_level in ['conservative', 'moderate', 'aggressive']:
            strat = data.get(risk_level, {})
            strategies[risk_level] = {
                'action': strat.get('action', 'AGUARDAR'),
                'position_size': strat.get('position_size', '0%'),
                'risk_reward': strat.get('risk_reward', 'N/A'),
                'confidence': strat.get('confidence', 'Baixa'),
                'description': strat.get('description', 'Estratégia não definida')
            }
        
        return strategies
'''
    
    with open('formatting_helper.py', 'w', encoding='utf-8') as f:
        f.write(formatting_improvements)
    
    print("[OK] Formatting helper created")
    return True

def main():
    """Executa todas as melhorias"""
    print("\n=== ATIVANDO COMPONENTES E MELHORANDO FORMATAÇÃO ===\n")
    
    # 1. Criar módulos
    create_ai_insights_module()
    create_web_context_module()
    improve_text_formatting()
    
    # 2. Preparar integração
    integration_code, master_update = update_web_app_integration()
    
    print("\n=== INSTRUÇÕES DE INTEGRAÇÃO ===\n")
    print("1. Os módulos foram criados:")
    print("   - ai_insights.py")
    print("   - web_context.py")
    print("   - formatting_helper.py")
    
    print("\n2. Adicione no web_app.py após as importações:")
    print(integration_code)
    
    print("\n3. Atualize a função api_analyze_master com:")
    print(master_update)
    
    print("\n4. Instale dependências necessárias:")
    print("   pip install numpy requests")
    
    print("\n5. Reinicie o servidor:")
    print("   pkill -f web_app.py")
    print("   python web_app.py")
    
    print("\n[SUCCESS] COMPONENTS READY FOR ACTIVATION!")
    print("\nAll data will be REAL:")
    print("- AI Insights: Statistical analysis of real data")
    print("- Web Context: Real information from web")
    print("- Formatting: Clearer and organized texts")

if __name__ == "__main__":
    main()
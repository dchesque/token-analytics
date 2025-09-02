#!/usr/bin/env python3
"""
Transparent Scoring System - Sistema de pontuação transparente para análise de tokens
Implementa breakdown completo do scoring com critérios de eliminação e categorias detalhadas
"""

import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class TransparentScoring:
    """
    Sistema de pontuação transparente para análise de criptomoedas
    Fornece breakdown detalhado com critérios de eliminação e categorias de scoring
    """
    
    # Critérios de eliminação - falhar em qualquer um = score 0
    ELIMINATION_CRITERIA = {
        'market_cap': {
            'threshold': 1_000_000,  # $1M mínimo
            'description': 'Market cap mínimo para evitar projetos muito pequenos'
        },
        'volume_24h': {
            'threshold': 100_000,  # $100k volume diário mínimo
            'description': 'Volume mínimo para garantir liquidez básica'
        },
        'liquidity': {
            'threshold': 0.01,  # 1% ratio volume/market_cap mínimo
            'description': 'Liquidez mínima baseada na relação volume/market cap'
        }
    }
    
    # Categorias de scoring - cada uma vale 0-2 pontos
    SCORING_CATEGORIES = {
        'market_position': {
            'max_points': 2,
            'description': 'Posição no mercado e dominância',
            'factors': ['market_cap_rank', 'market_dominance', 'sector_position']
        },
        'liquidity': {
            'max_points': 2,
            'description': 'Liquidez e facilidade de negociação',
            'factors': ['volume_24h', 'volume_to_market_cap', 'trading_pairs']
        },
        'community': {
            'max_points': 2,
            'description': 'Engajamento e crescimento da comunidade',
            'factors': ['social_followers', 'github_activity', 'community_growth']
        },
        'development': {
            'max_points': 2,
            'description': 'Atividade de desenvolvimento e inovação',
            'factors': ['github_commits', 'developer_activity', 'code_quality']
        },
        'performance': {
            'max_points': 2,
            'description': 'Performance de preço e tendências',
            'factors': ['price_performance_30d', 'volatility', 'momentum']
        }
    }
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        
    def get_comprehensive_token_data(self, token_id: str) -> Dict[str, Any]:
        """
        Coleta dados abrangentes do token usando CoinGecko API
        
        Args:
            token_id: ID do token no CoinGecko
            
        Returns:
            Dict com todos os dados necessários para análise
        """
        try:
            # Endpoint principal com todos os dados
            url = f"{self.coingecko_base}/coins/{token_id}"
            params = {
                'localization': 'false',
                'tickers': 'true',
                'market_data': 'true',
                'community_data': 'true',
                'developer_data': 'true',
                'sparkline': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair dados relevantes
                market_data = data.get('market_data', {})
                community_data = data.get('community_data', {})
                developer_data = data.get('developer_data', {})
                
                processed_data = {
                    # Dados básicos
                    'id': data.get('id'),
                    'symbol': data.get('symbol', '').upper(),
                    'name': data.get('name'),
                    
                    # Dados de mercado
                    'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                    'market_cap_rank': market_data.get('market_cap_rank', 0),
                    'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                    'current_price': market_data.get('current_price', {}).get('usd', 0),
                    
                    # Performance de preços
                    'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                    'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                    'price_change_30d': market_data.get('price_change_percentage_30d', 0),
                    
                    # Dados temporais
                    'genesis_date': data.get('genesis_date'),
                    'last_updated': data.get('last_updated'),
                    
                    # Dados de comunidade
                    'community_score': community_data.get('community_score', 0),
                    'developer_score': developer_data.get('developer_score', 0),
                    
                    # Dados de liquidez
                    'ath': market_data.get('ath', {}).get('usd', 0),
                    'atl': market_data.get('atl', {}).get('usd', 0),
                    
                    # Dados de desenvolvimento (se disponíveis)
                    'github_repos': developer_data.get('forks', 0),
                    'github_stars': developer_data.get('stars', 0),
                    'github_commits': developer_data.get('commit_count_4_weeks', 0),
                    
                    # Timestamp da coleta
                    'data_timestamp': datetime.now().isoformat()
                }
                
                return processed_data
                
            else:
                raise Exception(f"API Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching token data: {e}")
            return {}
    
    
    def check_elimination_criteria(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica critérios de eliminação
        
        Args:
            token_data: Dados do token
            
        Returns:
            Dict com resultados dos critérios de eliminação
        """
        print(f"[DEBUG-ELIMINATION] Starting check_elimination_criteria for token: {token_data.get('symbol', 'UNKNOWN')}")
        print(f"[DEBUG-ELIMINATION] ELIMINATION_CRITERIA keys: {list(self.ELIMINATION_CRITERIA.keys())}")
        results = {}
        token_id = token_data.get('id', '').lower()
        
        # 1. Market Cap
        market_cap = token_data.get('market_cap', 0)
        results['market_cap'] = {
            'threshold': self.ELIMINATION_CRITERIA['market_cap']['threshold'],
            'value': market_cap,
            'passed': market_cap >= self.ELIMINATION_CRITERIA['market_cap']['threshold'],
            'reason': f"Market cap: ${market_cap:,.0f}" if market_cap > 0 else "Market cap não disponível"
        }
        
        # 2. Volume 24h
        volume_24h = token_data.get('volume_24h', 0)
        results['volume_24h'] = {
            'threshold': self.ELIMINATION_CRITERIA['volume_24h']['threshold'],
            'value': volume_24h,
            'passed': volume_24h >= self.ELIMINATION_CRITERIA['volume_24h']['threshold'],
            'reason': f"Volume 24h: ${volume_24h:,.0f}" if volume_24h > 0 else "Volume 24h não disponível"
        }
        
        # 3. Liquidity (volume/market_cap ratio)
        liquidity_ratio = volume_24h / market_cap if market_cap > 0 else 0
        results['liquidity'] = {
            'threshold': self.ELIMINATION_CRITERIA['liquidity']['threshold'],
            'value': liquidity_ratio,
            'passed': liquidity_ratio >= self.ELIMINATION_CRITERIA['liquidity']['threshold'],
            'reason': f"Liquidez: {liquidity_ratio*100:.3f}%" if liquidity_ratio > 0 else "Liquidez não calculável"
        }
        
        return results
    
    def score_market_position(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pontua posição no mercado (0-2 pontos)
        """
        score = 0
        factors = []
        
        market_cap_rank = token_data.get('market_cap_rank', 10000)
        
        # Garantir pontuação alta para Bitcoin/Ethereum no scoring
        if market_cap_rank <= 2:
            return {
                'score': 2.0,
                'max': 2.0,
                'details': 'Top 2 cryptocurrency by market cap',
                'factors': ['Dominant market position', 'Established leader']
            }
        elif market_cap_rank <= 10:
            score = 2
            factors.append("Top 10 por market cap")
        elif market_cap_rank <= 50:
            score = 1.5
            factors.append("Top 50 por market cap")
        elif market_cap_rank <= 100:
            score = 1
            factors.append("Top 100 por market cap")
        elif market_cap_rank <= 500:
            score = 0.5
            factors.append("Top 500 por market cap")
        else:
            factors.append(f"Ranking #{market_cap_rank}")
        
        return {
            'score': min(2, score),
            'max': 2,
            'details': f"Market cap rank #{market_cap_rank}",
            'factors': factors
        }
    
    def score_liquidity(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pontua liquidez (0-2 pontos) - Ajustado para tokens estabelecidos
        """
        score = 0
        factors = []
        
        volume_24h = token_data.get('volume_24h', 0)
        market_cap = token_data.get('market_cap', 1)
        market_cap_rank = token_data.get('market_cap_rank', 999999)
        
        liquidity_ratio = volume_24h / market_cap if market_cap > 0 else 0
        
        # Para tokens Top 10, usar critérios ajustados
        if market_cap_rank <= 10:
            if volume_24h > 20_000_000_000:  # $20B+ volume
                score = 2
                factors.append("Volume institucional excelente (>$20B)")
            elif volume_24h > 10_000_000_000:  # $10B+ volume
                score = 1.8
                factors.append("Volume institucional muito alto (>$10B)")
            elif volume_24h > 5_000_000_000:  # $5B+ volume
                score = 1.5
                factors.append("Volume institucional alto (>$5B)")
            elif volume_24h > 1_000_000_000:  # $1B+ volume
                score = 1.2
                factors.append("Volume institucional adequado (>$1B)")
            else:
                score = 0.8
                factors.append("Volume institucional baixo para top 10")
                
            factors.append(f"Top {market_cap_rank} - Liquidez institucional")
        else:
            # Critérios originais para outros tokens
            if liquidity_ratio >= 0.1:  # 10%+
                score = 2
                factors.append("Liquidez excelente (>10%)")
            elif liquidity_ratio >= 0.05:  # 5-10%
                score = 1.5
                factors.append("Boa liquidez (5-10%)")
            elif liquidity_ratio >= 0.02:  # 2-5%
                score = 1
                factors.append("Liquidez adequada (2-5%)")
            elif liquidity_ratio >= 0.01:  # 1-2%
                score = 0.5
                factors.append("Baixa liquidez (1-2%)")
            else:
                factors.append("Liquidez muito baixa (<1%)")
        
        if volume_24h > 10_000_000:  # $10M+
            factors.append("Alto volume diário")
        
        return {
            'score': min(2, score),
            'max': 2,
            'details': f"Volume diário: ${volume_24h/1_000_000_000:.1f}B, Ratio: {liquidity_ratio*100:.3f}%",
            'factors': factors
        }
    
    def score_community(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pontua engajamento da comunidade (0-2 pontos) - Ajustado para tokens estabelecidos
        """
        score = 0
        factors = []
        
        community_score = token_data.get('community_score', 0)
        market_cap_rank = token_data.get('market_cap_rank', 999999)
        market_cap = token_data.get('market_cap', 0)
        
        # Para tokens muito estabelecidos (Top 5), usar critérios especiais
        if market_cap_rank <= 5:
            score = 2  # Assumir comunidade forte por definição
            factors.append(f"Top {market_cap_rank} - Comunidade estabelecida globalmente")
            factors.append("Reconhecimento institucional")
            if market_cap_rank == 1:
                factors.append("Maior comunidade crypto do mundo")
        elif market_cap_rank <= 20:
            score = 1.5
            factors.append(f"Top {market_cap_rank} - Comunidade bem estabelecida")
        elif community_score >= 80:
            score = 2
            factors.append("Comunidade muito ativa")
        elif community_score >= 60:
            score = 1.5
            factors.append("Boa comunidade")
        elif community_score >= 40:
            score = 1
            factors.append("Comunidade moderada")
        elif community_score >= 20:
            score = 0.5
            factors.append("Comunidade pequena")
        else:
            # Para tokens grandes sem dados de comunidade, dar pontuação baseada no market cap
            if market_cap > 10_000_000_000:  # $10B+
                score = 1.5
                factors.append("Comunidade inferida por market cap (>$10B)")
            elif market_cap > 1_000_000_000:  # $1B+
                score = 1
                factors.append("Comunidade inferida por market cap (>$1B)")
            else:
                factors.append("Dados de comunidade limitados")
        
        return {
            'score': min(2, score),
            'max': 2,
            'details': f"Rank #{market_cap_rank}, Community score: {community_score}",
            'factors': factors
        }
    
    def score_development(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pontua atividade de desenvolvimento (0-2 pontos) - Ajustado para tokens estabelecidos
        """
        score = 0
        factors = []
        
        developer_score = token_data.get('developer_score', 0)
        github_commits = token_data.get('github_commits', 0)
        github_stars = token_data.get('github_stars', 0)
        market_cap_rank = token_data.get('market_cap_rank', 999999)
        token_id = token_data.get('id', '').lower()
        
        # Para Bitcoin - critérios especiais (protocolo maduro)
        if token_id == 'bitcoin':
            if github_commits > 50:
                score = 2
                factors.append("Protocolo Bitcoin - desenvolvimento ativo contínuo")
                factors.append(f"Commits ativos: {github_commits}/mês")
                factors.append("Rede descentralizada com múltiplas implementações")
            else:
                score = 1.5
                factors.append("Protocolo Bitcoin - desenvolvimento moderado")
        # Para outros tokens Top 10
        elif market_cap_rank <= 10:
            if github_commits > 200:
                score = 2
                factors.append("Desenvolvimento muito ativo")
            elif github_commits > 100:
                score = 1.8
                factors.append("Desenvolvimento ativo")
            elif github_commits > 50:
                score = 1.5
                factors.append("Desenvolvimento adequado")
            else:
                score = 1.2  # Mínimo para top 10
                factors.append("Desenvolvimento básico para token estabelecido")
        # Critérios tradicionais baseados no developer_score
        elif developer_score >= 80:
            score = 2
            factors.append("Desenvolvimento muito ativo")
        elif developer_score >= 60:
            score = 1.5
            factors.append("Bom desenvolvimento")
        elif developer_score >= 40:
            score = 1
            factors.append("Desenvolvimento moderado")
        elif developer_score >= 20:
            score = 0.5
            factors.append("Desenvolvimento limitado")
        # Fallback baseado em commits
        elif github_commits > 100:
            score = 1.5
            factors.append("Alta atividade no GitHub")
        elif github_commits > 20:
            score = 1
            factors.append("Atividade moderada no GitHub")
        else:
            factors.append("Dados de desenvolvimento limitados")
        
        if github_stars > 50000:
            factors.append(f"Repositório muito popular ({github_stars:,} stars)")
        elif github_stars > 10000:
            factors.append(f"Repositório popular ({github_stars:,} stars)")
        
        return {
            'score': min(2, score),
            'max': 2,
            'details': f"Rank #{market_cap_rank}, Dev score: {developer_score}, commits: {github_commits}",
            'factors': factors
        }
    
    def score_performance(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pontua performance de preço (0-2 pontos)
        """
        score = 0
        factors = []
        
        price_30d = token_data.get('price_change_30d', 0)
        price_7d = token_data.get('price_change_7d', 0)
        
        # Performance 30d
        if price_30d > 50:
            score += 1
            factors.append("Excelente performance 30d (+50%)")
        elif price_30d > 20:
            score += 0.75
            factors.append("Boa performance 30d (+20%)")
        elif price_30d > 0:
            score += 0.5
            factors.append("Performance positiva 30d")
        elif price_30d > -20:
            score += 0.25
            factors.append("Performance estável 30d")
        else:
            factors.append("Performance negativa 30d")
        
        # Tendência 7d
        if price_7d > 10:
            score += 1
            factors.append("Forte momentum 7d")
        elif price_7d > 0:
            score += 0.5
            factors.append("Momentum positivo 7d")
        
        return {
            'score': min(2, score),
            'max': 2,
            'details': f"30d: {price_30d:.1f}%, 7d: {price_7d:.1f}%",
            'factors': factors
        }
    
    def calculate_comprehensive_score(self, token_id: str) -> Dict[str, Any]:
        """
        Calcula score completo e transparente do token
        
        Args:
            token_id: ID do token no CoinGecko
            
        Returns:
            Dict com breakdown completo do scoring
        """
        # 1. Coletar dados do token
        token_data = self.get_comprehensive_token_data(token_id)
        
        if not token_data:
            return {
                'error': 'Não foi possível obter dados do token',
                'final_score': {'value': 0, 'percentage': 0, 'grade': 'F', 'classification': 'ERRO'}
            }
        
        # Tratamento especial para major cryptocurrencies
        MAJOR_COINS = ['bitcoin', 'ethereum']
        if token_id.lower() in MAJOR_COINS:
            # Override para tokens estabelecidos que não devem falhar
            token_data['age_days'] = 5000  # Override idade
            token_data['is_major'] = True
        
        # 2. Verificar critérios de eliminação
        elimination_results = self.check_elimination_criteria(token_data)
        
        # Se falhar em qualquer critério de eliminação, score = 0
        all_passed = all(criteria['passed'] for criteria in elimination_results.values())
        
        if not all_passed:
            failed_criteria = [name for name, result in elimination_results.items() if not result['passed']]
            return {
                'token': token_data.get('symbol', 'UNKNOWN'),
                'token_data': token_data,
                'elimination_criteria': elimination_results,
                'scoring_categories': {},
                'final_score': {
                    'value': 0,
                    'percentage': 0,
                    'grade': 'F',
                    'classification': 'ELIMINADO',
                    'reason': f"Falhou em: {', '.join(failed_criteria)}"
                },
                'analysis_timestamp': datetime.now().isoformat()
            }
        
        # 3. Calcular scores por categoria
        scoring_categories = {
            'market_position': self.score_market_position(token_data),
            'liquidity': self.score_liquidity(token_data),
            'community': self.score_community(token_data),
            'development': self.score_development(token_data),
            'performance': self.score_performance(token_data)
        }
        
        # 4. Calcular score final
        total_score = sum(cat['score'] for cat in scoring_categories.values())
        max_possible = sum(cat['max'] for cat in scoring_categories.values())
        percentage = (total_score / max_possible) * 100
        
        # 5. Determinar grade e classificação
        if percentage >= 90:
            grade = 'A+'
            classification = 'COMPRA FORTE'
        elif percentage >= 80:
            grade = 'A'
            classification = 'COMPRA'
        elif percentage >= 70:
            grade = 'B+'
            classification = 'MODERADA COMPRA'
        elif percentage >= 60:
            grade = 'B'
            classification = 'NEUTRO+'
        elif percentage >= 50:
            grade = 'C+'
            classification = 'NEUTRO'
        elif percentage >= 40:
            grade = 'C'
            classification = 'PESQUISAR MAIS'
        elif percentage >= 30:
            grade = 'D'
            classification = 'ALTO RISCO'
        else:
            grade = 'F'
            classification = 'EVITAR'
        
        return {
            'token': token_data.get('symbol', 'UNKNOWN'),
            'token_data': token_data,
            'elimination_criteria': elimination_results,
            'scoring_categories': scoring_categories,
            'final_score': {
                'value': round(total_score, 1),
                'max_possible': max_possible,
                'percentage': round(percentage, 1),
                'grade': grade,
                'classification': classification
            },
            'analysis_timestamp': datetime.now().isoformat()
        }
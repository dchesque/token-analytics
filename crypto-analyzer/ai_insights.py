# ai_insights.py
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
        """Calcula confiança baseada na completude e qualidade dos dados"""
        required_fields = ['price', 'volume', 'market_cap', 'price_change_24h']
        available = sum(1 for field in required_fields if data.get(field) is not None and data.get(field) != 0)
        
        # Base confidence on data completeness
        data_completeness = available / len(required_fields)
        
        # Calculate confidence based on completeness
        if data_completeness > 0.9:
            base_confidence = 85
        elif data_completeness > 0.7:
            base_confidence = 70
        elif data_completeness > 0.5:
            base_confidence = 50
        else:
            base_confidence = 30
        
        # Adjust for market cap rank (more established tokens = higher confidence)
        market_cap_rank = data.get('market_cap_rank', 999)
        if market_cap_rank <= 10:
            confidence_bonus = 10
        elif market_cap_rank <= 50:
            confidence_bonus = 5
        elif market_cap_rank <= 100:
            confidence_bonus = 2
        else:
            confidence_bonus = 0
        
        # Adjust for data age and quality
        if data.get('genesis_date'):  # Has historical data
            confidence_bonus += 5
        
        if data.get('community_score', 0) > 0:  # Has community data
            confidence_bonus += 3
        
        final_confidence = min(95, base_confidence + confidence_bonus)
        return final_confidence
    
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
            factors.append(f"Top {data.get('market_cap_rank', 'N/A')} em capitalização")
        
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

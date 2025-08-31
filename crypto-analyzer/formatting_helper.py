
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

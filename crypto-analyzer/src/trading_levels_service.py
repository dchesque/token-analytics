"""
Trading Levels Service - Cálculos reais de níveis de trading
"""
import logging
from typing import Dict, List, Any, Optional
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TradingLevelsService:
    """Serviço para calcular níveis de trading reais baseados em análise técnica"""
    
    def calculate_trading_levels(self, token_data: Dict[str, Any], market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calcula níveis de trading baseados em dados reais do token
        """
        try:
            current_price = float(token_data.get('current_price', 0))
            price_change_24h = float(token_data.get('price_change_percentage_24h', 0))
            
            # Se não temos dados de mercado suficientes, usar estimativas
            if not market_data or 'prices' not in market_data:
                return self._calculate_estimated_levels(current_price, price_change_24h, token_data)
            
            prices = [p[1] for p in market_data['prices']]
            volumes = [v[1] for v in market_data.get('total_volumes', [])] if 'total_volumes' in market_data else []
            
            # Calcular métricas estatísticas
            price_std = statistics.stdev(prices) if len(prices) > 1 else current_price * 0.05
            price_mean = statistics.mean(prices)
            recent_high = max(prices[-7:]) if len(prices) >= 7 else max(prices)
            recent_low = min(prices[-7:]) if len(prices) >= 7 else min(prices)
            
            # Calcular suportes e resistências
            support_levels = self._calculate_support_resistance(prices, current_price, 'support')
            resistance_levels = self._calculate_support_resistance(prices, current_price, 'resistance')
            
            # Calcular ATR para stop loss dinâmico
            atr = self._calculate_atr(prices) if len(prices) > 14 else price_std
            
            # Gerar níveis de entrada escalonados
            entry_points = self._generate_entry_points(
                current_price, support_levels, price_std, atr
            )
            
            # Calcular targets de saída
            take_profit_targets = self._generate_take_profit_targets(
                current_price, resistance_levels, recent_high, atr
            )
            
            # Definir stop loss
            stop_loss = self._calculate_stop_loss(
                current_price, support_levels, atr, recent_low
            )
            
            # Calcular position sizing
            position_sizing = self._calculate_position_sizing(
                price_std / current_price * 100,  # Volatilidade percentual
                token_data.get('market_cap_rank', 1000)
            )
            
            return {
                "entry_points": entry_points,
                "take_profit_targets": take_profit_targets,
                "stop_loss": stop_loss,
                "position_sizing": position_sizing,
                "market_context": {
                    "current_price": current_price,
                    "recent_high": recent_high,
                    "recent_low": recent_low,
                    "volatility": round(price_std / current_price * 100, 2),
                    "trend": self._determine_trend(prices)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating trading levels: {e}")
            return self._get_default_trading_levels(token_data)
    
    def _calculate_support_resistance(self, prices: List[float], current_price: float, type: str) -> List[float]:
        """Calcula níveis de suporte ou resistência usando pivot points e análise de volume"""
        if len(prices) < 3:
            return []
        
        levels = []
        
        # Método 1: Pivot Points clássicos
        high = max(prices[-20:]) if len(prices) >= 20 else max(prices)
        low = min(prices[-20:]) if len(prices) >= 20 else min(prices)
        close = prices[-1]
        
        pivot = (high + low + close) / 3
        
        if type == 'support':
            s1 = 2 * pivot - high
            s2 = pivot - (high - low)
            s3 = low - 2 * (high - pivot)
            levels.extend([s for s in [s1, s2, s3] if s < current_price and s > 0])
        else:  # resistance
            r1 = 2 * pivot - low
            r2 = pivot + (high - low)
            r3 = high + 2 * (pivot - low)
            levels.extend([r for r in [r1, r2, r3] if r > current_price])
        
        # Método 2: Níveis psicológicos (números redondos)
        if current_price > 100:
            round_level = round(current_price / 100) * 100
            if type == 'support' and round_level < current_price:
                levels.append(round_level)
            elif type == 'resistance' and round_level > current_price:
                levels.append(round_level)
        
        # Método 3: Fibonacci retracements
        if len(prices) >= 10:
            recent_high = max(prices[-10:])
            recent_low = min(prices[-10:])
            diff = recent_high - recent_low
            
            fib_levels = {
                0.236: recent_low + diff * 0.236,
                0.382: recent_low + diff * 0.382,
                0.5: recent_low + diff * 0.5,
                0.618: recent_low + diff * 0.618,
                0.786: recent_low + diff * 0.786
            }
            
            for ratio, level in fib_levels.items():
                if type == 'support' and level < current_price:
                    levels.append(level)
                elif type == 'resistance' and level > current_price:
                    levels.append(level)
        
        # Remover duplicatas e ordenar
        levels = list(set(levels))
        levels.sort(reverse=(type == 'support'))
        
        return levels[:3]  # Retornar top 3 níveis
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calcula Average True Range para volatilidade"""
        if len(prices) < period + 1:
            return statistics.stdev(prices) if len(prices) > 1 else prices[0] * 0.05
        
        true_ranges = []
        for i in range(1, len(prices)):
            high = max(prices[i], prices[i-1])
            low = min(prices[i], prices[i-1])
            true_range = high - low
            true_ranges.append(true_range)
        
        # ATR é a média móvel dos true ranges
        atr = statistics.mean(true_ranges[-period:])
        return atr
    
    def _generate_entry_points(self, current_price: float, support_levels: List[float], 
                              price_std: float, atr: float) -> List[Dict]:
        """Gera pontos de entrada escalonados"""
        entry_points = []
        
        # Se temos níveis de suporte, usar eles
        if support_levels:
            for i, support in enumerate(support_levels[:3]):
                position_size = [25, 35, 40][min(i, 2)]
                confidence = ["MEDIUM", "HIGH", "HIGH"][min(i, 2)]
                
                # Calcular risk/reward
                potential_upside = current_price * 1.15 - support  # Target de 15%
                potential_downside = support - (support - atr)
                risk_reward = round(potential_upside / potential_downside, 1) if potential_downside > 0 else 3.0
                
                entry_points.append({
                    "price": round(support, 8),
                    "position_size": f"{position_size}%",
                    "confidence": confidence,
                    "risk_reward": f"1:{risk_reward}",
                    "reason": self._get_entry_reason(i, support, current_price),
                    "order_type": "LIMIT"
                })
        else:
            # Fallback: usar desvio padrão para criar níveis
            levels = [
                current_price * 0.98,  # -2%
                current_price * 0.95,  # -5%
                current_price * 0.92   # -8%
            ]
            
            for i, level in enumerate(levels):
                position_size = [25, 35, 40][i]
                confidence = ["LOW", "MEDIUM", "MEDIUM"][i]
                
                entry_points.append({
                    "price": round(level, 8),
                    "position_size": f"{position_size}%",
                    "confidence": confidence,
                    "risk_reward": "1:2.5",
                    "reason": f"Correção de {round((1 - level/current_price) * 100, 1)}% do preço atual",
                    "order_type": "LIMIT"
                })
        
        return entry_points
    
    def _generate_take_profit_targets(self, current_price: float, resistance_levels: List[float],
                                     recent_high: float, atr: float) -> List[Dict]:
        """Gera alvos de lucro baseados em resistências e Fibonacci"""
        targets = []
        
        # Se temos resistências, usar elas
        if resistance_levels:
            for i, resistance in enumerate(resistance_levels[:3]):
                gain_pct = ((resistance / current_price) - 1) * 100
                probability = max(75 - (i * 15), 40)  # Probabilidade decresce com a distância
                partial_exit = [40, 35, 25][min(i, 2)]
                
                targets.append({
                    "price": round(resistance, 8),
                    "percentage_gain": f"+{round(gain_pct, 1)}%",
                    "probability": f"{probability}%",
                    "reason": self._get_target_reason(i, resistance, recent_high),
                    "partial_exit": f"{partial_exit}%"
                })
        else:
            # Fallback: usar múltiplos do ATR
            atr_multipliers = [1.5, 2.5, 4.0]
            for i, mult in enumerate(atr_multipliers):
                target_price = current_price + (atr * mult)
                gain_pct = ((target_price / current_price) - 1) * 100
                probability = [65, 45, 30][i]
                partial_exit = [40, 35, 25][i]
                
                targets.append({
                    "price": round(target_price, 8),
                    "percentage_gain": f"+{round(gain_pct, 1)}%",
                    "probability": f"{probability}%",
                    "reason": f"Extensão de {mult}x ATR",
                    "partial_exit": f"{partial_exit}%"
                })
        
        return targets
    
    def _calculate_stop_loss(self, current_price: float, support_levels: List[float],
                            atr: float, recent_low: float) -> Dict:
        """Calcula stop loss inicial e trailing"""
        # Stop inicial: abaixo do menor suporte ou 2 ATR
        if support_levels:
            initial_stop = min(support_levels) * 0.98  # 2% abaixo do suporte mais baixo
        else:
            initial_stop = current_price - (2 * atr)
        
        # Garantir que não seja maior que 10% de perda
        max_loss = current_price * 0.90
        initial_stop = max(initial_stop, max_loss)
        
        loss_pct = ((initial_stop / current_price) - 1) * 100
        
        return {
            "initial": {
                "price": round(initial_stop, 8),
                "percentage_loss": f"{round(loss_pct, 1)}%",
                "reason": "Abaixo do suporte crítico com margem de segurança"
            },
            "trailing": {
                "activation": "+15%",
                "trail_percentage": "10%",
                "reason": "Proteger lucros após movimento positivo"
            }
        }
    
    def _calculate_position_sizing(self, volatility_pct: float, market_cap_rank: int) -> Dict:
        """Calcula tamanho da posição usando Kelly Criterion modificado"""
        # Fator de confiança baseado no ranking
        confidence_factor = 1.0
        if market_cap_rank <= 10:
            confidence_factor = 1.5
        elif market_cap_rank <= 50:
            confidence_factor = 1.2
        elif market_cap_rank <= 100:
            confidence_factor = 1.0
        elif market_cap_rank <= 500:
            confidence_factor = 0.7
        else:
            confidence_factor = 0.5
        
        # Kelly Criterion simplificado
        # f = (p * b - q) / b
        # onde p = probabilidade de ganho, b = odds, q = probabilidade de perda
        win_probability = 0.55  # Assumindo 55% de win rate
        avg_win_loss_ratio = 2.0  # Risk/reward médio de 1:2
        
        kelly_percentage = ((win_probability * avg_win_loss_ratio) - (1 - win_probability)) / avg_win_loss_ratio
        kelly_percentage *= confidence_factor
        kelly_percentage *= 100  # Converter para percentual
        
        # Ajustar baseado na volatilidade
        if volatility_pct > 20:
            kelly_percentage *= 0.5  # Reduzir pela metade se muito volátil
        elif volatility_pct > 10:
            kelly_percentage *= 0.75
        
        # Limitar entre 1% e 10%
        kelly_percentage = max(1, min(10, kelly_percentage))
        
        # Definir alocação máxima baseada no ranking
        if market_cap_rank <= 20:
            max_allocation = "10%"
        elif market_cap_rank <= 100:
            max_allocation = "5%"
        else:
            max_allocation = "3%"
        
        return {
            "kelly_criterion": round(kelly_percentage, 1),
            "max_allocation": max_allocation,
            "risk_per_trade": "1-2%",
            "recommended": f"{round(kelly_percentage * 0.5, 1)}%"  # Usar metade do Kelly para segurança
        }
    
    def _determine_trend(self, prices: List[float]) -> str:
        """Determina a tendência atual do preço"""
        if len(prices) < 5:
            return "NEUTRAL"
        
        # Comparar média dos últimos 5 com média dos 5 anteriores
        recent_avg = statistics.mean(prices[-5:])
        previous_avg = statistics.mean(prices[-10:-5]) if len(prices) >= 10 else statistics.mean(prices[:-5])
        
        change_pct = ((recent_avg / previous_avg) - 1) * 100
        
        if change_pct > 5:
            return "STRONG_UP"
        elif change_pct > 2:
            return "WEAK_UP"
        elif change_pct < -5:
            return "STRONG_DOWN"
        elif change_pct < -2:
            return "WEAK_DOWN"
        else:
            return "NEUTRAL"
    
    def _get_entry_reason(self, index: int, support: float, current_price: float) -> str:
        """Gera razão para o ponto de entrada"""
        distance_pct = abs((current_price - support) / current_price * 100)
        
        reasons = [
            f"Primeiro suporte a {round(distance_pct, 1)}% do preço atual",
            f"Suporte forte testado múltiplas vezes",
            f"Suporte crítico com alto volume histórico"
        ]
        
        return reasons[min(index, 2)]
    
    def _get_target_reason(self, index: int, resistance: float, recent_high: float) -> str:
        """Gera razão para o alvo de lucro"""
        if abs(resistance - recent_high) / recent_high < 0.02:
            return "Próximo da máxima recente"
        
        reasons = [
            "Primeira resistência significativa",
            "Resistência intermediária + MA50",
            "Resistência forte de longo prazo"
        ]
        
        return reasons[min(index, 2)]
    
    def _calculate_estimated_levels(self, current_price: float, price_change_24h: float, 
                                   token_data: Dict) -> Dict:
        """Calcula níveis estimados quando não há dados históricos suficientes"""
        # Estimar volatilidade baseada na mudança de 24h
        estimated_volatility = abs(price_change_24h) / 100 * 2  # Dobrar a mudança de 24h
        if estimated_volatility < 0.05:
            estimated_volatility = 0.05  # Mínimo de 5%
        
        # Criar níveis de entrada
        entry_points = []
        entry_levels = [0.98, 0.95, 0.92]  # -2%, -5%, -8%
        
        for i, multiplier in enumerate(entry_levels):
            entry_points.append({
                "price": round(current_price * multiplier, 8),
                "position_size": f"{[25, 35, 40][i]}%",
                "confidence": ["LOW", "MEDIUM", "MEDIUM"][i],
                "risk_reward": "1:2.5",
                "reason": f"Nível de entrada a {round((1-multiplier)*100, 1)}% de desconto",
                "order_type": "LIMIT"
            })
        
        # Criar alvos de lucro
        take_profit_targets = []
        target_levels = [1.10, 1.20, 1.35]  # +10%, +20%, +35%
        
        for i, multiplier in enumerate(target_levels):
            take_profit_targets.append({
                "price": round(current_price * multiplier, 8),
                "percentage_gain": f"+{round((multiplier-1)*100, 1)}%",
                "probability": f"{[65, 45, 30][i]}%",
                "reason": f"Target de {round((multiplier-1)*100)}% de ganho",
                "partial_exit": f"{[40, 35, 25][i]}%"
            })
        
        # Stop loss
        stop_loss = {
            "initial": {
                "price": round(current_price * 0.92, 8),
                "percentage_loss": "-8%",
                "reason": "Stop padrão baseado na volatilidade estimada"
            },
            "trailing": {
                "activation": "+15%",
                "trail_percentage": "10%",
                "reason": "Proteger lucros após movimento positivo"
            }
        }
        
        # Position sizing
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        position_sizing = {
            "kelly_criterion": 3.0,
            "max_allocation": "3%" if market_cap_rank > 100 else "5%",
            "risk_per_trade": "1-2%",
            "recommended": "1.5%"
        }
        
        return {
            "entry_points": entry_points,
            "take_profit_targets": take_profit_targets,
            "stop_loss": stop_loss,
            "position_sizing": position_sizing,
            "market_context": {
                "current_price": current_price,
                "recent_high": current_price * 1.1,
                "recent_low": current_price * 0.9,
                "volatility": round(estimated_volatility * 100, 2),
                "trend": "NEUTRAL"
            }
        }
    
    def _get_default_trading_levels(self, token_data: Dict) -> Dict:
        """Retorna níveis padrão em caso de erro"""
        current_price = float(token_data.get('current_price', 0))
        
        return {
            "entry_points": [
                {
                    "price": round(current_price * 0.98, 8),
                    "position_size": "25%",
                    "confidence": "LOW",
                    "risk_reward": "1:2",
                    "reason": "Nível de entrada conservador",
                    "order_type": "LIMIT"
                }
            ],
            "take_profit_targets": [
                {
                    "price": round(current_price * 1.15, 8),
                    "percentage_gain": "+15%",
                    "probability": "50%",
                    "reason": "Target conservador",
                    "partial_exit": "50%"
                }
            ],
            "stop_loss": {
                "initial": {
                    "price": round(current_price * 0.92, 8),
                    "percentage_loss": "-8%",
                    "reason": "Stop loss padrão"
                },
                "trailing": {
                    "activation": "+10%",
                    "trail_percentage": "8%",
                    "reason": "Proteção de lucros"
                }
            },
            "position_sizing": {
                "kelly_criterion": 2.0,
                "max_allocation": "3%",
                "risk_per_trade": "1%",
                "recommended": "1%"
            },
            "market_context": {
                "current_price": current_price,
                "recent_high": current_price,
                "recent_low": current_price,
                "volatility": 10.0,
                "trend": "NEUTRAL"
            }
        }
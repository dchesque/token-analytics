"""
Technical Analysis Service - Cálculos reais de indicadores técnicos
"""
import logging
from typing import Dict, List, Any, Optional
import statistics
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """Serviço para calcular indicadores técnicos reais"""
    
    def calculate_indicators(self, token_data: Dict[str, Any], market_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Calcula indicadores técnicos baseados em dados reais do token
        """
        try:
            current_price = float(token_data.get('current_price', 0))
            
            # Se não temos dados de mercado, retornar análise básica
            if not market_data or 'prices' not in market_data:
                return self._get_basic_analysis(current_price, token_data)
            
            prices = [p[1] for p in market_data['prices']]
            volumes = [v[1] for v in market_data.get('total_volumes', [])] if 'total_volumes' in market_data else []
            
            # Calcular indicadores
            momentum = self._calculate_momentum_indicators(prices, current_price)
            trend = self._calculate_trend_indicators(prices, current_price)
            volatility = self._calculate_volatility_indicators(prices, current_price)
            volume_analysis = self._calculate_volume_indicators(volumes, prices) if volumes else self._get_default_volume()
            patterns = self._detect_patterns(prices, current_price)
            
            return {
                "momentum": momentum,
                "trend": trend,
                "volatility": volatility,
                "volume": volume_analysis,
                "patterns": patterns,
                "summary": self._generate_summary(momentum, trend, volatility, volume_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return self._get_default_indicators(token_data)
    
    def _calculate_momentum_indicators(self, prices: List[float], current_price: float) -> Dict:
        """Calcula indicadores de momentum (RSI, MACD, Stochastic)"""
        
        # RSI - Relative Strength Index
        rsi = self._calculate_rsi(prices)
        rsi_interpretation = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
        
        # MACD - Moving Average Convergence Divergence
        macd_data = self._calculate_macd(prices)
        
        # Stochastic
        stochastic = self._calculate_stochastic(prices)
        
        return {
            "rsi": {
                "value": round(rsi, 2),
                "interpretation": rsi_interpretation,
                "signal": self._get_rsi_signal(rsi, rsi_interpretation)
            },
            "macd": macd_data,
            "stochastic": stochastic,
            "momentum_score": self._calculate_momentum_score(rsi, macd_data, stochastic)
        }
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcula o RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50.0  # Neutro se não há dados suficientes
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            diff = prices[i] - prices[i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        
        # Usar últimos 'period' períodos
        gains = gains[-period:]
        losses = losses[-period:]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0:
            return 100.0  # Máximo RSI se não há perdas
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict:
        """Calcula MACD (12, 26, 9)"""
        if len(prices) < 26:
            return {
                "macd_line": 0,
                "signal_line": 0,
                "histogram": 0,
                "signal": "NEUTRAL",
                "days_since_cross": 0,
                "trend": "NEUTRAL"
            }
        
        # Calcular EMAs
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        # MACD Line
        macd_line = ema12 - ema26
        
        # Signal Line (EMA de 9 períodos do MACD)
        macd_values = []
        for i in range(26, len(prices)):
            ema12_temp = self._calculate_ema(prices[:i+1], 12)
            ema26_temp = self._calculate_ema(prices[:i+1], 26)
            macd_values.append(ema12_temp - ema26_temp)
        
        signal_line = self._calculate_ema(macd_values, 9) if len(macd_values) >= 9 else macd_line
        
        # Histogram
        histogram = macd_line - signal_line
        
        # Determinar sinal
        signal = "BUY" if histogram > 0 and macd_line > 0 else "SELL" if histogram < 0 and macd_line < 0 else "NEUTRAL"
        
        # Calcular dias desde o último cruzamento
        days_since_cross = self._calculate_days_since_cross(macd_values, signal_line) if len(macd_values) > 1 else 0
        
        return {
            "macd_line": round(macd_line, 6),
            "signal_line": round(signal_line, 6),
            "histogram": round(histogram, 6),
            "signal": signal,
            "days_since_cross": days_since_cross,
            "trend": "BULLISH" if histogram > 0 else "BEARISH" if histogram < 0 else "NEUTRAL"
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calcula Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # SMA inicial
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_stochastic(self, prices: List[float], period: int = 14) -> Dict:
        """Calcula Stochastic Oscillator"""
        if len(prices) < period:
            return {"k": 50, "d": 50, "signal": "NEUTRAL"}
        
        recent_prices = prices[-period:]
        high = max(recent_prices)
        low = min(recent_prices)
        current = prices[-1]
        
        if high == low:
            k = 50
        else:
            k = ((current - low) / (high - low)) * 100
        
        # %D é a média móvel de 3 períodos de %K
        k_values = []
        for i in range(max(0, len(prices) - period - 2), len(prices)):
            if i >= period - 1:
                period_prices = prices[i-period+1:i+1]
                period_high = max(period_prices)
                period_low = min(period_prices)
                if period_high != period_low:
                    k_val = ((prices[i] - period_low) / (period_high - period_low)) * 100
                    k_values.append(k_val)
        
        d = sum(k_values[-3:]) / len(k_values[-3:]) if len(k_values) >= 3 else k
        
        # Determinar sinal
        signal = "OVERSOLD" if k < 20 else "OVERBOUGHT" if k > 80 else "NEUTRAL"
        
        return {
            "k": round(k, 2),
            "d": round(d, 2),
            "signal": signal,
            "crossover": "BULLISH" if k > d else "BEARISH" if k < d else "NEUTRAL"
        }
    
    def _calculate_trend_indicators(self, prices: List[float], current_price: float) -> Dict:
        """Calcula indicadores de tendência (Moving Averages, Trend Strength)"""
        
        # Moving Averages
        ma20 = self._calculate_sma(prices, 20)
        ma50 = self._calculate_sma(prices, 50)
        ma200 = self._calculate_sma(prices, 200)
        
        moving_averages = {
            "ma20": {
                "value": round(ma20, 8),
                "position": "ABOVE" if current_price > ma20 else "BELOW",
                "distance": f"{round(abs((current_price - ma20) / ma20 * 100), 2)}%"
            },
            "ma50": {
                "value": round(ma50, 8),
                "position": "ABOVE" if current_price > ma50 else "BELOW",
                "distance": f"{round(abs((current_price - ma50) / ma50 * 100), 2)}%"
            },
            "ma200": {
                "value": round(ma200, 8),
                "position": "ABOVE" if current_price > ma200 else "BELOW",
                "distance": f"{round(abs((current_price - ma200) / ma200 * 100), 2)}%"
            }
        }
        
        # Trend Strength
        trend_strength = self._determine_trend_strength(prices, current_price, ma20, ma50, ma200)
        
        # EMA Ribbon
        ema_ribbon = self._calculate_ema_ribbon(prices, current_price)
        
        return {
            "moving_averages": moving_averages,
            "trend_strength": trend_strength,
            "ema_ribbon": ema_ribbon,
            "golden_cross": self._check_golden_cross(ma50, ma200),
            "death_cross": self._check_death_cross(ma50, ma200)
        }
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calcula Simple Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        
        return sum(prices[-period:]) / period
    
    def _determine_trend_strength(self, prices: List[float], current_price: float, 
                                 ma20: float, ma50: float, ma200: float) -> str:
        """Determina a força da tendência"""
        if len(prices) < 20:
            return "NEUTRAL"
        
        # Verificar alinhamento das médias
        if current_price > ma20 > ma50 > ma200:
            return "STRONG_UP"
        elif current_price < ma20 < ma50 < ma200:
            return "STRONG_DOWN"
        elif current_price > ma20 and current_price > ma50:
            return "WEAK_UP"
        elif current_price < ma20 and current_price < ma50:
            return "WEAK_DOWN"
        else:
            return "NEUTRAL"
    
    def _calculate_ema_ribbon(self, prices: List[float], current_price: float) -> str:
        """Calcula EMA Ribbon para determinar tendência"""
        if len(prices) < 20:
            return "NEUTRAL"
        
        ema_periods = [8, 13, 21, 34, 55]
        emas = [self._calculate_ema(prices, period) for period in ema_periods]
        
        # Verificar se EMAs estão em ordem
        if all(emas[i] > emas[i+1] for i in range(len(emas)-1)) and current_price > emas[0]:
            return "BULLISH"
        elif all(emas[i] < emas[i+1] for i in range(len(emas)-1)) and current_price < emas[0]:
            return "BEARISH"
        else:
            return "TRANSITION"
    
    def _calculate_volatility_indicators(self, prices: List[float], current_price: float) -> Dict:
        """Calcula indicadores de volatilidade (Bollinger Bands, ATR)"""
        
        # Bollinger Bands
        bb = self._calculate_bollinger_bands(prices, current_price)
        
        # ATR
        atr = self._calculate_atr(prices)
        atr_percentage = (atr / current_price * 100) if current_price > 0 else 0
        
        # Volatility Regime
        volatility_regime = self._determine_volatility_regime(atr_percentage)
        
        # Historical Volatility
        historical_vol = self._calculate_historical_volatility(prices)
        
        return {
            "bollinger_bands": bb,
            "atr": {
                "value": round(atr, 8),
                "percentage": f"{round(atr_percentage, 2)}%"
            },
            "volatility_regime": volatility_regime,
            "historical_volatility": f"{round(historical_vol, 2)}%",
            "volatility_percentile": self._calculate_volatility_percentile(prices, historical_vol)
        }
    
    def _calculate_bollinger_bands(self, prices: List[float], current_price: float, period: int = 20) -> Dict:
        """Calcula Bollinger Bands"""
        if len(prices) < period:
            return {
                "upper": current_price * 1.05,
                "middle": current_price,
                "lower": current_price * 0.95,
                "width": 10.0,
                "position": "MIDDLE",
                "squeeze": False
            }
        
        sma = self._calculate_sma(prices, period)
        std = statistics.stdev(prices[-period:])
        
        upper = sma + (2 * std)
        lower = sma - (2 * std)
        width = ((upper - lower) / sma * 100) if sma > 0 else 0
        
        # Determinar posição
        if current_price > upper:
            position = "ABOVE_UPPER"
        elif current_price < lower:
            position = "BELOW_LOWER"
        elif current_price > sma:
            position = "UPPER_HALF"
        else:
            position = "LOWER_HALF"
        
        # Detectar squeeze (baixa volatilidade)
        squeeze = width < 10  # Banda menor que 10%
        
        return {
            "upper": round(upper, 8),
            "middle": round(sma, 8),
            "lower": round(lower, 8),
            "width": round(width, 2),
            "position": position,
            "squeeze": squeeze
        }
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calcula Average True Range"""
        if len(prices) < 2:
            return prices[0] * 0.05 if prices else 0
        
        true_ranges = []
        for i in range(1, len(prices)):
            high = max(prices[i], prices[i-1])
            low = min(prices[i], prices[i-1])
            true_range = high - low
            true_ranges.append(true_range)
        
        if len(true_ranges) >= period:
            return sum(true_ranges[-period:]) / period
        else:
            return sum(true_ranges) / len(true_ranges) if true_ranges else 0
    
    def _determine_volatility_regime(self, atr_percentage: float) -> str:
        """Determina o regime de volatilidade"""
        if atr_percentage < 2:
            return "LOW"
        elif atr_percentage < 5:
            return "NORMAL"
        elif atr_percentage < 10:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _calculate_historical_volatility(self, prices: List[float], period: int = 20) -> float:
        """Calcula volatilidade histórica"""
        if len(prices) < 2:
            return 0
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return 0
        
        # Usar últimos 'period' retornos
        recent_returns = returns[-period:] if len(returns) >= period else returns
        
        if len(recent_returns) > 1:
            return statistics.stdev(recent_returns) * 100 * (252 ** 0.5)  # Anualizada
        else:
            return 0
    
    def _calculate_volatility_percentile(self, prices: List[float], current_vol: float) -> int:
        """Calcula o percentil da volatilidade atual"""
        if len(prices) < 100:
            return 50  # Neutro se não há dados suficientes
        
        # Calcular volatilidade para diferentes períodos
        vol_history = []
        for i in range(20, len(prices)):
            period_prices = prices[i-20:i]
            vol = self._calculate_historical_volatility(period_prices)
            vol_history.append(vol)
        
        if not vol_history:
            return 50
        
        # Calcular percentil
        below = sum(1 for v in vol_history if v < current_vol)
        percentile = (below / len(vol_history)) * 100
        
        return round(percentile)
    
    def _calculate_volume_indicators(self, volumes: List[float], prices: List[float]) -> Dict:
        """Calcula indicadores de volume"""
        if not volumes or len(volumes) < 2:
            return self._get_default_volume()
        
        # Volume Trend
        recent_avg = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else sum(volumes) / len(volumes)
        previous_avg = sum(volumes[-10:-5]) / 5 if len(volumes) >= 10 else recent_avg
        
        if recent_avg > previous_avg * 1.2:
            volume_trend = "INCREASING"
        elif recent_avg < previous_avg * 0.8:
            volume_trend = "DECREASING"
        else:
            volume_trend = "STABLE"
        
        # OBV - On Balance Volume
        obv = self._calculate_obv(prices, volumes)
        
        # Volume Ratio
        current_volume = volumes[-1] if volumes else 0
        avg_volume = sum(volumes[-20:]) / len(volumes[-20:]) if len(volumes) >= 20 else sum(volumes) / len(volumes)
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Unusual Activity
        unusual_activity = volume_ratio > 2 or volume_ratio < 0.5
        
        return {
            "volume_trend": volume_trend,
            "obv": obv,
            "volume_ratio": round(volume_ratio, 2),
            "unusual_activity": unusual_activity,
            "average_volume": round(avg_volume, 2),
            "current_volume": round(current_volume, 2)
        }
    
    def _calculate_obv(self, prices: List[float], volumes: List[float]) -> Dict:
        """Calcula On Balance Volume"""
        if len(prices) < 2 or len(volumes) < 2:
            return {"value": 0, "trend": "NEUTRAL"}
        
        obv = 0
        obv_values = []
        
        for i in range(1, min(len(prices), len(volumes))):
            if prices[i] > prices[i-1]:
                obv += volumes[i]
            elif prices[i] < prices[i-1]:
                obv -= volumes[i]
            obv_values.append(obv)
        
        # Determinar tendência do OBV
        if len(obv_values) >= 5:
            recent_obv = sum(obv_values[-5:]) / 5
            previous_obv = sum(obv_values[-10:-5]) / 5 if len(obv_values) >= 10 else recent_obv
            
            if recent_obv > previous_obv:
                trend = "BULLISH"
            elif recent_obv < previous_obv:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"
        else:
            trend = "NEUTRAL"
        
        return {
            "value": round(obv, 2),
            "trend": trend
        }
    
    def _detect_patterns(self, prices: List[float], current_price: float) -> Dict:
        """Detecta padrões gráficos e de candlestick"""
        
        chart_patterns = []
        candlestick_patterns = []
        support_resistance_tests = 0
        
        if len(prices) >= 20:
            # Detectar padrões gráficos simples
            chart_patterns = self._detect_chart_patterns(prices)
            
            # Detectar padrões de candlestick (simplificado)
            candlestick_patterns = self._detect_candlestick_patterns(prices)
            
            # Contar testes de suporte/resistência
            support_resistance_tests = self._count_support_resistance_tests(prices)
        
        return {
            "chart_patterns": chart_patterns,
            "candlestick_patterns": candlestick_patterns,
            "support_resistance_tests": support_resistance_tests,
            "pattern_strength": self._calculate_pattern_strength(chart_patterns, candlestick_patterns)
        }
    
    def _detect_chart_patterns(self, prices: List[float]) -> List[str]:
        """Detecta padrões gráficos básicos"""
        patterns = []
        
        if len(prices) < 20:
            return patterns
        
        # Detectar triângulo ascendente
        if self._is_ascending_triangle(prices):
            patterns.append("ascending_triangle")
        
        # Detectar double bottom
        if self._is_double_bottom(prices):
            patterns.append("double_bottom")
        
        # Detectar head and shoulders
        if self._is_head_and_shoulders(prices):
            patterns.append("head_and_shoulders")
        
        # Detectar flag/pennant
        if self._is_flag_pattern(prices):
            patterns.append("flag")
        
        return patterns
    
    def _is_ascending_triangle(self, prices: List[float]) -> bool:
        """Detecta padrão de triângulo ascendente"""
        if len(prices) < 20:
            return False
        
        # Verificar se os topos estão no mesmo nível e os fundos estão subindo
        highs = []
        lows = []
        
        for i in range(0, len(prices)-5, 5):
            period = prices[i:i+5]
            highs.append(max(period))
            lows.append(min(period))
        
        if len(highs) < 3:
            return False
        
        # Topos devem estar próximos (variação < 2%)
        avg_high = sum(highs) / len(highs)
        high_variation = all(abs(h - avg_high) / avg_high < 0.02 for h in highs)
        
        # Fundos devem estar subindo
        lows_rising = all(lows[i] < lows[i+1] for i in range(len(lows)-1))
        
        return high_variation and lows_rising
    
    def _is_double_bottom(self, prices: List[float]) -> bool:
        """Detecta padrão double bottom"""
        if len(prices) < 20:
            return False
        
        # Encontrar dois mínimos similares
        min_indices = []
        for i in range(5, len(prices)-5):
            if prices[i] == min(prices[i-5:i+5]):
                min_indices.append(i)
        
        if len(min_indices) >= 2:
            # Verificar se os dois mínimos são similares (diferença < 3%)
            for i in range(len(min_indices)-1):
                idx1, idx2 = min_indices[i], min_indices[i+1]
                if abs(idx2 - idx1) > 5:  # Distância mínima entre fundos
                    diff = abs(prices[idx1] - prices[idx2]) / prices[idx1]
                    if diff < 0.03:
                        return True
        
        return False
    
    def _is_head_and_shoulders(self, prices: List[float]) -> bool:
        """Detecta padrão head and shoulders"""
        if len(prices) < 15:
            return False
        
        # Simplificado: procurar três picos com o do meio maior
        peaks = []
        for i in range(2, len(prices)-2):
            if prices[i] > prices[i-1] and prices[i] > prices[i-2] and \
               prices[i] > prices[i+1] and prices[i] > prices[i+2]:
                peaks.append((i, prices[i]))
        
        if len(peaks) >= 3:
            # Verificar se temos padrão de ombro-cabeça-ombro
            for i in range(len(peaks)-2):
                left_shoulder = peaks[i][1]
                head = peaks[i+1][1]
                right_shoulder = peaks[i+2][1]
                
                # Cabeça deve ser maior que os ombros
                if head > left_shoulder and head > right_shoulder:
                    # Ombros devem ser similares
                    if abs(left_shoulder - right_shoulder) / left_shoulder < 0.05:
                        return True
        
        return False
    
    def _is_flag_pattern(self, prices: List[float]) -> bool:
        """Detecta padrão de bandeira"""
        if len(prices) < 15:
            return False
        
        # Procurar movimento forte seguido de consolidação
        for i in range(5, len(prices)-10):
            # Movimento forte (>10% em 5 períodos)
            initial_move = abs(prices[i] - prices[i-5]) / prices[i-5]
            if initial_move > 0.1:
                # Consolidação (range < 5% nos próximos períodos)
                consolidation = prices[i:i+10]
                range_pct = (max(consolidation) - min(consolidation)) / min(consolidation)
                if range_pct < 0.05:
                    return True
        
        return False
    
    def _detect_candlestick_patterns(self, prices: List[float]) -> List[str]:
        """Detecta padrões de candlestick simplificados"""
        patterns = []
        
        if len(prices) < 3:
            return patterns
        
        # Hammer/Hanging Man
        if self._is_hammer(prices):
            patterns.append("hammer")
        
        # Doji
        if self._is_doji(prices):
            patterns.append("doji")
        
        # Engulfing
        if self._is_engulfing(prices):
            patterns.append("engulfing")
        
        # Morning/Evening Star
        if self._is_star_pattern(prices):
            patterns.append("star_pattern")
        
        return patterns
    
    def _is_hammer(self, prices: List[float]) -> bool:
        """Detecta padrão hammer"""
        if len(prices) < 3:
            return False
        
        # Simplificado: grande movimento para baixo seguido de recuperação
        recent = prices[-3:]
        if min(recent) == recent[1]:  # Mínimo no meio
            recovery = (recent[2] - recent[1]) / recent[1]
            if recovery > 0.02:  # Recuperação > 2%
                return True
        
        return False
    
    def _is_doji(self, prices: List[float]) -> bool:
        """Detecta padrão doji"""
        if len(prices) < 2:
            return False
        
        # Simplificado: mudança mínima no preço
        change = abs(prices[-1] - prices[-2]) / prices[-2]
        return change < 0.001  # Mudança < 0.1%
    
    def _is_engulfing(self, prices: List[float]) -> bool:
        """Detecta padrão engulfing"""
        if len(prices) < 3:
            return False
        
        # Bullish engulfing: grande vela verde após vela vermelha
        if prices[-3] > prices[-2] and prices[-1] > prices[-2]:
            if (prices[-1] - prices[-2]) > abs(prices[-2] - prices[-3]):
                return True
        
        # Bearish engulfing: grande vela vermelha após vela verde
        if prices[-3] < prices[-2] and prices[-1] < prices[-2]:
            if abs(prices[-1] - prices[-2]) > (prices[-2] - prices[-3]):
                return True
        
        return False
    
    def _is_star_pattern(self, prices: List[float]) -> bool:
        """Detecta padrão morning/evening star"""
        if len(prices) < 4:
            return False
        
        # Morning star: queda, indecisão, recuperação
        if prices[-4] > prices[-3] and abs(prices[-2] - prices[-3]) / prices[-3] < 0.01 and prices[-1] > prices[-2]:
            return True
        
        # Evening star: alta, indecisão, queda
        if prices[-4] < prices[-3] and abs(prices[-2] - prices[-3]) / prices[-3] < 0.01 and prices[-1] < prices[-2]:
            return True
        
        return False
    
    def _count_support_resistance_tests(self, prices: List[float]) -> int:
        """Conta quantas vezes o preço testou suporte/resistência"""
        if len(prices) < 20:
            return 0
        
        tests = 0
        
        # Identificar níveis significativos
        significant_levels = []
        for i in range(10, len(prices)-10):
            # Máximo local
            if prices[i] == max(prices[i-10:i+10]):
                significant_levels.append(prices[i])
            # Mínimo local
            if prices[i] == min(prices[i-10:i+10]):
                significant_levels.append(prices[i])
        
        # Contar quantas vezes o preço se aproximou desses níveis
        for level in significant_levels:
            touches = sum(1 for p in prices if abs(p - level) / level < 0.02)  # Dentro de 2%
            if touches >= 2:
                tests += 1
        
        return min(tests, 10)  # Limitar a 10
    
    def _calculate_pattern_strength(self, chart_patterns: List[str], candlestick_patterns: List[str]) -> str:
        """Calcula a força dos padrões detectados"""
        total_patterns = len(chart_patterns) + len(candlestick_patterns)
        
        if total_patterns == 0:
            return "NONE"
        elif total_patterns <= 2:
            return "WEAK"
        elif total_patterns <= 4:
            return "MODERATE"
        else:
            return "STRONG"
    
    def _get_rsi_signal(self, rsi: float, interpretation: str) -> str:
        """Gera sinal baseado no RSI"""
        if rsi < 20:
            return "STRONG_BUY"
        elif rsi < 30:
            return "BUY"
        elif rsi > 80:
            return "STRONG_SELL"
        elif rsi > 70:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_momentum_score(self, rsi: float, macd_data: Dict, stochastic: Dict) -> int:
        """Calcula score de momentum (0-100)"""
        score = 50  # Base neutra
        
        # RSI contribution
        if rsi < 30:
            score += 20
        elif rsi > 70:
            score -= 20
        else:
            score += (50 - rsi) / 2  # Normalizar para contribuição
        
        # MACD contribution
        if macd_data['signal'] == "BUY":
            score += 15
        elif macd_data['signal'] == "SELL":
            score -= 15
        
        # Stochastic contribution
        if stochastic['signal'] == "OVERSOLD":
            score += 15
        elif stochastic['signal'] == "OVERBOUGHT":
            score -= 15
        
        return max(0, min(100, round(score)))
    
    def _calculate_days_since_cross(self, macd_values: List[float], signal_line: float) -> int:
        """Calcula dias desde o último cruzamento MACD"""
        if len(macd_values) < 2:
            return 0
        
        days = 0
        for i in range(len(macd_values)-1, 0, -1):
            if (macd_values[i] > signal_line) != (macd_values[i-1] > signal_line):
                break
            days += 1
        
        return days
    
    def _check_golden_cross(self, ma50: float, ma200: float) -> bool:
        """Verifica se há golden cross (MA50 > MA200)"""
        return ma50 > ma200
    
    def _check_death_cross(self, ma50: float, ma200: float) -> bool:
        """Verifica se há death cross (MA50 < MA200)"""
        return ma50 < ma200
    
    def _generate_summary(self, momentum: Dict, trend: Dict, volatility: Dict, volume: Dict) -> Dict:
        """Gera resumo da análise técnica"""
        
        # Calcular score geral
        bullish_signals = 0
        bearish_signals = 0
        
        # Momentum signals
        if momentum['rsi']['value'] < 30:
            bullish_signals += 2
        elif momentum['rsi']['value'] > 70:
            bearish_signals += 2
        
        if momentum['macd']['signal'] == "BUY":
            bullish_signals += 2
        elif momentum['macd']['signal'] == "SELL":
            bearish_signals += 2
        
        # Trend signals
        if trend['trend_strength'] in ["STRONG_UP", "WEAK_UP"]:
            bullish_signals += 3
        elif trend['trend_strength'] in ["STRONG_DOWN", "WEAK_DOWN"]:
            bearish_signals += 3
        
        if trend.get('golden_cross'):
            bullish_signals += 2
        if trend.get('death_cross'):
            bearish_signals += 2
        
        # Volume signals
        if volume['obv']['trend'] == "BULLISH":
            bullish_signals += 1
        elif volume['obv']['trend'] == "BEARISH":
            bearish_signals += 1
        
        # Overall signal
        if bullish_signals > bearish_signals + 2:
            overall_signal = "STRONG_BUY"
        elif bullish_signals > bearish_signals:
            overall_signal = "BUY"
        elif bearish_signals > bullish_signals + 2:
            overall_signal = "STRONG_SELL"
        elif bearish_signals > bullish_signals:
            overall_signal = "SELL"
        else:
            overall_signal = "NEUTRAL"
        
        # Calculate confidence
        total_signals = bullish_signals + bearish_signals
        if total_signals > 8:
            confidence = "HIGH"
        elif total_signals > 4:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        return {
            "overall_signal": overall_signal,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "confidence": confidence,
            "key_levels": {
                "support": trend['moving_averages']['ma50']['value'],
                "resistance": trend['moving_averages']['ma20']['value']
            },
            "recommendation": self._generate_recommendation(overall_signal, confidence, volatility['volatility_regime'])
        }
    
    def _generate_recommendation(self, signal: str, confidence: str, volatility_regime: str) -> str:
        """Gera recomendação baseada na análise"""
        if signal == "STRONG_BUY" and confidence == "HIGH":
            return "Forte sinal de compra. Considere entrada escalonada."
        elif signal == "BUY":
            return "Sinal de compra moderado. Aguarde confirmação ou use stop loss apertado."
        elif signal == "STRONG_SELL" and confidence == "HIGH":
            return "Forte sinal de venda. Considere reduzir posição ou sair."
        elif signal == "SELL":
            return "Sinal de venda moderado. Monitore suportes próximos."
        elif volatility_regime == "EXTREME":
            return "Alta volatilidade detectada. Reduza tamanho da posição."
        else:
            return "Mercado neutro. Aguarde sinais mais claros antes de operar."
    
    def _get_default_volume(self) -> Dict:
        """Retorna análise de volume padrão"""
        return {
            "volume_trend": "STABLE",
            "obv": {"value": 0, "trend": "NEUTRAL"},
            "volume_ratio": 1.0,
            "unusual_activity": False,
            "average_volume": 0,
            "current_volume": 0
        }
    
    def _get_basic_analysis(self, current_price: float, token_data: Dict) -> Dict:
        """Retorna análise básica quando não há dados históricos"""
        return {
            "momentum": {
                "rsi": {"value": 50, "interpretation": "NEUTRAL", "signal": "HOLD"},
                "macd": {
                    "macd_line": 0,
                    "signal_line": 0,
                    "histogram": 0,
                    "signal": "NEUTRAL",
                    "days_since_cross": 0,
                    "trend": "NEUTRAL"
                },
                "stochastic": {"k": 50, "d": 50, "signal": "NEUTRAL", "crossover": "NEUTRAL"},
                "momentum_score": 50
            },
            "trend": {
                "moving_averages": {
                    "ma20": {"value": current_price, "position": "AT", "distance": "0%"},
                    "ma50": {"value": current_price, "position": "AT", "distance": "0%"},
                    "ma200": {"value": current_price, "position": "AT", "distance": "0%"}
                },
                "trend_strength": "NEUTRAL",
                "ema_ribbon": "NEUTRAL",
                "golden_cross": False,
                "death_cross": False
            },
            "volatility": {
                "bollinger_bands": {
                    "upper": current_price * 1.05,
                    "middle": current_price,
                    "lower": current_price * 0.95,
                    "width": 10.0,
                    "position": "MIDDLE",
                    "squeeze": False
                },
                "atr": {"value": current_price * 0.05, "percentage": "5%"},
                "volatility_regime": "NORMAL",
                "historical_volatility": "0%",
                "volatility_percentile": 50
            },
            "volume": self._get_default_volume(),
            "patterns": {
                "chart_patterns": [],
                "candlestick_patterns": [],
                "support_resistance_tests": 0,
                "pattern_strength": "NONE"
            },
            "summary": {
                "overall_signal": "NEUTRAL",
                "bullish_signals": 0,
                "bearish_signals": 0,
                "confidence": "LOW",
                "key_levels": {
                    "support": current_price * 0.95,
                    "resistance": current_price * 1.05
                },
                "recommendation": "Dados insuficientes para análise técnica completa."
            }
        }
    
    def _get_default_indicators(self, token_data: Dict) -> Dict:
        """Retorna indicadores padrão em caso de erro"""
        current_price = float(token_data.get('current_price', 0))
        return self._get_basic_analysis(current_price, token_data)
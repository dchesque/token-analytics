"""
Actionable Strategies Service - Estratégias personalizadas e acionáveis
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ActionableStrategiesService:
    """Serviço para gerar estratégias personalizadas e acionáveis"""
    
    def generate_strategies(self, 
                          token_data: Dict[str, Any], 
                          master_score: float,
                          technical_analysis: Dict[str, Any],
                          trading_levels: Dict[str, Any],
                          market_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Gera estratégias personalizadas baseadas em análise completa
        """
        try:
            current_price = float(token_data.get('current_price', 0))
            market_cap_rank = token_data.get('market_cap_rank', 1000)
            
            # Determinar contexto de mercado
            market_conditions = self._assess_market_conditions(
                token_data, technical_analysis, market_context
            )
            
            # Gerar estratégias para diferentes perfis
            strategies = {
                "conservative": self._generate_conservative_strategy(
                    token_data, master_score, technical_analysis, trading_levels, market_conditions
                ),
                "moderate": self._generate_moderate_strategy(
                    token_data, master_score, technical_analysis, trading_levels, market_conditions
                ),
                "aggressive": self._generate_aggressive_strategy(
                    token_data, master_score, technical_analysis, trading_levels, market_conditions
                )
            }
            
            # Gerar recomendação principal
            primary_recommendation = self._generate_primary_recommendation(
                strategies, master_score, technical_analysis
            )
            
            # Adicionar alertas e avisos
            warnings = self._generate_warnings(
                token_data, technical_analysis, market_conditions
            )
            
            return {
                "strategies": strategies,
                "primary_recommendation": primary_recommendation,
                "market_conditions": market_conditions,
                "warnings": warnings,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating strategies: {e}")
            return self._get_default_strategies(token_data, master_score)
    
    def _assess_market_conditions(self, token_data: Dict, technical_analysis: Dict, market_context: Optional[Dict]) -> Dict:
        """Avalia as condições atuais do mercado"""
        
        # Volatilidade do token
        volatility_regime = technical_analysis.get('volatility', {}).get('volatility_regime', 'NORMAL')
        
        # Tendência geral
        trend_strength = technical_analysis.get('trend', {}).get('trend_strength', 'NEUTRAL')
        
        # Volume
        volume_trend = technical_analysis.get('volume', {}).get('volume_trend', 'STABLE')
        
        # Fear & Greed Index (estimado baseado em momentum)
        momentum_score = technical_analysis.get('momentum', {}).get('momentum_score', 50)
        if momentum_score < 25:
            fear_greed = "EXTREME_FEAR"
        elif momentum_score < 40:
            fear_greed = "FEAR"
        elif momentum_score < 60:
            fear_greed = "NEUTRAL"
        elif momentum_score < 75:
            fear_greed = "GREED"
        else:
            fear_greed = "EXTREME_GREED"
        
        # Bitcoin correlation (estimativa baseada no ranking)
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        if market_cap_rank <= 10:
            btc_correlation = "LOW"
        elif market_cap_rank <= 100:
            btc_correlation = "MEDIUM"
        else:
            btc_correlation = "HIGH"
        
        return {
            "volatility_regime": volatility_regime,
            "trend_strength": trend_strength,
            "volume_trend": volume_trend,
            "fear_greed_index": fear_greed,
            "btc_correlation": btc_correlation,
            "overall_sentiment": self._calculate_overall_sentiment(
                trend_strength, fear_greed, volatility_regime
            )
        }
    
    def _calculate_overall_sentiment(self, trend: str, fear_greed: str, volatility: str) -> str:
        """Calcula sentimento geral do mercado"""
        bullish_factors = 0
        bearish_factors = 0
        
        # Trend factors
        if trend in ["STRONG_UP", "WEAK_UP"]:
            bullish_factors += 2
        elif trend in ["STRONG_DOWN", "WEAK_DOWN"]:
            bearish_factors += 2
        
        # Fear & Greed factors
        if fear_greed in ["EXTREME_FEAR", "FEAR"]:
            bullish_factors += 1  # Contrarian indicator
        elif fear_greed in ["EXTREME_GREED", "GREED"]:
            bearish_factors += 1
        
        # Volatility factors
        if volatility == "EXTREME":
            bearish_factors += 1
        
        if bullish_factors > bearish_factors:
            return "BULLISH"
        elif bearish_factors > bullish_factors:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _generate_conservative_strategy(self, token_data: Dict, score: float, 
                                      technical: Dict, trading_levels: Dict, 
                                      market: Dict) -> Dict:
        """Gera estratégia conservadora"""
        
        current_price = float(token_data.get('current_price', 0))
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        
        # Lógica de decisão conservadora
        if score < 4:
            action = "AVOID"
            conviction = "HIGH"
            rationale = "Score muito baixo indica riscos elevados"
        elif score < 6:
            action = "WAIT"
            conviction = "MEDIUM" 
            rationale = "Aguardar melhores condições de entrada"
        elif score < 8:
            action = "DCA"
            conviction = "MEDIUM"
            rationale = "DCA cauteloso em token com fundamentos medianos"
        else:
            action = "BUY"
            conviction = "HIGH"
            rationale = "Score alto com estratégia conservadora"
        
        # Ajustes baseados em condições técnicas
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        if technical_signal in ["STRONG_SELL", "SELL"] and action in ["BUY", "DCA"]:
            action = "WAIT"
            rationale += " + sinais técnicos negativos"
        
        # Position sizing conservador
        max_position = "2%" if market_cap_rank <= 100 else "1%"
        if market['volatility_regime'] == "EXTREME":
            max_position = "0.5%"
        
        strategy = {
            "action": action,
            "conviction": conviction,
            "rationale": rationale,
            "position_sizing": {
                "initial": "0.5%" if action in ["BUY", "DCA"] else "0%",
                "maximum": max_position,
                "scaling": "Aumentar gradualmente apenas com confirmação técnica"
            },
            "execution_plan": self._generate_conservative_execution(
                action, current_price, trading_levels, technical
            ),
            "risk_management": {
                "stop_loss": trading_levels.get('stop_loss', {}).get('initial', {}).get('price', current_price * 0.9),
                "position_limit": max_position,
                "correlation_check": "Verificar correlação com BTC antes de aumentar posição"
            },
            "monitoring": {
                "key_metrics": [
                    "Score de transparência",
                    "Volume de trading",
                    "Suporte técnico em " + str(round(current_price * 0.95, 4))
                ],
                "review_triggers": [
                    "Score cai abaixo de 5",
                    "Break de suporte principal", 
                    "Volume seca por 3+ dias"
                ],
                "adjustment_rules": [
                    "Reduzir posição se score cair >20%",
                    "Considerar saída se perda >10%",
                    "Reavaliar mensalmente"
                ]
            }
        }
        
        return strategy
    
    def _generate_moderate_strategy(self, token_data: Dict, score: float,
                                   technical: Dict, trading_levels: Dict,
                                   market: Dict) -> Dict:
        """Gera estratégia moderada"""
        
        current_price = float(token_data.get('current_price', 0))
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        
        # Lógica de decisão moderada
        if score < 3:
            action = "AVOID"
            conviction = "HIGH"
            rationale = "Riscos fundamentais muito altos"
        elif score < 5:
            action = "WATCHLIST"
            conviction = "MEDIUM"
            rationale = "Monitorar para possível entrada futura"
        elif score < 7:
            action = "DCA"
            conviction = "MEDIUM"
            rationale = "Entrada gradual com fundamentos médios"
        else:
            action = "BUY"
            conviction = "HIGH"
            rationale = "Score sólido justifica posição maior"
        
        # Ajustes técnicos
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        if technical_signal == "STRONG_BUY" and action == "WATCHLIST":
            action = "DCA"
            rationale += " + forte sinal técnico de compra"
        elif technical_signal in ["STRONG_SELL"] and action == "BUY":
            action = "WAIT"
            rationale += " mas aguardando melhores níveis técnicos"
        
        # Position sizing moderado
        max_position = "5%" if market_cap_rank <= 50 else "3%" if market_cap_rank <= 200 else "2%"
        
        strategy = {
            "action": action,
            "conviction": conviction,
            "rationale": rationale,
            "position_sizing": {
                "initial": "1%" if action in ["BUY", "DCA"] else "0%",
                "maximum": max_position,
                "scaling": "Escalar posição baseado em performance e confirmações"
            },
            "execution_plan": self._generate_moderate_execution(
                action, current_price, trading_levels, technical
            ),
            "risk_management": {
                "stop_loss": trading_levels.get('stop_loss', {}).get('initial', {}).get('price', current_price * 0.92),
                "position_limit": max_position,
                "correlation_check": "Monitorar correlação com top 10 tokens"
            },
            "monitoring": {
                "key_metrics": [
                    "Score master vs benchmark",
                    "RSI e MACD",
                    "Volume e liquidez"
                ],
                "review_triggers": [
                    "Mudança >15% no score",
                    "Break de resistência/suporte",
                    "Volume anômalo"
                ],
                "adjustment_rules": [
                    "Aumentar se score melhora +20%",
                    "Reduzir se score piora >15%",
                    "Take profit parcial em +25%"
                ]
            }
        }
        
        return strategy
    
    def _generate_aggressive_strategy(self, token_data: Dict, score: float,
                                     technical: Dict, trading_levels: Dict, 
                                     market: Dict) -> Dict:
        """Gera estratégia agressiva"""
        
        current_price = float(token_data.get('current_price', 0))
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        
        # Lógica de decisão agressiva
        if score < 4:
            action = "SHORT_TERM_TRADE"
            conviction = "LOW"
            rationale = "Trade especulativo apenas com stop apertado"
        elif score < 6:
            action = "SWING_TRADE"
            conviction = "MEDIUM"
            rationale = "Swing trade aproveitando volatilidade"
        elif score < 8:
            action = "POSITION_TRADE"
            conviction = "MEDIUM"
            rationale = "Posição média com gestão ativa"
        else:
            action = "ACCUMULATE"
            conviction = "HIGH"
            rationale = "Score alto justifica acumulação agressiva"
        
        # Ajustes técnicos agressivos
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        volatility = market.get('volatility_regime', 'NORMAL')
        
        if technical_signal == "STRONG_BUY" and volatility != "EXTREME":
            if action == "SWING_TRADE":
                action = "POSITION_TRADE"
            conviction = "HIGH"
            rationale += " + momentum técnico forte"
        
        # Position sizing agressivo
        base_position = "3%" if market_cap_rank <= 20 else "2%" if market_cap_rank <= 100 else "1%"
        if volatility == "EXTREME":
            base_position = str(float(base_position.rstrip('%')) * 0.5) + "%"
        
        max_position = "10%" if market_cap_rank <= 20 else "7%" if market_cap_rank <= 100 else "5%"
        
        strategy = {
            "action": action,
            "conviction": conviction,
            "rationale": rationale,
            "position_sizing": {
                "initial": base_position if action != "SHORT_TERM_TRADE" else "0.5%",
                "maximum": max_position,
                "scaling": "Escalar rapidamente em confirmações, reduzir em sinais contrários"
            },
            "execution_plan": self._generate_aggressive_execution(
                action, current_price, trading_levels, technical
            ),
            "risk_management": {
                "stop_loss": trading_levels.get('stop_loss', {}).get('initial', {}).get('price', current_price * 0.88),
                "position_limit": max_position,
                "correlation_check": "Diversificar apenas entre setores não correlacionados"
            },
            "monitoring": {
                "key_metrics": [
                    "Momentum score diário",
                    "Volume breakouts", 
                    "Social sentiment"
                ],
                "review_triggers": [
                    "Mudança técnica >10%",
                    "Volume spike 2x+",
                    "Break de nível chave"
                ],
                "adjustment_rules": [
                    "Dobrar posição em breakouts confirmados",
                    "Corte rápido em falsos sinais",
                    "Take profit agressivo 30-50%"
                ]
            }
        }
        
        return strategy
    
    def _generate_conservative_execution(self, action: str, current_price: float,
                                       trading_levels: Dict, technical: Dict) -> Dict:
        """Gera plano de execução conservador"""
        
        if action == "AVOID":
            return {
                "immediate_action": "Não investir no momento",
                "entry_conditions": ["Score subir acima de 6", "Confirmação técnica clara"],
                "exit_conditions": ["N/A"],
                "time_horizon": "Indefinido",
                "specific_instructions": [
                    "Manter token na watchlist",
                    "Reavaliar mensalmente",
                    "Considerar apenas com score >6"
                ]
            }
        
        elif action == "WAIT":
            support_level = trading_levels.get('entry_points', [{}])[0].get('price', current_price * 0.95)
            return {
                "immediate_action": "Aguardar melhores condições",
                "entry_conditions": [
                    f"Preço recuar para ${round(support_level, 4)}",
                    "RSI abaixo de 40",
                    "Volume confirmar interesse"
                ],
                "exit_conditions": ["Score cair <5", "Break de suporte"],
                "time_horizon": "2-4 semanas",
                "specific_instructions": [
                    f"Colocar alerta em ${round(support_level, 4)}",
                    "Verificar condições técnicas diariamente",
                    "Não entrar em FOMO"
                ]
            }
        
        elif action == "DCA":
            entry_points = trading_levels.get('entry_points', [])
            return {
                "immediate_action": "Iniciar DCA com 0.5% do portfolio",
                "entry_conditions": [
                    "Compras semanais pequenas",
                    "Aumentar em quedas >10%", 
                    "Pausar se score deteriorar"
                ],
                "exit_conditions": [
                    "Score <4",
                    "Perda acumulada >12%",
                    "Break técnico confirmado"
                ],
                "time_horizon": "3-6 meses",
                "specific_instructions": [
                    "Comprar $X a cada quarta-feira",
                    f"Dobrar compra se preço <${round(current_price * 0.9, 4)}",
                    "Revisar estratégia mensalmente",
                    "Não exceder 2% do portfolio total"
                ]
            }
        
        else:  # BUY
            entry_price = trading_levels.get('entry_points', [{}])[0].get('price', current_price)
            stop_loss = trading_levels.get('stop_loss', {}).get('initial', {}).get('price', current_price * 0.92)
            
            return {
                "immediate_action": f"Compra inicial de 0.5% próximo a ${round(entry_price, 4)}",
                "entry_conditions": [
                    "Preço próximo do nível calculado",
                    "Volume confirmar movimento",
                    "BTC estável (variação <3%)"
                ],
                "exit_conditions": [
                    f"Stop loss em ${round(stop_loss, 4)}",
                    "Score cair abaixo de 6",
                    "Deterioração técnica"
                ],
                "time_horizon": "1-3 meses",
                "specific_instructions": [
                    f"1. Colocar ordem limit em ${round(entry_price, 4)}",
                    f"2. Definir stop loss em ${round(stop_loss, 4)}",
                    "3. Aumentar posição gradualmente se confirmado",
                    "4. Take profit parcial em +20%"
                ]
            }
    
    def _generate_moderate_execution(self, action: str, current_price: float,
                                   trading_levels: Dict, technical: Dict) -> Dict:
        """Gera plano de execução moderado"""
        
        if action == "AVOID":
            return {
                "immediate_action": "Evitar investimento",
                "entry_conditions": ["Score >5", "Tendência técnica clara"],
                "exit_conditions": ["N/A"],
                "time_horizon": "Até condições melhorarem",
                "specific_instructions": [
                    "Monitorar score semanalmente",
                    "Aguardar reversão técnica",
                    "Considerar apenas com múltiplas confirmações"
                ]
            }
        
        elif action == "WATCHLIST":
            return {
                "immediate_action": "Adicionar à watchlist premium",
                "entry_conditions": [
                    "Score melhorar para >6",
                    "Break de resistência técnica",
                    "Volume crescente por 3+ dias"
                ],
                "exit_conditions": ["Score deteriorar <4"],
                "time_horizon": "1-2 meses de observação",
                "specific_instructions": [
                    "Configurar alertas de preço e volume",
                    "Acompanhar desenvolvimentos do projeto",
                    "Preparar análise de entrada"
                ]
            }
        
        elif action in ["DCA", "BUY"]:
            entry_points = trading_levels.get('entry_points', [])
            targets = trading_levels.get('take_profit_targets', [])
            
            return {
                "immediate_action": "Entrada escalonada começando com 1%",
                "entry_conditions": [
                    f"Nível 1: ${round(entry_points[0]['price'], 4) if entry_points else current_price} (25%)",
                    f"Nível 2: ${round(entry_points[1]['price'], 4) if len(entry_points) > 1 else current_price * 0.95} (35%)",
                    f"Nível 3: ${round(entry_points[2]['price'], 4) if len(entry_points) > 2 else current_price * 0.92} (40%)"
                ],
                "exit_conditions": [
                    f"Target 1: ${round(targets[0]['price'], 4) if targets else current_price * 1.15} (40%)",
                    f"Target 2: ${round(targets[1]['price'], 4) if len(targets) > 1 else current_price * 1.25} (35%)",
                    "Stop loss: Break de suporte confirmado"
                ],
                "time_horizon": "2-6 meses",
                "specific_instructions": [
                    "Executar entrada em 3 níveis",
                    "Usar trailing stop após +15%",
                    "Reavaliar posição a cada +/-20%",
                    "Manter log de decisões"
                ]
            }
        
        else:  # WAIT with better conditions
            return {
                "immediate_action": "Aguardar configuração técnica mais clara",
                "entry_conditions": [
                    "Confirmação de trend",
                    "RSI sair de extremos",
                    "Volume validar movimento"
                ],
                "exit_conditions": ["Condições técnicas deteriorarem"],
                "time_horizon": "2-6 semanas",
                "specific_instructions": [
                    "Monitorar diariamente",
                    "Preparar ordem para execução rápida",
                    "Não entrar sem confirmação técnica"
                ]
            }
    
    def _generate_aggressive_execution(self, action: str, current_price: float,
                                     trading_levels: Dict, technical: Dict) -> Dict:
        """Gera plano de execução agressivo"""
        
        if action == "SHORT_TERM_TRADE":
            return {
                "immediate_action": "Trade especulativo com 0.5%",
                "entry_conditions": [
                    "Break de resistência intraday",
                    "Volume >150% da média",
                    "Momentum técnico forte"
                ],
                "exit_conditions": [
                    "Stop apertado: -3%",
                    "Target: +8-12%",
                    "Máximo 48h holding"
                ],
                "time_horizon": "1-3 dias",
                "specific_instructions": [
                    "Usar apenas capital especulativo",
                    "Stop loss automático",
                    "Take profit parcial em +6%",
                    "Sair no close se não performar"
                ]
            }
        
        elif action == "SWING_TRADE":
            return {
                "immediate_action": "Posição swing com 2%",
                "entry_conditions": [
                    "Confirmação de reversão técnica",
                    "Volume breakout confirmado",
                    "RSI saindo de oversold"
                ],
                "exit_conditions": [
                    "Target: +25-40%",
                    "Stop: -8%",
                    "Time stop: 4-6 semanas"
                ],
                "time_horizon": "2-6 semanas",
                "specific_instructions": [
                    "Entrada em 2 tranches",
                    "Trailing stop após +15%",
                    "Take profit 50% em +25%",
                    "Reavaliar em resistências"
                ]
            }
        
        elif action == "POSITION_TRADE":
            entry_points = trading_levels.get('entry_points', [])
            targets = trading_levels.get('take_profit_targets', [])
            
            return {
                "immediate_action": "Construir posição de 2-3%",
                "entry_conditions": [
                    "Accumular em pullbacks",
                    "Aumentar em breakouts",
                    "Scale in agressivamente"
                ],
                "exit_conditions": [
                    f"Target principal: ${round(targets[1]['price'], 4) if len(targets) > 1 else current_price * 1.3}",
                    "Stop dinâmico baseado em ATR",
                    "Reavaliar em macro changes"
                ],
                "time_horizon": "1-4 meses",
                "specific_instructions": [
                    "Build full position rapidamente",
                    "Use momentum para adicionar",
                    "Take profit escalonado 30/40/30",
                    "Hedge com derivativos se disponível"
                ]
            }
        
        else:  # ACCUMULATE
            return {
                "immediate_action": "Início de acumulação agressiva",
                "entry_conditions": [
                    "Comprar qualquer dip <5%",
                    "Dobrar em quedas >10%",
                    "Scale máximo permitido"
                ],
                "exit_conditions": [
                    "Score fundamental deteriorar >30%",
                    "Break estrutural confirmado",
                    "Target longo prazo: +100-200%"
                ],
                "time_horizon": "3-12 meses",
                "specific_instructions": [
                    "Usar todo capital disponível para o token",
                    "DCA agressivo em correções",
                    "Hold através de volatilidade normal",
                    "Take profit apenas em targets extremos"
                ]
            }
    
    def _generate_primary_recommendation(self, strategies: Dict, score: float, technical: Dict) -> Dict:
        """Gera recomendação principal baseada nas estratégias"""
        
        # Determinar qual estratégia recomendar como principal
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        confidence = technical.get('summary', {}).get('confidence', 'LOW')
        
        # Lógica para escolher estratégia principal
        if score >= 8 and technical_signal in ["STRONG_BUY", "BUY"] and confidence == "HIGH":
            primary_strategy = "moderate"
            risk_level = "MODERATE"
        elif score >= 7 and technical_signal in ["BUY", "NEUTRAL"]:
            primary_strategy = "moderate"
            risk_level = "MODERATE"
        elif score >= 6:
            primary_strategy = "conservative"
            risk_level = "LOW"
        elif score < 4:
            primary_strategy = "conservative"  # Will likely be AVOID
            risk_level = "HIGH"
        else:
            primary_strategy = "conservative"
            risk_level = "MODERATE"
        
        chosen_strategy = strategies[primary_strategy]
        
        return {
            "recommended_strategy": primary_strategy.upper(),
            "action": chosen_strategy["action"],
            "conviction": chosen_strategy["conviction"],
            "risk_level": risk_level,
            "key_reason": chosen_strategy["rationale"],
            "immediate_steps": chosen_strategy["execution_plan"]["specific_instructions"][:3],
            "success_probability": self._calculate_success_probability(score, technical, chosen_strategy),
            "expected_timeline": chosen_strategy["execution_plan"]["time_horizon"]
        }
    
    def _calculate_success_probability(self, score: float, technical: Dict, strategy: Dict) -> str:
        """Calcula probabilidade de sucesso da estratégia"""
        base_prob = min(score * 10, 90)  # Score 8 = 80% base
        
        # Ajustes técnicos
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        if technical_signal in ["STRONG_BUY", "BUY"]:
            base_prob += 10
        elif technical_signal in ["STRONG_SELL", "SELL"]:
            base_prob -= 15
        
        # Ajustes por convicção
        conviction = strategy.get('conviction', 'LOW')
        if conviction == "HIGH":
            base_prob += 5
        elif conviction == "LOW":
            base_prob -= 10
        
        # Limitar entre 10-90%
        final_prob = max(10, min(90, base_prob))
        
        if final_prob >= 70:
            return f"ALTA ({round(final_prob)}%)"
        elif final_prob >= 50:
            return f"MÉDIA ({round(final_prob)}%)"
        else:
            return f"BAIXA ({round(final_prob)}%)"
    
    def _generate_warnings(self, token_data: Dict, technical: Dict, market: Dict) -> List[Dict]:
        """Gera alertas e avisos importantes"""
        warnings = []
        
        current_price = float(token_data.get('current_price', 0))
        market_cap_rank = token_data.get('market_cap_rank', 1000)
        
        # Warning de volatilidade
        volatility_regime = market.get('volatility_regime', 'NORMAL')
        if volatility_regime == "EXTREME":
            warnings.append({
                "type": "HIGH_VOLATILITY",
                "severity": "HIGH",
                "message": "Volatilidade extrema detectada",
                "recommendation": "Reduzir tamanhos de posição pela metade",
                "icon": "⚠️"
            })
        
        # Warning técnico
        technical_signal = technical.get('summary', {}).get('overall_signal', 'NEUTRAL')
        if technical_signal in ["STRONG_SELL", "SELL"]:
            warnings.append({
                "type": "TECHNICAL_NEGATIVE",
                "severity": "MEDIUM",
                "message": "Múltiplos indicadores técnicos negativos",
                "recommendation": "Aguardar reversão antes de investir",
                "icon": "📉"
            })
        
        # Warning de liquidez
        if market_cap_rank > 500:
            warnings.append({
                "type": "LOW_LIQUIDITY",
                "severity": "MEDIUM", 
                "message": "Token de baixa capitalização e liquidez",
                "recommendation": "Usar ordens limit e evitar posições grandes",
                "icon": "💧"
            })
        
        # Warning de correlação BTC
        btc_correlation = market.get('btc_correlation', 'MEDIUM')
        if btc_correlation == "HIGH":
            warnings.append({
                "type": "BTC_CORRELATION",
                "severity": "LOW",
                "message": "Alta correlação com Bitcoin",
                "recommendation": "Monitorar BTC antes de tomar decisões",
                "icon": "🔗"
            })
        
        # Warning de Fear & Greed
        fear_greed = market.get('fear_greed_index', 'NEUTRAL')
        if fear_greed == "EXTREME_GREED":
            warnings.append({
                "type": "MARKET_EUPHORIA",
                "severity": "MEDIUM",
                "message": "Mercado em euforia extrema",
                "recommendation": "Considerar tomar lucros parciais",
                "icon": "🚀"
            })
        elif fear_greed == "EXTREME_FEAR":
            warnings.append({
                "type": "MARKET_PANIC",
                "severity": "LOW",
                "message": "Mercado em pânico extremo",
                "recommendation": "Pode ser oportunidade para compra gradual",
                "icon": "😰"
            })
        
        return warnings
    
    def _get_default_strategies(self, token_data: Dict, score: float) -> Dict:
        """Retorna estratégias padrão em caso de erro"""
        current_price = float(token_data.get('current_price', 0))
        
        default_strategy = {
            "action": "WAIT",
            "conviction": "LOW",
            "rationale": "Análise incompleta - aguardar dados",
            "position_sizing": {
                "initial": "0%",
                "maximum": "1%",
                "scaling": "Aguardar análise completa"
            },
            "execution_plan": {
                "immediate_action": "Não tomar ação até análise completa",
                "entry_conditions": ["Dados suficientes para análise"],
                "exit_conditions": ["N/A"],
                "time_horizon": "Indefinido",
                "specific_instructions": [
                    "Aguardar dados de mercado",
                    "Reavaliar quando análise estiver completa"
                ]
            },
            "risk_management": {
                "stop_loss": current_price * 0.9,
                "position_limit": "1%",
                "correlation_check": "Verificar antes de qualquer entrada"
            },
            "monitoring": {
                "key_metrics": ["Disponibilidade de dados"],
                "review_triggers": ["Sistema voltar ao normal"],
                "adjustment_rules": ["Seguir estratégias normais após correção"]
            }
        }
        
        return {
            "strategies": {
                "conservative": default_strategy,
                "moderate": default_strategy,
                "aggressive": default_strategy
            },
            "primary_recommendation": {
                "recommended_strategy": "CONSERVATIVE",
                "action": "WAIT",
                "conviction": "LOW",
                "risk_level": "HIGH",
                "key_reason": "Dados insuficientes para análise",
                "immediate_steps": ["Aguardar correção do sistema"],
                "success_probability": "BAIXA (20%)",
                "expected_timeline": "Indefinido"
            },
            "market_conditions": {
                "volatility_regime": "UNKNOWN",
                "trend_strength": "UNKNOWN", 
                "volume_trend": "UNKNOWN",
                "fear_greed_index": "UNKNOWN",
                "btc_correlation": "UNKNOWN",
                "overall_sentiment": "UNKNOWN"
            },
            "warnings": [
                {
                    "type": "SYSTEM_ERROR",
                    "severity": "HIGH",
                    "message": "Erro na análise de estratégias",
                    "recommendation": "Não tomar decisões até correção",
                    "icon": "🚫"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
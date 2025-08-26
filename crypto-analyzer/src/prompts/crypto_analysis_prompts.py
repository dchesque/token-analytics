"""
Specialized prompts for cryptocurrency analysis using AI
Optimized for financial analysis and trading insights
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class AnalysisType(Enum):
    """Types of analysis that can be performed"""
    TECHNICAL = "technical"
    TRADING_SIGNALS = "trading_signals"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_CONTEXT = "market_context"
    COMPARATIVE = "comparative"
    COMPREHENSIVE = "comprehensive"


class CryptoAnalysisPrompts:
    """Collection of specialized prompts for crypto analysis"""
    
    # Base system prompts for different analysis types
    SYSTEM_PROMPTS = {
        AnalysisType.TECHNICAL: """You are a professional cryptocurrency technical analyst with expertise in chart patterns, indicators, and market structure. 

Your role:
- Analyze price data, volume, and technical indicators
- Identify support/resistance levels and chart patterns  
- Provide clear technical insights based on data
- Focus on objective technical analysis, not speculation
- Always include confidence levels for your assessments

Format your response as structured JSON matching the expected schema.
Be precise, data-driven, and professional in your analysis.""",

        AnalysisType.TRADING_SIGNALS: """You are an experienced cryptocurrency trader specializing in generating actionable trading signals.

Your role:
- Generate specific buy/sell/hold recommendations
- Calculate precise entry points, stop losses, and take profits
- Assess risk-reward ratios and position sizing
- Provide clear reasoning for each recommendation
- Include confidence scores and risk warnings

IMPORTANT: Always include appropriate risk disclaimers. Trading involves significant financial risk.
Format your response as structured JSON with clear trading parameters.""",

        AnalysisType.RISK_ASSESSMENT: """You are a cryptocurrency risk management specialist focused on identifying and quantifying various types of investment risks.

Your role:
- Evaluate market, technical, fundamental, and regulatory risks
- Assess volatility, liquidity, and correlation risks
- Provide risk scores and mitigation strategies
- Consider macro-economic factors and market conditions
- Deliver actionable risk management recommendations

Focus on comprehensive risk evaluation with practical mitigation strategies.
Format your response as structured JSON with risk scores and recommendations.""",

        AnalysisType.MARKET_CONTEXT: """You are a cryptocurrency market analyst specializing in contextual market analysis and sentiment evaluation.

Your role:
- Interpret current market conditions and sentiment
- Analyze macro-economic factors affecting crypto markets
- Identify key market drivers and catalysts
- Assess institutional and retail sentiment
- Provide context for price movements and market behavior

Deliver insights that help understand the broader market environment.
Format your response as structured JSON with market context and sentiment analysis.""",

        AnalysisType.COMPARATIVE: """You are a cryptocurrency research analyst specializing in comparative analysis between different digital assets.

Your role:
- Compare tokens across multiple dimensions (technical, fundamental, social)
- Identify relative strengths and weaknesses
- Analyze competitive positioning and market dynamics
- Provide rankings and relative value assessments
- Suggest portfolio allocation considerations

Deliver objective comparative insights to inform investment decisions.
Format your response as structured JSON with comparative metrics and rankings."""
    }
    
    # User prompts for different analysis types
    USER_PROMPTS = {
        AnalysisType.TECHNICAL: """Analyze the technical aspects of {token_name} ({token_symbol}) based on the following market data:

**Current Price Data:**
- Current Price: ${current_price}
- 24h Change: {price_change_24h}%
- 24h High: ${high_24h}
- 24h Low: ${low_24h}
- 24h Volume: ${volume_24h}
- Market Cap: ${market_cap}
- Market Cap Rank: #{market_cap_rank}

**Additional Market Metrics:**
{additional_metrics}

**Social/Development Data:**
{social_data}

Please provide a comprehensive technical analysis including:

1. **Price Action Analysis**
   - Current trend direction and strength
   - Key support and resistance levels
   - Important price zones and psychological levels

2. **Technical Indicators**
   - Volume analysis and trends
   - Momentum indicators interpretation
   - Moving average positions and crossovers

3. **Chart Patterns**
   - Identify any significant chart patterns
   - Pattern completion targets and implications
   - Timeframe considerations

4. **Technical Outlook**
   - Short-term (1-7 days) technical bias
   - Medium-term (1-4 weeks) expectations
   - Key levels to watch for trend changes

Provide specific price levels and confidence scores for your analysis.""",

        AnalysisType.TRADING_SIGNALS: """Generate actionable trading signals for {token_name} ({token_symbol}) based on current market conditions:

**Current Market Data:**
- Price: ${current_price}
- 24h Change: {price_change_24h}%
- Volume: ${volume_24h}
- Market Cap: ${market_cap}
- Volatility: {volatility_metrics}

**Technical Context:**
{technical_context}

**Market Conditions:**
{market_conditions}

Please provide specific trading recommendations including:

1. **Primary Recommendation**
   - Action: BUY/SELL/HOLD
   - Confidence Level: (0-100%)
   - Reasoning: Clear justification for the recommendation

2. **Entry Strategy** (if BUY/SELL recommended)
   - Optimal entry price range
   - Entry timing considerations
   - DCA strategy if applicable

3. **Risk Management**
   - Stop loss level and rationale
   - Take profit targets (multiple levels)
   - Position size recommendation (% of portfolio)
   - Risk-reward ratio

4. **Time Horizon**
   - Expected holding period
   - Key dates/events to monitor
   - Exit conditions

5. **Risk Warnings**
   - Specific risks for this trade
   - Market conditions that could invalidate the signal

DISCLAIMER: This is not financial advice. Always do your own research and risk management.""",

        AnalysisType.RISK_ASSESSMENT: """Conduct a comprehensive risk assessment for {token_name} ({token_symbol}):

**Token Information:**
- Current Price: ${current_price}
- Market Cap: ${market_cap} (Rank: #{market_cap_rank})
- 24h Volume: ${volume_24h}
- Recent Performance: {performance_data}

**Market Context:**
{market_context}

**Technical Data:**
{technical_data}

**Fundamental Information:**
{fundamental_data}

Please assess the following risk categories:

1. **Market Risk (Score: /10)**
   - Price volatility assessment
   - Liquidity risk evaluation
   - Market correlation analysis
   - Beta relative to Bitcoin/market

2. **Technical Risk (Score: /10)**
   - Chart pattern risks
   - Support/resistance breakdown risks
   - Technical indicator warnings
   - Momentum and trend risks

3. **Fundamental Risk (Score: /10)**
   - Project viability and development activity
   - Team and governance risks
   - Competition and market positioning
   - Technology and security risks

4. **Regulatory Risk (Score: /10)**
   - Regulatory compliance status
   - Geographic regulatory exposure
   - Potential regulatory changes impact
   - Legal and compliance risks

5. **Liquidity Risk (Score: /10)**
   - Trading volume sustainability
   - Market depth analysis
   - Exchange distribution risk
   - Slippage potential for large orders

**Risk Mitigation Strategies:**
- Specific actions to reduce identified risks
- Portfolio diversification recommendations
- Position sizing guidelines
- Monitoring and adjustment triggers

**Overall Risk Score: /10**
**Investment Suitability:** Conservative/Moderate/Aggressive investors""",

        AnalysisType.MARKET_CONTEXT: """Provide comprehensive market context analysis for {token_name} ({token_symbol}):

**Current Market Data:**
- Price: ${current_price} ({price_change_24h}% 24h)
- Market Cap: ${market_cap}
- Volume: ${volume_24h}
- Market Position: {market_position}

**Broader Market Conditions:**
{market_conditions}

**Recent News and Events:**
{recent_events}

**Social Sentiment Data:**
{social_sentiment}

Analyze the following contextual factors:

1. **Market Sentiment Analysis**
   - Overall crypto market sentiment
   - Sector-specific sentiment for this token type
   - Retail vs institutional sentiment indicators
   - Social media and community sentiment

2. **Macro-Economic Context**
   - Impact of traditional market conditions
   - Federal Reserve policy and interest rates
   - Global economic factors affecting crypto
   - Currency and inflation considerations

3. **Sector and Competitive Context**
   - Performance relative to sector peers
   - Market share and competitive positioning
   - Technology adoption and innovation trends
   - Partnership and ecosystem developments

4. **Catalysts and Risk Factors**
   - Upcoming events, releases, or announcements
   - Potential positive catalysts
   - Known risk factors and potential headwinds
   - Seasonal or cyclical considerations

5. **Institutional and Whale Activity**
   - Large holder behavior analysis
   - Exchange inflow/outflow patterns
   - Institutional adoption indicators
   - Whale wallet movement analysis

**Market Context Summary:**
- Current market phase assessment
- Key factors driving price action
- Important levels and events to monitor
- Overall market health indicators""",

        AnalysisType.COMPARATIVE: """Compare {token_name} ({token_symbol}) against its peer group and the broader crypto market:

**Target Token Data:**
- Price: ${current_price}
- Market Cap: ${market_cap} (Rank: #{market_cap_rank})
- Volume: ${volume_24h}
- Performance: {performance_metrics}

**Comparison Peers:**
{peer_data}

**Market Benchmark Data:**
{benchmark_data}

Provide comparative analysis across these dimensions:

1. **Performance Comparison**
   - Relative performance vs peers (1D, 7D, 30D, YTD)
   - Volatility comparison and risk-adjusted returns
   - Volume and liquidity comparison
   - Market cap growth trajectory

2. **Technical Strength Comparison**
   - Relative technical indicators strength
   - Chart pattern quality vs peers
   - Support/resistance level strength
   - Momentum comparison

3. **Fundamental Comparison**
   - Development activity and community growth
   - Use case adoption and real-world utility
   - Team and governance quality
   - Technology and innovation leadership

4. **Market Position Analysis**
   - Market share within sector
   - Competitive advantages and moats
   - Partnership and ecosystem strength
   - Brand recognition and mindshare

5. **Risk-Reward Profile**
   - Risk-adjusted return potential
   - Downside protection vs peers
   - Upside potential comparison
   - Overall risk profile ranking

**Comparative Rankings:**
- Overall score vs peers (1-10)
- Best-in-class attributes
- Areas of underperformance
- Relative value assessment

**Portfolio Allocation Suggestion:**
- Recommended position size relative to peers
- Diversification benefits or risks
- Optimal portfolio weighting rationale"""
    }

    # Structured response schemas
    RESPONSE_SCHEMAS = {
        AnalysisType.TECHNICAL: {
            "technical_analysis": {
                "trend": {"type": "string", "enum": ["bullish", "bearish", "neutral", "sideways"]},
                "trend_strength": {"type": "number", "minimum": 0, "maximum": 10},
                "support_levels": {"type": "array", "items": {"type": "number"}},
                "resistance_levels": {"type": "array", "items": {"type": "number"}},
                "chart_patterns": {"type": "array", "items": {"type": "string"}},
                "key_indicators": {
                    "type": "object",
                    "properties": {
                        "volume_trend": {"type": "string"},
                        "momentum": {"type": "string"},
                        "moving_averages": {"type": "string"}
                    }
                },
                "technical_outlook": {
                    "short_term": {"type": "string"},
                    "medium_term": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 100}
                }
            }
        },

        AnalysisType.TRADING_SIGNALS: {
            "trading_signal": {
                "recommendation": {"type": "string", "enum": ["BUY", "SELL", "HOLD"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                "entry_price": {"type": "number"},
                "entry_range": {
                    "low": {"type": "number"},
                    "high": {"type": "number"}
                },
                "stop_loss": {"type": "number"},
                "take_profit_levels": {"type": "array", "items": {"type": "number"}},
                "position_size": {"type": "string"},
                "risk_reward_ratio": {"type": "number"},
                "time_horizon": {"type": "string"},
                "reasoning": {"type": "string"},
                "risk_factors": {"type": "array", "items": {"type": "string"}},
                "exit_conditions": {"type": "array", "items": {"type": "string"}}
            }
        },

        AnalysisType.RISK_ASSESSMENT: {
            "risk_assessment": {
                "overall_risk_score": {"type": "number", "minimum": 0, "maximum": 10},
                "risk_breakdown": {
                    "market_risk": {"type": "number", "minimum": 0, "maximum": 10},
                    "technical_risk": {"type": "number", "minimum": 0, "maximum": 10},
                    "fundamental_risk": {"type": "number", "minimum": 0, "maximum": 10},
                    "regulatory_risk": {"type": "number", "minimum": 0, "maximum": 10},
                    "liquidity_risk": {"type": "number", "minimum": 0, "maximum": 10}
                },
                "risk_factors": {"type": "array", "items": {"type": "string"}},
                "mitigation_strategies": {"type": "array", "items": {"type": "string"}},
                "investment_suitability": {"type": "string", "enum": ["conservative", "moderate", "aggressive"]},
                "position_sizing": {"type": "string"}
            }
        }
    }

    @classmethod
    def get_system_prompt(cls, analysis_type: AnalysisType) -> str:
        """Get system prompt for analysis type"""
        return cls.SYSTEM_PROMPTS.get(analysis_type, cls.SYSTEM_PROMPTS[AnalysisType.TECHNICAL])

    @classmethod
    def get_user_prompt(cls, analysis_type: AnalysisType, **kwargs) -> str:
        """Get formatted user prompt for analysis type"""
        template = cls.USER_PROMPTS.get(analysis_type, cls.USER_PROMPTS[AnalysisType.TECHNICAL])
        
        # Format the template with provided data
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # If formatting fails, return template with available data
            available_data = {k: v for k, v in kwargs.items() if v is not None}
            try:
                return template.format(**available_data)
            except:
                return template

    @classmethod
    def format_token_data(cls, token_data: Dict[str, Any]) -> Dict[str, str]:
        """Format token data for prompt templates"""
        formatted = {}
        
        # Basic formatting
        for key, value in token_data.items():
            if value is None:
                formatted[key] = "N/A"
            elif isinstance(value, (int, float)):
                if key.endswith('_price') or key.startswith('price_'):
                    formatted[key] = f"{value:.6f}" if value < 1 else f"{value:.2f}"
                elif key.endswith('_cap') or key.endswith('_volume'):
                    formatted[key] = cls._format_large_number(value)
                else:
                    formatted[key] = str(value)
            else:
                formatted[key] = str(value)
        
        return formatted

    @classmethod
    def _format_large_number(cls, value: float) -> str:
        """Format large numbers in readable format"""
        if value >= 1e12:
            return f"{value/1e12:.2f}T"
        elif value >= 1e9:
            return f"{value/1e9:.2f}B"
        elif value >= 1e6:
            return f"{value/1e6:.2f}M"
        elif value >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:.2f}"

    @classmethod
    def create_comprehensive_prompt(cls, token_data: Dict[str, Any], 
                                  analysis_types: List[AnalysisType]) -> tuple:
        """Create a comprehensive analysis prompt combining multiple types"""
        
        if AnalysisType.COMPREHENSIVE in analysis_types:
            # Use comprehensive analysis
            system_prompt = """You are a senior cryptocurrency analyst with expertise across technical analysis, trading, risk management, and market research.

Your role is to provide comprehensive, multi-dimensional analysis covering:
- Technical analysis and chart patterns
- Trading signals and actionable recommendations  
- Risk assessment and management strategies
- Market context and sentiment analysis
- Comparative positioning vs peers

Deliver professional, data-driven analysis with specific actionable insights.
Format your response as structured JSON with all requested analysis sections."""

            formatted_data = cls.format_token_data(token_data)
            
            user_prompt = f"""Provide comprehensive analysis for {formatted_data.get('token_name', 'Unknown')} ({formatted_data.get('token_symbol', 'N/A')}):

**Current Market Data:**
{cls._format_market_data_section(formatted_data)}

**Analysis Required:**
1. Technical Analysis - trends, patterns, key levels
2. Trading Signals - buy/sell/hold with specific levels  
3. Risk Assessment - comprehensive risk evaluation
4. Market Context - sentiment and macro factors
5. Summary - key takeaways and recommendations

Please provide detailed analysis for each section with specific data points, confidence levels, and actionable insights."""
            
        else:
            # Combine multiple specific analysis types
            system_prompts = [cls.get_system_prompt(at) for at in analysis_types]
            system_prompt = "\n\n".join(system_prompts)
            
            user_prompts = []
            formatted_data = cls.format_token_data(token_data)
            
            for analysis_type in analysis_types:
                user_prompts.append(cls.get_user_prompt(analysis_type, **formatted_data))
            
            user_prompt = "\n\n---\n\n".join(user_prompts)
        
        return system_prompt, user_prompt

    @classmethod
    def _format_market_data_section(cls, data: Dict[str, str]) -> str:
        """Format market data section for prompts"""
        return f"""
- Current Price: ${data.get('current_price', 'N/A')}
- 24h Change: {data.get('price_change_24h', 'N/A')}%
- Market Cap: ${data.get('market_cap', 'N/A')}
- Volume: ${data.get('volume_24h', 'N/A')}
- Market Rank: #{data.get('market_cap_rank', 'N/A')}
"""

    @classmethod
    def optimize_prompt_for_model(cls, prompt: str, model_config) -> str:
        """Optimize prompt length and complexity for specific model"""
        max_tokens = model_config.max_tokens if model_config else 4096
        
        # If prompt is too long, truncate intelligently
        if len(prompt) > max_tokens * 3:  # Rough token estimation
            lines = prompt.split('\n')
            truncated_lines = []
            current_length = 0
            
            for line in lines:
                if current_length + len(line) > max_tokens * 2.5:
                    break
                truncated_lines.append(line)
                current_length += len(line)
            
            prompt = '\n'.join(truncated_lines)
            prompt += "\n\n[Note: Analysis data truncated to fit model context limits]"
        
        return prompt

    @classmethod
    def get_response_schema(cls, analysis_type: AnalysisType) -> Optional[Dict]:
        """Get JSON schema for expected response format"""
        return cls.RESPONSE_SCHEMAS.get(analysis_type)
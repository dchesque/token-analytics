import time
from fetcher import DataFetcher
from social_analyzer import SocialAnalyzer
from config import MIN_MARKET_CAP, MIN_VOLUME, MIN_AGE_DAYS, STRONG_BUY_SCORE, RESEARCH_SCORE

# AI Integration imports
try:
    from ai_openrouter_agent import create_ai_agent, quick_analysis, AIResponse
    from ai_config import AIConfig, AITier
    from prompts.crypto_analysis_prompts import AnalysisType
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI features not available: {e}")
    AI_AVAILABLE = False

# Estrutura de mercado crypto
MARKET_STRUCTURE = {
    'MAJORS': {
        'tokens': ['BTC', 'ETH'],
        'description': 'Ativos principais do mercado',
        'typical_allocation': '40-60% do portfolio crypto'
    },
    'LARGE_CAPS': {
        'tokens': ['BNB', 'SOL', 'XRP', 'ADA'],
        'description': 'Top 10 estabelecidos',
        'typical_allocation': '20-30% do portfolio'
    },
    'MID_CAPS': {
        'tokens': ['MATIC', 'LINK', 'UNI', 'ARB'],
        'description': 'Projetos sólidos com potencial',
        'typical_allocation': '10-20% do portfolio'
    },
    'SMALL_CAPS': {
        'tokens': ['Projetos inovadores menores'],
        'description': 'Alto risco, alto retorno potencial',
        'typical_allocation': '5-10% do portfolio'
    },
    'SPECULATIVE': {
        'tokens': ['Memes', 'Micro caps'],
        'description': 'Extremamente volátil',
        'typical_allocation': '0-5% do portfolio'
    }
}

class CryptoAnalyzer:
    def __init__(self, enable_ai=True, user_tier="budget"):
        self.fetcher = DataFetcher()
        self.debug_mode = False  # Desabilitado para evitar problemas Unicode no Windows
        
        # AI Integration
        self.ai_enabled = enable_ai and AI_AVAILABLE and AIConfig.is_feature_enabled('ai_analysis')
        self.ai_agent = None
        self.user_tier = user_tier
        
        if self.ai_enabled:
            try:
                self.ai_agent = create_ai_agent(user_tier)
            except Exception as e:
                print(f"Failed to initialize AI agent: {e}")
                self.ai_enabled = False
    
    def analyze(self, token_query, enable_ai=None, ai_analysis_type=None):
        """
        Analyze token with optional AI enhancement
        
        Args:
            token_query: Token symbol or name to analyze
            enable_ai: Override AI setting for this analysis
            ai_analysis_type: Type of AI analysis ('technical', 'trading_signals', 'risk_assessment', etc.)
        """
        token_id = self.fetcher.search_token(token_query)
        if not token_id:
            return {
                'token': token_query,
                'error': 'Token não encontrado',
                'passed_elimination': False,
                'score': 0,
                'decision': 'TOKEN NÃO ENCONTRADO'
            }
        
        token_data = self.fetcher.get_token_data(token_id)
        if not token_data:
            return {
                'token': token_query,
                'error': 'Erro ao buscar dados do token',
                'passed_elimination': False,
                'score': 0,
                'decision': 'ERRO AO BUSCAR DADOS'
            }
        
        elimination_result = self.check_elimination(token_data)
        if not elimination_result['passed']:
            return {
                'token': token_data['symbol'],
                'token_name': token_data['name'],
                'passed_elimination': False,
                'elimination_reasons': elimination_result['reasons'],
                'score': 0,
                'decision': 'REJEITADO',
                'data': token_data
            }
        
        score_result = self.calculate_score(token_data)
        market_context = self.check_market_context()
        decision = self.make_decision(score_result['score'], market_context, token_data)
        
        # Adicionar análise técnica de momentum
        momentum_analysis = self.analyze_price_momentum(token_id, token_data)
        
        # Preparar resultado base
        base_result = {
            'token': token_data['symbol'],
            'token_name': token_data['name'],
            'passed_elimination': True,
            'score': score_result['score'],
            'score_breakdown': score_result['breakdown'],
            'classification': decision['final_decision'],
            'classification_info': decision['classification_info'],
            'market_sentiment': decision['market_sentiment'],
            'strengths': decision['strengths'],
            'weaknesses': decision['weaknesses'],
            'fear_greed': decision['fear_greed'],
            'market_context': market_context,
            'price': token_data['price'],
            'market_cap': token_data['market_cap'],
            'volume': token_data['volume'],
            'price_change_24h': token_data['price_change_24h'],
            'price_change_7d': token_data['price_change_7d'],
            'price_change_30d': token_data['price_change_30d'],
            'momentum_analysis': momentum_analysis,
            'data': token_data,
            # Campos adicionais para DisplayManager
            'decision': decision['final_decision'],
            'analysis': {
                'strengths': decision['strengths'],
                'weaknesses': decision['weaknesses'],
                'risks': []  # Para compatibilidade com save_report
            }
        }
        
        # Adicionar análise AI se habilitada
        if enable_ai is True or (enable_ai is None and self.ai_enabled):
            ai_result = self.analyze_with_ai(token_data, ai_analysis_type)
            if ai_result:
                base_result['ai_analysis'] = ai_result
                base_result['ai_enabled'] = True
            else:
                base_result['ai_enabled'] = False
                base_result['ai_error'] = "AI analysis failed"
        else:
            base_result['ai_enabled'] = False
        
        return base_result
    
    def check_elimination(self, data):
        reasons = []
        
        if data['market_cap'] < MIN_MARKET_CAP:
            reasons.append(f"Market cap muito baixo: ${data['market_cap']:,.0f} < ${MIN_MARKET_CAP:,.0f}")
        
        if data['volume'] < MIN_VOLUME:
            reasons.append(f"Volume muito baixo: ${data['volume']:,.0f} < ${MIN_VOLUME:,.0f}")
        
        if data['age_days'] < MIN_AGE_DAYS:
            reasons.append(f"Token muito novo: {data['age_days']} dias < {MIN_AGE_DAYS} dias")
        
        if data['volume'] == 0 or data['market_cap'] == 0:
            reasons.append("Sem liquidez verificável")
        
        return {
            'passed': len(reasons) == 0,
            'reasons': reasons
        }
    
    def calculate_score(self, data):
        score = 0
        breakdown = {}
        
        # Debug information
        symbol = data.get('symbol', 'UNK')
        market_cap = data.get('market_cap', 0)
        market_cap_rank = data.get('market_cap_rank', 9999)
        volume = data.get('volume', 0)
        
        # Comentado temporariamente para evitar problemas Unicode no Windows
        # print(f"\nDEBUG SCORING - {symbol}")
        # print(f"   Market Cap: ${market_cap:,.0f}")
        # print(f"   Rank: #{market_cap_rank}")
        # print(f"   Volume 24h: ${volume:,.0f}")
        
        # 1. MARKET CAP SCORING (0-2 pontos) - Peso fundamental
        if market_cap >= 100_000_000_000:  # >= $100B (Bitcoin, Ethereum)
            breakdown['market_cap'] = 2
            score += 2
            # print(f"   OK Market Cap: 2/2 pontos (>= $100B)")
        elif market_cap >= 10_000_000_000:  # >= $10B (Top ~20)
            breakdown['market_cap'] = 2
            score += 2
            if self.debug_mode: print(f"   OK Market Cap: 2/2 pontos (>= $10B)")
        elif market_cap >= 1_000_000_000:  # >= $1B (Top ~100)
            breakdown['market_cap'] = 1
            score += 1
            if self.debug_mode: print(f"   OK Market Cap: 1/2 pontos (>= $1B)")
        else:
            breakdown['market_cap'] = 0
            if self.debug_mode: print(f"   Market Cap: 0/2 pontos (< $1B)")
        
        # 2. LIQUIDEZ (0-2 pontos) - Baseado em volume e ranking
        if market_cap > 0:
            volume_ratio = volume / market_cap
            if market_cap_rank <= 50 and volume > 1_000_000_000:  # Top 50 + >$1B volume
                breakdown['liquidity'] = 2
                score += 2
                if self.debug_mode: print(f"   OK Liquidez: 2/2 pontos (Top 50 + alto volume)")
            elif volume_ratio > 0.02 or volume > 500_000_000:  # >2% ratio OU >$500M volume
                breakdown['liquidity'] = 1
                score += 1
                if self.debug_mode: print(f"   OK Liquidez: 1/2 pontos (boa liquidez)")
            else:
                breakdown['liquidity'] = 0
                if self.debug_mode: print(f"   Liquidez: 0/2 pontos (baixa liquidez)")
        else:
            breakdown['liquidity'] = 0
            if self.debug_mode: print(f"   Liquidez: 0/2 pontos (sem dados)")
        
        # 3. DESENVOLVIMENTO (0-2 pontos) - Com fallback para tokens estabelecidos
        github_commits = data.get('github_commits', 0)
        github_stars = data.get('github_stars', 0)
        
        # Tokens blue-chip (Bitcoin, Ethereum) podem ter desenvolvimento em repositórios múltiplos
        if market_cap_rank <= 10 and market_cap >= 50_000_000_000:  # Top 10 + >$50B
            breakdown['development'] = 2  # Assume desenvolvimento ativo para blue chips
            score += 2
            if self.debug_mode: print(f"   OK Desenvolvimento: 2/2 pontos (blue chip estabelecido)")
        elif github_commits > 50 or github_stars > 1000:
            breakdown['development'] = 2
            score += 2
            if self.debug_mode: print(f"   OK Desenvolvimento: 2/2 pontos (ativo no GitHub)")
        elif github_commits > 10 or github_stars > 100:
            breakdown['development'] = 1
            score += 1
            if self.debug_mode: print(f"   OK Desenvolvimento: 1/2 pontos (desenvolvimento moderado)")
        elif market_cap_rank <= 100:  # Top 100 sem dados GitHub = desenvolvimento possível
            breakdown['development'] = 1
            score += 1
            if self.debug_mode: print(f"   OK Desenvolvimento: 1/2 pontos (Top 100, desenvolvimento inferido)")
        else:
            breakdown['development'] = 0
            if self.debug_mode: print(f"   Desenvolvimento: 0/2 pontos (sem atividade)")
        
        # 4. COMUNIDADE (0-2 pontos) - Com ajustes para tokens estabelecidos
        twitter_followers = data.get('twitter_followers', 0)
        reddit_subscribers = data.get('reddit_subscribers', 0)
        
        total_community = twitter_followers + reddit_subscribers
        
        if market_cap_rank <= 5:  # Top 5 = comunidade massiva mesmo sem dados
            breakdown['community'] = 2
            score += 2
            if self.debug_mode: print(f"   OK Comunidade: 2/2 pontos (Top 5 global)")
        elif total_community > 500_000 or twitter_followers > 300_000:
            breakdown['community'] = 2
            score += 2
            if self.debug_mode: print(f"   OK Comunidade: 2/2 pontos (comunidade grande)")
        elif total_community > 50_000 or twitter_followers > 30_000 or market_cap_rank <= 50:
            breakdown['community'] = 1
            score += 1
            if self.debug_mode: print(f"   OK Comunidade: 1/2 pontos (comunidade boa)")
        else:
            breakdown['community'] = 0
            if self.debug_mode: print(f"   Comunidade: 0/2 pontos (comunidade pequena)")
        
        # 5. PERFORMANCE E ESTABILIDADE (0-2 pontos)
        price_change_30d = data.get('price_change_30d', 0)
        age_days = data.get('age_days', 0)
        
        # Tokens estabelecidos (>2 anos) ganham pontos por estabilidade
        if age_days > 730:  # >2 anos
            if price_change_30d > -30:  # Não está em colapso
                breakdown['performance'] = 1
                score += 1
                if self.debug_mode: print(f"   OK Performance: 1/2 pontos (token estavel, +{price_change_30d:.1f}%)")
                
                # Bonus para performance positiva
                if price_change_30d > 5:
                    breakdown['performance'] = 2
                    score += 1  # +1 adicional
                    if self.debug_mode: print(f"   OK Performance: 2/2 pontos (boa performance)")
            else:
                breakdown['performance'] = 0
                if self.debug_mode: print(f"   Performance: 0/2 pontos (queda severa: {price_change_30d:.1f}%)")
        else:
            # Tokens novos precisam de performance positiva
            if price_change_30d > 10:
                breakdown['performance'] = 2
                score += 2
                if self.debug_mode: print(f"   OK Performance: 2/2 pontos (token novo com boa performance)")
            elif price_change_30d > 0:
                breakdown['performance'] = 1
                score += 1
                if self.debug_mode: print(f"   OK Performance: 1/2 pontos (performance positiva)")
            else:
                breakdown['performance'] = 0
                if self.debug_mode: print(f"   Performance: 0/2 pontos (performance negativa)")
        
        # AJUSTE FINAL PARA BLUE CHIPS
        # Bitcoin e Ethereum devem ter score mínimo de 7/10
        if symbol.upper() in ['BTC', 'BITCOIN'] and score < 7:
            adjustment = 7 - score
            breakdown['blue_chip_adjustment'] = adjustment
            score = 7
            if self.debug_mode: print(f"   AJUSTE Bitcoin: +{adjustment} pontos (score minimo 7/10)")
        elif symbol.upper() in ['ETH', 'ETHEREUM'] and score < 7:
            adjustment = 7 - score
            breakdown['blue_chip_adjustment'] = adjustment
            score = 7
            if self.debug_mode: print(f"   AJUSTE Ethereum: +{adjustment} pontos (score minimo 7/10)")
        
        if self.debug_mode:
            print(f"   SCORE FINAL: {score}/10")
        
        return {
            'score': min(score, 10),  # Máximo 10
            'breakdown': breakdown
        }
    
    def generate_analysis_points(self, data):
        """Gera pontos fortes e fracos baseados nos dados reais"""
        
        strengths = []
        weaknesses = []
        
        # Market Cap Analysis
        market_cap = data.get('market_cap', 0)
        rank = data.get('market_cap_rank', 999)
        symbol = data.get('symbol', '').upper()
        
        if rank <= 5:
            strengths.append(f"Top {rank} em market cap global")
        elif rank <= 20:
            strengths.append(f"Top {rank} - projeto estabelecido")
        elif rank <= 100:
            strengths.append(f"Rank #{rank} - boa posição")
        elif rank > 500:
            weaknesses.append(f"Rank #{rank} - fora do top 500")
        
        if market_cap > 100_000_000_000:  # > $100B
            strengths.append(f"Market cap gigante: ${market_cap/1_000_000_000:.0f}B")
        elif market_cap > 10_000_000_000:  # > $10B
            strengths.append(f"Market cap alto: ${market_cap/1_000_000_000:.1f}B")
        elif market_cap < 100_000_000:  # < $100M
            weaknesses.append(f"Market cap baixo: ${market_cap/1_000_000:.1f}M")
        
        # Liquidez
        volume = data.get('volume', 0)
        if market_cap > 0:
            volume_ratio = volume / market_cap
            
            if rank <= 50 and volume > 1_000_000_000:  # Top 50 + >$1B volume
                strengths.append(f"Excelente liquidez: ${volume/1_000_000_000:.1f}B volume diário")
            elif volume_ratio > 0.05:
                strengths.append(f"Boa liquidez: {volume_ratio:.1%} do market cap")
            elif volume_ratio < 0.01:
                weaknesses.append(f"Baixa liquidez: {volume_ratio:.2%} do market cap")
        
        # Desenvolvimento
        github_commits = data.get('github_commits', 0)
        github_stars = data.get('github_stars', 0)
        
        # Casos especiais para Bitcoin/Ethereum
        if symbol in ['BTC', 'BITCOIN']:
            strengths.append("Desenvolvimento contínuo e estabelecido")
        elif symbol in ['ETH', 'ETHEREUM']:
            strengths.append("Desenvolvimento muito ativo (Ethereum ecosystem)")
        elif github_commits > 100:
            strengths.append(f"Desenvolvimento muito ativo: {github_commits} commits/mês")
        elif github_commits > 50:
            strengths.append(f"Desenvolvimento ativo: {github_commits} commits/mês")
        elif github_commits < 10 and github_stars < 100 and rank > 100:
            weaknesses.append("Pouca atividade de desenvolvimento recente")
        
        # Comunidade
        twitter_followers = data.get('twitter_followers', 0)
        reddit_subscribers = data.get('reddit_subscribers', 0)
        
        # Bitcoin tem comunidade especial
        if symbol in ['BTC', 'BITCOIN']:
            strengths.append("Maior comunidade do mercado crypto")
        elif symbol in ['ETH', 'ETHEREUM']:
            strengths.append("Segunda maior comunidade crypto")
        elif twitter_followers > 1_000_000 or reddit_subscribers > 500_000:
            strengths.append(f"Comunidade massiva: {twitter_followers:,} no Twitter")
        elif twitter_followers > 100_000 or reddit_subscribers > 50_000:
            strengths.append(f"Comunidade forte: {twitter_followers:,} seguidores")
        elif twitter_followers < 10_000 and reddit_subscribers < 5_000 and rank > 100:
            weaknesses.append("Comunidade pequena")
        
        # Performance de preço
        price_30d = data.get('price_change_30d', 0)
        price_7d = data.get('price_change_7d', 0)
        age_days = data.get('age_days', 0)
        
        if price_30d > 30:
            strengths.append(f"Alta volatilidade positiva observada: +{price_30d:.1f}% (30d)")
        elif price_30d > 10:
            strengths.append(f"Performance positiva recente: +{price_30d:.1f}% (30d)")
        elif price_30d < -50:
            weaknesses.append(f"Alta volatilidade negativa: {price_30d:.1f}% (30d)")
        elif price_30d < -20:
            weaknesses.append(f"Volatilidade negativa observada: {price_30d:.1f}% (30d)")
        
        # Estabilidade/Idade
        if age_days > 2000:  # > ~5.5 anos
            strengths.append(f"Token muito estabelecido ({age_days//365} anos)")
        elif age_days > 730:  # > 2 anos
            strengths.append(f"Token estabelecido ({age_days//365:.1f} anos)")
        elif age_days < 365:  # < 1 ano
            weaknesses.append(f"Token relativamente novo ({age_days} dias)")
        
        # Volatilidade
        if abs(price_7d) > 40:
            weaknesses.append(f"Alta volatilidade: {price_7d:+.1f}% (7d)")
        
        return strengths[:5], weaknesses[:3]  # Limita para não poluir
    
    def check_market_context(self):
        fear_greed = self.fetcher.get_fear_greed()
        
        if not fear_greed:
            return {
                'fear_greed_index': 50,
                'market_sentiment': 'Neutral',
                'recommendation': 'Dados indisponíveis'
            }
        
        fg_value = fear_greed['value']
        
        if fg_value < 25:
            sentiment = 'Extreme Fear'
            recommendation = 'Momento pode ser bom para compra'
        elif fg_value < 45:
            sentiment = 'Fear'
            recommendation = 'Cautela recomendada'
        elif fg_value < 55:
            sentiment = 'Neutral'
            recommendation = 'Mercado equilibrado'
        elif fg_value < 75:
            sentiment = 'Greed'
            recommendation = 'Cautela com FOMO'
        else:
            sentiment = 'Extreme Greed'
            recommendation = 'Alto risco, considere aguardar'
        
        return {
            'fear_greed_index': fg_value,
            'market_sentiment': sentiment,
            'recommendation': recommendation
        }
    
    def classify_token(self, score, market_data):
        """Classifica o token usando terminologia crypto correta"""
        
        market_cap = market_data.get('market_cap', 0)
        rank = market_data.get('market_cap_rank', 999)
        token_id = market_data.get('id', '').lower()
        categories = market_data.get('categories', [])
        
        # Classificação especial para Majors
        if token_id in ['bitcoin', 'ethereum']:
            classification = "MAJOR"
            description = "Ativo principal do mercado crypto"
            emoji = "MAJOR"
            risk_level = "Estabelecido"
        
        # Por market cap rank
        elif rank <= 10:
            classification = "LARGE CAP"
            description = "Top 10 do mercado"
            emoji = "LARGE"
            risk_level = "Baixo-Médio"
        
        elif rank <= 50:
            classification = "MID CAP"
            description = "Projeto estabelecido"
            emoji = "⭐"
            risk_level = "Médio"
        
        elif rank <= 100:
            classification = "SMALL CAP"
            description = "Capitalização menor"
            emoji = "🔹"
            risk_level = "Médio-Alto"
        
        elif rank <= 500:
            classification = "MICRO CAP"
            description = "Projeto pequeno"
            emoji = "🔸"
            risk_level = "Alto"
        
        else:
            classification = "NANO CAP"
            description = "Projeto muito pequeno"
            emoji = "⚡"
            risk_level = "Muito Alto"
        
        # Override para categorias especiais
        if 'meme-token' in categories or token_id in ['dogecoin', 'shiba-inu', 'pepe', 'floki', 'bonk']:
            classification = "MEME COIN"
            description = "Token meme/comunidade"
            emoji = "🐕"
            risk_level = "Especulativo"
        
        elif 'stablecoin' in categories or token_id in ['tether', 'usd-coin', 'dai', 'frax']:
            classification = "STABLECOIN"
            description = "Moeda estável"
            emoji = "💵"
            risk_level = "Baixo"
        
        elif 'defi' in categories or 'decentralized-finance' in categories:
            classification = f"DEFI {classification}"
            description = f"DeFi - {description}"
            emoji = "🏦"
        
        elif 'layer-2' in categories or token_id in ['arbitrum', 'optimism', 'polygon-pos']:
            classification = "LAYER 2"
            description = "Solução de escalabilidade"
            emoji = "⚡"
            risk_level = "Médio"
        
        # Qualidade baseada no score
        if score >= 9:
            quality = "Fundamentos Excelentes"
        elif score >= 7:
            quality = "Fundamentos Sólidos"
        elif score >= 5:
            quality = "Fundamentos Medianos"
        elif score >= 3:
            quality = "Fundamentos Fracos"
        else:
            quality = "Fundamentos Muito Fracos"
        
        return {
            'classification': classification,
            'description': description,
            'quality': quality,
            'risk_level': risk_level,
            'emoji': emoji,
            'score': score,
            'rank': rank,
            'market_cap': market_cap,
            'context': f"Rank #{rank}" if rank and rank != 999 else "N/A"  # ADICIONA ESTE CAMPO
        }
    
    def analyze_major_metrics(self, token_id, data):
        """Análise especial para Bitcoin e Ethereum"""
        
        if token_id == 'bitcoin':
            return {
                'dominance': data.get('market_cap_percentage', {}).get('btc', 0),
                'hash_rate': 'Rede mais segura (PoW)',
                'adoption': 'Reserva de valor digital',
                'narrative': 'Digital Gold',
                'key_metrics': [
                    f"Dominância: {data.get('market_data', {}).get('market_cap_dominance', 0):.1f}%",
                    "Halving a cada 4 anos",
                    "Supply máximo: 21M BTC",
                    "Rede desde 2009"
                ]
            }
        
        elif token_id == 'ethereum':
            return {
                'dominance': data.get('market_cap_percentage', {}).get('eth', 0),
                'ecosystem': 'Maior ecossistema DeFi/NFT',
                'adoption': 'Plataforma de smart contracts',
                'narrative': 'World Computer',
                'key_metrics': [
                    f"TVL em DeFi: ${data.get('defi_tvl', 0)/1e9:.1f}B",
                    "Proof of Stake desde 2022",
                    "Gas fees variáveis",
                    "L2s para escalabilidade"
                ]
            }
        
        return None
    
    def display_token_classification(self, classification_data):
        """Mostra classificação apropriada do token"""
        
        # Cores por categoria
        colors = {
            'MAJOR': 'bright_yellow',
            'LARGE CAP': 'bright_blue',
            'MID CAP': 'blue',
            'SMALL CAP': 'cyan',
            'MICRO CAP': 'magenta',
            'NANO CAP': 'red',
            'MEME COIN': 'yellow',
            'STABLECOIN': 'green',
            'LAYER 2': 'bright_cyan',
            'DEFI': 'bright_magenta'
        }
        
        content = f"""
{classification_data['emoji']} CLASSIFICAÇÃO: {classification_data['classification']}
📝 {classification_data['description']}
⚖️ Nível de Risco: {classification_data['risk_level']}
📊 Score de Fundamentos: {classification_data['score']}/10
🏆 Ranking: #{classification_data['rank']}

💰 Market Cap: ${classification_data['market_cap']/1e9:.1f}B
📈 {classification_data['quality']}
"""
        
        # Se for Major, adiciona métricas especiais
        if classification_data['classification'] == 'MAJOR':
            if major_metrics := classification_data.get('major_metrics'):
                content += f"\n🔑 MÉTRICAS PRINCIPAIS:\n"
                for metric in major_metrics['key_metrics']:
                    content += f"• {metric}\n"
        
        return content
    
    def analyze_market_sentiment(self, fear_greed_value):
        """Analisa sentimento do mercado - APENAS INFORMATIVO"""
        
        if fear_greed_value < 25:
            sentiment = "Mercado em Fear Extremo"
            description = "Pessimismo máximo no mercado"
            emoji = "😱"
        elif fear_greed_value < 45:
            sentiment = "Mercado em Fear"
            description = "Sentimento negativo predominante"
            emoji = "😨"
        elif fear_greed_value < 55:
            sentiment = "Mercado Neutro"
            description = "Sentimento equilibrado"
            emoji = "😐"
        elif fear_greed_value < 75:
            sentiment = "Mercado em Greed"
            description = "Otimismo predominante"
            emoji = "😊"
        else:
            sentiment = "Mercado em Greed Extremo"
            description = "Euforia no mercado"
            emoji = "🤑"
        
        return {
            'sentiment': sentiment,
            'description': description,
            'emoji': emoji,
            'value': fear_greed_value
        }
    
    def make_decision(self, score, market_context, data):
        """Método mantido para compatibilidade - agora chama classify_token"""
        classification = self.classify_token(score, data)
        sentiment = self.analyze_market_sentiment(market_context.get('fear_greed_index', 50))
        strengths, weaknesses = self.generate_analysis_points(data)
        
        # Adiciona métricas especiais para Majors
        if classification['classification'] == 'MAJOR':
            token_id = data.get('id', '').lower()
            major_metrics = self.analyze_major_metrics(token_id, data)
            if major_metrics:
                classification['major_metrics'] = major_metrics
        
        return {
            'final_decision': classification['classification'],
            'classification_info': classification,
            'market_sentiment': sentiment,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'fear_greed': sentiment['value']
        }
    
    def analyze_multiple(self, tokens: list, delay_seconds: int = 3):
        """Analisa múltiplos tokens com delay para evitar rate limit"""
        results = []
        
        print(f"🔄 Analisando {len(tokens)} tokens com delay de {delay_seconds}s entre cada...")
        
        for i, token in enumerate(tokens):
            print(f"\n[{i+1}/{len(tokens)}] 🔍 Analisando {token.upper()}...")
            
            try:
                result = self.analyze(token)
                if result:
                    results.append(result)
                else:
                    print(f"Falha ao analisar {token}")
                    
            except Exception as e:
                print(f"Erro ao analisar {token}: {e}")
                
            # Delay entre análises (exceto no último)
            if i < len(tokens) - 1:
                print(f"⏳ Aguardando {delay_seconds}s antes do próximo token...")
                time.sleep(delay_seconds)
        
        if self.debug_mode: print(f"\nAnalise concluida: {len(results)}/{len(tokens)} tokens processados")
        return results
    
    def analyze_price_momentum(self, token_id: str, current_data: dict):
        """Analisa momentum de preço - NÃO É RECOMENDAÇÃO"""
        
        print(f"📈 Analisando momentum técnico de {token_id}...")
        
        # Busca histórico
        history = self.fetcher.get_price_history(token_id, 90)
        
        if not history or len(history['prices']) < 14:
            return {
                'trend': 'INDEFINIDO',
                'emoji': '❓',
                'color': 'white',
                'score': 0,
                'signals': ['Dados históricos insuficientes'],
                'indicators': {},
                'technical_analysis': ['Não foi possível realizar análise técnica']
            }
        
        current_price = current_data.get('price', history['current_price'])
        
        # Calcula indicadores simples
        indicators = {
            'price_vs_30d_avg': (current_price / history['avg_30d'] - 1) * 100 if history['avg_30d'] else 0,
            'price_vs_7d_avg': (current_price / history['avg_7d'] - 1) * 100 if history['avg_7d'] else 0,
            'position_in_range': (current_price - history['min_90d']) / (history['max_90d'] - history['min_90d']) * 100 if (history['max_90d'] - history['min_90d']) > 0 else 50,
            'distance_from_ath': (current_price / history['max_90d'] - 1) * 100 if history['max_90d'] else 0,
            'distance_from_atl': (current_price / history['min_90d'] - 1) * 100 if history['min_90d'] else 0
        }
        
        # Análise de momentum
        momentum_score = 0
        signals = []
        
        # Tendência de curto prazo (7d)
        if indicators['price_vs_7d_avg'] > 5:
            momentum_score += 2
            signals.append(f"Momentum positivo: +{indicators['price_vs_7d_avg']:.1f}% vs média 7d")
        elif indicators['price_vs_7d_avg'] < -5:
            momentum_score -= 2
            signals.append(f"Momentum negativo: {indicators['price_vs_7d_avg']:.1f}% vs média 7d")
        else:
            signals.append(f"Lateralizado: {indicators['price_vs_7d_avg']:+.1f}% vs média 7d")
        
        # Tendência de médio prazo (30d)
        if indicators['price_vs_30d_avg'] > 10:
            momentum_score += 3
            signals.append(f"Tendência de alta: +{indicators['price_vs_30d_avg']:.1f}% vs média 30d")
        elif indicators['price_vs_30d_avg'] < -10:
            momentum_score -= 3
            signals.append(f"Tendência de baixa: {indicators['price_vs_30d_avg']:.1f}% vs média 30d")
        else:
            signals.append(f"Consolidação: {indicators['price_vs_30d_avg']:+.1f}% vs média 30d")
        
        # Posição no range de 90d
        if indicators['position_in_range'] > 80:
            momentum_score += 1
            signals.append(f"Próximo da máxima: {indicators['position_in_range']:.0f}% do range 90d")
        elif indicators['position_in_range'] < 20:
            momentum_score -= 1
            signals.append(f"Próximo da mínima: {indicators['position_in_range']:.0f}% do range 90d")
        else:
            signals.append(f"Meio do range: {indicators['position_in_range']:.0f}% do range 90d")
        
        # RSI simplificado (ganhos vs perdas nos últimos 14 dias)
        if len(history['prices']) >= 14:
            gains = []
            losses = []
            for i in range(1, 15):
                change = history['prices'][-i] - history['prices'][-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                
                if rsi > 70:
                    signals.append(f"RSI alto: {rsi:.0f} (sobrecomprado)")
                    momentum_score -= 1
                elif rsi < 30:
                    signals.append(f"RSI baixo: {rsi:.0f} (sobrevendido)")
                    momentum_score += 1
                else:
                    signals.append(f"RSI neutro: {rsi:.0f}")
                
                indicators['rsi'] = rsi
        
        # Volume trend (se disponível)
        if history['volumes'] and len(history['volumes']) >= 14:
            recent_vol = sum(history['volumes'][-7:]) / 7
            older_vol = sum(history['volumes'][-30:-23]) / 7 if len(history['volumes']) >= 30 else recent_vol
            vol_change = (recent_vol / older_vol - 1) * 100 if older_vol else 0
            
            if vol_change > 50:
                signals.append(f"Volume crescente: +{vol_change:.0f}%")
                momentum_score += 1
            elif vol_change < -30:
                signals.append(f"Volume decrescente: {vol_change:.0f}%")
                momentum_score -= 1
            
            indicators['volume_change'] = vol_change
        
        # Classificação final de momentum
        if momentum_score >= 4:
            trend = "FORTE ALTA"
            emoji = "🚀"
            color = "green"
        elif momentum_score >= 2:
            trend = "ALTA"
            emoji = "📈"
            color = "green"
        elif momentum_score >= -1:
            trend = "NEUTRO"
            emoji = "➡️"
            color = "yellow"
        elif momentum_score >= -3:
            trend = "BAIXA"
            emoji = "📉"
            color = "orange"
        else:
            trend = "FORTE BAIXA"
            emoji = "⬇️"
            color = "red"
        
        return {
            'trend': trend,
            'emoji': emoji,
            'color': color,
            'score': momentum_score,
            'signals': signals,
            'indicators': indicators,
            'technical_analysis': self._generate_technical_summary(trend, indicators, signals, current_data)
        }
    
    def _generate_technical_summary(self, trend, indicators, signals, current_data):
        """Gera resumo técnico - EDUCACIONAL, NÃO RECOMENDAÇÃO"""
        
        summary = []
        
        # Estado atual do preço
        if indicators['position_in_range'] > 80:
            summary.append("⚠️ Preço próximo da máxima recente - possível resistência")
        elif indicators['position_in_range'] < 20:
            summary.append("📊 Preço próximo da mínima recente - possível suporte")
        else:
            summary.append(f"📍 Preço no meio do range histórico ({indicators['position_in_range']:.0f}%)")
        
        # Momentum
        if trend in ["FORTE ALTA", "ALTA"]:
            summary.append("📈 Momentum técnico positivo observado")
        elif trend in ["FORTE BAIXA", "BAIXA"]:
            summary.append("📉 Momentum técnico negativo observado")
        else:
            summary.append("➡️ Momentum lateral - sem direção clara")
        
        # Contexto de preço
        if indicators['distance_from_ath'] < -50:
            summary.append(f"💡 {abs(indicators['distance_from_ath']):.0f}% abaixo da máxima de 90d")
        elif indicators['distance_from_atl'] > 100:
            summary.append(f"💡 {indicators['distance_from_atl']:.0f}% acima da mínima de 90d")
        
        # RSI context se disponível
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            if rsi > 70:
                summary.append(f"📊 RSI indica condição de sobrecompra ({rsi:.0f})")
            elif rsi < 30:
                summary.append(f"📊 RSI indica condição de sobrevenda ({rsi:.0f})")
        
        # Volume context se disponível
        if 'volume_change' in indicators:
            vol_change = indicators['volume_change']
            if abs(vol_change) > 30:
                direction = "aumento" if vol_change > 0 else "diminuição"
                summary.append(f"📊 {direction.title()} significativo no volume ({vol_change:+.0f}%)")
        
        return summary
    
    def analyze_with_social(self, token_query: str) -> dict:
        """Análise completa com tratamento de erros"""
        
        # Análise base (sempre funciona)
        try:
            base_analysis = self.analyze(token_query)
        except Exception as e:
            print(f"Erro na análise base: {e}")
            return {'error': str(e), 'token': token_query, 'passed_elimination': False}
        
        # Garante que classification_info existe
        if 'classification_info' not in base_analysis:
            base_analysis['classification_info'] = {
                'classification': 'UNKNOWN',
                'emoji': '❓',
                'context': 'N/A',
                'quality': 'Não analisado',
                'risk_level': 'Desconhecido'
            }
        
        # Se a análise base falhou, retorna sem dados sociais
        if not base_analysis.get('passed_elimination', False):
            return base_analysis
        
        # Tenta adicionar dados sociais (opcional)
        try:
            social_analyzer = SocialAnalyzer()
            symbol = base_analysis.get('token', token_query)
            token_id = base_analysis.get('data', {}).get('id', token_query.lower())
            
            print(f"🔍 Buscando dados sociais para {symbol}...")
            social_data = social_analyzer.get_lunarcrush_data(symbol)
        except Exception as e:
            print(f"Análise social não disponível: {e}")
            social_data = social_analyzer._empty_social_data() if 'social_analyzer' in locals() else {
                'galaxy_score': 0, 'social_volume': 0, 'sentiment_bullish': 50,
                'sentiment_bearish': 50, 'alt_rank': 999, 'history_7d': []
            }
        
        # Tenta buscar dados Messari (opcional)
        try:
            messari_data = social_analyzer.get_messari_data(symbol)
        except Exception as e:
            print(f"Dados Messari não disponíveis: {e}")
            messari_data = {}
        
        # Tenta buscar dados DeFi (opcional)
        defi_data = None
        try:
            categories = base_analysis.get('data', {}).get('categories', [])
            if any('defi' in str(cat).lower() for cat in categories):
                if self.debug_mode: print(f"Token DeFi detectado, buscando metricas DeFiLlama...")
                defi_data = social_analyzer.get_defillama_extended(token_id)
        except Exception as e:
            print(f"Dados DeFi não disponíveis: {e}")
        
        # Tenta detectar hype (opcional)
        try:
            hype_analysis = social_analyzer.detect_hype(symbol, social_data)
        except Exception as e:
            print(f"Detecção de hype não disponível: {e}")
            hype_analysis = None
        
        # Ajusta score baseado em dados extras
        enhanced_score = base_analysis.get('score', 0)
        adjustments = []
        
        # Bonus/penalidade por social
        if social_data.get('galaxy_score', 0) > 80:
            enhanced_score += 0.5
            adjustments.append("📱 +0.5 (Galaxy Score alto)")
        
        if social_data.get('sentiment_bullish', 50) > 75:
            enhanced_score += 0.3
            adjustments.append("🐂 +0.3 (Sentimento muito bullish)")
        
        # Penalidade por hype extremo
        if hype_analysis.get('hype_score', 0) >= 70:
            enhanced_score -= 1.0
            adjustments.append("🔥 -1.0 (Hype extremo detectado)")
        elif hype_analysis.get('hype_score', 0) >= 50:
            enhanced_score -= 0.5
            adjustments.append("⚠️ -0.5 (Hype alto detectado)")
        
        # Bonus por métricas Messari
        if messari_data.get('real_volume', 0) > 0:
            current_volume = base_analysis.get('volume', 1)
            if current_volume > 0:
                real_vol_ratio = messari_data['real_volume'] / current_volume
                if real_vol_ratio > 0.8:  # Volume é majoritariamente real
                    enhanced_score += 0.3
                    adjustments.append("OK +0.3 (Volume real verificado)")
        
        # Bonus por baixa volatilidade (estabilidade)
        if messari_data.get('volatility_30d', 0) > 0:
            if messari_data['volatility_30d'] < 0.5:  # Baixa volatilidade
                enhanced_score += 0.2
                adjustments.append("📊 +0.2 (Baixa volatilidade)")
        
        # DeFi metrics
        if defi_data and defi_data.get('tvl_current', 0) > 0:
            if defi_data.get('mcap_to_tvl', 999) < 1.5:
                enhanced_score += 0.5
                adjustments.append("DeFi +0.5 (TVL/Mcap saudavel)")
            
            if defi_data.get('revenue_24h', 0) > 100000:  # $100k+ revenue/dia
                enhanced_score += 0.5
                adjustments.append("💰 +0.5 (Revenue alto)")
        
        # Limita score em 10
        enhanced_score = min(max(enhanced_score, 0), 10)
        
        # Retorna análise completa
        enhanced_analysis = {
            **base_analysis,
            'enhanced_score': enhanced_score,
            'score_adjustments': adjustments,
            'social_metrics': {
                'galaxy_score': social_data.get('galaxy_score', 0),
                'social_volume': social_data.get('social_volume', 0),
                'social_change': social_data.get('social_volume_change', 0),
                'sentiment': f"{social_data.get('sentiment_bullish', 50):.0f}% Bullish",
                'alt_rank': social_data.get('alt_rank', 999),
                'tweets': social_data.get('tweets', 0),
                'reddit_posts': social_data.get('reddit_posts', 0),
                'sentiment_bullish': social_data.get('sentiment_bullish', 50),
                'sentiment_bearish': social_data.get('sentiment_bearish', 50),
                'galaxy_score_change': social_data.get('galaxy_score_change', 0)
            } if social_data.get('galaxy_score', 0) > 0 else {
                'galaxy_score': 0,
                'social_volume': 0,
                'sentiment': '50% Bullish',
                'alt_rank': 999,
                'tweets': 0,
                'reddit_posts': 0,
                'sentiment_bullish': 50,
                'sentiment_bearish': 50,
                'galaxy_score_change': 0
            },
            'messari_metrics': {
                'real_volume': messari_data.get('real_volume', 0),
                'volatility_30d': messari_data.get('volatility_30d', 0),
                'developers': messari_data.get('developers_count', 0),
                'stock_to_flow': messari_data.get('stock_to_flow', 0),
                'annual_inflation': messari_data.get('annual_inflation', 0),
                'volume_turnover': messari_data.get('volume_turnover', 0),
                'y2050_supply': messari_data.get('y2050_supply', 0),
                'liquid_supply': messari_data.get('liquid_supply', 0),
                'watchers': messari_data.get('watchers', 0)
            } if messari_data.get('real_volume', 0) > 0 else None,
            'defi_metrics': {
                'tvl': defi_data.get('tvl_current', 0),
                'tvl_current': defi_data.get('tvl_current', 0),
                'mcap_tvl_ratio': defi_data.get('mcap_to_tvl', 999),
                'mcap_to_tvl': defi_data.get('mcap_to_tvl', 999),
                'revenue_24h': defi_data.get('revenue_24h', 0),
                'revenue_7d': defi_data.get('revenue_7d', 0),
                'chains': defi_data.get('chains', []),
                'main_chain': defi_data.get('main_chain', 'unknown'),
                'category': defi_data.get('category', 'unknown'),
                'tvl_7d_change': defi_data.get('tvl_7d_change', 0),
                'tvl_30d_change': defi_data.get('tvl_30d_change', 0),
                'fees_24h': defi_data.get('fees_24h', 0),
                'apy': defi_data.get('apy', 0),
                'user_24h': defi_data.get('user_24h', 0),
                'tx_count_24h': defi_data.get('tx_count_24h', 0)
            } if defi_data and defi_data.get('tvl_current', 0) > 0 else None,
            'hype_analysis': hype_analysis
        }
        
        # Adiciona campos obrigatórios para DisplayManager
        enhanced_analysis['decision'] = enhanced_analysis.get('classification', 'N/A')
        enhanced_analysis['analysis'] = {
            'strengths': enhanced_analysis.get('strengths', []),
            'weaknesses': enhanced_analysis.get('weaknesses', []),
            'risks': []  # Para compatibilidade com save_report
        }
        
        return enhanced_analysis
    
    def analyze_with_ai(self, token_data, analysis_type=None, user_id="default"):
        """
        Perform AI-powered analysis of token data
        
        Args:
            token_data: Token data from traditional analysis
            analysis_type: Type of AI analysis to perform
            user_id: User identifier for rate limiting
        
        Returns:
            Dict containing AI analysis results or None if failed
        """
        if not self.ai_enabled or not self.ai_agent:
            return None
        
        try:
            # Determine analysis type
            if analysis_type is None:
                analysis_type = "technical"  # Default to technical analysis
            
            # Convert string to AnalysisType enum
            if isinstance(analysis_type, str):
                try:
                    analysis_enum = AnalysisType(analysis_type.lower())
                except ValueError:
                    analysis_enum = AnalysisType.TECHNICAL
            else:
                analysis_enum = analysis_type
            
            # Prepare data for AI analysis
            ai_input_data = self._prepare_ai_input(token_data)
            
            # Perform AI analysis
            ai_response = self.ai_agent.analyze_token(
                ai_input_data,
                analysis_enum,
                user_id
            )
            
            if ai_response.success:
                # Format AI response for integration with traditional analysis
                return {
                    'type': analysis_enum.value,
                    'model_used': ai_response.model_used,
                    'confidence': ai_response.confidence,
                    'tokens_used': ai_response.tokens_used,
                    'cost': ai_response.cost,
                    'cached': ai_response.cached,
                    'processing_time': ai_response.processing_time,
                    'data': ai_response.data,
                    'timestamp': time.time(),
                    'success': True
                }
            else:
                return {
                    'type': analysis_enum.value if isinstance(analysis_enum, AnalysisType) else analysis_type,
                    'error': ai_response.error,
                    'model_attempted': ai_response.model_used,
                    'success': False
                }
                
        except Exception as e:
            return {
                'type': analysis_type if isinstance(analysis_type, str) else 'unknown',
                'error': f"AI analysis failed: {str(e)}",
                'success': False
            }
    
    def _prepare_ai_input(self, token_data):
        """Prepare token data for AI analysis"""
        return {
            'token_name': token_data.get('name', 'Unknown'),
            'token_symbol': token_data.get('symbol', 'UNK'),
            'current_price': token_data.get('price', 0),
            'market_cap': token_data.get('market_cap', 0),
            'market_cap_rank': token_data.get('market_cap_rank', 999),
            'volume_24h': token_data.get('volume', 0),
            'price_change_24h': token_data.get('price_change_24h', 0),
            'price_change_7d': token_data.get('price_change_7d', 0),
            'price_change_30d': token_data.get('price_change_30d', 0),
            'high_24h': token_data.get('high_24h', 0),
            'low_24h': token_data.get('low_24h', 0),
            'circulating_supply': token_data.get('circulating_supply', 0),
            'total_supply': token_data.get('total_supply', 0),
            'max_supply': token_data.get('max_supply', 0),
            'age_days': token_data.get('age_days', 0),
            'ath': token_data.get('ath', 0),
            'ath_date': token_data.get('ath_date', ''),
            'atl': token_data.get('atl', 0),
            'atl_date': token_data.get('atl_date', ''),
            # Social metrics
            'twitter_followers': token_data.get('twitter_followers', 0),
            'reddit_subscribers': token_data.get('reddit_subscribers', 0),
            'github_stars': token_data.get('github_stars', 0),
            'github_commits': token_data.get('github_commits', 0),
            'github_forks': token_data.get('github_forks', 0),
            # Additional context
            'additional_metrics': {
                'volatility_30d': token_data.get('volatility_30d', 0),
                'sharpe_ratio': token_data.get('sharpe_ratio', 0),
                'beta': token_data.get('beta', 0),
                'correlation_btc': token_data.get('correlation_btc', 0)
            }
        }
    
    def get_ai_models(self):
        """Get available AI models for current user tier"""
        if not self.ai_enabled or not self.ai_agent:
            return []
        
        return self.ai_agent.get_available_models()
    
    def get_ai_usage_stats(self, user_id="default", days=1):
        """Get AI usage statistics"""
        if not self.ai_enabled or not self.ai_agent:
            return None
        
        return self.ai_agent.get_usage_stats(user_id, days)
    
    def is_ai_enabled(self):
        """Check if AI analysis is enabled and available"""
        return self.ai_enabled and self.ai_agent is not None
    
    def ai_health_check(self):
        """Check AI service health"""
        if not self.ai_enabled or not self.ai_agent:
            return {
                'status': 'disabled',
                'message': 'AI analysis is not enabled or available'
            }
        
        return self.ai_agent.health_check()
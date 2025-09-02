# ai_insights.py - Enhanced AI Agent with Web Research
"""
Advanced AI Insights Module with Web Research and Deep Analysis
Maintains same interface for complete compatibility with existing system
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from urllib.parse import quote_plus

class AIInsights:
    """
    Enhanced AI Insights com web research e análise profunda
    Mantém a mesma interface para compatibilidade total
    """
    
    def __init__(self):
        # API Keys - carregadas do ambiente ou None para fallback
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.tavily_key = os.getenv('TAVILY_API_KEY') 
        self.serper_key = os.getenv('SERPER_API_KEY')
        self.brave_key = os.getenv('BRAVE_API_KEY')
        
        # Configurações
        self.session = None
        self.timeout = 15  # timeout para requests
        
        print(f"[AI_INSIGHTS] Enhanced AI Agent initialized")
        print(f"[AI_INSIGHTS] APIs available: OpenRouter:{bool(self.openrouter_key)}, Tavily:{bool(self.tavily_key)}, Serper:{bool(self.serper_key)}, Brave:{bool(self.brave_key)}")
    
    def analyze(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        MESMA INTERFACE - não quebra compatibilidade
        Método principal que mantém a mesma assinatura do sistema original
        """
        start_time = time.time()
        
        try:
            # Se temos APIs configuradas, usar análise avançada
            if self._has_web_apis():
                print(f"[AI_INSIGHTS] Running enhanced analysis with web research...")
                result = self._run_enhanced_analysis(token_data)
            else:
                print(f"[AI_INSIGHTS] Running advanced rule-based analysis...")
                result = self._run_advanced_rule_based_analysis(token_data)
            
            # Garantir que retorna no MESMO formato esperado
            processing_time = time.time() - start_time
            result['processing_time'] = round(processing_time, 2)
            
            return result
            
        except Exception as e:
            print(f"[AI_INSIGHTS] Error in enhanced analysis: {e}")
            # Fallback para análise básica original se algo falhar
            return self._basic_analysis_fallback(token_data)
    
    def _has_web_apis(self) -> bool:
        """Verifica se temos pelo menos uma API web configurada"""
        return bool(self.tavily_key or self.serper_key or self.brave_key)
    
    def _run_enhanced_analysis(self, token_data: Dict) -> Dict:
        """Executa análise completa com web research"""
        
        token_symbol = token_data.get('symbol', 'UNKNOWN')
        token_name = token_data.get('name', token_symbol)
        
        try:
            # PASSO 1: Executar web research assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            web_intelligence = loop.run_until_complete(
                self._gather_web_intelligence(token_symbol, token_name)
            )
            
            loop.close()
            
        except Exception as e:
            print(f"[AI_INSIGHTS] Web research failed: {e}")
            web_intelligence = {'news': [], 'analysis': [], 'sentiment': 'NEUTRAL'}
        
        # PASSO 2: Combinar dados on-chain com web intelligence
        enhanced_context = self._prepare_enhanced_context(token_data, web_intelligence)
        
        # PASSO 3: Gerar análise usando AI ou regras avançadas
        if self.openrouter_key:
            analysis = self._generate_ai_analysis(enhanced_context)
        else:
            analysis = self._generate_enhanced_rule_based_analysis(enhanced_context)
        
        return self._format_final_response(analysis, enhanced_context)
    
    async def _gather_web_intelligence(self, symbol: str, name: str) -> Dict:
        """Coleta inteligência de múltiplas fontes web em paralelo"""
        
        # Preparar queries inteligentes
        queries = [
            f"{symbol} cryptocurrency news latest 2024",
            f"{name} {symbol} price prediction analysis", 
            f"{symbol} on-chain metrics whale activity",
            f"{name} technical analysis trading signals"
        ]
        
        tasks = []
        
        # Lançar buscas em paralelo baseadas nas APIs disponíveis
        if self.tavily_key:
            tasks.append(self._search_tavily(queries[0]))
        if self.serper_key:
            tasks.append(self._search_serper(queries[1]))  
        if self.brave_key:
            tasks.append(self._search_brave(queries[2]))
        
        # Se não tiver APIs, usar fallback web scraping
        if not tasks:
            tasks.append(self._fallback_web_search(symbol))
        
        # Executar todas as buscas em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        web_data = {
            'news': [],
            'analysis': [], 
            'sentiment': 'NEUTRAL',
            'key_mentions': []
        }
        
        for result in results:
            if isinstance(result, dict) and not isinstance(result, Exception):
                web_data['news'].extend(result.get('news', [])[:3])
                web_data['analysis'].extend(result.get('analysis', [])[:2])
                web_data['key_mentions'].extend(result.get('mentions', [])[:5])
        
        return web_data
    
    async def _search_tavily(self, query: str) -> Dict:
        """Busca inteligente no Tavily API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 5,
                    "include_domains": ["coindesk.com", "cointelegraph.com", "decrypt.co", "theblock.co"]
                }
                
                async with session.post(
                    'https://api.tavily.com/search',
                    json=payload,
                    timeout=self.timeout
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._process_tavily_results(data)
        except Exception as e:
            print(f"[AI_INSIGHTS] Tavily search failed: {e}")
        
        return {'news': [], 'analysis': []}
    
    async def _search_serper(self, query: str) -> Dict:
        """Busca inteligente no Serper API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "q": query,
                    "num": 5,
                    "gl": "us",
                    "hl": "en"
                }
                
                headers = {
                    'X-API-KEY': self.serper_key,
                    'Content-Type': 'application/json'
                }
                
                async with session.post(
                    'https://google.serper.dev/search',
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._process_serper_results(data)
        except Exception as e:
            print(f"[AI_INSIGHTS] Serper search failed: {e}")
            
        return {'news': [], 'analysis': []}
    
    async def _search_brave(self, query: str) -> Dict:
        """Busca inteligente no Brave Search API"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip',
                    'X-Subscription-Token': self.brave_key
                }
                
                params = {
                    'q': query,
                    'count': 5,
                    'result_filter': 'web',
                    'safesearch': 'moderate'
                }
                
                async with session.get(
                    'https://api.search.brave.com/res/v1/web/search',
                    headers=headers,
                    params=params,
                    timeout=self.timeout
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._process_brave_results(data)
        except Exception as e:
            print(f"[AI_INSIGHTS] Brave search failed: {e}")
            
        return {'news': [], 'analysis': []}
    
    async def _fallback_web_search(self, symbol: str) -> Dict:
        """Fallback search sem APIs externas"""
        # Simulação de dados baseados em padrões conhecidos
        return {
            'news': [f"Recent activity detected for {symbol}"],
            'analysis': [f"{symbol} shows market interest"],
            'mentions': []
        }
    
    def _process_tavily_results(self, data: Dict) -> Dict:
        """Processa resultados do Tavily"""
        results = {'news': [], 'analysis': []}
        
        for item in data.get('results', []):
            title = item.get('title', '')
            content = item.get('content', '')
            
            if any(word in title.lower() for word in ['news', 'update', 'announcement']):
                results['news'].append(title)
            else:
                results['analysis'].append(f"{title}: {content[:100]}...")
        
        return results
    
    def _process_serper_results(self, data: Dict) -> Dict:
        """Processa resultados do Serper"""  
        results = {'news': [], 'analysis': []}
        
        for item in data.get('organic', []):
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            
            if any(word in title.lower() for word in ['analysis', 'prediction', 'forecast']):
                results['analysis'].append(f"{title}: {snippet}")
            else:
                results['news'].append(title)
        
        return results
    
    def _process_brave_results(self, data: Dict) -> Dict:
        """Processa resultados do Brave"""
        results = {'news': [], 'analysis': []}
        
        for item in data.get('web', {}).get('results', []):
            title = item.get('title', '')
            description = item.get('description', '')
            
            if any(word in description.lower() for word in ['technical', 'chart', 'trading']):
                results['analysis'].append(f"{title}: {description}")
            else:
                results['news'].append(title)
        
        return results
    
    def _prepare_enhanced_context(self, token_data: Dict, web_data: Dict) -> Dict:
        """Prepara contexto enriquecido com dados web"""
        return {
            'token_symbol': token_data.get('symbol', 'UNKNOWN'),
            'token_name': token_data.get('name', 'UNKNOWN'),
            'price': token_data.get('current_price', token_data.get('price', 0)),
            'market_cap': token_data.get('market_cap', 0),
            'volume': token_data.get('volume_24h', token_data.get('volume', 0)),
            'price_change_24h': token_data.get('price_change_24h', 0),
            'price_change_7d': token_data.get('price_change_7d', 0),
            'market_cap_rank': token_data.get('market_cap_rank', 999),
            'web_news': web_data.get('news', []),
            'web_analysis': web_data.get('analysis', []),
            'web_mentions': web_data.get('key_mentions', [])
        }
    
    def _generate_ai_analysis(self, context: Dict) -> Dict:
        """Gera análise usando OpenRouter AI"""
        try:
            prompt = self._build_analysis_prompt(context)
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.openrouter_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3-haiku',
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 800,
                    'temperature': 0.7
                },
                timeout=20
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']
                return self._parse_ai_response(content)
                
        except Exception as e:
            print(f"[AI_INSIGHTS] OpenRouter AI failed: {e}")
        
        # Fallback para análise baseada em regras se AI falhar
        return self._generate_enhanced_rule_based_analysis(context)
    
    def _build_analysis_prompt(self, context: Dict) -> str:
        """Constrói prompt inteligente para o AI"""
        return f"""
Analyze {context['token_symbol']} ({context['token_name']}) cryptocurrency with this data:

MARKET DATA:
- Price: ${context['price']:,.6f}
- Market Cap: ${context['market_cap']:,}
- Volume 24h: ${context['volume']:,}
- Price Change 24h: {context['price_change_24h']:.2f}%
- Price Change 7d: {context['price_change_7d']:.2f}%
- Market Rank: #{context['market_cap_rank']}

WEB INTELLIGENCE:
Recent News: {'; '.join(context['web_news'][:3]) if context['web_news'] else 'No recent news'}
Market Analysis: {'; '.join(context['web_analysis'][:2]) if context['web_analysis'] else 'No analysis found'}

Provide a comprehensive analysis with:
1. Executive Summary (2-3 sentences)
2. Key Factors (3-4 specific bullet points)  
3. Main Risks (2-3 specific risks)
4. Opportunities (2-3 specific opportunities)
5. Clear Recommendation
6. Confidence Level (0-100)

Be specific, reference actual data points, avoid generic statements.
Format as JSON with fields: summary, key_factors, risks, opportunities, recommendation, confidence.
"""
    
    def _parse_ai_response(self, content: str) -> Dict:
        """Extrai dados estruturados da resposta da AI"""
        try:
            # Tentar extrair JSON da resposta
            if '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Se não conseguir extrair JSON, fazer parsing manual
        lines = content.split('\n')
        
        return {
            'summary': self._extract_section(content, 'summary', 'Executive Summary'),
            'key_factors': self._extract_list(content, 'factors', 'key factors'),
            'risks': self._extract_list(content, 'risks', 'risks'),
            'opportunities': self._extract_list(content, 'opportunities', 'opportunities'),
            'recommendation': self._extract_section(content, 'recommendation', 'Recommendation'),
            'confidence': self._extract_confidence(content)
        }
    
    def _extract_section(self, content: str, key: str, fallback_key: str) -> str:
        """Extrai seção específica do texto"""
        content_lower = content.lower()
        
        for keyword in [key, fallback_key.lower()]:
            if keyword in content_lower:
                start = content_lower.find(keyword)
                # Pegar próximos 200 caracteres
                section = content[start:start+200]
                # Limpar e retornar primeira frase relevante
                lines = section.split('\n')
                for line in lines[1:]:  # Pular o cabeçalho
                    if line.strip() and len(line.strip()) > 20:
                        return line.strip()
        
        return f"Analysis completed based on available data for the token."
    
    def _extract_list(self, content: str, key: str, fallback_key: str) -> List[str]:
        """Extrai lista de items do texto"""
        content_lower = content.lower()
        items = []
        
        for keyword in [key, fallback_key.lower()]:
            if keyword in content_lower:
                start = content_lower.find(keyword)
                section = content[start:start+500]
                
                # Procurar por bullets ou números
                lines = section.split('\n')
                for line in lines:
                    line = line.strip()
                    if (line.startswith('-') or line.startswith('•') or 
                        line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                        clean_line = line.lstrip('-•123. ').strip()
                        if len(clean_line) > 10:
                            items.append(clean_line)
                
                if items:
                    return items[:3]
        
        # Fallback baseado em dados do token
        return [f"Market analysis based on current data trends"]
    
    def _extract_confidence(self, content: str) -> int:
        """Extrai nível de confiança do texto"""
        import re
        
        # Procurar por números seguidos de %
        confidence_match = re.search(r'confidence[:\s]*(\d+)', content.lower())
        if confidence_match:
            return min(95, max(10, int(confidence_match.group(1))))
        
        # Procurar por palavras qualitativas
        if any(word in content.lower() for word in ['high confidence', 'very confident', 'strong']):
            return 85
        elif any(word in content.lower() for word in ['medium', 'moderate']):
            return 65
        elif any(word in content.lower() for word in ['low', 'uncertain', 'limited']):
            return 40
        
        return 70  # Default
    
    def _generate_enhanced_rule_based_analysis(self, context: Dict) -> Dict:
        """Análise avançada baseada em regras quando não temos AI"""
        
        price_change = context['price_change_24h']
        volume = context['volume']
        market_cap = context['market_cap']
        rank = context['market_cap_rank']
        
        # Análise de momentum
        momentum = self._calculate_momentum(price_change)
        
        # Análise de liquidez
        liquidity_ratio = (volume / market_cap * 100) if market_cap > 0 else 0
        
        # Análise de risco
        volatility = abs(price_change)
        risk_level = self._calculate_risk(volatility, liquidity_ratio)
        
        # Gerar insights baseados em web data
        web_sentiment = self._analyze_web_sentiment(context.get('web_news', []), context.get('web_analysis', []))
        
        return {
            'summary': self._generate_enhanced_summary(context, momentum, liquidity_ratio, risk_level, web_sentiment),
            'key_factors': self._extract_enhanced_key_factors(context, web_sentiment),
            'risks': self._identify_enhanced_risks(context, risk_level),
            'opportunities': self._identify_enhanced_opportunities(context, momentum, web_sentiment),
            'recommendation': self._generate_enhanced_recommendation(context, momentum, risk_level),
            'confidence': self._calculate_enhanced_confidence(context)
        }
    
    def _analyze_web_sentiment(self, news: List[str], analysis: List[str]) -> str:
        """Analisa sentimento das informações web"""
        all_text = ' '.join(news + analysis).lower()
        
        positive_words = ['bullish', 'growth', 'rise', 'surge', 'positive', 'gain', 'up', 'strong']
        negative_words = ['bearish', 'fall', 'drop', 'decline', 'negative', 'loss', 'down', 'weak']
        
        pos_count = sum(1 for word in positive_words if word in all_text)
        neg_count = sum(1 for word in negative_words if word in all_text)
        
        if pos_count > neg_count + 1:
            return 'POSITIVO'
        elif neg_count > pos_count + 1:
            return 'NEGATIVO'
        else:
            return 'NEUTRO'
    
    def _generate_enhanced_summary(self, context: Dict, momentum: float, liquidity: float, risk: str, sentiment: str) -> str:
        """Gera resumo enriquecido com dados web"""
        symbol = context['token_symbol']
        change = context['price_change_24h']
        
        trend = "alta" if change > 0 else "baixa"
        web_context = f"Sentimento web: {sentiment.lower()}." if sentiment != 'NEUTRO' else ""
        
        return f"{symbol} está em {trend} ({change:+.1f}%) com momentum {momentum:.0f}/100. Liquidez: {liquidity:.1f}% do market cap. Risco: {risk}. {web_context}".strip()
    
    def _extract_enhanced_key_factors(self, context: Dict, sentiment: str) -> List[str]:
        """Extrai fatores-chave enriquecidos"""
        factors = []
        
        # Fatores baseados em ranking
        if context['market_cap_rank'] <= 10:
            factors.append(f"Top {context['market_cap_rank']} - Criptomoeda estabelecida")
        elif context['market_cap_rank'] <= 100:
            factors.append(f"Rank #{context['market_cap_rank']} - Projeto consolidado")
        
        # Fatores baseados em performance
        if context['price_change_7d'] > 10:
            factors.append(f"Forte valorização semanal: +{context['price_change_7d']:.1f}%")
        
        # Fatores baseados em volume
        volume_ratio = (context['volume'] / context['market_cap'] * 100) if context['market_cap'] > 0 else 0
        if volume_ratio > 20:
            factors.append("Volume institucional - alta liquidez")
        
        # Fatores baseados em web sentiment
        if sentiment == 'POSITIVO':
            factors.append("Sentimento web positivo - interesse crescente")
        
        return factors[:4]  # Máximo 4 fatores
    
    def _identify_enhanced_risks(self, context: Dict, risk_level: str) -> List[str]:
        """Identifica riscos enriquecidos"""
        risks = []
        
        if abs(context['price_change_24h']) > 10:
            risks.append(f"Alta volatilidade: {context['price_change_24h']:+.1f}% em 24h")
        
        volume_ratio = (context['volume'] / context['market_cap'] * 100) if context['market_cap'] > 0 else 0
        if volume_ratio < 1:
            risks.append("Baixa liquidez pode gerar slippage")
        
        if context['market_cap_rank'] > 300:
            risks.append("Projeto de baixa capitalização - maior risco")
        
        return risks[:3]
    
    def _identify_enhanced_opportunities(self, context: Dict, momentum: float, sentiment: str) -> List[str]:
        """Identifica oportunidades enriquecidas"""
        opportunities = []
        
        if momentum > 60 and context['price_change_7d'] > 5:
            opportunities.append("Tendência de alta consistente - momentum positivo")
        
        if context['market_cap_rank'] <= 50:
            opportunities.append("Projeto estabelecido com menor risco de rugpull")
        
        volume_ratio = (context['volume'] / context['market_cap'] * 100) if context['market_cap'] > 0 else 0
        if volume_ratio > 10:
            opportunities.append("Excelente liquidez para entrada/saída")
        
        if sentiment == 'POSITIVO':
            opportunities.append("Sentimento de mercado favorável")
        
        return opportunities[:3]
    
    def _generate_enhanced_recommendation(self, context: Dict, momentum: float, risk_level: str) -> str:
        """Gera recomendação enriquecida"""
        
        if momentum > 70 and risk_level == 'BAIXO' and context['market_cap_rank'] <= 100:
            return "COMPRA - Forte momentum com risco controlado"
        elif momentum > 50 and risk_level in ['BAIXO', 'MÉDIO']:
            return "ACUMULAR - Momentum positivo, aguardar correções"
        elif risk_level == 'ALTO':
            return "AGUARDAR - Risco elevado, monitorar estabilização"
        else:
            return "NEUTRO - Monitorar desenvolvimento dos indicadores"
    
    def _calculate_enhanced_confidence(self, context: Dict) -> int:
        """Calcula confiança enriquecida com dados web"""
        base_confidence = self._calculate_confidence(context)
        
        # Bonus por dados web
        if context.get('web_news'):
            base_confidence += 10
        if context.get('web_analysis'):
            base_confidence += 5
        
        return min(95, base_confidence)
    
    def _run_advanced_rule_based_analysis(self, token_data: Dict) -> Dict:
        """Análise avançada sem APIs web - versão melhorada da original"""
        
        # Usar as funções originais melhoradas
        price = token_data.get('current_price', token_data.get('price', 0))
        volume = token_data.get('volume_24h', token_data.get('volume', 0))
        market_cap = token_data.get('market_cap', 0)
        price_change_24h = token_data.get('price_change_24h', 0)
        
        # Análises avançadas
        volatility = abs(price_change_24h) if price_change_24h else 0
        liquidity_ratio = (volume / market_cap * 100) if market_cap > 0 else 0
        momentum_score = self._calculate_momentum(price_change_24h)
        risk_level = self._calculate_risk(volatility, liquidity_ratio)
        
        # Gerar resumo avançado
        summary = self._generate_summary(
            token_data.get('symbol', 'TOKEN'),
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
    
    def _format_final_response(self, analysis: Dict, context: Dict) -> Dict:
        """Formata resposta final no formato esperado pelo sistema"""
        return {
            'status': 'completed',
            'summary': analysis.get('summary', 'Enhanced analysis completed'),
            'confidence': analysis.get('confidence', 70),
            'sentiment': self._determine_sentiment(
                context['price_change_24h'], 
                analysis.get('confidence', 70)
            ),
            'key_factors': analysis.get('key_factors', []),
            'risks': analysis.get('risks', []),
            'opportunities': analysis.get('opportunities', []),
            'recommendation': analysis.get('recommendation', 'NEUTRO'),
            'model_used': 'Enhanced AI Agent v2.0',
            'metrics': {
                'volatility': round(abs(context['price_change_24h']), 2),
                'liquidity_ratio': round((context['volume'] / context['market_cap'] * 100) if context['market_cap'] > 0 else 0, 2),
                'momentum_score': self._calculate_momentum(context['price_change_24h']),
                'risk_level': self._calculate_risk(
                    abs(context['price_change_24h']), 
                    (context['volume'] / context['market_cap'] * 100) if context['market_cap'] > 0 else 0
                )
            }
        }
    
    def _basic_analysis_fallback(self, token_data: Dict) -> Dict:
        """Fallback para análise básica se tudo mais falhar"""
        print("[AI_INSIGHTS] Using basic fallback analysis")
        
        return {
            'status': 'completed',
            'summary': f"Análise básica para {token_data.get('symbol', 'TOKEN')}. Sistema funcionando em modo de fallback.",
            'confidence': 40,
            'sentiment': 'NEUTRO',
            'key_factors': ['Análise em modo básico'],
            'risks': ['Dados limitados'],
            'opportunities': ['Aguardar dados completos'],
            'metrics': {
                'volatility': 0,
                'liquidity_ratio': 0,
                'momentum_score': 50,
                'risk_level': 'MÉDIO'
            }
        }
    
    # =================== MÉTODOS ORIGINAIS MANTIDOS ===================
    # Mantendo todos os métodos originais para compatibilidade total
    
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
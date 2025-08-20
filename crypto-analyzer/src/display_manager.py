"""
Display Manager - Sistema de visualização hierárquica profissional
Organiza resultados em camadas claras: 3 Camadas → Análises Complementares → Disclaimer
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from datetime import datetime
import math

console = Console()

class DisplayManager:
    """Gerenciador de exibição hierárquica e profissional"""
    
    def __init__(self):
        self.console = console
    
    def display_complete_analysis(self, result: dict):
        """Exibe análise completa seguindo hierarquia correta"""
        
        # Se não passou na eliminatória, exibição simplificada
        if not result.get('passed_elimination', False):
            self._display_header(result)
            self._display_layer_1_elimination(result)
            self._display_disclaimer()
            return
        
        # Análise completa para tokens aprovados
        self._display_header(result)
        
        # SECAO PRINCIPAL: Sistema de 3 Camadas
        self.console.print("\n[bold cyan]=============== SISTEMA DE 3 CAMADAS ===============[/bold cyan]\n")
        self._display_layer_1_elimination(result)
        self._display_layer_2_scoring(result)
        self._display_layer_3_decision(result)
        
        # SECOES COMPLEMENTARES
        self.console.print("\n[bold cyan]============ ANALISES COMPLEMENTARES ============[/bold cyan]\n")
        self._display_technical_analysis(result)
        self._display_price_levels_strategy(result)
        self._display_hype_detection(result)
        
        # Métricas On-Chain se disponível
        if result.get('defi_metrics') and result['defi_metrics'].get('tvl', 0) > 0:
            self._display_onchain_metrics(result)
        
        # Disclaimer
        self._display_disclaimer()
    
    def _display_header(self, result):
        """Header principal com informações do token"""
        token_name = result.get('token_name', 'Unknown')
        token_symbol = result.get('token', 'UNK').upper()
        
        # Criar header estilizado
        header = Text()
        header.append("=" * 70 + "\n", style="bright_blue")
        header.append(" " * 20 + f"{token_name.upper()} ({token_symbol}) ANALISE COMPLETA\n", style="bold white")
        header.append("=" * 70, style="bright_blue")
        
        self.console.print(Align.center(header))
    
    def _display_layer_1_elimination(self, result):
        """CAMADA 1: Critérios Eliminatórios"""
        
        passed = result.get('passed_elimination', False)
        data = result.get('data', {})
        
        if not passed:
            # Token rejeitado
            reasons = result.get('elimination_reasons', [])
            
            content = "[bold red]X REJEITADO[/bold red] - Nao atendeu criterios minimos\n\n"
            content += "[red]Motivos:[/red]\n"
            for reason in reasons:
                content += f"  - {reason}\n"
            
            panel = Panel(
                content,
                title="[bold red]🚫 CAMADA 1: ELIMINATÓRIA[/bold red]",
                border_style="red",
                expand=False
            )
        else:
            # Token aprovado - mostrar critérios atendidos
            market_cap = data.get('market_cap', 0)
            volume = data.get('volume', 0)
            age_days = data.get('age_days', 0)
            
            # Calcular ratio de liquidez
            liquidity_ratio = (volume / market_cap * 100) if market_cap > 0 else 0
            
            content = "[bold green]✅ APROVADO[/bold green] - Passou em todos os critérios\n\n"
            content += "[green]Critérios Atendidos:[/green]\n"
            content += f"  • Market Cap: ${self._format_number(market_cap)} [green]✓[/green] (mín: $1M)\n"
            content += f"  • Volume 24h: ${self._format_number(volume)} [green]✓[/green] (mín: $100K)\n"
            content += f"  • Idade: {age_days:,} dias [green]✓[/green] (mín: 180 dias)\n"
            content += f"  • Liquidez: {liquidity_ratio:.2f}% do MCap [green]✓[/green] (mín: 0.1%)\n"
            
            # Adicionar informações extras se disponíveis
            if data.get('circulating_supply'):
                content += f"  • Supply Circulante: {self._format_number(data['circulating_supply'])} tokens\n"
            
            panel = Panel(
                content,
                title="[bold green]✅ CAMADA 1: ELIMINATÓRIA[/bold green]",
                border_style="green",
                expand=False
            )
        
        self.console.print(panel)
    
    def _display_layer_2_scoring(self, result):
        """CAMADA 2: Sistema de Pontuação Detalhado"""
        
        score = result.get('score', 0)
        breakdown = result.get('score_breakdown', {})
        data = result.get('data', {})
        
        # Criar barra visual de progresso
        score_percentage = int(score * 10)
        filled_blocks = score_percentage // 3
        empty_blocks = 33 - filled_blocks
        score_bar = "[green]█[/green]" * filled_blocks + "[dim]░[/dim]" * empty_blocks
        
        # Determinar cor baseada no score
        if score >= 8:
            score_color = "bright_green"
            grade = "A"
        elif score >= 6:
            score_color = "yellow"
            grade = "B"
        elif score >= 4:
            score_color = "orange1"
            grade = "C"
        else:
            score_color = "red"
            grade = "D"
        
        content = f"[{score_color} bold]SCORE FINAL: {score}/10 (Grade {grade})[/{score_color} bold]\n"
        content += f"{score_bar} [{score_percentage}%]\n\n"
        
        content += "[bold]Breakdown Detalhado:[/bold]\n\n"
        
        # Criar tabela de breakdown
        criteria_details = [
            ("Market Position", 
             breakdown.get('market_cap', 0),
             f"Rank #{data.get('market_cap_rank', 'N/A')} • MCap ${self._format_number(data.get('market_cap', 0))}"),
            
            ("Liquidez",
             breakdown.get('liquidity', 0),
             f"Volume ${self._format_number(data.get('volume', 0))} • Ratio {(data.get('volume', 0)/data.get('market_cap', 1)*100):.1f}%"),
            
            ("Desenvolvimento",
             breakdown.get('development', 0),
             f"{data.get('github_commits', 0)} commits/mês • {data.get('github_stars', 0)} stars"),
            
            ("Comunidade",
             breakdown.get('community', 0),
             f"{self._format_number(data.get('twitter_followers', 0))} Twitter • {self._format_number(data.get('reddit_subscribers', 0))} Reddit"),
            
            ("Performance",
             breakdown.get('performance', 0),
             f"30d: {data.get('price_change_30d', 0):+.1f}% • 7d: {data.get('price_change_7d', 0):+.1f}%")
        ]
        
        for name, points, details in criteria_details:
            # Criar barra visual para cada critério
            if points >= 1.8:
                bar = "[green]██[/green]"
                pts_color = "green"
            elif points >= 1.2:
                bar = "[yellow]█░[/yellow]"
                pts_color = "yellow"
            elif points >= 0.6:
                bar = "[orange1]█░[/orange1]"
                pts_color = "orange1"
            else:
                bar = "[red]░░[/red]"
                pts_color = "red"
            
            content += f"  {name:<18} {bar} [{pts_color}]{points:.1f}/2.0[/{pts_color}]\n"
            content += f"  [dim]└─ {details}[/dim]\n\n"
        
        # Adicionar insights baseados no score
        if score >= 8:
            content += "\n💎 [green]Fundamentos Excelentes - Token de alta qualidade[/green]"
        elif score >= 6:
            content += "\n⭐ [yellow]Fundamentos Sólidos - Merece análise aprofundada[/yellow]"
        elif score >= 4:
            content += "\n📊 [orange1]Fundamentos Medianos - Cautela recomendada[/orange1]"
        else:
            content += "\n⚠️ [red]Fundamentos Fracos - Alto risco[/red]"
        
        panel = Panel(
            content,
            title=f"[bold]📊 CAMADA 2: PONTUAÇÃO FUNDAMENTAL[/bold]",
            border_style=score_color,
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_layer_3_decision(self, result):
        """CAMADA 3: Decisão e Classificação Final"""
        
        score = result.get('score', 0)
        classification = result.get('classification_info', {})
        market_context = result.get('market_context', {})
        
        # Decisão baseada no score
        if score >= 8:
            decision = "CONSIDERAR COMPRA"
            decision_emoji = "🟢"
            decision_color = "green"
            action = "Token apresenta fundamentos sólidos para investimento"
        elif score >= 5:
            decision = "ESTUDAR MAIS"
            decision_emoji = "🟡"
            decision_color = "yellow"
            action = "Necessita análise adicional antes de decisão"
        else:
            decision = "EVITAR"
            decision_emoji = "🔴"
            decision_color = "red"
            action = "Fundamentos insuficientes para investimento"
        
        content = f"[{decision_color} bold]{decision_emoji} DECISÃO FINAL: {decision}[/{decision_color} bold]\n"
        content += f"[dim]{action}[/dim]\n\n"
        
        # Classificação do token
        content += "[bold]Classificação de Mercado:[/bold]\n"
        content += f"  • Categoria: {classification.get('classification', 'N/A')} {classification.get('emoji', '')}\n"
        content += f"  • Descrição: {classification.get('description', 'N/A')}\n"
        content += f"  • Nível de Risco: {classification.get('risk_level', 'N/A')}\n"
        content += f"  • Qualidade: {classification.get('quality', 'N/A')}\n\n"
        
        # Contexto de mercado
        fg_value = market_context.get('fear_greed_index', 50)
        fg_sentiment = market_context.get('market_sentiment', 'Neutral')
        
        # Cor do Fear & Greed
        if fg_value < 25:
            fg_color = "red"
            fg_emoji = "😱"
        elif fg_value < 45:
            fg_color = "orange1"
            fg_emoji = "😨"
        elif fg_value < 55:
            fg_color = "yellow"
            fg_emoji = "😐"
        elif fg_value < 75:
            fg_color = "green"
            fg_emoji = "😊"
        else:
            fg_color = "bright_green"
            fg_emoji = "🤑"
        
        content += "[bold]Contexto de Mercado:[/bold]\n"
        content += f"  • Fear & Greed: [{fg_color}]{fg_value}/100 {fg_emoji} ({fg_sentiment})[/{fg_color}]\n"
        content += f"  • Recomendação: {market_context.get('recommendation', 'N/A')}\n\n"
        
        # Pontos fortes e fracos
        strengths = result.get('strengths', [])
        weaknesses = result.get('weaknesses', [])
        
        if strengths:
            content += "[bold green]✅ Pontos Fortes:[/bold green]\n"
            for strength in strengths[:4]:
                content += f"  • {strength}\n"
            content += "\n"
        
        if weaknesses:
            content += "[bold orange1]⚠️ Pontos de Atenção:[/bold orange1]\n"
            for weakness in weaknesses[:3]:
                content += f"  • {weakness}\n"
        
        panel = Panel(
            content,
            title="[bold]🎯 CAMADA 3: DECISÃO DE INVESTIMENTO[/bold]",
            border_style=decision_color,
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_technical_analysis(self, result):
        """Análise Técnica com Momentum e Indicadores"""
        
        momentum = result.get('momentum_analysis', {})
        
        if not momentum or momentum.get('trend') == 'INDEFINIDO':
            return
        
        trend = momentum.get('trend', 'NEUTRO')
        trend_emoji = momentum.get('emoji', '➡️')
        trend_color = momentum.get('color', 'yellow')
        
        content = f"[{trend_color} bold]{trend_emoji} MOMENTUM: {trend}[/{trend_color} bold]\n\n"
        
        # Indicadores técnicos
        indicators = momentum.get('indicators', {})
        
        if indicators:
            content += "[bold]Indicadores Técnicos:[/bold]\n"
            
            # RSI
            rsi = indicators.get('rsi', 0)
            if rsi > 0:
                if rsi > 70:
                    rsi_status = "[red]Sobrecomprado[/red]"
                elif rsi < 30:
                    rsi_status = "[green]Sobrevendido[/green]"
                else:
                    rsi_status = "[yellow]Neutro[/yellow]"
                content += f"  • RSI(14): {rsi:.0f} - {rsi_status}\n"
            
            # Médias móveis
            ma7 = indicators.get('price_vs_7d_avg', 0)
            ma30 = indicators.get('price_vs_30d_avg', 0)
            
            content += f"  • Preço vs MA(7): {ma7:+.1f}%\n"
            content += f"  • Preço vs MA(30): {ma30:+.1f}%\n"
            
            # Posição no range
            position = indicators.get('position_in_range', 50)
            content += f"  • Posição no Range (90d): {position:.0f}%\n"
            
            # Volume
            vol_change = indicators.get('volume_change', 0)
            if vol_change != 0:
                vol_trend = "📈 aumentando" if vol_change > 0 else "📉 diminuindo"
                content += f"  • Volume: {vol_change:+.0f}% ({vol_trend})\n"
        
        # Sinais técnicos
        signals = momentum.get('signals', [])
        if signals:
            content += "\n[bold]Sinais Detectados:[/bold]\n"
            for signal in signals[:5]:
                content += f"  • {signal}\n"
        
        # Análise técnica resumida
        tech_analysis = momentum.get('technical_analysis', [])
        if tech_analysis:
            content += "\n[bold]Resumo Técnico:[/bold]\n"
            for analysis in tech_analysis[:3]:
                content += f"  • {analysis}\n"
        
        panel = Panel(
            content,
            title="[cyan]📈 ANÁLISE TÉCNICA (ADICIONAL)[/cyan]",
            border_style="cyan",
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_price_levels_strategy(self, result):
        """Níveis de Preço Detalhados e Estratégias de Trading"""
        
        data = result.get('data', {})
        current_price = data.get('price', 0)
        
        if current_price == 0:
            return
        
        # Pegar dados do momentum para calcular níveis
        momentum = result.get('momentum_analysis', {})
        history = momentum.get('indicators', {})
        
        # Calcular níveis baseados em dados reais ou estimativas
        ath_distance = history.get('distance_from_ath', 20)  # % do ATH
        atl_distance = history.get('distance_from_atl', -30)  # % do ATL
        
        # Calcular preços de suporte e resistência
        resistance_major = current_price * (1 + abs(ath_distance)/100) if ath_distance < 0 else current_price * 1.3
        resistance_med = current_price * 1.15
        resistance_minor = current_price * 1.07
        
        support_minor = current_price * 0.95
        support_med = current_price * 0.88
        support_major = current_price * (1 - abs(atl_distance)/100) if atl_distance > 0 else current_price * 0.75
        
        content = f"[bold]💰 PREÇO ATUAL: ${current_price:,.2f}[/bold]\n"
        content += f"Variações: 24h [{self._color_percent(data.get('price_change_24h', 0))}], "
        content += f"7d [{self._color_percent(data.get('price_change_7d', 0))}], "
        content += f"30d [{self._color_percent(data.get('price_change_30d', 0))}]\n\n"
        
        content += "[bold]═══════════ MAPA DE PREÇOS ═══════════[/bold]\n\n"
        
        # Resistências
        content += "[red]🎯 RESISTÊNCIAS (Pontos de Realização):[/red]\n"
        content += f"  R3: ${resistance_major:,.2f} ━━━ Resistência Major ({self._calc_percent(current_price, resistance_major):+.1f}%)\n"
        content += f"  R2: ${resistance_med:,.2f} ━━━ Resistência Média ({self._calc_percent(current_price, resistance_med):+.1f}%)\n"
        content += f"  R1: ${resistance_minor:,.2f} ━━━ Resistência Local ({self._calc_percent(current_price, resistance_minor):+.1f}%) 🔴\n\n"
        
        content += f"  [yellow]📍 ${current_price:,.2f} ━━━ [bold]PREÇO ATUAL[/bold] ←─────[/yellow]\n\n"
        
        # Suportes
        content += "[green]🛡️ SUPORTES (Pontos de Entrada):[/green]\n"
        content += f"  S1: ${support_minor:,.2f} ━━━ Suporte Local ({self._calc_percent(current_price, support_minor):.1f}%) 🟢\n"
        content += f"  S2: ${support_med:,.2f} ━━━ Suporte Médio ({self._calc_percent(current_price, support_med):.1f}%)\n"
        content += f"  S3: ${support_major:,.2f} ━━━ Suporte Major ({self._calc_percent(current_price, support_major):.1f}%)\n\n"
        
        # Estratégias baseadas no score
        score = result.get('score', 0)
        
        content += "[bold]═══════════ ESTRATÉGIAS POR PERFIL ═══════════[/bold]\n\n"
        
        if score >= 8:
            content += f"[green]🟢 COMPRADOR (Score Alto: {score}/10):[/green]\n"
            content += f"  • Entrada Imediata: ${current_price:,.2f} (25% posição)\n"
            content += f"  • Entrada em Reteste: ${support_minor:,.2f} (35% posição)\n"
            content += f"  • Entrada em Correção: ${support_med:,.2f} (40% posição)\n"
            content += f"  • Stop Loss: ${support_major:,.2f} ({self._calc_percent(current_price, support_major):.1f}%)\n"
            content += f"  • Alvo 1: ${resistance_minor:,.2f} ({self._calc_percent(current_price, resistance_minor):+.1f}%)\n"
            content += f"  • Alvo 2: ${resistance_med:,.2f} ({self._calc_percent(current_price, resistance_med):+.1f}%)\n"
            content += f"  • Alvo 3: ${resistance_major:,.2f} ({self._calc_percent(current_price, resistance_major):+.1f}%)\n"
            
        elif score >= 5:
            content += f"[yellow]🟡 OBSERVADOR (Score Médio: {score}/10):[/yellow]\n"
            content += f"  • Aguardar: Correção para ${support_minor:,.2f}\n"
            content += f"  • Entrada Principal: ${support_med:,.2f} (60% posição)\n"
            content += f"  • Entrada Adicional: ${support_major:,.2f} (40% posição)\n"
            content += f"  • Stop Loss: {support_major * 0.9:.2f} ({self._calc_percent(support_med, support_major * 0.9):.1f}%)\n"
            content += f"  • Alvo Conservador: ${resistance_minor:,.2f}\n"
            content += f"  • Alvo Otimista: ${resistance_med:,.2f}\n"
            
        else:
            content += f"[red]🔴 EVITAR (Score Baixo: {score}/10):[/red]\n"
            content += f"  • ⚠️ Não recomendado para compra\n"
            content += f"  • Monitorar fundamentos\n"
            content += f"  • Aguardar score > 5 para considerar entrada\n"
            content += f"  • Se já possui: Considerar reduzir exposição\n"
        
        content += "\n[bold]═══════════ GESTÃO DE RISCO ═══════════[/bold]\n\n"
        
        # Tamanho de posição baseado no score
        position_size = self._calculate_position_size(score)
        
        content += f"[bold]⚖️ TAMANHO DE POSIÇÃO SUGERIDO:[/bold]\n"
        content += f"  • Com score {score}/10 → {position_size}% do portfolio crypto\n"
        
        # Ajuste por Fear & Greed
        fg = result.get('market_context', {}).get('fear_greed_index', 50)
        if fg < 30:
            content += f"  • Fear Extremo ({fg}/100) → Pode aumentar +5%\n"
        elif fg > 75:
            content += f"  • Greed Extremo ({fg}/100) → Reduzir -5%\n"
        
        # Risk/Reward
        risk = abs(self._calc_percent(current_price, support_med))
        reward = abs(self._calc_percent(current_price, resistance_minor))
        rr_ratio = reward / risk if risk > 0 else 0
        
        content += f"\n[bold]📊 RISK/REWARD:[/bold]\n"
        content += f"  • Risco: -{risk:.1f}% (até stop)\n"
        content += f"  • Retorno: +{reward:.1f}% (até alvo 1)\n"
        content += f"  • Ratio: 1:{rr_ratio:.1f} "
        
        if rr_ratio >= 2:
            content += "[green](Excelente)[/green]"
        elif rr_ratio >= 1.5:
            content += "[yellow](Bom)[/yellow]"
        elif rr_ratio >= 1:
            content += "[orange1](Aceitável)[/orange1]"
        else:
            content += "[red](Ruim)[/red]"
        
        # DCA Strategy
        content += "\n\n[bold]🔄 ESTRATÉGIA DCA (Dollar Cost Average):[/bold]\n"
        content += "  • 30% na entrada inicial\n"
        content += "  • 30% se cair -5%\n"
        content += "  • 40% se cair -10%\n"
        
        panel = Panel(
            content,
            title="[magenta]💹 NÍVEIS DE PREÇO E ESTRATÉGIA (ADICIONAL)[/magenta]",
            border_style="magenta",
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_hype_detection(self, result):
        """Detecção de Hype e Métricas Sociais"""
        
        hype = result.get('hype_analysis', {})
        social = result.get('social_metrics', {})
        
        if not hype and not social:
            return
        
        content = ""
        
        # Análise de Hype
        if hype:
            hype_level = hype.get('hype_level', 'NORMAL')
            hype_score = hype.get('hype_score', 0)
            hype_color = hype.get('hype_color', 'green')
            
            # Barra visual do hype
            hype_filled = int(hype_score / 5)
            hype_bar = "[red]█[/red]" * hype_filled + "[dim]░[/dim]" * (20 - hype_filled)
            
            content += f"[{hype_color} bold]🌡️ NÍVEL DE HYPE: {hype_level}[/{hype_color} bold]\n"
            content += f"Score: {hype_score}/100 {hype_bar}\n\n"
            
            # Sinais de hype
            if hype.get('signals'):
                content += "[bold]Sinais Detectados:[/bold]\n"
                for signal in hype.get('signals', [])[:4]:
                    content += f"  • {signal}\n"
                content += "\n"
            
            # Recomendações
            if hype.get('recommendations'):
                content += "[bold]💡 Recomendações:[/bold]\n"
                for rec in hype.get('recommendations', [])[:3]:
                    content += f"  • {rec}\n"
                content += "\n"
        
        # Métricas Sociais
        if social and social.get('galaxy_score', 0) > 0:
            content += "[bold]📱 Métricas Sociais:[/bold]\n"
            
            galaxy = social.get('galaxy_score', 0)
            content += f"  • Galaxy Score: {galaxy}/100\n"
            
            social_vol = social.get('social_volume', 0)
            if social_vol:
                content += f"  • Volume Social: {self._format_number(social_vol)} menções/dia\n"
            
            sentiment = social.get('sentiment', '')
            if sentiment:
                content += f"  • Sentimento: {sentiment}\n"
            
            alt_rank = social.get('alt_rank', 999)
            if alt_rank < 999:
                content += f"  • Alt Rank: #{alt_rank}\n"
            
            tweets = social.get('tweets', 0)
            if tweets:
                content += f"  • Tweets: {self._format_number(tweets)}\n"
        
        # Análise final
        if hype:
            content += "\n[bold]📊 Análise Social:[/bold]\n"
            
            if hype.get('hype_score', 0) >= 70:
                content += "  ⚠️ [red]ALERTA: Hype extremo detectado - possível topo local[/red]\n"
            elif hype.get('hype_score', 0) >= 50:
                content += "  ⚠️ [yellow]Hype elevado - cautela com FOMO[/yellow]\n"
            elif hype.get('hype_score', 0) >= 30:
                content += "  📊 [cyan]Interesse crescente - momentum positivo[/cyan]\n"
            else:
                content += "  ✅ [green]Níveis normais - sem sinais de bolha[/green]\n"
        
        if not content:
            return
        
        panel = Panel(
            content,
            title="[yellow]🔥 DETECÇÃO DE HYPE (ADICIONAL)[/yellow]",
            border_style="yellow",
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_onchain_metrics(self, result):
        """Métricas On-Chain e DeFi"""
        
        defi = result.get('defi_metrics', {})
        
        if not defi or defi.get('tvl', 0) == 0:
            return
        
        content = "[bold]🔗 Métricas Blockchain:[/bold]\n\n"
        
        # TVL
        tvl = defi.get('tvl', 0)
        content += f"  • TVL (Total Value Locked): ${self._format_number(tvl)}\n"
        
        # MCap/TVL Ratio
        mcap_tvl = defi.get('mcap_tvl_ratio', 999)
        if mcap_tvl < 999:
            if mcap_tvl < 1:
                content += f"    └─ MCap/TVL: {mcap_tvl:.2f}x [green](Subvalorizado)[/green]\n"
            elif mcap_tvl < 2:
                content += f"    └─ MCap/TVL: {mcap_tvl:.2f}x [yellow](Justo)[/yellow]\n"
            else:
                content += f"    └─ MCap/TVL: {mcap_tvl:.2f}x [red](Sobrevalorizado)[/red]\n"
        
        # Revenue
        revenue_24h = defi.get('revenue_24h', 0)
        if revenue_24h:
            content += f"  • Revenue 24h: ${self._format_number(revenue_24h)}\n"
            revenue_7d = defi.get('revenue_7d', 0)
            if revenue_7d:
                content += f"    └─ Revenue 7d: ${self._format_number(revenue_7d)}\n"
        
        # Chains
        chains = defi.get('chains', [])
        if chains:
            content += f"  • Chains Suportadas: {len(chains)}\n"
            content += f"    └─ Principais: {', '.join(chains[:3])}\n"
        
        # Categoria DeFi
        category = defi.get('category', '')
        if category:
            content += f"  • Categoria: {category.title()}\n"
        
        panel = Panel(
            content,
            title="[blue]⛓️ MÉTRICAS ON-CHAIN (ADICIONAL)[/blue]",
            border_style="blue",
            expand=False
        )
        
        self.console.print(panel)
    
    def _display_disclaimer(self):
        """Disclaimer Legal Importante"""
        
        content = """[bold red]⚠️ AVISO LEGAL IMPORTANTE[/bold red]

Esta análise é [bold]EXCLUSIVAMENTE EDUCACIONAL E INFORMATIVA[/bold].

[red]NÃO CONSTITUI[/red] recomendação de investimento, consultoria financeira ou sugestão de compra/venda.

[bold]RISCOS:[/bold]
- Criptomoedas são ativos de [bold red]ALTÍSSIMO RISCO[/bold red]
- Você pode perder [bold red]TODO[/bold red] seu capital investido
- Mercado extremamente volátil e imprevisível
- Sujeito a manipulação e eventos inesperados

[bold]RECOMENDAÇÕES:[/bold]
- Sempre faça sua própria pesquisa ([bold]DYOR[/bold])
- Nunca invista mais do que pode perder
- Consulte um assessor financeiro profissional
- Diversifique seus investimentos

[dim]Análise gerada em: {}
Fontes: CoinGecko, LunarCrush, DeFiLlama, Alternative.me
Versão: Crypto Analyzer v2024.2.0[/dim]""".format(
            datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        )
        
        panel = Panel(
            content,
            title="[bold red]DISCLAIMER[/bold red]",
            border_style="red",
            expand=False
        )
        
        self.console.print(panel)
        self.console.print()
    
    # ============= MÉTODOS AUXILIARES =============
    
    def _format_number(self, num):
        """Formata números grandes de forma legível"""
        if num >= 1_000_000_000_000:
            return f"{num/1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:
            return f"{num/1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.0f}"
    
    def _calc_percent(self, from_price, to_price):
        """Calcula percentual de diferença entre preços"""
        if from_price == 0:
            return 0
        return ((to_price - from_price) / from_price) * 100
    
    def _color_percent(self, percent):
        """Retorna percentual colorido baseado no valor"""
        if percent > 0:
            return f"[green]{percent:+.1f}%[/green]"
        elif percent < 0:
            return f"[red]{percent:.1f}%[/red]"
        else:
            return f"[yellow]{percent:.1f}%[/yellow]"
    
    def _calculate_position_size(self, score):
        """Calcula tamanho de posição baseado no score"""
        if score >= 9:
            return "15-20"
        elif score >= 8:
            return "12-15"
        elif score >= 7:
            return "10-12"
        elif score >= 6:
            return "8-10"
        elif score >= 5:
            return "5-8"
        elif score >= 4:
            return "3-5"
        else:
            return "0-3"
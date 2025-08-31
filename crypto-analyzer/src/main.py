import sys
import json
import os
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, IntPrompt, Confirm

# Fix para emojis no Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass

from analyzer import CryptoAnalyzer
from config import (
    REPORTS_DIR, ENABLE_LUNARCRUSH, ENABLE_MESSARI, 
    LUNARCRUSH_API_KEY, MESSARI_API_KEY, HybridConfig
)
from enhanced_features import EnhancedAnalyzer
from display_manager import DisplayManager

# Hybrid AI Mode imports
try:
    from hybrid_ai_agent import hybrid_ai_agent, HybridAnalysisResult
    from quota_manager import quota_manager
    from config import HYBRID_MODE_ENABLED
    HYBRID_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Hybrid AI mode not available: {e}")
    HYBRID_AVAILABLE = False
    HYBRID_MODE_ENABLED = False

console = Console(force_terminal=True, legacy_windows=False)

def save_report(result, format_type='json'):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    token_name = result.get('token', 'unknown').lower()
    
    if format_type == 'json':
        filename = f"{token_name}_{timestamp}.json"
        filepath = REPORTS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    elif format_type == 'txt':
        filename = f"{token_name}_{timestamp}.txt"
        filepath = REPORTS_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE ANÁLISE: {result.get('token_name', 'N/A')} ({result.get('token', 'N/A')})\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            if not result['passed_elimination']:
                f.write("ERRO: REJEITADO - Não passou nos critérios eliminatórios\n\n")
                f.write("Motivos da rejeição:\n")
                for reason in result.get('elimination_reasons', []):
                    f.write(f"• {reason}\n")
            else:
                f.write(f"OK DECISÃO: {result['decision']}\n")
                f.write(f"📊 Score: {result['score']}/10\n\n")
                
                if result.get('analysis'):
                    analysis = result['analysis']
                    
                    if analysis.get('strengths'):
                        f.write("💪 PONTOS FORTES:\n")
                        for strength in analysis['strengths']:
                            f.write(f"• {strength}\n")
                        f.write("\n")
                    
                    if analysis.get('weaknesses'):
                        f.write("WARN PONTOS FRACOS:\n")
                        for weakness in analysis['weaknesses']:
                            f.write(f"• {weakness}\n")
                        f.write("\n")
                    
                    if analysis.get('risks'):
                        f.write("🚨 RISCOS:\n")
                        for risk in analysis['risks']:
                            f.write(f"• {risk}\n")
                        f.write("\n")
                
                if result.get('market_context'):
                    context = result['market_context']
                    f.write("🌍 CONTEXTO DE MERCADO:\n")
                    f.write(f"• Fear & Greed Index: {context['fear_greed_index']}/100 ({context['market_sentiment']})\n")
                    f.write(f"• Recomendação: {context['recommendation']}\n\n")
            
            if result.get('data'):
                data = result['data']
                f.write("📈 DADOS FUNDAMENTAIS:\n")
                f.write(f"• Preço: ${data.get('price', 0):,.4f}\n")
                f.write(f"• Market Cap: ${data.get('market_cap', 0):,.0f}\n")
                f.write(f"• Volume 24h: ${data.get('volume', 0):,.0f}\n")
                f.write(f"• Rank: #{data.get('market_cap_rank', 'N/A')}\n")
                f.write(f"• Mudança 24h: {data.get('price_change_24h', 0):+.2f}%\n")
                f.write(f"• Mudança 7d: {data.get('price_change_7d', 0):+.2f}%\n")
                f.write(f"• Mudança 30d: {data.get('price_change_30d', 0):+.2f}%\n")
                f.write(f"• Idade: {data.get('age_days', 0)} dias\n")
        
        return filepath

def display_enhanced_result(result):
    """Exibe resultado usando o novo DisplayManager hierárquico"""
    display = DisplayManager()
    display.display_complete_analysis(result)

def display_enhanced_social_analysis(result):
    """Usa o novo DisplayManager para análise social"""
    display = DisplayManager()
    display.display_complete_analysis(result)

def display_hype_panel(hype_data, token):
    """Display panel com detecção de hype"""
    
    content = [
        f"{hype_data.get('hype_level', '😴 NORMAL')}",
        f"📊 Score de Hype: {hype_data.get('hype_score', 0)}/100",
        f"WARN Risco: {hype_data.get('hype_risk', 'Sem sinais')}",
        ""
    ]
    
    if hype_data.get('signals'):
        content.append("🔍 Sinais Detectados:")
        for signal in hype_data['signals'][:4]:
            content.append(f"• {signal}")
        content.append("")
    
    if hype_data.get('recommendations'):
        content.append("💡 Recomendações:")
        for rec in hype_data['recommendations'][:3]:
            content.append(f"• {rec}")
    
    border_color = hype_data.get('hype_color', 'green')
    console.print(Panel(
        "\n".join(content),
        title=f"🔥 DETECÇÃO DE HYPE: {token.upper()}",
        border_style=border_color,
        expand=False
    ))

def display_social_metrics_panel(social_data, token):
    """Display panel com métricas sociais"""
    
    content = [
        f"⭐ Galaxy Score: {social_data.get('galaxy_score', 0):.1f}",
        f"📊 Volume Social: {social_data.get('social_volume', 0):,}",
        f"👥 Contribuidores: {social_data.get('social_contributors', 0):,}",
        f"🏆 Alt Rank: #{social_data.get('alt_rank', 999)}",
        "",
        f"🐂 Sentimento Bullish: {social_data.get('sentiment_bullish', 50):.0f}%",
        f"🐻 Sentimento Bearish: {social_data.get('sentiment_bearish', 50):.0f}%",
        "",
        f"📱 Tweets: {social_data.get('tweets', 0):,}",
        f"💬 Posts Reddit: {social_data.get('reddit_posts', 0):,}",
        f"📰 Artigos: {social_data.get('news_articles', 0):,}"
    ]
    
    # Calcular mudanças
    social_change = social_data.get('social_volume_change', 0)
    galaxy_change = social_data.get('galaxy_score_change', 0)
    
    if abs(social_change) > 10 or abs(galaxy_change) > 10:
        content.extend([
            "",
            "📈 Mudanças Recentes:"
        ])
        
        if abs(social_change) > 10:
            sign = "📈" if social_change > 0 else "📉"
            content.append(f"• {sign} Volume Social: {social_change:+.0f}%")
        
        if abs(galaxy_change) > 10:
            sign = "⭐" if galaxy_change > 0 else "⭐"
            content.append(f"• {sign} Galaxy Score: {galaxy_change:+.0f}%")
    
    console.print(Panel(
        "\n".join(content),
        title=f"📱 MÉTRICAS SOCIAIS: {token.upper()}",
        border_style="cyan",
        expand=False
    ))

def display_messari_panel(messari_data, token):
    """Display panel com dados Messari"""
    
    content = [
        f"💰 Volume Real 24h: ${messari_data.get('real_volume', 0):,.0f}",
        f"🔄 Volume Turnover: {messari_data.get('volume_turnover', 0):.1f}%",
        f"📊 Volatilidade 30d: {messari_data.get('volatility_30d', 0):.1f}%",
        "",
        f"💎 Supply Y2050: {messari_data.get('y2050_supply', 0):,.0f}",
        f"💧 Supply Líquido: {messari_data.get('liquid_supply', 0):,.0f}",
        f"📈 Inflação Anual: {messari_data.get('annual_inflation', 0):.1f}%",
        "",
        f"👨‍💻 Desenvolvedores: {messari_data.get('developers_count', 0):,}",
        f"👀 Watchers GitHub: {messari_data.get('watchers', 0):,}",
        f"📊 Stock-to-Flow: {messari_data.get('stock_to_flow', 0):.1f}"
    ]
    
    console.print(Panel(
        "\n".join(content),
        title=f"📊 MÉTRICAS FUNDAMENTAIS: {token.upper()}",
        border_style="green",
        expand=False
    ))

def display_defi_panel(defi_data, token):
    """Display panel com dados DeFi"""
    
    content = [
        f"🏦 TVL Atual: ${defi_data.get('tvl_current', 0):,.0f}",
        f"📈 TVL 7d: {defi_data.get('tvl_7d_change', 0):+.1f}%",
        f"📊 TVL 30d: {defi_data.get('tvl_30d_change', 0):+.1f}%",
        f"💎 MCap/TVL: {defi_data.get('mcap_to_tvl', 999):.1f}x",
        "",
        f"💰 Revenue 24h: ${defi_data.get('revenue_24h', 0):,.0f}",
        f"💸 Fees 24h: ${defi_data.get('fees_24h', 0):,.0f}",
        f"📊 APY: {defi_data.get('apy', 0):.1f}%",
        "",
        f"👥 Usuários 24h: {defi_data.get('user_24h', 0):,}",
        f"🔄 Transações 24h: {defi_data.get('tx_count_24h', 0):,}"
    ]
    
    if defi_data.get('main_chain'):
        content.extend([
            "",
            f"⛓️ Chain Principal: {defi_data['main_chain'].title()}",
            f"🏷️ Categoria: {defi_data.get('category', 'unknown').title()}"
        ])
    
    console.print(Panel(
        "\n".join(content),
        title=f"🏦 MÉTRICAS DEFI: {token.upper()}",
        border_style="purple",
        expand=False
    ))

def display_result(result):
    """Redireciona para o novo sistema de display hierárquico"""
    display_enhanced_result(result)

def analyze_token(token_query, use_social=True):
    analyzer = CryptoAnalyzer()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(f"Analisando {token_query.upper()}...", total=None)
        
        try:
            if use_social:
                progress.update(task, description="Coletando dados sociais...")
                result = analyzer.analyze_with_social(token_query)
            else:
                result = analyzer.analyze(token_query)
            progress.update(task, description="Análise concluída!")
            
        except Exception as e:
            console.print(f"[red]Erro durante análise: {e}[/red]")
            return
    
    display_enhanced_result(result)
    
    try:
        json_path = save_report(result, 'json')
        txt_path = save_report(result, 'txt')
        
        console.print(f"\n💾 [dim]Relatórios salvos:[/dim]")
        console.print(f"   [dim]JSON: {json_path.name}[/dim]")
        console.print(f"   [dim]TXT: {txt_path.name}[/dim]")
        
    except Exception as e:
        console.print(f"[yellow]Aviso: Erro ao salvar relatórios: {e}[/yellow]")

def interactive_mode():
    console.print(Panel(
        "[bold blue]Crypto Analyzer v2.0 - Modo Interativo[/bold blue]\n\n"
        "Escolha uma opção:\n"
        "1. Analisar token individual\n"
        "2. Comparar múltiplos tokens\n"
        "3. Modo watch (monitoramento)\n"
        "4. Ver histórico de análises\n"
        "5. Sair\n\n"
        "Ou digite diretamente o nome de um token para análise rápida.",
        border_style="blue"
    ))
    
    enhanced = EnhancedAnalyzer()
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Escolha uma opção ou digite um token[/bold cyan]", default="1")
            
            if user_input.lower() in ['quit', 'exit', 'sair', '5']:
                console.print("[dim]👋 Até logo![/dim]")
                break
            
            if user_input == '1':
                # Análise individual
                token = Prompt.ask("Token para analisar", default="bitcoin")
                use_social = Confirm.ask("Incluir análise social avançada?", default=True)
                
                analyzer = CryptoAnalyzer()
                if use_social:
                    result = analyzer.analyze_with_social(token)
                else:
                    result = analyzer.analyze(token)
                
                if result:
                    enhanced.add_to_history(result)
                display_enhanced_result(result)
                
            elif user_input == '2':
                # Comparação múltipla
                tokens_input = Prompt.ask("Tokens para comparar (separados por espaço)", default="bitcoin ethereum")
                tokens = tokens_input.split()
                comparison = enhanced.compare_tokens(tokens)
                enhanced.display_comparison_table(comparison)
                
                if Confirm.ask("Gerar relatório HTML?"):
                    html_file = enhanced.generate_html_report(comparison)
                    console.print(f"[green]📄 Relatório HTML salvo: {html_file.name}[/green]")
                
            elif user_input == '3':
                # Modo watch
                tokens_input = Prompt.ask("Tokens para monitorar (separados por espaço)", default="bitcoin ethereum")
                tokens = tokens_input.split()
                interval = IntPrompt.ask("Intervalo em minutos", default=5)
                enhanced.watch_tokens(tokens, interval)
                
            elif user_input == '4':
                # Histórico
                limit = IntPrompt.ask("Quantas análises mostrar", default=20)
                enhanced.show_history(limit)
                
            else:
                # Tentar como nome de token
                if user_input.strip():
                    analyzer = CryptoAnalyzer()
                    result = analyzer.analyze_with_social(user_input.strip())
                    if result:
                        enhanced.add_to_history(result)
                    display_enhanced_result(result)
                else:
                    console.print("[yellow]Opção inválida ou token vazio.[/yellow]")
            
        except KeyboardInterrupt:
            console.print("\n[dim]👋 Análise interrompida. Até logo![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Erro inesperado: {e}[/red]")

def show_help():
    # Build help text based on available features
    help_text = (
        "[bold blue]Crypto Analyzer v2024.2.1 - Ajuda[/bold blue]\n\n"
        "[bold]Uso Básico:[/bold]\n"
        "  python main.py                    # Modo interativo\n"
        "  python main.py bitcoin            # Analisar um token\n"
        "  python main.py bitcoin ethereum   # Analisar múltiplos tokens\n\n"
        "[bold]Comandos Especiais:[/bold]\n"
        "  python main.py --compare token1 token2 token3  # Comparar tokens\n"
        "  python main.py --watch token1 token2 [minutos] # Modo watch\n"
        "  python main.py --history                       # Ver histórico\n"
        "  python main.py --help                          # Esta ajuda\n"
    )
    
    # Add hybrid AI commands if available
    if HYBRID_AVAILABLE and HYBRID_MODE_ENABLED:
        help_text += (
            "\n[bold green]Modo Híbrido IA (Novo!):[/bold green]\n"
            "  python main.py bitcoin --hybrid               # Análise híbrida (quant + web)\n"
            "  python main.py --hybrid --compare bitcoin eth # Comparação híbrida\n"
            "  python main.py --hybrid --deep-research BTC   # Research profundo\n"
            "  python main.py --hybrid-status                # Status das APIs\n"
            "  python main.py --quota-status                 # Status das quotas\n\n"
            "[bold green]Flags Híbridas:[/bold green]\n"
            "  --hybrid                      # Ativar análise híbrida\n"
            "  --deep-research               # Research profundo com múltiplas fontes\n"
            "  --sentiment-focus             # Foco em análise de sentimento\n"
            "  --narrative-analysis          # Detectar mudanças narrativas\n"
        )
    elif not HYBRID_AVAILABLE:
        help_text += (
            "\n[bold yellow]Modo Híbrido IA:[/bold yellow]\n"
            "  [dim]Não disponível - instale dependências:[/dim]\n"
            "  [dim]pip install tavily-python beautifulsoup4 textblob[/dim]\n"
        )
    
    help_text += (
        "\n[bold]Exemplos:[/bold]\n"
        "  python main.py --compare bitcoin ethereum solana\n"
        "  python main.py --watch bitcoin ethereum 10\n"
        "  python main.py --history\n"
    )
    
    if HYBRID_AVAILABLE and HYBRID_MODE_ENABLED:
        help_text += (
            "  python main.py bitcoin --hybrid\n"
            "  python main.py --hybrid --deep-research ethereum\n"
        )
    
    help_text += (
        "\n[bold]Arquivos gerados:[/bold]\n"
        "  reports/[token]_[data].json       # Dados completos\n"
        "  reports/[token]_[data].txt        # Relatório legível\n"
        "  reports/comparison_[data].html    # Comparação com gráficos\n"
        "  data/analysis_history.json       # Histórico de análises"
    )
    
    if HYBRID_AVAILABLE:
        help_text += (
            "\n  data/api_quotas.json             # Status quotas APIs\n"
            "  data/web_cache/                  # Cache web research"
        )
    
    console.print(Panel(help_text, border_style="blue"))

def show_api_status():
    """Mostra quais APIs estão habilitadas"""
    
    console.print("\n[bold blue]Status das APIs:[/bold blue]")
    console.print("[green]OK[/green] CoinGecko: Ativo (sem key necessária)")
    console.print("[green]OK[/green] DeFiLlama: Ativo (sem key necessária)")
    console.print("[green]OK[/green] Fear & Greed: Ativo (sem key necessária)")
    
    if ENABLE_LUNARCRUSH:
        console.print(f"[green]OK[/green] LunarCrush: Ativo (com API key)")
    else:
        console.print(f"[yellow]--[/yellow] LunarCrush: Desabilitado (configure LUNARCRUSH_API_KEY)")
    
    if ENABLE_MESSARI:
        console.print(f"[green]OK[/green] Messari: Ativo (com API key)")
    else:
        console.print(f"[dim]--[/dim] Messari: Desabilitado (opcional)")
    
    # Show Hybrid AI status
    if HYBRID_AVAILABLE:
        console.print(f"\n[bold green]Modo Híbrido IA:[/bold green]")
        
        if HYBRID_MODE_ENABLED:
            available_apis = HybridConfig.get_available_apis()
            console.print(f"[green]OK[/green] Híbrido: Ativo ({len(available_apis)} APIs disponíveis)")
            
            # Show individual API status
            from config import API_AVAILABILITY
            for api_name, is_available in API_AVAILABILITY.items():
                if is_available:
                    console.print(f"[green] +[/green] {api_name.replace('_', ' ').title()}: Disponível")
                else:
                    console.print(f"[yellow] --[/yellow] {api_name.replace('_', ' ').title()}: Não configurado")
                    
            # Show priority tokens
            priority_tokens = HybridConfig.get_hybrid_status()['priority_tokens']
            console.print(f"[dim] • Tokens prioritários: {', '.join(priority_tokens[:3])}{'...' if len(priority_tokens) > 3 else ''}[/dim]")
        else:
            console.print(f"[yellow]--[/yellow] Híbrido: Desabilitado (configure HYBRID_MODE_ENABLED=true)")
    else:
        console.print(f"\n[yellow]Modo Híbrido IA:[/yellow]")
        console.print(f"[yellow]--[/yellow] Não disponível (instale dependências)")
    
    if not ENABLE_LUNARCRUSH:
        console.print("\n[dim]Para habilitar análise social completa:[/dim]")
        console.print("[dim]1. Obtenha API key em https://lunarcrush.com/developers[/dim]")
        console.print("[dim]2. Configure LUNARCRUSH_API_KEY no arquivo .env[/dim]")
        console.print("[dim]3. Ou defina a variável de ambiente[/dim]")
    
    if HYBRID_AVAILABLE and not HYBRID_MODE_ENABLED:
        console.print("\n[dim]Para habilitar modo híbrido IA:[/dim]")
        console.print("[dim]1. Configure HYBRID_MODE_ENABLED=true no .env[/dim]")
        console.print("[dim]2. Opcionalmente configure APIs premium (Tavily, You.com, SerpAPI)[/dim]")
        console.print("[dim]3. Use --hybrid para análises com contexto web[/dim]")
    
    print()


def perform_hybrid_analysis(token: str, analysis_type: str = "comprehensive") -> dict:
    """Perform hybrid analysis for a token"""
    
    if not HYBRID_AVAILABLE or not HYBRID_MODE_ENABLED:
        console.print("[red]ERRO: Modo híbrido não disponível[/red]")
        return None
    
    console.print(f"\n[bold green]Iniciando análise híbrida: {token.upper()}[/bold green]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Traditional analysis
        task1 = progress.add_task("[green]Análise quantitativa...", total=None)
        
        try:
            analyzer = CryptoAnalyzer()
            traditional_result = analyzer.analyze_with_social(token)
            
            if not traditional_result or not traditional_result.get('success'):
                progress.update(task1, completed=True)
                console.print(f"[red]ERRO: Erro na análise quantitativa de {token}[/red]")
                return None
            
            progress.update(task1, completed=True)
            
            # Step 2: Web research
            task2 = progress.add_task("[blue]Pesquisa web inteligente...", total=None)
            
            hybrid_result = hybrid_ai_agent.analyze_with_web_context(token, traditional_result)
            progress.update(task2, completed=True)
            
            # Step 3: Generate insights
            task3 = progress.add_task("[yellow]Gerando insights híbridos...", total=None)
            
            contextual_insights = hybrid_ai_agent.generate_contextual_insights({
                'quantitative_analysis': traditional_result,
                'web_research': hybrid_result.web_research,
                'hybrid_insights': hybrid_result.hybrid_insights,
                'final_recommendation': hybrid_result.final_recommendation
            })
            
            progress.update(task3, completed=True)
            
            # Combine all results
            complete_result = {
                'token': token,
                'analysis_type': 'hybrid',
                'timestamp': hybrid_result.timestamp,
                'quantitative_analysis': traditional_result,
                'web_research': hybrid_result.web_research.__dict__ if hybrid_result.web_research else None,
                'hybrid_insights': hybrid_result.hybrid_insights,
                'contextual_score_adjustment': hybrid_result.contextual_score_adjustment,
                'final_recommendation': hybrid_result.final_recommendation,
                'confidence_level': hybrid_result.confidence_level,
                'processing_time': hybrid_result.processing_time,
                'contextual_insights': contextual_insights,
                'success': True
            }
            
            return complete_result
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]ERRO: Erro na análise híbrida: {e}[/red]")
            return None


def display_hybrid_result(result: dict):
    """Display hybrid analysis result using DisplayManager"""
    
    if not result or not result.get('success'):
        console.print("[red]ERRO: Nenhum resultado para exibir[/red]")
        return
    
    try:
        display_manager = DisplayManager()
        
        # Use enhanced display for hybrid results
        display_manager.display_hybrid_analysis(result)
        
        # Show quota usage if available
        if HYBRID_AVAILABLE:
            quota_stats = quota_manager.get_usage_stats(days=1)
            if quota_stats.get('total_requests', 0) > 0:
                console.print(f"\n[dim]📊 Uso hoje: {quota_stats['total_requests']} requests, "
                            f"${quota_stats.get('estimated_monthly_cost', 0):.4f} custos[/dim]")
        
    except Exception as e:
        console.print(f"[red]Erro ao exibir resultado híbrido: {e}[/red]")
        # Fallback to traditional display
        display_enhanced_result(result.get('quantitative_analysis', result))


def show_hybrid_status():
    """Show detailed hybrid mode status"""
    
    if not HYBRID_AVAILABLE:
        console.print("[red]ERRO: Modo híbrido não disponível[/red]")
        console.print("[dim]Instale dependências: pip install tavily-python beautifulsoup4 textblob[/dim]")
        return
    
    status = HybridConfig.get_hybrid_status()
    
    console.print(Panel(
        f"[bold green]Status do Modo Híbrido IA[/bold green]\n\n"
        f"[bold]Configuração:[/bold]\n"
        f"• Habilitado: {'[green]Sim[/green]' if status['enabled'] else '[red]Não[/red]'}\n"
        f"• APIs Disponíveis: {len(status['available_apis'])}\n"
        f"• Tokens Prioritários: {len(status['priority_tokens'])}\n\n"
        f"[bold]APIs Configuradas:[/bold]\n" +
        '\n'.join([f"• {api.title().replace('_', ' ')}: [green]OK[/green]" for api in status['available_apis']]) + "\n\n"
        f"[bold]Cache:[/bold]\n"
        f"• Web Research: {status['cache_settings']['web_research']}s\n"
        f"• Sentiment: {status['cache_settings']['sentiment']}s\n"
        f"• News: {status['cache_settings']['news']}s\n\n"
        f"[bold]Features:[/bold]\n" +
        '\n'.join([f"• {feature.replace('_', ' ').title()}: {'[green]OK[/green]' if enabled else '[red]OFF[/red]'}" 
                  for feature, enabled in status['features'].items()]),
        title="Hybrid AI Status",
        border_style="green"
    ))


def show_quota_status():
    """Show API quota status"""
    
    if not HYBRID_AVAILABLE:
        console.print("[red]ERRO: Modo híbrido não disponível - quotas não aplicáveis[/red]")
        return
    
    status = quota_manager.get_quota_status()
    
    table = Table(title="📊 Status das Quotas de API")
    table.add_column("API", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Diário", justify="right")
    table.add_column("Por Hora", justify="right") 
    table.add_column("Custo Est.", justify="right")
    table.add_column("Qualidade", justify="center")
    
    for api_name, api_status in status['providers'].items():
        # Status indicator
        if not api_status['api_key_configured']:
            status_indicator = "[red]ERRO: Sem key[/red]"
        elif api_status['monthly_remaining'] <= 0:
            status_indicator = "[red]ERRO: Esgotado[/red]"
        elif api_status['hourly_remaining'] <= 0:
            status_indicator = "[yellow]WARN Rate limit[/yellow]"
        else:
            status_indicator = "[green]OK Ativo[/green]"
        
        # Daily usage
        daily_usage = f"{api_status['monthly_usage']}/{api_status['monthly_limit']}"
        
        # Hourly usage
        hourly_usage = f"{api_status['hourly_usage']}/{api_status['hourly_limit']}"
        
        # Cost
        cost = f"${api_status['estimated_monthly_cost']:.4f}"
        
        # Quality score
        quality = f"{api_status['quality_score']}/10"
        
        table.add_row(
            api_name.title(),
            status_indicator,
            daily_usage,
            hourly_usage,
            cost,
            quality
        )
    
    console.print(table)
    
    # Show usage summary
    usage_stats = quota_manager.get_usage_stats(days=30)
    console.print(f"\n[dim]📈 Últimos 30 dias: {usage_stats['total_requests']} requests, "
                  f"{usage_stats['successful_requests']} sucessos, "
                  f"${usage_stats.get('estimated_monthly_cost', 0):.4f} custos[/dim]")


def hybrid_comparison(tokens: list, analysis_focus: str = "comprehensive"):
    """Perform hybrid comparison of multiple tokens"""
    
    if not HYBRID_AVAILABLE or not HYBRID_MODE_ENABLED:
        console.print("[red]ERRO: Modo híbrido não disponível para comparação[/red]")
        return
    
    if len(tokens) < 2:
        console.print("[red]ERRO: Pelo menos 2 tokens necessários para comparação híbrida[/red]")
        return
    
    console.print(f"\n[bold green]Comparação Híbrida: {', '.join(tokens).upper()}[/bold green]")
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        for i, token in enumerate(tokens):
            task = progress.add_task(f"[cyan]Analisando {token.upper()}...", total=None)
            
            result = perform_hybrid_analysis(token, analysis_focus)
            if result:
                results.append(result)
            
            progress.update(task, completed=True)
    
    if not results:
        console.print("[red]ERRO: Nenhum resultado obtido para comparação[/red]")
        return
    
    # Display comparison results
    try:
        display_manager = DisplayManager()
        display_manager.display_hybrid_comparison(results)
        
        # Save comparison report
        comparison_data = {
            'comparison_type': 'hybrid',
            'analysis_focus': analysis_focus,
            'timestamp': datetime.now().isoformat(),
            'tokens': results,
            'summary': generate_comparison_summary(results)
        }
        
        try:
            json_path = save_report(comparison_data, 'json')
            console.print(f"\n💾 [dim]Comparação híbrida salva: {json_path.name}[/dim]")
        except Exception as e:
            console.print(f"[yellow]Aviso: Erro ao salvar comparação: {e}[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Erro na comparação híbrida: {e}[/red]")


def generate_comparison_summary(results: list) -> dict:
    """Generate summary for hybrid comparison"""
    
    if not results:
        return {}
    
    summary = {
        'total_tokens': len(results),
        'highest_score': None,
        'highest_confidence': None,
        'most_bullish_sentiment': None,
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    try:
        # Find highest scoring token
        scores = []
        for result in results:
            final_rec = result.get('final_recommendation', {})
            adjusted_score = final_rec.get('adjusted_score', 0)
            if adjusted_score:
                scores.append((result['token'], adjusted_score))
        
        if scores:
            summary['highest_score'] = max(scores, key=lambda x: x[1])
        
        # Find highest confidence
        confidences = []
        for result in results:
            confidence = result.get('confidence_level', 0)
            if confidence:
                confidences.append((result['token'], confidence))
        
        if confidences:
            summary['highest_confidence'] = max(confidences, key=lambda x: x[1])
        
        # Find most bullish sentiment
        sentiments = []
        for result in results:
            web_research = result.get('web_research', {})
            if web_research:
                sentiment_analysis = web_research.get('sentiment_analysis', {})
                overall_sentiment = sentiment_analysis.get('overall_sentiment', 0.5)
                sentiments.append((result['token'], overall_sentiment))
        
        if sentiments:
            summary['most_bullish_sentiment'] = max(sentiments, key=lambda x: x[1])
    
    except Exception as e:
        summary['error'] = str(e)
    
    return summary


def main():
    console.print("[bold blue]Crypto Analyzer v2024.2.1[/bold blue]")
    
    # Mostra status das APIs no início
    show_api_status()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ['--help', '-h', 'help']:
            show_help()
            return
        
        elif command == '--compare':
            if len(sys.argv) < 4:
                console.print("[red]ERRO: Uso: python main.py --compare token1 token2 [token3 ...][/red]")
                return
            
            tokens = sys.argv[2:]
            enhanced = EnhancedAnalyzer()
            comparison = enhanced.compare_tokens(tokens)
            enhanced.display_comparison_table(comparison)
            enhanced.display_comparison_panels(comparison)
            
            if Confirm.ask("\nGerar relatório HTML com gráficos?"):
                html_file = enhanced.generate_html_report(comparison)
                console.print(f"[green]📄 Relatório HTML salvo: {html_file.name}[/green]")
                console.print(f"[blue]🌐 Abra o arquivo no navegador para ver os gráficos[/blue]")
        
        elif command == '--watch':
            if len(sys.argv) < 3:
                console.print("[red]ERRO: Uso: python main.py --watch token1 [token2 ...] [minutos][/red]")
                return
            
            # Separar tokens de intervalo
            args = sys.argv[2:]
            interval = 5  # padrão
            tokens = []
            
            for arg in args:
                if arg.isdigit():
                    interval = int(arg)
                else:
                    tokens.append(arg)
            
            if not tokens:
                console.print("[red]ERRO: Pelo menos um token deve ser especificado[/red]")
                return
            
            enhanced = EnhancedAnalyzer()
            enhanced.watch_tokens(tokens, interval)
        
        elif command == '--history':
            limit = 20
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                limit = int(sys.argv[2])
            
            enhanced = EnhancedAnalyzer()
            enhanced.show_history(limit)
        
        # Hybrid AI Mode commands
        elif command == '--hybrid-status':
            show_hybrid_status()
            return
            
        elif command == '--quota-status':
            show_quota_status()
            return
            
        elif command in ['--hybrid', '--deep-research', '--sentiment-focus', '--narrative-analysis']:
            # Parse hybrid mode arguments
            hybrid_mode = True
            analysis_focus = "comprehensive"
            tokens_to_analyze = []
            
            # Determine analysis focus based on command
            if command == '--deep-research':
                analysis_focus = "deep_research"
            elif command == '--sentiment-focus':
                analysis_focus = "sentiment"
            elif command == '--narrative-analysis':
                analysis_focus = "narrative"
            
            # Extract tokens and additional flags
            i = 1
            while i < len(sys.argv):
                arg = sys.argv[i]
                
                if arg == '--compare' and i + 1 < len(sys.argv):
                    # Hybrid comparison mode
                    remaining_args = sys.argv[i+1:]
                    if len(remaining_args) >= 2:
                        hybrid_comparison(remaining_args, analysis_focus)
                        return
                    else:
                        console.print("[red]ERRO: Uso: python main.py --hybrid --compare token1 token2 [token3 ...][/red]")
                        return
                
                elif arg not in ['--hybrid', '--deep-research', '--sentiment-focus', '--narrative-analysis']:
                    tokens_to_analyze.append(arg)
                
                i += 1
            
            if not tokens_to_analyze:
                console.print("[red]ERRO: Especifique pelo menos um token para análise híbrida[/red]")
                console.print("[dim]Exemplo: python main.py bitcoin --hybrid[/dim]")
                return
            
            # Perform hybrid analysis for tokens
            for token in tokens_to_analyze:
                result = perform_hybrid_analysis(token, analysis_focus)
                
                if result:
                    # Add to history if available
                    if 'enhanced' in locals():
                        enhanced = EnhancedAnalyzer()
                        enhanced.add_to_history(result)
                    
                    # Display result
                    display_hybrid_result(result)
                    
                    # Save reports
                    try:
                        json_path = save_report(result, 'json')
                        console.print(f"\n💾 [dim]Relatório híbrido salvo: {json_path.name}[/dim]")
                    except Exception as e:
                        console.print(f"[yellow]Aviso: Erro ao salvar relatório: {e}[/yellow]")
                    
                    # Add separator for multiple tokens
                    if len(tokens_to_analyze) > 1 and token != tokens_to_analyze[-1]:
                        console.print("\n" + "="*80 + "\n")
        
        else:
            # Análise tradicional de tokens
            tokens = sys.argv[1:]
            enhanced = EnhancedAnalyzer()
            
            if len(tokens) == 1:
                # Análise individual
                analyzer = CryptoAnalyzer()
                result = analyzer.analyze_with_social(tokens[0])
                if result:
                    enhanced.add_to_history(result)
                display_enhanced_result(result)
                
                # Salvar relatórios
                try:
                    json_path = save_report(result, 'json')
                    txt_path = save_report(result, 'txt')
                    console.print(f"\n💾 [dim]Relatórios salvos:[/dim]")
                    console.print(f"   [dim]JSON: {json_path.name}[/dim]")
                    console.print(f"   [dim]TXT: {txt_path.name}[/dim]")
                except Exception as e:
                    console.print(f"[yellow]Aviso: Erro ao salvar relatórios: {e}[/yellow]")
            else:
                # Comparação múltipla
                comparison = enhanced.compare_tokens(tokens)
                enhanced.display_comparison_table(comparison)
                
                if Confirm.ask("\nGerar relatório HTML com gráficos?", default=True):
                    html_file = enhanced.generate_html_report(comparison)
                    console.print(f"[green]📄 Relatório HTML salvo: {html_file.name}[/green]")
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
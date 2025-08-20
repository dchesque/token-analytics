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
    LUNARCRUSH_API_KEY, MESSARI_API_KEY
)
from enhanced_features import EnhancedAnalyzer
from display_manager import DisplayManager

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
                f.write("❌ REJEITADO - Não passou nos critérios eliminatórios\n\n")
                f.write("Motivos da rejeição:\n")
                for reason in result.get('elimination_reasons', []):
                    f.write(f"• {reason}\n")
            else:
                f.write(f"✅ DECISÃO: {result['decision']}\n")
                f.write(f"📊 Score: {result['score']}/10\n\n")
                
                if result.get('analysis'):
                    analysis = result['analysis']
                    
                    if analysis.get('strengths'):
                        f.write("💪 PONTOS FORTES:\n")
                        for strength in analysis['strengths']:
                            f.write(f"• {strength}\n")
                        f.write("\n")
                    
                    if analysis.get('weaknesses'):
                        f.write("⚠️ PONTOS FRACOS:\n")
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
        f"⚠️ Risco: {hype_data.get('hype_risk', 'Sem sinais')}",
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
    console.print(Panel(
        "[bold blue]Crypto Analyzer v2.0 - Ajuda[/bold blue]\n\n"
        "[bold]Uso Básico:[/bold]\n"
        "  python main.py                    # Modo interativo\n"
        "  python main.py bitcoin            # Analisar um token\n"
        "  python main.py bitcoin ethereum   # Analisar múltiplos tokens\n\n"
        "[bold]Comandos Especiais:[/bold]\n"
        "  python main.py --compare token1 token2 token3  # Comparar tokens\n"
        "  python main.py --watch token1 token2 [minutos] # Modo watch\n"
        "  python main.py --history                       # Ver histórico\n"
        "  python main.py --help                          # Esta ajuda\n\n"
        "[bold]Exemplos:[/bold]\n"
        "  python main.py --compare bitcoin ethereum solana\n"
        "  python main.py --watch bitcoin ethereum 10\n"
        "  python main.py --history\n\n"
        "[bold]Arquivos gerados:[/bold]\n"
        "  reports/[token]_[data].json       # Dados completos\n"
        "  reports/[token]_[data].txt        # Relatório legível\n"
        "  reports/comparison_[data].html    # Comparação com gráficos\n"
        "  data/analysis_history.json       # Histórico de análises",
        border_style="blue"
    ))

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
    
    if not ENABLE_LUNARCRUSH:
        console.print("\n[dim]Para habilitar análise social completa:[/dim]")
        console.print("[dim]1. Obtenha API key em https://lunarcrush.com/developers[/dim]")
        console.print("[dim]2. Configure LUNARCRUSH_API_KEY no arquivo .env[/dim]")
        console.print("[dim]3. Ou defina a variável de ambiente[/dim]")
    
    print()

def main():
    console.print("[bold blue]Crypto Analyzer v2.0[/bold blue]")
    
    # Mostra status das APIs no início
    show_api_status()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command in ['--help', '-h', 'help']:
            show_help()
            return
        
        elif command == '--compare':
            if len(sys.argv) < 4:
                console.print("[red]❌ Uso: python main.py --compare token1 token2 [token3 ...][/red]")
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
                console.print("[red]❌ Uso: python main.py --watch token1 [token2 ...] [minutos][/red]")
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
                console.print("[red]❌ Pelo menos um token deve ser especificado[/red]")
                return
            
            enhanced = EnhancedAnalyzer()
            enhanced.watch_tokens(tokens, interval)
        
        elif command == '--history':
            limit = 20
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                limit = int(sys.argv[2])
            
            enhanced = EnhancedAnalyzer()
            enhanced.show_history(limit)
        
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
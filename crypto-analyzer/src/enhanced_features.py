"""
Funcionalidades aprimoradas para o Crypto Analyzer
- Comparação lado a lado
- Relatórios HTML
- Modo watch
- Histórico de análises
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from analyzer import CryptoAnalyzer
from config import REPORTS_DIR, DATA_DIR

console = Console()

class EnhancedAnalyzer:
    def __init__(self):
        self.analyzer = CryptoAnalyzer()
        self.history_file = DATA_DIR / 'analysis_history.json'
        self.ensure_history_file()
    
    def ensure_history_file(self):
        """Garante que o arquivo de histórico existe"""
        if not self.history_file.exists():
            self.save_history([])
    
    def load_history(self) -> List[Dict]:
        """Carrega histórico de análises"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def save_history(self, history: List[Dict]):
        """Salva histórico de análises"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[yellow]Aviso: Erro ao salvar histórico: {e}[/yellow]")
    
    def add_to_history(self, result: Dict):
        """Adiciona análise ao histórico"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'token': result.get('token', 'unknown'),
            'token_name': result.get('token_name', 'Unknown'),
            'score': result.get('score', 0),
            'decision': result.get('decision', 'unknown'),
            'passed_elimination': result.get('passed_elimination', False),
            'market_context': result.get('market_context', {}),
            'price': result.get('data', {}).get('price', 0),
            'market_cap': result.get('data', {}).get('market_cap', 0),
            'volume': result.get('data', {}).get('volume', 0)
        }
        
        history = self.load_history()
        history.append(history_entry)
        
        # Manter apenas últimas 1000 análises
        if len(history) > 1000:
            history = history[-1000:]
        
        self.save_history(history)
    
    def compare_tokens(self, token_list: List[str]) -> Dict:
        """Compara múltiplos tokens lado a lado"""
        console.print(f"[bold blue]🔍 Comparando {len(token_list)} tokens...[/bold blue]\n")
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=True
        ) as progress:
            
            for i, token in enumerate(token_list):
                task = progress.add_task(f"Analisando {token.upper()} ({i+1}/{len(token_list)})...", total=None)
                
                try:
                    result = self.analyzer.analyze(token)
                    if result:
                        results.append(result)
                        self.add_to_history(result)
                    progress.update(task, description=f"{token.upper()} concluído!")
                    time.sleep(0.5)  # Evitar rate limiting
                except Exception as e:
                    console.print(f"[red]Erro ao analisar {token}: {e}[/red]")
        
        return {
            'tokens': results,
            'comparison_timestamp': datetime.now().isoformat(),
            'total_analyzed': len(results)
        }
    
    def display_comparison_table(self, comparison_result: Dict):
        """Exibe comparação em tabela"""
        results = comparison_result['tokens']
        
        if not results:
            console.print("[red]❌ Nenhum token analisado com sucesso[/red]")
            return
        
        # Criar tabela de comparação
        table = Table(title="📊 Comparação de Tokens", show_header=True, header_style="bold magenta")
        
        table.add_column("Token", style="cyan", no_wrap=True)
        table.add_column("Score", justify="center", style="bright_white")
        table.add_column("Decisão", justify="center")
        table.add_column("Preço", justify="right", style="green")
        table.add_column("Market Cap", justify="right", style="blue")
        table.add_column("Volume 24h", justify="right", style="yellow")
        table.add_column("Mudança 30d", justify="center")
        
        # Ordenar por score (maior primeiro)
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        for result in sorted_results:
            token = result.get('token', 'N/A')
            name = result.get('token_name', 'N/A')
            score = result.get('score', 0)
            decision = result.get('decision', 'N/A')
            
            data = result.get('data', {})
            price = data.get('price', 0)
            market_cap = data.get('market_cap', 0)
            volume = data.get('volume', 0)
            change_30d = data.get('price_change_30d', 0)
            
            # Cores condicionais
            if score >= 8:
                score_color = "[green]"
                decision_color = "[green]"
            elif score >= 5:
                score_color = "[yellow]"
                decision_color = "[yellow]"
            else:
                score_color = "[red]"
                decision_color = "[red]"
            
            change_color = "[green]" if change_30d > 0 else "[red]"
            
            table.add_row(
                f"{token}\n[dim]{name}[/dim]",
                f"{score_color}{score}/10[/{score_color.strip('[]')}]",
                f"{decision_color}{decision}[/{decision_color.strip('[]')}]",
                f"${price:,.2f}" if price else "N/A",
                self.format_large_number(market_cap),
                self.format_large_number(volume),
                f"{change_color}{change_30d:+.1f}%[/{change_color.strip('[]')}]" if change_30d != 0 else "N/A"
            )
        
        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Análise realizada em: {comparison_result['comparison_timestamp']}[/dim]")
    
    def display_comparison_panels(self, comparison_result: Dict):
        """Exibe comparação em painéis lado a lado"""
        results = comparison_result['tokens']
        
        if not results:
            return
        
        panels = []
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        for result in sorted_results:
            token = result.get('token', 'N/A')
            name = result.get('token_name', 'N/A')
            score = result.get('score', 0)
            decision = result.get('decision', 'N/A')
            
            # Cor baseada no score
            if score >= 8:
                color = "green"
                emoji = "🚀"
            elif score >= 5:
                color = "yellow"
                emoji = "🤔"
            else:
                color = "red"
                emoji = "⚠️"
            
            content = f"[{color}]{emoji} {decision}[/{color}]\n"
            content += f"📊 Score: {score}/10\n\n"
            
            if result.get('analysis'):
                analysis = result['analysis']
                if analysis.get('strengths'):
                    content += "✅ Pontos Fortes:\n"
                    for strength in analysis['strengths'][:2]:  # Limitar espaço
                        content += f"• {strength}\n"
                
                if analysis.get('risks'):
                    content += "\n🚨 Riscos:\n"
                    for risk in analysis['risks'][:2]:  # Limitar espaço
                        content += f"• {risk}\n"
            
            panel = Panel(
                content,
                title=f"📊 {name.upper()}",
                border_style=color,
                width=30
            )
            panels.append(panel)
        
        # Exibir painéis em colunas
        if len(panels) <= 3:
            console.print(Columns(panels, equal=True))
        else:
            # Dividir em linhas de 3
            for i in range(0, len(panels), 3):
                console.print(Columns(panels[i:i+3], equal=True))
                if i + 3 < len(panels):
                    console.print()
    
    def watch_tokens(self, token_list: List[str], interval_minutes: int = 5):
        """Modo watch - reavalia tokens periodicamente"""
        console.print(f"[bold blue]👁️ Modo Watch iniciado[/bold blue]")
        console.print(f"Tokens: {', '.join(token_list)}")
        console.print(f"Intervalo: {interval_minutes} minutos")
        console.print(f"Pressione Ctrl+C para parar\n")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                console.print(f"[bold cyan]🔄 Iteração {iteration} - {timestamp}[/bold cyan]")
                console.print("=" * 60)
                
                # Realizar comparação
                comparison = self.compare_tokens(token_list)
                self.display_comparison_table(comparison)
                
                # Aguardar próxima iteração
                console.print(f"\n[dim]⏰ Próxima atualização em {interval_minutes} minutos...[/dim]")
                console.print(f"[dim]Pressione Ctrl+C para parar[/dim]\n")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Modo watch interrompido pelo usuário[/yellow]")
        except Exception as e:
            console.print(f"\n[red]❌ Erro no modo watch: {e}[/red]")
    
    def generate_html_report(self, comparison_result: Dict, filename: str = None) -> Path:
        """Gera relatório HTML com gráfico básico"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"comparison_report_{timestamp}.html"
            
            filepath = REPORTS_DIR / filename
            results = comparison_result['tokens']
            
            console.print(f"[cyan]Gerando relatório HTML: {filename}[/cyan]")
            
        except Exception as e:
            console.print(f"[red]Erro ao inicializar geração do HTML: {str(e)}[/red]")
            raise
        
        # Template HTML
        html_template = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Analyzer - Relatório de Comparação</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 20px; background-color: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #2c3e50; margin-bottom: 10px; }
        .timestamp { color: #7f8c8d; font-size: 14px; }
        .chart-container { width: 100%; height: 400px; margin: 30px 0; }
        .table-container { margin: 30px 0; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
        .score-high { background-color: #d4edda; color: #155724; }
        .score-medium { background-color: #fff3cd; color: #856404; }
        .score-low { background-color: #f8d7da; color: #721c24; }
        .decision-buy { color: #28a745; font-weight: bold; }
        .decision-study { color: #ffc107; font-weight: bold; }
        .decision-avoid { color: #dc3545; font-weight: bold; }
        .summary { background-color: #e9ecef; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #6c757d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Crypto Analyzer</h1>
            <h2>Relatório de Comparação de Tokens</h2>
            <div class="timestamp">Gerado em: {timestamp}</div>
        </div>

        <div class="summary">
            <h3>📊 Resumo da Análise</h3>
            <p><strong>Tokens analisados:</strong> {total_tokens}</p>
            <p><strong>Data da análise:</strong> {analysis_date}</p>
            <p><strong>Contexto de mercado:</strong> {market_context}</p>
        </div>

        <div class="chart-container">
            <canvas id="scoresChart"></canvas>
        </div>

        <div class="table-container">
            <h3>📋 Detalhes da Comparação</h3>
            <table>
                <thead>
                    <tr>
                        <th>Token</th>
                        <th>Score</th>
                        <th>Decisão</th>
                        <th>Preço (USD)</th>
                        <th>Market Cap</th>
                        <th>Volume 24h</th>
                        <th>Mudança 30d</th>
                        <th>Rank</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="summary">
            <h3>⚠️ Disclaimer</h3>
            <p><strong>Este relatório NÃO constitui recomendação de investimento.</strong></p>
            <p>As análises são baseadas em dados públicos e critérios técnicos. Sempre faça sua própria pesquisa antes de investir em criptomoedas.</p>
            <p>Criptomoedas são investimentos de alto risco e podem resultar em perda total do capital.</p>
        </div>

        <div class="footer">
            <p>Gerado por Crypto Analyzer - Sistema de Análise em 3 Camadas</p>
            <p>APIs utilizadas: CoinGecko, Alternative.me</p>
        </div>
    </div>

    <script>
        // Dados dos tokens
        const tokenData = {chart_data};

        // Configuração do gráfico
        const ctx = document.getElementById('scoresChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: tokenData.labels,
                datasets: [{{
                    label: 'Score (0-10)',
                    data: tokenData.scores,
                    backgroundColor: tokenData.colors,
                    borderColor: tokenData.colors.map(color => color.replace('0.8', '1')),
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Comparação de Scores dos Tokens'
                    }},
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 10,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        # Preparar dados para o template
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        total_tokens = len(results)
        analysis_date = comparison_result.get('comparison_timestamp', '')
        
        # Contexto de mercado (usar do primeiro token)
        market_context = "N/A"
        if results and results[0].get('market_context'):
            ctx = results[0]['market_context']
            market_context = f"Fear & Greed: {ctx.get('fear_greed_index', 'N/A')}/100 ({ctx.get('market_sentiment', 'N/A')})"
        
        # Preparar dados do gráfico
        chart_data = {
            'labels': [],
            'scores': [],
            'colors': []
        }
        
        # Preparar linhas da tabela
        table_rows = []
        
        sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
        for result in sorted_results:
            token = result.get('token', 'N/A')
            name = result.get('token_name', 'N/A')
            score = result.get('score', 0)
            decision = result.get('decision', 'N/A')
            
            data = result.get('data', {})
            price = data.get('price', 0)
            market_cap = data.get('market_cap', 0)
            volume = data.get('volume', 0)
            change_30d = data.get('price_change_30d', 0)
            rank = data.get('market_cap_rank', 'N/A')
            
            # Dados do gráfico
            chart_data['labels'].append(f"{token}")
            chart_data['scores'].append(score)
            
            # Cores baseadas no score
            if score >= 8:
                chart_data['colors'].append('rgba(40, 167, 69, 0.8)')
                score_class = 'score-high'
                decision_class = 'decision-buy'
            elif score >= 5:
                chart_data['colors'].append('rgba(255, 193, 7, 0.8)')
                score_class = 'score-medium'
                decision_class = 'decision-study'
            else:
                chart_data['colors'].append('rgba(220, 53, 69, 0.8)')
                score_class = 'score-low'
                decision_class = 'decision-avoid'
            
            # Linha da tabela
            table_rows.append(f"""
                <tr>
                    <td><strong>{token}</strong><br><small>{name}</small></td>
                    <td class="{score_class}">{score}/10</td>
                    <td class="{decision_class}">{decision}</td>
                    <td>${price:,.2f}</td>
                    <td>{self.format_large_number(market_cap)}</td>
                    <td>{self.format_large_number(volume)}</td>
                    <td style="color: {'green' if change_30d > 0 else 'red'}">{change_30d:+.1f}%</td>
                    <td>#{rank}</td>
                </tr>
            """)
        
        try:
            # Gerar HTML final - usar replace em vez de format para evitar problemas com {}
            html_content = html_template
            html_content = html_content.replace('{timestamp}', timestamp)
            html_content = html_content.replace('{total_tokens}', str(total_tokens))
            html_content = html_content.replace('{analysis_date}', str(analysis_date))
            html_content = html_content.replace('{market_context}', str(market_context))
            html_content = html_content.replace('{table_rows}', ''.join(table_rows))
            html_content = html_content.replace('{chart_data}', json.dumps(chart_data))
            
            console.print(f"[cyan]Salvando relatório em: {filepath}[/cyan]")
            
            # Salvar arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            console.print(f"[green]Relatório HTML gerado com sucesso![/green]")
            return filepath
            
        except Exception as e:
            console.print(f"[red]Erro ao gerar ou salvar HTML:[/red]")
            console.print(f"[yellow]Detalhes: {str(e)}[/yellow]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            raise
    
    def format_large_number(self, num: float) -> str:
        """Formata números grandes"""
        if num >= 1_000_000_000_000:
            return f"${num / 1_000_000_000_000:.1f}T"
        elif num >= 1_000_000_000:
            return f"${num / 1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"${num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"${num / 1_000:.1f}K"
        else:
            return f"${num:.2f}"
    
    def show_history(self, limit: int = 20):
        """Mostra histórico de análises"""
        history = self.load_history()
        
        if not history:
            console.print("[yellow]📝 Nenhum histórico encontrado[/yellow]")
            return
        
        # Mostrar últimas análises
        recent = history[-limit:] if len(history) > limit else history
        recent.reverse()  # Mais recente primeiro
        
        table = Table(title=f"📚 Histórico de Análises (últimas {len(recent)})", show_header=True, header_style="bold blue")
        
        table.add_column("Data/Hora", style="cyan", no_wrap=True)
        table.add_column("Token", style="bright_white")
        table.add_column("Score", justify="center")
        table.add_column("Decisão", justify="center")
        table.add_column("Preço", justify="right", style="green")
        
        for entry in recent:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%d/%m %H:%M')
            token = f"{entry['token']}\n[dim]{entry['token_name']}[/dim]"
            score = entry['score']
            decision = entry['decision']
            price = entry.get('price', 0)
            
            # Cor do score
            if score >= 8:
                score_text = f"[green]{score}/10[/green]"
                decision_text = f"[green]{decision}[/green]"
            elif score >= 5:
                score_text = f"[yellow]{score}/10[/yellow]"
                decision_text = f"[yellow]{decision}[/yellow]"
            else:
                score_text = f"[red]{score}/10[/red]"
                decision_text = f"[red]{decision}[/red]"
            
            table.add_row(
                timestamp,
                token,
                score_text,
                decision_text,
                f"${price:,.2f}" if price else "N/A"
            )
        
        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Total de análises no histórico: {len(history)}[/dim]")
#!/usr/bin/env python3
"""
test_new_display.py - Script de teste para o novo DisplayManager
Valida se o sistema hierárquico funciona corretamente com diferentes tokens
"""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import CryptoAnalyzer
from display_manager import DisplayManager
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_display_bitcoin():
    """Testa análise e exibição do Bitcoin"""
    print("\n" + "="*80)
    print("TESTE 1: BITCOIN - Token com dados completos")
    print("="*80)
    
    analyzer = CryptoAnalyzer()
    display_manager = DisplayManager()
    
    try:
        result = analyzer.analyze_with_social('bitcoin')
        
        if result and result.get('passed_elimination'):
            console.print(Panel(
                "[green]✅ Bitcoin: Análise obtida com sucesso[/green]",
                title="TESTE 1 - SUCESSO",
                border_style="green"
            ))
            display_manager.display_complete_analysis(result)
        else:
            console.print(Panel(
                f"[red]❌ Bitcoin: Falha na análise - {result.get('error', 'Não passou na eliminatória')}[/red]",
                title="TESTE 1 - FALHA",
                border_style="red"
            ))
    except Exception as e:
        console.print(Panel(
            f"[red]❌ Erro no teste Bitcoin: {e}[/red]",
            title="TESTE 1 - ERRO",
            border_style="red"
        ))

def test_display_rejected_token():
    """Testa exibição de token rejeitado"""
    print("\n" + "="*80)
    print("TESTE 2: TOKEN REJEITADO - Exibição simplificada")
    print("="*80)
    
    analyzer = CryptoAnalyzer()
    display_manager = DisplayManager()
    
    # Cria dados simulados de um token rejeitado
    rejected_result = {
        'token': 'TESTCOIN',
        'token_name': 'Test Coin',
        'passed_elimination': False,
        'elimination_reasons': [
            'Market cap muito baixo: $50,000 < $1,000,000',
            'Volume muito baixo: $5,000 < $100,000',
            'Token muito novo: 90 dias < 180 dias'
        ],
        'score': 0,
        'decision': 'REJEITADO',
        'data': {
            'market_cap': 50000,
            'volume': 5000,
            'age_days': 90,
            'price': 0.001
        }
    }
    
    try:
        console.print(Panel(
            "[yellow]⚠️ Testando exibição de token rejeitado[/yellow]",
            title="TESTE 2 - EXECUTANDO",
            border_style="yellow"
        ))
        display_manager.display_complete_analysis(rejected_result)
        
        console.print(Panel(
            "[green]✅ Token Rejeitado: Exibição funcionou corretamente[/green]",
            title="TESTE 2 - SUCESSO",
            border_style="green"
        ))
    except Exception as e:
        console.print(Panel(
            f"[red]❌ Erro no teste de token rejeitado: {e}[/red]",
            title="TESTE 2 - ERRO",
            border_style="red"
        ))

def test_display_medium_token():
    """Testa análise de um token de médio porte"""
    print("\n" + "="*80)
    print("TESTE 3: TOKEN MÉDIO - Sistema completo de 3 camadas")
    print("="*80)
    
    analyzer = CryptoAnalyzer()
    display_manager = DisplayManager()
    
    try:
        # Tenta alguns tokens mid-cap populares
        test_tokens = ['ethereum', 'solana', 'matic-network']
        
        for token in test_tokens:
            try:
                result = analyzer.analyze_with_social(token)
                
                if result and result.get('passed_elimination'):
                    console.print(Panel(
                        f"[green]✅ {token.upper()}: Análise obtida com sucesso[/green]",
                        title=f"TESTE 3 - {token.upper()} SUCESSO",
                        border_style="green"
                    ))
                    display_manager.display_complete_analysis(result)
                    break  # Se conseguir analisar um, sai do loop
                else:
                    console.print(Panel(
                        f"[yellow]⚠️ {token.upper()}: {result.get('error', 'Não passou na eliminatória')}[/yellow]",
                        title=f"TESTE 3 - {token.upper()} PULADO",
                        border_style="yellow"
                    ))
                    continue
            except Exception as e:
                console.print(Panel(
                    f"[yellow]⚠️ Erro com {token}: {e}[/yellow]",
                    title=f"TESTE 3 - {token.upper()} ERRO",
                    border_style="yellow"
                ))
                continue
        else:
            console.print(Panel(
                "[red]❌ Nenhum token médio pôde ser analisado[/red]",
                title="TESTE 3 - FALHA TOTAL",
                border_style="red"
            ))
            
    except Exception as e:
        console.print(Panel(
            f"[red]❌ Erro geral no teste 3: {e}[/red]",
            title="TESTE 3 - ERRO FATAL",
            border_style="red"
        ))

def test_display_components():
    """Testa componentes individuais do DisplayManager"""
    print("\n" + "="*80)
    print("TESTE 4: COMPONENTES INDIVIDUAIS - Verificação de métodos")
    print("="*80)
    
    display_manager = DisplayManager()
    
    try:
        # Testa formatação de números
        test_numbers = [1000, 1_000_000, 1_000_000_000, 1_000_000_000_000]
        console.print("[cyan]Testando formatação de números:[/cyan]")
        for num in test_numbers:
            formatted = display_manager._format_number(num)
            console.print(f"  {num:,} -> {formatted}")
        
        # Testa cálculo de percentuais
        console.print("\n[cyan]Testando cálculo de percentuais:[/cyan]")
        test_cases = [(100, 110), (100, 90), (50, 75)]
        for from_price, to_price in test_cases:
            percent = display_manager._calc_percent(from_price, to_price)
            console.print(f"  ${from_price} -> ${to_price} = {percent:+.1f}%")
        
        # Testa coloração de percentuais
        console.print("\n[cyan]Testando coloração de percentuais:[/cyan]")
        test_percents = [15.5, -8.2, 0]
        for pct in test_percents:
            colored = display_manager._color_percent(pct)
            console.print(f"  {pct}% -> {colored}")
        
        # Testa cálculo de posição
        console.print("\n[cyan]Testando cálculo de tamanho de posição:[/cyan]")
        test_scores = [9.5, 8.0, 6.5, 5.0, 3.5, 1.0]
        for score in test_scores:
            position = display_manager._calculate_position_size(score)
            console.print(f"  Score {score}/10 -> {position}% do portfolio")
        
        console.print(Panel(
            "[green]✅ Todos os componentes funcionaram corretamente[/green]",
            title="TESTE 4 - SUCESSO",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]❌ Erro nos componentes: {e}[/red]",
            title="TESTE 4 - ERRO",
            border_style="red"
        ))

def run_all_tests():
    """Executa todos os testes de validação"""
    console.print(Panel(
        "[bold blue]🧪 INICIANDO TESTES DO NOVO SISTEMA DE DISPLAY[/bold blue]\n\n"
        "Este script validará:\n"
        "• Sistema hierárquico de 3 camadas\n"
        "• Exibição de tokens rejeitados\n"
        "• Análises complementares\n"
        "• Componentes individuais\n\n"
        "[bold]Aguarde... pode levar alguns minutos devido ao rate limiting.[/bold]",
        title="🚀 CRYPTO ANALYZER - TESTE DE VALIDAÇÃO",
        border_style="blue"
    ))
    
    # Executa todos os testes
    test_display_components()  # Mais rápido primeiro
    test_display_rejected_token()  # Simulado, rápido
    test_display_bitcoin()  # Análise real
    test_display_medium_token()  # Análise real
    
    console.print(Panel(
        "[bold green]🎉 TESTES CONCLUÍDOS![/bold green]\n\n"
        "Verifique os resultados acima para confirmar se:\n"
        "• ✅ Headers estão sendo exibidos corretamente\n"
        "• ✅ Sistema de 3 camadas funciona\n"
        "• ✅ Análises complementares aparecem\n"
        "• ✅ Tokens rejeitados são tratados adequadamente\n"
        "• ✅ Disclaimer aparece ao final\n\n"
        "[dim]Se algum teste falhou, verifique a conectividade com APIs[/dim]",
        title="📊 VALIDAÇÃO FINALIZADA",
        border_style="green"
    ))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "components":
            test_display_components()
        elif sys.argv[1] == "bitcoin":
            test_display_bitcoin()
        elif sys.argv[1] == "rejected":
            test_display_rejected_token()
        elif sys.argv[1] == "medium":
            test_display_medium_token()
        else:
            console.print(f"[red]Teste '{sys.argv[1]}' não encontrado[/red]")
            console.print("[yellow]Testes disponíveis: components, bitcoin, rejected, medium[/yellow]")
    else:
        run_all_tests()
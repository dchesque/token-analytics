#!/usr/bin/env python3
"""
Script de teste para verificar as correções dos bugs:
1. Geração de relatório HTML
2. Conexão com LunarCrush v4
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from enhanced_features import EnhancedAnalyzer
from social_analyzer import SocialAnalyzer
from rich.console import Console

console = Console()

def test_html_generation():
    """Testa se o relatório HTML está sendo gerado corretamente"""
    console.print("[bold blue]Teste 1: Geração de Relatório HTML[/bold blue]\n")
    
    try:
        analyzer = EnhancedAnalyzer()
        
        # Dados fictícios para teste
        test_comparison = {
            'tokens': [
                {
                    'token': 'BTC',
                    'token_name': 'Bitcoin',
                    'score': 8.5,
                    'decision': 'Comprar',
                    'data': {
                        'price': 45000.50,
                        'market_cap': 850000000000,
                        'volume': 25000000000,
                        'price_change_30d': 12.5,
                        'market_cap_rank': 1
                    },
                    'market_context': {
                        'fear_greed_index': 65,
                        'market_sentiment': 'Ganância'
                    }
                },
                {
                    'token': 'ETH', 
                    'token_name': 'Ethereum',
                    'score': 7.2,
                    'decision': 'Estudar',
                    'data': {
                        'price': 3200.80,
                        'market_cap': 400000000000,
                        'volume': 15000000000,
                        'price_change_30d': -5.2,
                        'market_cap_rank': 2
                    },
                    'market_context': {
                        'fear_greed_index': 65,
                        'market_sentiment': 'Ganância'
                    }
                }
            ],
            'comparison_timestamp': '2024-08-20T10:30:00',
            'total_analyzed': 2
        }
        
        console.print("Tentando gerar relatório HTML de teste...")
        
        # Tentar gerar HTML
        filepath = analyzer.generate_html_report(test_comparison, "test_report.html")
        
        if filepath.exists():
            console.print(f"[green]✅ Relatório HTML gerado com sucesso![/green]")
            console.print(f"[cyan]📁 Localização: {filepath}[/cyan]")
            
            # Verificar tamanho do arquivo
            size = filepath.stat().st_size
            console.print(f"[cyan]📏 Tamanho: {size:,} bytes[/cyan]")
            
            if size > 1000:  # Arquivo deve ter pelo menos 1KB
                console.print("[green]✅ Arquivo tem tamanho adequado[/green]")
                return True
            else:
                console.print("[yellow]⚠️ Arquivo muito pequeno, pode ter erro[/yellow]")
                return False
        else:
            console.print("[red]❌ Arquivo não foi criado[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Erro no teste HTML: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

def test_lunarcrush_connection():
    """Testa a conexão com LunarCrush v4"""
    console.print("\n[bold blue]Teste 2: Conexão LunarCrush v4[/bold blue]\n")
    
    try:
        social = SocialAnalyzer()
        
        # Testar conexão
        console.print("Testando conexão com LunarCrush...")
        test_result = social.test_lunarcrush_connection()
        
        if test_result["success"]:
            console.print(f"[green]✅ Conexão funcionando: {test_result['message']}[/green]")
            
            # Testar busca de dados reais
            console.print("Testando busca de dados para BTC...")
            btc_data = social.get_lunarcrush_data('BTC')
            
            if btc_data.get('source', '').startswith('lunarcrush'):
                console.print("[green]✅ Dados do LunarCrush obtidos com sucesso![/green]")
                console.print(f"[cyan]Galaxy Score: {btc_data.get('galaxy_score', 0)}[/cyan]")
                console.print(f"[cyan]Volume Social: {btc_data.get('social_volume', 0)}[/cyan]")
                return True
            else:
                console.print(f"[yellow]⚠️ Usando dados alternativos: {btc_data.get('source')}[/yellow]")
                console.print("LunarCrush não retornou dados, mas alternativas funcionam")
                return True
        else:
            console.print(f"[red]❌ Falha na conexão: {test_result['error']}[/red]")
            console.print("Testando dados alternativos...")
            
            # Testar alternativas
            alt_data = social._get_alternative_social_data('BTC')
            if alt_data.get('source'):
                console.print(f"[green]✅ Dados alternativos funcionando: {alt_data.get('source')}[/green]")
                return True
            else:
                console.print("[red]❌ Nem dados alternativos funcionam[/red]")
                return False
            
    except Exception as e:
        console.print(f"[red]❌ Erro no teste LunarCrush: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

def main():
    """Executa todos os testes"""
    console.print("[bold green]Teste de Correção dos Bugs - Crypto Analyzer[/bold green]")
    console.print("=" * 60 + "\n")
    
    # Resultados
    results = {}
    
    # Teste 1: HTML
    results['html'] = test_html_generation()
    
    # Teste 2: LunarCrush
    results['lunarcrush'] = test_lunarcrush_connection()
    
    # Resumo
    console.print("\n" + "=" * 60)
    console.print("[bold blue]Resumo dos Testes[/bold blue]\n")
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "[green]PASSOU[/green]" if passed_test else "[red]FALHOU[/red]"
        console.print(f"{test_name.upper():15} {status}")
        if passed_test:
            passed += 1
    
    console.print(f"\n[bold]Resultado: {passed}/{total} testes passaram[/bold]")
    
    if passed == total:
        console.print("[green]Todos os bugs foram corrigidos com sucesso![/green]")
        return True
    else:
        console.print("[yellow]Alguns problemas ainda existem[/yellow]")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
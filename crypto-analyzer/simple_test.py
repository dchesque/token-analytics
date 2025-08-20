#!/usr/bin/env python3
"""
Teste simples dos bugs corrigidos
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_html_generation():
    """Testa geração HTML"""
    try:
        from enhanced_features import EnhancedAnalyzer
        
        print("Teste 1: Geracao de HTML")
        print("-" * 30)
        
        analyzer = EnhancedAnalyzer()
        
        # Dados de teste
        test_data = {
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
                    }
                }
            ],
            'comparison_timestamp': '2024-08-20T10:30:00',
            'total_analyzed': 1
        }
        
        print("Tentando gerar HTML...")
        filepath = analyzer.generate_html_report(test_data, "test_simple.html")
        
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"SUCESSO: Arquivo criado - {size} bytes")
            return True
        else:
            print("FALHA: Arquivo não criado")
            return False
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return False

def test_lunarcrush():
    """Testa LunarCrush"""
    try:
        from social_analyzer import SocialAnalyzer
        
        print("\nTeste 2: LunarCrush API")
        print("-" * 30)
        
        social = SocialAnalyzer()
        
        # Testar conexão
        print("Testando conexao...")
        test_result = social.test_lunarcrush_connection()
        
        if test_result["success"]:
            print(f"SUCESSO: {test_result['message']}")
            return True
        else:
            print(f"API nao disponivel: {test_result['error']}")
            # Testar fallback
            data = social._get_alternative_social_data('BTC')
            if data.get('source'):
                print(f"FALLBACK OK: {data['source']}")
                return True
            else:
                print("FALLBACK FALHOU")
                return False
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        return False

def main():
    """Roda todos os testes"""
    print("=== TESTE DE CORRECAO DOS BUGS ===")
    
    # Teste 1
    html_ok = test_html_generation()
    
    # Teste 2  
    lunar_ok = test_lunarcrush()
    
    # Resultado
    print("\n=== RESULTADO ===")
    print(f"HTML:       {'OK' if html_ok else 'FALHOU'}")
    print(f"LunarCrush: {'OK' if lunar_ok else 'FALHOU'}")
    
    if html_ok and lunar_ok:
        print("\nTodos os bugs corrigidos!")
        return True
    else:
        print("\nAinda ha problemas.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
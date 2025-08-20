#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar as correções implementadas
"""
import sys
import os
sys.path.append('src')

def test_display_result_safe():
    """Testa display_result com dados faltantes"""
    from main import display_result
    
    # Caso 1: resultado sem classification_info
    result_empty = {
        'passed_elimination': True,
        'score': 7,
        'token': 'BTC',
        'token_name': 'Bitcoin'
    }
    
    try:
        display_result(result_empty)
        print("+ display_result funciona com classification_info vazio")
        return True
    except Exception as e:
        print(f"- display_result falhou: {e}")
        return False

def test_social_analyzer_error_handling():
    """Testa tratamento de erros no social analyzer"""
    from social_analyzer import SocialAnalyzer
    
    analyzer = SocialAnalyzer()
    
    # Testa com símbolo inexistente
    try:
        result = analyzer.get_lunarcrush_data("SIMBOLOINEXISTENTE123")
        if isinstance(result, dict):
            print("+ social_analyzer retorna dict vazio em caso de erro")
            return True
        else:
            print("- social_analyzer não retorna dict")
            return False
    except Exception as e:
        print(f"- social_analyzer não trata erros: {e}")
        return False

def test_classify_token_context():
    """Testa se classify_token retorna campo 'context'"""
    from analyzer import CryptoAnalyzer
    
    analyzer = CryptoAnalyzer()
    
    # Dados mock
    mock_data = {
        'market_cap': 1000000000,
        'market_cap_rank': 50,
        'id': 'test-token',
        'categories': []
    }
    
    try:
        result = analyzer.classify_token(5, mock_data)
        if 'context' in result:
            print("+ classify_token inclui campo 'context'")
            return True
        else:
            print("- classify_token não inclui campo 'context'")
            return False
    except Exception as e:
        print(f"- classify_token falhou: {e}")
        return False

def test_analyze_with_social_error_handling():
    """Testa análise social com tratamento de erros"""
    from analyzer import CryptoAnalyzer
    
    analyzer = CryptoAnalyzer()
    
    try:
        # Deve funcionar mesmo com erros na API
        result = analyzer.analyze_with_social('bitcoin')
        
        if result and 'classification_info' in result:
            print("+ analyze_with_social mantém classification_info")
            return True
        else:
            print("- analyze_with_social não garante classification_info")
            return False
    except Exception as e:
        print(f"- analyze_with_social falhou: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("Testando correções implementadas...\n")
    
    tests = [
        ("Display Result Seguro", test_display_result_safe),
        ("Social Analyzer Error Handling", test_social_analyzer_error_handling),  
        ("Classify Token Context", test_classify_token_context),
        ("Analyze Social Error Handling", test_analyze_with_social_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"Testando: {name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"- Erro inesperado em {name}: {e}")
        print()
    
    print(f"Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("Todas as correções foram implementadas com sucesso!")
        return True
    else:
        print("Algumas correções precisam de ajustes")
        return False

if __name__ == "__main__":
    main()
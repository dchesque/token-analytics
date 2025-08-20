#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da atualização LunarCrush v4 com fallbacks
"""
import sys
import os
sys.path.append('src')

def test_config_loading():
    """Testa carregamento da configuração"""
    try:
        from config import ENABLE_LUNARCRUSH, ENABLE_MESSARI, USE_ALTERNATIVE_SOCIAL
        print(f"+ Config carregado - LunarCrush: {ENABLE_LUNARCRUSH}, Messari: {ENABLE_MESSARI}")
        return True
    except Exception as e:
        print(f"- Erro config: {e}")
        return False

def test_social_analyzer_fallback():
    """Testa fallback do social analyzer"""
    try:
        from social_analyzer import SocialAnalyzer
        analyzer = SocialAnalyzer()
        
        # Testa com Bitcoin
        result = analyzer.get_lunarcrush_data('bitcoin')
        
        if result and result.get('source'):
            print(f"+ Social analyzer funcionando - Source: {result['source']}")
            return True
        else:
            print(f"- Social analyzer falhou")
            return False
    except Exception as e:
        print(f"- Erro social analyzer: {e}")
        return False

def test_hype_detector_limited():
    """Testa detector de hype com dados limitados"""
    try:
        from social_analyzer import SocialAnalyzer
        analyzer = SocialAnalyzer()
        
        # Dados limitados mock
        limited_data = {
            'source': 'limited',
            'galaxy_score': 0,
            'social_volume': 0
        }
        
        hype_result = analyzer.detect_hype('test', limited_data)
        
        if hype_result and hype_result.get('hype_level') == 'DADOS SOCIAIS LIMITADOS':
            print("+ Hype detector funciona com dados limitados")
            return True
        else:
            print("- Hype detector falhou com dados limitados")
            return False
    except Exception as e:
        print(f"- Erro hype detector: {e}")
        return False

def test_full_analysis():
    """Testa análise completa sem API key"""
    try:
        from analyzer import CryptoAnalyzer
        analyzer = CryptoAnalyzer()
        
        # Testa análise completa
        result = analyzer.analyze_with_social('bitcoin')
        
        if result and result.get('token') == 'BTC' and 'classification_info' in result:
            print("+ Análise completa funcionando sem LunarCrush")
            
            # Verifica se dados sociais estão usando fallback
            if 'social_metrics' in result:
                print("+ Métricas sociais usando fallback")
            
            return True
        else:
            print("- Análise completa falhou")
            return False
    except Exception as e:
        print(f"- Erro análise completa: {e}")
        return False

def test_api_status_display():
    """Testa display de status das APIs"""
    try:
        from main import show_api_status
        
        print("+ Testando display de status...")
        show_api_status()
        print("+ Display de status funcionando")
        return True
    except Exception as e:
        print(f"- Erro display status: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("Testando atualização LunarCrush v4...\n")
    
    tests = [
        ("Config Loading", test_config_loading),
        ("Social Analyzer Fallback", test_social_analyzer_fallback),
        ("Hype Detector Limited", test_hype_detector_limited),
        ("Full Analysis", test_full_analysis),
        ("API Status Display", test_api_status_display)
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
        print("SUCCESS: Todas as funcionalidades estão funcionando!")
        print("\nRESTAURADO:")
        print("+ App funciona SEM LunarCrush (usa dados básicos)")
        print("+ Se usuário quiser social completo, pode adicionar key")
        print("+ Não quebra se não tiver key")
        print("+ Mostra claramente o que está disponível")
        return True
    else:
        print("FALHOU: Algumas funcionalidades precisam de ajustes")
        return False

if __name__ == "__main__":
    main()
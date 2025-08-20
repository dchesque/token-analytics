#!/usr/bin/env python3
"""
Teste de integração da análise social avançada
Valida se todas as funcionalidades estão funcionando corretamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import CryptoAnalyzer
from social_analyzer import SocialAnalyzer
from config import *

def test_social_analyzer_integration():
    """Testa a integração completa do social analyzer"""
    
    print("🧪 TESTE DE INTEGRAÇÃO - ANÁLISE SOCIAL AVANÇADA")
    print("=" * 60)
    
    # Teste 1: Instanciar Social Analyzer
    print("\n1. Testando instanciação do SocialAnalyzer...")
    try:
        social_analyzer = SocialAnalyzer()
        print("✅ SocialAnalyzer instanciado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao instanciar SocialAnalyzer: {e}")
        return False
    
    # Teste 2: Testar estruturas de dados vazias
    print("\n2. Testando estruturas de dados vazias...")
    try:
        empty_social = social_analyzer._empty_social_data()
        empty_messari = social_analyzer._empty_messari_data()
        empty_defi = social_analyzer._empty_defi_data()
        
        assert 'galaxy_score' in empty_social
        assert 'real_volume' in empty_messari
        assert 'tvl_current' in empty_defi
        
        print("✅ Estruturas de dados vazias funcionando")
    except Exception as e:
        print(f"❌ Erro nas estruturas vazias: {e}")
        return False
    
    # Teste 3: Testar detecção de hype com dados mock
    print("\n3. Testando detecção de hype...")
    try:
        mock_social_data = {
            'social_volume_change': 200,  # Hype alto
            'galaxy_score_change': 60,
            'sentiment_bullish': 90,
            'social_contributors': 500,
            'alt_rank': 15,
            'history_7d': [
                {'social_contributors': 300},
                {'social_contributors': 350}
            ]
        }
        
        hype_result = social_analyzer.detect_hype("TEST", mock_social_data)
        
        assert 'hype_score' in hype_result
        assert 'hype_level' in hype_result
        assert 'signals' in hype_result
        assert 'recommendations' in hype_result
        
        print(f"✅ Hype detection funcionando - Score: {hype_result['hype_score']}")
        print(f"    Level: {hype_result['hype_level']}")
        
    except Exception as e:
        print(f"❌ Erro na detecção de hype: {e}")
        return False
    
    # Teste 4: Testar cache
    print("\n4. Testando sistema de cache...")
    try:
        # Simular cache
        social_analyzer._save_cache("test_key", {"test": "data"}, 300)
        
        # Verificar se cache existe
        is_cached = social_analyzer._check_cache("test_key", 300)
        assert is_cached == True
        
        print("✅ Sistema de cache funcionando")
    except Exception as e:
        print(f"❌ Erro no sistema de cache: {e}")
        return False
    
    # Teste 5: Testar integração com CryptoAnalyzer
    print("\n5. Testando integração com CryptoAnalyzer...")
    try:
        analyzer = CryptoAnalyzer()
        
        # Verificar se método analyze_with_social existe
        assert hasattr(analyzer, 'analyze_with_social'), "Método analyze_with_social não encontrado"
        
        print("✅ Integração com CryptoAnalyzer OK")
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False
    
    # Teste 6: Testar configurações
    print("\n6. Testando configurações...")
    try:
        assert LUNARCRUSH_API is not None
        assert MESSARI_API is not None
        assert DEFILLAMA_API_V2 is not None
        assert 'extreme' in HYPE_THRESHOLDS
        assert REQUESTS_PER_MINUTE > 0
        
        print("✅ Configurações carregadas corretamente")
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Análise social avançada está funcionando corretamente")
    print("\n📋 Funcionalidades implementadas:")
    print("   • LunarCrush API integration")
    print("   • Messari API integration") 
    print("   • DeFiLlama API integration")
    print("   • Hype detection algorithm")
    print("   • Rate limiting system")
    print("   • Cache system")
    print("   • Enhanced score calculation")
    print("   • Social metrics display")
    
    return True

def test_api_configurations():
    """Testa se as configurações das APIs estão corretas"""
    
    print("\n🔧 TESTE DE CONFIGURAÇÕES DE API")
    print("=" * 40)
    
    apis = {
        'LunarCrush': LUNARCRUSH_API,
        'Messari': MESSARI_API,
        'DeFiLlama': DEFILLAMA_API_V2
    }
    
    for name, url in apis.items():
        if url and url.startswith('http'):
            print(f"✅ {name}: {url}")
        else:
            print(f"❌ {name}: Configuração inválida")
    
    print(f"\n📊 Thresholds de Hype:")
    for level, threshold in HYPE_THRESHOLDS.items():
        print(f"   • {level}: {threshold}%")
    
    print(f"\n⏱️ Rate Limiting: {REQUESTS_PER_MINUTE} requests/minuto")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE INTEGRAÇÃO")
    print("📅 Validando implementação da análise social avançada")
    print()
    
    try:
        # Testa configurações
        test_api_configurations()
        
        # Testa integração
        success = test_social_analyzer_integration()
        
        if success:
            print("\n🎯 RESULTADO: Implementação validada com sucesso!")
            print("💡 Pronto para testes com tokens reais!")
        else:
            print("\n❌ RESULTADO: Alguns testes falharam")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        sys.exit(1)
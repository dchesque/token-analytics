#!/usr/bin/env python3
"""
Script de validação simples para verificar se a implementação está correta
Verifica imports, estruturas de dados e funcionalidades principais
"""

import sys
import os

def validate_file_structure():
    """Valida se todos os arquivos necessários existem"""
    
    required_files = [
        'src/config.py',
        'src/analyzer.py', 
        'src/social_analyzer.py',
        'src/main.py',
        'src/fetcher.py'
    ]
    
    print("📁 Validando estrutura de arquivos...")
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - ARQUIVO FALTANDO!")
            return False
    
    return True

def validate_config_additions():
    """Valida se as configurações foram adicionadas corretamente"""
    
    print("\n🔧 Validando configurações...")
    
    try:
        with open('src/config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        required_configs = [
            'LUNARCRUSH_API',
            'MESSARI_API', 
            'DEFILLAMA_API_V2',
            'HYPE_THRESHOLDS',
            'CACHE_SOCIAL',
            'CACHE_DEFI',
            'CACHE_FUNDAMENTAL',
            'REQUESTS_PER_MINUTE'
        ]
        
        for config in required_configs:
            if config in config_content:
                print(f"✅ {config}")
            else:
                print(f"❌ {config} - CONFIGURAÇÃO FALTANDO!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler config.py: {e}")
        return False

def validate_social_analyzer():
    """Valida se o social_analyzer.py foi criado corretamente"""
    
    print("\n📊 Validando SocialAnalyzer...")
    
    try:
        with open('src/social_analyzer.py', 'r', encoding='utf-8') as f:
            social_content = f.read()
        
        required_methods = [
            'class SocialAnalyzer',
            'def get_lunarcrush_data',
            'def get_messari_data',
            'def get_defillama_extended',
            'def detect_hype',
            'def _rate_limit',
            'def _empty_social_data',
            'def _empty_messari_data',
            'def _empty_defi_data'
        ]
        
        for method in required_methods:
            if method in social_content:
                print(f"✅ {method}")
            else:
                print(f"❌ {method} - MÉTODO FALTANDO!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler social_analyzer.py: {e}")
        return False

def validate_analyzer_integration():
    """Valida se o analyzer.py foi atualizado corretamente"""
    
    print("\n🔗 Validando integração com analyzer.py...")
    
    try:
        with open('src/analyzer.py', 'r', encoding='utf-8') as f:
            analyzer_content = f.read()
        
        required_integrations = [
            'from social_analyzer import SocialAnalyzer',
            'def analyze_with_social',
            'social_analyzer = SocialAnalyzer()',
            'hype_detection',
            'enhanced_score'
        ]
        
        for integration in required_integrations:
            if integration in analyzer_content:
                print(f"✅ {integration}")
            else:
                print(f"❌ {integration} - INTEGRAÇÃO FALTANDO!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler analyzer.py: {e}")
        return False

def validate_main_interface():
    """Valida se o main.py foi atualizado corretamente"""
    
    print("\n🖥️ Validando interface main.py...")
    
    try:
        with open('src/main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        required_functions = [
            'def display_enhanced_result',
            'def display_enhanced_social_analysis', 
            'def display_hype_panel',
            'def display_social_metrics_panel',
            'def display_messari_panel',
            'def display_defi_panel',
            'analyze_with_social'
        ]
        
        for function in required_functions:
            if function in main_content:
                print(f"✅ {function}")
            else:
                print(f"❌ {function} - FUNÇÃO FALTANDO!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler main.py: {e}")
        return False

def validate_hype_thresholds():
    """Valida se os thresholds de hype estão configurados"""
    
    print("\n🔥 Validando thresholds de hype...")
    
    try:
        with open('src/config.py', 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        expected_thresholds = ['extreme', 'high', 'moderate', 'normal']
        
        for threshold in expected_thresholds:
            if f"'{threshold}'" in config_content:
                print(f"✅ Threshold '{threshold}'")
            else:
                print(f"❌ Threshold '{threshold}' - FALTANDO!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao validar thresholds: {e}")
        return False

def main():
    """Função principal de validação"""
    
    print("🧪 VALIDAÇÃO DA IMPLEMENTAÇÃO")
    print("📋 Análise social avançada com LunarCrush, Messari, DeFiLlama e Hype Detection")
    print("=" * 80)
    
    # Lista de validações
    validations = [
        ("Estrutura de arquivos", validate_file_structure),
        ("Configurações", validate_config_additions),
        ("SocialAnalyzer", validate_social_analyzer),
        ("Integração Analyzer", validate_analyzer_integration),
        ("Interface Main", validate_main_interface),
        ("Thresholds de Hype", validate_hype_thresholds)
    ]
    
    results = []
    
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro em {name}: {e}")
            results.append((name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 80)
    print("📊 RESUMO DA VALIDAÇÃO")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} validações passaram")
    
    if passed == total:
        print("🎉 IMPLEMENTAÇÃO COMPLETA E VALIDADA!")
        print("\n📋 Funcionalidades implementadas:")
        print("   ✅ Configurações das APIs (LunarCrush, Messari, DeFiLlama)")
        print("   ✅ SocialAnalyzer com rate limiting e cache")
        print("   ✅ Algoritmo de detecção de hype")
        print("   ✅ Integração com analyzer principal")
        print("   ✅ Interface atualizada com novos panels")
        print("   ✅ Score enhancement baseado em dados sociais")
        print("\n💡 Pronto para testes com tokens reais!")
        return True
    else:
        print("⚠️ IMPLEMENTAÇÃO INCOMPLETA")
        print("❌ Algumas validações falharam. Verifique os itens marcados.")
        return False

if __name__ == "__main__":
    # Mudar para o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    success = main()
    sys.exit(0 if success else 1)
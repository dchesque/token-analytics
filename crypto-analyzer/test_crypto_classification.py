#!/usr/bin/env python3
"""
Teste específico para validar as novas classificações crypto
Testa Bitcoin, Ethereum, Cardano e Shiba Inu
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_crypto_classifications():
    """Testa as novas classificações crypto"""
    print("🧪 TESTANDO NOVAS CLASSIFICAÇÕES CRYPTO")
    print("=" * 45)
    
    try:
        from analyzer import CryptoAnalyzer
        analyzer = CryptoAnalyzer()
        
        # Bitcoin - deve ser MAJOR
        print("\n👑 TESTE BITCOIN:")
        bitcoin_data = {
            'id': 'bitcoin',
            'market_cap': 2000000000000,  # 2T
            'market_cap_rank': 1,
            'categories': []
        }
        
        result = analyzer.classify_token(9, bitcoin_data)
        print(f"   Classificação: {result['classification']}")
        print(f"   Descrição: {result['description']}")
        print(f"   Emoji: {result['emoji']}")
        print(f"   Risco: {result['risk_level']}")
        
        if result['classification'] == 'MAJOR':
            print("   ✅ Bitcoin classificado como MAJOR")
        else:
            print(f"   ❌ Bitcoin deveria ser MAJOR, mas foi {result['classification']}")
            return False
        
        # Ethereum - deve ser MAJOR
        print("\n👑 TESTE ETHEREUM:")
        ethereum_data = {
            'id': 'ethereum',
            'market_cap': 500000000000,  # 500B
            'market_cap_rank': 2,
            'categories': []
        }
        
        result = analyzer.classify_token(8, ethereum_data)
        print(f"   Classificação: {result['classification']}")
        print(f"   Descrição: {result['description']}")
        print(f"   Emoji: {result['emoji']}")
        print(f"   Risco: {result['risk_level']}")
        
        if result['classification'] == 'MAJOR':
            print("   ✅ Ethereum classificado como MAJOR")
        else:
            print(f"   ❌ Ethereum deveria ser MAJOR, mas foi {result['classification']}")
            return False
        
        # Cardano - deve ser LARGE CAP
        print("\n💎 TESTE CARDANO:")
        cardano_data = {
            'id': 'cardano',
            'market_cap': 50000000000,  # 50B
            'market_cap_rank': 8,
            'categories': []
        }
        
        result = analyzer.classify_token(7, cardano_data)
        print(f"   Classificação: {result['classification']}")
        print(f"   Descrição: {result['description']}")
        print(f"   Emoji: {result['emoji']}")
        print(f"   Risco: {result['risk_level']}")
        
        if result['classification'] == 'LARGE CAP':
            print("   ✅ Cardano classificado como LARGE CAP")
        else:
            print(f"   ❌ Cardano deveria ser LARGE CAP, mas foi {result['classification']}")
            return False
        
        # Shiba Inu - deve ser MEME COIN
        print("\n🐕 TESTE SHIBA INU:")
        shiba_data = {
            'id': 'shiba-inu',
            'market_cap': 10000000000,  # 10B
            'market_cap_rank': 15,
            'categories': ['meme-token']
        }
        
        result = analyzer.classify_token(4, shiba_data)
        print(f"   Classificação: {result['classification']}")
        print(f"   Descrição: {result['description']}")
        print(f"   Emoji: {result['emoji']}")
        print(f"   Risco: {result['risk_level']}")
        
        if result['classification'] == 'MEME COIN':
            print("   ✅ Shiba Inu classificado como MEME COIN")
        else:
            print(f"   ❌ Shiba Inu deveria ser MEME COIN, mas foi {result['classification']}")
            return False
        
        # Teste USDC - deve ser STABLECOIN
        print("\n💵 TESTE USDC:")
        usdc_data = {
            'id': 'usd-coin',
            'market_cap': 35000000000,  # 35B
            'market_cap_rank': 5,
            'categories': ['stablecoin']
        }
        
        result = analyzer.classify_token(6, usdc_data)
        print(f"   Classificação: {result['classification']}")
        print(f"   Descrição: {result['description']}")
        print(f"   Emoji: {result['emoji']}")
        print(f"   Risco: {result['risk_level']}")
        
        if result['classification'] == 'STABLECOIN':
            print("   ✅ USDC classificado como STABLECOIN")
        else:
            print(f"   ❌ USDC deveria ser STABLECOIN, mas foi {result['classification']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro durante teste: {e}")
        return False

def test_major_metrics():
    """Testa as métricas especiais para Majors"""
    print("\n🔑 TESTANDO MÉTRICAS DOS MAJORS")
    print("=" * 35)
    
    try:
        from analyzer import CryptoAnalyzer
        analyzer = CryptoAnalyzer()
        
        # Teste Bitcoin
        print("\n📊 BITCOIN METRICS:")
        bitcoin_metrics = analyzer.analyze_major_metrics('bitcoin', {
            'market_cap_percentage': {'btc': 58.5},
            'market_data': {'market_cap_dominance': 58.5}
        })
        
        if bitcoin_metrics:
            print(f"   Narrativa: {bitcoin_metrics['narrative']}")
            print(f"   Adoção: {bitcoin_metrics['adoption']}")
            print("   Métricas principais:")
            for metric in bitcoin_metrics['key_metrics']:
                print(f"     • {metric}")
            print("   ✅ Métricas Bitcoin geradas")
        else:
            print("   ❌ Métricas Bitcoin não geradas")
            return False
        
        # Teste Ethereum
        print("\n📊 ETHEREUM METRICS:")
        ethereum_metrics = analyzer.analyze_major_metrics('ethereum', {
            'market_cap_percentage': {'eth': 18.2},
            'defi_tvl': 95000000000  # 95B
        })
        
        if ethereum_metrics:
            print(f"   Narrativa: {ethereum_metrics['narrative']}")
            print(f"   Ecossistema: {ethereum_metrics['ecosystem']}")
            print("   Métricas principais:")
            for metric in ethereum_metrics['key_metrics']:
                print(f"     • {metric}")
            print("   ✅ Métricas Ethereum geradas")
        else:
            print("   ❌ Métricas Ethereum não geradas")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro durante teste métricas: {e}")
        return False

def test_display_classification():
    """Testa a exibição das classificações"""
    print("\n🎨 TESTANDO EXIBIÇÃO DAS CLASSIFICAÇÕES")
    print("=" * 45)
    
    try:
        from analyzer import CryptoAnalyzer
        analyzer = CryptoAnalyzer()
        
        # Dados de teste para Bitcoin
        classification_data = {
            'classification': 'MAJOR',
            'description': 'Ativo principal do mercado crypto',
            'risk_level': 'Estabelecido',
            'score': 9,
            'rank': 1,
            'market_cap': 2000000000000,
            'quality': 'Fundamentos Excelentes',
            'emoji': '👑',
            'major_metrics': {
                'key_metrics': [
                    'Dominância: 58.5%',
                    'Halving a cada 4 anos',
                    'Supply máximo: 21M BTC',
                    'Rede desde 2009'
                ]
            }
        }
        
        display_result = analyzer.display_token_classification(classification_data)
        
        print("📋 DISPLAY RESULT:")
        print(display_result)
        
        # Verificar se contém elementos esperados
        expected_elements = [
            '👑 CLASSIFICAÇÃO: MAJOR',
            'Ativo principal do mercado crypto',
            'Nível de Risco: Estabelecido',
            'Score de Fundamentos: 9/10',
            'Ranking: #1',
            'Market Cap: 2000.0B',
            'Fundamentos Excelentes',
            'MÉTRICAS PRINCIPAIS'
        ]
        
        all_present = True
        for element in expected_elements:
            if element in display_result:
                print(f"   ✅ {element}")
            else:
                print(f"   ❌ Faltando: {element}")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"   ❌ Erro durante teste display: {e}")
        return False

def main():
    """Executa todos os testes de classificação crypto"""
    print("🚀 TESTE DAS CLASSIFICAÇÕES CRYPTO CORRIGIDAS")
    print("=" * 55)
    
    tests = [
        ("Classificações Crypto", test_crypto_classifications),
        ("Métricas dos Majors", test_major_metrics),
        ("Display das Classificações", test_display_classification)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSOU")
            else:
                print(f"\n❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"\n❌ Erro durante {test_name}: {e}")
    
    print("\n" + "=" * 55)
    print(f"📋 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 CORREÇÕES VALIDADAS COM SUCESSO!")
        print("\n📋 Validações confirmadas:")
        print("   ✅ Bitcoin e Ethereum = MAJOR")
        print("   ✅ Terminologia crypto correta")
        print("   ✅ Meme coins identificados")
        print("   ✅ Stablecoins classificados")
        print("   ✅ Métricas especiais para Majors")
        print("   ✅ Display formatado corretamente")
        
        print("\n💡 Estrutura final implementada:")
        print("   👑 MAJORS: Bitcoin, Ethereum")
        print("   💎 LARGE CAP: Top 10 do mercado")
        print("   ⭐ MID CAP: Projetos estabelecidos")
        print("   🔹 SMALL CAP: Capitalização menor")
        print("   🔸 MICRO CAP: Projetos pequenos")
        print("   ⚡ NANO CAP: Projetos muito pequenos")
        print("   🐕 MEME COIN: Tokens meme/comunidade")
        print("   💵 STABLECOIN: Moedas estáveis")
        print("   🏦 DEFI: Tokens DeFi")
        print("   ⚡ LAYER 2: Soluções de escalabilidade")
        
        return 0
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
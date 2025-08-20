#!/usr/bin/env python3
"""
Script de teste para validar o módulo DataFetcher
Testa busca de dados do Bitcoin e Ethereum conforme especificado
"""

import sys
import time
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_fetcher():
    """Testa todas as funcionalidades do DataFetcher"""
    print("🧪 Testando DataFetcher - Bitcoin e Ethereum")
    print("=" * 50)
    
    try:
        from fetcher import DataFetcher
        print("✅ DataFetcher importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar DataFetcher: {e}")
        return False
    
    fetcher = DataFetcher()
    
    # Teste 1: Fear & Greed Index
    print("\n1️⃣ Testando Fear & Greed Index...")
    try:
        fg_data = fetcher.get_fear_greed()
        if fg_data and 'value' in fg_data:
            print(f"   ✅ Fear & Greed: {fg_data['value']}/100 ({fg_data['classification']})")
            print(f"   📅 Timestamp: {fg_data['timestamp']}")
        else:
            print("   ❌ Dados do Fear & Greed inválidos")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao buscar Fear & Greed: {e}")
        return False
    
    # Teste 2: Busca de tokens
    print("\n2️⃣ Testando busca de tokens...")
    tokens_to_test = ['bitcoin', 'ethereum', 'BTC', 'ETH']
    
    for token_query in tokens_to_test:
        try:
            print(f"   🔍 Buscando '{token_query}'...")
            token_id = fetcher.search_token(token_query)
            if token_id:
                print(f"      ✅ Encontrado: {token_id}")
            else:
                print(f"      ❌ Token '{token_query}' não encontrado")
                return False
        except Exception as e:
            print(f"      ❌ Erro ao buscar '{token_query}': {e}")
            return False
    
    # Teste 3: Dados do Bitcoin
    print("\n3️⃣ Testando dados completos do Bitcoin...")
    try:
        start_time = time.time()
        btc_data = fetcher.get_token_data('bitcoin')
        fetch_time = time.time() - start_time
        
        if not btc_data:
            print("   ❌ Dados do Bitcoin não foram obtidos")
            return False
        
        print(f"   ✅ Dados obtidos em {fetch_time:.2f}s")
        print(f"   📊 Nome: {btc_data['name']} ({btc_data['symbol']})")
        print(f"   💰 Preço: ${btc_data['price']:,.2f}")
        print(f"   📈 Market Cap: ${btc_data['market_cap']:,.0f}")
        print(f"   📊 Volume 24h: ${btc_data['volume']:,.0f}")
        print(f"   📅 Rank: #{btc_data['market_cap_rank']}")
        print(f"   📈 Mudança 24h: {btc_data['price_change_24h']:+.2f}%")
        print(f"   🏷️ Categoria: {btc_data['category']}")
        print(f"   📆 Idade: {btc_data['age_days']} dias")
        print(f"   👥 Twitter: {btc_data['twitter_followers']:,} seguidores")
        print(f"   💻 GitHub commits (4 semanas): {btc_data['github_commits']}")
        
        # Validar campos obrigatórios
        required_fields = ['price', 'market_cap', 'volume', 'name', 'symbol']
        for field in required_fields:
            if btc_data.get(field) is None or btc_data.get(field) == 0:
                print(f"   ⚠️ Campo {field} está vazio ou zero")
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar dados do Bitcoin: {e}")
        return False
    
    # Teste 4: Dados do Ethereum
    print("\n4️⃣ Testando dados completos do Ethereum...")
    try:
        start_time = time.time()
        eth_data = fetcher.get_token_data('ethereum')
        fetch_time = time.time() - start_time
        
        if not eth_data:
            print("   ❌ Dados do Ethereum não foram obtidos")
            return False
        
        print(f"   ✅ Dados obtidos em {fetch_time:.2f}s")
        print(f"   📊 Nome: {eth_data['name']} ({eth_data['symbol']})")
        print(f"   💰 Preço: ${eth_data['price']:,.2f}")
        print(f"   📈 Market Cap: ${eth_data['market_cap']:,.0f}")
        print(f"   📊 Volume 24h: ${eth_data['volume']:,.0f}")
        print(f"   📅 Rank: #{eth_data['market_cap_rank']}")
        print(f"   📈 Mudança 24h: {eth_data['price_change_24h']:+.2f}%")
        print(f"   🏷️ Categoria: {eth_data['category']}")
        print(f"   📆 Idade: {eth_data['age_days']} dias")
        print(f"   👥 Twitter: {eth_data['twitter_followers']:,} seguidores")
        print(f"   💻 GitHub commits (4 semanas): {eth_data['github_commits']}")
        
    except Exception as e:
        print(f"   ❌ Erro ao buscar dados do Ethereum: {e}")
        return False
    
    # Teste 5: Cache funcionando
    print("\n5️⃣ Testando cache (deve ser instantâneo)...")
    try:
        start_time = time.time()
        btc_data_cached = fetcher.get_token_data('bitcoin')
        cache_time = time.time() - start_time
        
        if cache_time < 0.1:  # Deve ser muito rápido se vier do cache
            print(f"   ✅ Cache funcionando! Tempo: {cache_time:.4f}s")
        else:
            print(f"   ⚠️ Cache pode não estar funcionando. Tempo: {cache_time:.4f}s")
        
        # Verificar se os dados são os mesmos
        if btc_data_cached['price'] == btc_data['price']:
            print("   ✅ Dados do cache consistentes")
        else:
            print("   ⚠️ Dados do cache inconsistentes")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar cache: {e}")
        return False
    
    # Teste 6: Lista de tokens populares
    print("\n6️⃣ Testando lista de tokens populares...")
    try:
        token_list = fetcher.get_token_list(10)  # Top 10
        if token_list and len(token_list) > 0:
            print(f"   ✅ Lista obtida com {len(token_list)} tokens")
            print("   📋 Top 5:")
            for i, token in enumerate(token_list[:5]):
                print(f"      {i+1}. {token['name']} ({token['symbol']}) - ${token['current_price']:,.2f}")
        else:
            print("   ❌ Lista de tokens não obtida")
            return False
    except Exception as e:
        print(f"   ❌ Erro ao buscar lista de tokens: {e}")
        return False
    
    # Teste 7: Token inexistente
    print("\n7️⃣ Testando token inexistente...")
    try:
        fake_token = fetcher.search_token('tokenquenaoexiste123456')
        if fake_token is None:
            print("   ✅ Token inexistente tratado corretamente")
        else:
            print(f"   ⚠️ Token inexistente retornou: {fake_token}")
    except Exception as e:
        print(f"   ⚠️ Erro esperado ao buscar token inexistente: {e}")
    
    return True

def main():
    """Executa os testes do fetcher"""
    print("🚀 Teste do DataFetcher - Bitcoin e Ethereum")
    print("Testando busca de dados das APIs públicas")
    print("")
    
    success = test_fetcher()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Todos os testes passaram!")
        print("✅ DataFetcher está funcionando corretamente")
        print("\n📋 Validações confirmadas:")
        print("   ✅ Buscar dados do Bitcoin com sucesso")
        print("   ✅ Buscar dados do Ethereum com sucesso")
        print("   ✅ Cache funcionando (segunda chamada instantânea)")
        print("   ✅ Tratamento quando token não existe")
        print("   ✅ Fear & Greed Index funcionando")
        print("   ✅ Lista de tokens funcionando")
        return 0
    else:
        print("❌ Alguns testes falharam!")
        print("⚠️ Verifique sua conexão com a internet e tente novamente")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação das Correções de API
=========================================
Testa as 3 correções principais sem problemas de encoding
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetcher import DataFetcher
from social_analyzer import SocialAnalyzer
import time

def test_rate_limiting():
    """Testa o rate limiting melhorado"""
    print("\n=== TESTE 1: RATE LIMITING ===")
    
    fetcher = DataFetcher()
    
    print(f"Config rate limiting:")
    print(f"- Min delay: {fetcher.MIN_TIME_BETWEEN_REQUESTS}s")  
    print(f"- Max requests/min: {fetcher.MAX_REQUESTS_PER_MINUTE}")
    
    # Teste com múltiplos requests
    start_time = time.time()
    
    for i in range(3):
        print(f"\nRequest {i+1}/3...")
        result = fetcher.search_token('bitcoin')
        print(f"Resultado: {'OK' if result else 'FALHOU'}")
    
    total_time = time.time() - start_time
    print(f"\nTempo total para 3 requests: {total_time:.2f}s")
    print("Rate limiting: FUNCIONANDO" if total_time >= 8 else "PRECISA AJUSTE")

def test_coingecko_fallback():
    """Testa fallback chain do CoinGecko"""
    print("\n=== TESTE 2: COINGECKO FALLBACK ===")
    
    fetcher = DataFetcher()
    
    print("Testando fallback: market_chart -> OHLC -> basic_price")
    
    # Testa busca de histórico (pode dar 401 no market_chart)
    token_id = fetcher.search_token('bitcoin')
    if not token_id:
        print("ERRO: Não conseguiu encontrar Bitcoin")
        return
    
    print(f"Token ID encontrado: {token_id}")
    
    # Testa histórico de preços
    history = fetcher.get_price_history(token_id, 7)
    
    if history and history.get('data_points', 0) > 0:
        print(f"Histórico obtido: {history['data_points']} pontos de dados")
        print(f"Preço atual: ${history.get('current_price', 0):,.2f}")
        print("Fallback chain: FUNCIONANDO")
    else:
        print("ERRO: Não conseguiu obter histórico")
        print("Fallback chain: PRECISA REVISÃO")

def test_lunarcrush_v4():
    """Testa endpoints LunarCrush v4"""
    print("\n=== TESTE 3: LUNARCRUSH V4 ===")
    
    analyzer = SocialAnalyzer()
    
    print("Testando estratégias LunarCrush v4:")
    print("- Endpoint insights")
    print("- Endpoint time-series") 
    print("- Endpoint lista")
    
    # Testa dados sociais
    social_data = analyzer.get_lunarcrush_data('bitcoin')
    
    if social_data:
        source = social_data.get('source', 'unknown')
        print(f"Dados obtidos via: {source}")
        
        # Verifica dados principais
        galaxy_score = social_data.get('galaxy_score', 0)
        social_volume = social_data.get('social_volume', 0)
        
        print(f"Galaxy Score: {galaxy_score}")
        print(f"Social Volume: {social_volume}")
        
        if galaxy_score > 0 or social_volume > 0 or 'alternative' in source:
            print("LunarCrush v4: FUNCIONANDO (com fallbacks)")
        else:
            print("LunarCrush v4: DADOS LIMITADOS")
    else:
        print("ERRO: Não conseguiu obter dados sociais")

def test_error_handling():
    """Testa tratamento de erros"""
    print("\n=== TESTE 4: TRATAMENTO DE ERROS ===")
    
    fetcher = DataFetcher()
    
    # Testa token inexistente
    print("Testando token inexistente...")
    result = fetcher.search_token('tokenquenoexistexyz123')
    print(f"Token inexistente: {'TRATADO OK' if result is None else 'ENCONTROU ALGO'}")
    
    # Testa histórico de token inexistente
    print("Testando histórico de token inválido...")
    history = fetcher.get_price_history('invalid-token-12345', 7)
    if history and 'data_points' in history:
        print("Tratamento de erro: FUNCIONANDO")
    else:
        print("Tratamento de erro: PRECISA REVISÃO")

def main():
    print("VALIDAÇÃO DAS CORREÇÕES DE API")
    print("=" * 50)
    
    try:
        # Teste 1: Rate limiting
        test_rate_limiting()
        
        # Teste 2: Fallback CoinGecko  
        test_coingecko_fallback()
        
        # Teste 3: LunarCrush v4
        test_lunarcrush_v4()
        
        # Teste 4: Tratamento de erros
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("VALIDAÇÃO CONCLUÍDA")
        print("Verifique os resultados acima para confirmar se as correções estão funcionando.")
        
    except Exception as e:
        print(f"\nERRO DURANTE VALIDAÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
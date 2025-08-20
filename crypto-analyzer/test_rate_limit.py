#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste específico do Rate Limiting
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetcher import DataFetcher

def test_rate_limit_detailed():
    """Teste detalhado do rate limiting"""
    print("TESTE DETALHADO DO RATE LIMITING")
    print("=" * 40)
    
    fetcher = DataFetcher()
    
    print(f"Configuração:")
    print(f"- MIN_TIME_BETWEEN_REQUESTS: {fetcher.MIN_TIME_BETWEEN_REQUESTS}s")
    print(f"- MAX_REQUESTS_PER_MINUTE: {fetcher.MAX_REQUESTS_PER_MINUTE}")
    
    # Teste com delays entre requests
    times = []
    
    print(f"\nTestando 5 requests consecutivos:")
    
    for i in range(5):
        start = time.time()
        
        # Simular um request
        fetcher._rate_limit()
        
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        
        print(f"Request {i+1}: {elapsed:.2f}s de delay")
    
    print(f"\nResultados:")
    print(f"- Delay médio: {sum(times)/len(times):.2f}s")
    print(f"- Delay mínimo: {min(times):.2f}s") 
    print(f"- Delay máximo: {max(times):.2f}s")
    
    # Verificar se está respeitando o mínimo
    min_expected = fetcher.MIN_TIME_BETWEEN_REQUESTS
    if min(times[1:]) >= min_expected - 0.1:  # Tolerância de 0.1s
        print(f"✓ Rate limiting FUNCIONANDO (respeitando {min_expected}s mínimo)")
    else:
        print(f"✗ Rate limiting FALHOU (não respeitando {min_expected}s mínimo)")
    
    print(f"\nTempo total: {sum(times):.2f}s")

if __name__ == "__main__":
    test_rate_limit_detailed()
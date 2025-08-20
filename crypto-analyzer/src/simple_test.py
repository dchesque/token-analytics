#!/usr/bin/env python3
"""
simple_test.py - Teste básico sem display para validar funcionamento
"""

from analyzer import CryptoAnalyzer

def test_core_functionality():
    """Testa funcionalidade básica sem display"""
    print('=== TESTE DE FUNCIONALIDADE BASICA ===\n')
    
    try:
        analyzer = CryptoAnalyzer()
        print('OK Analyzer criado com sucesso')
        
        # Teste 1: Buscar token
        print('\n1. Testando busca de token...')
        token_id = analyzer.fetcher.search_token('bitcoin')
        print(f'   Token ID encontrado: {token_id}')
        
        if not token_id:
            print('   ERRO: Token não encontrado')
            return False
            
        # Teste 2: Buscar dados do token
        print('\n2. Testando fetch de dados...')
        token_data = analyzer.fetcher.get_token_data(token_id)
        
        if token_data:
            print(f'   OK Dados obtidos: {len(token_data)} campos')
            print(f'   Symbol: {token_data.get("symbol", "N/A")}')
            print(f'   Name: {token_data.get("name", "N/A")}')
            print(f'   Price: ${token_data.get("price", 0):,.2f}')
            print(f'   Market Cap: ${token_data.get("market_cap", 0):,.0f}')
        else:
            print('   ERRO: Dados não obtidos')
            return False
            
        # Teste 3: Análise básica
        print('\n3. Testando análise básica...')
        result = analyzer.analyze('bitcoin')
        
        if result:
            print(f'   OK Analise concluida')
            print(f'   Passed elimination: {result.get("passed_elimination", False)}')
            print(f'   Score: {result.get("score", 0)}/10')
            print(f'   Classification: {result.get("classification", "N/A")}')
            
            # Verificar campos necessários para DisplayManager
            required_fields = [
                'token', 'token_name', 'passed_elimination', 'score',
                'score_breakdown', 'classification_info', 'data'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f'   AVISO: Campos ausentes: {missing_fields}')
            else:
                print('   OK Todos os campos obrigatorios presentes')
                
        else:
            print('   ERRO: Análise não retornou resultado')
            return False
            
        print('\n=== TESTE CONCLUÍDO COM SUCESSO ===')
        return True
        
    except Exception as e:
        print(f'\nERRO DURANTE TESTE: {e}')
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    print(f'\nResultado final: {"SUCESSO" if success else "FALHA"}')
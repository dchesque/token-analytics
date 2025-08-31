#!/usr/bin/env python3
"""
Test script to verify the new priority component initialization
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_initialization():
    """Test the new initialization function"""
    print("Testando inicializacao prioritaria de componentes")
    print("=" * 50)
    
    try:
        # Import and test the initialization
        from web_app import initialize_all_components
        
        print("Executando initialize_all_components()...")
        result = initialize_all_components()
        
        if result:
            print("SUCESSO: Inicializacao prioritaria concluida")
            print("Componentes criticos disponiveis")
        else:
            print("ATENCAO: Inicializacao com problemas")
            print("Alguns componentes criticos falharam")
        
        print("\nStatus geral:")
        print(f"   Resultado da inicializacao: {'SUCESSO' if result else 'FALHA PARCIAL'}")
        
        return result
        
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        return False
    except Exception as e:
        print(f"Erro durante teste: {e}")
        return False

if __name__ == "__main__":
    success = test_initialization()
    print("=" * 50)
    if success:
        print("TESTE CONCLUIDO: Sistema pronto para uso")
    else:
        print("TESTE COM PROBLEMAS: Verificar configuracao")
    
    sys.exit(0 if success else 1)
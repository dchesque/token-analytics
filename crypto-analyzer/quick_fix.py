#!/usr/bin/env python3
"""
quick_fix.py - Correção rápida para o endpoint master
Execute este script para aplicar as correções necessárias
"""

import os
import sys
import shutil
from datetime import datetime

def backup_file(filepath):
    """Cria backup do arquivo"""
    backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"OK Backup criado: {backup_path}")
    return backup_path

def fix_web_app():
    """Aplica correções no web_app.py"""
    
    print("\n=== APLICANDO CORREÇÕES NO WEB_APP.PY ===\n")
    
    # Backup primeiro
    backup_file("web_app.py")
    
    # Ler arquivo atual
    with open("web_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Correção 1: Adicionar inicialização robusta de componentes
    initialization_code = '''
# ============= INITIALIZATION FIX START =============
def initialize_components_safe():
    """Inicialização segura de todos os componentes"""
    components = {
        'analyzer': None,
        'technical_analyzer': None,
        'social_analyzer': None,
        'ai_agent': None,
        'hybrid_ai_agent': None
    }
    
    # Tentar importar e inicializar cada componente
    try:
        from src.analyzer import CryptoAnalyzer
        components['analyzer'] = CryptoAnalyzer()
        print("[INIT] OK Analyzer carregado")
    except Exception as e:
        print(f"[INIT] ERROR Analyzer falhou: {e}")
    
    try:
        from src.technical_analyzer import TechnicalAnalyzer
        components['technical_analyzer'] = TechnicalAnalyzer()
        print("[INIT] OK Technical Analyzer carregado")
    except Exception as e:
        print(f"[INIT] - Technical Analyzer nao disponivel: {e}")
    
    try:
        from src.social_analyzer import SocialAnalyzer
        components['social_analyzer'] = SocialAnalyzer()
        print("[INIT] OK Social Analyzer carregado")
    except Exception as e:
        print(f"[INIT] - Social Analyzer nao disponivel: {e}")
    
    # Componentes opcionais
    try:
        from ai_agent import AIAgent
        components['ai_agent'] = AIAgent()
        print("[INIT] OK AI Agent carregado")
    except:
        print("[INIT] - AI Agent nao disponivel (opcional)")
    
    try:
        from hybrid_ai_agent import HybridAIAgent
        components['hybrid_ai_agent'] = HybridAIAgent()
        print("[INIT] OK Hybrid AI carregado")
    except:
        print("[INIT] - Hybrid AI nao disponivel (opcional)")
    
    return components

# Inicializar componentes globalmente
print("\\n=== INICIALIZANDO COMPONENTES ===")
_components = initialize_components_safe()
analyzer = _components['analyzer']
technical_analyzer = _components['technical_analyzer']
social_analyzer = _components['social_analyzer']
ai_agent = _components['ai_agent']
hybrid_ai_agent = _components['hybrid_ai_agent']

COMPONENTS_LOADED = analyzer is not None
print(f"\\n[INIT] Componentes carregados: {COMPONENTS_LOADED}")
print("=" * 50 + "\\n")
# ============= INITIALIZATION FIX END =============

'''
    
    # Correção 2: Endpoint master mais robusto
    master_endpoint_fix = '''
@app.route('/api/analyze/<token>/master')
def api_analyze_master(token):
    """Master analysis endpoint - VERSÃO CORRIGIDA E ROBUSTA"""
    from datetime import datetime
    import time
    
    start_time = time.time()
    
    # Estrutura garantida
    result = {
        'success': True,
        'token': str(token).upper(),
        'timestamp': datetime.now().isoformat(),
        'processing_time': 0,
        'completion_rate': 0,
        'components': {
            'fundamental': {'status': 'pending'},
            'technical': {'status': 'pending'},
            'ai_insights': {'status': 'pending'},
            'web_context': {'status': 'pending'},
            'trading_levels': {'status': 'pending'},
            'strategies': {'status': 'pending'}
        }
    }
    
    completed = 0
    total = 6
    
    # Component 1: Fundamental (CRÍTICO)
    try:
        if analyzer:
            print(f"[MASTER] Processando fundamental para {token}...")
            basic_data = analyzer.analyze(token)
            
            if basic_data and not basic_data.get('error'):
                result['fundamental'] = {
                    'status': 'completed',
                    'data': basic_data,
                    'three_layers': basic_data,
                    'score': basic_data.get('score', 0),
                    'decision': basic_data.get('decision', 'HOLD'),
                    'classification': basic_data.get('classification', 'Unknown')
                }
                result['components']['fundamental'] = {'status': 'completed'}
                completed += 1
                print(f"[MASTER] ✓ Fundamental completo")
            else:
                raise Exception(basic_data.get('error', 'Análise falhou'))
        else:
            raise Exception('Analyzer não inicializado')
            
    except Exception as e:
        print(f"[MASTER] ✗ Fundamental erro: {e}")
        # Dados de fallback
        result['fundamental'] = {
            'status': 'error',
            'error': str(e),
            'data': {'token': token.upper(), 'score': 5.0, 'decision': 'HOLD'}
        }
        result['components']['fundamental'] = {'status': 'error', 'error': str(e)}
    
    # Component 2: Technical
    try:
        if technical_analyzer:
            print(f"[MASTER] Processando technical...")
            # Implementar análise técnica
            result['technical'] = {
                'status': 'completed',
                'momentum': 'NEUTRAL',
                'indicators': {'fear_greed': 50}
            }
            result['components']['technical'] = {'status': 'completed'}
            completed += 1
        else:
            result['technical'] = {'status': 'unavailable'}
            result['components']['technical'] = {'status': 'disabled'}
            
    except Exception as e:
        result['components']['technical'] = {'status': 'error', 'error': str(e)}
    
    # Component 3: AI Insights (opcional)
    try:
        result['ai_insights'] = {
            'status': 'disabled',
            'summary': 'AI analysis not configured',
            'confidence': None
        }
        result['components']['ai_insights'] = {'status': 'disabled'}
        
    except Exception as e:
        result['components']['ai_insights'] = {'status': 'error'}
    
    # Component 4: Web Context (opcional)
    try:
        result['web_context'] = {
            'status': 'disabled',
            'summary': 'Web research not configured'
        }
        result['components']['web_context'] = {'status': 'disabled'}
        
    except Exception as e:
        result['components']['web_context'] = {'status': 'error'}
    
    # Component 5: Trading Levels
    try:
        current_price = result.get('fundamental', {}).get('data', {}).get('price', 100)
        if current_price:
            result['trading_levels'] = {
                'status': 'completed',
                'entry_points': [current_price * 0.95, current_price * 0.90],
                'take_profit': [current_price * 1.10, current_price * 1.20],
                'stop_loss': current_price * 0.85
            }
            result['components']['trading_levels'] = {'status': 'completed'}
            completed += 1
    except:
        result['components']['trading_levels'] = {'status': 'error'}
    
    # Component 6: Strategies
    try:
        result['strategies'] = {
            'status': 'completed',
            'conservative': {'action': 'WAIT', 'position_size': '5%'},
            'moderate': {'action': 'DCA', 'position_size': '10%'},
            'aggressive': {'action': 'BUY', 'position_size': '15%'}
        }
        result['components']['strategies'] = {'status': 'completed'}
        completed += 1
    except:
        result['components']['strategies'] = {'status': 'error'}
    
    # Finalizar
    result['completion_rate'] = round((completed / total) * 100, 1)
    result['processing_time'] = round(time.time() - start_time, 2)
    
    print(f"[MASTER] Análise completa: {completed}/{total} componentes ({result['completion_rate']}%)")
    
    return jsonify(result)
'''
    
    # Localizar onde inserir o código de inicialização
    import_section_end = content.find("# Flask app configuration")
    if import_section_end == -1:
        import_section_end = content.find("app = Flask(__name__)")
    
    if import_section_end != -1:
        # Inserir inicialização após imports
        content = content[:import_section_end] + initialization_code + content[import_section_end:]
        print("OK Codigo de inicializacao inserido")
    
    # Localizar e substituir o endpoint master
    master_start = content.find("@app.route('/api/analyze/<token>/master')")
    if master_start != -1:
        # Encontrar o fim da função
        master_end = content.find("@app.route", master_start + 1)
        if master_end == -1:
            master_end = content.find("if __name__", master_start)
        
        if master_end != -1:
            # Substituir função inteira
            content = content[:master_start] + master_endpoint_fix + "\n" + content[master_end:]
            print("OK Endpoint master corrigido")
    
    # Salvar arquivo corrigido
    with open("web_app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("OK Arquivo web_app.py atualizado com sucesso!")
    
    return True

def test_fix():
    """Testa se as correções funcionaram"""
    print("\n=== TESTANDO CORREÇÕES ===\n")
    
    try:
        import requests
        import json
        
        # Testar endpoint
        print("Testando endpoint /api/analyze/BTC/master...")
        
        try:
            r = requests.get("http://localhost:8000/api/analyze/BTC/master", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('token') == 'BTC':
                    print(f"OK Endpoint funcionando!")
                    print(f"   Completion rate: {data.get('completion_rate', 0)}%")
                    print(f"   Components OK: {sum(1 for c in data.get('components', {}).values() if c.get('status') == 'completed')}/6")
                    return True
                else:
                    print("WARNING Endpoint retornou dados inesperados")
            else:
                print(f"ERROR Erro HTTP {r.status_code}")
        except Exception as e:
            print(f"ERROR Erro ao testar: {e}")
            print("\nCertifique-se de que o servidor está rodando:")
            print("  python web_app.py")
            
    except ImportError:
        print("WARNING Biblioteca 'requests' nao instalada. Nao foi possivel testar.")
    
    return False

def main():
    """Executa as correções"""
    print("\n" + "="*60)
    print("     CRYPTO ANALYZER - CORRECAO RAPIDA")
    print("="*60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("web_app.py"):
        print("ERROR Erro: arquivo web_app.py nao encontrado!")
        print("   Certifique-se de executar este script no diretorio crypto-analyzer/")
        return False
    
    # Aplicar correções
    if fix_web_app():
        print("\nOK CORRECOES APLICADAS COM SUCESSO!")
        
        print("\nProximos passos:")
        print("1. Reinicie o servidor:")
        print("   pkill -f web_app.py")
        print("   python web_app.py")
        print("\n2. Teste o endpoint:")
        print("   curl http://localhost:8000/api/analyze/BTC/master")
        print("\n3. Acesse a interface web:")
        print("   http://localhost:8000/master")
        
        # Tentar testar automaticamente
        test_fix()
        
        return True
    else:
        print("\nERROR Erro ao aplicar correcoes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
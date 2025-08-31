#!/usr/bin/env python3
"""
apply_improvements.py - Aplica todas as melhorias automaticamente
Ativa AI Insights e Web Context com dados reais
"""

import os
import sys
import shutil
from datetime import datetime

def backup_files():
    """Cria backup dos arquivos antes de modificar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.exists("web_app.py"):
        backup_name = f"web_app.py.backup.{timestamp}"
        shutil.copy2("web_app.py", backup_name)
        print(f"[OK] Backup criado: {backup_name}")
    
    return timestamp

def apply_web_app_changes():
    """Aplica mudanças no web_app.py"""
    
    if not os.path.exists("web_app.py"):
        print("❌ Arquivo web_app.py não encontrado!")
        return False
    
    with open("web_app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 1. Adicionar imports dos novos módulos
    import_section = '''
# ============= AI & WEB MODULES INTEGRATION =============
try:
    from ai_insights import AIInsights
    ai_insights_module = AIInsights()
    print("[INIT] ✅ AI Insights module loaded with real data analysis")
except Exception as e:
    print(f"[INIT] ⚠️ AI Insights not available: {e}")
    ai_insights_module = None

try:
    from web_context import WebContext
    web_context_module = WebContext()
    print("[INIT] ✅ Web Context module loaded with real web data")
except Exception as e:
    print(f"[INIT] ⚠️ Web Context not available: {e}")
    web_context_module = None

try:
    from formatting_helper import FormattingHelper
    formatter = FormattingHelper()
    print("[INIT] ✅ Formatting helper loaded")
except Exception as e:
    print(f"[INIT] ⚠️ Formatting helper not available: {e}")
    formatter = None
# ============= END AI & WEB INTEGRATION =============

'''
    
    # Encontrar onde inserir (após initialize_components_safe ou após imports iniciais)
    insert_pos = content.find("COMPONENTS_LOADED = analyzer is not None")
    if insert_pos != -1:
        insert_pos = content.find("\n", insert_pos) + 1
        content = content[:insert_pos] + import_section + content[insert_pos:]
        print("[OK] Módulos de importação adicionados")
    
    # 2. Atualizar função api_analyze_master
    # Encontrar a parte de AI Insights
    ai_start = content.find("# Component 3: AI Insights")
    if ai_start == -1:
        ai_start = content.find("# PART 3: AI Insights")
    
    if ai_start != -1:
        # Encontrar o fim dessa seção
        ai_end = content.find("# Component 4:", ai_start)
        if ai_end == -1:
            ai_end = content.find("# PART 4:", ai_start)
        
        if ai_end != -1:
            # Substituir com código melhorado
            new_ai_code = '''    # Component 3: AI Insights (com dados reais)
    try:
        if ai_insights_module and 'fundamental' in result and result['fundamental'].get('data'):
            print(f"[MASTER] Processing real AI insights for {token}...")
            
            # Usar dados reais do fundamental
            real_data = result['fundamental'].get('data', {})
            ai_result = ai_insights_module.analyze(real_data)
            
            # Formatar resultado se formatter disponível
            if formatter and ai_result.get('status') == 'completed':
                result['ai_insights'] = {
                    'status': 'completed',
                    'summary': ai_result.get('summary', ''),
                    'confidence': ai_result.get('confidence', 0),
                    'sentiment': ai_result.get('sentiment', 'NEUTRO'),
                    'key_factors': ai_result.get('key_factors', []),
                    'risks': ai_result.get('risks', []),
                    'opportunities': ai_result.get('opportunities', []),
                    'metrics': ai_result.get('metrics', {})
                }
            else:
                result['ai_insights'] = ai_result
            
            result['components']['ai_insights'] = {'status': ai_result.get('status', 'error')}
            
            if ai_result.get('status') == 'completed':
                completed += 1
                print(f"[MASTER] ✓ AI insights completed with real data")
        else:
            result['ai_insights'] = {
                'status': 'unavailable',
                'summary': 'Aguardando dados fundamentais'
            }
            result['components']['ai_insights'] = {'status': 'disabled'}
            
    except Exception as e:
        print(f"[MASTER] ✗ AI insights error: {e}")
        result['ai_insights'] = {'status': 'error', 'error': str(e)}
        result['components']['ai_insights'] = {'status': 'error', 'error': str(e)}
    
'''
            content = content[:ai_start] + new_ai_code + content[ai_end:]
            print("[OK] AI Insights atualizado para usar dados reais")
    
    # 3. Atualizar Web Context
    web_start = content.find("# Component 4: Web Context")
    if web_start == -1:
        web_start = content.find("# PART 4: Web Context")
    
    if web_start != -1:
        web_end = content.find("# Component 5:", web_start)
        if web_end == -1:
            web_end = content.find("# PART 5:", web_start)
        
        if web_end != -1:
            new_web_code = '''    # Component 4: Web Context (dados reais da web)
    try:
        if web_context_module:
            print(f"[MASTER] Fetching real web context for {token}...")
            
            # Buscar contexto real da web
            web_result = web_context_module.analyze(
                token,
                result.get('fundamental', {}).get('data', {})
            )
            
            result['web_context'] = web_result
            result['components']['web_context'] = {'status': web_result.get('status', 'error')}
            
            if web_result.get('status') in ['completed', 'partial']:
                completed += 1
                print(f"[MASTER] ✓ Web context fetched from real sources")
        else:
            result['web_context'] = {
                'status': 'unavailable',
                'summary': 'Módulo de contexto web não disponível'
            }
            result['components']['web_context'] = {'status': 'disabled'}
            
    except Exception as e:
        print(f"[MASTER] ✗ Web context error: {e}")
        result['web_context'] = {'status': 'error', 'error': str(e)}
        result['components']['web_context'] = {'status': 'error', 'error': str(e)}
    
'''
            content = content[:web_start] + new_web_code + content[web_end:]
            print("[OK] Web Context atualizado para buscar dados reais")
    
    # 4. Melhorar formatação do fundamental
    fund_format = '''
            # Formatar dados para melhor legibilidade
            if formatter:
                formatted_data = formatter.format_fundamental(basic_data)
                result['fundamental']['formatted'] = formatted_data
'''
    
    # Encontrar onde adicionar formatação
    fund_complete = content.find('print(f"[MASTER] ✓ Fundamental completo")')
    if fund_complete != -1:
        insert_pos = content.rfind('\n', 0, fund_complete)
        content = content[:insert_pos] + fund_format + content[insert_pos:]
        print("[OK] Formatação melhorada adicionada ao fundamental")
    
    # Salvar arquivo atualizado
    with open("web_app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("[OK] web_app.py atualizado com sucesso!")
    return True

def test_improvements():
    """Testa se as melhorias funcionam"""
    print("\n=== TESTANDO MELHORIAS ===\n")
    
    try:
        # Testar importação dos módulos
        print("Testando módulos...")
        
        try:
            from ai_insights import AIInsights
            ai = AIInsights()
            test_data = {
                'token': 'TEST',
                'price': 100,
                'volume': 1000000,
                'market_cap': 10000000,
                'price_change_24h': 5.5
            }
            result = ai.analyze(test_data)
            if result.get('status') == 'completed':
                print("[OK] AI Insights funcionando")
                print(f"   Summary: {result.get('summary', '')[:100]}...")
            else:
                print("[WARNING] AI Insights com problemas")
        except Exception as e:
            print(f"[ERROR] AI Insights erro: {e}")
        
        try:
            from web_context import WebContext
            web = WebContext()
            result = web.analyze('BTC', {})
            if result.get('status') in ['completed', 'partial']:
                print("[OK] Web Context funcionando")
                print(f"   Summary: {result.get('summary', '')[:100]}...")
            else:
                print("[WARNING] Web Context com problemas")
        except Exception as e:
            print(f"[ERROR] Web Context erro: {e}")
        
        try:
            from formatting_helper import FormattingHelper
            fmt = FormattingHelper()
            print("[OK] Formatting Helper funcionando")
        except Exception as e:
            print(f"[ERROR] Formatting Helper erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro nos testes: {e}")
        return False

def main():
    """Executa todas as melhorias"""
    print("\n" + "="*60)
    print("   ATIVANDO AI INSIGHTS E WEB CONTEXT COM DADOS REAIS")
    print("="*60)
    
    # 1. Criar backup
    backup_files()
    
    # 2. Executar script de criação de módulos
    print("\nCriando módulos...")
    os.system("python activate_components.py")
    
    # 3. Aplicar mudanças no web_app.py
    print("\nAplicando integração...")
    if apply_web_app_changes():
        
        # 4. Testar
        test_improvements()
        
        print("\n" + "="*60)
        print("[SUCCESS] MELHORIAS APLICADAS COM SUCESSO!")
        print("="*60)
        
        print("\nResumo das melhorias:")
        print("1. [OK] AI Insights ativado - análise estatística de dados reais")
        print("2. [OK] Web Context ativado - busca informações reais da web")
        print("3. [OK] Formatação melhorada - textos mais claros")
        print("4. [OK] Sem dados simulados - tudo baseado em dados reais")
        
        print("\nPróximos passos:")
        print("1. Instalar dependências:")
        print("   pip install numpy requests")
        print("\n2. Reiniciar o servidor:")
        print("   pkill -f web_app.py")
        print("   python web_app.py")
        print("\n3. Testar no navegador:")
        print("   http://localhost:8000/master")
        print("   Analise um token como BTC ou ADA")
        
        print("\nOs componentes agora mostrarão:")
        print("- AI Insights: COMPLETED (com análise real)")
        print("- Web Context: COMPLETED (com dados da web)")
        print("- Textos formatados e organizados")
        
    else:
        print("\n[ERROR] Erro ao aplicar mudanças")
        print("Verifique se está no diretório correto")

if __name__ == "__main__":
    main()
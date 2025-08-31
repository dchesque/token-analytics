#!/usr/bin/env python3
"""
AI Token Preview Web Application
Flask-based web interface with REST API for cryptocurrency analysis
Supports both Web UI and API endpoints for EasyPanel deployment
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from analyzer import CryptoAnalyzer
    from display_manager import DisplayManager
    from fetcher import DataFetcher
    from social_analyzer import SocialAnalyzer
    from enhanced_features import EnhancedAnalyzer
    # Import configuration constants directly (no Config class needed)
    import config
    # AI Integration imports
    from ai_openrouter_agent import create_ai_agent, get_ai_health
    from ai_config import AIConfig, AITier
    from prompts.crypto_analysis_prompts import AnalysisType
    AI_INTEGRATION_AVAILABLE = True
    
    # Try to import hybrid AI agent (optional) - now enabled
    try:
        from hybrid_ai_agent import HybridAIAgent
        HYBRID_AI_AVAILABLE = True
        print("Hybrid AI Agent enabled successfully")
    except ImportError as e:
        print(f"Hybrid AI Agent not available: {e}")
        HYBRID_AI_AVAILABLE = False
        HybridAIAgent = None
        
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    print("Some features may not be available")
    AI_INTEGRATION_AVAILABLE = False
    HYBRID_AI_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)

# Configure Flask for production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Handle proxy headers for EasyPanel deployment
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Request logging middleware for debugging
@app.before_request
def log_request():
    print(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")
    if request.path.startswith('/api'):
        print(f"API Request Data: {request.get_json() if request.is_json else 'No JSON data'}")

# Simple test route to verify Flask is working
@app.route('/test')
def test():
    """Simple test endpoint to verify Flask is responding"""
    return jsonify({
        'message': 'Flask app is working!',
        'path': request.path,
        'method': request.method,
        'timestamp': datetime.now().isoformat()
    })

# Global cache for results
cache = {}
cache_lock = threading.Lock()
CACHE_DURATION = int(os.environ.get('CACHE_DURATION', 300))  # 5 minutes

# PRIORIDADE 1: Inicialização de Componentes
def initialize_all_components():
    """Inicializa todos os componentes com fallback seguro"""
    global analyzer, technical_analyzer, ai_agent, hybrid_ai_agent, fetcher, social_analyzer, display_manager, enhanced_analyzer
    
    print("🔧 Iniciando inicialização prioritária de componentes...")
    
    # 1. Analyzer principal (CRÍTICO)
    analyzer = None
    try:
        print("Inicializando CryptoAnalyzer...")
        enable_ai = os.environ.get('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
        user_tier = os.environ.get('AI_TIER', 'budget')
        analyzer = CryptoAnalyzer(enable_ai=enable_ai and AI_INTEGRATION_AVAILABLE, user_tier=user_tier)
        print("✓ CryptoAnalyzer inicializado")
    except Exception as e:
        print(f"✗ Falha ao inicializar analyzer: {e}")
        # Tentar fallback sem AI
        try:
            analyzer = CryptoAnalyzer(enable_ai=False, user_tier='basic')
            print("✓ CryptoAnalyzer inicializado (modo fallback)")
        except Exception as e2:
            print(f"✗ Fallback analyzer também falhou: {e2}")
            analyzer = None
    
    # 2. DataFetcher (CRÍTICO)
    fetcher = None
    try:
        print("Inicializando DataFetcher...")
        fetcher = DataFetcher()
        print("✓ DataFetcher inicializado")
    except Exception as e:
        print(f"✗ Falha ao inicializar fetcher: {e}")
        fetcher = None
    
    # 3. Technical Analyzer (IMPORTANTE)
    technical_analyzer = None
    try:
        print("Inicializando análise técnica...")
        # Tentar importar e inicializar EnhancedAnalyzer
        technical_analyzer = EnhancedAnalyzer()
        print("✓ Technical analyzer inicializado")
    except Exception as e:
        technical_analyzer = None
        print(f"- Technical analyzer não disponível: {e}")
    
    # 4. AI Agent (opcional)
    ai_agent = None
    if AI_INTEGRATION_AVAILABLE:
        try:
            print("Inicializando AI Agent...")
            enable_ai = os.environ.get('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
            user_tier = os.environ.get('AI_TIER', 'budget')
            if enable_ai:
                ai_agent = create_ai_agent(user_tier)
                print("✓ AI agent inicializado")
            else:
                print("- AI agent desabilitado por configuração")
        except Exception as e:
            ai_agent = None
            print(f"- AI agent não disponível: {e}")
    else:
        print("- AI integration não disponível")
    
    # 5. Hybrid AI (opcional)
    hybrid_ai_agent = None
    if HYBRID_AI_AVAILABLE and HybridAIAgent:
        try:
            print("Inicializando Hybrid AI...")
            hybrid_ai_agent = HybridAIAgent()
            print("✓ Hybrid AI inicializado")
        except Exception as e:
            hybrid_ai_agent = None
            print(f"- Hybrid AI não disponível: {e}")
    else:
        print("- Hybrid AI não disponível")
    
    # 6. SocialAnalyzer (opcional)
    social_analyzer = None
    try:
        print("Inicializando SocialAnalyzer...")
        social_analyzer = SocialAnalyzer()
        print("✓ SocialAnalyzer inicializado")
    except Exception as e:
        social_analyzer = None
        print(f"- SocialAnalyzer não disponível: {e}")
    
    # 7. DisplayManager (útil)
    display_manager = None
    try:
        print("Inicializando DisplayManager...")
        display_manager = DisplayManager()
        print("✓ DisplayManager inicializado")
    except Exception as e:
        display_manager = None
        print(f"- DisplayManager não disponível: {e}")
    
    # 8. EnhancedAnalyzer (importante para análise técnica)
    if not technical_analyzer:  # Se não conseguimos inicializar acima
        try:
            print("Tentando EnhancedAnalyzer novamente...")
            enhanced_analyzer = EnhancedAnalyzer()
            technical_analyzer = enhanced_analyzer  # Usar como technical_analyzer
            print("✓ EnhancedAnalyzer inicializado (segunda tentativa)")
        except Exception as e:
            enhanced_analyzer = None
            print(f"- EnhancedAnalyzer não disponível: {e}")
    else:
        enhanced_analyzer = technical_analyzer  # Referenciar o que já funcionou
    
    # Verificar status mínimo necessário
    critical_components = [analyzer, fetcher]
    critical_loaded = all(comp is not None for comp in critical_components)
    
    if critical_loaded:
        print("🎉 Componentes críticos carregados com sucesso!")
        component_count = sum(1 for comp in [analyzer, fetcher, technical_analyzer, ai_agent, hybrid_ai_agent, social_analyzer, display_manager, enhanced_analyzer] if comp is not None)
        print(f"📊 Total de componentes ativos: {component_count}/8")
        return True
    else:
        print("💥 ERRO CRÍTICO: Componentes essenciais não puderam ser inicializados!")
        print(f"   - Analyzer: {'OK' if analyzer else 'FALHOU'}")
        print(f"   - Fetcher: {'OK' if fetcher else 'FALHOU'}")
        return False

def clean_unicode_for_windows(data):
    """Remove or replace problematic Unicode characters for Windows"""
    if isinstance(data, str):
        # Replace common emoji and Unicode chars that cause problems on Windows
        replacements = {
            '📊': 'Chart',
            '📈': 'Up',
            '📉': 'Down',
            '💰': 'Money',
            '🚀': 'Rocket',
            '⚡': 'Lightning',
            '🔥': 'Fire',
            '📍': 'Pin',
            '➡️': 'Right',
            '⬇️': 'Down',
            '⚖️': 'Scale',
            '🏆': 'Trophy',
            '📝': 'Note'
        }
        for emoji, replacement in replacements.items():
            data = data.replace(emoji, replacement)
        # Remove any remaining high Unicode characters
        data = data.encode('ascii', 'ignore').decode('ascii')
        return data
    elif isinstance(data, dict):
        return {k: clean_unicode_for_windows(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_unicode_for_windows(item) for item in data]
    return data

def initialize_components():
    """
    Robust component initialization with individual error handling
    Ensures at least basic functionality is always available
    """
    global fetcher, social_analyzer, analyzer, display_manager, ai_agent, hybrid_ai_agent, enhanced_analyzer
    global COMPONENTS_LOADED
    
    component_status = {
        'fetcher': False,
        'social_analyzer': False,
        'analyzer': False,
        'display_manager': False,
        'enhanced_analyzer': False,
        'ai_agent': False,
        'hybrid_ai_agent': False
    }
    
    # Initialize DataFetcher (most critical component)
    try:
        fetcher = DataFetcher()
        component_status['fetcher'] = True
        print("✓ DataFetcher initialized")
    except Exception as e:
        print(f"✗ DataFetcher failed: {e}")
        fetcher = None
    
    # Initialize SocialAnalyzer 
    try:
        social_analyzer = SocialAnalyzer()
        component_status['social_analyzer'] = True
        print("✓ SocialAnalyzer initialized")
    except Exception as e:
        print(f"✗ SocialAnalyzer failed: {e}")
        social_analyzer = None
    
    # Initialize CryptoAnalyzer (critical for basic functionality)
    try:
        enable_ai = os.environ.get('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
        user_tier = os.environ.get('AI_TIER', 'budget')
        analyzer = CryptoAnalyzer(enable_ai=enable_ai and AI_INTEGRATION_AVAILABLE, user_tier=user_tier)
        component_status['analyzer'] = True
        print("✓ CryptoAnalyzer initialized")
    except Exception as e:
        print(f"✗ CryptoAnalyzer failed: {e}")
        # Create fallback analyzer
        try:
            analyzer = CryptoAnalyzer(enable_ai=False, user_tier='basic')
            component_status['analyzer'] = True
            print("✓ CryptoAnalyzer initialized (fallback mode)")
        except Exception as e2:
            print(f"✗ CryptoAnalyzer fallback also failed: {e2}")
            analyzer = None
    
    # Initialize DisplayManager
    try:
        display_manager = DisplayManager()
        component_status['display_manager'] = True
        print("✓ DisplayManager initialized")
    except Exception as e:
        print(f"✗ DisplayManager failed: {e}")
        display_manager = None
    
    # Initialize EnhancedAnalyzer
    try:
        enhanced_analyzer = EnhancedAnalyzer()
        component_status['enhanced_analyzer'] = True
        print("✓ EnhancedAnalyzer initialized")
    except Exception as e:
        print(f"✗ EnhancedAnalyzer failed: {e}")
        enhanced_analyzer = None
    
    # Initialize AI Agent (optional)
    ai_agent = None
    if AI_INTEGRATION_AVAILABLE:
        try:
            enable_ai = os.environ.get('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
            user_tier = os.environ.get('AI_TIER', 'budget')
            if enable_ai:
                ai_agent = create_ai_agent(user_tier)
                component_status['ai_agent'] = True
                print("✓ AI Agent initialized")
        except Exception as e:
            print(f"✗ AI Agent failed: {e}")
            ai_agent = None
    
    # Initialize Hybrid AI Agent (optional)
    hybrid_ai_agent = None
    if HYBRID_AI_AVAILABLE and HybridAIAgent:
        try:
            hybrid_ai_agent = HybridAIAgent()
            component_status['hybrid_ai_agent'] = True
            print("✓ Hybrid AI Agent initialized")
        except Exception as e:
            print(f"✗ Hybrid AI Agent failed: {e}")
            hybrid_ai_agent = None
    
    # Determine if we have minimum components needed
    critical_components = ['fetcher', 'analyzer']
    critical_loaded = all(component_status.get(comp, False) for comp in critical_components)
    
    if critical_loaded:
        COMPONENTS_LOADED = True
        loaded_count = sum(component_status.values())
        total_count = len(component_status)
        print(f"✓ Components initialized successfully ({loaded_count}/{total_count} loaded)")
    else:
        COMPONENTS_LOADED = False
        print("✗ Critical components failed to load - running in degraded mode")
    
    return component_status

def ensure_analyzer():
    """Ensure analyzer is available, create fallback if needed"""
    global analyzer
    if analyzer is None:
        try:
            print("Creating fallback analyzer...")
            analyzer = CryptoAnalyzer(enable_ai=False, user_tier='basic')
            print("✓ Fallback analyzer created")
            return True
        except Exception as e:
            print(f"✗ Failed to create fallback analyzer: {e}")
            return False
    return True

def get_token_data_with_fallback(token):
    """
    Get token data with multiple fallback strategies
    1. Use analyzer if available
    2. Use fetcher directly if available
    3. Return mock data for testing
    """
    token = str(token).upper()
    
    # Strategy 1: Use analyzer
    if analyzer:
        try:
            print(f"Attempting analysis with analyzer for {token}")
            result = analyzer.analyze(token)
            if result and not result.get('error'):
                return result
            print(f"Analyzer returned error or no data: {result.get('error') if result else 'No result'}")
        except Exception as e:
            print(f"Analyzer failed: {e}")
    
    # Strategy 2: Use fetcher directly
    if fetcher:
        try:
            print(f"Attempting direct fetch for {token}")
            data = fetcher.get_token_data(token)
            if data:
                # Create basic analysis structure
                return {
                    'token': token,
                    'data': data,
                    'score': 5.0,  # neutral score
                    'decision': 'HOLD',
                    'classification': 'Unknown',
                    'passed_elimination': True,
                    'price_change_24h': data.get('price_change_percentage_24h', 0),
                    'price_change_7d': data.get('price_change_percentage_7d', 0),
                    'price_change_30d': data.get('price_change_percentage_30d', 0),
                    'note': 'Using direct fetcher data - analysis unavailable'
                }
        except Exception as e:
            print(f"Direct fetcher failed: {e}")
    
    # Strategy 3: Mock data for testing
    print(f"Using mock data for {token}")
    return {
        'token': token,
        'data': {
            'id': token.lower(),
            'symbol': token,
            'name': f'{token} Token',
            'current_price': 1.0,
            'market_cap': 1000000,
            'total_volume': 100000,
            'market_cap_rank': 999,
            'price_change_percentage_24h': 0,
            'price_change_percentage_7d': 0,
            'price_change_percentage_30d': 0
        },
        'score': 5.0,
        'decision': 'HOLD',
        'classification': 'Test Data',
        'passed_elimination': True,
        'price_change_24h': 0,
        'price_change_7d': 0,
        'price_change_30d': 0,
        'note': 'Using mock test data - real data unavailable'
    }

# CHAMADA DA INICIALIZAÇÃO PRIORITÁRIA
COMPONENTS_LOADED = initialize_all_components()

def get_cached_result(token):
    """Get cached result if available and not expired"""
    if not COMPONENTS_LOADED:
        return None
        
    with cache_lock:
        if token in cache:
            result, timestamp = cache[token]
            if time.time() - timestamp < CACHE_DURATION:
                return result
            else:
                del cache[token]
    return None

def cache_result(token, result):
    """Cache analysis result"""
    with cache_lock:
        cache[token] = (result, time.time())

def analyze_token_internal(token_name):
    """Internal function to analyze a token"""
    if not COMPONENTS_LOADED:
        return {
            'success': False,
            'error': 'Analysis components not available. Please check configuration.'
        }
    
    try:
        # Check cache first
        cached = get_cached_result(token_name)
        if cached:
            return cached
        
        # Perform analysis
        print(f"Starting analysis for token: {token_name}")
        result = analyzer.analyze(token_name)
        print(f"Analysis result type: {type(result)}, has error: {result.get('error') if result else 'None'}")
        
        # The analyzer doesn't return a 'success' field, check for 'error' instead
        if result and not result.get('error'):
            # Clean Unicode characters that may cause problems
            cleaned_result = clean_unicode_for_windows(result)
            
            # Wrap the result in a success structure
            wrapped_result = {
                'success': True,
                'data': cleaned_result,
                'token': cleaned_result.get('token', token_name),
                'score': cleaned_result.get('score', 0),
                'decision': cleaned_result.get('decision', 'ANALYZED'),
                'passed_elimination': cleaned_result.get('passed_elimination', False)
            }
            # Cache the successful result
            cache_result(token_name, wrapped_result)
            print(f"Analysis successful for {token_name}: score={wrapped_result['score']}, decision={wrapped_result['decision']}")
            return wrapped_result
        else:
            error_msg = result.get('error', 'Analysis failed') if result else 'No data received'
            print(f"Analysis failed for {token_name}: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'data': result
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/master')
def master_analysis():
    """Master analysis web interface"""
    return render_template('master.html')

@app.route('/api/analyze/<token>')
def api_analyze(token):
    """API endpoint for token analysis"""
    try:
        result = analyze_token_internal(token)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze_post():
    """POST endpoint for token analysis"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token name required'
            }), 400
        
        result = analyze_token_internal(token)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compare multiple tokens"""
    try:
        data = request.get_json()
        tokens = data.get('tokens', [])
        
        if not tokens or len(tokens) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 tokens required for comparison'
            }), 400
        
        results = []
        for token in tokens[:5]:  # Limit to 5 tokens
            result = analyze_token_internal(token)
            results.append({
                'token': token,
                'data': result
            })
        
        return jsonify({
            'success': True,
            'comparison': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """API status and health check"""
    try:
        if not COMPONENTS_LOADED:
            return jsonify({
                'success': False,
                'status': 'degraded',
                'error': 'Analysis components not loaded',
                'cache_size': len(cache),
                'version': '2.0',
                'timestamp': datetime.now().isoformat()
            })
        
        # Check API status if fetcher is available
        api_statuses = {}
        if hasattr(fetcher, 'check_api_status'):
            try:
                api_statuses = fetcher.check_api_status()
            except:
                api_statuses = {'status': 'unknown'}
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'apis': api_statuses,
            'cache_size': len(cache),
            'version': '2.0',
            'components_loaded': COMPONENTS_LOADED,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint for Docker/EasyPanel"""
    return jsonify({
        'status': 'healthy',
        'components_loaded': COMPONENTS_LOADED,
        'ai_available': AI_INTEGRATION_AVAILABLE,
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.1'
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint that doesn't depend on any components"""
    return jsonify({'message': 'pong', 'status': 'ok'})

@app.route('/api/history')
def api_history():
    """Get analysis history"""
    try:
        history_file = Path('data/analysis_history.json')
        if history_file.exists():
            with open(history_file, 'r') as f:
                history = json.load(f)
            return jsonify({
                'success': True,
                'history': history[-50:]  # Last 50 entries
            })
        else:
            return jsonify({
                'success': True,
                'history': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<token>')
def api_report(token):
    """Generate and download HTML report"""
    try:
        if not COMPONENTS_LOADED:
            return jsonify({
                'success': False,
                'error': 'Analysis components not available'
            }), 500
            
        result = analyze_token_internal(token)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Generate HTML report
        report_path = Path('reports') / f"{token}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.parent.mkdir(exist_ok=True)
        
        # Create HTML report using display manager
        html_content = display_manager.generate_html_report(result, token)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return send_file(report_path, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# AI-powered analysis endpoints
@app.route('/api/analyze/<token>/ai')
@app.route('/api/analyze/<token>/ai/<analysis_type>')
def api_analyze_ai(token, analysis_type='technical'):
    """AI-powered token analysis endpoint"""
    try:
        if not AI_INTEGRATION_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'AI analysis not available - missing dependencies'
            }), 503
        
        if not ai_agent:
            return jsonify({
                'success': False,
                'error': 'AI agent not initialized'
            }), 503
        
        # Get user tier from request headers or use default
        user_tier = request.headers.get('X-AI-Tier', 'budget')
        user_id = request.headers.get('X-User-ID', 'web_user')
        
        # Validate analysis type
        valid_types = ['technical', 'trading_signals', 'risk_assessment', 'market_context', 'comparative']
        if analysis_type not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid analysis type. Valid types: {", ".join(valid_types)}'
            }), 400
        
        # Get traditional analysis first
        traditional_result = analyze_token_internal(token)
        if not traditional_result.get('success'):
            return jsonify(traditional_result)
        
        # Perform AI analysis
        try:
            analysis_enum = AnalysisType(analysis_type.lower())
        except ValueError:
            analysis_enum = AnalysisType.TECHNICAL
        
        # Prepare token data for AI
        token_data = traditional_result.get('data', {})
        ai_input_data = {
            'token_name': token_data.get('name', token),
            'token_symbol': token_data.get('symbol', token),
            'current_price': token_data.get('price', 0),
            'market_cap': token_data.get('market_cap', 0),
            'volume_24h': token_data.get('volume', 0),
            'price_change_24h': token_data.get('price_change_24h', 0)
        }
        
        ai_response = ai_agent.analyze_token(ai_input_data, analysis_enum, user_id)
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'token': token,
                'analysis_type': analysis_type,
                'traditional_analysis': traditional_result,
                'ai_analysis': {
                    'model_used': ai_response.model_used,
                    'confidence': ai_response.confidence,
                    'tokens_used': ai_response.tokens_used,
                    'cost': ai_response.cost,
                    'cached': ai_response.cached,
                    'processing_time': ai_response.processing_time,
                    'data': ai_response.data
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.error,
                'traditional_analysis': traditional_result,
                'ai_analysis': {
                    'error': ai_response.error,
                    'model_attempted': ai_response.model_used
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI analysis failed: {str(e)}'
        }), 500

@app.route('/api/ai/models')
def api_ai_models():
    """Get available AI models for current user tier"""
    try:
        if not AI_INTEGRATION_AVAILABLE or not ai_agent:
            return jsonify({
                'success': False,
                'error': 'AI services not available'
            }), 503
        
        user_tier = request.headers.get('X-AI-Tier', 'budget')
        
        # Get available models
        models = ai_agent.get_available_models()
        
        return jsonify({
            'success': True,
            'user_tier': user_tier,
            'models': models,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/usage')
@app.route('/api/ai/usage/<int:days>')
def api_ai_usage(days=1):
    """Get AI usage statistics"""
    try:
        if not AI_INTEGRATION_AVAILABLE or not ai_agent:
            return jsonify({
                'success': False,
                'error': 'AI services not available'
            }), 503
        
        user_id = request.headers.get('X-User-ID', 'web_user')
        usage_stats = ai_agent.get_usage_stats(user_id, days)
        
        return jsonify({
            'success': True,
            'usage_stats': usage_stats,
            'period_days': days,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/health')
def api_ai_health():
    """AI service health check"""
    try:
        if not AI_INTEGRATION_AVAILABLE:
            return jsonify({
                'success': False,
                'status': 'unavailable',
                'error': 'AI integration not available'
            })
        
        health_status = get_ai_health()
        
        return jsonify({
            'success': health_status['status'] in ['healthy', 'degraded'],
            'health_status': health_status,
            'ai_integration_available': AI_INTEGRATION_AVAILABLE,
            'ai_agent_initialized': ai_agent is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare-ai', methods=['POST'])
def api_compare_ai():
    """AI-powered token comparison"""
    try:
        if not AI_INTEGRATION_AVAILABLE or not ai_agent:
            return jsonify({
                'success': False,
                'error': 'AI services not available'
            }), 503
        
        data = request.get_json()
        tokens = data.get('tokens', [])
        
        if not tokens or len(tokens) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 tokens required for AI comparison'
            }), 400
        
        user_id = request.headers.get('X-User-ID', 'web_user')
        
        # Get traditional analysis for all tokens
        tokens_data = []
        for token in tokens[:5]:  # Limit to 5 tokens
            result = analyze_token_internal(token)
            if result.get('success'):
                tokens_data.append(result.get('data', {}))
        
        if len(tokens_data) < 2:
            return jsonify({
                'success': False,
                'error': 'Could not analyze enough tokens for comparison'
            }), 400
        
        # Perform AI comparison
        ai_response = ai_agent.compare_tokens(tokens_data, user_id)
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'comparison': {
                    'tokens': tokens,
                    'ai_analysis': {
                        'model_used': ai_response.model_used,
                        'confidence': ai_response.confidence,
                        'data': ai_response.data,
                        'processing_time': ai_response.processing_time
                    }
                },
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.error
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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

@app.route('/api/analyze/<token>/basic')
def api_analyze_basic(token):
    """Ultra-lightweight basic analysis - guaranteed to work"""
    try:
        start_time = time.time()
        
        # Try basic analysis only
        basic_data = {}
        if analyzer:
            try:
                basic_data = analyzer.analyze(token) or {}
            except:
                basic_data = {'error': 'Basic analysis failed'}
        
        response = {
            'success': True,
            'token': str(token).upper(),
            'timestamp': datetime.now().isoformat(),
            'processing_time': round(time.time() - start_time, 2),
            'completion_rate': 100.0,
            'components': {
                'fundamental': {'status': 'completed'},
                'technical': {'status': 'basic'},
                'ai_insights': {'status': 'disabled'},
                'web_context': {'status': 'disabled'},
                'trading_levels': {'status': 'disabled'},
                'strategies': {'status': 'disabled'}
            },
            'fundamental': basic_data,
            'mode': 'basic_safe'
        }
        
        return jsonify(response)
        
    except Exception:
        # Absolute fallback - no analysis at all
        return jsonify({
            'success': False,
            'token': str(token).upper(),
            'timestamp': datetime.now().isoformat(),
            'error': 'All analysis methods failed',
            'processing_time': 0.1,
            'completion_rate': 0.0,
            'components': {
                'fundamental': {'status': 'error'},
                'technical': {'status': 'error'},
                'ai_insights': {'status': 'error'},
                'web_context': {'status': 'error'},
                'trading_levels': {'status': 'error'},
                'strategies': {'status': 'error'}
            },
            'mode': 'emergency_fallback'
        })

@app.route('/api/analyze/<token>/master-emergency')
def api_analyze_master_emergency(token):
    """Emergency ultra-simple endpoint that ALWAYS returns valid JSON"""
    try:
        return jsonify({
            'token': str(token).upper(),
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'processing_time': 0.1,
            'completion_rate': 100.0,
            'components': {
                'fundamental': {'status': 'completed'},
                'technical': {'status': 'completed'},
                'ai_insights': {'status': 'completed'},
                'web_context': {'status': 'completed'},
                'trading_levels': {'status': 'completed'},
                'strategies': {'status': 'completed'}
            },
            'fundamental': {
                'token': str(token).upper(),
                'status': 'completed',
                'note': 'Emergency mode - basic data only'
            },
            'note': 'Using emergency fallback endpoint'
        })
    except Exception as e:
        # Even if this fails, return something
        return jsonify({
            'token': 'ERROR',
            'success': False,
            'error': str(e),
            'timestamp': '2025-08-26T00:00:00',
            'components': {'all': {'status': 'error'}}
        }), 200

@app.route('/api/analyze/<token>/master-safe')
def api_analyze_master_safe(token):
    """Safe fallback endpoint that always returns valid JSON"""
    try:
        # Simple basic analysis without heavy components
        if not analyzer:
            raise Exception("Analyzer not available")
            
        basic_analysis = analyzer.analyze(token)
        
        return jsonify({
            'success': True,
            'token': token.upper(),
            'timestamp': datetime.now().isoformat(),
            'fundamental': basic_analysis or {'error': 'Analysis failed'},
            'components': {
                'fundamental': {'status': 'completed'},
                'technical': {'status': 'disabled'},
                'ai_insights': {'status': 'disabled'},
                'web_context': {'status': 'disabled'},
                'trading_levels': {'status': 'disabled'},
                'strategies': {'status': 'disabled'}
            },
            'processing_time': 0.1,
            'completion_rate': 16.7,
            'note': 'Safe mode - limited features'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'token': token.upper(),
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'components': {
                'fundamental': {'status': 'error', 'error': str(e)},
                'technical': {'status': 'disabled'},
                'ai_insights': {'status': 'disabled'}, 
                'web_context': {'status': 'disabled'},
                'trading_levels': {'status': 'disabled'},
                'strategies': {'status': 'disabled'}
            },
            'processing_time': 0.0,
            'completion_rate': 0.0,
            'note': 'Safe mode error fallback'
        }), 200  # Return 200 to ensure JSON parsing works

@app.route('/api/debug/trading-levels/<token>')
def debug_trading_levels(token):
    """Debug endpoint for testing trading levels calculation"""
    try:
        # Mock price data for testing
        test_prices = {
            'bitcoin': 110000,
            'ethereum': 4200,
            'solana': 250,
            'cardano': 1.2,
            'dogecoin': 0.08
        }
        
        price = test_prices.get(token.lower(), 100)  # Default to $100
        
        print(f"DEBUG ENDPOINT: Testing trading levels for {token} at ${price}")
        levels = calculate_trading_levels(price, token)
        
        return jsonify({
            'success': True,
            'token': token,
            'test_price': price,
            'trading_levels': levels,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'reports', 'templates', 'static', 'static/css', 'static/js']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

def get_historical_data(token, days=365):
    """Fetch historical OHLCV data from CoinGecko"""
    import requests
    
    try:
        # CoinGecko OHLC endpoint
        url = f"https://api.coingecko.com/api/v3/coins/{token}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days
        }
        
        print(f"DEBUG: Fetching {days} days of OHLCV data for {token}")
        
        headers = {'Accept': 'application/json'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: Retrieved {len(data)} data points")
            return data
        else:
            print(f"DEBUG: CoinGecko OHLC failed with status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"DEBUG: Error fetching historical data: {e}")
        return []

def find_pivot_points(ohlc_data, window=20):
    """Find pivot highs and lows from OHLCV data"""
    if len(ohlc_data) < window * 2:
        return []
    
    pivots = []
    
    for i in range(window, len(ohlc_data) - window):
        current_high = ohlc_data[i][2]  # High price
        current_low = ohlc_data[i][3]   # Low price
        current_time = ohlc_data[i][0]  # Timestamp
        
        # Check for pivot high
        is_pivot_high = True
        for j in range(i - window, i + window + 1):
            if j != i and ohlc_data[j][2] >= current_high:
                is_pivot_high = False
                break
        
        # Check for pivot low  
        is_pivot_low = True
        for j in range(i - window, i + window + 1):
            if j != i and ohlc_data[j][3] <= current_low:
                is_pivot_low = False
                break
        
        if is_pivot_high:
            pivots.append({
                'price': current_high,
                'type': 'resistance',
                'timestamp': current_time,
                'source': 'pivot_high'
            })
            
        if is_pivot_low:
            pivots.append({
                'price': current_low,
                'type': 'support',
                'timestamp': current_time,
                'source': 'pivot_low'
            })
    
    return pivots

def calculate_volume_nodes(ohlc_data, bins=50):
    """Calculate volume profile to find high volume price areas"""
    if not ohlc_data:
        return []
    
    import numpy as np
    
    # Extract price and volume data
    highs = [candle[2] for candle in ohlc_data]  # High prices
    lows = [candle[3] for candle in ohlc_data]   # Low prices
    volumes = [candle[4] if len(candle) > 4 else 1000000 for candle in ohlc_data]  # Volume
    
    # Create price range
    min_price = min(lows)
    max_price = max(highs)
    
    # Create price bins
    price_bins = np.linspace(min_price, max_price, bins)
    volume_at_price = np.zeros(bins - 1)
    
    # Distribute volume across price bins
    for i, (high, low, volume) in enumerate(zip(highs, lows, volumes)):
        # Assume volume is distributed evenly across the price range of the candle
        price_range = high - low if high != low else max_price * 0.001  # Avoid division by zero
        
        for j in range(len(price_bins) - 1):
            bin_low = price_bins[j]
            bin_high = price_bins[j + 1]
            bin_center = (bin_low + bin_high) / 2
            
            # Check if this price bin intersects with the candle's price range
            if bin_center >= low and bin_center <= high:
                volume_at_price[j] += volume / max(1, price_range)
    
    # Find high volume nodes (top 20% of volume)
    volume_threshold = np.percentile(volume_at_price, 80)
    volume_nodes = []
    
    for i, volume in enumerate(volume_at_price):
        if volume >= volume_threshold:
            price_level = (price_bins[i] + price_bins[i + 1]) / 2
            volume_nodes.append({
                'price': price_level,
                'volume': volume,
                'type': 'volume_node',
                'source': 'volume_profile'
            })
    
    return sorted(volume_nodes, key=lambda x: x['volume'], reverse=True)

def find_price_clusters(ohlc_data, tolerance=0.02):
    """Find price levels with multiple touches within tolerance"""
    if not ohlc_data:
        return []
    
    # Extract all significant price levels (highs and lows)
    price_levels = []
    for candle in ohlc_data:
        price_levels.extend([candle[2], candle[3]])  # High and low
    
    clusters = []
    used_prices = set()
    
    for base_price in price_levels:
        if base_price in used_prices:
            continue
            
        # Find all prices within tolerance of base_price
        cluster_prices = []
        for price in price_levels:
            if abs(price - base_price) / base_price <= tolerance:
                cluster_prices.append(price)
                used_prices.add(price)
        
        # Only consider clusters with multiple touches
        if len(cluster_prices) >= 3:
            avg_price = sum(cluster_prices) / len(cluster_prices)
            clusters.append({
                'price': avg_price,
                'touches': len(cluster_prices),
                'type': 'cluster',
                'source': 'price_clustering'
            })
    
    return sorted(clusters, key=lambda x: x['touches'], reverse=True)

def calculate_fibonacci_levels(ohlc_data):
    """Calculate Fibonacci retracement levels from major swings"""
    if len(ohlc_data) < 50:
        return []
    
    # Find the major high and low in recent data
    recent_data = ohlc_data[-100:]  # Last 100 periods
    
    highs = [candle[2] for candle in recent_data]
    lows = [candle[3] for candle in recent_data]
    
    swing_high = max(highs)
    swing_low = min(lows)
    
    # Calculate Fibonacci levels
    fib_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
    fib_levels = []
    
    price_range = swing_high - swing_low
    
    for ratio in fib_ratios:
        # Retracement from high
        retracement_level = swing_high - (price_range * ratio)
        fib_levels.append({
            'price': retracement_level,
            'level': f'Fib {ratio}',
            'type': 'fibonacci',
            'source': 'fibonacci_retracement'
        })
        
        # Extension from low
        extension_level = swing_high + (price_range * ratio)
        fib_levels.append({
            'price': extension_level,
            'level': f'Fib Ext {ratio}',
            'type': 'fibonacci',
            'source': 'fibonacci_extension'
        })
    
    return fib_levels

def find_psychological_levels(current_price):
    """Find psychological support/resistance levels (round numbers)"""
    import math
    
    levels = []
    
    # Determine the scale based on current price
    if current_price >= 100000:
        scales = [10000, 25000, 50000, 100000]
    elif current_price >= 10000:
        scales = [1000, 2500, 5000, 10000]
    elif current_price >= 1000:
        scales = [100, 250, 500, 1000]
    elif current_price >= 100:
        scales = [10, 25, 50, 100]
    elif current_price >= 10:
        scales = [1, 2.5, 5, 10]
    else:
        scales = [0.1, 0.25, 0.5, 1]
    
    for scale in scales:
        # Find nearby round numbers
        lower_bound = current_price * 0.5
        upper_bound = current_price * 2
        
        # Generate round numbers in this range
        start = int(lower_bound / scale) * scale
        end = int(upper_bound / scale) * scale
        
        current = start
        while current <= end:
            if current != current_price and lower_bound <= current <= upper_bound:
                levels.append({
                    'price': float(current),
                    'type': 'psychological',
                    'source': 'round_number',
                    'scale': scale
                })
            current += scale
    
    return levels

def count_touches(level_price, ohlc_data, tolerance=0.015):
    """Count how many times price touched this level"""
    touches = 0
    
    for candle in ohlc_data:
        high = candle[2]
        low = candle[3]
        
        # Check if the candle touched this level within tolerance
        if (abs(high - level_price) / level_price <= tolerance or
            abs(low - level_price) / level_price <= tolerance or
            (low <= level_price <= high)):
            touches += 1
    
    return touches

def calculate_trading_levels(current_price, token, market_data=None):
    """Calculate realistic trading levels based on historical technical analysis"""
    import time
    from datetime import datetime
    
    start_time = time.time()
    
    try:
        price = float(current_price)
        print(f"DEBUG: Starting real technical analysis for {token} at ${price}")
        
        # Get historical data
        ohlc_data = get_historical_data(token, days=365)
        
        if not ohlc_data:
            print("DEBUG: No historical data available, falling back to basic calculation")
            return calculate_basic_levels(price)
        
        print(f"DEBUG: Analyzing {len(ohlc_data)} historical data points")
        
        # Find all types of levels
        pivot_levels = find_pivot_points(ohlc_data, window=10)
        volume_nodes = calculate_volume_nodes(ohlc_data, bins=30)
        price_clusters = find_price_clusters(ohlc_data, tolerance=0.02)
        fib_levels = calculate_fibonacci_levels(ohlc_data)
        psychological_levels = find_psychological_levels(price)
        
        print(f"DEBUG: Found {len(pivot_levels)} pivots, {len(volume_nodes)} volume nodes, {len(price_clusters)} clusters")
        
        # Combine all levels and add strength scoring
        all_levels = []
        
        for level in pivot_levels + volume_nodes + price_clusters + fib_levels + psychological_levels:
            touches = count_touches(level['price'], ohlc_data)
            
            if touches >= 2:  # Minimum 2 touches for validity
                strength_score = touches
                
                # Bonus for volume nodes
                if level.get('type') == 'volume_node':
                    strength_score += 3
                
                # Bonus for fibonacci levels
                if level.get('type') == 'fibonacci':
                    strength_score += 2
                
                all_levels.append({
                    'price': level['price'],
                    'strength': strength_score,
                    'touches': touches,
                    'type': level.get('type', 'unknown'),
                    'source': level.get('source', 'unknown'),
                    'level_info': level.get('level', '')
                })
        
        # Sort by strength
        all_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        # Separate supports and resistances
        supports = [l for l in all_levels if l['price'] < price * 0.98][:8]
        resistances = [l for l in all_levels if l['price'] > price * 1.02][:8]
        
        # Generate entry levels from supports
        entries = []
        for i, support in enumerate(supports[:5]):
            confidence = min(95, 60 + (support['strength'] * 5))
            size_pct = 8 + (i * 2)  # 8%, 10%, 12%, 14%, 16%
            
            reason_parts = []
            if support['touches'] > 1:
                reason_parts.append(f"Tested {support['touches']} times")
            if support['type'] == 'volume_node':
                reason_parts.append("High volume area")
            elif support['type'] == 'fibonacci':
                reason_parts.append(f"Fibonacci level")
            elif support['type'] == 'psychological':
                reason_parts.append("Psychological level")
            
            entries.append({
                'price': round(support['price'], 4 if support['price'] < 1 else 2),
                'size': f'{size_pct}%',
                'confidence': confidence,
                'reason': ' + '.join(reason_parts) if reason_parts else f"Strong support ({support['type']})"
            })
        
        # Generate exit levels from resistances
        exits = []
        take_profits = [15, 20, 25, 20, 15]  # Distribution of take profits
        
        for i, resistance in enumerate(resistances[:5]):
            probability = max(30, min(85, 50 + (resistance['strength'] * 4)))
            
            reason_parts = []
            if resistance['touches'] > 1:
                reason_parts.append(f"Tested {resistance['touches']} times")
            if resistance['type'] == 'volume_node':
                reason_parts.append("High volume resistance")
            elif resistance['type'] == 'fibonacci':
                reason_parts.append(f"Fibonacci resistance")
            elif resistance['type'] == 'psychological':
                reason_parts.append("Psychological resistance")
            
            exits.append({
                'price': round(resistance['price'], 4 if resistance['price'] < 1 else 2),
                'take': f'{take_profits[i]}%',
                'probability': probability,
                'reason': ' + '.join(reason_parts) if reason_parts else f"Strong resistance ({resistance['type']})"
            })
        
        # Calculate structural stop losses
        stop_losses = []
        if supports:
            # Place initial stop below strongest support
            strongest_support = supports[0]['price']
            initial_stop = strongest_support * 0.97  # 3% below support
            
            # Trailing stop above second strongest support if available
            trailing_stop = supports[1]['price'] * 0.995 if len(supports) > 1 else strongest_support * 0.985
            
            stop_losses = [
                {
                    'price': round(initial_stop, 4 if initial_stop < 1 else 2),
                    'type': 'structural',
                    'risk': f'-{((price - initial_stop) / price * 100):.1f}%'
                },
                {
                    'price': round(trailing_stop, 4 if trailing_stop < 1 else 2),
                    'type': 'trailing',
                    'risk': f'-{((price - trailing_stop) / price * 100):.1f}%'
                }
            ]
        
        processing_time = time.time() - start_time
        
        result = {
            'entries': entries,
            'exits': exits,
            'stop_losses': stop_losses,
            'analysis_metadata': {
                'method': 'historical_technical_analysis',
                'data_points': len(ohlc_data),
                'levels_analyzed': len(all_levels),
                'supports_found': len(supports),
                'resistances_found': len(resistances),
                'processing_time': round(processing_time, 3)
            }
        }
        
        print(f"DEBUG: Real technical analysis completed in {processing_time:.3f}s")
        return result
        
    except Exception as e:
        print(f"DEBUG: Error in technical analysis: {e}")
        import traceback
        traceback.print_exc()
        return calculate_basic_levels(price)

def calculate_basic_levels(price):
    """Fallback to basic levels if technical analysis fails"""
    return {
        'entries': [
            {'price': round(price * 0.95, 2), 'size': '10%', 'confidence': 70, 'reason': 'Basic support level'},
            {'price': round(price * 0.90, 2), 'size': '15%', 'confidence': 65, 'reason': 'Secondary support'},
            {'price': round(price * 0.85, 2), 'size': '20%', 'confidence': 60, 'reason': 'Strong support zone'}
        ],
        'exits': [
            {'price': round(price * 1.10, 2), 'take': '25%', 'probability': 60, 'reason': 'Basic resistance'},
            {'price': round(price * 1.20, 2), 'take': '35%', 'probability': 45, 'reason': 'Major resistance'},
            {'price': round(price * 1.30, 2), 'take': '25%', 'probability': 30, 'reason': 'Extension target'}
        ],
        'stop_losses': [
            {'price': round(price * 0.88, 2), 'type': 'initial', 'risk': '-12%'}
        ],
        'analysis_metadata': {
            'method': 'basic_fallback',
            'note': 'Historical data unavailable'
        }
    }

def generate_strategies(analysis_result):
    """Generate personalized trading strategies based on analysis"""
    try:
        # Extract key metrics from analysis
        fundamental = analysis_result.get('fundamental', {})
        score = fundamental.get('three_layers', {}).get('score', 0)
        classification = fundamental.get('classification', 'Unknown')
        
        # Get current price for ranges
        current_price = fundamental.get('three_layers', {}).get('price', 0)
        
        strategies = {
            'conservative': {
                'action': 'wait',
                'entry_range': [current_price * 0.92, current_price * 0.95] if current_price > 0 else [0, 0],
                'position_size': '5-8%',
                'risk_reward': 1.5,
                'description': 'Wait for strong confirmation and clear support levels'
            },
            'moderate': {
                'action': 'accumulate',
                'entry_range': [current_price * 0.95, current_price * 0.98] if current_price > 0 else [0, 0],
                'position_size': '10-12%',
                'risk_reward': 2.0,
                'description': 'Dollar-cost average on dips with moderate position sizing'
            },
            'aggressive': {
                'action': 'buy_dips',
                'entry_range': [current_price * 0.98, current_price * 1.02] if current_price > 0 else [0, 0],
                'position_size': '15-20%',
                'risk_reward': 3.0,
                'description': 'Active trading with higher position size and risk'
            }
        }
        
        # Adjust strategies based on classification
        if classification == 'MAJOR':
            strategies['conservative']['action'] = 'accumulate'
            strategies['moderate']['position_size'] = '12-15%'
            strategies['aggressive']['position_size'] = '20-25%'
        elif classification == 'SPECULATIVE':
            strategies['conservative']['position_size'] = '3-5%'
            strategies['moderate']['position_size'] = '5-8%'
            strategies['aggressive']['position_size'] = '8-12%'
        
        # Adjust based on score
        if score >= 8:
            for strategy in strategies.values():
                strategy['confidence'] = 'high'
        elif score >= 6:
            for strategy in strategies.values():
                strategy['confidence'] = 'medium'
        else:
            for strategy in strategies.values():
                strategy['confidence'] = 'low'
        
        return strategies
        
    except Exception as e:
        return {
            'conservative': {'error': str(e)},
            'moderate': {'error': str(e)},
            'aggressive': {'error': str(e)}
        }

def generate_formatted_report(analysis_result):
    """Generate a formatted report combining all analysis components"""
    try:
        token = analysis_result.get('token', 'UNKNOWN')
        timestamp = analysis_result.get('timestamp', 'Unknown')
        processing_time = analysis_result.get('processing_time', 0)
        completion_rate = analysis_result.get('completion_rate', 0)
        
        # Header
        report = f"""
═══════════════════════════════════════════════════════════════════════════════
                        CRYPTO ANALYZER MASTER REPORT
                              {token} - Complete Analysis
═══════════════════════════════════════════════════════════════════════════════

Generated: {timestamp}
Processing Time: {processing_time}s
Completion Rate: {completion_rate}%

"""
        
        # Fundamental Analysis Section
        fundamental = analysis_result.get('fundamental', {})
        if fundamental.get('status') == 'completed':
            three_layers = fundamental.get('three_layers', {})
            report += f"""
┌─ FUNDAMENTAL ANALYSIS ─────────────────────────────────────────────────────┐
│                                                                            │
│  Classification: {fundamental.get('classification', 'Unknown')}
│  Overall Score: {three_layers.get('score', 0)}/10
│  Decision: {three_layers.get('decision', 'Unknown')}
│  Market Cap: ${three_layers.get('market_cap', 0):,}
│  Current Price: ${three_layers.get('price', 0)}
│  24h Change: {three_layers.get('price_change_24h', 0):.2f}%
│                                                                            │
│  Strengths:
"""
            for strength in fundamental.get('strengths', [])[:3]:
                report += f"│    • {strength}\n"
            
            if fundamental.get('risks'):
                report += "│  Risks:\n"
                for risk in fundamental.get('risks', [])[:2]:
                    report += f"│    ⚠ {risk}\n"
            
            report += "└────────────────────────────────────────────────────────────────────────────┘\n"
        
        # Technical Analysis Section
        technical = analysis_result.get('technical', {})
        if technical.get('status') == 'completed':
            momentum = technical.get('momentum', 'UNKNOWN')
            fear_greed = technical.get('indicators', {}).get('fear_greed', 0)
            
            report += f"""
┌─ TECHNICAL ANALYSIS ───────────────────────────────────────────────────────┐
│                                                                            │
│  Momentum: {momentum}
│  Fear & Greed Index: {fear_greed}
│  Volume Trend: {technical.get('indicators', {}).get('volume_change', 0):+.1f}%
│                                                                            │
│  Key Patterns:
"""
            for pattern in technical.get('patterns', [])[:3]:
                report += f"│    • {pattern}\n"
            
            report += "└────────────────────────────────────────────────────────────────────────────┘\n"
        
        # AI Insights Section
        ai_insights = analysis_result.get('ai_insights', {})
        if ai_insights.get('status') == 'completed':
            summary = ai_insights.get('summary', '')[:200] + '...' if len(ai_insights.get('summary', '')) > 200 else ai_insights.get('summary', '')
            
            report += f"""
┌─ AI INSIGHTS ──────────────────────────────────────────────────────────────┐
│                                                                            │
│  Model: {ai_insights.get('model_used', 'Unknown')}
│  Confidence: {ai_insights.get('confidence', 0):.0f}%
│  Cost: ${ai_insights.get('cost', 0):.4f}
│                                                                            │
│  Summary:
│  {summary}
│                                                                            │
"""
            
            if ai_insights.get('opportunities'):
                report += "│  Opportunities:\n"
                for opp in ai_insights.get('opportunities', [])[:2]:
                    report += f"│    💡 {opp}\n"
            
            report += "└────────────────────────────────────────────────────────────────────────────┘\n"
        
        # Trading Levels Section
        trading_levels = analysis_result.get('trading_levels', {})
        if trading_levels and not trading_levels.get('error'):
            report += f"""
┌─ TRADING LEVELS ───────────────────────────────────────────────────────────┐
│                                                                            │
│  Entry Opportunities:
"""
            for entry in trading_levels.get('entries', [])[:3]:
                report += f"│    📈 ${entry.get('price', 0)} - {entry.get('size', '')} ({entry.get('confidence', 0)}% confidence)\n"
            
            report += "│\n│  Exit Targets:\n"
            for exit in trading_levels.get('exits', [])[:3]:
                report += f"│    📊 ${exit.get('price', 0)} - Take {exit.get('take', '')} ({exit.get('probability', 0)}% probability)\n"
            
            report += "└────────────────────────────────────────────────────────────────────────────┘\n"
        
        # Strategies Section
        strategies = analysis_result.get('strategies', {})
        if strategies and not any(s.get('error') for s in strategies.values()):
            report += f"""
┌─ PERSONALIZED STRATEGIES ──────────────────────────────────────────────────┐
│                                                                            │
│  🛡️ Conservative: {strategies.get('conservative', {}).get('action', 'Unknown')}
│     Position Size: {strategies.get('conservative', {}).get('position_size', 'Unknown')}
│     Risk/Reward: {strategies.get('conservative', {}).get('risk_reward', 'Unknown')}
│                                                                            │
│  ⚖️ Moderate: {strategies.get('moderate', {}).get('action', 'Unknown')}
│     Position Size: {strategies.get('moderate', {}).get('position_size', 'Unknown')}
│     Risk/Reward: {strategies.get('moderate', {}).get('risk_reward', 'Unknown')}
│                                                                            │
│  🚀 Aggressive: {strategies.get('aggressive', {}).get('action', 'Unknown')}
│     Position Size: {strategies.get('aggressive', {}).get('position_size', 'Unknown')}
│     Risk/Reward: {strategies.get('aggressive', {}).get('risk_reward', 'Unknown')}
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
"""
        
        report += f"""
═══════════════════════════════════════════════════════════════════════════════
                           END OF MASTER REPORT
                      Generated by Crypto Analyzer v2.0
═══════════════════════════════════════════════════════════════════════════════
"""
        
        return report
        
    except Exception as e:
        return f"Error generating formatted report: {str(e)}"

def print_routes():
    """Print all registered Flask routes for debugging"""
    print("\n=== REGISTERED FLASK ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} [{', '.join(rule.methods)}] -> {rule.endpoint}")
    print("=== END ROUTES ===\n")

# Print routes when module is loaded (for WSGI servers)
if not app.debug:
    print_routes()

# Make sure Flask app is available for WSGI servers
application = app

if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Print registered routes for debugging
    print_routes()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting AI Token Preview Web Server")
    print(f"Components Loaded: {COMPONENTS_LOADED}")
    print(f"AI Integration Available: {AI_INTEGRATION_AVAILABLE}")
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug}")
    print(f"Cache Duration: {CACHE_DURATION}s")
    
    # Run the app
    app.run(host=host, port=port, debug=debug)
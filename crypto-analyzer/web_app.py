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
    # Import configuration constants directly (no Config class needed)
    import config
    # AI Integration imports
    from ai_openrouter_agent import create_ai_agent, get_ai_health
    from ai_config import AIConfig, AITier
    from prompts.crypto_analysis_prompts import AnalysisType
    AI_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    print("Some features may not be available")
    AI_INTEGRATION_AVAILABLE = False

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

# Initialize components (with error handling)
try:
    # Initialize components directly (they create their own configurations)
    fetcher = DataFetcher()
    social_analyzer = SocialAnalyzer()
    
    # Initialize analyzer with AI support
    enable_ai = os.environ.get('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
    user_tier = os.environ.get('AI_TIER', 'budget')
    analyzer = CryptoAnalyzer(enable_ai=enable_ai and AI_INTEGRATION_AVAILABLE, user_tier=user_tier)
    
    display_manager = DisplayManager()
    
    # Initialize AI agent separately for web endpoints
    ai_agent = None
    if AI_INTEGRATION_AVAILABLE and enable_ai:
        try:
            ai_agent = create_ai_agent(user_tier)
        except Exception as e:
            print(f"Warning: Could not initialize AI agent: {e}")
            ai_agent = None
    
    COMPONENTS_LOADED = True
except Exception as e:
    print(f"Warning: Could not initialize analysis components: {e}")
    COMPONENTS_LOADED = False
    fetcher = None
    social_analyzer = None
    analyzer = None
    display_manager = None
    ai_agent = None

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
        result = analyzer.analyze(token_name)
        
        if result and result.get('success', False):
            # Cache the successful result
            cache_result(token_name, result)
            return result
        else:
            return {
                'success': False,
                'error': result.get('error', 'Analysis failed') if result else 'No data received'
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
    
    print(f"🚀 Starting AI Token Preview Web Server")
    print(f"📊 Components Loaded: {COMPONENTS_LOADED}")
    print(f"🤖 AI Integration Available: {AI_INTEGRATION_AVAILABLE}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📁 Cache Duration: {CACHE_DURATION}s")
    
    # Run the app
    app.run(host=host, port=port, debug=debug)
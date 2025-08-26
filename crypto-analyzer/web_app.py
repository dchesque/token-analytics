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
    from fetcher import CryptoFetcher
    from social_analyzer import SocialAnalyzer
    from config import Config
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    print("Some features may not be available")

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)

# Global cache for results
cache = {}
cache_lock = threading.Lock()
CACHE_DURATION = int(os.environ.get('CACHE_DURATION', 300))  # 5 minutes

# Initialize components (with error handling)
try:
    config = Config()
    fetcher = CryptoFetcher(config)
    social_analyzer = SocialAnalyzer(config)
    analyzer = CryptoAnalyzer(config, fetcher, social_analyzer)
    display_manager = DisplayManager()
    COMPONENTS_LOADED = True
except Exception as e:
    print(f"Warning: Could not initialize analysis components: {e}")
    COMPONENTS_LOADED = False
    config = None
    analyzer = None
    display_manager = None

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
        'timestamp': datetime.now().isoformat()
    })

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

if __name__ == '__main__':
    # Create necessary directories
    create_directories()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting AI Token Preview Web Server")
    print(f"📊 Components Loaded: {COMPONENTS_LOADED}")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug Mode: {debug}")
    print(f"📁 Cache Duration: {CACHE_DURATION}s")
    
    # Run the app
    app.run(host=host, port=port, debug=debug)
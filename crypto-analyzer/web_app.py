#!/usr/bin/env python3
"""
AI Token Preview Web Application
Flask-based web interface for AI Token Preview v2.0
Supports both API and Web UI modes
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

from analyzer import CryptoAnalyzer
from display_manager import DisplayManager
from fetcher import CryptoFetcher
from social_analyzer import SocialAnalyzer
from config import Config

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
CACHE_DURATION = 300  # 5 minutes

# Initialize components
config = Config()
fetcher = CryptoFetcher(config)
social_analyzer = SocialAnalyzer(config)
analyzer = CryptoAnalyzer(config, fetcher, social_analyzer)
display_manager = DisplayManager()

def get_cached_result(token):
    """Get cached result if available and not expired"""
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
        api_statuses = fetcher.check_api_status()
        return jsonify({
            'success': True,
            'status': 'healthy',
            'apis': api_statuses,
            'cache_size': len(cache),
            'version': '2.0',
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
    
    # Get port from environment or default
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)
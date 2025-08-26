#!/usr/bin/env python3
"""
Health Check Script for AI Token Preview
Used by Docker and EasyPanel to monitor application health
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def check_imports():
    """Check if all required modules can be imported"""
    try:
        import requests
        import rich
        import colorama
        from dotenv import load_dotenv
        return True, "All core modules importable"
    except ImportError as e:
        return False, f"Import error: {str(e)}"

def check_flask():
    """Check if Flask and web components are available"""
    try:
        import flask
        from flask_cors import CORS
        return True, "Flask components available"
    except ImportError as e:
        return False, f"Flask import error: {str(e)}"

def check_app_modules():
    """Check if application modules can be imported"""
    try:
        from analyzer import CryptoAnalyzer
        from display_manager import DisplayManager
        from fetcher import CryptoFetcher
        from social_analyzer import SocialAnalyzer
        from config import Config
        return True, "All app modules importable"
    except ImportError as e:
        return False, f"App module error: {str(e)}"

def check_directories():
    """Check if required directories exist"""
    required_dirs = ['data', 'reports', 'templates', 'static', 'src']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        # Try to create missing directories
        for dir_name in missing_dirs:
            try:
                Path(dir_name).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create directory {dir_name}: {str(e)}"
        return True, f"Created missing directories: {', '.join(missing_dirs)}"
    
    return True, "All directories present"

def check_web_server():
    """Check if web server can be reached"""
    import requests
    
    port = os.environ.get('PORT', 8000)
    
    try:
        response = requests.get(f'http://localhost:{port}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                return True, "Web server responding"
            else:
                return False, f"Web server unhealthy: {data}"
        else:
            return False, f"Web server returned status {response.status_code}"
    except requests.ConnectionError:
        # Server might not be running in health check mode
        return None, "Web server not running (may be normal)"
    except Exception as e:
        return False, f"Web server check failed: {str(e)}"

def check_api_connectivity():
    """Check if external APIs are reachable"""
    import requests
    
    apis = {
        'CoinGecko': 'https://api.coingecko.com/api/v3/ping',
        'Alternative.me': 'https://api.alternative.me/fng/',
        'DeFiLlama': 'https://api.llama.fi/protocols'
    }
    
    results = {}
    for name, url in apis.items():
        try:
            response = requests.get(url, timeout=5)
            results[name] = response.status_code == 200
        except:
            results[name] = False
    
    if all(results.values()):
        return True, f"All APIs reachable: {list(results.keys())}"
    elif any(results.values()):
        working = [k for k, v in results.items() if v]
        failing = [k for k, v in results.items() if not v]
        return None, f"Partial API access. Working: {working}, Failing: {failing}"
    else:
        return False, "No external APIs reachable"

def check_environment():
    """Check environment variables"""
    web_mode = os.environ.get('WEB_MODE', 'false').lower() == 'true'
    port = os.environ.get('PORT', '8000')
    
    info = {
        'web_mode': web_mode,
        'port': port,
        'has_lunarcrush_key': bool(os.environ.get('LUNARCRUSH_API_KEY')),
        'has_messari_key': bool(os.environ.get('MESSARI_API_KEY')),
        'debug': os.environ.get('DEBUG', 'false').lower() == 'true',
        'production': os.environ.get('PRODUCTION', 'false').lower() == 'true'
    }
    
    return True, f"Environment configured: {info}"

def check_disk_space():
    """Check available disk space"""
    import shutil
    
    try:
        stat = shutil.disk_usage('/')
        free_gb = stat.free / (1024 ** 3)
        used_percent = (stat.used / stat.total) * 100
        
        if free_gb < 0.1:
            return False, f"Critical: Only {free_gb:.2f}GB free"
        elif free_gb < 0.5:
            return None, f"Warning: Only {free_gb:.2f}GB free ({used_percent:.1f}% used)"
        else:
            return True, f"Disk space OK: {free_gb:.1f}GB free ({used_percent:.1f}% used)"
    except Exception as e:
        return None, f"Could not check disk space: {str(e)}"

def run_health_checks():
    """Run all health checks and return results"""
    checks = [
        ("Import Check", check_imports),
        ("Flask Check", check_flask),
        ("App Modules", check_app_modules),
        ("Directories", check_directories),
        ("Environment", check_environment),
        ("Disk Space", check_disk_space),
        ("API Connectivity", check_api_connectivity),
        ("Web Server", check_web_server)
    ]
    
    results = []
    overall_status = "healthy"
    
    for name, check_func in checks:
        try:
            status, message = check_func()
            results.append({
                "check": name,
                "status": "pass" if status is True else "warn" if status is None else "fail",
                "message": message
            })
            
            if status is False:
                overall_status = "unhealthy"
            elif status is None and overall_status == "healthy":
                overall_status = "degraded"
        except Exception as e:
            results.append({
                "check": name,
                "status": "error",
                "message": f"Check failed: {str(e)}"
            })
            overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "pass"),
            "warned": sum(1 for r in results if r["status"] == "warn"),
            "failed": sum(1 for r in results if r["status"] == "fail"),
            "errors": sum(1 for r in results if r["status"] == "error")
        }
    }

def main():
    """Main health check function"""
    # Parse arguments
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    json_output = '--json' in sys.argv
    
    # Run health checks
    results = run_health_checks()
    
    # Output results
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        # Console output
        status_symbols = {
            "pass": "✓",
            "warn": "⚠",
            "fail": "✗",
            "error": "!"
        }
        
        status_colors = {
            "pass": "\033[92m",  # Green
            "warn": "\033[93m",  # Yellow
            "fail": "\033[91m",  # Red
            "error": "\033[91m",  # Red
        }
        reset_color = "\033[0m"
        
        print("\n" + "="*64)
        print("AI TOKEN PREVIEW HEALTH CHECK")
        print("="*64)
        
        for check in results["checks"]:
            symbol = status_symbols.get(check["status"], "?")
            color = status_colors.get(check["status"], "")
            
            if verbose or check["status"] != "pass":
                print(f"{color}{symbol}{reset_color} {check['check']}: {check['message']}")
        
        print("-"*60)
        summary = results["summary"]
        print(f"Summary: {summary['passed']}/{summary['total']} passed, "
              f"{summary['warned']} warnings, {summary['failed']} failed")
        
        print(f"\nOverall Status: {results['status'].upper()}")
        print("="*60 + "\n")
    
    # Exit with appropriate code
    if results["status"] == "healthy":
        sys.exit(0)
    elif results["status"] == "degraded":
        sys.exit(0)  # Still considered OK for Docker health check
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/bin/bash

# AI Token Preview Entrypoint Script
# Handles both CLI and Web modes with proper initialization

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
WEB_MODE="${WEB_MODE:-true}"
PORT="${PORT:-8000}"
DEBUG="${DEBUG:-false}"
WORKERS="${MAX_WORKERS:-4}"
TIMEOUT="${REQUEST_TIMEOUT:-30}"

# Print startup banner
print_banner() {
    echo -e "${BLUE}====================================${NC}"
    echo -e "${BLUE}   AI Token Preview v2.0 Docker    ${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo ""
    echo -e "Mode: ${GREEN}$([ "$WEB_MODE" = "true" ] && echo "WEB" || echo "CLI")${NC}"
    echo -e "Port: ${GREEN}${PORT}${NC}"
    echo -e "Debug: ${GREEN}${DEBUG}${NC}"
    echo -e "Workers: ${GREEN}${WORKERS}${NC}"
    echo ""
}

# Check environment
check_environment() {
    echo -e "${BLUE}Checking environment...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python3 not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2)"
    
    # Check required directories
    for dir in data reports templates static; do
        if [ ! -d "/app/$dir" ]; then
            echo -e "${YELLOW}Creating directory: $dir${NC}"
            mkdir -p "/app/$dir"
        fi
    done
    echo -e "${GREEN}✓${NC} Directories ready"
    
    # Set permissions
    chmod -R 755 /app/data /app/reports 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Permissions set"
}

# Check dependencies
check_dependencies() {
    echo -e "${BLUE}Checking dependencies...${NC}"
    
    # Test basic imports
    python3 -c "
import sys
import os
sys.path.append('/app/src')

# Test core modules
try:
    import requests
    import rich
    import colorama
    from dotenv import load_dotenv
    print('✓ Core dependencies OK')
except ImportError as e:
    print(f'✗ Core dependency error: {e}')
    sys.exit(1)

# Test Flask if web mode
if os.environ.get('WEB_MODE', 'false').lower() == 'true':
    try:
        import flask
        from flask_cors import CORS
        print('✓ Flask dependencies OK')
    except ImportError as e:
        print(f'✗ Flask dependency error: {e}')
        sys.exit(1)

# Test app modules
try:
    from config import Config
    print('✓ Application modules OK')
except ImportError as e:
    print(f'✗ App module error: {e}')
    sys.exit(1)
" || exit 1
}

# Initialize application data
initialize_app() {
    echo -e "${BLUE}Initializing application...${NC}"
    
    # Load environment if .env exists
    if [ -f "/app/.env" ]; then
        echo -e "${GREEN}✓${NC} Loading .env file"
        export $(cat /app/.env | grep -v '^#' | xargs) 2>/dev/null || true
    fi
    
    # Create default config if needed
    if [ ! -f "/app/data/config.json" ] && [ "$WEB_MODE" = "true" ]; then
        echo -e "${YELLOW}Creating default config...${NC}"
        cat > /app/data/config.json << EOF
{
  "version": "2.0.0",
  "created": "$(date -Iseconds)",
  "web_mode": true,
  "settings": {
    "cache_duration": ${CACHE_DURATION:-600},
    "max_workers": ${WORKERS},
    "timeout": ${TIMEOUT}
  }
}
EOF
    fi
    
    echo -e "${GREEN}✓${NC} Application initialized"
}

# Wait for dependencies (if any)
wait_for_deps() {
    echo -e "${BLUE}Checking external dependencies...${NC}"
    
    # Test internet connectivity
    if ! curl -s --max-time 10 https://api.coingecko.com/api/v3/ping > /dev/null; then
        echo -e "${YELLOW}⚠${NC} Limited internet connectivity - some features may not work"
    else
        echo -e "${GREEN}✓${NC} Internet connectivity OK"
    fi
}

# Start CLI mode
start_cli() {
    echo -e "${GREEN}Starting CLI mode...${NC}"
    echo ""
    
    # If arguments provided, run with them
    if [ $# -gt 1 ] && [ "$1" = "cli" ]; then
        shift  # Remove 'cli' argument
        exec python3 /app/src/main.py "$@"
    else
        # Interactive mode
        exec python3 /app/src/main.py
    fi
}

# Start web mode
start_web() {
    echo -e "${GREEN}Starting web mode...${NC}"
    echo ""
    
    # Choose the best way to run Flask
    if [ "$DEBUG" = "true" ]; then
        echo -e "${YELLOW}Running in DEBUG mode${NC}"
        exec python3 /app/web_app.py
    else
        # Production mode with gunicorn if available
        if command -v gunicorn &> /dev/null; then
            echo -e "${GREEN}Starting with Gunicorn (production mode)${NC}"
            exec gunicorn \
                --bind 0.0.0.0:${PORT} \
                --workers ${WORKERS} \
                --timeout ${TIMEOUT} \
                --access-logfile - \
                --error-logfile - \
                --log-level info \
                --preload \
                web_app:app
        else
            echo -e "${YELLOW}Gunicorn not available, using Flask dev server${NC}"
            exec python3 /app/web_app.py
        fi
    fi
}

# Handle shutdown signals
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    
    # Kill any background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT SIGQUIT

# Main execution
main() {
    print_banner
    check_environment
    check_dependencies
    initialize_app
    wait_for_deps
    
    # Determine mode and start
    case "${1:-auto}" in
        cli)
            start_cli "$@"
            ;;
        web)
            WEB_MODE=true start_web
            ;;
        test)
            echo -e "${BLUE}Running health check...${NC}"
            python3 /app/healthcheck.py --verbose
            exit $?
            ;;
        shell|bash)
            echo -e "${GREEN}Starting interactive shell...${NC}"
            exec /bin/bash
            ;;
        auto|*)
            # Auto-detect mode
            if [ "$WEB_MODE" = "true" ]; then
                start_web
            else
                start_cli "$@"
            fi
            ;;
    esac
}

# Change to app directory
cd /app

# Run main function with all arguments
main "$@"
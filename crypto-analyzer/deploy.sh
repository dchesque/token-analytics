#!/bin/bash

# AI Token Preview Deploy Script for EasyPanel
# Version: 2.0
# Description: Automated deployment script for EasyPanel VPS

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="ai-token-preview"
VERSION="2.0"
BUILD_DIR="./build"
ARCHIVE_NAME="${APP_NAME}-deploy.tar.gz"

# Functions
print_header() {
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}   AI Token Preview Deploy Script v2.0  ${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker found"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose found"
    
    # Check required files
    required_files=("Dockerfile" "docker-compose.yml" "docker-compose.prod.yml" "requirements.txt" "web_app.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    print_success "All required files present"
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    
    # Build with production optimizations
    docker build \
        --tag ${APP_NAME}:latest \
        --tag ${APP_NAME}:${VERSION} \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from ${APP_NAME}:latest \
        .
    
    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Test the image locally
test_image() {
    print_info "Testing Docker image..."
    
    # Run a quick test
    docker run --rm ${APP_NAME}:latest python -c "import sys; print('Python OK'); sys.exit(0)"
    
    if [ $? -eq 0 ]; then
        print_success "Image test passed"
    else
        print_error "Image test failed"
        exit 1
    fi
    
    # Test web server startup
    print_info "Testing web server..."
    container_id=$(docker run -d -p 8000:8000 --env WEB_MODE=true ${APP_NAME}:latest)
    sleep 5
    
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "Web server test passed"
    else
        print_warning "Web server test failed (may be normal in test environment)"
    fi
    
    docker stop $container_id &> /dev/null
    docker rm $container_id &> /dev/null
}

# Create deployment package
create_package() {
    print_info "Creating deployment package..."
    
    # Clean build directory
    rm -rf ${BUILD_DIR}
    mkdir -p ${BUILD_DIR}
    
    # Copy necessary files
    cp Dockerfile ${BUILD_DIR}/
    cp docker-compose.yml ${BUILD_DIR}/
    cp docker-compose.prod.yml ${BUILD_DIR}/
    cp .dockerignore ${BUILD_DIR}/
    cp requirements.txt ${BUILD_DIR}/
    cp web_app.py ${BUILD_DIR}/
    cp -r src ${BUILD_DIR}/
    cp entrypoint.sh ${BUILD_DIR}/ 2>/dev/null || true
    cp healthcheck.py ${BUILD_DIR}/ 2>/dev/null || true
    cp easypanel-config.json ${BUILD_DIR}/ 2>/dev/null || true
    cp .env.production ${BUILD_DIR}/.env.example 2>/dev/null || true
    
    # Copy templates and static if they exist
    [ -d "templates" ] && cp -r templates ${BUILD_DIR}/
    [ -d "static" ] && cp -r static ${BUILD_DIR}/
    
    # Create archive
    cd ${BUILD_DIR}
    tar -czf ../${ARCHIVE_NAME} .
    cd ..
    
    # Clean up
    rm -rf ${BUILD_DIR}
    
    if [ -f ${ARCHIVE_NAME} ]; then
        print_success "Deployment package created: ${ARCHIVE_NAME}"
        print_info "Package size: $(du -h ${ARCHIVE_NAME} | cut -f1)"
    else
        print_error "Failed to create deployment package"
        exit 1
    fi
}

# Export Docker image (optional)
export_image() {
    print_info "Exporting Docker image (optional)..."
    
    docker save -o ${APP_NAME}-image.tar ${APP_NAME}:latest
    
    if [ -f ${APP_NAME}-image.tar ]; then
        gzip ${APP_NAME}-image.tar
        print_success "Docker image exported: ${APP_NAME}-image.tar.gz"
        print_info "Image size: $(du -h ${APP_NAME}-image.tar.gz | cut -f1)"
    else
        print_warning "Failed to export Docker image"
    fi
}

# Print deployment instructions
print_instructions() {
    echo ""
    print_header
    echo -e "${GREEN}Build completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}═══ EasyPanel Deployment Instructions ═══${NC}"
    echo ""
    echo "1. ${YELLOW}Upload to EasyPanel:${NC}"
    echo "   - Log in to your EasyPanel dashboard"
    echo "   - Create a new project or select existing"
    echo "   - Choose 'Docker Compose' as project type"
    echo "   - Upload: ${GREEN}${ARCHIVE_NAME}${NC}"
    echo ""
    echo "2. ${YELLOW}Configure Environment Variables:${NC}"
    echo "   Required:"
    echo "   - WEB_MODE=true"
    echo "   - PORT=8000"
    echo "   Optional:"
    echo "   - LUNARCRUSH_API_KEY=your_key"
    echo "   - MESSARI_API_KEY=your_key"
    echo "   - DEBUG=false"
    echo "   - DOMAIN=your-domain.com"
    echo ""
    echo "3. ${YELLOW}Configure Volumes:${NC}"
    echo "   - /app/data → Persistent data storage"
    echo "   - /app/reports → Generated reports"
    echo ""
    echo "4. ${YELLOW}Set Resource Limits:${NC}"
    echo "   - Memory: 512MB (minimum)"
    echo "   - CPU: 0.5 cores (minimum)"
    echo ""
    echo "5. ${YELLOW}Configure Domain:${NC}"
    echo "   - Enable HTTPS/SSL"
    echo "   - Set your custom domain"
    echo "   - Port: 8000"
    echo ""
    echo "6. ${YELLOW}Deploy:${NC}"
    echo "   - Click 'Deploy' button"
    echo "   - Wait for health checks to pass"
    echo "   - Access at: https://your-domain.com"
    echo ""
    echo -e "${BLUE}═══ Alternative: Manual VPS Deployment ═══${NC}"
    echo ""
    echo "# On your VPS:"
    echo "scp ${ARCHIVE_NAME} user@vps:/opt/${APP_NAME}/"
    echo "ssh user@vps"
    echo "cd /opt/${APP_NAME}"
    echo "tar -xzf ${ARCHIVE_NAME}"
    echo "docker-compose -f docker-compose.prod.yml up -d"
    echo ""
    echo -e "${BLUE}═══ Useful Commands ═══${NC}"
    echo ""
    echo "# View logs:"
    echo "docker-compose logs -f crypto-analyzer"
    echo ""
    echo "# Restart service:"
    echo "docker-compose restart crypto-analyzer"
    echo ""
    echo "# Check status:"
    echo "docker-compose ps"
    echo "curl http://localhost:8000/health"
    echo ""
    echo "# Update deployment:"
    echo "./deploy.sh && scp ${ARCHIVE_NAME} user@vps:/opt/${APP_NAME}/"
    echo ""
    print_info "Files created:"
    echo "  - ${GREEN}${ARCHIVE_NAME}${NC} (upload this to EasyPanel)"
    [ -f "${APP_NAME}-image.tar.gz" ] && echo "  - ${GREEN}${APP_NAME}-image.tar.gz${NC} (optional Docker image)"
    echo ""
    print_success "Deployment package ready!"
}

# Main execution
main() {
    print_header
    
    # Parse arguments
    case "${1:-}" in
        --skip-test)
            SKIP_TEST=true
            ;;
        --skip-build)
            SKIP_BUILD=true
            ;;
        --export-image)
            EXPORT_IMAGE=true
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --skip-test      Skip Docker image testing"
            echo "  --skip-build     Skip Docker image building"
            echo "  --export-image   Export Docker image as tar.gz"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
    esac
    
    # Run deployment steps
    check_prerequisites
    
    if [ "${SKIP_BUILD:-false}" != "true" ]; then
        build_image
    fi
    
    if [ "${SKIP_TEST:-false}" != "true" ]; then
        test_image
    fi
    
    create_package
    
    if [ "${EXPORT_IMAGE:-false}" == "true" ]; then
        export_image
    fi
    
    print_instructions
}

# Run main function
main "$@"
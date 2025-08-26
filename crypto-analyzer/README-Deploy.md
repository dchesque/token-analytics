# Crypto Analyzer v2.0 - Deployment Guide

Complete guide for deploying Crypto Analyzer to EasyPanel and other platforms.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [EasyPanel Deployment](#easypanel-deployment)
- [Manual VPS Deployment](#manual-vps-deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Monitoring](#monitoring)
- [Updates](#updates)
- [FAQ](#faq)

## 🎯 Overview

Crypto Analyzer v2.0 is a modern cryptocurrency analysis tool featuring:

- **Dual Mode Operation**: CLI and Web interface
- **Real-time Data**: Market data, social metrics, sentiment analysis
- **Modern UI**: Responsive dashboard with dark/light themes
- **REST API**: Full API access for integrations
- **Docker Ready**: Containerized for easy deployment
- **Production Optimized**: Security, caching, and performance features

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EasyPanel     │    │  Docker         │    │  Application    │
│   (Reverse      │───▶│  Container      │───▶│  Flask Web      │
│   Proxy/SSL)    │    │  (Port 8000)    │    │  + CLI Mode     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       ▼
         │                       │              ┌─────────────────┐
         │                       │              │  External APIs  │
         │                       │              │  - CoinGecko    │
         │                       │              │  - LunarCrush   │
         │                       ▼              │  - DeFiLlama    │
┌─────────────────┐    ┌─────────────────┐    │  - Alternative  │
│   Persistent    │    │   Data &        │    └─────────────────┘
│   Storage       │    │   Reports       │
│   (Volumes)     │    │   Storage       │
└─────────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### For EasyPanel Deployment

- [EasyPanel](https://easypanel.io/) account and VPS
- Domain name (optional but recommended)
- Basic understanding of Docker containers

### For Manual VPS Deployment

- Linux VPS (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- 1GB+ RAM, 10GB+ storage
- Root or sudo access

### API Keys (Optional)

- **LunarCrush API Key** (for social metrics): [lunarcrush.com/developers](https://lunarcrush.com/developers)
- **Messari API Key** (for enhanced data): [messari.io/api](https://messari.io/api)

## 🚀 EasyPanel Deployment

### Step 1: Prepare Deployment Package

1. **Clone or Download** the project:
   ```bash
   git clone <repository-url>
   cd crypto-analyzer
   ```

2. **Run Deployment Script**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   This creates `crypto-analyzer-deploy.tar.gz` with all necessary files.

### Step 2: EasyPanel Setup

1. **Login to EasyPanel Dashboard**
   - Access your EasyPanel instance
   - Navigate to "Projects" or "Applications"

2. **Create New Project**
   - Click "New Project" or "Add Application"
   - Choose "Docker Compose" as project type
   - Set project name: `crypto-analyzer`

3. **Upload Deployment Package**
   - Upload the `crypto-analyzer-deploy.tar.gz` file
   - EasyPanel will extract and detect the Docker Compose configuration

### Step 3: Configure Environment Variables

Set these environment variables in EasyPanel:

#### Required Variables
```env
WEB_MODE=true
PORT=8000
```

#### Optional Variables
```env
# API Keys
LUNARCRUSH_API_KEY=your_lunarcrush_key_here
MESSARI_API_KEY=your_messari_key_here

# Performance
DEBUG=false
CACHE_DURATION=600
MAX_WORKERS=4

# Domain (if using custom domain)
DOMAIN=crypto.yourdomain.com
```

### Step 4: Configure Storage

Map these persistent volumes:

| Container Path | Description | Size |
|---|---|---|
| `/app/data` | Application data and cache | 1GB |
| `/app/reports` | Generated analysis reports | 500MB |

### Step 5: Domain & SSL Setup

1. **Add Domain**:
   - Go to "Domains" in EasyPanel
   - Add your domain: `crypto.yourdomain.com`
   - Point to the crypto-analyzer service

2. **Enable SSL**:
   - Enable "Auto SSL" in EasyPanel
   - Certificate will be automatically provisioned via Let's Encrypt

### Step 6: Deploy

1. **Click Deploy**
2. **Monitor Logs** for successful startup
3. **Access Application** at your configured domain

## 🖥️ Manual VPS Deployment

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/crypto-analyzer
cd /opt/crypto-analyzer
```

### Step 2: Deploy Application

```bash
# Upload and extract deployment package
scp crypto-analyzer-deploy.tar.gz user@your-vps:/opt/crypto-analyzer/
tar -xzf crypto-analyzer-deploy.tar.gz

# Create environment file
cp .env.production .env
# Edit .env with your configuration

# Create persistent directories
mkdir -p data reports

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Setup Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/crypto-analyzer
server {
    listen 80;
    server_name crypto.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/crypto-analyzer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d crypto.yourdomain.com
```

### Step 4: Setup Systemd Service (Optional)

```ini
# /etc/systemd/system/crypto-analyzer.service
[Unit]
Description=Crypto Analyzer Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/opt/crypto-analyzer
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable crypto-analyzer
sudo systemctl start crypto-analyzer
```

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Default | Required |
|---|---|---|---|
| `WEB_MODE` | Enable web interface | `true` | Yes |
| `PORT` | Application port | `8000` | Yes |
| `DEBUG` | Debug mode | `false` | No |
| `LUNARCRUSH_API_KEY` | LunarCrush API key | - | No |
| `MESSARI_API_KEY` | Messari API key | - | No |
| `CACHE_DURATION` | Cache duration (seconds) | `600` | No |
| `MAX_WORKERS` | Worker processes | `4` | No |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `30` | No |

### Resource Requirements

#### Minimum Requirements
- **CPU**: 1 core
- **RAM**: 512MB
- **Storage**: 5GB
- **Network**: 10Mbps

#### Recommended for Production
- **CPU**: 2 cores
- **RAM**: 1GB
- **Storage**: 20GB
- **Network**: 100Mbps

### Performance Tuning

```yaml
# docker-compose.prod.yml adjustments for high traffic
services:
  crypto-analyzer:
    environment:
      - MAX_WORKERS=8
      - CACHE_DURATION=300
      - REQUEST_TIMEOUT=60
    
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 2048M
        reservations:
          cpus: '1.0'
          memory: 512M
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Symptoms**: Container exits immediately or fails health checks

**Solutions**:
```bash
# Check logs
docker-compose logs crypto-analyzer

# Check health status
docker-compose ps

# Run health check manually
docker exec crypto-analyzer python healthcheck.py --verbose

# Check environment variables
docker exec crypto-analyzer env | grep -E "(WEB_MODE|PORT)"
```

#### 2. Web Interface Not Accessible

**Symptoms**: Cannot access web interface, 502/503 errors

**Solutions**:
```bash
# Check if container is running
docker-compose ps

# Check port binding
docker-compose port crypto-analyzer 8000

# Check firewall
sudo ufw status
sudo ufw allow 8000

# Check nginx logs (if using reverse proxy)
sudo tail -f /var/log/nginx/error.log
```

#### 3. API Keys Not Working

**Symptoms**: Social metrics unavailable, rate limiting

**Solutions**:
```bash
# Verify environment variables
docker exec crypto-analyzer env | grep API_KEY

# Test API connectivity
docker exec crypto-analyzer python -c "
import os
print('LunarCrush:', bool(os.environ.get('LUNARCRUSH_API_KEY')))
print('Messari:', bool(os.environ.get('MESSARI_API_KEY')))
"

# Check API status
curl http://localhost:8000/api/status
```

#### 4. High Memory Usage

**Symptoms**: Container using excessive RAM, OOM kills

**Solutions**:
```bash
# Monitor resource usage
docker stats crypto-analyzer

# Reduce cache duration
# Edit .env: CACHE_DURATION=180

# Reduce worker count
# Edit .env: MAX_WORKERS=2

# Restart container
docker-compose restart crypto-analyzer
```

#### 5. SSL Certificate Issues

**Symptoms**: HTTPS not working, certificate errors

**Solutions**:
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check nginx configuration
sudo nginx -t
```

### Debug Mode

Enable debug mode for detailed logging:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

```bash
# View detailed logs
docker-compose logs -f crypto-analyzer
```

### Health Checks

The application includes comprehensive health checks:

```bash
# Manual health check
curl http://localhost:8000/health

# Detailed system check
docker exec crypto-analyzer python healthcheck.py --verbose --json

# API status check
curl http://localhost:8000/api/status
```

## 📊 Monitoring

### Built-in Monitoring

1. **Health Endpoints**:
   - `GET /health` - Basic health check
   - `GET /api/status` - Detailed system status

2. **Logs**:
   ```bash
   # View application logs
   docker-compose logs -f crypto-analyzer
   
   # Follow specific service logs
   docker logs -f crypto-analyzer --tail=100
   ```

3. **Metrics**:
   ```bash
   # Container resource usage
   docker stats crypto-analyzer
   
   # System resource usage
   htop
   df -h
   free -h
   ```

### External Monitoring (Optional)

#### Uptime Monitoring

Set up monitoring for these endpoints:
- `https://your-domain.com/health` (should return 200)
- `https://your-domain.com/api/status` (should return JSON)

#### Log Analysis

```bash
# Setup log rotation
sudo nano /etc/logrotate.d/docker-containers

# Content:
/var/lib/docker/containers/*/*-json.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

#### Resource Alerts

Setup alerts for:
- CPU usage > 80%
- Memory usage > 90%
- Disk usage > 85%
- Response time > 5 seconds

## 🔄 Updates

### Update Application

```bash
# Download new version
wget https://github.com/your-repo/crypto-analyzer/releases/download/v2.1/crypto-analyzer-deploy.tar.gz

# Backup current version
tar -czf backup-$(date +%Y%m%d).tar.gz data/ reports/ .env

# Extract new version
tar -xzf crypto-analyzer-deploy.tar.gz

# Update containers
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl http://localhost:8000/health
```

### Rollback Process

```bash
# Stop current version
docker-compose -f docker-compose.prod.yml down

# Restore backup
tar -xzf backup-YYYYMMDD.tar.gz

# Start previous version
docker-compose -f docker-compose.prod.yml up -d
```

### EasyPanel Updates

1. Upload new deployment package
2. Update environment variables if needed
3. Deploy new version
4. Monitor deployment logs
5. Verify functionality

## ❓ FAQ

### General Questions

**Q: Can I run both CLI and Web modes simultaneously?**
A: No, the container runs in either CLI or Web mode based on the `WEB_MODE` environment variable.

**Q: How much does it cost to run?**
A: The application is free. You only pay for:
- VPS hosting ($5-20/month)
- Domain name ($10-15/year, optional)
- API keys (LunarCrush plans start at $50/month, optional)

**Q: Can I customize the interface?**
A: Yes, you can modify the templates and CSS files before deployment.

### Technical Questions

**Q: What happens if external APIs are down?**
A: The application has fallback mechanisms and will show available data. Check `/api/status` for API availability.

**Q: How is data cached?**
A: API responses are cached in memory for 5-10 minutes (configurable). Persistent data is stored in the `/app/data` volume.

**Q: Can I integrate this with other systems?**
A: Yes, the application provides a REST API at `/api/analyze/<token>` and `/api/compare` endpoints.

### Security Questions

**Q: Is my data secure?**
A: Yes, the application:
- Runs in an isolated Docker container
- Uses HTTPS with SSL certificates
- Doesn't store personal information
- Follows security best practices

**Q: Can I use this commercially?**
A: Check the license file. The application itself is open source, but you're responsible for API key compliance.

### Performance Questions

**Q: How many concurrent users can it handle?**
A: With default settings: 50-100 concurrent users. Scale by adjusting `MAX_WORKERS` and resources.

**Q: How fast are the analyses?**
A: Typical analysis takes 2-5 seconds, depending on API response times and enabled features.

**Q: Can I run multiple instances?**
A: Yes, you can deploy multiple instances behind a load balancer for high availability.

## 🛠️ Advanced Configuration

### Custom Themes

Modify `/static/css/main.css` to customize the appearance:

```css
:root {
  --accent-color: #your-color;
  --bg-primary: #your-background;
}
```

### Additional APIs

Add new data sources by extending the fetcher modules:

```python
# In src/fetcher.py
def fetch_custom_data(self, token):
    # Your custom API integration
    pass
```

### Custom Domains

For multiple domains or subdomains:

```nginx
server {
    listen 443 ssl;
    server_name crypto.domain1.com crypto.domain2.com;
    # ... rest of configuration
}
```

### Database Integration

For persistent data storage, add PostgreSQL or MongoDB:

```yaml
# In docker-compose.prod.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: crypto_analyzer
      POSTGRES_USER: crypto
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the main README.md for API documentation
- **Community**: Join discussions in GitHub Issues
- **Commercial Support**: Contact for enterprise deployments

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

---

**Happy Analyzing! 📈🚀**

*Last updated: $(date)*
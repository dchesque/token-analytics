/**
 * AI Token Preview v2.0 - Main JavaScript
 * Modern vanilla JavaScript with ES6+ features
 */

class CryptoAnalyzer {
    constructor() {
        this.init();
        this.bindEvents();
        this.loadHistory();
        this.checkApiStatus();
        
        // Application state
        this.currentToken = null;
        this.analysisCache = new Map();
        this.historyKey = 'crypto_analyzer_history';
        this.maxHistoryItems = 50;
    }

    init() {
        // Hide loading screen and show app
        setTimeout(() => {
            document.getElementById('loading-screen').style.opacity = '0';
            document.getElementById('app').style.opacity = '1';
            
            setTimeout(() => {
                document.getElementById('loading-screen').style.display = 'none';
            }, 300);
        }, 1000);

        // Initialize theme
        this.initTheme();
        
        // Set focus on search input
        document.getElementById('token-input').focus();
    }

    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
    }

    updateThemeIcon(theme) {
        const icon = document.querySelector('.theme-toggle i');
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    bindEvents() {
        // Search form submission
        document.getElementById('analyze-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAnalyze();
        });

        // Quick token buttons
        document.querySelectorAll('.quick-token').forEach(btn => {
            btn.addEventListener('click', () => {
                const token = btn.dataset.token;
                document.getElementById('token-input').value = token;
                this.analyzeToken(token);
            });
        });

        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Modal handling
        this.initModals();

        // Export report button
        document.addEventListener('click', (e) => {
            if (e.target.matches('#export-report') || e.target.closest('#export-report')) {
                this.exportReport();
            }
            
            if (e.target.matches('#analyze-another') || e.target.closest('#analyze-another')) {
                this.resetToSearch();
            }
            
            if (e.target.matches('#retry-btn') || e.target.closest('#retry-btn')) {
                this.handleAnalyze();
            }
            
            if (e.target.matches('#clear-history') || e.target.closest('#clear-history')) {
                this.clearHistory();
            }
        });

        // History item clicks
        document.getElementById('history-list').addEventListener('click', (e) => {
            const historyItem = e.target.closest('.history-item');
            if (historyItem) {
                const token = historyItem.dataset.token;
                this.analyzeToken(token);
            }
        });

        // Input suggestions (basic implementation)
        const tokenInput = document.getElementById('token-input');
        tokenInput.addEventListener('input', this.debounce(() => {
            this.handleInputSuggestions();
        }, 300));

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals or reset
            if (e.key === 'Escape') {
                this.closeModals();
                if (document.getElementById('results-section').style.display !== 'none') {
                    this.resetToSearch();
                }
            }
            
            // Ctrl/Cmd + K to focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('token-input').focus();
                document.getElementById('token-input').select();
            }
        });
    }

    async handleAnalyze() {
        const tokenInput = document.getElementById('token-input');
        const token = tokenInput.value.trim();
        
        if (!token) {
            this.showError('Please enter a token name or symbol');
            return;
        }
        
        await this.analyzeToken(token);
    }

    async analyzeToken(token) {
        try {
            this.currentToken = token;
            this.showLoadingState(token);
            
            // Check cache first
            const cacheKey = token.toLowerCase();
            const cached = this.analysisCache.get(cacheKey);
            const now = Date.now();
            
            if (cached && (now - cached.timestamp) < 300000) { // 5 minutes cache
                this.displayResults(cached.data);
                return;
            }
            
            // Animate loading steps
            this.animateLoadingSteps();
            
            // Fetch data from API
            const response = await fetch(`/api/analyze/${encodeURIComponent(token)}`);
            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            // Cache the result
            this.analysisCache.set(cacheKey, {
                data: data,
                timestamp: now
            });
            
            // Save to history
            this.saveToHistory(token, data);
            
            // Display results
            this.displayResults(data);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showErrorState(error.message);
        }
    }

    showLoadingState(token) {
        document.getElementById('loading-token').textContent = token;
        document.getElementById('results-section').style.display = 'block';
        document.getElementById('analysis-loading').style.display = 'block';
        document.getElementById('results-content').style.display = 'none';
        document.getElementById('error-state').style.display = 'none';
        
        // Reset loading steps
        document.querySelectorAll('.loading-step').forEach(step => {
            step.classList.remove('active');
        });
        document.querySelector('.loading-step[data-step="market"]').classList.add('active');
        
        // Scroll to results
        document.getElementById('results-section').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    animateLoadingSteps() {
        const steps = ['market', 'social', 'analysis'];
        let currentStep = 0;
        
        const interval = setInterval(() => {
            // Remove active from all steps
            document.querySelectorAll('.loading-step').forEach(step => {
                step.classList.remove('active');
            });
            
            // Add active to current step
            if (currentStep < steps.length) {
                document.querySelector(`.loading-step[data-step="${steps[currentStep]}"]`).classList.add('active');
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 1000);
    }

    displayResults(data) {
        // Hide loading, show results
        document.getElementById('analysis-loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
        document.getElementById('error-state').style.display = 'none';
        
        // Update token info
        this.updateTokenInfo(data);
        
        // Update price information
        this.updatePriceInfo(data);
        
        // Update market metrics
        this.updateMarketMetrics(data);
        
        // Update social metrics
        this.updateSocialMetrics(data);
        
        // Update fear & greed
        this.updateFearGreed(data);
        
        // Update technical analysis
        this.updateTechnicalAnalysis(data);
        
        // Update insights
        this.updateInsights(data);
    }

    updateTokenInfo(data) {
        const tokenData = data.market_data;
        if (!tokenData) return;
        
        document.getElementById('token-name').textContent = tokenData.name || 'Unknown Token';
        document.getElementById('token-symbol').textContent = (tokenData.symbol || '').toUpperCase();
        
        // Update token logo if available
        const logo = document.getElementById('token-logo');
        if (tokenData.image) {
            logo.src = tokenData.image;
            logo.alt = `${tokenData.name} logo`;
            logo.style.display = 'block';
        } else {
            logo.style.display = 'none';
        }
    }

    updatePriceInfo(data) {
        const tokenData = data.market_data;
        if (!tokenData) return;
        
        const price = tokenData.current_price || 0;
        const change24h = tokenData.price_change_percentage_24h || 0;
        
        // Current price
        document.getElementById('current-price').textContent = this.formatCurrency(price);
        
        // Price change
        const changeElement = document.getElementById('price-change');
        changeElement.textContent = `${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%`;
        changeElement.className = `price-change ${change24h >= 0 ? 'positive' : 'negative'}`;
        
        // 24h high/low
        document.getElementById('high-24h').textContent = this.formatCurrency(tokenData.high_24h || 0);
        document.getElementById('low-24h').textContent = this.formatCurrency(tokenData.low_24h || 0);
        
        // Market cap and volume
        document.getElementById('market-cap').textContent = this.formatLargeNumber(tokenData.market_cap || 0);
        document.getElementById('volume-24h').textContent = this.formatLargeNumber(tokenData.total_volume || 0);
    }

    updateMarketMetrics(data) {
        const container = document.getElementById('market-metrics');
        const tokenData = data.market_data;
        
        if (!tokenData) {
            container.innerHTML = '<p class="no-data">No market data available</p>';
            return;
        }
        
        const metrics = [
            { label: 'Market Cap Rank', value: tokenData.market_cap_rank ? `#${tokenData.market_cap_rank}` : 'N/A' },
            { label: 'Circulating Supply', value: this.formatLargeNumber(tokenData.circulating_supply || 0) },
            { label: 'Total Supply', value: this.formatLargeNumber(tokenData.total_supply || 0) },
            { label: 'Max Supply', value: tokenData.max_supply ? this.formatLargeNumber(tokenData.max_supply) : 'N/A' }
        ];
        
        container.innerHTML = metrics.map(metric => `
            <div class="metric-item">
                <span class="metric-value">${metric.value}</span>
                <span class="metric-label">${metric.label}</span>
            </div>
        `).join('');
    }

    updateSocialMetrics(data) {
        const container = document.getElementById('social-metrics');
        const socialData = data.social_data;
        
        if (!socialData || !socialData.lunarcrush_data) {
            container.innerHTML = '<p class="no-data">Configure LunarCrush API key for social metrics</p>';
            return;
        }
        
        const luna = socialData.lunarcrush_data;
        container.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-item">
                    <span class="metric-value">${luna.galaxy_score || 'N/A'}</span>
                    <span class="metric-label">Galaxy Score</span>
                </div>
                <div class="metric-item">
                    <span class="metric-value">${luna.alt_rank || 'N/A'}</span>
                    <span class="metric-label">Alt Rank</span>
                </div>
                <div class="metric-item">
                    <span class="metric-value">${this.formatNumber(luna.social_volume || 0)}</span>
                    <span class="metric-label">Social Volume</span>
                </div>
                <div class="metric-item">
                    <span class="metric-value">${luna.sentiment || 'N/A'}</span>
                    <span class="metric-label">Sentiment</span>
                </div>
            </div>
        `;
    }

    updateFearGreed(data) {
        const fearGreedData = data.fear_greed;
        const valueElement = document.getElementById('fear-greed-value');
        const labelElement = document.getElementById('fear-greed-label');
        
        if (!fearGreedData) {
            valueElement.textContent = '--';
            labelElement.textContent = 'No data';
            return;
        }
        
        valueElement.textContent = fearGreedData.value || '--';
        labelElement.textContent = fearGreedData.value_classification || 'Unknown';
        
        // Update circle color based on value
        const circle = document.getElementById('fear-greed-circle');
        const value = fearGreedData.value || 0;
        let rotation = (value / 100) * 180; // Convert to degrees for semicircle
        
        circle.style.background = `conic-gradient(
            from ${rotation}deg,
            var(--error-color) 0deg,
            var(--warning-color) 60deg,
            var(--success-color) 120deg,
            transparent 180deg
        )`;
    }

    updateTechnicalAnalysis(data) {
        const container = document.getElementById('technical-summary');
        const analysis = data.analysis;
        
        if (!analysis || !analysis.technical_indicators) {
            container.innerHTML = '<p class="no-data">No technical analysis available</p>';
            return;
        }
        
        const indicators = analysis.technical_indicators;
        const items = Object.entries(indicators).map(([key, value]) => {
            const signal = this.getTechnicalSignal(value);
            return `
                <div class="technical-item">
                    <span class="technical-name">${this.formatTechnicalName(key)}</span>
                    <span class="technical-signal ${signal.class}">${signal.text}</span>
                </div>
            `;
        }).join('');
        
        container.innerHTML = items;
    }

    updateInsights(data) {
        const container = document.getElementById('insights-list');
        const insights = data.analysis?.key_insights || [];
        
        if (!insights.length) {
            container.innerHTML = '<p class="no-data">No key insights available</p>';
            return;
        }
        
        const insightItems = insights.map((insight, index) => `
            <div class="insight-item">
                <div class="insight-icon">
                    <i class="fas fa-${this.getInsightIcon(index)}"></i>
                </div>
                <div class="insight-content">
                    <div class="insight-title">${insight.title || `Insight ${index + 1}`}</div>
                    <div class="insight-description">${insight.description || insight}</div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = insightItems;
    }

    showErrorState(message) {
        document.getElementById('analysis-loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'none';
        document.getElementById('error-state').style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }

    resetToSearch() {
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('token-input').value = '';
        document.getElementById('token-input').focus();
    }

    // Theme management
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.updateThemeIcon(newTheme);
    }

    // History management
    saveToHistory(token, data) {
        let history = this.getHistory();
        
        // Remove existing entry for this token
        history = history.filter(item => item.token.toLowerCase() !== token.toLowerCase());
        
        // Add new entry at the beginning
        history.unshift({
            token: token,
            name: data.market_data?.name || token,
            symbol: data.market_data?.symbol || token,
            image: data.market_data?.image,
            timestamp: Date.now(),
            price: data.market_data?.current_price,
            change: data.market_data?.price_change_percentage_24h
        });
        
        // Limit history size
        if (history.length > this.maxHistoryItems) {
            history = history.slice(0, this.maxHistoryItems);
        }
        
        localStorage.setItem(this.historyKey, JSON.stringify(history));
        this.displayHistory();
    }

    getHistory() {
        try {
            return JSON.parse(localStorage.getItem(this.historyKey)) || [];
        } catch {
            return [];
        }
    }

    displayHistory() {
        const container = document.getElementById('history-list');
        const history = this.getHistory();
        
        if (!history.length) {
            container.innerHTML = '<p class="no-history">No recent analysis found</p>';
            return;
        }
        
        const historyItems = history.slice(0, 12).map(item => `
            <div class="history-item" data-token="${item.token}">
                <div class="history-token">
                    ${item.image ? `<img src="${item.image}" alt="${item.name}" width="24" height="24">` : ''}
                    <span class="history-token-name">${item.name || item.token}</span>
                </div>
                <div class="history-timestamp">${this.formatTimestamp(item.timestamp)}</div>
                ${item.price ? `<div class="history-price">${this.formatCurrency(item.price)}</div>` : ''}
            </div>
        `).join('');
        
        container.innerHTML = historyItems;
    }

    clearHistory() {
        if (confirm('Are you sure you want to clear the analysis history?')) {
            localStorage.removeItem(this.historyKey);
            this.displayHistory();
        }
    }

    loadHistory() {
        this.displayHistory();
    }

    // API status check
    async checkApiStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            const statusIndicator = document.getElementById('api-status');
            const statusIcon = statusIndicator.querySelector('i');
            const statusText = statusIndicator.querySelector('span');
            
            if (data.success) {
                statusIndicator.className = 'status-indicator healthy';
                statusText.textContent = 'APIs Online';
                
                // Show API details in tooltip or similar
                const workingApis = Object.entries(data.apis || {})
                    .filter(([name, status]) => status)
                    .map(([name]) => name);
                
                statusIndicator.title = `Working APIs: ${workingApis.join(', ')}`;
            } else {
                statusIndicator.className = 'status-indicator error';
                statusText.textContent = 'API Issues';
                statusIndicator.title = 'Some APIs may be unavailable';
            }
        } catch (error) {
            const statusIndicator = document.getElementById('api-status');
            statusIndicator.className = 'status-indicator error';
            statusIndicator.querySelector('span').textContent = 'Connection Error';
            statusIndicator.title = 'Unable to check API status';
        }
    }

    // Export functionality
    async exportReport() {
        if (!this.currentToken) return;
        
        try {
            const response = await fetch(`/api/report/${encodeURIComponent(this.currentToken)}`);
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.currentToken}_analysis_${new Date().toISOString().split('T')[0]}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            this.showError('Failed to export report');
        }
    }

    // Modal management
    initModals() {
        document.getElementById('about-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.showModal('about-modal');
        });
        
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModals();
            });
        });
        
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModals();
                }
            });
        });
    }

    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    // Input suggestions (basic implementation)
    handleInputSuggestions() {
        const input = document.getElementById('token-input');
        const value = input.value.trim();
        
        if (value.length < 2) {
            this.hideSuggestions();
            return;
        }
        
        // Basic suggestions based on popular tokens
        const suggestions = [
            'bitcoin', 'ethereum', 'cardano', 'solana', 'polygon', 'chainlink',
            'polkadot', 'litecoin', 'bitcoin-cash', 'stellar', 'xrp', 'dogecoin'
        ].filter(token => token.toLowerCase().includes(value.toLowerCase()));
        
        this.showSuggestions(suggestions.slice(0, 5));
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('search-suggestions');
        
        if (!suggestions.length) {
            this.hideSuggestions();
            return;
        }
        
        container.innerHTML = suggestions.map(token => `
            <div class="suggestion-item" data-token="${token}">
                ${token}
            </div>
        `).join('');
        
        container.style.display = 'block';
        
        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                document.getElementById('token-input').value = item.dataset.token;
                this.hideSuggestions();
                this.analyzeToken(item.dataset.token);
            });
        });
    }

    hideSuggestions() {
        document.getElementById('search-suggestions').style.display = 'none';
    }

    // Utility functions
    formatCurrency(value, currency = 'USD') {
        if (typeof value !== 'number' || isNaN(value)) return '$0.00';
        
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: value < 0.01 ? 6 : 2,
            maximumFractionDigits: value < 0.01 ? 6 : 2
        }).format(value);
    }

    formatLargeNumber(value) {
        if (typeof value !== 'number' || isNaN(value)) return '0';
        
        if (value >= 1e12) {
            return `$${(value / 1e12).toFixed(2)}T`;
        } else if (value >= 1e9) {
            return `$${(value / 1e9).toFixed(2)}B`;
        } else if (value >= 1e6) {
            return `$${(value / 1e6).toFixed(2)}M`;
        } else if (value >= 1e3) {
            return `$${(value / 1e3).toFixed(2)}K`;
        } else {
            return `$${value.toFixed(2)}`;
        }
    }

    formatNumber(value) {
        if (typeof value !== 'number' || isNaN(value)) return '0';
        
        return new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 2
        }).format(value);
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        
        return date.toLocaleDateString();
    }

    formatTechnicalName(key) {
        return key.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    getTechnicalSignal(value) {
        if (typeof value === 'string') {
            const lower = value.toLowerCase();
            if (lower.includes('bullish') || lower.includes('buy')) {
                return { class: 'bullish', text: 'Bullish' };
            } else if (lower.includes('bearish') || lower.includes('sell')) {
                return { class: 'bearish', text: 'Bearish' };
            } else {
                return { class: 'neutral', text: 'Neutral' };
            }
        } else if (typeof value === 'number') {
            if (value > 0.6) {
                return { class: 'bullish', text: 'Bullish' };
            } else if (value < 0.4) {
                return { class: 'bearish', text: 'Bearish' };
            } else {
                return { class: 'neutral', text: 'Neutral' };
            }
        }
        
        return { class: 'neutral', text: 'Unknown' };
    }

    getInsightIcon(index) {
        const icons = ['lightbulb', 'chart-line', 'exclamation-triangle', 'info-circle', 'star'];
        return icons[index % icons.length];
    }

    showError(message) {
        // Simple error display - could be enhanced with a toast system
        alert(message);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CryptoAnalyzer();
});

// Handle service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Could register a service worker here for offline functionality
    });
}

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Application error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});
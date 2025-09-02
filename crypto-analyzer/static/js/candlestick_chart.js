/**
 * Candlestick Chart Component for Master Token Analysis
 * Integrates with DEX Screener, GeckoTerminal, and Uniswap Subgraph
 */

class CandlestickChart {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.chart = null;
        this.currentToken = null;
        this.currentPool = null;
        this.currentTimeframe = '5m';
        this.isLoading = false;
        
        // Create chart HTML structure
        this.createChartHTML();
        this.bindEvents();
    }
    
    createChartHTML() {
        this.container.innerHTML = `
            <div class="candlestick-chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">
                        <i class="fas fa-chart-line"></i>
                        Price Chart
                    </h3>
                    <div class="chart-controls">
                        <div class="timeframe-buttons">
                            <button class="timeframe-btn active" data-timeframe="5m">5m</button>
                            <button class="timeframe-btn" data-timeframe="15m">15m</button>
                            <button class="timeframe-btn" data-timeframe="1h">1h</button>
                            <button class="timeframe-btn" data-timeframe="4h">4h</button>
                            <button class="timeframe-btn" data-timeframe="1d">1d</button>
                        </div>
                        <div class="chart-info">
                            <span id="chart-pool-info">Select a token to view chart</span>
                        </div>
                    </div>
                </div>
                <div class="chart-content">
                    <div class="chart-loading" id="chart-loading" style="display: none;">
                        <div class="loading-spinner"></div>
                        <p>Loading chart data...</p>
                    </div>
                    <div class="chart-error" id="chart-error" style="display: none;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p id="chart-error-message">No chart data available</p>
                    </div>
                    <canvas id="candlestick-canvas"></canvas>
                </div>
                <div class="chart-footer">
                    <div class="pool-selector" id="pool-selector" style="display: none;">
                        <label>Pool:</label>
                        <select id="pool-select">
                            <option value="">Select pool...</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
        
        // Add CSS styles
        this.addStyles();
    }
    
    addStyles() {
        const styleId = 'candlestick-chart-styles';
        if (document.getElementById(styleId)) return;
        
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .candlestick-chart-container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin: 20px 0;
                overflow: hidden;
            }
            
            .chart-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .chart-title {
                margin: 0;
                font-size: 1.2em;
                font-weight: 600;
            }
            
            .chart-title i {
                margin-right: 8px;
            }
            
            .chart-controls {
                display: flex;
                align-items: center;
                gap: 15px;
            }
            
            .timeframe-buttons {
                display: flex;
                gap: 5px;
            }
            
            .timeframe-btn {
                padding: 6px 12px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
                font-size: 12px;
            }
            
            .timeframe-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .timeframe-btn.active {
                background: white;
                color: #667eea;
                font-weight: bold;
            }
            
            .chart-info {
                font-size: 0.9em;
                opacity: 0.9;
            }
            
            .chart-content {
                position: relative;
                height: 400px;
                padding: 20px;
            }
            
            .chart-loading, .chart-error {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
                color: #666;
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            #candlestick-canvas {
                width: 100%;
                height: 100%;
                display: block;
            }
            
            .chart-footer {
                padding: 15px 20px;
                background: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
            
            .pool-selector {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .pool-selector label {
                font-weight: 500;
                color: #495057;
            }
            
            #pool-select {
                padding: 6px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background: white;
                min-width: 200px;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    bindEvents() {
        // Timeframe button clicks
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('timeframe-btn')) {
                this.setTimeframe(e.target.dataset.timeframe);
            }
        });
        
        // Pool selection
        const poolSelect = this.container.querySelector('#pool-select');
        if (poolSelect) {
            poolSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.selectPool(e.target.value);
                }
            });
        }
    }
    
    async loadTokenChart(token, chain = 'ethereum') {
        this.currentToken = token;
        this.showLoading();
        
        try {
            console.log(`Loading chart for ${token} on ${chain}`);
            
            // Step 1: Get token pools
            const pools = await this.fetchTokenPools(chain, token);
            
            if (!pools || !pools.data || !pools.data.primary_pool) {
                this.showError('No trading pools found for this token');
                return;
            }
            
            // Step 2: Populate pool selector
            this.populatePoolSelector(pools.data);
            
            // Step 3: Load chart for primary pool
            const primaryPool = pools.data.primary_pool;
            this.currentPool = primaryPool.pool_address;
            
            await this.loadPoolChart(chain, this.currentPool);
            
            // Update chart info
            this.updateChartInfo(primaryPool);
            
        } catch (error) {
            console.error('Error loading token chart:', error);
            this.showError('Failed to load chart data');
        }
    }
    
    async fetchTokenPools(chain, tokenAddress) {
        const response = await fetch(`/api/token/${chain}/${tokenAddress}/pools`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }
    
    async fetchPoolOHLCV(network, pool, timeframe = '5m', limit = 200) {
        const params = new URLSearchParams({
            timeframe: timeframe,
            limit: limit.toString()
        });
        
        const response = await fetch(`/api/ohlcv/${network}/${pool}?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    }
    
    async loadPoolChart(network, poolAddress) {
        try {
            console.log(`Loading OHLCV for pool ${poolAddress} on ${network}`);
            
            const ohlcvData = await this.fetchPoolOHLCV(network, poolAddress, this.currentTimeframe);
            
            if (!ohlcvData || !ohlcvData.data || ohlcvData.data.length === 0) {
                this.showError('No chart data available for this pool');
                return;
            }
            
            // Render candlestick chart
            this.renderChart(ohlcvData.data);
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading pool chart:', error);
            this.showError('Failed to load chart data');
        }
    }
    
    populatePoolSelector(poolsData) {
        const poolSelect = this.container.querySelector('#pool-select');
        const poolSelector = this.container.querySelector('#pool-selector');
        
        // Clear existing options
        poolSelect.innerHTML = '<option value="">Select pool...</option>';
        
        // Add primary pool
        if (poolsData.primary_pool) {
            const pool = poolsData.primary_pool;
            const option = document.createElement('option');
            option.value = pool.pool_address;
            option.textContent = `${pool.base_token.symbol}/${pool.quote_token.symbol} (${pool.dex_id}) - $${pool.liquidity_usd.toLocaleString()}`;
            option.selected = true;
            poolSelect.appendChild(option);
        }
        
        // Add other pools
        if (poolsData.all_pools) {
            poolsData.all_pools.slice(1, 6).forEach(pool => { // Show top 5 alternative pools
                const option = document.createElement('option');
                option.value = pool.pool_address;
                option.textContent = `${pool.base_token.symbol}/${pool.quote_token.symbol} (${pool.dex_id}) - $${pool.liquidity_usd.toLocaleString()}`;
                poolSelect.appendChild(option);
            });
        }
        
        poolSelector.style.display = 'flex';
    }
    
    async selectPool(poolAddress) {
        this.currentPool = poolAddress;
        await this.loadPoolChart('ethereum', poolAddress); // Default to ethereum for now
    }
    
    setTimeframe(timeframe) {
        // Update active button
        this.container.querySelectorAll('.timeframe-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        this.container.querySelector(`[data-timeframe="${timeframe}"]`).classList.add('active');
        
        this.currentTimeframe = timeframe;
        
        // Reload chart with new timeframe
        if (this.currentPool) {
            this.loadPoolChart('ethereum', this.currentPool);
        }
    }
    
    renderChart(ohlcvData) {
        const canvas = this.container.querySelector('#candlestick-canvas');
        const ctx = canvas.getContext('2d');
        
        // Clear previous chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Convert OHLCV data to Chart.js format
        const chartData = this.formatChartData(ohlcvData);
        
        // Chart.js configuration
        const config = {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'Price',
                    data: chartData,
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.getTimeUnit(this.currentTimeframe),
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'MMM DD HH:mm',
                                day: 'MMM DD'
                            }
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            display: true,
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(4);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                const point = context.raw;
                                return [
                                    `Open: $${point.o.toFixed(4)}`,
                                    `High: $${point.h.toFixed(4)}`,
                                    `Low: $${point.l.toFixed(4)}`,
                                    `Close: $${point.c.toFixed(4)}`,
                                    `Volume: $${point.v ? point.v.toLocaleString() : 'N/A'}`
                                ];
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        };
        
        // Check if Chart.js candlestick plugin is available
        if (typeof Chart !== 'undefined') {
            try {
                this.chart = new Chart(ctx, config);
            } catch (error) {
                console.warn('Candlestick chart not available, using line chart fallback:', error);
                this.renderLineChart(ohlcvData);
            }
        } else {
            console.warn('Chart.js not available, rendering simple chart');
            this.renderSimpleChart(ohlcvData);
        }
    }
    
    formatChartData(ohlcvData) {
        return ohlcvData.map(candle => ({
            x: new Date(candle[0] * 1000), // Convert timestamp to Date
            o: candle[1], // open
            h: candle[2], // high
            l: candle[3], // low
            c: candle[4], // close
            v: candle[5]  // volume
        }));
    }
    
    renderLineChart(ohlcvData) {
        // Fallback to line chart if candlestick not available
        const canvas = this.container.querySelector('#candlestick-canvas');
        const ctx = canvas.getContext('2d');
        
        const chartData = ohlcvData.map(candle => ({
            x: new Date(candle[0] * 1000),
            y: candle[4] // close price
        }));
        
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Price',
                    data: chartData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.getTimeUnit(this.currentTimeframe)
                        }
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(4);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    renderSimpleChart(ohlcvData) {
        // Very simple canvas-based chart if Chart.js is not available
        const canvas = this.container.querySelector('#candlestick-canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        const width = canvas.width;
        const height = canvas.height;
        const padding = 40;
        
        // Calculate price range
        const prices = ohlcvData.map(candle => candle[4]); // close prices
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const priceRange = maxPrice - minPrice;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw line chart
        ctx.beginPath();
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        
        ohlcvData.forEach((candle, index) => {
            const x = padding + (index / (ohlcvData.length - 1)) * (width - 2 * padding);
            const y = height - padding - ((candle[4] - minPrice) / priceRange) * (height - 2 * padding);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Draw price labels
        ctx.fillStyle = '#666';
        ctx.font = '12px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`$${maxPrice.toFixed(4)}`, 5, 20);
        ctx.fillText(`$${minPrice.toFixed(4)}`, 5, height - 10);
        
        // Draw title
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Price Chart (Simple View)', width / 2, 20);
    }
    
    getTimeUnit(timeframe) {
        switch (timeframe) {
            case '1m':
            case '5m':
            case '15m':
                return 'minute';
            case '1h':
            case '4h':
                return 'hour';
            case '1d':
                return 'day';
            default:
                return 'hour';
        }
    }
    
    updateChartInfo(pool) {
        const infoElement = this.container.querySelector('#chart-pool-info');
        if (infoElement && pool) {
            infoElement.textContent = `${pool.base_token.symbol}/${pool.quote_token.symbol} on ${pool.dex_id} - $${pool.price_usd} ($${pool.liquidity_usd.toLocaleString()} liquidity)`;
        }
    }
    
    showLoading() {
        this.isLoading = true;
        this.container.querySelector('#chart-loading').style.display = 'block';
        this.container.querySelector('#chart-error').style.display = 'none';
        this.container.querySelector('#candlestick-canvas').style.display = 'none';
    }
    
    hideLoading() {
        this.isLoading = false;
        this.container.querySelector('#chart-loading').style.display = 'none';
        this.container.querySelector('#candlestick-canvas').style.display = 'block';
    }
    
    showError(message) {
        this.isLoading = false;
        this.container.querySelector('#chart-loading').style.display = 'none';
        this.container.querySelector('#chart-error').style.display = 'block';
        this.container.querySelector('#chart-error-message').textContent = message;
        this.container.querySelector('#candlestick-canvas').style.display = 'none';
    }
    
    // Public method to get token address from token symbol
    async resolveTokenAddress(tokenSymbol) {
        // This would typically query CoinGecko or a token registry
        // For now, return some known token addresses
        const knownTokens = {
            'BTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', // WBTC
            'ETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', // WETH
            'USDC': '0xa0b86a33e6441c67b2e3a4e2fc4c69861f8f3ec6',
            'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
            'UNI': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'
        };
        
        return knownTokens[tokenSymbol.toUpperCase()] || tokenSymbol;
    }
}

// Auto-refresh functionality
CandlestickChart.prototype.startAutoRefresh = function(intervalSeconds = 30) {
    if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
    }
    
    this.refreshInterval = setInterval(() => {
        if (this.currentPool && !this.isLoading) {
            console.log('Auto-refreshing chart data...');
            this.loadPoolChart('ethereum', this.currentPool);
        }
    }, intervalSeconds * 1000);
};

CandlestickChart.prototype.stopAutoRefresh = function() {
    if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
    }
};

// Export for use in other scripts
window.CandlestickChart = CandlestickChart;
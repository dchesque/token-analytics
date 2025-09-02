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
                background: var(--bg-card, #1e293b);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                margin: 20px 0;
                overflow: hidden;
                border: 1px solid var(--border-color, rgba(148, 163, 184, 0.2));
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
                color: var(--text-secondary, #94a3b8);
            }
            
            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid rgba(148, 163, 184, 0.3);
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
                background: var(--bg-secondary, #0f172a);
                border-top: 1px solid var(--border-color, rgba(148, 163, 184, 0.2));
                color: var(--text-secondary, #94a3b8);
            }
            
            .pool-selector {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .pool-selector label {
                font-weight: 500;
                color: var(--text-primary, #e2e8f0);
            }
            
            #pool-select {
                padding: 6px 12px;
                border: 1px solid var(--border-color, rgba(148, 163, 184, 0.3));
                border-radius: 4px;
                background: var(--bg-card, #1e293b);
                color: var(--text-primary, #e2e8f0);
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
    
    async loadTokenChart(token, chain = null) {
        this.currentToken = token;
        this.showLoading();
        
        try {
            console.log(`Loading chart for ${token}`);
            
            // Auto-detect best chain for token
            const bestChain = chain || this.detectBestChain(token);
            console.log(`Using chain: ${bestChain}`);
            
            // Step 1: Get token pools
            const pools = await this.fetchTokenPools(bestChain, token);
            
            if (!pools || !pools.data || !pools.data.primary_pool) {
                console.warn('No pools found, generating mock chart with realistic data');
                await this.loadMockChart(token, bestChain);
                return;
            }
            
            // Step 2: Populate pool selector
            this.populatePoolSelector(pools.data);
            
            // Step 3: Load chart for primary pool
            const primaryPool = pools.data.primary_pool;
            this.currentPool = primaryPool.pool_address;
            
            await this.loadPoolChart(bestChain, this.currentPool);
            
            // Update chart info
            this.updateChartInfo(primaryPool);
            
        } catch (error) {
            console.error('Error loading token chart:', error);
            console.log('Falling back to mock chart');
            await this.loadMockChart(token, chain || 'ethereum');
        }
    }
    
    detectBestChain(token) {
        const tokenLower = token.toLowerCase();
        
        // Chain-specific tokens
        const chainMappings = {
            'solana': 'solana',
            'sol': 'solana',
            'bnb': 'bsc',
            'binancecoin': 'bsc',
            'matic': 'polygon', 
            'polygon': 'polygon',
            'avax': 'avalanche',
            'avalanche': 'avalanche',
            'dot': 'polkadot',
            'polkadot': 'polkadot'
        };
        
        return chainMappings[tokenLower] || 'ethereum';
    }
    
    async loadMockChart(token, chain) {
        console.log(`Loading mock chart for ${token} on ${chain}`);
        
        // Get mock pools data
        const pools = this.getMockPoolData(chain, token);
        this.populatePoolSelector(pools.data);
        
        // Generate realistic mock OHLCV data
        const mockOHLCV = this.generateMockOHLCV(pools.data.primary_pool.price_usd);
        
        // Render the chart
        this.renderChart(mockOHLCV);
        
        // Update chart info
        this.updateChartInfo(pools.data.primary_pool);
        
        this.hideLoading();
    }
    
    async fetchTokenPools(chain, tokenAddress) {
        try {
            const response = await fetch(`/api/token/${chain}/${tokenAddress}/pools`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('API endpoint not available, using mock data');
        }
        
        // Fallback: return mock pool data for testing
        return this.getMockPoolData(chain, tokenAddress);
    }
    
    getMockPoolData(chain, tokenAddress) {
        // Comprehensive token mapping for better display
        const tokenMap = {
            'bitcoin': { symbol: 'BTC', name: 'Bitcoin', price: 110000 },
            'btc': { symbol: 'BTC', name: 'Bitcoin', price: 110000 },
            'ethereum': { symbol: 'ETH', name: 'Ethereum', price: 4400 },
            'eth': { symbol: 'ETH', name: 'Ethereum', price: 4400 },
            'solana': { symbol: 'SOL', name: 'Solana', price: 260 },
            'sol': { symbol: 'SOL', name: 'Solana', price: 260 },
            'cardano': { symbol: 'ADA', name: 'Cardano', price: 1.2 },
            'ada': { symbol: 'ADA', name: 'Cardano', price: 1.2 },
            'polkadot': { symbol: 'DOT', name: 'Polkadot', price: 8.5 },
            'dot': { symbol: 'DOT', name: 'Polkadot', price: 8.5 },
            'chainlink': { symbol: 'LINK', name: 'Chainlink', price: 25 },
            'link': { symbol: 'LINK', name: 'Chainlink', price: 25 },
            'uniswap': { symbol: 'UNI', name: 'Uniswap', price: 15 },
            'uni': { symbol: 'UNI', name: 'Uniswap', price: 15 },
            'avalanche': { symbol: 'AVAX', name: 'Avalanche', price: 45 },
            'avax': { symbol: 'AVAX', name: 'Avalanche', price: 45 },
            'polygon': { symbol: 'MATIC', name: 'Polygon', price: 1.1 },
            'matic': { symbol: 'MATIC', name: 'Polygon', price: 1.1 },
            'tether': { symbol: 'USDT', name: 'Tether', price: 1.0 },
            'usdt': { symbol: 'USDT', name: 'Tether', price: 1.0 },
            'usd-coin': { symbol: 'USDC', name: 'USD Coin', price: 1.0 },
            'usdc': { symbol: 'USDC', name: 'USD Coin', price: 1.0 },
            'binancecoin': { symbol: 'BNB', name: 'BNB', price: 700 },
            'bnb': { symbol: 'BNB', name: 'BNB', price: 700 },
        };
        
        const tokenKey = tokenAddress.toLowerCase();
        const tokenInfo = tokenMap[tokenKey] || { 
            symbol: tokenAddress.length === 42 ? 'TOKEN' : tokenAddress.toUpperCase(), 
            name: `${tokenAddress} Token`,
            price: 100 + Math.random() * 1000
        };
        
        const mockPools = {
            success: true,
            chain: chain,
            token_address: tokenAddress,
            data: {
                primary_pool: {
                    pool_address: '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                    base_token: {
                        symbol: tokenInfo.symbol,
                        name: tokenInfo.name
                    },
                    quote_token: {
                        symbol: chain === 'ethereum' ? 'WETH' : 'USDC',
                        name: chain === 'ethereum' ? 'Wrapped Ethereum' : 'USD Coin'
                    },
                    dex_id: chain === 'ethereum' ? 'uniswap_v3' : 'raydium',
                    price_usd: tokenInfo.price,
                    liquidity_usd: 1000000 + Math.random() * 10000000
                },
                all_pools: []
            }
        };
        
        console.log(`Using mock pool data for ${tokenAddress} -> ${tokenInfo.symbol}/${mockPools.data.primary_pool.quote_token.symbol}`);
        return mockPools;
    }
    
    async fetchPoolOHLCV(network, pool, timeframe = '5m', limit = 200) {
        try {
            const params = new URLSearchParams({
                timeframe: timeframe,
                limit: limit.toString()
            });
            
            const response = await fetch(`/api/ohlcv/${network}/${pool}?${params}`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.warn('OHLCV API endpoint not available, generating mock data');
        }
        
        // Fallback: generate mock OHLCV data
        return this.getMockOHLCVData(timeframe, limit);
    }
    
    getMockOHLCVData(timeframe, limit) {
        const now = Date.now();
        const timeframeMinutes = this._timeframe_to_minutes(timeframe);
        const intervalMs = timeframeMinutes * 60 * 1000;
        
        const candles = [];
        let basePrice = 2000 + Math.random() * 1000; // Base price around $2000-3000
        
        for (let i = limit - 1; i >= 0; i--) {
            const timestamp = Math.floor((now - (i * intervalMs)) / 1000);
            
            // Generate realistic price movement
            const volatility = 0.02; // 2% max change per candle
            const change = (Math.random() - 0.5) * 2 * volatility;
            const open = basePrice;
            const close = open * (1 + change);
            
            // Generate high/low with some spread
            const spread = Math.abs(change) + Math.random() * 0.01;
            const high = Math.max(open, close) * (1 + spread);
            const low = Math.min(open, close) * (1 - spread);
            
            // Generate volume
            const volume = 100000 + Math.random() * 500000;
            
            candles.push([timestamp, open, high, low, close, volume]);
            
            // Update base price for next candle
            basePrice = close;
        }
        
        console.log(`Generated ${candles.length} mock OHLCV candles for ${timeframe}`);
        
        return {
            success: true,
            data: candles,
            candles_count: candles.length,
            network: 'ethereum',
            pool: 'mock_pool',
            timeframe: timeframe
        };
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
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    up: {
                        borderColor: '#10b981', // Verde para velas de alta
                        backgroundColor: 'rgba(16, 185, 129, 0.1)'
                    },
                    down: {
                        borderColor: '#ef4444', // Vermelho para velas de baixa
                        backgroundColor: 'rgba(239, 68, 68, 0.1)'
                    }
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                // Dark theme configuration
                backgroundColor: '#1a1a1a',
                color: '#e2e8f0',
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
                            color: 'rgba(148, 163, 184, 0.1)',
                            borderColor: 'rgba(148, 163, 184, 0.3)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                size: 11
                            }
                        },
                        border: {
                            color: 'rgba(148, 163, 184, 0.3)'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        grid: {
                            display: true,
                            color: 'rgba(148, 163, 184, 0.1)',
                            borderColor: 'rgba(148, 163, 184, 0.3)'
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: {
                                size: 11
                            },
                            callback: function(value) {
                                return '$' + value.toFixed(4);
                            }
                        },
                        border: {
                            color: 'rgba(148, 163, 184, 0.3)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false,
                        labels: {
                            color: '#e2e8f0'
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#e2e8f0',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(148, 163, 184, 0.3)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
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
                    tension: 0.3,
                    pointBackgroundColor: '#764ba2',
                    pointBorderColor: '#667eea',
                    pointRadius: 2,
                    pointHoverRadius: 4
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
    
    _timeframe_to_minutes(timeframe) {
        const timeframe_map = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        };
        return timeframe_map[timeframe] || 5;
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
        // Extensive token mapping for major cryptocurrencies
        const knownTokens = {
            // Major tokens
            'BTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', // WBTC
            'BITCOIN': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', // WBTC
            'WBTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
            
            'ETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', // WETH
            'ETHEREUM': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', // WETH
            'WETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
            
            // Stablecoins
            'USDC': '0xa0b86a33e6441c67b2e3a4e2fc4c69861f8f3ec6',
            'USDT': '0xdac17f958d2ee523a2206206994597c13d831ec7',
            'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f',
            'BUSD': '0x4fabb145d64652a948d72533023f6e7a623c7c53',
            'FRAX': '0x853d955acef822db058eb8505911ed77f175b99e',
            
            // DeFi tokens
            'UNI': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
            'UNISWAP': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984',
            'AAVE': '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',
            'COMP': '0xc00e94cb662c3520282e6f5717214004a7f26888',
            'SUSHI': '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2',
            'CRV': '0xd533a949740bb3306d119cc777fa900ba034cd52',
            'CURVE': '0xd533a949740bb3306d119cc777fa900ba034cd52',
            '1INCH': '0x111111111117dc0aa78b770fa6a738034120c302',
            'SNX': '0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f',
            'SYNTHETIX': '0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f',
            
            // Layer 2 / Other chains tokens
            'MATIC': '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0',
            'POLYGON': '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0',
            'AVAX': '0x85f138bfee4ef8e540890cfb48f620571d67eda3', // wrapped AVAX on Ethereum
            'AVALANCHE': '0x85f138bfee4ef8e540890cfb48f620571d67eda3',
            
            // Popular altcoins
            'LINK': '0x514910771af9ca656af840dff83e8264ecf986ca',
            'CHAINLINK': '0x514910771af9ca656af840dff83e8264ecf986ca',
            'ADA': '0x3ee2200efb3400fabb9aacf31297cbdd1d435d47', // BSC wrapped ADA
            'CARDANO': '0x3ee2200efb3400fabb9aacf31297cbdd1d435d47',
            'SOL': '0x570a5d26f7765ecb712c0924e4de545b89fd43df', // Wrapped SOL
            'SOLANA': '0x570a5d26f7765ecb712c0924e4de545b89fd43df',
            'DOT': '0x7083609fce4d1d8dc0c979aab8c869ea2c873402', // Wrapped DOT
            'POLKADOT': '0x7083609fce4d1d8dc0c979aab8c869ea2c873402',
            
            // Meme coins
            'DOGE': '0x4206931337dc273a630d328da6441786bfad668f', // Wrapped DOGE
            'DOGECOIN': '0x4206931337dc273a630d328da6441786bfad668f',
            'SHIB': '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce',
            'SHIBA': '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce',
            'PEPE': '0x6982508145454ce325ddbe47a25d4ec3d2311933',
            
            // Exchange tokens
            'BNB': '0xb8c77482e45f1f44de1745f52c74426c631bdd52', // BNB on Ethereum
            'BINANCE': '0xb8c77482e45f1f44de1745f52c74426c631bdd52',
            'CRO': '0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b',
            'CRONOS': '0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b',
            'FTT': '0x50d1c9771902476076ecfc8b2a83ad6b9355a4c9', // FTX Token
            'OKB': '0x75231f58b43240c9718dd58b4967c5114342a86c',
            
            // Popular ERC-20 tokens
            'BAT': '0x0d8775f648430679a709e98d2b0cb6250d2887ef',
            'ZRX': '0xe41d2489571d322189246dafa5ebde1f4699f498',
            'OMG': '0xd26114cd6ee289accf82350c8d8487fedb8a0c07',
            'GNT': '0xa74476443119a942de498590fe1f2454d7d4ac0d', // Golem
            'REP': '0x221657776846890989a759ba2973e427dff5c9bb', // Augur
            'KNC': '0xdd974d5c2e2928dea5f71b9825b8b646686bd200', // Kyber Network
            'LRC': '0xbbbbca6a901c926f240b89eacb641d8aec7aeafd', // Loopring
            'RLC': '0x607f4c5bb672230e8672085532f7e901544a7375', // iExec RLC
        };
        
        const symbol = tokenSymbol.toUpperCase().trim();
        
        // Try exact match first
        if (knownTokens[symbol]) {
            console.log(`Resolved ${tokenSymbol} to ${knownTokens[symbol]}`);
            return knownTokens[symbol];
        }
        
        // If it looks like an address already, return it
        if (tokenSymbol.startsWith('0x') && tokenSymbol.length === 42) {
            console.log(`${tokenSymbol} appears to be an address already`);
            return tokenSymbol.toLowerCase();
        }
        
        // Try partial matching (e.g., user enters "bitcoin" but we have "BTC")
        const partialMatch = Object.keys(knownTokens).find(key => 
            key.includes(symbol) || symbol.includes(key)
        );
        
        if (partialMatch) {
            console.log(`Partial match: ${tokenSymbol} → ${partialMatch} → ${knownTokens[partialMatch]}`);
            return knownTokens[partialMatch];
        }
        
        console.warn(`No address found for token: ${tokenSymbol}, using as-is`);
        return tokenSymbol;
    }
    
    generateMockOHLCV(basePrice, days = 7, intervalMinutes = 5) {
        const candles = [];
        const totalCandles = (days * 24 * 60) / intervalMinutes;
        const now = Date.now();
        let currentPrice = basePrice;
        
        console.log(`Generating ${totalCandles} mock candles for ${days} days`);
        
        for (let i = totalCandles - 1; i >= 0; i--) {
            const timestamp = now - (i * intervalMinutes * 60 * 1000);
            
            // Add some realistic price movement
            const volatility = 0.02; // 2% volatility
            const trend = (Math.random() - 0.5) * 0.001; // Small trend component
            const priceChange = (Math.random() - 0.5) * volatility + trend;
            
            const open = currentPrice;
            const priceMove = open * priceChange;
            const high = open + Math.abs(priceMove) * (1 + Math.random() * 0.5);
            const low = open - Math.abs(priceMove) * (1 + Math.random() * 0.5);
            const close = open + priceMove;
            
            // Ensure high is highest and low is lowest
            const actualHigh = Math.max(open, high, low, close);
            const actualLow = Math.min(open, high, low, close);
            
            const volume = 50000 + Math.random() * 500000; // Random volume
            
            candles.push({
                x: timestamp,
                o: open,
                h: actualHigh,
                l: actualLow,
                c: close,
                v: volume
            });
            
            currentPrice = close;
        }
        
        console.log(`Generated ${candles.length} mock candles, price range: $${Math.min(...candles.map(c => c.l)).toFixed(4)} - $${Math.max(...candles.map(c => c.h)).toFixed(4)}`);
        return candles;
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
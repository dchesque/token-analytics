// master_display_fix.js
// Funções para exibir corretamente os dados do backend

function displayTechnicalAnalysis(data) {
    const technical = data.technical || {};
    const container = document.getElementById('technical-content');
    
    if (!container) return;
    
    if (technical.status === 'completed' && technical.momentum) {
        container.innerHTML = `
            <div class="analysis-content">
                <h4>Technical Indicators</h4>
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="label">Momentum:</span>
                        <span class="value">${technical.momentum || 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Fear & Greed Index:</span>
                        <span class="value">${technical.indicators?.fear_greed || 50}/100</span>
                    </div>
                    <div class="metric">
                        <span class="label">24h Price Change:</span>
                        <span class="value">${technical.indicators?.price_change_24h || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">7d Price Change:</span>
                        <span class="value">${technical.indicators?.price_change_7d || 0}%</span>
                    </div>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = '<p>Technical analysis data loading...</p>';
    }
}

function displayTradingLevels(data) {
    const levels = data.trading_levels || {};
    const container = document.getElementById('trading-levels-content');
    
    if (!container) return;
    
    if (levels.status === 'completed' && levels.entry_points) {
        const entryPoints = levels.entry_points || [];
        const takeProfits = levels.take_profit || [];
        const stopLoss = levels.stop_loss || 0;
        
        container.innerHTML = `
            <div class="trading-levels">
                <h4>Entry Points</h4>
                <div class="levels-list">
                    ${entryPoints.map((price, i) => `
                        <div class="level-item">
                            <span class="label">Entry ${i+1}:</span>
                            <span class="value">$${price.toFixed(6)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <h4>Take Profit Targets</h4>
                <div class="levels-list">
                    ${takeProfits.map((price, i) => `
                        <div class="level-item">
                            <span class="label">TP ${i+1}:</span>
                            <span class="value">$${price.toFixed(6)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <h4>Stop Loss</h4>
                <div class="level-item">
                    <span class="label">SL:</span>
                    <span class="value">$${stopLoss.toFixed(6)}</span>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = '<p>Trading levels calculating...</p>';
    }
}

function displayAIInsights(data) {
    const insights = data.ai_insights || {};
    const container = document.getElementById('ai-insights-content');
    
    if (!container) return;
    
    if (insights.status === 'completed' && insights.summary) {
        container.innerHTML = `
            <div class="ai-insights">
                <h4>AI Analysis Summary</h4>
                <p class="summary">${insights.summary}</p>
                
                <div class="insights-grid">
                    <div class="insight-item">
                        <span class="label">Sentiment:</span>
                        <span class="value ${insights.sentiment?.toLowerCase()}">${insights.sentiment || 'NEUTRAL'}</span>
                    </div>
                    <div class="insight-item">
                        <span class="label">Confidence:</span>
                        <span class="value">${insights.confidence || 0}%</span>
                    </div>
                </div>
                
                ${insights.key_factors?.length ? `
                    <h5>Key Factors</h5>
                    <ul>
                        ${insights.key_factors.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${insights.risks?.length ? `
                    <h5>Risks</h5>
                    <ul class="risks">
                        ${insights.risks.map(r => `<li>${r}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${insights.opportunities?.length ? `
                    <h5>Opportunities</h5>
                    <ul class="opportunities">
                        ${insights.opportunities.map(o => `<li>${o}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    } else {
        container.innerHTML = '<p>AI insights processing...</p>';
    }
}

function displayStrategies(data) {
    const strategies = data.strategies || {};
    const container = document.getElementById('strategies-content');
    
    if (!container) return;
    
    if (strategies.status === 'completed') {
        const strategyTypes = ['conservative', 'moderate', 'aggressive'];
        
        container.innerHTML = `
            <div class="strategies">
                ${strategyTypes.map(type => {
                    const strat = strategies[type] || {};
                    return `
                        <div class="strategy-card ${type}">
                            <h4>${type.charAt(0).toUpperCase() + type.slice(1)} Strategy</h4>
                            <div class="strategy-details">
                                <p><strong>Action:</strong> ${strat.action || 'N/A'}</p>
                                <p><strong>Position Size:</strong> ${strat.position_size || '0%'}</p>
                                <p><strong>Risk/Reward:</strong> ${strat.risk_reward || 'N/A'}</p>
                                <p><strong>Description:</strong> ${strat.description || 'Strategy details not available'}</p>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } else {
        container.innerHTML = '<p>Strategy recommendations loading...</p>';
    }
}

// Função principal para atualizar toda a interface
function updateMasterDisplay(data) {
    console.log('Updating display with data:', data);
    
    // Atualizar cada seção
    displayTechnicalAnalysis(data);
    displayTradingLevels(data);
    displayAIInsights(data);
    displayStrategies(data);
    
    // Atualizar status na overview
    updateComponentStatus(data.components);
}

function updateComponentStatus(components) {
    // Atualizar indicadores de status na overview
    Object.keys(components || {}).forEach(comp => {
        const status = components[comp].status;
        const element = document.querySelector(`[data-component="${comp}"]`);
        if (element) {
            element.className = `status-indicator ${status}`;
            element.textContent = status.toUpperCase();
        }
    });
}

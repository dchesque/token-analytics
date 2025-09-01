// transparent_display.js - Visualização profissional do sistema de scoring transparente

function displayTransparentScoring(data) {
    console.log('🔍 displayTransparentScoring called with data:', data);
    
    const fundamentalData = data.fundamental;
    const scoringData = fundamentalData?.transparent_scoring;
    
    if (!scoringData) {
        console.log('❌ No transparent scoring data available');
        console.log('Available in fundamental:', Object.keys(fundamentalData || {}));
        return;
    }
    
    console.log('✅ Found transparent scoring data:', scoringData.final_score);
    
    // Tentar encontrar container - múltiplas opções
    let container = document.getElementById('fundamental-content') 
        || document.getElementById('technical-content')
        || document.querySelector('#fundamental .tab-content')
        || document.querySelector('.results-section');
    
    if (!container) {
        console.log('❌ No suitable container found');
        console.log('Available elements:', [
            document.getElementById('fundamental-content') ? 'fundamental-content' : null,
            document.getElementById('technical-content') ? 'technical-content' : null,
            document.querySelector('#fundamental .tab-content') ? 'fundamental tab-content' : null,
            document.querySelector('.results-section') ? 'results-section' : null
        ].filter(Boolean));
        return;
    }
    
    console.log('📍 Using container:', container.id || container.className);
    
    // Adicionar ao invés de substituir
    const transparentHTML = generateTransparentScoringHTML(scoringData);
    container.innerHTML = transparentHTML + container.innerHTML;
    
    console.log('✅ Transparent scoring displayed successfully');
}

function generateTransparentScoringHTML(scoringData) {
    const finalScore = scoringData.final_score;
    const eliminationCriteria = scoringData.elimination_criteria;
    const scoringCategories = scoringData.scoring_categories;
    const tokenData = scoringData.token_data;
    
    return `
        <div class="transparent-scoring">
            <div class="scoring-header">
                <h3>Análise Transparente: ${tokenData?.symbol || 'Token'}</h3>
                <div class="final-score-display">
                    <div class="score-circle ${getGradeClass(finalScore.grade)}">
                        <span class="score-value">${finalScore.value}/10</span>
                        <span class="score-percentage">${finalScore.percentage}%</span>
                        <span class="score-grade">${finalScore.grade}</span>
                    </div>
                    <div class="score-classification">
                        <h4>${finalScore.classification}</h4>
                    </div>
                </div>
            </div>
            
            <!-- Critérios de Eliminação -->
            <div class="elimination-criteria">
                <h4>🚨 Critérios de Eliminação</h4>
                <div class="criteria-grid">
                    ${Object.entries(eliminationCriteria).map(([key, criteria]) => `
                        <div class="criterion-item ${criteria.passed ? 'passed' : 'failed'}">
                            <div class="criterion-status">
                                ${criteria.passed ? '✅' : '❌'}
                            </div>
                            <div class="criterion-details">
                                <span class="criterion-label">${getCriterionLabel(key)}</span>
                                <span class="criterion-value">${criteria.reason}</span>
                                <span class="criterion-threshold">Mínimo: ${formatThreshold(key, criteria.threshold)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Pontuação por Categoria -->
            <div class="scoring-categories">
                <h4>📊 Breakdown do Score</h4>
                <div class="categories-container">
                    ${Object.entries(scoringCategories).map(([key, category]) => `
                        <div class="category-item">
                            <div class="category-header">
                                <span class="category-name">${getCategoryLabel(key)}</span>
                                <span class="category-score">${category.score}/${category.max}</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${(category.score / category.max) * 100}%"></div>
                            </div>
                            <div class="category-details">
                                <p class="category-description">${category.details}</p>
                                <ul class="category-factors">
                                    ${category.factors.map(factor => `<li>${factor}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Dados do Token -->
            <div class="token-metrics">
                <h4>📈 Métricas do Token</h4>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Market Cap</span>
                        <span class="metric-value">$${formatNumber(tokenData.market_cap)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Volume 24h</span>
                        <span class="metric-value">$${formatNumber(tokenData.volume_24h)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Rank</span>
                        <span class="metric-value">#${tokenData.market_cap_rank || 'N/A'}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Preço</span>
                        <span class="metric-value">$${formatPrice(tokenData.current_price)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">24h Change</span>
                        <span class="metric-value ${tokenData.price_change_24h >= 0 ? 'positive' : 'negative'}">
                            ${tokenData.price_change_24h?.toFixed(2) || 0}%
                        </span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">30d Change</span>
                        <span class="metric-value ${tokenData.price_change_30d >= 0 ? 'positive' : 'negative'}">
                            ${tokenData.price_change_30d?.toFixed(2) || 0}%
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getGradeClass(grade) {
    const gradeClasses = {
        'A+': 'grade-a-plus',
        'A': 'grade-a',
        'B+': 'grade-b-plus',
        'B': 'grade-b',
        'C+': 'grade-c-plus',
        'C': 'grade-c',
        'D': 'grade-d',
        'F': 'grade-f'
    };
    return gradeClasses[grade] || 'grade-f';
}

function getCriterionLabel(key) {
    const labels = {
        'market_cap': 'Market Cap',
        'volume_24h': 'Volume 24h',
        'token_age': 'Idade do Token',
        'liquidity': 'Liquidez'
    };
    return labels[key] || key;
}

function getCategoryLabel(key) {
    const labels = {
        'market_position': 'Posição no Mercado',
        'liquidity': 'Liquidez',
        'community': 'Comunidade',
        'development': 'Desenvolvimento',
        'performance': 'Performance'
    };
    return labels[key] || key;
}

function formatThreshold(key, threshold) {
    switch(key) {
        case 'market_cap':
        case 'volume_24h':
            return `$${formatNumber(threshold)}`;
        case 'token_age':
            return `${threshold} dias`;
        case 'liquidity':
            return `${(threshold * 100).toFixed(2)}%`;
        default:
            return threshold;
    }
}

function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toLocaleString();
}

function formatPrice(price) {
    if (!price) return '0';
    if (price >= 1) return price.toFixed(2);
    if (price >= 0.01) return price.toFixed(4);
    if (price >= 0.0001) return price.toFixed(6);
    return price.toFixed(8);
}

// Integrar com sistema existente
function updateMasterDisplayWithTransparent(data) {
    console.log('🎯 updateMasterDisplayWithTransparent called');
    console.log('Data received:', data);
    
    // Chamar função original
    if (typeof updateMasterDisplay === 'function') {
        console.log('📞 Calling original updateMasterDisplay');
        updateMasterDisplay(data);
    } else {
        console.log('⚠️ updateMasterDisplay function not available');
    }
    
    // Adicionar visualização transparente
    console.log('🔄 Calling displayTransparentScoring');
    displayTransparentScoring(data);
}

// Sobrescrever função de display existente para incluir transparent scoring
if (typeof window !== 'undefined') {
    const originalDisplayResults = window.displayResults;
    window.displayResults = function(data) {
        // Chamar função original se existir
        if (typeof originalDisplayResults === 'function') {
            originalDisplayResults.call(this, data);
        }
        
        // Aplicar correções de display existentes
        if (typeof updateMasterDisplay === 'function') {
            updateMasterDisplay(data);
        }
        
        // Aplicar transparent scoring
        updateMasterDisplayWithTransparent(data);
    };
}
// Safe Currency Formatter - Frontend only formatting without breaking backend

class SafeCurrencyFormatter {
    static formatCurrency(value, options = {}) {
        const { decimals = null } = options;
        
        if (value === null || value === undefined || value === 0) {
            return '$0.00';
        }

        const num = parseFloat(value);
        
        // Auto-detect decimals
        let finalDecimals = decimals;
        if (finalDecimals === null) {
            if (Math.abs(num) >= 10000) {
                finalDecimals = 2;
            } else if (Math.abs(num) >= 100) {
                finalDecimals = 2;
            } else if (Math.abs(num) >= 1) {
                finalDecimals = 2;
            } else if (Math.abs(num) >= 0.01) {
                finalDecimals = 4;
            } else {
                finalDecimals = 8;
            }
        }

        // Format with locale
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: finalDecimals,
            maximumFractionDigits: finalDecimals
        }).format(num);
    }

    static formatCompact(value) {
        if (value === null || value === undefined || value === 0) {
            return '$0.00';
        }

        const num = parseFloat(value);
        
        if (Math.abs(num) >= 1_000_000_000_000) {
            return `$${(num / 1_000_000_000_000).toFixed(2)}T`;
        } else if (Math.abs(num) >= 1_000_000_000) {
            return `$${(num / 1_000_000_000).toFixed(2)}B`;
        } else if (Math.abs(num) >= 1_000_000) {
            return `$${(num / 1_000_000).toFixed(2)}M`;
        } else if (Math.abs(num) >= 1_000) {
            return `$${(num / 1_000).toFixed(1)}K`;
        } else {
            return this.formatCurrency(num);
        }
    }

    static formatPercentage(value, decimals = 1) {
        if (value === null || value === undefined) {
            return "0.0%";
        }
        const num = parseFloat(value);
        return `${num.toFixed(decimals)}%`;
    }

    // Format all price values in displayed elements
    static formatDisplayedPrices() {
        // Format any element with data-price attribute
        document.querySelectorAll('[data-price]').forEach(element => {
            const value = parseFloat(element.dataset.price);
            element.textContent = this.formatCurrency(value);
        });

        // Format any element with data-market-cap attribute
        document.querySelectorAll('[data-market-cap]').forEach(element => {
            const value = parseFloat(element.dataset.marketCap);
            element.textContent = this.formatCompact(value);
        });

        // Format any element with data-volume attribute
        document.querySelectorAll('[data-volume]').forEach(element => {
            const value = parseFloat(element.dataset.volume);
            element.textContent = this.formatCompact(value);
        });
    }
}

window.SafeCurrencyFormatter = SafeCurrencyFormatter;
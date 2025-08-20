import json
from datetime import datetime
from pathlib import Path

def format_currency(value):
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.2f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"

def format_number(value):
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return f"{value:.0f}"

def safe_divide(numerator, denominator):
    if denominator == 0 or numerator is None or denominator is None:
        return 0
    return numerator / denominator

def get_age_in_days(genesis_date_str):
    if not genesis_date_str:
        return 0
    
    try:
        genesis = datetime.strptime(genesis_date_str, '%Y-%m-%d')
        return (datetime.now() - genesis).days
    except ValueError:
        return 0

def categorize_market_cap(market_cap):
    if market_cap >= 10_000_000_000:
        return "Large Cap"
    elif market_cap >= 1_000_000_000:
        return "Mid Cap"
    elif market_cap >= 100_000_000:
        return "Small Cap"
    else:
        return "Micro Cap"

def get_risk_level(market_cap, age_days, volume_ratio):
    risk_score = 0
    
    if market_cap < 100_000_000:
        risk_score += 2
    elif market_cap < 1_000_000_000:
        risk_score += 1
    
    if age_days < 365:
        risk_score += 2
    elif age_days < 730:
        risk_score += 1
    
    if volume_ratio < 0.01:
        risk_score += 2
    elif volume_ratio < 0.05:
        risk_score += 1
    
    if risk_score >= 5:
        return "Very High"
    elif risk_score >= 3:
        return "High"
    elif risk_score >= 1:
        return "Medium"
    else:
        return "Low"

def validate_token_data(data):
    required_fields = ['price', 'market_cap', 'volume']
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] <= 0:
            return False, f"Campo obrigatório inválido: {field}"
    
    return True, "Dados válidos"
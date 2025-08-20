#!/usr/bin/env python3
"""
minimal_test.py - Test core functionality without print statements to avoid Unicode issues
"""

from analyzer import CryptoAnalyzer

def test_without_print():
    """Test analyzer functionality and return results without printing"""
    
    try:
        analyzer = CryptoAnalyzer()
        
        # Test analysis of bitcoin
        result = analyzer.analyze('bitcoin')
        
        # Validate result structure
        if not result:
            return False, "No result returned"
            
        if not result.get('passed_elimination'):
            return False, f"Token rejected: {result.get('elimination_reasons', [])}"
            
        # Check required fields for DisplayManager
        required_fields = [
            'token', 'token_name', 'passed_elimination', 'score',
            'score_breakdown', 'classification_info', 'data'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing fields: {missing_fields}"
        
        # Test DisplayManager instantiation
        from display_manager import DisplayManager
        display_manager = DisplayManager()
        
        # Test helper functions
        test_num = 1000000
        formatted = display_manager._format_number(test_num)
        if formatted != "1.00M":
            return False, f"Format number failed: expected '1.00M', got '{formatted}'"
        
        # Test percentage calculation
        percent = display_manager._calc_percent(100, 110)
        if abs(percent - 10.0) > 0.001:
            return False, f"Percent calculation failed: expected 10.0, got {percent}"
        
        # Test position size calculation
        position = display_manager._calculate_position_size(8.5)
        if position != "12-15":
            return False, f"Position size failed: expected '12-15', got '{position}'"
            
        return True, {
            'token': result['token'],
            'score': result['score'],
            'classification': result.get('classification', 'N/A'),
            'market_cap': result['data'].get('market_cap', 0),
            'price': result['data'].get('price', 0)
        }
        
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, result = test_without_print()
    
    if success:
        # Print success message - should work
        with open('test_result.txt', 'w') as f:
            f.write("TEST SUCCESS\n")
            f.write(f"Token: {result['token']}\n")
            f.write(f"Score: {result['score']}/10\n")
            f.write(f"Classification: {result['classification']}\n")
            f.write(f"Market Cap: ${result['market_cap']:,.0f}\n")
            f.write(f"Price: ${result['price']:,.2f}\n")
        
        print("SUCCESS - Check test_result.txt for details")
    else:
        with open('test_result.txt', 'w') as f:
            f.write("TEST FAILED\n")
            f.write(f"Error: {result}\n")
        print(f"FAILED - {result}")
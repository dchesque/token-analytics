#!/usr/bin/env python3
"""
Test script for Gemini 2.0 Flash integration
Tests if the new model is working correctly
"""

import sys
import os
from pathlib import Path

# Add src to path to import modules
sys.path.append(str(Path(__file__).parent / 'src'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

try:
    from ai_openrouter_agent import create_ai_agent
    from prompts.crypto_analysis_prompts import AnalysisType
    print("SUCCESS: Imports successful")
except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)

def test_gemini_integration():
    """Test Gemini 2.0 Flash integration"""
    print("TESTING: Gemini 2.0 Flash integration...")
    print(f"AI_TIER: {os.getenv('AI_TIER')}")
    print(f"OpenRouter Key: {'SET' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}")
    
    try:
        # Create AI agent
        print("\nCREATING: AI agent...")
        agent = create_ai_agent()
        if not agent:
            print("ERROR: Failed to create AI agent")
            return False
        print("SUCCESS: AI agent created successfully")
        
        # Test data for Bitcoin analysis
        test_data = {
            'token': 'bitcoin',
            'price': 110000,
            'market_cap': 2200000000000,
            'volume_24h': 50000000000,
            'price_change_24h': -1.2,
            'score': 9,
            'classification': 'MAJOR'
        }
        
        print(f"\nDATA: Testing analysis with: {test_data}")
        print("CALLING: AI agent for analysis...")
        
        # Make AI analysis call
        response = agent.analyze_token(
            token_data=test_data,
            analysis_type=AnalysisType.TECHNICAL,
            user_id='gemini_test'
        )
        
        print(f"\nRESULTS: Analysis completed")
        print(f"Success: {response.success if response else 'No response'}")
        if response:
            print(f"Model used: {response.model_used}")
            print(f"Cost: ${response.cost:.6f}" if response.cost else "Cost: N/A")
            print(f"Tokens used: {response.tokens_used}" if response.tokens_used else "Tokens: N/A")
            print(f"Processing time: {response.processing_time:.2f}s" if response.processing_time else "Time: N/A")
            print(f"Cached: {response.cached}")
            
            if response.success and response.data:
                analysis_preview = str(response.data).replace('\n', ' ')[:200]
                print(f"Response preview: {analysis_preview}...")
                
                # Check if it's actually using Gemini
                if response.model_used == "google/gemini-2.0-flash-001":
                    print("SUCCESS: Using Gemini 2.0 Flash!")
                    return True
                else:
                    print(f"WARNING: Expected Gemini 2.0 Flash, got {response.model_used}")
                    return False
            else:
                print(f"ERROR: Analysis failed: {response.error if response else 'No response'}")
                return False
        else:
            print("ERROR: No response from AI agent")
            return False
            
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("GEMINI 2.0 FLASH INTEGRATION TEST")
    print("=" * 50)
    
    success = test_gemini_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("TEST PASSED: Gemini 2.0 Flash is working!")
        print("Expected cost per analysis: ~$0.0001")
        print("Expected performance: 3-5 seconds")
    else:
        print("TEST FAILED: Check configuration and logs")
        
    print("=" * 50)
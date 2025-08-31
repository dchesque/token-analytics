#!/usr/bin/env python3
"""
Quick validation test for the crypto analyzer fixes
Tests the most critical functionality to ensure the application is working
"""

import requests
import json
import sys
import time

def test_basic_functionality():
    """Test basic endpoint functionality"""
    base_url = "http://localhost:5000"
    
    print("🔍 Quick Test - Crypto Analyzer Master Endpoint")
    print("-" * 50)
    
    # Test 1: Server running
    print("1. Testing server availability...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server not reachable: {e}")
        print("   💡 Make sure to run: python web_app.py")
        return False
    
    # Test 2: Master endpoint basic functionality
    print("\n2. Testing master endpoint with Bitcoin...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/api/analyze/bitcoin/master", timeout=25)
        response_time = time.time() - start_time
        
        print(f"   Response time: {response_time:.2f}s")
        print(f"   HTTP status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Expected HTTP 200, got {response.status_code}")
            return False
        
        # Parse JSON
        try:
            data = response.json()
            print("   ✅ Valid JSON response")
        except:
            print("   ❌ Invalid JSON response")
            return False
        
        # Check essential fields
        required_fields = ['success', 'token', 'timestamp', 'completion_rate']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            print(f"   ❌ Missing fields: {missing}")
            return False
        
        print("   ✅ All essential fields present")
        
        # Check analysis results
        completion_rate = data.get('completion_rate', 0)
        success = data.get('success', False)
        
        print(f"   📊 Success: {success}")
        print(f"   📊 Completion Rate: {completion_rate}%")
        
        if completion_rate > 0:
            print("   ✅ Analysis completed with data")
        else:
            print("   ⚠️  Low completion rate")
        
        # Check for components
        components = data.get('components', {})
        if components:
            print(f"   📊 Components: {len(components)} found")
            working_components = sum(1 for status in components.values() 
                                   if (status == 'completed' or 
                                       (isinstance(status, dict) and status.get('status') == 'completed')))
            print(f"   📊 Working components: {working_components}/{len(components)}")
        
        return True
        
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout (>25s)")
        return False
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    """Run the quick test"""
    success = test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 QUICK TEST PASSED")
        print("The crypto analyzer appears to be working correctly!")
        print("\n💡 Next steps:")
        print("  • Run full tests: python test_master_endpoint.py")
        print("  • Check the web interface: http://localhost:5000/master")
    else:
        print("❌ QUICK TEST FAILED")
        print("Some issues were found. Check the output above for details.")
        print("\n🔧 Troubleshooting:")
        print("  • Make sure Flask app is running: python web_app.py")
        print("  • Check for any error messages in the console")
        print("  • Run diagnostic: python test_master_endpoint.py")
    
    print("=" * 50)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
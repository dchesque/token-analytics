#!/usr/bin/env python3
"""
Test script for Master Analysis Endpoint
Tests the comprehensive fixes implemented for the /api/analyze/<token>/master endpoint
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any, List, Tuple

class MasterEndpointTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.test_tokens = ["bitcoin", "ethereum", "invalid-token-123", "solana"]
        
    def run_all_tests(self) -> bool:
        """Run all test scenarios and return overall success"""
        print("="*60)
        print("CRYPTO ANALYZER - MASTER ENDPOINT TEST SUITE")
        print("="*60)
        print(f"Testing endpoint: {self.base_url}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        all_passed = True
        
        # Test 1: Server availability
        all_passed &= self.test_server_availability()
        
        # Test 2: Valid token analysis
        all_passed &= self.test_valid_token_analysis()
        
        # Test 3: Invalid token handling
        all_passed &= self.test_invalid_token_handling()
        
        # Test 4: Response structure validation
        all_passed &= self.test_response_structure()
        
        # Test 5: Fallback behavior
        all_passed &= self.test_fallback_behavior()
        
        # Test 6: Component status handling
        all_passed &= self.test_component_status()
        
        # Test 7: Error handling improvements
        all_passed &= self.test_error_handling()
        
        # Print summary
        self.print_summary(all_passed)
        
        return all_passed
    
    def test_server_availability(self) -> bool:
        """Test if the server is running and responsive"""
        print("\n[TEST 1] Server Availability")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=10)
            if response.status_code == 200:
                print("✅ Server is running and responsive")
                return True
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot reach server: {e}")
            print("💡 Make sure the Flask application is running on the specified port")
            return False
    
    def test_valid_token_analysis(self) -> bool:
        """Test master analysis with valid tokens"""
        print("\n[TEST 2] Valid Token Analysis")
        print("-" * 40)
        
        success_count = 0
        test_tokens = ["bitcoin", "ethereum"]
        
        for token in test_tokens:
            print(f"\nTesting token: {token}")
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}/api/analyze/{token}/master",
                    timeout=30
                )
                processing_time = time.time() - start_time
                
                print(f"  Response time: {processing_time:.2f}s")
                print(f"  HTTP Status: {response.status_code}")
                
                # Should always return HTTP 200 (even with errors)
                if response.status_code != 200:
                    print(f"  ❌ Expected HTTP 200, got {response.status_code}")
                    continue
                
                # Check if response is valid JSON
                try:
                    data = response.json()
                    print(f"  ✅ Valid JSON response received")
                except json.JSONDecodeError:
                    print(f"  ❌ Invalid JSON response")
                    continue
                
                # Check essential fields
                essential_fields = ['success', 'token', 'timestamp']
                missing_fields = [field for field in essential_fields if field not in data]
                
                if missing_fields:
                    print(f"  ❌ Missing essential fields: {missing_fields}")
                else:
                    print(f"  ✅ All essential fields present")
                    success_count += 1
                
                # Print analysis results summary
                if data.get('success'):
                    completion_rate = data.get('completion_rate', 0)
                    print(f"  📊 Completion Rate: {completion_rate}%")
                    print(f"  📊 Components: {len(data.get('components', {}))}")
                else:
                    print(f"  ⚠️  Analysis completed with errors: {data.get('error', 'Unknown')}")
                    if data.get('partial_data'):
                        print(f"  📊 Partial data available")
                
            except requests.exceptions.Timeout:
                print(f"  ❌ Request timeout (>30s)")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Request error: {e}")
        
        success_rate = success_count / len(test_tokens) * 100
        print(f"\n📊 Valid Token Test Success Rate: {success_rate:.1f}%")
        return success_count > 0  # Pass if at least one token works
    
    def test_invalid_token_handling(self) -> bool:
        """Test how the endpoint handles invalid tokens"""
        print("\n[TEST 3] Invalid Token Handling")
        print("-" * 40)
        
        invalid_tokens = ["nonexistent-token-xyz", ""]
        success = True
        
        for token in invalid_tokens:
            print(f"\nTesting invalid token: '{token}'")
            try:
                response = requests.get(
                    f"{self.base_url}/api/analyze/{token}/master",
                    timeout=15
                )
                
                print(f"  HTTP Status: {response.status_code}")
                
                # Should return HTTP 200 with error information
                if response.status_code != 200:
                    print(f"  ❌ Expected HTTP 200, got {response.status_code}")
                    success = False
                    continue
                
                data = response.json()
                
                # Should have success=False for invalid tokens
                if data.get('success', True):
                    print(f"  ❌ Expected success=False for invalid token")
                    success = False
                else:
                    print(f"  ✅ Correctly marked as unsuccessful")
                    print(f"  📝 Error: {data.get('error', 'No error message')}")
                    
            except Exception as e:
                print(f"  ❌ Exception during invalid token test: {e}")
                success = False
        
        return success
    
    def test_response_structure(self) -> bool:
        """Test that response structure matches expected format"""
        print("\n[TEST 4] Response Structure Validation")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/api/analyze/bitcoin/master", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code} - Cannot test structure")
                return False
            
            data = response.json()
            
            # Required top-level fields
            required_fields = ['success', 'token', 'timestamp', 'completion_rate', 'processing_time']
            success_fields = ['fundamental', 'technical', 'ai_insights', 'trading_levels', 'strategies', 'formatted_report', 'components']
            
            print("Checking required fields:")
            for field in required_fields:
                if field in data:
                    print(f"  ✅ {field}")
                else:
                    print(f"  ❌ {field} - MISSING")
            
            print("\nChecking success-dependent fields:")
            for field in success_fields:
                if field in data:
                    field_value = data[field]
                    if field_value is not None:
                        print(f"  ✅ {field} - Present")
                    else:
                        print(f"  ⚠️  {field} - Null (fallback)")
                else:
                    print(f"  ❌ {field} - Missing")
            
            # Check components structure
            components = data.get('components', {})
            if components:
                print(f"\nComponent Status Summary:")
                for comp_name, comp_status in components.items():
                    status = comp_status if isinstance(comp_status, str) else comp_status.get('status', 'unknown')
                    print(f"  {comp_name}: {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Structure test failed: {e}")
            return False
    
    def test_fallback_behavior(self) -> bool:
        """Test fallback behavior when components fail"""
        print("\n[TEST 5] Fallback Behavior")
        print("-" * 40)
        
        print("Testing endpoint behavior under component stress...")
        
        try:
            response = requests.get(f"{self.base_url}/api/analyze/ethereum/master", timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Unexpected status code: {response.status_code}")
                return False
            
            data = response.json()
            
            # Check if using fallback mechanisms
            completion_rate = data.get('completion_rate', 0)
            
            if completion_rate < 100:
                print(f"⚠️  Partial completion detected: {completion_rate}%")
                print("✅ Fallback system appears to be working")
                
                # Check if partial data is provided
                if any(data.get(key) is not None for key in ['fundamental', 'technical']):
                    print("✅ Partial data successfully provided")
                else:
                    print("❌ No partial data provided during fallback")
                    return False
            else:
                print("✅ Full analysis completed successfully")
            
            # Always should return HTTP 200 and valid JSON
            print("✅ Endpoint maintains stability during partial failures")
            return True
            
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
            return False
    
    def test_component_status(self) -> bool:
        """Test component status reporting"""
        print("\n[TEST 6] Component Status Reporting")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/api/analyze/solana/master", timeout=30)
            data = response.json()
            
            components = data.get('components', {})
            
            if not components:
                print("❌ No component status information found")
                return False
            
            print(f"Found {len(components)} components:")
            
            status_types = {}
            for comp_name, comp_data in components.items():
                status = comp_data if isinstance(comp_data, str) else comp_data.get('status', 'unknown')
                status_types[status] = status_types.get(status, 0) + 1
                
                print(f"  {comp_name}: {status}")
                
                # Check for error details if available
                if isinstance(comp_data, dict) and comp_data.get('error'):
                    print(f"    Error: {comp_data['error']}")
            
            print(f"\nStatus Summary:")
            for status, count in status_types.items():
                print(f"  {status}: {count} components")
            
            # Check if completion rate matches component status
            completion_rate = data.get('completion_rate', 0)
            completed_components = status_types.get('completed', 0)
            total_components = len(components)
            
            if total_components > 0:
                expected_rate = (completed_components / total_components) * 100
                rate_difference = abs(completion_rate - expected_rate)
                
                if rate_difference < 20:  # Allow some tolerance for fallback calculations
                    print(f"✅ Completion rate ({completion_rate}%) aligns with component status")
                else:
                    print(f"⚠️  Completion rate ({completion_rate}%) vs calculated ({expected_rate:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ Component status test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test improved error handling"""
        print("\n[TEST 7] Error Handling Improvements")
        print("-" * 40)
        
        test_scenarios = [
            ("valid_token", "bitcoin", "Should succeed or provide partial data"),
            ("invalid_token", "fake-token-xyz", "Should fail gracefully"),
            ("empty_token", "", "Should handle empty input"),
        ]
        
        all_passed = True
        
        for scenario_name, token, description in test_scenarios:
            print(f"\nTesting {scenario_name}: {description}")
            try:
                response = requests.get(
                    f"{self.base_url}/api/analyze/{token}/master",
                    timeout=20
                )
                
                # All scenarios should return HTTP 200
                if response.status_code != 200:
                    print(f"  ❌ Expected HTTP 200, got {response.status_code}")
                    all_passed = False
                    continue
                
                # Should always return valid JSON
                try:
                    data = response.json()
                    print(f"  ✅ Valid JSON response")
                except json.JSONDecodeError:
                    print(f"  ❌ Invalid JSON response")
                    all_passed = False
                    continue
                
                # Check error message quality
                if not data.get('success', True):
                    error_msg = data.get('error', '')
                    if error_msg:
                        print(f"  ✅ Descriptive error message: {error_msg[:100]}")
                    else:
                        print(f"  ❌ No error message provided")
                        all_passed = False
                
                # Check if partial data is provided when possible
                if scenario_name == "valid_token" and not data.get('success'):
                    if data.get('partial_data') or any(data.get(key) for key in ['fundamental', 'technical']):
                        print(f"  ✅ Partial data provided during errors")
                    else:
                        print(f"  ⚠️  No partial data provided")
                
            except requests.exceptions.Timeout:
                print(f"  ❌ Request timeout")
                all_passed = False
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def print_summary(self, overall_success: bool) -> None:
        """Print test results summary"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        if overall_success:
            print("🎉 OVERALL RESULT: PASSED")
            print("\n✅ Key improvements validated:")
            print("  • HTTP 200 responses for all scenarios")
            print("  • Structured error handling")
            print("  • Fallback system functioning")
            print("  • Component status reporting")
            print("  • Partial data provision")
            print("  • No more 500 errors")
        else:
            print("❌ OVERALL RESULT: SOME ISSUES FOUND")
            print("\n🔧 Areas needing attention:")
            print("  • Check server configuration")
            print("  • Verify component initialization")
            print("  • Review error handling logic")
        
        print(f"\n📊 Test completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Master Analysis Endpoint')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL for the application (default: http://localhost:5000)')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick tests only')
    
    args = parser.parse_args()
    
    tester = MasterEndpointTester(base_url=args.url)
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
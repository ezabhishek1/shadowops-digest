#!/usr/bin/env python3
"""
Integration test script for ShadowOps Digest API
Tests the complete user workflow from frontend to backend
"""

import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend health check failed: {e}")
        return False

def test_digest_endpoint():
    """Test the main digest endpoint with sample data"""
    sample_data = {
        "tickets": [
            "VPN connection fails on Windows 10",
            "Outlook password reset needed", 
            "Printer not responding in Building A",
            "WiFi connectivity issues in conference room",
            "Password reset for user account",
            "Network printer offline error"
        ],
        "avg_time_per_ticket_minutes": 30,
        "hourly_cost_usd": 40.0
    }
    
    try:
        print("🔄 Testing digest endpoint...")
        response = requests.post(
            f"{API_BASE_URL}/digest",
            json=sample_data,
            timeout=35,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Digest endpoint test passed")
            print(f"   - Clusters: {len(result.get('clusters', {}))}")
            print(f"   - Suggestion: {result.get('suggestion', 'N/A')[:50]}...")
            print(f"   - Time wasted: {result.get('time_wasted_hours', 0)} hours")
            print(f"   - Cost saved: ${result.get('cost_saved_usd', 0)}")
            return True, result
        else:
            print(f"❌ Digest endpoint test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Digest endpoint test failed: {e}")
        return False, None

def test_error_handling():
    """Test API error handling with invalid data"""
    invalid_data = {
        "tickets": [],  # Empty tickets should fail
        "avg_time_per_ticket_minutes": 30,
        "hourly_cost_usd": 40.0
    }
    
    try:
        print("🔄 Testing error handling...")
        response = requests.post(
            f"{API_BASE_URL}/digest",
            json=invalid_data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:
            print("✅ Error handling test passed (validation error returned)")
            return True
        else:
            print(f"❌ Error handling test failed: Expected 422, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_cors_headers():
    """Test CORS configuration for frontend integration"""
    try:
        print("🔄 Testing CORS configuration...")
        response = requests.options(
            f"{API_BASE_URL}/digest",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        cors_headers = response.headers
        if "Access-Control-Allow-Origin" in cors_headers:
            print("✅ CORS configuration test passed")
            print(f"   - Allow Origin: {cors_headers.get('Access-Control-Allow-Origin')}")
            return True
        else:
            print("❌ CORS configuration test failed: Missing CORS headers")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS configuration test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting ShadowOps Digest Integration Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Backend Health
    if test_backend_health():
        tests_passed += 1
    
    # Test 2: Main Digest Endpoint
    success, result = test_digest_endpoint()
    if success:
        tests_passed += 1
    
    # Test 3: Error Handling
    if test_error_handling():
        tests_passed += 1
    
    # Test 4: CORS Configuration
    if test_cors_headers():
        tests_passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All integration tests passed! Frontend-backend integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the backend configuration and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
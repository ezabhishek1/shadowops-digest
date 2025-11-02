#!/usr/bin/env python3
"""
End-to-End Workflow Test for ShadowOps Digest
Simulates complete user interaction from frontend to backend
"""

import requests
import json
import time
import sys

def test_complete_user_journey():
    """Test the complete user journey as it would happen in the frontend"""
    
    print("🚀 Testing Complete User Journey")
    print("=" * 50)
    
    # Step 1: Check if both services are running
    print("1️⃣ Checking service availability...")
    
    # Check backend
    try:
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        if backend_response.status_code == 200:
            print("   ✅ Backend API is running")
        else:
            print("   ❌ Backend API is not responding correctly")
            return False
    except Exception as e:
        print(f"   ❌ Backend API is not accessible: {e}")
        return False
    
    # Check frontend (just check if port is open)
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ Frontend is running")
        else:
            print("   ⚠️  Frontend may not be fully loaded yet")
    except Exception as e:
        print(f"   ⚠️  Frontend check failed (may still be starting): {e}")
    
    # Step 2: Simulate user input data (as it would come from the frontend form)
    print("\n2️⃣ Simulating user input...")
    
    user_input = {
        "tickets": [
            "VPN connection fails when working from home",
            "Outlook keeps asking for password after update", 
            "Printer in meeting room shows offline status",
            "WiFi connection drops frequently in building A",
            "Cannot access shared drive after password reset",
            "Network printer queue is stuck with pending jobs",
            "Email sync issues on mobile after policy change",
            "VPN client crashes on startup with error 800",
            "File server permissions not working for new user",
            "Wireless printer not detected after maintenance"
        ],
        "avg_time_per_ticket_minutes": 35,
        "hourly_cost_usd": 45.0
    }
    
    print(f"   📝 User entered {len(user_input['tickets'])} tickets")
    print(f"   ⏱️  Average time per ticket: {user_input['avg_time_per_ticket_minutes']} minutes")
    print(f"   💰 Hourly cost: ${user_input['hourly_cost_usd']}")
    
    # Step 3: Simulate frontend API call
    print("\n3️⃣ Simulating frontend API call...")
    
    try:
        # This simulates what the useDigest hook does
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/digest",
            json=user_input,
            headers={
                "Content-Type": "application/json",
                "Origin": "http://localhost:3000"  # Simulate frontend origin
            },
            timeout=35
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"   ✅ API call successful ({processing_time:.2f}s)")
            
            # Step 4: Validate response data (as frontend would receive it)
            print("\n4️⃣ Validating response data...")
            
            result = response.json()
            
            # Check required fields
            required_fields = ['clusters', 'suggestion', 'time_wasted_hours', 'cost_saved_usd', 'digest_summary']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                return False
            
            print("   ✅ All required fields present")
            
            # Validate data structure
            clusters = result['clusters']
            if not isinstance(clusters, dict) or len(clusters) == 0:
                print("   ❌ Invalid clusters data")
                return False
            
            print(f"   ✅ Clusters: {len(clusters)} groups created")
            
            # Check if all tickets are assigned
            total_assigned = sum(len(ticket_list) for ticket_list in clusters.values())
            if total_assigned != len(user_input['tickets']):
                print(f"   ⚠️  Warning: {total_assigned}/{len(user_input['tickets'])} tickets assigned")
            else:
                print("   ✅ All tickets properly assigned to clusters")
            
            # Validate business metrics
            if result['time_wasted_hours'] <= 0 or result['cost_saved_usd'] <= 0:
                print("   ❌ Invalid business metrics")
                return False
            
            print("   ✅ Business metrics are valid")
            
            # Step 5: Display results (as frontend would show them)
            print("\n5️⃣ Results that would be displayed to user:")
            print(f"   📊 Executive Summary: {result['digest_summary']}")
            print(f"   🏷️  Clusters Created:")
            
            for i, (cluster_name, ticket_indices) in enumerate(clusters.items(), 1):
                print(f"      {i}. {cluster_name} ({len(ticket_indices)} tickets)")
                print(f"         Tickets: {', '.join(f'#{idx+1}' for idx in ticket_indices)}")
            
            print(f"   💡 Suggestion: {result['suggestion']}")
            print(f"   ⏰ Time Wasted: {result['time_wasted_hours']} hours")
            print(f"   💰 Potential Savings: ${result['cost_saved_usd']}")
            
            # Step 6: Validate CORS headers (important for frontend integration)
            print("\n6️⃣ Validating CORS configuration...")
            
            cors_headers = response.headers
            if 'Access-Control-Allow-Origin' in cors_headers:
                allowed_origin = cors_headers['Access-Control-Allow-Origin']
                if allowed_origin in ['*', 'http://localhost:3000']:
                    print("   ✅ CORS properly configured for frontend")
                else:
                    print(f"   ⚠️  CORS origin: {allowed_origin}")
            else:
                print("   ❌ CORS headers missing")
                return False
            
            print("\n🎉 Complete user journey test PASSED!")
            print("✅ Frontend-backend integration is fully functional")
            return True
            
        else:
            print(f"   ❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        return False

def test_error_scenarios():
    """Test error handling scenarios that users might encounter"""
    
    print("\n🔧 Testing Error Handling Scenarios")
    print("=" * 50)
    
    error_scenarios = [
        {
            "name": "Empty ticket list",
            "data": {
                "tickets": [],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 40.0
            },
            "expected_status": 422
        },
        {
            "name": "Invalid time value",
            "data": {
                "tickets": ["Test ticket"],
                "avg_time_per_ticket_minutes": 0,  # Invalid
                "hourly_cost_usd": 40.0
            },
            "expected_status": 422
        },
        {
            "name": "Invalid cost value", 
            "data": {
                "tickets": ["Test ticket"],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 0.5  # Too low
            },
            "expected_status": 422
        }
    ]
    
    passed = 0
    for scenario in error_scenarios:
        try:
            response = requests.post(
                "http://localhost:8000/digest",
                json=scenario["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == scenario["expected_status"]:
                print(f"   ✅ {scenario['name']}: Proper error handling")
                passed += 1
            else:
                print(f"   ❌ {scenario['name']}: Expected {scenario['expected_status']}, got {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {scenario['name']}: Error - {e}")
    
    return passed == len(error_scenarios)

def main():
    """Run complete integration tests"""
    
    success = True
    
    # Test main user journey
    if not test_complete_user_journey():
        success = False
    
    # Test error scenarios
    if not test_error_scenarios():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ ShadowOps Digest frontend-backend integration is working perfectly")
        print("✅ Users can successfully analyze tickets and receive insights")
        return 0
    else:
        print("❌ Some tests failed")
        print("⚠️  Please check the configuration and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main())
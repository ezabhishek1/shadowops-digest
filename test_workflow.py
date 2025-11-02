#!/usr/bin/env python3
"""
Complete User Workflow Test for ShadowOps Digest
Tests the entire user journey from ticket input to results display
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

class WorkflowTester:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ShadowOps-Workflow-Tester/1.0"
        })
    
    def test_api_health(self) -> bool:
        """Test API health and availability"""
        print("🔍 Testing API health...")
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API is healthy - Status: {health_data.get('status')}")
                return True
            else:
                print(f"❌ API health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API health check failed - Error: {e}")
            return False
    
    def test_input_validation(self) -> bool:
        """Test input validation scenarios"""
        print("🔍 Testing input validation...")
        
        test_cases = [
            {
                "name": "Empty tickets",
                "data": {
                    "tickets": [],
                    "avg_time_per_ticket_minutes": 30,
                    "hourly_cost_usd": 40.0
                },
                "expected_status": 422
            },
            {
                "name": "Invalid time range",
                "data": {
                    "tickets": ["Test ticket"],
                    "avg_time_per_ticket_minutes": 500,  # Too high
                    "hourly_cost_usd": 40.0
                },
                "expected_status": 422
            },
            {
                "name": "Invalid cost range",
                "data": {
                    "tickets": ["Test ticket"],
                    "avg_time_per_ticket_minutes": 30,
                    "hourly_cost_usd": 600.0  # Too high
                },
                "expected_status": 422
            }
        ]
        
        passed = 0
        for test_case in test_cases:
            try:
                response = self.session.post(
                    f"{self.api_url}/digest",
                    json=test_case["data"],
                    timeout=10
                )
                
                if response.status_code == test_case["expected_status"]:
                    print(f"  ✅ {test_case['name']} - Validation working correctly")
                    passed += 1
                else:
                    print(f"  ❌ {test_case['name']} - Expected {test_case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {test_case['name']} - Error: {e}")
        
        return passed == len(test_cases)
    
    def test_complete_workflow(self) -> Dict[str, Any]:
        """Test complete user workflow with realistic data"""
        print("🔍 Testing complete user workflow...")
        
        # Realistic IT support tickets
        sample_tickets = [
            "VPN connection fails when connecting from home office",
            "Outlook keeps asking for password after Windows update",
            "Printer in conference room B shows offline error",
            "WiFi connection drops every 30 minutes in building A",
            "User cannot access shared drive after password change",
            "Network printer queue stuck with multiple jobs",
            "Email sync issues on mobile device after policy update",
            "VPN client crashes on startup with error code 800",
            "Shared folder permissions not working for new employee",
            "Wireless printer not found after network maintenance"
        ]
        
        workflow_data = {
            "tickets": sample_tickets,
            "avg_time_per_ticket_minutes": 35,
            "hourly_cost_usd": 45.0
        }
        
        try:
            print(f"  📤 Sending {len(sample_tickets)} tickets for analysis...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.api_url}/digest",
                json=workflow_data,
                timeout=35
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ['clusters', 'suggestion', 'time_wasted_hours', 'cost_saved_usd', 'digest_summary']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"  ❌ Missing required fields: {missing_fields}")
                    return {"success": False, "error": f"Missing fields: {missing_fields}"}
                
                # Validate data quality
                clusters = result['clusters']
                total_tickets_in_clusters = sum(len(tickets) for tickets in clusters.values())
                
                print(f"  ✅ Workflow completed successfully in {processing_time:.2f} seconds")
                print(f"  📊 Analysis Results:")
                print(f"     - Clusters created: {len(clusters)}")
                print(f"     - Tickets processed: {total_tickets_in_clusters}/{len(sample_tickets)}")
                print(f"     - Time wasted: {result['time_wasted_hours']} hours")
                print(f"     - Potential savings: ${result['cost_saved_usd']}")
                print(f"     - Suggestion: {result['suggestion'][:80]}...")
                
                # Validate cluster assignment
                if total_tickets_in_clusters != len(sample_tickets):
                    print(f"  ⚠️  Warning: Not all tickets were assigned to clusters")
                
                return {
                    "success": True,
                    "result": result,
                    "processing_time": processing_time,
                    "clusters_count": len(clusters),
                    "tickets_processed": total_tickets_in_clusters
                }
                
            else:
                error_msg = f"Request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f": {response.text}"
                
                print(f"  ❌ {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            print(f"  ❌ Workflow test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_error_recovery(self) -> bool:
        """Test error handling and recovery scenarios"""
        print("🔍 Testing error recovery...")
        
        # Test with malformed JSON
        try:
            response = self.session.post(
                f"{self.api_url}/digest",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [400, 422]:
                print("  ✅ Malformed JSON handled correctly")
                return True
            else:
                print(f"  ❌ Malformed JSON not handled properly: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error recovery test failed: {e}")
            return False
    
    def test_performance_limits(self) -> bool:
        """Test performance with edge cases"""
        print("🔍 Testing performance limits...")
        
        # Test with maximum allowed tickets
        max_tickets = ["Test ticket " + str(i) for i in range(100)]  # Reduced for testing
        
        performance_data = {
            "tickets": max_tickets,
            "avg_time_per_ticket_minutes": 30,
            "hourly_cost_usd": 40.0
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.api_url}/digest",
                json=performance_data,
                timeout=35
            )
            end_time = time.time()
            
            if response.status_code == 200:
                processing_time = end_time - start_time
                print(f"  ✅ Performance test passed - {len(max_tickets)} tickets in {processing_time:.2f}s")
                return True
            else:
                print(f"  ❌ Performance test failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Performance test failed: {e}")
            return False

def main():
    """Run comprehensive workflow tests"""
    print("🚀 ShadowOps Digest - Complete Workflow Testing")
    print("=" * 60)
    
    tester = WorkflowTester()
    
    # Test results tracking
    tests = [
        ("API Health", tester.test_api_health),
        ("Input Validation", tester.test_input_validation),
        ("Error Recovery", tester.test_error_recovery),
        ("Performance Limits", tester.test_performance_limits)
    ]
    
    passed_tests = 0
    total_tests = len(tests) + 1  # +1 for workflow test
    
    # Run basic tests
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed_tests += 1
        else:
            print(f"   Test failed - check backend configuration")
    
    # Run complete workflow test
    print(f"\n📋 Complete User Workflow")
    workflow_result = tester.test_complete_workflow()
    if workflow_result["success"]:
        passed_tests += 1
        
        # Additional workflow validation
        result = workflow_result["result"]
        print(f"\n📈 Workflow Quality Metrics:")
        print(f"   - Response time: {workflow_result['processing_time']:.2f}s")
        print(f"   - Clusters created: {workflow_result['clusters_count']}")
        print(f"   - Data completeness: {workflow_result['tickets_processed']}/10 tickets")
        
        # Validate business logic
        if result['time_wasted_hours'] > 0 and result['cost_saved_usd'] > 0:
            print(f"   - Business metrics: ✅ Valid")
        else:
            print(f"   - Business metrics: ⚠️  Check calculation logic")
    
    # Final results
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Frontend-backend integration is fully functional.")
        print("✅ The complete user workflow is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
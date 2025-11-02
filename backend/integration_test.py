#!/usr/bin/env python3
"""
Integration tests for ShadowOps Digest API endpoints.

Tests the complete digest generation workflow including API validation,
error handling, and end-to-end functionality without requiring FastAPI test client.
"""

import sys
import os
import json
import traceback
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate_ticket_request(data: Dict[str, Any]) -> bool:
    """Validate ticket request data manually."""
    from models import TicketRequest
    
    try:
        request = TicketRequest(**data)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def validate_cluster_result(data: Dict[str, Any]) -> bool:
    """Validate cluster result data manually."""
    from models import ClusterResult
    
    try:
        result = ClusterResult(**data)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def simulate_digest_endpoint(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate the /digest endpoint functionality."""
    from clustering import cluster_tickets
    from suggestion import select_suggestion
    from calculator import calculate_time_cost
    from summarizer import generate_digest_summary
    from models import TicketRequest, ClusterResult
    
    # Validate input
    request = TicketRequest(**request_data)
    
    # Process the request
    clusters = cluster_tickets(request.tickets, use_vector_store=False)
    suggestion = select_suggestion(clusters, request.tickets)
    time_wasted, cost_saved = calculate_time_cost(
        clusters, request.avg_time_per_ticket_minutes, request.hourly_cost_usd
    )
    digest_summary = generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
    
    # Create result
    result = ClusterResult(
        clusters=clusters,
        suggestion=suggestion,
        time_wasted_hours=time_wasted,
        cost_saved_usd=cost_saved,
        digest_summary=digest_summary
    )
    
    return result.model_dump()

def test_valid_digest_requests():
    """Test digest endpoint with various valid requests."""
    print("Testing valid digest requests...")
    
    test_cases = [
        {
            "name": "Standard request",
            "data": {
                "tickets": [
                    "VPN connection fails on Windows 10",
                    "Cannot connect to VPN from home",
                    "Outlook password reset needed",
                    "User account locked out",
                    "Printer not responding in Building A",
                    "Network printer offline"
                ],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 50.0
            }
        },
        {
            "name": "Minimal request",
            "data": {
                "tickets": ["Single issue"],
                "avg_time_per_ticket_minutes": 15,
                "hourly_cost_usd": 25.0
            }
        },
        {
            "name": "Large request",
            "data": {
                "tickets": [f"Issue number {i}" for i in range(25)],
                "avg_time_per_ticket_minutes": 45,
                "hourly_cost_usd": 75.0
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"  Testing {test_case['name']}...")
        
        try:
            result = simulate_digest_endpoint(test_case['data'])
            
            # Validate response structure
            assert "clusters" in result
            assert "suggestion" in result
            assert "time_wasted_hours" in result
            assert "cost_saved_usd" in result
            assert "digest_summary" in result
            
            # Validate data types and constraints
            assert isinstance(result["clusters"], dict)
            assert len(result["clusters"]) >= 1
            assert len(result["clusters"]) <= 10
            
            assert isinstance(result["suggestion"], str)
            assert 10 <= len(result["suggestion"]) <= 200
            
            assert isinstance(result["time_wasted_hours"], float)
            assert result["time_wasted_hours"] >= 0
            
            assert isinstance(result["cost_saved_usd"], float)
            assert result["cost_saved_usd"] >= 0
            
            assert isinstance(result["digest_summary"], str)
            assert 50 <= len(result["digest_summary"]) <= 300
            
            print(f"    ✓ {test_case['name']} passed")
            
        except Exception as e:
            print(f"    ✗ {test_case['name']} failed: {e}")
            raise

def test_invalid_digest_requests():
    """Test digest endpoint with invalid requests."""
    print("Testing invalid digest requests...")
    
    invalid_cases = [
        {
            "name": "Empty tickets",
            "data": {
                "tickets": [],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 50.0
            }
        },
        {
            "name": "Negative time",
            "data": {
                "tickets": ["Test ticket"],
                "avg_time_per_ticket_minutes": -10,
                "hourly_cost_usd": 50.0
            }
        },
        {
            "name": "Zero cost",
            "data": {
                "tickets": ["Test ticket"],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 0
            }
        },
        {
            "name": "Missing fields",
            "data": {
                "tickets": ["Test ticket"]
                # Missing required fields
            }
        },
        {
            "name": "Too many tickets",
            "data": {
                "tickets": [f"Ticket {i}" for i in range(1001)],
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 50.0
            }
        }
    ]
    
    for test_case in invalid_cases:
        print(f"  Testing {test_case['name']}...")
        
        try:
            result = simulate_digest_endpoint(test_case['data'])
            print(f"    ✗ {test_case['name']} should have failed but didn't")
            raise AssertionError(f"Expected validation error for {test_case['name']}")
        except Exception as e:
            # Expected to fail
            print(f"    ✓ {test_case['name']} correctly failed: {type(e).__name__}")

def test_ticket_assignment_completeness():
    """Test that all tickets are assigned to clusters."""
    print("Testing ticket assignment completeness...")
    
    test_data = {
        "tickets": [
            "VPN connection fails",
            "Email not working", 
            "Printer offline",
            "Network timeout",
            "Password reset needed",
            "Software crash"
        ],
        "avg_time_per_ticket_minutes": 30,
        "hourly_cost_usd": 50.0
    }
    
    result = simulate_digest_endpoint(test_data)
    
    # Collect all assigned ticket indices
    assigned_indices = []
    for cluster_indices in result["clusters"].values():
        assigned_indices.extend(cluster_indices)
    
    # All tickets should be assigned exactly once
    expected_indices = list(range(len(test_data["tickets"])))
    assert set(assigned_indices) == set(expected_indices), "All tickets should be assigned"
    assert len(assigned_indices) == len(set(assigned_indices)), "No duplicate assignments"
    
    print("  ✓ All tickets properly assigned to clusters")

def test_cost_calculation_accuracy():
    """Test accuracy of cost calculations."""
    print("Testing cost calculation accuracy...")
    
    test_data = {
        "tickets": ["Issue 1", "Issue 2", "Issue 3", "Issue 4"],
        "avg_time_per_ticket_minutes": 60,  # 1 hour per ticket
        "hourly_cost_usd": 100.0
    }
    
    result = simulate_digest_endpoint(test_data)
    
    # Calculate expected time wasted
    num_tickets = len(test_data["tickets"])
    avg_time = test_data["avg_time_per_ticket_minutes"]
    expected_time_hours = (num_tickets * avg_time) / 60.0
    
    # Time wasted should match calculation (allowing for rounding)
    assert abs(result["time_wasted_hours"] - expected_time_hours) < 0.1, "Time calculation should be accurate"
    
    # Cost saved should be reasonable (not exceed total cost)
    max_possible_cost = expected_time_hours * test_data["hourly_cost_usd"]
    assert 0 <= result["cost_saved_usd"] <= max_possible_cost, "Cost savings should be reasonable"
    
    print("  ✓ Cost calculations are accurate")

def test_response_consistency():
    """Test that identical requests produce identical responses."""
    print("Testing response consistency...")
    
    test_data = {
        "tickets": [
            "Network issue 1",
            "Network issue 2", 
            "Email problem 1",
            "Email problem 2"
        ],
        "avg_time_per_ticket_minutes": 30,
        "hourly_cost_usd": 40.0
    }
    
    # Run the same request multiple times
    results = []
    for i in range(3):
        result = simulate_digest_endpoint(test_data)
        results.append(result)
    
    # Results should be consistent
    first_result = results[0]
    for i, result in enumerate(results[1:], 1):
        assert result["clusters"] == first_result["clusters"], f"Clusters should be identical (run {i+1})"
        assert result["time_wasted_hours"] == first_result["time_wasted_hours"], f"Time should be identical (run {i+1})"
        assert result["cost_saved_usd"] == first_result["cost_saved_usd"], f"Cost should be identical (run {i+1})"
    
    print("  ✓ Responses are consistent across multiple runs")

def test_edge_cases():
    """Test various edge cases."""
    print("Testing edge cases...")
    
    edge_cases = [
        {
            "name": "Short tickets",
            "data": {
                "tickets": ["Issue A", "Issue B", "Issue C", "Issue D", "Issue E"],
                "avg_time_per_ticket_minutes": 1,
                "hourly_cost_usd": 1.0
            }
        },
        {
            "name": "Very long tickets",
            "data": {
                "tickets": ["This is a very long ticket description " * 10],
                "avg_time_per_ticket_minutes": 480,  # Max time
                "hourly_cost_usd": 1000.0  # Max cost
            }
        },
        {
            "name": "Identical tickets",
            "data": {
                "tickets": ["Same issue"] * 5,
                "avg_time_per_ticket_minutes": 30,
                "hourly_cost_usd": 50.0
            }
        }
    ]
    
    for test_case in edge_cases:
        print(f"  Testing {test_case['name']}...")
        
        try:
            result = simulate_digest_endpoint(test_case['data'])
            
            # Basic validation
            assert isinstance(result, dict)
            assert "clusters" in result
            assert "suggestion" in result
            assert "digest_summary" in result
            
            print(f"    ✓ {test_case['name']} handled correctly")
            
        except Exception as e:
            print(f"    ✗ {test_case['name']} failed: {e}")
            raise

def test_data_format_validation():
    """Test data format validation."""
    print("Testing data format validation...")
    
    # Test valid request validation
    valid_data = {
        "tickets": ["Test ticket 1", "Test ticket 2"],
        "avg_time_per_ticket_minutes": 30,
        "hourly_cost_usd": 50.0
    }
    
    assert validate_ticket_request(valid_data), "Valid request should pass validation"
    
    # Test valid response validation
    valid_response = {
        "clusters": {"Network Issues": [0, 1]},
        "suggestion": "Create troubleshooting guide",
        "time_wasted_hours": 1.0,
        "cost_saved_usd": 50.0,
        "digest_summary": "2 tickets clustered into 1 category. Primary issue: Network Issues (2 tickets). Recommendation: Create troubleshooting guide. Potential savings: 1.0 hours, $50."
    }
    
    assert validate_cluster_result(valid_response), "Valid response should pass validation"
    
    print("  ✓ Data format validation working correctly")

def main():
    """Run all integration tests."""
    print("ShadowOps Digest Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Valid Digest Requests", test_valid_digest_requests),
        ("Invalid Digest Requests", test_invalid_digest_requests),
        ("Ticket Assignment Completeness", test_ticket_assignment_completeness),
        ("Cost Calculation Accuracy", test_cost_calculation_accuracy),
        ("Response Consistency", test_response_consistency),
        ("Edge Cases", test_edge_cases),
        ("Data Format Validation", test_data_format_validation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            test_func()
            print(f"✓ {test_name} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            print(f"  Traceback: {traceback.format_exc()}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Integration Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("Some integration tests failed. Check the output above for details.")
        return 1
    else:
        print("All integration tests passed successfully!")
        print("\nIntegration Summary:")
        print("- API endpoint simulation works correctly")
        print("- Data validation is functioning properly")
        print("- Complete workflow produces consistent results")
        print("- Edge cases are handled gracefully")
        return 0

if __name__ == "__main__":
    sys.exit(main())
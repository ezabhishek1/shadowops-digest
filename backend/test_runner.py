#!/usr/bin/env python3
"""
Simple test runner for ShadowOps Digest backend tests.

This script runs basic functionality tests without requiring pytest,
focusing on core module functionality and integration testing.
"""

import sys
import os
import traceback
from typing import Dict, List, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_test(test_name: str, test_func) -> bool:
    """Run a single test function and report results."""
    try:
        print(f"Running {test_name}...", end=" ")
        test_func()
        print("✓ PASSED")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print(f"  Traceback: {traceback.format_exc()}")
        return False

def test_clustering_basic():
    """Test basic clustering functionality."""
    from clustering import cluster_tickets
    
    tickets = [
        "VPN connection fails on Windows 10",
        "Cannot connect to VPN from home",
        "Outlook password reset needed",
        "User account locked out"
    ]
    
    result = cluster_tickets(tickets, use_vector_store=False)
    
    assert isinstance(result, dict), "Result should be a dictionary"
    assert len(result) >= 1, "Should have at least one cluster"
    assert len(result) <= 10, "Should have at most 10 clusters"
    
    # Check all tickets are assigned
    all_indices = []
    for indices in result.values():
        all_indices.extend(indices)
    assert set(all_indices) == set(range(len(tickets))), "All tickets should be assigned"

def test_suggestion_basic():
    """Test basic suggestion generation."""
    from suggestion import select_suggestion
    
    clusters = {
        "Network Issues": [0, 1, 2],
        "Authentication Problems": [3, 4]
    }
    tickets = [
        "VPN connection failed",
        "Network timeout",
        "WiFi issues",
        "Password reset needed",
        "Account locked"
    ]
    
    result = select_suggestion(clusters, tickets)
    
    assert isinstance(result, str), "Result should be a string"
    assert 10 <= len(result) <= 200, f"Suggestion length {len(result)} should be 10-200 chars"

def test_calculator_basic():
    """Test basic cost calculation."""
    from calculator import calculate_time_cost
    
    clusters = {
        "Network Issues": [0, 1, 2],
        "Email Problems": [3, 4]
    }
    
    time_wasted, cost_saved = calculate_time_cost(clusters, 30, 50.0)
    
    assert isinstance(time_wasted, float), "Time wasted should be float"
    assert isinstance(cost_saved, float), "Cost saved should be float"
    assert time_wasted >= 0, "Time wasted should be non-negative"
    assert cost_saved >= 0, "Cost saved should be non-negative"

def test_summarizer_basic():
    """Test basic summarizer functionality."""
    from summarizer import generate_digest_summary
    
    clusters = {
        "Network Issues": [0, 1, 2],
        "Email Problems": [3, 4]
    }
    suggestion = "Create network troubleshooting guide"
    
    result = generate_digest_summary(clusters, suggestion, 2.5, 125.0)
    
    assert isinstance(result, str), "Result should be a string"
    assert 50 <= len(result) <= 300, f"Summary length {len(result)} should be 50-300 chars"
    assert "5 tickets" in result, "Should mention ticket count"
    assert "2 categories" in result or "2 categor" in result, "Should mention cluster count"

def test_models_validation():
    """Test Pydantic model validation."""
    from models import TicketRequest, ClusterResult
    
    # Test valid ticket request
    valid_request = TicketRequest(
        tickets=["Test ticket 1", "Test ticket 2"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    assert len(valid_request.tickets) == 2
    
    # Test valid cluster result
    valid_result = ClusterResult(
        clusters={"Network Issues": [0, 1]},
        suggestion="Create troubleshooting guide",
        time_wasted_hours=1.0,
        cost_saved_usd=50.0,
        digest_summary="2 tickets clustered into 1 category. Primary issue: Network Issues (2 tickets). Recommendation: Create troubleshooting guide. Potential savings: 1.0 hours, $50."
    )
    assert valid_result.time_wasted_hours == 1.0

def test_integration_workflow():
    """Test complete workflow integration."""
    from clustering import cluster_tickets
    from suggestion import select_suggestion
    from calculator import calculate_time_cost
    from summarizer import generate_digest_summary
    
    # Sample data
    tickets = [
        "VPN connection fails",
        "Network timeout issues",
        "Email not syncing",
        "Outlook crashes",
        "Printer not working"
    ]
    avg_time = 30
    hourly_cost = 40.0
    
    # Run complete workflow
    clusters = cluster_tickets(tickets, use_vector_store=False)
    suggestion = select_suggestion(clusters, tickets)
    time_wasted, cost_saved = calculate_time_cost(clusters, avg_time, hourly_cost)
    summary = generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
    
    # Validate results
    assert isinstance(clusters, dict)
    assert isinstance(suggestion, str)
    assert isinstance(time_wasted, float)
    assert isinstance(cost_saved, float)
    assert isinstance(summary, str)
    
    # Check workflow consistency
    total_tickets = sum(len(indices) for indices in clusters.values())
    assert total_tickets == len(tickets), "All tickets should be clustered"
    assert 50 <= len(summary) <= 300, "Summary should meet length requirements"

def main():
    """Run all tests and report results."""
    print("ShadowOps Digest Backend Test Runner")
    print("=" * 40)
    
    tests = [
        ("Clustering Basic", test_clustering_basic),
        ("Suggestion Basic", test_suggestion_basic),
        ("Calculator Basic", test_calculator_basic),
        ("Summarizer Basic", test_summarizer_basic),
        ("Models Validation", test_models_validation),
        ("Integration Workflow", test_integration_workflow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("Some tests failed. Check the output above for details.")
        return 1
    else:
        print("All tests passed successfully!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
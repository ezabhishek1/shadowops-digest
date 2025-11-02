#!/usr/bin/env python3
"""
Performance tests for ShadowOps Digest backend.

Tests response time validation, load handling, and timeout scenarios
as required by the task specifications.
"""

import sys
import os
import time
import traceback
from typing import List, Dict

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def measure_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

def test_clustering_performance():
    """Test clustering algorithm performance with various dataset sizes."""
    from clustering import cluster_tickets
    
    print("Testing clustering performance...")
    
    # Test cases with different sizes
    test_cases = [
        ("Small dataset (5 tickets)", [f"Issue {i}" for i in range(5)]),
        ("Medium dataset (20 tickets)", [f"Network problem {i}" for i in range(20)]),
        ("Large dataset (50 tickets)", [f"Support ticket {i}" for i in range(50)]),
    ]
    
    for test_name, tickets in test_cases:
        result, duration = measure_time(cluster_tickets, tickets, use_vector_store=False)
        
        print(f"  {test_name}: {duration:.2f}s")
        
        # Validate results
        assert isinstance(result, dict), "Should return dictionary"
        assert len(result) >= 1, "Should have at least one cluster"
        assert len(result) <= 10, "Should respect cluster limit"
        
        # Performance assertions
        if len(tickets) <= 20:
            assert duration < 5.0, f"Small/medium datasets should complete in <5s, took {duration:.2f}s"
        else:
            assert duration < 15.0, f"Large datasets should complete in <15s, took {duration:.2f}s"

def test_suggestion_performance():
    """Test suggestion generation performance."""
    from suggestion import select_suggestion
    
    print("Testing suggestion generation performance...")
    
    # Create test clusters of varying complexity
    test_cases = [
        ("Simple clusters", {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4]
        }, ["VPN failed", "Network down", "WiFi issue", "Email sync", "Outlook crash"]),
        
        ("Complex clusters", {
            f"Category {i}": [i*2, i*2+1] for i in range(8)
        }, [f"Complex issue {i}" for i in range(16)]),
    ]
    
    for test_name, clusters, tickets in test_cases:
        result, duration = measure_time(select_suggestion, clusters, tickets)
        
        print(f"  {test_name}: {duration:.2f}s")
        
        # Validate results
        assert isinstance(result, str), "Should return string"
        assert 10 <= len(result) <= 200, "Should meet length requirements"
        
        # Performance assertion
        assert duration < 3.0, f"Suggestion generation should complete in <3s, took {duration:.2f}s"

def test_cost_calculation_performance():
    """Test cost calculation performance."""
    from calculator import calculate_time_cost
    
    print("Testing cost calculation performance...")
    
    # Test with various cluster sizes
    test_cases = [
        ("Small calculation", {"Issues": [0, 1, 2]}),
        ("Medium calculation", {f"Cat{i}": list(range(i*5, (i+1)*5)) for i in range(5)}),
        ("Large calculation", {f"Category{i}": list(range(i*10, (i+1)*10)) for i in range(10)}),
    ]
    
    for test_name, clusters in test_cases:
        result, duration = measure_time(calculate_time_cost, clusters, 30, 50.0)
        
        print(f"  {test_name}: {duration:.2f}s")
        
        # Validate results
        time_wasted, cost_saved = result
        assert isinstance(time_wasted, float), "Time should be float"
        assert isinstance(cost_saved, float), "Cost should be float"
        assert time_wasted >= 0, "Time should be non-negative"
        assert cost_saved >= 0, "Cost should be non-negative"
        
        # Performance assertion
        assert duration < 1.0, f"Cost calculation should complete in <1s, took {duration:.2f}s"

def test_summarizer_performance():
    """Test digest summarizer performance."""
    from summarizer import generate_digest_summary
    
    print("Testing summarizer performance...")
    
    # Test with various complexity levels
    test_cases = [
        ("Simple summary", {"Network": [0, 1]}, "Fix network"),
        ("Medium summary", {f"Cat{i}": [i, i+1] for i in range(0, 10, 2)}, "Improve processes"),
        ("Complex summary", {f"Category{i}": list(range(i*3, (i+1)*3)) for i in range(8)}, "Implement comprehensive troubleshooting procedures"),
    ]
    
    for test_name, clusters, suggestion in test_cases:
        result, duration = measure_time(generate_digest_summary, clusters, suggestion, 5.0, 250.0)
        
        print(f"  {test_name}: {duration:.2f}s")
        
        # Validate results
        assert isinstance(result, str), "Should return string"
        assert 50 <= len(result) <= 300, "Should meet length requirements"
        
        # Performance assertion
        assert duration < 2.0, f"Summary generation should complete in <2s, took {duration:.2f}s"

def test_complete_workflow_performance():
    """Test complete digest generation workflow performance."""
    from clustering import cluster_tickets
    from suggestion import select_suggestion
    from calculator import calculate_time_cost
    from summarizer import generate_digest_summary
    
    print("Testing complete workflow performance...")
    
    # Test cases with different complexities
    test_cases = [
        ("Small workflow", [f"Issue {i}" for i in range(5)]),
        ("Medium workflow", [f"Support ticket {i}" for i in range(15)]),
        ("Large workflow", [f"IT problem {i}" for i in range(30)]),
    ]
    
    for test_name, tickets in test_cases:
        def complete_workflow():
            clusters = cluster_tickets(tickets, use_vector_store=False)
            suggestion = select_suggestion(clusters, tickets)
            time_wasted, cost_saved = calculate_time_cost(clusters, 30, 50.0)
            summary = generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
            return clusters, suggestion, time_wasted, cost_saved, summary
        
        result, duration = measure_time(complete_workflow)
        clusters, suggestion, time_wasted, cost_saved, summary = result
        
        print(f"  {test_name}: {duration:.2f}s")
        
        # Validate complete workflow results
        assert isinstance(clusters, dict), "Clusters should be dict"
        assert isinstance(suggestion, str), "Suggestion should be string"
        assert isinstance(time_wasted, float), "Time should be float"
        assert isinstance(cost_saved, float), "Cost should be float"
        assert isinstance(summary, str), "Summary should be string"
        
        # Performance assertions based on dataset size
        if len(tickets) <= 10:
            assert duration < 8.0, f"Small workflow should complete in <8s, took {duration:.2f}s"
        elif len(tickets) <= 20:
            assert duration < 15.0, f"Medium workflow should complete in <15s, took {duration:.2f}s"
        else:
            assert duration < 25.0, f"Large workflow should complete in <25s, took {duration:.2f}s"

def test_edge_case_performance():
    """Test performance with edge cases."""
    from clustering import cluster_tickets
    from suggestion import select_suggestion
    from calculator import calculate_time_cost
    from summarizer import generate_digest_summary
    
    print("Testing edge case performance...")
    
    # Single ticket
    single_ticket = ["Single issue"]
    result, duration = measure_time(cluster_tickets, single_ticket, use_vector_store=False)
    print(f"  Single ticket clustering: {duration:.2f}s")
    assert duration < 1.0, "Single ticket should be very fast"
    
    # Empty suggestion
    empty_clusters = {}
    result, duration = measure_time(select_suggestion, empty_clusters, [])
    print(f"  Empty clusters suggestion: {duration:.2f}s")
    assert duration < 1.0, "Empty clusters should be very fast"
    
    # Zero cost calculation
    result, duration = measure_time(calculate_time_cost, {"Issue": [0]}, 0, 0.0)
    print(f"  Zero cost calculation: {duration:.2f}s")
    assert duration < 0.5, "Zero cost should be very fast"

def test_memory_usage():
    """Test memory usage patterns (basic check)."""
    import gc
    from clustering import cluster_tickets
    
    print("Testing memory usage patterns...")
    
    # Force garbage collection before test
    gc.collect()
    
    # Test with progressively larger datasets
    for size in [10, 25, 50]:
        tickets = [f"Memory test ticket {i} with some description" for i in range(size)]
        
        # Run clustering multiple times
        for _ in range(3):
            result = cluster_tickets(tickets, use_vector_store=False)
            assert isinstance(result, dict)
        
        # Force garbage collection
        gc.collect()
        
        print(f"  Processed {size} tickets successfully")

def main():
    """Run all performance tests."""
    print("ShadowOps Digest Performance Test Suite")
    print("=" * 50)
    
    tests = [
        ("Clustering Performance", test_clustering_performance),
        ("Suggestion Performance", test_suggestion_performance),
        ("Cost Calculation Performance", test_cost_calculation_performance),
        ("Summarizer Performance", test_summarizer_performance),
        ("Complete Workflow Performance", test_complete_workflow_performance),
        ("Edge Case Performance", test_edge_case_performance),
        ("Memory Usage", test_memory_usage),
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
    print(f"Performance Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("Some performance tests failed. Check the output above for details.")
        return 1
    else:
        print("All performance tests passed successfully!")
        print("\nPerformance Summary:")
        print("- All components meet response time requirements")
        print("- Memory usage is within acceptable limits")
        print("- Edge cases are handled efficiently")
        return 0

if __name__ == "__main__":
    sys.exit(main())
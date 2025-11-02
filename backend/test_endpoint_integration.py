#!/usr/bin/env python3
"""
Integration test for the POST /digest endpoint.

This script tests the complete endpoint functionality including
request validation, processing pipeline, caching, and error handling.
"""

import sys
import os
import asyncio
from unittest.mock import Mock

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_digest_endpoint_success():
    """Test successful digest generation."""
    from main import generate_digest
    from models import TicketRequest
    
    # Create test request
    request = TicketRequest(
        tickets=[
            "VPN connection fails on Windows 10",
            "Cannot connect to VPN from home",
            "Outlook password reset needed",
            "User account locked out"
        ],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    # Mock FastAPI Request object
    mock_req = Mock()
    mock_req.state.correlation_id = "test-123"
    
    # Call the endpoint
    result = await generate_digest(request, mock_req)
    
    # Validate response
    assert hasattr(result, 'clusters'), "Result should have clusters"
    assert hasattr(result, 'suggestion'), "Result should have suggestion"
    assert hasattr(result, 'time_wasted_hours'), "Result should have time_wasted_hours"
    assert hasattr(result, 'cost_saved_usd'), "Result should have cost_saved_usd"
    assert hasattr(result, 'digest_summary'), "Result should have digest_summary"
    
    # Validate data types and ranges
    assert isinstance(result.clusters, dict), "Clusters should be a dictionary"
    assert isinstance(result.suggestion, str), "Suggestion should be a string"
    assert isinstance(result.time_wasted_hours, float), "Time wasted should be a float"
    assert isinstance(result.cost_saved_usd, float), "Cost saved should be a float"
    assert isinstance(result.digest_summary, str), "Digest summary should be a string"
    
    # Validate business logic
    assert len(result.clusters) >= 1, "Should have at least one cluster"
    assert len(result.clusters) <= 10, "Should have at most 10 clusters"
    assert 10 <= len(result.suggestion) <= 200, "Suggestion should be 10-200 characters"
    assert 50 <= len(result.digest_summary) <= 300, "Summary should be 50-300 characters"
    assert result.time_wasted_hours >= 0, "Time wasted should be non-negative"
    assert result.cost_saved_usd >= 0, "Cost saved should be non-negative"
    
    # Validate all tickets are assigned
    all_indices = []
    for indices in result.clusters.values():
        all_indices.extend(indices)
    assert set(all_indices) == set(range(len(request.tickets))), "All tickets should be assigned"
    
    print("✓ Digest endpoint success test passed")
    return result

async def test_digest_endpoint_caching():
    """Test caching functionality of the digest endpoint."""
    from main import generate_digest, digest_cache
    from models import TicketRequest
    
    # Clear cache first
    digest_cache.clear()
    
    # Create test request
    request = TicketRequest(
        tickets=["Test caching ticket"],
        avg_time_per_ticket_minutes=15,
        hourly_cost_usd=40.0
    )
    
    # Mock FastAPI Request object
    mock_req = Mock()
    mock_req.state.correlation_id = "cache-test-123"
    
    # First call - should process and cache
    result1 = await generate_digest(request, mock_req)
    cache_size_after_first = len(digest_cache)
    
    # Second call - should use cache
    result2 = await generate_digest(request, mock_req)
    cache_size_after_second = len(digest_cache)
    
    # Validate caching behavior
    assert cache_size_after_first == 1, "Cache should have one entry after first call"
    assert cache_size_after_second == 1, "Cache size should remain same after second call"
    
    # Results should be identical
    assert result1.clusters == result2.clusters, "Cached clusters should match"
    assert result1.suggestion == result2.suggestion, "Cached suggestion should match"
    assert result1.time_wasted_hours == result2.time_wasted_hours, "Cached time should match"
    assert result1.cost_saved_usd == result2.cost_saved_usd, "Cached cost should match"
    assert result1.digest_summary == result2.digest_summary, "Cached summary should match"
    
    print("✓ Digest endpoint caching test passed")

async def test_digest_endpoint_validation():
    """Test request validation in the digest endpoint."""
    from main import app
    from models import TicketRequest
    from pydantic import ValidationError
    
    # Test invalid ticket request (empty tickets)
    try:
        invalid_request = TicketRequest(
            tickets=[],  # Empty tickets should fail
            avg_time_per_ticket_minutes=30,
            hourly_cost_usd=50.0
        )
        assert False, "Should have raised ValidationError for empty tickets"
    except ValidationError:
        pass  # Expected
    
    # Test invalid time (too high)
    try:
        invalid_request = TicketRequest(
            tickets=["Test ticket"],
            avg_time_per_ticket_minutes=500,  # Too high
            hourly_cost_usd=50.0
        )
        assert False, "Should have raised ValidationError for invalid time"
    except ValidationError:
        pass  # Expected
    
    # Test invalid cost (negative)
    try:
        invalid_request = TicketRequest(
            tickets=["Test ticket"],
            avg_time_per_ticket_minutes=30,
            hourly_cost_usd=-10.0  # Negative cost
        )
        assert False, "Should have raised ValidationError for negative cost"
    except ValidationError:
        pass  # Expected
    
    print("✓ Digest endpoint validation test passed")

async def test_cache_status_endpoint():
    """Test the cache status endpoint."""
    from main import cache_status, digest_cache
    
    # Clear cache and add test entry
    digest_cache.clear()
    digest_cache["test_key"] = {
        "result": {"test": "data"},
        "timestamp": "2023-01-01T00:00:00"
    }
    
    # Call cache status endpoint
    status = await cache_status()
    
    # Validate response
    assert isinstance(status, dict), "Status should be a dictionary"
    assert "cache_entries" in status, "Should include cache_entries"
    assert "cache_ttl_minutes" in status, "Should include cache_ttl_minutes"
    assert "timestamp" in status, "Should include timestamp"
    
    assert isinstance(status["cache_entries"], int), "Cache entries should be integer"
    assert status["cache_entries"] >= 0, "Cache entries should be non-negative"
    
    print("✓ Cache status endpoint test passed")

async def main():
    """Run all integration tests."""
    print("ShadowOps Digest Endpoint Integration Tests")
    print("=" * 50)
    
    try:
        # Run tests
        await test_digest_endpoint_success()
        await test_digest_endpoint_caching()
        await test_digest_endpoint_validation()
        await test_cache_status_endpoint()
        
        print("\n" + "=" * 50)
        print("All endpoint integration tests passed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
#!/usr/bin/env python3
"""
Test script for verifying the caching functionality in the digest endpoint.

This script tests the cache key generation, cache storage/retrieval,
and cache expiration functionality.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cache_key_generation():
    """Test cache key generation for consistent hashing."""
    from main import generate_cache_key
    from models import TicketRequest
    
    # Create identical requests
    request1 = TicketRequest(
        tickets=["VPN issue", "Email problem"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    request2 = TicketRequest(
        tickets=["VPN issue", "Email problem"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    # Different order should produce same key (sorted)
    request3 = TicketRequest(
        tickets=["Email problem", "VPN issue"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    # Different content should produce different key
    request4 = TicketRequest(
        tickets=["VPN issue", "Email problem"],
        avg_time_per_ticket_minutes=45,  # Different time
        hourly_cost_usd=50.0
    )
    
    key1 = generate_cache_key(request1)
    key2 = generate_cache_key(request2)
    key3 = generate_cache_key(request3)
    key4 = generate_cache_key(request4)
    
    assert key1 == key2, "Identical requests should have same cache key"
    assert key1 == key3, "Different order should produce same cache key"
    assert key1 != key4, "Different parameters should produce different cache key"
    
    print("✓ Cache key generation works correctly")

def test_cache_storage_retrieval():
    """Test cache storage and retrieval functionality."""
    from main import cache_result, get_cached_result, generate_cache_key
    from models import TicketRequest, ClusterResult
    
    # Create test data
    request = TicketRequest(
        tickets=["Test ticket"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    result = ClusterResult(
        clusters={"Test Issues": [0]},
        suggestion="Create test guide",
        time_wasted_hours=0.5,
        cost_saved_usd=25.0,
        digest_summary="1 ticket clustered into 1 category. Primary issue: Test Issues (1 ticket). Recommendation: Create test guide. Potential savings: 0.5 hours, $25."
    )
    
    cache_key = generate_cache_key(request)
    
    # Test cache miss
    cached = get_cached_result(cache_key)
    assert cached is None, "Should return None for cache miss"
    
    # Test cache storage
    cache_result(cache_key, result)
    
    # Test cache hit
    cached = get_cached_result(cache_key)
    assert cached is not None, "Should return cached result"
    assert cached.clusters == result.clusters, "Cached clusters should match"
    assert cached.suggestion == result.suggestion, "Cached suggestion should match"
    assert cached.time_wasted_hours == result.time_wasted_hours, "Cached time should match"
    assert cached.cost_saved_usd == result.cost_saved_usd, "Cached cost should match"
    
    print("✓ Cache storage and retrieval works correctly")

def test_cache_expiration():
    """Test cache expiration functionality."""
    from main import cache_result, get_cached_result, generate_cache_key, digest_cache, CACHE_TTL_MINUTES
    from models import TicketRequest, ClusterResult
    
    # Create test data
    request = TicketRequest(
        tickets=["Expiration test"],
        avg_time_per_ticket_minutes=30,
        hourly_cost_usd=50.0
    )
    
    result = ClusterResult(
        clusters={"Test Issues": [0]},
        suggestion="Create test guide",
        time_wasted_hours=0.5,
        cost_saved_usd=25.0,
        digest_summary="1 ticket clustered into 1 category. Primary issue: Test Issues (1 ticket). Recommendation: Create test guide. Potential savings: 0.5 hours, $25."
    )
    
    cache_key = generate_cache_key(request)
    
    # Store result in cache
    cache_result(cache_key, result)
    
    # Verify it's cached
    cached = get_cached_result(cache_key)
    assert cached is not None, "Should be cached initially"
    
    # Manually expire the cache entry by setting old timestamp
    if cache_key in digest_cache:
        digest_cache[cache_key]["timestamp"] = datetime.utcnow() - timedelta(minutes=CACHE_TTL_MINUTES + 1)
    
    # Test expired cache
    cached = get_cached_result(cache_key)
    assert cached is None, "Should return None for expired cache"
    assert cache_key not in digest_cache, "Expired entry should be removed"
    
    print("✓ Cache expiration works correctly")

def test_cache_cleanup():
    """Test cache cleanup functionality."""
    from main import cleanup_expired_cache, digest_cache, CACHE_TTL_MINUTES
    
    # Add some test entries with different timestamps
    test_entries = {
        "fresh_key": {
            "result": {"test": "data1"},
            "timestamp": datetime.utcnow()  # Fresh entry
        },
        "expired_key": {
            "result": {"test": "data2"},
            "timestamp": datetime.utcnow() - timedelta(minutes=CACHE_TTL_MINUTES + 1)  # Expired
        },
        "another_fresh_key": {
            "result": {"test": "data3"},
            "timestamp": datetime.utcnow() - timedelta(minutes=5)  # Still fresh
        }
    }
    
    # Add entries to cache
    for key, entry in test_entries.items():
        digest_cache[key] = entry
    
    # Run cleanup
    cleanup_expired_cache()
    
    # Check results
    assert "fresh_key" in digest_cache, "Fresh entry should remain"
    assert "another_fresh_key" in digest_cache, "Another fresh entry should remain"
    assert "expired_key" not in digest_cache, "Expired entry should be removed"
    
    # Clean up test entries
    for key in ["fresh_key", "another_fresh_key"]:
        if key in digest_cache:
            del digest_cache[key]
    
    print("✓ Cache cleanup works correctly")

def main():
    """Run all caching tests."""
    print("ShadowOps Digest Caching Test Suite")
    print("=" * 40)
    
    try:
        test_cache_key_generation()
        test_cache_storage_retrieval()
        test_cache_expiration()
        test_cache_cleanup()
        
        print("\n" + "=" * 40)
        print("All caching tests passed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
Integration tests for complete digest generation workflow.

Tests the end-to-end process from ticket input to final digest output,
including API endpoint integration and performance validation.
"""

import pytest
import asyncio
import os
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import TicketRequest, ClusterResult


class TestDigestWorkflowIntegration:
    """Integration tests for complete digest generation workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        
        self.valid_request = {
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
        
        self.minimal_request = {
            "tickets": ["Single issue"],
            "avg_time_per_ticket_minutes": 15,
            "hourly_cost_usd": 25.0
        }
        
        self.large_request = {
            "tickets": [f"Issue number {i}" for i in range(50)],
            "avg_time_per_ticket_minutes": 45,
            "hourly_cost_usd": 75.0
        }
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_digest_endpoint_valid_request(self):
        """Test digest endpoint with valid request."""
        response = self.client.post("/digest", json=self.valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "clusters" in data
        assert "suggestion" in data
        assert "time_wasted_hours" in data
        assert "cost_saved_usd" in data
        assert "digest_summary" in data
        
        # Validate data types and constraints
        assert isinstance(data["clusters"], dict)
        assert len(data["clusters"]) >= 1
        assert len(data["clusters"]) <= 10
        
        assert isinstance(data["suggestion"], str)
        assert 10 <= len(data["suggestion"]) <= 200
        
        assert isinstance(data["time_wasted_hours"], float)
        assert data["time_wasted_hours"] >= 0
        
        assert isinstance(data["cost_saved_usd"], float)
        assert data["cost_saved_usd"] >= 0
        
        assert isinstance(data["digest_summary"], str)
        assert 50 <= len(data["digest_summary"]) <= 300
    
    def test_digest_endpoint_minimal_request(self):
        """Test digest endpoint with minimal valid request."""
        response = self.client.post("/digest", json=self.minimal_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle single ticket gracefully
        assert len(data["clusters"]) >= 1
        assert data["time_wasted_hours"] > 0
    
    def test_digest_endpoint_large_request(self):
        """Test digest endpoint with large request."""
        response = self.client.post("/digest", json=self.large_request)
        
        # Should either succeed or timeout gracefully
        assert response.status_code in [200, 408]  # Success or timeout
        
        if response.status_code == 200:
            data = response.json()
            assert len(data["clusters"]) <= 10  # Cluster limit enforced
    
    def test_digest_endpoint_invalid_requests(self):
        """Test digest endpoint with various invalid requests."""
        # Empty tickets
        invalid_request = self.valid_request.copy()
        invalid_request["tickets"] = []
        response = self.client.post("/digest", json=invalid_request)
        assert response.status_code == 422
        
        # Negative time
        invalid_request = self.valid_request.copy()
        invalid_request["avg_time_per_ticket_minutes"] = -10
        response = self.client.post("/digest", json=invalid_request)
        assert response.status_code == 422
        
        # Zero cost
        invalid_request = self.valid_request.copy()
        invalid_request["hourly_cost_usd"] = 0
        response = self.client.post("/digest", json=invalid_request)
        assert response.status_code == 422
        
        # Missing fields
        incomplete_request = {"tickets": ["Test"]}
        response = self.client.post("/digest", json=incomplete_request)
        assert response.status_code == 422
    
    def test_digest_workflow_consistency(self):
        """Test that digest workflow produces consistent results."""
        # Run the same request multiple times
        responses = []
        for _ in range(3):
            response = self.client.post("/digest", json=self.valid_request)
            assert response.status_code == 200
            responses.append(response.json())
        
        # Results should be consistent (same input, same output)
        first_response = responses[0]
        for response in responses[1:]:
            # Clusters should be identical
            assert response["clusters"] == first_response["clusters"]
            
            # Metrics should be identical
            assert response["time_wasted_hours"] == first_response["time_wasted_hours"]
            assert response["cost_saved_usd"] == first_response["cost_saved_usd"]
    
    def test_correlation_id_tracking(self):
        """Test that correlation IDs are properly tracked."""
        response = self.client.post("/digest", json=self.valid_request)
        
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) > 0
    
    def test_error_handling_integration(self):
        """Test error handling in integration scenarios."""
        # Test with malformed JSON
        response = self.client.post("/digest", data="invalid json")
        assert response.status_code == 422
        
        # Test with wrong content type
        response = self.client.post("/digest", data=self.valid_request)
        assert response.status_code == 422
    
    @patch('main.cluster_tickets')
    def test_clustering_failure_handling(self, mock_cluster):
        """Test handling of clustering failures."""
        # Mock clustering to raise an exception
        mock_cluster.side_effect = Exception("Clustering failed")
        
        response = self.client.post("/digest", json=self.valid_request)
        assert response.status_code == 500
        
        data = response.json()
        assert "error" in data
        assert "correlation_id" in data.get("details", {})
    
    @patch('main.select_suggestion')
    def test_suggestion_failure_handling(self, mock_suggestion):
        """Test handling of suggestion generation failures."""
        # Mock suggestion generation to raise an exception
        mock_suggestion.side_effect = Exception("Suggestion failed")
        
        response = self.client.post("/digest", json=self.valid_request)
        assert response.status_code == 500
    
    def test_ticket_assignment_completeness(self):
        """Test that all tickets are assigned to clusters."""
        response = self.client.post("/digest", json=self.valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Collect all assigned ticket indices
        assigned_indices = []
        for cluster_indices in data["clusters"].values():
            assigned_indices.extend(cluster_indices)
        
        # All tickets should be assigned exactly once
        expected_indices = list(range(len(self.valid_request["tickets"])))
        assert set(assigned_indices) == set(expected_indices)
        assert len(assigned_indices) == len(set(assigned_indices))  # No duplicates
    
    def test_cost_calculation_accuracy(self):
        """Test accuracy of cost calculations."""
        response = self.client.post("/digest", json=self.valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Calculate expected time wasted
        num_tickets = len(self.valid_request["tickets"])
        avg_time = self.valid_request["avg_time_per_ticket_minutes"]
        expected_time_hours = (num_tickets * avg_time) / 60.0
        
        # Time wasted should match calculation (rounded to 1 decimal)
        assert abs(data["time_wasted_hours"] - round(expected_time_hours, 1)) < 0.1
        
        # Cost saved should be reasonable (not exceed total cost)
        max_possible_cost = expected_time_hours * self.valid_request["hourly_cost_usd"]
        assert 0 <= data["cost_saved_usd"] <= max_possible_cost


class TestPerformanceValidation:
    """Performance tests for digest generation."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.client = TestClient(app)
    
    def test_response_time_small_dataset(self):
        """Test response time for small dataset."""
        request_data = {
            "tickets": ["Issue 1", "Issue 2", "Issue 3"],
            "avg_time_per_ticket_minutes": 30,
            "hourly_cost_usd": 50.0
        }
        
        import time
        start_time = time.time()
        response = self.client.post("/digest", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should complete within reasonable time (less than 10 seconds for small dataset)
        response_time = end_time - start_time
        assert response_time < 10.0
    
    def test_timeout_handling(self):
        """Test timeout handling for large datasets."""
        # Create a very large request that might timeout
        large_request = {
            "tickets": [f"Complex issue description number {i} with lots of details" for i in range(100)],
            "avg_time_per_ticket_minutes": 60,
            "hourly_cost_usd": 100.0
        }
        
        response = self.client.post("/digest", json=large_request)
        
        # Should either succeed or return timeout error
        assert response.status_code in [200, 408]
        
        if response.status_code == 408:
            data = response.json()
            assert "timeout" in data["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__])
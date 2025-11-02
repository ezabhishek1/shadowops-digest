"""
Unit tests for ticket clustering functionality.

Tests the clustering algorithm accuracy, edge cases, and integration
with OpenAI and fallback methods.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clustering import TicketClusteringEngine, cluster_tickets


class TestTicketClusteringEngine:
    """Test cases for TicketClusteringEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_tickets = [
            "VPN connection fails on Windows 10",
            "Cannot connect to VPN from home",
            "Outlook password reset needed",
            "User account locked out",
            "Printer not responding in Building A",
            "Network printer offline"
        ]
        
        self.single_ticket = ["VPN connection issue"]
        
        self.large_ticket_set = [
            f"Network issue {i}" for i in range(15)
        ] + [
            f"Email problem {i}" for i in range(10)
        ] + [
            f"Hardware failure {i}" for i in range(8)
        ]
    
    def test_single_ticket_clustering(self):
        """Test clustering with single ticket returns one cluster."""
        engine = TicketClusteringEngine(use_vector_store=False)
        result = engine.cluster_tickets(self.single_ticket)
        
        assert len(result) == 1
        assert "General Issues" in result
        assert result["General Issues"] == [0]
    
    def test_empty_ticket_list(self):
        """Test clustering with empty ticket list."""
        engine = TicketClusteringEngine(use_vector_store=False)
        result = engine.cluster_tickets([])
        
        # Should return empty clusters or handle gracefully
        assert isinstance(result, dict)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_fallback_clustering_without_openai(self):
        """Test that clustering falls back to sklearn when OpenAI is unavailable."""
        engine = TicketClusteringEngine(use_vector_store=False)
        assert not engine.use_openai
        
        result = engine.cluster_tickets(self.sample_tickets)
        
        assert isinstance(result, dict)
        assert len(result) >= 1
        assert len(result) <= 10  # Max clusters constraint
        
        # Verify all tickets are assigned
        all_indices = []
        for indices in result.values():
            all_indices.extend(indices)
        assert set(all_indices) == set(range(len(self.sample_tickets)))
    
    def test_cluster_count_limits(self):
        """Test that clustering respects cluster count limits."""
        engine = TicketClusteringEngine(use_vector_store=False)
        result = engine.cluster_tickets(self.large_ticket_set)
        
        assert len(result) >= 1
        assert len(result) <= 10
    
    def test_cluster_name_generation(self):
        """Test that cluster names are meaningful and properly formatted."""
        engine = TicketClusteringEngine(use_vector_store=False)
        result = engine.cluster_tickets(self.sample_tickets)
        
        for cluster_name in result.keys():
            assert isinstance(cluster_name, str)
            assert len(cluster_name) > 0
            assert len(cluster_name) <= 50
    
    def test_preprocess_ticket(self):
        """Test ticket preprocessing functionality."""
        engine = TicketClusteringEngine(use_vector_store=False)
        
        # Test basic preprocessing
        processed = engine._preprocess_ticket("VPN Connection Failed!")
        assert processed == "vpn connection failed"
        
        # Test special character removal
        processed = engine._preprocess_ticket("Email@domain.com not working!!!")
        assert "email" in processed
        assert "@" not in processed
        assert "!" not in processed
    
    def test_determine_cluster_count(self):
        """Test cluster count determination logic."""
        engine = TicketClusteringEngine(use_vector_store=False)
        
        # Test various ticket counts
        assert engine._determine_cluster_count(1) == 1
        assert engine._determine_cluster_count(2) == 1
        assert engine._determine_cluster_count(5) == 2
        assert engine._determine_cluster_count(15) >= 3
        assert engine._determine_cluster_count(100) <= 10
    
    @patch('clustering.OpenAI')
    def test_openai_integration_success(self, mock_openai):
        """Test successful OpenAI integration."""
        # Mock OpenAI client and responses
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock embeddings response
        mock_embedding_response = Mock()
        mock_embedding_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3] * 512),  # 1536 dimensions
            Mock(embedding=[0.4, 0.5, 0.6] * 512),
            Mock(embedding=[0.7, 0.8, 0.9] * 512)
        ]
        mock_client.embeddings.create.return_value = mock_embedding_response
        
        # Mock chat completion for cluster naming
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="Network Issues"))]
        mock_client.chat.completions.create.return_value = mock_chat_response
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            engine = TicketClusteringEngine(use_vector_store=False)
            result = engine.cluster_tickets(self.sample_tickets[:3])
            
            assert isinstance(result, dict)
            assert len(result) >= 1
    
    @patch('clustering.OpenAI')
    def test_openai_integration_failure(self, mock_openai):
        """Test graceful handling of OpenAI failures."""
        # Mock OpenAI to raise an exception
        mock_openai.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            engine = TicketClusteringEngine(use_vector_store=False)
            # Should fall back to sklearn clustering
            result = engine.cluster_tickets(self.sample_tickets)
            
            assert isinstance(result, dict)
            assert len(result) >= 1


class TestClusterTicketsFunction:
    """Test cases for the main cluster_tickets function."""
    
    def test_cluster_tickets_function(self):
        """Test the main cluster_tickets function."""
        tickets = [
            "VPN connection issue",
            "Email not working",
            "Printer offline"
        ]
        
        result = cluster_tickets(tickets, use_vector_store=False)
        
        assert isinstance(result, dict)
        assert len(result) >= 1
        
        # Verify all tickets are assigned
        all_indices = []
        for indices in result.values():
            all_indices.extend(indices)
        assert set(all_indices) == set(range(len(tickets)))
    
    def test_cluster_tickets_with_vector_store_disabled(self):
        """Test clustering with vector store disabled."""
        tickets = ["Network issue", "Email problem"]
        
        result = cluster_tickets(tickets, use_vector_store=False)
        
        assert isinstance(result, dict)
        assert len(result) >= 1


if __name__ == "__main__":
    pytest.main([__file__])
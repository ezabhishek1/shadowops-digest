"""
Unit tests for suggestion generation functionality.

Tests suggestion generation quality, template fallbacks,
and AI integration accuracy.
"""

import pytest
import os
from unittest.mock import Mock, patch

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from suggestion import SuggestionGenerator, select_suggestion


class TestSuggestionGenerator:
    """Test cases for SuggestionGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SuggestionGenerator()
        
        self.sample_clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4],
            "Hardware Failures": [5]
        }
        
        self.sample_tickets = [
            "VPN connection fails on Windows 10",
            "Cannot connect to VPN from home",
            "Network timeout issues",
            "Outlook password reset needed",
            "Email not syncing",
            "Printer not responding"
        ]
        
        self.network_heavy_clusters = {
            "Network Connectivity": [0, 1, 2, 3, 4],
            "Minor Issues": [5]
        }
    
    def test_suggestion_generation_basic(self):
        """Test basic suggestion generation."""
        suggestion = self.generator.select_suggestion(self.sample_clusters, self.sample_tickets)
        
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        assert len(suggestion) <= 200
    
    def test_suggestion_contains_actionable_language(self):
        """Test that suggestions contain actionable language."""
        suggestion = self.generator.select_suggestion(self.sample_clusters, self.sample_tickets)
        
        actionable_words = [
            "create", "implement", "develop", "establish", "set up", "build", "design",
            "improve", "enhance", "optimize", "streamline", "automate",
            "provide", "offer", "add", "include", "integrate",
            "train", "educate", "document", "standardize"
        ]
        
        suggestion_lower = suggestion.lower()
        has_actionable = any(word in suggestion_lower for word in actionable_words)
        assert has_actionable, f"Suggestion lacks actionable language: {suggestion}"
    
    def test_primary_cluster_identification(self):
        """Test identification of primary cluster."""
        primary = self.generator._identify_primary_cluster(self.network_heavy_clusters, self.sample_tickets)
        
        assert primary["name"] == "Network Connectivity"
        assert primary["size"] == 5
        assert len(primary["indices"]) == 5
        assert primary["percentage"] > 50  # Should be majority
    
    def test_empty_clusters_handling(self):
        """Test handling of empty clusters."""
        suggestion = self.generator.select_suggestion({}, [])
        
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        # Should return a default suggestion
        assert "troubleshooting" in suggestion.lower() or "improve" in suggestion.lower()
    
    def test_single_cluster_handling(self):
        """Test handling of single cluster."""
        single_cluster = {"General Issues": [0, 1, 2]}
        tickets = ["Issue 1", "Issue 2", "Issue 3"]
        
        suggestion = self.generator.select_suggestion(single_cluster, tickets)
        
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        assert len(suggestion) <= 200
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_template_based_suggestion(self):
        """Test template-based suggestion generation when OpenAI is unavailable."""
        generator = SuggestionGenerator()
        assert not generator.use_openai
        
        suggestion = generator.select_suggestion(self.sample_clusters, self.sample_tickets)
        
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        assert len(suggestion) <= 200
    
    def test_network_issue_template_matching(self):
        """Test that network issues get appropriate template suggestions."""
        network_clusters = {
            "Network Connectivity Issues": [0, 1, 2, 3]
        }
        network_tickets = [
            "VPN connection failed",
            "Network timeout",
            "Internet not working",
            "WiFi disconnected"
        ]
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            generator = SuggestionGenerator()
            suggestion = generator.select_suggestion(network_clusters, network_tickets)
            
            # Should contain network-related improvement suggestions
            suggestion_lower = suggestion.lower()
            network_keywords = ["network", "vpn", "connection", "troubleshooting", "guide"]
            has_network_context = any(keyword in suggestion_lower for keyword in network_keywords)
            assert has_network_context, f"Network suggestion lacks context: {suggestion}"
    
    def test_suggestion_validation_and_cleaning(self):
        """Test suggestion validation and cleaning."""
        # Test with quotes
        dirty_suggestion = '"Create a network guide"'
        clean = self.generator._validate_and_clean_suggestion(dirty_suggestion)
        assert not clean.startswith('"')
        assert not clean.endswith('"')
        
        # Test with "Suggestion:" prefix
        prefixed = "Suggestion: Implement network monitoring"
        clean = self.generator._validate_and_clean_suggestion(prefixed)
        assert not clean.lower().startswith("suggestion:")
        
        # Test capitalization
        lowercase = "create network documentation"
        clean = self.generator._validate_and_clean_suggestion(lowercase)
        assert clean[0].isupper()
    
    def test_suggestion_length_validation(self):
        """Test suggestion length validation."""
        # Too short
        short = "Fix it"
        clean = self.generator._validate_and_clean_suggestion(short)
        assert len(clean) >= 10
        
        # Too long
        long = "A" * 250
        clean = self.generator._validate_and_clean_suggestion(long)
        assert len(clean) <= 200
    
    @patch('suggestion.OpenAI')
    def test_ai_suggestion_generation(self, mock_openai):
        """Test AI-powered suggestion generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Create comprehensive VPN troubleshooting guide"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            generator = SuggestionGenerator()
            suggestion = generator.select_suggestion(self.sample_clusters, self.sample_tickets)
            
            assert isinstance(suggestion, str)
            assert len(suggestion) >= 10
    
    @patch('suggestion.OpenAI')
    def test_ai_failure_fallback(self, mock_openai):
        """Test fallback when AI generation fails."""
        # Mock OpenAI to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            generator = SuggestionGenerator()
            suggestion = generator.select_suggestion(self.sample_clusters, self.sample_tickets)
            
            # Should still return a valid suggestion (fallback)
            assert isinstance(suggestion, str)
            assert len(suggestion) >= 10
    
    def test_cluster_context_preparation(self):
        """Test cluster context preparation for AI prompts."""
        context = self.generator._prepare_cluster_context(self.sample_clusters, self.sample_tickets)
        
        assert isinstance(context, str)
        assert "Network Issues: 3 tickets" in context
        assert "Email Problems: 2 tickets" in context
        assert "Hardware Failures: 1 tickets" in context
    
    def test_template_initialization(self):
        """Test that suggestion templates are properly initialized."""
        templates = self.generator.suggestion_templates
        
        assert isinstance(templates, dict)
        assert "network" in templates
        assert "authentication" in templates
        assert "email" in templates
        assert "default" in templates
        
        # Each template should have required fields
        for category, template_info in templates.items():
            if category != "default":
                assert "keywords" in template_info
                assert "template" in template_info
                assert isinstance(template_info["keywords"], list)
                assert isinstance(template_info["template"], str)


class TestSelectSuggestionFunction:
    """Test cases for the main select_suggestion function."""
    
    def test_select_suggestion_function(self):
        """Test the main select_suggestion function."""
        clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4]
        }
        tickets = [
            "VPN connection failed",
            "Network timeout",
            "WiFi issues",
            "Email not working",
            "Outlook problems"
        ]
        
        suggestion = select_suggestion(clusters, tickets)
        
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        assert len(suggestion) <= 200
    
    def test_function_with_edge_cases(self):
        """Test function with edge cases."""
        # Empty inputs
        suggestion = select_suggestion({}, [])
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10
        
        # Single cluster
        single_cluster = {"Issues": [0]}
        single_ticket = ["Problem"]
        suggestion = select_suggestion(single_cluster, single_ticket)
        assert isinstance(suggestion, str)
        assert len(suggestion) >= 10


if __name__ == "__main__":
    pytest.main([__file__])
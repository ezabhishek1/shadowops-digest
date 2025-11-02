"""
Unit tests for digest summarization functionality.

Tests summary generation, formatting, length validation,
and template-based summary creation.
"""

import pytest
import os

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from summarizer import DigestSummarizer, generate_digest_summary


class TestDigestSummarizer:
    """Test cases for DigestSummarizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.summarizer = DigestSummarizer()
        
        self.sample_clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4],
            "Hardware Failures": [5]
        }
        
        self.single_cluster = {
            "General Issues": [0, 1, 2, 3, 4]
        }
        
        self.large_clusters = {
            f"Category {i}": list(range(i*3, (i+1)*3)) for i in range(8)
        }
        
        self.sample_suggestion = "Create comprehensive VPN troubleshooting guide"
    
    def test_basic_summary_generation(self):
        """Test basic digest summary generation."""
        summary = self.summarizer.generate_digest_summary(
            self.sample_clusters, self.sample_suggestion, 3.0, 150.0
        )
        
        assert isinstance(summary, str)
        assert 50 <= len(summary) <= 300
        assert "6 tickets" in summary
        assert "3 categories" in summary
        assert "Network Issues" in summary
    
    def test_single_cluster_summary(self):
        """Test summary generation with single cluster."""
        summary = self.summarizer.generate_digest_summary(
            self.single_cluster, self.sample_suggestion, 2.5, 125.0
        )
        
        assert isinstance(summary, str)
        assert "5 tickets" in summary
        assert "1 category" in summary
        assert "General Issues" in summary
    
    def test_empty_clusters_handling(self):
        """Test handling of empty clusters."""
        summary = self.summarizer.generate_digest_summary(
            {}, self.sample_suggestion, 0.0, 0.0
        )
        
        assert isinstance(summary, str)
        assert len(summary) >= 50
        assert "0 tickets" in summary
    
    def test_summary_length_validation(self):
        """Test that summaries meet length requirements."""
        # Test with various cluster sizes
        test_cases = [
            (self.sample_clusters, 3.0, 150.0),
            (self.single_cluster, 2.5, 125.0),
            (self.large_clusters, 12.0, 600.0)
        ]
        
        for clusters, time_wasted, cost_saved in test_cases:
            summary = self.summarizer.generate_digest_summary(
                clusters, self.sample_suggestion, time_wasted, cost_saved
            )
            
            assert 50 <= len(summary) <= 300, f"Summary length {len(summary)} out of range"
    
    def test_summary_contains_required_information(self):
        """Test that summaries contain all required information."""
        summary = self.summarizer.generate_digest_summary(
            self.sample_clusters, self.sample_suggestion, 3.0, 150.0
        )
        
        # Should contain numeric data
        assert any(char.isdigit() for char in summary)
        
        # Should contain clustering information
        cluster_keywords = ["cluster", "categor", "group", "issue", "problem"]
        assert any(keyword in summary.lower() for keyword in cluster_keywords)
        
        # Should contain suggestion information
        suggestion_keywords = ["suggestion", "recommendation", "improve", "solution", "create"]
        assert any(keyword in summary.lower() for keyword in suggestion_keywords)
        
        # Should contain cost/time information
        cost_keywords = ["$", "dollar", "cost", "saving", "hour"]
        assert any(keyword in summary.lower() for keyword in cost_keywords)
    
    def test_template_selection(self):
        """Test template selection logic."""
        # Small dataset should use concise template
        small_clusters = {"Issue": [0, 1]}
        summary_data = self.summarizer._prepare_summary_data(
            small_clusters, self.sample_suggestion, 1.0, 50.0
        )
        template_type = self.summarizer._select_template_type(summary_data)
        assert template_type == "concise"
        
        # Large complex dataset should use detailed template
        summary_data = self.summarizer._prepare_summary_data(
            self.large_clusters, self.sample_suggestion, 12.0, 600.0
        )
        template_type = self.summarizer._select_template_type(summary_data)
        assert template_type == "detailed"
    
    def test_suggestion_shortening(self):
        """Test suggestion shortening for summary inclusion."""
        long_suggestion = "Create a comprehensive network troubleshooting self-service guide with detailed step-by-step instructions"
        short = self.summarizer._shorten_suggestion(long_suggestion, 60)
        
        assert len(short) <= 60
        assert short.endswith("...")
        assert "Create" in short
    
    def test_summary_data_preparation(self):
        """Test summary data preparation."""
        summary_data = self.summarizer._prepare_summary_data(
            self.sample_clusters, self.sample_suggestion, 3.0, 150.0
        )
        
        assert summary_data["ticket_count"] == 6
        assert summary_data["cluster_count"] == 3
        assert summary_data["category_word"] == "categories"
        assert summary_data["primary_cluster"] == "Network Issues"
        assert summary_data["primary_count"] == 3
        assert summary_data["primary_percentage"] == 50.0
    
    def test_cluster_overview_creation(self):
        """Test cluster overview generation."""
        overview = self.summarizer.create_cluster_overview(self.sample_clusters)
        
        assert isinstance(overview, str)
        assert "Network Issues" in overview
        assert "3 tickets" in overview
        assert "50.0%" in overview
    
    def test_empty_cluster_overview(self):
        """Test cluster overview with empty clusters."""
        overview = self.summarizer.create_cluster_overview({})
        
        assert overview == "No clusters identified"
    
    def test_summary_truncation(self):
        """Test intelligent summary truncation."""
        long_summary = "This is a very long summary that exceeds the maximum length limit and needs to be truncated intelligently at sentence boundaries to maintain readability and coherence while preserving the most important information."
        
        truncated = self.summarizer._truncate_summary(long_summary, 100)
        
        assert len(truncated) <= 100
        assert truncated.endswith(".")
    
    def test_summary_expansion(self):
        """Test summary expansion for short summaries."""
        short_summary = "5 tickets clustered."
        expanded = self.summarizer._expand_summary(short_summary)
        
        assert len(expanded) > len(short_summary)
        assert "analyzed" in expanded
    
    def test_fallback_summary_generation(self):
        """Test fallback summary generation."""
        fallback = self.summarizer._generate_fallback_summary(
            self.sample_clusters, self.sample_suggestion, 3.0, 150.0
        )
        
        assert isinstance(fallback, str)
        assert len(fallback) >= 50
        assert "6 tickets" in fallback
        assert "3 categories" in fallback
    
    def test_format_summary_with_missing_variables(self):
        """Test summary formatting with missing template variables."""
        incomplete_data = {
            "ticket_count": 5,
            "cluster_count": 2
            # Missing other required variables
        }
        
        # Should handle gracefully and fall back to standard template
        try:
            summary = self.summarizer._format_summary(incomplete_data, "standard")
            # Should not raise exception, might use fallback
            assert isinstance(summary, str)
        except KeyError:
            # This is acceptable behavior - the method should handle this
            pass
    
    def test_numeric_formatting_in_summary(self):
        """Test that numeric values are properly formatted in summaries."""
        summary = self.summarizer.generate_digest_summary(
            self.sample_clusters, self.sample_suggestion, 3.7, 156.89
        )
        
        # Time should be formatted to 1 decimal place
        assert "3.7" in summary
        
        # Cost should be formatted to 2 decimal places
        assert "156.89" in summary or "157" in summary  # May be rounded
    
    def test_category_word_selection(self):
        """Test singular/plural category word selection."""
        # Single cluster should use "category"
        single_data = self.summarizer._prepare_summary_data(
            {"Issue": [0, 1]}, self.sample_suggestion, 1.0, 50.0
        )
        assert single_data["category_word"] == "category"
        
        # Multiple clusters should use "categories"
        multi_data = self.summarizer._prepare_summary_data(
            self.sample_clusters, self.sample_suggestion, 3.0, 150.0
        )
        assert multi_data["category_word"] == "categories"


class TestGenerateDigestSummaryFunction:
    """Test cases for the main generate_digest_summary function."""
    
    def test_generate_digest_summary_function(self):
        """Test the main generate_digest_summary function."""
        clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4]
        }
        suggestion = "Implement network troubleshooting guide"
        
        summary = generate_digest_summary(clusters, suggestion, 2.5, 125.0)
        
        assert isinstance(summary, str)
        assert 50 <= len(summary) <= 300
        assert "5 tickets" in summary
        assert "2 categories" in summary
    
    def test_function_with_edge_cases(self):
        """Test function with edge cases."""
        # Empty clusters
        summary = generate_digest_summary({}, "Improve processes", 0.0, 0.0)
        assert isinstance(summary, str)
        assert len(summary) >= 50
        
        # Single ticket
        single_cluster = {"Issue": [0]}
        summary = generate_digest_summary(single_cluster, "Fix issue", 0.5, 25.0)
        assert isinstance(summary, str)
        assert "1 ticket" in summary
    
    def test_function_with_various_inputs(self):
        """Test function with various input combinations."""
        test_cases = [
            # (clusters, suggestion, time, cost)
            ({"Network": [0, 1, 2, 3]}, "Create VPN guide", 2.0, 100.0),
            ({"Email": [0], "Hardware": [1]}, "Improve support", 1.0, 50.0),
            ({f"Cat{i}": [i] for i in range(10)}, "Streamline processes", 5.0, 250.0)
        ]
        
        for clusters, suggestion, time_wasted, cost_saved in test_cases:
            summary = generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
            
            assert isinstance(summary, str)
            assert 50 <= len(summary) <= 300
            assert str(sum(len(indices) for indices in clusters.values())) in summary


if __name__ == "__main__":
    pytest.main([__file__])
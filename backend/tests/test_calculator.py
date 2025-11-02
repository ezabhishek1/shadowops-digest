"""
Unit tests for cost calculation functionality.

Tests cost calculation validation, time wasted computation,
and savings estimation accuracy.
"""

import pytest
import os

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator import CostCalculator, calculate_time_cost


class TestCostCalculator:
    """Test cases for CostCalculator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CostCalculator()
        
        self.sample_clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4],
            "Hardware Failures": [5]
        }
        
        self.single_cluster = {
            "General Issues": [0, 1, 2, 3, 4]
        }
        
        self.large_clusters = {
            f"Category {i}": list(range(i*5, (i+1)*5)) for i in range(5)
        }
    
    def test_basic_time_calculation(self):
        """Test basic time wasted calculation."""
        time_wasted = self.calculator._calculate_time_wasted(6, 30)  # 6 tickets, 30 min each
        
        assert time_wasted == 3.0  # 180 minutes = 3 hours
    
    def test_zero_tickets_time_calculation(self):
        """Test time calculation with zero tickets."""
        time_wasted = self.calculator._calculate_time_wasted(0, 30)
        
        assert time_wasted == 0.0
    
    def test_zero_time_per_ticket(self):
        """Test time calculation with zero time per ticket."""
        time_wasted = self.calculator._calculate_time_wasted(5, 0)
        
        assert time_wasted == 0.0
    
    def test_calculate_time_cost_basic(self):
        """Test basic time and cost calculation."""
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            self.sample_clusters, 30, 50.0  # 30 min per ticket, $50/hour
        )
        
        # 6 tickets * 30 min = 180 min = 3 hours
        assert time_wasted == 3.0
        
        # Cost saved should be positive and reasonable
        assert cost_saved > 0
        assert cost_saved <= 3.0 * 50.0  # Can't save more than total cost
    
    def test_calculate_time_cost_precision(self):
        """Test that results are formatted to correct precision."""
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            self.sample_clusters, 37, 42.33  # Odd numbers to test rounding
        )
        
        # Time should be rounded to 1 decimal place
        assert isinstance(time_wasted, float)
        assert len(str(time_wasted).split('.')[-1]) <= 1
        
        # Cost should be rounded to 2 decimal places
        assert isinstance(cost_saved, float)
        assert len(str(cost_saved).split('.')[-1]) <= 2
    
    def test_empty_clusters(self):
        """Test calculation with empty clusters."""
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            {}, 30, 50.0
        )
        
        assert time_wasted == 0.0
        assert cost_saved == 0.0
    
    def test_single_large_cluster(self):
        """Test calculation with single large cluster."""
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            self.single_cluster, 45, 60.0
        )
        
        # 5 tickets * 45 min = 225 min = 3.75 hours
        expected_time = 3.8  # Rounded to 1 decimal
        assert abs(time_wasted - expected_time) < 0.1
        
        # Should have reasonable cost savings
        assert cost_saved > 0
    
    def test_reduction_factor_calculation(self):
        """Test reduction factor calculation for different cluster types."""
        # Network issues should have higher reduction potential
        network_factor = self.calculator._get_cluster_reduction_factor("Network Issues", 5)
        general_factor = self.calculator._get_cluster_reduction_factor("General Issues", 5)
        
        assert 0.1 <= network_factor <= 0.8
        assert 0.1 <= general_factor <= 0.8
    
    def test_size_multiplier_logic(self):
        """Test size-based multiplier logic."""
        small_multiplier = self.calculator._get_size_multiplier(2)
        medium_multiplier = self.calculator._get_size_multiplier(5)
        large_multiplier = self.calculator._get_size_multiplier(12)
        
        assert small_multiplier < medium_multiplier < large_multiplier
        assert 0.8 <= small_multiplier <= 1.3
        assert 0.8 <= large_multiplier <= 1.3
    
    def test_efficiency_factor_calculation(self):
        """Test efficiency factor calculation."""
        # Single cluster should have high efficiency
        single_efficiency = self.calculator._calculate_efficiency_factor(self.single_cluster)
        
        # Many clusters should have lower efficiency
        many_efficiency = self.calculator._calculate_efficiency_factor(self.large_clusters)
        
        assert 0.8 <= single_efficiency <= 1.2
        assert 0.8 <= many_efficiency <= 1.2
    
    def test_cluster_analysis(self):
        """Test detailed cluster analysis functionality."""
        analysis = self.calculator.get_cluster_analysis(
            self.sample_clusters, 30, 50.0
        )
        
        assert "total_clusters" in analysis
        assert "total_tickets" in analysis
        assert "cluster_details" in analysis
        
        assert analysis["total_clusters"] == 3
        assert analysis["total_tickets"] == 6
        
        # Check cluster details
        for cluster_name in self.sample_clusters.keys():
            assert cluster_name in analysis["cluster_details"]
            details = analysis["cluster_details"][cluster_name]
            
            assert "ticket_count" in details
            assert "time_hours" in details
            assert "reduction_potential" in details
            assert "potential_savings_usd" in details
            assert "priority" in details
    
    def test_negative_values_handling(self):
        """Test handling of negative or invalid values."""
        # Should handle gracefully and return safe defaults
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            self.sample_clusters, -10, -50.0
        )
        
        assert time_wasted >= 0.0
        assert cost_saved >= 0.0
    
    def test_large_numbers_handling(self):
        """Test handling of very large numbers."""
        large_clusters = {
            "Massive Category": list(range(1000))
        }
        
        time_wasted, cost_saved = self.calculator.calculate_time_cost(
            large_clusters, 60, 100.0
        )
        
        # Should handle large numbers without errors
        assert isinstance(time_wasted, float)
        assert isinstance(cost_saved, float)
        assert time_wasted > 0
        assert cost_saved >= 0


class TestCalculateTimeCostFunction:
    """Test cases for the main calculate_time_cost function."""
    
    def test_calculate_time_cost_function(self):
        """Test the main calculate_time_cost function."""
        clusters = {
            "Network Issues": [0, 1, 2],
            "Email Problems": [3, 4]
        }
        
        time_wasted, cost_saved = calculate_time_cost(clusters, 30, 40.0)
        
        assert isinstance(time_wasted, float)
        assert isinstance(cost_saved, float)
        assert time_wasted >= 0
        assert cost_saved >= 0
    
    def test_function_with_edge_cases(self):
        """Test function with edge cases."""
        # Empty clusters
        time_wasted, cost_saved = calculate_time_cost({}, 30, 40.0)
        assert time_wasted == 0.0
        assert cost_saved == 0.0
        
        # Single ticket
        single_cluster = {"Issue": [0]}
        time_wasted, cost_saved = calculate_time_cost(single_cluster, 15, 25.0)
        assert time_wasted == 0.3  # 15 min = 0.25 hours, rounded to 0.3
        assert cost_saved >= 0


if __name__ == "__main__":
    pytest.main([__file__])
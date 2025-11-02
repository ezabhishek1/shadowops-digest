"""
Cost Calculator for ShadowOps Digest

Module for calculating time wasted and potential cost savings from implementing
improvement suggestions based on ticket cluster analysis and operational parameters.
"""

import logging
from typing import Dict, List, Tuple
import math

logger = logging.getLogger(__name__)


class CostCalculator:
    """
    Calculator for time and cost analysis of IT support ticket patterns.
    
    Provides methods to calculate time wasted on repetitive issues and estimate
    potential savings from implementing improvement suggestions.
    """
    
    def __init__(self):
        """Initialize the cost calculator with default parameters."""
        # Default reduction assumptions for different improvement types
        self.reduction_factors = {
            "self_service": 0.6,      # Self-service guides reduce 60% of similar tickets
            "automation": 0.7,        # Automation reduces 70% of similar tickets
            "training": 0.4,          # Training reduces 40% of similar tickets
            "documentation": 0.5,     # Documentation reduces 50% of similar tickets
            "process": 0.45,          # Process improvements reduce 45% of similar tickets
            "default": 0.5            # Default 50% reduction assumption
        }
        
        # Efficiency factors for different cluster sizes
        self.efficiency_multipliers = {
            "small": 0.8,    # Small clusters (1-3 tickets) - 80% efficiency
            "medium": 1.0,   # Medium clusters (4-10 tickets) - 100% efficiency
            "large": 1.2     # Large clusters (11+ tickets) - 120% efficiency (economies of scale)
        }
    
    def calculate_time_cost(self, clusters: Dict[str, List[int]], 
                          avg_time_per_ticket: int, hourly_cost: float) -> Tuple[float, float]:
        """
        Calculate total time wasted and potential cost savings.
        
        Args:
            clusters: Dictionary mapping cluster names to ticket indices
            avg_time_per_ticket: Average time per ticket in minutes
            hourly_cost: Hourly cost in USD for support staff
            
        Returns:
            Tuple of (time_wasted_hours, cost_saved_usd)
        """
        logger.info(f"Calculating costs for {len(clusters)} clusters")
        
        try:
            # Calculate total time wasted
            total_tickets = sum(len(indices) for indices in clusters.values())
            time_wasted_hours = self._calculate_time_wasted(total_tickets, avg_time_per_ticket)
            
            # Calculate potential cost savings
            cost_saved_usd = self._calculate_cost_savings(
                clusters, time_wasted_hours, hourly_cost
            )
            
            # Format to required precision
            time_wasted_hours = round(time_wasted_hours, 1)
            cost_saved_usd = round(cost_saved_usd, 2)
            
            logger.info(f"Calculated: {time_wasted_hours}h wasted, ${cost_saved_usd} potential savings")
            return time_wasted_hours, cost_saved_usd
            
        except Exception as e:
            logger.error(f"Failed to calculate time and cost: {e}")
            # Return safe defaults
            return 0.0, 0.0
    
    def _calculate_time_wasted(self, total_tickets: int, avg_time_per_ticket: int) -> float:
        """
        Calculate total time wasted on all tickets.
        
        Args:
            total_tickets: Total number of tickets
            avg_time_per_ticket: Average time per ticket in minutes
            
        Returns:
            Total time wasted in hours
        """
        if total_tickets <= 0 or avg_time_per_ticket <= 0:
            return 0.0
        
        total_minutes = total_tickets * avg_time_per_ticket
        return total_minutes / 60.0
    
    def _calculate_cost_savings(self, clusters: Dict[str, List[int]], 
                              time_wasted_hours: float, hourly_cost: float) -> float:
        """
        Calculate potential cost savings from implementing improvements.
        
        Args:
            clusters: Dictionary of ticket clusters
            time_wasted_hours: Total time wasted in hours
            hourly_cost: Hourly cost in USD
            
        Returns:
            Potential cost savings in USD
        """
        if not clusters or time_wasted_hours <= 0 or hourly_cost <= 0:
            return 0.0
        
        # Calculate weighted reduction potential across all clusters
        total_reduction_potential = self._estimate_reduction_potential(clusters)
        
        # Calculate base savings
        base_savings = time_wasted_hours * hourly_cost * total_reduction_potential
        
        # Apply efficiency multipliers based on cluster characteristics
        efficiency_factor = self._calculate_efficiency_factor(clusters)
        
        # Calculate final savings with efficiency adjustments
        final_savings = base_savings * efficiency_factor
        
        # Ensure savings don't exceed total cost
        max_possible_savings = time_wasted_hours * hourly_cost
        return min(final_savings, max_possible_savings)
    
    def _estimate_reduction_potential(self, clusters: Dict[str, List[int]]) -> float:
        """
        Estimate overall reduction potential based on cluster analysis.
        
        Args:
            clusters: Dictionary of ticket clusters
            
        Returns:
            Weighted average reduction potential (0.0 to 1.0)
        """
        if not clusters:
            return 0.0
        
        total_tickets = sum(len(indices) for indices in clusters.values())
        weighted_reduction = 0.0
        
        for cluster_name, indices in clusters.items():
            cluster_size = len(indices)
            cluster_weight = cluster_size / total_tickets
            
            # Determine reduction factor based on cluster characteristics
            reduction_factor = self._get_cluster_reduction_factor(cluster_name, cluster_size)
            
            weighted_reduction += cluster_weight * reduction_factor
        
        return weighted_reduction
    
    def _get_cluster_reduction_factor(self, cluster_name: str, cluster_size: int) -> float:
        """
        Get reduction factor for a specific cluster based on its characteristics.
        
        Args:
            cluster_name: Name of the cluster
            cluster_size: Number of tickets in the cluster
            
        Returns:
            Reduction factor (0.0 to 1.0)
        """
        cluster_name_lower = cluster_name.lower()
        
        # Determine improvement type based on cluster name
        if any(keyword in cluster_name_lower for keyword in 
               ["network", "vpn", "connection", "internet"]):
            base_factor = self.reduction_factors["self_service"]
        elif any(keyword in cluster_name_lower for keyword in 
                 ["password", "login", "authentication", "access"]):
            base_factor = self.reduction_factors["automation"]
        elif any(keyword in cluster_name_lower for keyword in 
                 ["email", "outlook", "mail"]):
            base_factor = self.reduction_factors["documentation"]
        elif any(keyword in cluster_name_lower for keyword in 
                 ["hardware", "printer", "device"]):
            base_factor = self.reduction_factors["process"]
        elif any(keyword in cluster_name_lower for keyword in 
                 ["software", "application", "program"]):
            base_factor = self.reduction_factors["automation"]
        else:
            base_factor = self.reduction_factors["default"]
        
        # Adjust based on cluster size (larger clusters have higher potential)
        size_multiplier = self._get_size_multiplier(cluster_size)
        
        # Calculate final reduction factor
        final_factor = base_factor * size_multiplier
        
        # Ensure factor stays within reasonable bounds
        return min(max(final_factor, 0.1), 0.8)  # Between 10% and 80%
    
    def _get_size_multiplier(self, cluster_size: int) -> float:
        """
        Get size-based multiplier for reduction potential.
        
        Args:
            cluster_size: Number of tickets in the cluster
            
        Returns:
            Size multiplier (0.8 to 1.3)
        """
        if cluster_size <= 2:
            return 0.8   # Small clusters have lower reduction potential
        elif cluster_size <= 5:
            return 1.0   # Medium clusters have standard potential
        elif cluster_size <= 10:
            return 1.15  # Large clusters have higher potential
        else:
            return 1.3   # Very large clusters have highest potential
    
    def _calculate_efficiency_factor(self, clusters: Dict[str, List[int]]) -> float:
        """
        Calculate efficiency factor based on cluster distribution.
        
        Args:
            clusters: Dictionary of ticket clusters
            
        Returns:
            Efficiency factor (0.8 to 1.2)
        """
        if not clusters:
            return 1.0
        
        cluster_sizes = [len(indices) for indices in clusters.values()]
        total_tickets = sum(cluster_sizes)
        
        # Calculate cluster distribution metrics
        num_clusters = len(clusters)
        avg_cluster_size = total_tickets / num_clusters
        largest_cluster_size = max(cluster_sizes)
        
        # Base efficiency on cluster distribution
        if num_clusters == 1:
            # Single large cluster - high efficiency
            efficiency = 1.1
        elif num_clusters <= 3:
            # Few clusters - good efficiency
            efficiency = 1.05
        elif num_clusters <= 6:
            # Moderate number of clusters - standard efficiency
            efficiency = 1.0
        else:
            # Many small clusters - lower efficiency
            efficiency = 0.9
        
        # Adjust based on largest cluster dominance
        dominance_ratio = largest_cluster_size / total_tickets
        if dominance_ratio > 0.6:
            # One cluster dominates - increase efficiency
            efficiency *= 1.1
        elif dominance_ratio < 0.3:
            # No dominant cluster - decrease efficiency
            efficiency *= 0.95
        
        # Ensure efficiency stays within bounds
        return min(max(efficiency, 0.8), 1.2)
    
    def get_cluster_analysis(self, clusters: Dict[str, List[int]], 
                           avg_time_per_ticket: int, hourly_cost: float) -> Dict[str, any]:
        """
        Get detailed analysis for each cluster including individual savings potential.
        
        Args:
            clusters: Dictionary of ticket clusters
            avg_time_per_ticket: Average time per ticket in minutes
            hourly_cost: Hourly cost in USD
            
        Returns:
            Dictionary with detailed cluster analysis
        """
        analysis = {
            "total_clusters": len(clusters),
            "total_tickets": sum(len(indices) for indices in clusters.values()),
            "cluster_details": {}
        }
        
        for cluster_name, indices in clusters.items():
            cluster_size = len(indices)
            cluster_time_hours = (cluster_size * avg_time_per_ticket) / 60.0
            reduction_factor = self._get_cluster_reduction_factor(cluster_name, cluster_size)
            potential_savings = cluster_time_hours * hourly_cost * reduction_factor
            
            analysis["cluster_details"][cluster_name] = {
                "ticket_count": cluster_size,
                "time_hours": round(cluster_time_hours, 1),
                "reduction_potential": round(reduction_factor * 100, 1),
                "potential_savings_usd": round(potential_savings, 2),
                "priority": "High" if cluster_size >= 5 else "Medium" if cluster_size >= 3 else "Low"
            }
        
        return analysis


def calculate_time_cost(clusters: Dict[str, List[int]], avg_time_per_ticket: int, 
                       hourly_cost: float) -> Tuple[float, float]:
    """
    Main function to calculate time wasted and potential cost savings.
    
    Args:
        clusters: Dictionary mapping cluster names to ticket indices
        avg_time_per_ticket: Average time per ticket in minutes
        hourly_cost: Hourly cost in USD for support staff
        
    Returns:
        Tuple of (time_wasted_hours, cost_saved_usd)
    """
    calculator = CostCalculator()
    return calculator.calculate_time_cost(clusters, avg_time_per_ticket, hourly_cost)
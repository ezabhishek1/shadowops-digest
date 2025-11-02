"""
Digest Summarizer for ShadowOps Digest

Module for generating human-readable summaries of ticket analysis results,
combining cluster information, suggestions, and metrics into executive summaries.
"""

import logging
from typing import Dict, List
import re

logger = logging.getLogger(__name__)


class DigestSummarizer:
    """
    Summarizer for creating human-readable digest summaries.
    
    Generates executive summaries that combine cluster analysis, improvement
    suggestions, and cost metrics into concise, actionable reports.
    """
    
    def __init__(self):
        """Initialize the digest summarizer with formatting templates."""
        self.summary_templates = {
            "standard": "{ticket_count} tickets clustered into {cluster_count} {category_word}. "
                       "Primary issue: {primary_cluster} ({primary_count} tickets). "
                       "Recommendation: {suggestion_short}. "
                       "Potential savings: {time_saved} hours, ${cost_saved}.",
            
            "detailed": "{ticket_count} support tickets analyzed and grouped into {cluster_count} distinct "
                       "{category_word}. The largest category '{primary_cluster}' contains {primary_count} "
                       "tickets ({primary_percentage}%). Suggested improvement: {suggestion_short}. "
                       "Expected time savings: {time_saved}h, cost impact: ${cost_saved}.",
            
            "concise": "{ticket_count} tickets → {cluster_count} {category_word}. "
                      "Top issue: {primary_cluster} ({primary_count}). "
                      "Suggested improvement: {suggestion_short}. "
                      "Saves: {time_saved}h, ${cost_saved}."
        }
    
    def generate_digest_summary(self, clusters: Dict[str, List[int]], suggestion: str,
                              time_wasted: float, cost_saved: float) -> str:
        """
        Generate human-readable digest summary from analysis results.
        
        Args:
            clusters: Dictionary mapping cluster names to ticket indices
            suggestion: Improvement suggestion text
            time_wasted: Time wasted in hours
            cost_saved: Potential cost savings in USD
            
        Returns:
            Human-readable digest summary string
        """
        logger.info("Generating digest summary")
        
        try:
            # Calculate summary metrics
            summary_data = self._prepare_summary_data(clusters, suggestion, time_wasted, cost_saved)
            
            # Choose appropriate template based on content length
            template_type = self._select_template_type(summary_data)
            
            # Generate summary from template
            summary = self._format_summary(summary_data, template_type)
            
            # Validate and adjust summary length
            final_summary = self._validate_summary_length(summary)
            
            logger.info(f"Generated summary: {len(final_summary)} characters")
            return final_summary
            
        except Exception as e:
            logger.error(f"Failed to generate digest summary: {e}")
            return self._generate_fallback_summary(clusters, suggestion, time_wasted, cost_saved)
    
    def _prepare_summary_data(self, clusters: Dict[str, List[int]], suggestion: str,
                            time_wasted: float, cost_saved: float) -> Dict[str, any]:
        """
        Prepare data for summary generation.
        
        Args:
            clusters: Dictionary of clusters
            suggestion: Improvement suggestion
            time_wasted: Time wasted in hours
            cost_saved: Cost savings in USD
            
        Returns:
            Dictionary with formatted summary data
        """
        # Calculate basic metrics
        total_tickets = sum(len(indices) for indices in clusters.values())
        cluster_count = len(clusters)
        
        # Find primary cluster (largest)
        primary_cluster_name = "General Issues"
        primary_cluster_count = 0
        primary_percentage = 0.0
        
        if clusters:
            primary_cluster_name, primary_indices = max(clusters.items(), key=lambda x: len(x[1]))
            primary_cluster_count = len(primary_indices)
            primary_percentage = (primary_cluster_count / total_tickets * 100) if total_tickets > 0 else 0
        
        # Format suggestion for summary
        suggestion_short = self._shorten_suggestion(suggestion)
        
        # Determine category word (singular/plural)
        category_word = "category" if cluster_count == 1 else "categories"
        
        return {
            "ticket_count": total_tickets,
            "cluster_count": cluster_count,
            "category_word": category_word,
            "primary_cluster": primary_cluster_name,
            "primary_count": primary_cluster_count,
            "primary_percentage": round(primary_percentage, 1),
            "suggestion_short": suggestion_short,
            "time_saved": time_wasted,  # Using time_wasted as potential time saved
            "cost_saved": cost_saved
        }
    
    def _select_template_type(self, summary_data: Dict[str, any]) -> str:
        """
        Select appropriate template type based on data complexity.
        
        Args:
            summary_data: Prepared summary data
            
        Returns:
            Template type string
        """
        ticket_count = summary_data["ticket_count"]
        cluster_count = summary_data["cluster_count"]
        
        # Use detailed template for complex scenarios
        if ticket_count > 20 and cluster_count > 5:
            return "detailed"
        # Use concise template for simple scenarios
        elif ticket_count <= 5 or cluster_count <= 2:
            return "concise"
        # Use standard template for most cases
        else:
            return "standard"
    
    def _format_summary(self, summary_data: Dict[str, any], template_type: str) -> str:
        """
        Format summary using selected template.
        
        Args:
            summary_data: Prepared summary data
            template_type: Type of template to use
            
        Returns:
            Formatted summary string
        """
        template = self.summary_templates.get(template_type, self.summary_templates["standard"])
        
        try:
            return template.format(**summary_data)
        except KeyError as e:
            logger.warning(f"Missing template variable {e}, using standard template")
            return self.summary_templates["standard"].format(**summary_data)
    
    def _shorten_suggestion(self, suggestion: str, max_length: int = 60) -> str:
        """
        Shorten suggestion for summary inclusion.
        
        Args:
            suggestion: Full suggestion text
            max_length: Maximum length for shortened version
            
        Returns:
            Shortened suggestion text
        """
        if not suggestion:
            return "process improvements"
        
        # Clean the suggestion
        suggestion = suggestion.strip()
        
        # If already short enough, return as-is
        if len(suggestion) <= max_length:
            return suggestion
        
        # Try to find a good breaking point
        words = suggestion.split()
        shortened = ""
        
        for word in words:
            if len(shortened + " " + word) <= max_length - 3:  # Leave room for "..."
                shortened += " " + word if shortened else word
            else:
                break
        
        # If we couldn't fit any words, just truncate
        if not shortened:
            shortened = suggestion[:max_length - 3]
        
        return shortened + "..."
    
    def _validate_summary_length(self, summary: str) -> str:
        """
        Validate and adjust summary length to meet requirements.
        
        Args:
            summary: Generated summary text
            
        Returns:
            Length-validated summary
        """
        min_length = 50
        max_length = 300
        
        # If too short, add more detail
        if len(summary) < min_length:
            summary = self._expand_summary(summary)
        
        # If too long, truncate intelligently
        elif len(summary) > max_length:
            summary = self._truncate_summary(summary, max_length)
        
        return summary
    
    def _expand_summary(self, summary: str) -> str:
        """
        Expand a summary that's too short.
        
        Args:
            summary: Short summary text
            
        Returns:
            Expanded summary text
        """
        # Add more descriptive language
        expanded = summary
        
        # Add context if missing
        if "analyzed" not in expanded.lower():
            expanded = expanded.replace("tickets", "tickets analyzed")
        
        # Add impact statement if missing
        if "impact" not in expanded.lower() and "savings" in expanded.lower():
            expanded = expanded.replace("savings:", "potential impact:")
        
        return expanded
    
    def _truncate_summary(self, summary: str, max_length: int) -> str:
        """
        Intelligently truncate a summary that's too long.
        
        Args:
            summary: Long summary text
            max_length: Maximum allowed length
            
        Returns:
            Truncated summary text
        """
        if len(summary) <= max_length:
            return summary
        
        # Try to truncate at sentence boundaries
        sentences = re.split(r'[.!?]+', summary)
        truncated = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed limit
            test_length = len(truncated + ". " + sentence) if truncated else len(sentence)
            
            if test_length <= max_length - 1:  # Leave room for period
                truncated += ". " + sentence if truncated else sentence
            else:
                break
        
        # If no complete sentences fit, truncate at word boundaries
        if not truncated:
            words = summary.split()
            truncated = ""
            
            for word in words:
                if len(truncated + " " + word) <= max_length - 3:  # Leave room for "..."
                    truncated += " " + word if truncated else word
                else:
                    break
            
            truncated += "..."
        else:
            truncated += "."
        
        return truncated
    
    def _generate_fallback_summary(self, clusters: Dict[str, List[int]], suggestion: str,
                                 time_wasted: float, cost_saved: float) -> str:
        """
        Generate a basic fallback summary when main generation fails.
        
        Args:
            clusters: Dictionary of clusters
            suggestion: Improvement suggestion
            time_wasted: Time wasted in hours
            cost_saved: Cost savings in USD
            
        Returns:
            Basic fallback summary
        """
        total_tickets = sum(len(indices) for indices in clusters.values()) if clusters else 0
        cluster_count = len(clusters) if clusters else 0
        
        return (f"{total_tickets} tickets analyzed and grouped into {cluster_count} categories. "
                f"Recommended improvement identified. "
                f"Potential time savings: {time_wasted} hours, cost impact: ${cost_saved}.")
    
    def create_cluster_overview(self, clusters: Dict[str, List[int]]) -> str:
        """
        Create a brief overview of cluster distribution.
        
        Args:
            clusters: Dictionary of clusters
            
        Returns:
            Cluster overview string
        """
        if not clusters:
            return "No clusters identified"
        
        total_tickets = sum(len(indices) for indices in clusters.values())
        cluster_summaries = []
        
        # Sort clusters by size (largest first)
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
        
        for cluster_name, indices in sorted_clusters[:3]:  # Top 3 clusters
            percentage = (len(indices) / total_tickets * 100) if total_tickets > 0 else 0
            cluster_summaries.append(f"{cluster_name} ({len(indices)} tickets, {percentage:.1f}%)")
        
        overview = "; ".join(cluster_summaries)
        
        if len(sorted_clusters) > 3:
            remaining = len(sorted_clusters) - 3
            overview += f"; and {remaining} other {'category' if remaining == 1 else 'categories'}"
        
        return overview


def generate_digest_summary(clusters: Dict[str, List[int]], suggestion: str,
                          time_wasted: float, cost_saved: float) -> str:
    """
    Main function to generate digest summary from analysis results.
    
    Args:
        clusters: Dictionary mapping cluster names to ticket indices
        suggestion: Improvement suggestion text
        time_wasted: Time wasted in hours
        cost_saved: Potential cost savings in USD
        
    Returns:
        Human-readable digest summary string
    """
    summarizer = DigestSummarizer()
    return summarizer.generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
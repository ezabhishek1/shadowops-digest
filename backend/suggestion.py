"""
Suggestion Generator for ShadowOps Digest

AI-powered module that analyzes ticket clusters to generate actionable
improvement suggestions using GPT-4 with fallback templates for offline scenarios.
"""

import logging
import os
from typing import Dict, List, Optional
import re
from openai import OpenAI

logger = logging.getLogger(__name__)


class SuggestionGenerator:
    """
    AI-powered suggestion generator with GPT-4 integration and template fallbacks.
    
    Analyzes ticket clusters to identify improvement opportunities and generates
    actionable recommendations for reducing similar issues in the future.
    """
    
    def __init__(self):
        """Initialize the suggestion generator with OpenAI client and templates."""
        self.openai_client = None
        self.use_openai = False
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip() and api_key != "your_openai_api_key_here":
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_openai = True
                logger.info("OpenAI client initialized for suggestion generation")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.use_openai = False
        else:
            logger.info("OpenAI API key not found, using template-based suggestions")
        
        # Fallback suggestion templates
        self.suggestion_templates = self._initialize_templates()
    
    def select_suggestion(self, clusters: Dict[str, List[int]], tickets: List[str]) -> str:
        """
        Generate actionable improvement suggestion based on ticket clusters.
        
        Args:
            clusters: Dictionary mapping cluster names to ticket indices
            tickets: Original ticket descriptions
            
        Returns:
            Actionable improvement suggestion string
        """
        logger.info(f"Generating suggestion for {len(clusters)} clusters")
        
        try:
            # Identify the most impactful cluster
            primary_cluster = self._identify_primary_cluster(clusters, tickets)
            
            if self.use_openai:
                suggestion = self._generate_ai_suggestion(primary_cluster, clusters, tickets)
            else:
                suggestion = self._generate_template_suggestion(primary_cluster, clusters, tickets)
            
            # Validate and clean the suggestion
            cleaned_suggestion = self._validate_and_clean_suggestion(suggestion)
            
            logger.info(f"Generated suggestion: {cleaned_suggestion[:50]}...")
            return cleaned_suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate suggestion: {e}")
            return "Implement standardized troubleshooting procedures for common IT issues"
    
    def _identify_primary_cluster(self, clusters: Dict[str, List[int]], 
                                tickets: List[str]) -> Dict[str, any]:
        """
        Identify the most impactful cluster for suggestion generation.
        
        Args:
            clusters: Dictionary of clusters
            tickets: Original ticket descriptions
            
        Returns:
            Dictionary with primary cluster information
        """
        if not clusters:
            return {"name": "General Issues", "indices": [], "size": 0}
        
        # Find largest cluster (most impact potential)
        largest_cluster = max(clusters.items(), key=lambda x: len(x[1]))
        cluster_name, cluster_indices = largest_cluster
        
        # Analyze cluster characteristics
        cluster_tickets = [tickets[i] for i in cluster_indices]
        
        return {
            "name": cluster_name,
            "indices": cluster_indices,
            "size": len(cluster_indices),
            "tickets": cluster_tickets,
            "percentage": (len(cluster_indices) / len(tickets)) * 100 if tickets else 0
        }
    
    def _generate_ai_suggestion(self, primary_cluster: Dict[str, any], 
                              clusters: Dict[str, List[int]], tickets: List[str]) -> str:
        """
        Generate suggestion using OpenAI GPT-4.
        
        Args:
            primary_cluster: Information about the primary cluster
            clusters: All clusters
            tickets: Original tickets
            
        Returns:
            AI-generated suggestion
        """
        try:
            # Prepare context for AI
            cluster_summary = self._prepare_cluster_context(clusters, tickets)
            primary_tickets = "\n".join(f"- {ticket}" for ticket in primary_cluster["tickets"][:5])
            
            prompt = f"""You are an IT operations expert analyzing support ticket patterns. Based on the ticket analysis below, provide ONE specific, actionable improvement suggestion that would reduce similar tickets in the future.

TICKET ANALYSIS:
- Total tickets analyzed: {len(tickets)}
- Number of issue categories: {len(clusters)}
- Primary issue category: {primary_cluster['name']} ({primary_cluster['size']} tickets, {primary_cluster.get('percentage', 0):.1f}%)

PRIMARY ISSUE EXAMPLES:
{primary_tickets}

ALL CATEGORIES:
{cluster_summary}

REQUIREMENTS:
- Provide exactly ONE suggestion (not a list)
- Make it specific and actionable
- Focus on preventing the primary issue category
- Keep it between 10-200 characters
- Use action words like "Create", "Implement", "Develop", "Establish"
- Focus on root cause prevention, not symptom treatment

Suggestion:"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            suggestion = response.choices[0].message.content.strip()
            return suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate AI suggestion: {e}")
            raise
    
    def _generate_template_suggestion(self, primary_cluster: Dict[str, any], 
                                    clusters: Dict[str, List[int]], tickets: List[str]) -> str:
        """
        Generate suggestion using template-based approach.
        
        Args:
            primary_cluster: Information about the primary cluster
            clusters: All clusters
            tickets: Original tickets
            
        Returns:
            Template-based suggestion
        """
        cluster_name = primary_cluster["name"].lower()
        
        # Find best matching template
        best_template = self.suggestion_templates["default"]
        best_score = 0
        
        for category, template_info in self.suggestion_templates.items():
            if category == "default":
                continue
            
            keywords = template_info["keywords"]
            score = sum(1 for keyword in keywords if keyword in cluster_name)
            
            if score > best_score:
                best_score = score
                best_template = template_info
        
        # Generate suggestion from template
        suggestion = best_template["template"].format(
            cluster_name=primary_cluster["name"],
            ticket_count=primary_cluster["size"],
            percentage=primary_cluster.get("percentage", 0)
        )
        
        return suggestion
    
    def _prepare_cluster_context(self, clusters: Dict[str, List[int]], tickets: List[str]) -> str:
        """
        Prepare cluster context summary for AI prompt.
        
        Args:
            clusters: Dictionary of clusters
            tickets: Original tickets
            
        Returns:
            Formatted cluster context string
        """
        context_lines = []
        
        for cluster_name, indices in clusters.items():
            context_lines.append(f"- {cluster_name}: {len(indices)} tickets")
        
        return "\n".join(context_lines)
    
    def _validate_and_clean_suggestion(self, suggestion: str) -> str:
        """
        Validate and clean the generated suggestion.
        
        Args:
            suggestion: Raw suggestion text
            
        Returns:
            Cleaned and validated suggestion
        """
        if not suggestion:
            return "Implement standardized troubleshooting procedures for common IT issues"
        
        # Clean the suggestion
        suggestion = suggestion.strip()
        
        # Remove quotes if present
        suggestion = re.sub(r'^["\']|["\']$', '', suggestion)
        
        # Remove "Suggestion:" prefix if present
        suggestion = re.sub(r'^suggestion:\s*', '', suggestion, flags=re.IGNORECASE)
        
        # Ensure it starts with a capital letter
        if suggestion and not suggestion[0].isupper():
            suggestion = suggestion[0].upper() + suggestion[1:]
        
        # Ensure it doesn't end with a period (for consistency)
        suggestion = suggestion.rstrip('.')
        
        # Validate length
        if len(suggestion) < 10:
            return "Create comprehensive troubleshooting guides for common IT issues"
        elif len(suggestion) > 200:
            suggestion = suggestion[:197] + "..."
        
        # Validate actionable language
        actionable_patterns = [
            r'\b(create|implement|develop|establish|set up|build|design)\b',
            r'\b(improve|enhance|optimize|streamline|automate)\b',
            r'\b(provide|offer|add|include|integrate)\b',
            r'\b(train|educate|document|standardize)\b'
        ]
        
        has_actionable_language = any(
            re.search(pattern, suggestion.lower()) for pattern in actionable_patterns
        )
        
        if not has_actionable_language:
            # Prepend with actionable verb
            suggestion = f"Implement {suggestion.lower()}"
        
        return suggestion
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """
        Initialize fallback suggestion templates for different issue categories.
        
        Returns:
            Dictionary of suggestion templates by category
        """
        return {
            "network": {
                "keywords": ["network", "vpn", "connection", "internet", "wifi"],
                "template": "Create a comprehensive network troubleshooting self-service guide with step-by-step diagnostics"
            },
            "authentication": {
                "keywords": ["password", "login", "access", "account", "authentication"],
                "template": "Implement automated password reset system with multi-factor authentication setup"
            },
            "email": {
                "keywords": ["email", "outlook", "mail", "exchange"],
                "template": "Develop email configuration wizard and common issue resolution database"
            },
            "hardware": {
                "keywords": ["printer", "monitor", "keyboard", "mouse", "hardware"],
                "template": "Establish hardware replacement workflow with user self-service options"
            },
            "software": {
                "keywords": ["software", "application", "program", "install"],
                "template": "Create automated software deployment and troubleshooting system"
            },
            "phone": {
                "keywords": ["phone", "voip", "call", "telephone"],
                "template": "Implement VoIP troubleshooting guide with common configuration fixes"
            },
            "security": {
                "keywords": ["security", "virus", "malware", "firewall"],
                "template": "Develop security awareness training and automated threat response procedures"
            },
            "file_access": {
                "keywords": ["file", "folder", "share", "drive", "permission"],
                "template": "Create file access management system with automated permission requests"
            },
            "default": {
                "keywords": [],
                "template": "Implement standardized troubleshooting procedures and knowledge base for common IT issues"
            }
        }


def select_suggestion(clusters: Dict[str, List[int]], tickets: List[str]) -> str:
    """
    Main function to generate improvement suggestion from ticket clusters.
    
    Args:
        clusters: Dictionary mapping cluster names to ticket indices
        tickets: Original ticket descriptions
        
    Returns:
        Actionable improvement suggestion
    """
    generator = SuggestionGenerator()
    return generator.select_suggestion(clusters, tickets)
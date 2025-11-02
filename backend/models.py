"""
Pydantic models for ShadowOps Digest API request/response validation.

This module defines the data models used for API communication, including
input validation for ticket requests and structured output for digest results.
"""

from typing import Dict, List
from pydantic import BaseModel, Field, validator
import re


class TicketRequest(BaseModel):
    """
    Request model for ticket digest generation.
    
    Validates input data including ticket descriptions, timing parameters,
    and cost information for processing by the digest engine.
    """
    
    tickets: List[str] = Field(
        ...,
        min_items=1,
        max_items=1000,
        description="List of IT support ticket descriptions to analyze"
    )
    
    avg_time_per_ticket_minutes: int = Field(
        ...,
        ge=1,
        le=480,
        description="Average time spent per ticket in minutes (1-480)"
    )
    
    hourly_cost_usd: float = Field(
        ...,
        ge=1.0,
        le=500.0,
        description="Hourly cost in USD for support staff time (1.00-500.00)"
    )
    
    @validator('tickets')
    def validate_tickets(cls, v):
        """Validate ticket descriptions are non-empty and reasonable length."""
        if not v:
            raise ValueError("At least one ticket must be provided")
        
        for i, ticket in enumerate(v):
            if not ticket or not ticket.strip():
                raise ValueError(f"Ticket {i} cannot be empty")
            
            if len(ticket.strip()) < 5:
                raise ValueError(f"Ticket {i} must be at least 5 characters long")
            
            if len(ticket.strip()) > 500:
                raise ValueError(f"Ticket {i} must be less than 500 characters")
        
        return [ticket.strip() for ticket in v]
    
    @validator('hourly_cost_usd')
    def validate_hourly_cost(cls, v):
        """Validate hourly cost is reasonable and properly formatted."""
        if v <= 0:
            raise ValueError("Hourly cost must be greater than 0")
        
        # Round to 2 decimal places for currency
        return round(v, 2)


class ClusterResult(BaseModel):
    """
    Response model for ticket digest analysis results.
    
    Contains clustered tickets, improvement suggestions, cost analysis,
    and human-readable summary of the analysis.
    """
    
    clusters: Dict[str, List[int]] = Field(
        ...,
        description="Dictionary mapping cluster names to lists of ticket indices"
    )
    
    suggestion: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="Actionable improvement suggestion based on ticket analysis"
    )
    
    time_wasted_hours: float = Field(
        ...,
        ge=0,
        description="Total time wasted in hours based on ticket analysis"
    )
    
    cost_saved_usd: float = Field(
        ...,
        ge=0,
        description="Potential cost savings in USD from implementing suggestion"
    )
    
    digest_summary: str = Field(
        ...,
        min_length=50,
        max_length=300,
        description="Human-readable summary of the analysis results"
    )
    
    @validator('clusters')
    def validate_clusters(cls, v):
        """Validate cluster structure and content."""
        if not v:
            raise ValueError("At least one cluster must be generated")
        
        if len(v) > 10:
            raise ValueError("Maximum of 10 clusters allowed")
        
        # Validate cluster names
        for cluster_name in v.keys():
            if not cluster_name or not cluster_name.strip():
                raise ValueError("Cluster names cannot be empty")
            
            if len(cluster_name.strip()) > 50:
                raise ValueError("Cluster names must be less than 50 characters")
        
        # Validate ticket indices
        all_indices = []
        for cluster_name, indices in v.items():
            if not indices:
                raise ValueError(f"Cluster '{cluster_name}' cannot be empty")
            
            for idx in indices:
                if not isinstance(idx, int) or idx < 0:
                    raise ValueError(f"Invalid ticket index {idx} in cluster '{cluster_name}'")
                
                if idx in all_indices:
                    raise ValueError(f"Ticket index {idx} appears in multiple clusters")
                
                all_indices.append(idx)
        
        return v
    
    @validator('suggestion')
    def validate_suggestion(cls, v):
        """Validate suggestion is actionable and well-formed."""
        v = v.strip()
        
        if not v:
            raise ValueError("Suggestion cannot be empty")
        
        # Check for actionable language patterns
        actionable_patterns = [
            r'\b(create|implement|develop|establish|set up|build|design)\b',
            r'\b(improve|enhance|optimize|streamline|automate)\b',
            r'\b(provide|offer|add|include|integrate)\b',
            r'\b(train|educate|document|standardize)\b'
        ]
        
        has_actionable_language = any(
            re.search(pattern, v.lower()) for pattern in actionable_patterns
        )
        
        if not has_actionable_language:
            raise ValueError("Suggestion must contain actionable language (create, implement, improve, etc.)")
        
        return v
    
    @validator('time_wasted_hours')
    def validate_time_wasted(cls, v):
        """Validate and format time wasted to 1 decimal place."""
        if v < 0:
            raise ValueError("Time wasted cannot be negative")
        
        return round(v, 1)
    
    @validator('cost_saved_usd')
    def validate_cost_saved(cls, v):
        """Validate and format cost saved to 2 decimal places."""
        if v < 0:
            raise ValueError("Cost saved cannot be negative")
        
        return round(v, 2)
    
    @validator('digest_summary')
    def validate_digest_summary(cls, v):
        """Validate digest summary contains key information."""
        v = v.strip()
        
        if not v:
            raise ValueError("Digest summary cannot be empty")
        
        # Check for required information patterns (more flexible)
        required_patterns = [
            r'\d+',  # Some number (tickets, clusters, etc.)
            r'(cluster|categor|group|issue|problem)',  # Clustering reference
            r'(suggestion|recommendation|improve|solution)',  # Suggestion reference
            r'(\$|dollar|cost|saving|hour)',  # Cost/time information
        ]
        
        missing_info = []
        for i, pattern in enumerate(required_patterns):
            if not re.search(pattern, v.lower()):
                info_names = ['numeric data', 'clustering info', 'suggestion info', 'cost/time info']
                missing_info.append(info_names[i])
        
        if missing_info:
            raise ValueError(f"Digest summary missing: {', '.join(missing_info)}")
        
        return v


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(default="healthy", description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Response model for error cases."""
    
    error: str = Field(..., description="Error type or category")
    message: str = Field(..., description="Human-readable error message")
    details: Dict = Field(default_factory=dict, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")
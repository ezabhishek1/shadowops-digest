"""
ShadowOps Digest FastAPI Application

Main application entry point for the AI-driven ticket analysis and summarization service.
Provides REST API endpoints for processing IT support tickets and generating actionable insights.
"""

import logging
import uuid
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import uvicorn

from models import TicketRequest, ClusterResult, HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="ShadowOps Digest API",
    description="AI-driven daily summary tool for IT support ticket analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# In-memory cache for digest results
# In production, this should be replaced with Redis or similar
digest_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_MINUTES = 60  # Cache results for 1 hour

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """
    Add correlation ID to all requests for tracing and logging.
    
    Generates a unique correlation ID for each request and adds it to
    the response headers for request tracing across the system.
    """
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    # Log request details
    logger.info(
        f"Request started - ID: {correlation_id}, "
        f"Method: {request.method}, Path: {request.url.path}"
    )
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Log response details
    logger.info(
        f"Request completed - ID: {correlation_id}, "
        f"Status: {response.status_code}"
    )
    
    return response


def generate_cache_key(request: TicketRequest) -> str:
    """
    Generate a cache key for the digest request.
    
    Creates a hash-based cache key from the request parameters to enable
    caching of identical requests and improve response times.
    
    Args:
        request: TicketRequest containing tickets and parameters
        
    Returns:
        SHA-256 hash string to use as cache key
    """
    # Create a normalized representation of the request
    cache_data = {
        "tickets": sorted(request.tickets),  # Sort for consistent hashing
        "avg_time_per_ticket_minutes": request.avg_time_per_ticket_minutes,
        "hourly_cost_usd": request.hourly_cost_usd
    }
    
    # Convert to JSON string and hash
    cache_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.sha256(cache_string.encode()).hexdigest()


def get_cached_result(cache_key: str) -> Optional[ClusterResult]:
    """
    Retrieve cached digest result if available and not expired.
    
    Args:
        cache_key: Cache key to look up
        
    Returns:
        Cached ClusterResult if available and valid, None otherwise
    """
    if cache_key not in digest_cache:
        return None
    
    cached_entry = digest_cache[cache_key]
    
    # Check if cache entry has expired
    cache_time = cached_entry.get("timestamp")
    if not cache_time:
        # Invalid cache entry, remove it
        del digest_cache[cache_key]
        return None
    
    # Handle both datetime objects and string timestamps
    if isinstance(cache_time, str):
        try:
            cache_time = datetime.fromisoformat(cache_time.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Invalid timestamp format, remove entry
            del digest_cache[cache_key]
            return None
    
    if isinstance(cache_time, datetime):
        expiry_time = cache_time + timedelta(minutes=CACHE_TTL_MINUTES)
        if datetime.utcnow() > expiry_time:
            # Cache expired, remove it
            del digest_cache[cache_key]
            return None
    
    # Return cached result
    try:
        return ClusterResult(**cached_entry["result"])
    except Exception as e:
        logger.warning(f"Failed to deserialize cached result: {e}")
        # Remove invalid cache entry
        del digest_cache[cache_key]
        return None


def cache_result(cache_key: str, result: ClusterResult) -> None:
    """
    Cache a digest result for future use.
    
    Args:
        cache_key: Cache key to store under
        result: ClusterResult to cache
    """
    try:
        digest_cache[cache_key] = {
            "result": result.dict(),
            "timestamp": datetime.utcnow()
        }
        logger.info(f"Cached result with key: {cache_key[:16]}...")
    except Exception as e:
        logger.warning(f"Failed to cache result: {e}")


def cleanup_expired_cache() -> None:
    """
    Clean up expired cache entries to prevent memory leaks.
    
    This should be called periodically in production or replaced
    with a proper cache solution like Redis.
    """
    current_time = datetime.utcnow()
    expired_keys = []
    
    for cache_key, cached_entry in digest_cache.items():
        cache_time = cached_entry.get("timestamp")
        if cache_time:
            # Handle both datetime objects and string timestamps
            if isinstance(cache_time, str):
                try:
                    cache_time = datetime.fromisoformat(cache_time.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # Invalid timestamp format, mark for removal
                    expired_keys.append(cache_key)
                    continue
            
            if isinstance(cache_time, datetime):
                expiry_time = cache_time + timedelta(minutes=CACHE_TTL_MINUTES)
                if current_time > expiry_time:
                    expired_keys.append(cache_key)
    
    for key in expired_keys:
        del digest_cache[key]
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed field-level information.
    
    Converts validation errors into user-friendly error responses with
    specific field validation details for better API usability.
    """
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.warning(
        f"Validation error - ID: {correlation_id}, "
        f"Errors: {exc.errors()}"
    )
    
    error_details = {}
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_details[field_path] = error["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="validation_error",
            message="Request validation failed",
            details=error_details,
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent error response format.
    
    Provides standardized error responses for all HTTP exceptions
    while maintaining correlation IDs for request tracing.
    """
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        f"HTTP exception - ID: {correlation_id}, "
        f"Status: {exc.status_code}, Detail: {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            message=str(exc.detail),
            details={"status_code": exc.status_code},
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions with proper logging and error response.
    
    Catches all unhandled exceptions, logs them with full traceback,
    and returns a generic error response to avoid exposing internal details.
    """
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        f"Unexpected error - ID: {correlation_id}, "
        f"Type: {type(exc).__name__}, Message: {str(exc)}, "
        f"Traceback: {traceback.format_exc()}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred. Please try again later.",
            details={"correlation_id": correlation_id},
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns the current service status, timestamp, and version information
    for monitoring systems and container orchestration health checks.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )


@app.get("/cache/status")
async def cache_status():
    """
    Cache status endpoint for monitoring cache performance.
    
    Returns information about the current cache state including
    entry count and memory usage for operational monitoring.
    """
    # Clean up expired entries before reporting status
    cleanup_expired_cache()
    
    cache_info = {
        "cache_entries": len(digest_cache),
        "cache_ttl_minutes": CACHE_TTL_MINUTES,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Calculate approximate memory usage
    try:
        import sys
        total_size = sys.getsizeof(digest_cache)
        for key, value in digest_cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        cache_info["approximate_memory_kb"] = round(total_size / 1024, 2)
    except Exception:
        cache_info["approximate_memory_kb"] = "unknown"
    
    return cache_info


@app.post("/digest", response_model=ClusterResult)
async def generate_digest(request: TicketRequest, req: Request):
    """
    Generate AI-powered digest from IT support tickets.
    
    Processes a list of support tickets to identify patterns, cluster similar issues,
    generate actionable improvement suggestions, and calculate potential cost savings.
    Includes caching mechanism for repeated requests with identical parameters.
    
    Args:
        request: TicketRequest containing tickets, timing, and cost parameters
        req: FastAPI Request object for correlation tracking
    
    Returns:
        ClusterResult: Analysis results including clusters, suggestions, and metrics
    
    Raises:
        HTTPException: For processing errors or timeouts
    """
    import asyncio
    from clustering import cluster_tickets
    from suggestion import select_suggestion
    from calculator import calculate_time_cost
    from summarizer import generate_digest_summary
    
    correlation_id = getattr(req.state, 'correlation_id', 'unknown')
    
    logger.info(
        f"Digest generation started - ID: {correlation_id}, "
        f"Tickets: {len(request.tickets)}, "
        f"Avg time: {request.avg_time_per_ticket_minutes}min, "
        f"Hourly cost: ${request.hourly_cost_usd}"
    )
    
    # Generate cache key for this request
    cache_key = generate_cache_key(request)
    
    # Check for cached result
    cached_result = get_cached_result(cache_key)
    if cached_result:
        logger.info(f"Returning cached result - ID: {correlation_id}, Cache key: {cache_key[:16]}...")
        return cached_result
    
    # Clean up expired cache entries periodically
    cleanup_expired_cache()
    
    try:
        # Set 30-second timeout for the entire processing pipeline
        async def process_digest():
            # Step 1: Cluster tickets by root cause
            logger.info(f"Starting ticket clustering - ID: {correlation_id}")
            clusters = cluster_tickets(request.tickets)
            logger.info(f"Clustering completed - ID: {correlation_id}, Clusters: {len(clusters)}")
            
            # Step 2: Generate improvement suggestion
            logger.info(f"Generating suggestion - ID: {correlation_id}")
            suggestion = select_suggestion(clusters, request.tickets)
            logger.info(f"Suggestion generated - ID: {correlation_id}")
            
            # Step 3: Calculate time and cost metrics
            logger.info(f"Calculating costs - ID: {correlation_id}")
            time_wasted, cost_saved = calculate_time_cost(
                clusters, request.avg_time_per_ticket_minutes, request.hourly_cost_usd
            )
            logger.info(f"Cost calculation completed - ID: {correlation_id}")
            
            # Step 4: Generate digest summary
            logger.info(f"Generating summary - ID: {correlation_id}")
            digest_summary = generate_digest_summary(clusters, suggestion, time_wasted, cost_saved)
            logger.info(f"Summary generated - ID: {correlation_id}")
            
            # Create final result
            result = ClusterResult(
                clusters=clusters,
                suggestion=suggestion,
                time_wasted_hours=time_wasted,
                cost_saved_usd=cost_saved,
                digest_summary=digest_summary
            )
            
            return result
        
        # Execute with timeout
        result = await asyncio.wait_for(process_digest(), timeout=30.0)
        
        # Cache the result for future requests
        cache_result(cache_key, result)
        
        logger.info(
            f"Digest generation completed - ID: {correlation_id}, "
            f"Clusters: {len(result.clusters)}, "
            f"Time saved: {result.time_wasted_hours}h, "
            f"Cost saved: ${result.cost_saved_usd}"
        )
        
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"Digest generation timeout - ID: {correlation_id}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Request processing timed out after 30 seconds. Please try again with fewer tickets."
        )
        
    except ValidationError as e:
        logger.error(f"Validation error in digest generation - ID: {correlation_id}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data generated during processing"
        )
    
    except Exception as e:
        logger.error(f"Error in digest generation - ID: {correlation_id}, Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate digest. Please try again."
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
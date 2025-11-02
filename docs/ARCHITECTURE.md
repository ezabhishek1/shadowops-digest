# Architecture Overview

## System Architecture

ShadowOps Digest follows a modern three-tier architecture with clear separation of concerns.

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend Layer                       │
│                   (React + TailwindCSS)                  │
│  - User Interface                                        │
│  - State Management                                      │
│  - API Integration                                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     │
┌────────────────────▼────────────────────────────────────┐
│                    Backend Layer                         │
│                   (FastAPI + Python)                     │
│  - API Endpoints                                         │
│  - Business Logic                                        │
│  - Data Validation                                       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──────┐ ┌──▼──────┐ ┌──▼──────────┐
│   OpenAI     │ │Database │ │  ML Models  │
│     API      │ │(Postgres)│ │(scikit-learn)│
└──────────────┘ └─────────┘ └─────────────┘
```

## Backend Architecture

### Core Modules

**main.py** - Application Entry Point
- FastAPI application setup
- Middleware configuration
- Route definitions
- Exception handlers
- CORS configuration

**models.py** - Data Models
- Pydantic models for validation
- Request/response schemas
- Data type definitions

**clustering.py** - Clustering Engine
- OpenAI embedding generation
- FAISS vector similarity search
- Fallback to local ML clustering
- Cluster labeling and categorization

**suggestion.py** - Suggestion Generator
- Analyzes ticket patterns
- Generates actionable recommendations
- Uses GPT-4 for intelligent suggestions

**calculator.py** - Cost Calculator
- Time waste calculations
- Cost savings estimates
- ROI projections

**summarizer.py** - Digest Summarizer
- Generates human-readable summaries
- Combines all analysis results
- Formats output for display

### Request Flow

1. Client sends POST request to `/digest` endpoint
2. FastAPI validates request using Pydantic models
3. Clustering module processes tickets:
   - Generates embeddings (OpenAI or local)
   - Groups similar tickets
   - Labels clusters
4. Suggestion module analyzes patterns
5. Calculator computes savings
6. Summarizer creates final digest
7. Response sent back to client

### Error Handling

- Correlation IDs for request tracing
- Structured logging throughout
- Graceful fallbacks (OpenAI → local ML)
- Comprehensive error messages
- HTTP status codes for different error types

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── DigestCard.jsx      # Displays digest results
│   ├── Layout.jsx          # Page layout wrapper
│   └── ApiStatus.jsx       # API health indicator
├── pages/
│   └── Home.jsx            # Main application page
├── hooks/
│   └── useDigest.js        # Custom hook for API calls
└── App.jsx                 # Root component
```

### State Management

- React hooks for local state
- Custom `useDigest` hook for API integration
- No global state management (not needed for current scope)

### Data Flow

1. User enters tickets in form
2. Form submission triggers `useDigest` hook
3. Hook makes API call to backend
4. Loading state displayed during processing
5. Results rendered in DigestCard component
6. Error handling for failed requests

## Data Models

### Request Model
```python
class DigestRequest:
    tickets: List[str]
    avg_time_per_ticket_minutes: float
    hourly_cost_usd: float
```

### Response Model
```python
class DigestResponse:
    clusters: Dict[str, List[int]]
    suggestion: str
    time_wasted_hours: float
    cost_saved_usd: float
    digest_summary: str
```

## Security Considerations

1. **API Keys**: Stored in environment variables
2. **CORS**: Configured for specific origins
3. **Input Validation**: Pydantic models validate all inputs
4. **Rate Limiting**: Should be added for production
5. **Authentication**: Not implemented (future enhancement)

## Scalability Considerations

### Current Limitations
- Synchronous processing
- In-memory clustering
- No caching
- Single instance deployment

### Future Improvements
- Async processing with Celery
- Redis caching for embeddings
- Horizontal scaling with load balancer
- Database for ticket history
- Message queue for high volume

## Deployment Architecture

### Development
- Docker Compose orchestration
- Hot reload for both services
- Local PostgreSQL instance

### Production (Recommended)
- Container orchestration (Kubernetes/ECS)
- Managed database (RDS/Cloud SQL)
- CDN for frontend assets
- API Gateway for rate limiting
- Monitoring and logging (CloudWatch/Datadog)

## Technology Choices

### Why FastAPI?
- Modern Python framework
- Automatic API documentation
- Built-in validation with Pydantic
- High performance (async support)
- Type hints and IDE support

### Why React?
- Component-based architecture
- Large ecosystem
- Excellent developer experience
- Strong community support

### Why OpenAI?
- State-of-the-art embeddings
- High-quality text generation
- Easy integration
- Fallback to local ML available

## Performance Characteristics

- **Clustering**: O(n log n) with FAISS
- **Embedding Generation**: ~100ms per ticket (OpenAI)
- **Suggestion Generation**: ~2-3 seconds (GPT-4)
- **Total Processing**: ~5-10 seconds for 20 tickets

## Monitoring and Observability

### Logging
- Structured JSON logs
- Correlation IDs for request tracing
- Different log levels (INFO, WARNING, ERROR)

### Metrics (Future)
- Request latency
- Error rates
- Clustering accuracy
- API usage costs

### Health Checks
- `/health` endpoint for service status
- Database connectivity check
- External API availability

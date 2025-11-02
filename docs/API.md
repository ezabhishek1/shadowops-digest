# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com/api`

## Authentication

Currently, no authentication is required. Future versions will implement API key authentication.

## Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is down

---

### Generate Digest

Analyze IT support tickets and generate insights.

**Endpoint:** `POST /digest`

**Request Body:**
```json
{
  "tickets": [
    "VPN connection failing on Windows 10",
    "Cannot access shared drive",
    "Outlook keeps crashing",
    "Password reset for user account",
    "Printer not responding in Building A"
  ],
  "avg_time_per_ticket_minutes": 30,
  "hourly_cost_usd": 40.0
}
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tickets` | array[string] | Yes | List of ticket descriptions (1-100 tickets) |
| `avg_time_per_ticket_minutes` | float | Yes | Average time spent per ticket in minutes (> 0) |
| `hourly_cost_usd` | float | Yes | Hourly cost in USD (> 0) |

**Response:**
```json
{
  "clusters": {
    "Network Connectivity Issues": [0, 1],
    "Application Crashes": [2],
    "Authentication Problems": [3],
    "Hardware Issues": [4]
  },
  "suggestion": "Create a self-service VPN troubleshooting guide with step-by-step instructions for common Windows 10 connection issues. This could reduce ticket volume by 40%.",
  "time_wasted_hours": 2.5,
  "cost_saved_usd": 100.0,
  "digest_summary": "Analyzed 5 tickets across 4 categories. Primary issue: Network Connectivity (40%). Recommendation: VPN self-service guide. Potential savings: 2.5 hours, $100."
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `clusters` | object | Dictionary mapping cluster names to ticket indices |
| `suggestion` | string | Actionable improvement recommendation |
| `time_wasted_hours` | float | Estimated time wasted on repetitive issues |
| `cost_saved_usd` | float | Potential cost savings from implementing suggestion |
| `digest_summary` | string | Human-readable summary of the analysis |

**Status Codes:**
- `200 OK` - Successful analysis
- `400 Bad Request` - Invalid input data
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - External service (OpenAI) unavailable

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong",
  "correlation_id": "abc123-def456-ghi789"
}
```

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Test API calls directly in the browser
- Download OpenAPI specification

## Rate Limiting

**Current:** No rate limiting implemented

**Recommended for Production:**
- 100 requests per minute per IP
- 1000 requests per hour per API key
- Burst allowance: 10 requests

## CORS Configuration

**Development:**
- Allowed origins: `http://localhost:3000`, `http://localhost:8000`
- Allowed methods: GET, POST, OPTIONS
- Allowed headers: Content-Type, Authorization

**Production:**
- Configure specific allowed origins
- Enable credentials if needed
- Set appropriate cache duration

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message",
  "correlation_id": "unique-request-id",
  "field_errors": [  // Only for validation errors
    {
      "field": "tickets",
      "message": "List must contain at least 1 item"
    }
  ]
}
```

### Common Error Scenarios

**Empty Ticket List:**
```json
{
  "detail": "Tickets list cannot be empty",
  "correlation_id": "abc123"
}
```

**Invalid Time Value:**
```json
{
  "detail": "avg_time_per_ticket_minutes must be greater than 0",
  "correlation_id": "def456"
}
```

**OpenAI API Error:**
```json
{
  "detail": "Failed to generate embeddings. Falling back to local clustering.",
  "correlation_id": "ghi789"
}
```

## Request Examples

### cURL

```bash
curl -X POST "http://localhost:8000/digest" \
  -H "Content-Type: application/json" \
  -d '{
    "tickets": [
      "VPN not connecting",
      "Password reset needed",
      "Printer offline"
    ],
    "avg_time_per_ticket_minutes": 30,
    "hourly_cost_usd": 40.0
  }'
```

### Python

```python
import requests

url = "http://localhost:8000/digest"
data = {
    "tickets": [
        "VPN not connecting",
        "Password reset needed",
        "Printer offline"
    ],
    "avg_time_per_ticket_minutes": 30,
    "hourly_cost_usd": 40.0
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

### JavaScript (Fetch)

```javascript
const url = 'http://localhost:8000/digest';
const data = {
  tickets: [
    'VPN not connecting',
    'Password reset needed',
    'Printer offline'
  ],
  avg_time_per_ticket_minutes: 30,
  hourly_cost_usd: 40.0
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data),
})
  .then(response => response.json())
  .then(result => console.log(result))
  .catch(error => console.error('Error:', error));
```

## Best Practices

1. **Batch Processing**: Send multiple tickets in a single request rather than individual requests
2. **Error Handling**: Always handle both network errors and API errors
3. **Timeouts**: Set appropriate timeouts (recommend 30 seconds for digest generation)
4. **Retry Logic**: Implement exponential backoff for failed requests
5. **Correlation IDs**: Log correlation IDs for debugging
6. **Input Validation**: Validate data on client side before sending

## Performance Tips

- Optimal batch size: 10-50 tickets per request
- Expect 5-10 seconds processing time for 20 tickets
- OpenAI API calls are the primary bottleneck
- Consider caching results for identical ticket sets

## Versioning

Current version: `v1` (implicit in base URL)

Future versions will use explicit versioning:
- `http://localhost:8000/v1/digest`
- `http://localhost:8000/v2/digest`

## Support

For API issues or questions:
- GitHub Issues: [Report a bug](https://github.com/YOUR_USERNAME/shadowops-digest/issues)
- Documentation: [Full docs](https://github.com/YOUR_USERNAME/shadowops-digest/wiki)

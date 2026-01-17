# Step 6: REST API Backend - Setup Guide

## Overview
FastAPI-based REST API backend that exposes all AI features (chat, recommendations, sentiment analysis, predictions) as HTTP endpoints.

## Prerequisites
- Python 3.8+
- All dependencies from previous steps
- FastAPI and related packages installed

## Installation

### 1. Install Dependencies
```powershell
# Install FastAPI and dependencies
pip install fastapi uvicorn[standard] pydantic python-multipart slowapi python-jose[cryptography]
```

### 2. Environment Configuration
Create/update `.env` file in project root:
```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# API Security
API_KEY=your-secret-api-key-change-in-production
SECRET_KEY=your-jwt-secret-key-change-in-production

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:8080
```

## Running the API

### Option 1: Using Uvicorn (Recommended)
```powershell
# From project root directory
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Direct Python
```powershell
python api/main.py
```

### Option 3: With Custom Configuration
```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8080 --log-level debug
```

## Accessing the API

### Interactive Documentation (Swagger UI)
```
http://localhost:8000/docs
```
- Try out endpoints directly
- See request/response schemas
- Test with API key authentication

### Alternative Documentation (ReDoc)
```
http://localhost:8000/redoc
```
- Clean, organized documentation
- Full API reference

### Health Check
```
http://localhost:8000/
```

## API Authentication

### Using API Key (Header)
All endpoints require authentication via API key:

```bash
# Example using curl
curl -X POST "http://localhost:8000/api/chat" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "message": "Hello"}'
```

### Development Mode
For development, you can use the default key: `dev-api-key-change-in-production`

## API Endpoints

### 1. Chat Endpoints (`/api/chat`)
- `POST /api/chat` - Send message to AI advisor
- `POST /api/chat/reset` - Clear conversation history
- `GET /api/chat/history/{student_id}` - Get chat history
- `GET /api/chat/sessions` - List active sessions

### 2. Recommendation Endpoints (`/api/recommend`)
- `POST /api/recommend` - Get personalized course recommendations
- `GET /api/recommend/explain/{course}` - Get detailed course explanation
- `POST /api/recommend/learning-path` - Generate learning path
- `GET /api/recommend/courses` - Get all available courses
- `POST /api/recommend/interactive` - Conversational recommendations

### 3. Analysis Endpoints (`/api/analysis`)
- `POST /api/analysis/sentiment` - Analyze text sentiment
- `POST /api/analysis/classify` - Classify text into categories
- `POST /api/analysis/feedback` - Comprehensive feedback analysis
- `POST /api/analysis/topics` - Extract topics from text
- `POST /api/analysis/batch-sentiment` - Batch sentiment analysis
- `POST /api/analysis/batch-classify` - Batch text classification
- `GET /api/analysis/reports/{report_id}` - Retrieve analysis reports

### 4. Student Endpoints (`/api/students`)
- `GET /api/students` - List all students
- `GET /api/students/{id}` - Get student profile
- `GET /api/students/{id}/courses` - Get student's courses
- `GET /api/students/{id}/performance` - Get performance metrics
- `POST /api/students/{id}/enroll` - Enroll in course

### 5. Prediction Endpoints (`/api/predict`)
- `POST /api/predict/performance` - Predict grade for course
- `POST /api/predict/risk` - Assess at-risk status
- `GET /api/predict/features` - Get ML feature importance
- `POST /api/predict/batch` - Batch performance predictions

## Rate Limiting

Default rate limits:
- Global: 100 requests/minute, 1000 requests/hour
- Chat: 30 requests/minute
- Batch operations: 10-20 requests/minute
- Simple queries: 60 requests/minute

## Testing the API

### Using Python Requests
```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "dev-api-key-change-in-production"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Test chat endpoint
response = requests.post(
    f"{API_URL}/api/chat",
    headers=headers,
    json={
        "student_id": 1,
        "message": "What courses should I take next?"
    }
)

print(response.json())
```

### Using JavaScript/Fetch
```javascript
const API_URL = "http://localhost:8000";
const API_KEY = "dev-api-key-change-in-production";

async function chatWithAdvisor(studentId, message) {
    const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            student_id: studentId,
            message: message
        })
    });
    
    return await response.json();
}

// Usage
chatWithAdvisor(1, "Hello").then(console.log);
```

## Troubleshooting

### Issue: Port already in use
```powershell
# Use different port
uvicorn api.main:app --reload --port 8001
```

### Issue: Module not found
```powershell
# Ensure you're in the correct directory
cd c:\Users\User\Desktop\ai-data-roadmap\student-portal

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: OpenAI API errors
- Check `.env` file has valid `OPENAI_API_KEY`
- Verify API key is active and has credits

### Issue: Rate limit exceeded
- Wait for rate limit window to reset
- Increase limits in `api/config.py`

## Project Structure
```
api/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── models.py              # Pydantic models
├── middleware/
│   ├── auth.py           # Authentication & rate limiting
│   └── error_handler.py  # Error handlers
└── routes/
    ├── chat.py           # Chat endpoints
    ├── recommendations.py # Recommendation endpoints
    ├── analysis.py       # Analysis endpoints
    ├── students.py       # Student endpoints
    └── predictions.py    # Prediction endpoints
```

## Next Steps
1. Test all endpoints using Swagger UI
2. Implement frontend integration (Step 7)
3. Add database for persistent storage
4. Deploy to production (Step 8)

## Security Notes
- Change default API_KEY in production
- Use environment variables for secrets
- Enable HTTPS in production
- Configure proper CORS origins
- Implement rate limiting per user
- Add request logging

## Performance Tips
- Use async operations where possible
- Cache frequently accessed data
- Implement database connection pooling
- Use Redis for session management in production
- Monitor endpoint response times

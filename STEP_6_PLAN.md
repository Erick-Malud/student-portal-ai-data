# Level 5 Step 6: REST API Backend - Implementation Plan

**Objective:** Build a production-ready REST API to expose all AI features as web services

**Estimated Time:** 4-5 hours  
**Difficulty:** Intermediate to Advanced

---

## 🎯 What We'll Build

A **FastAPI-based REST API** that provides:
- Course recommendations endpoint
- AI student advisor chat endpoint
- Sentiment analysis endpoint
- Text classification endpoint
- Feedback analysis endpoint
- Student data endpoints
- ML prediction endpoints

**Why FastAPI?**
- ✅ Modern, fast Python web framework
- ✅ Automatic API documentation (Swagger UI)
- ✅ Type validation with Pydantic
- ✅ Async support for high performance
- ✅ Easy to learn and use

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Applications                     │
│           (React, Mobile, Desktop, CLI, etc.)                │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/HTTPS
                     v
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                   (Port 8000 default)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Endpoints (Routes)                    │ │
│  │                                                        │ │
│  │  POST /api/chat                  - AI advisor chat    │ │
│  │  POST /api/recommend             - Recommendations    │ │
│  │  POST /api/analyze-sentiment     - Sentiment analysis │ │
│  │  POST /api/analyze-feedback      - Full feedback      │ │
│  │  POST /api/classify-text         - Text classifier    │ │
│  │  GET  /api/student/{id}          - Student profile    │ │
│  │  POST /api/predict-performance   - ML predictions     │ │
│  │  GET  /api/courses               - Course catalog     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Middleware & Security                        │ │
│  │  • CORS (Cross-Origin Resource Sharing)               │ │
│  │  • Rate Limiting (prevent abuse)                      │ │
│  │  • Authentication (API keys/JWT)                      │ │
│  │  • Request Validation (Pydantic models)               │ │
│  │  • Error Handling (consistent responses)              │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                    AI Services Layer                         │
│  • CourseRecommender      • SentimentAnalyzer               │
│  • AIStudentAdvisor       • TextClassifier                  │
│  • FeedbackAnalyzer       • MLPredictor                     │
│  • RecommendationEngine   • EmbeddingsManager               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
│  • students.json          • course_db.py                    │
│  • student_feedback.json  • portal_db.py                    │
│  • ML models              • Embeddings cache                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Files to Create

### **1. api/main.py** (~300 lines)
- FastAPI application setup
- CORS configuration
- API documentation metadata
- Health check endpoint
- Error handlers

### **2. api/models.py** (~200 lines)
- Pydantic models for request/response validation
- ChatRequest, ChatResponse
- RecommendationRequest, RecommendationResponse
- SentimentRequest, SentimentResponse
- FeedbackRequest, FeedbackResponse

### **3. api/routes/chat.py** (~150 lines)
- POST /api/chat - AI advisor endpoint
- POST /api/chat/reset - Reset conversation
- GET /api/chat/history/{student_id} - Get chat history

### **4. api/routes/recommendations.py** (~200 lines)
- POST /api/recommend - Get course recommendations
- POST /api/recommend/explain/{course} - Explain recommendation
- GET /api/recommend/learning-path - Generate learning path

### **5. api/routes/analysis.py** (~250 lines)
- POST /api/analyze-sentiment - Single text sentiment
- POST /api/analyze-feedback - Full feedback analysis
- POST /api/classify-text - Classify message
- POST /api/extract-topics - Topic extraction
- GET /api/analysis/reports/{report_id} - Get saved reports

### **6. api/routes/students.py** (~150 lines)
- GET /api/students/{id} - Student profile
- GET /api/students/{id}/courses - Student courses
- GET /api/students/{id}/performance - Performance data
- POST /api/students/{id}/enroll - Enroll in course

### **7. api/routes/predictions.py** (~100 lines)
- POST /api/predict-performance - ML grade prediction
- POST /api/predict-risk - At-risk prediction
- GET /api/predict/features - Feature importance

### **8. api/middleware/auth.py** (~100 lines)
- API key authentication
- Rate limiting
- Request logging

### **9. api/middleware/error_handler.py** (~100 lines)
- Global exception handling
- Consistent error responses
- Error logging

### **10. api/config.py** (~50 lines)
- API configuration
- Environment variables
- CORS settings
- Rate limits

---

## 🔌 API Endpoints Specification

### **Chat Endpoints**

**POST /api/chat**
```json
Request:
{
  "student_id": 1,
  "message": "What courses should I take next?",
  "session_id": "optional-session-uuid"
}

Response:
{
  "response": "Based on your progress, I recommend...",
  "recommendations": ["Course A", "Course B"],
  "session_id": "abc-123-def",
  "timestamp": "2026-01-03T14:30:00Z"
}
```

---

### **Recommendation Endpoints**

**POST /api/recommend**
```json
Request:
{
  "student_id": 1,
  "num_recommendations": 5,
  "strategy": "hybrid",  // or "semantic", "ml", "collaborative"
  "filters": {
    "difficulty": ["beginner", "intermediate"],
    "category": ["programming", "data_science"]
  }
}

Response:
{
  "recommendations": [
    {
      "course_name": "Advanced Python",
      "score": 0.89,
      "confidence": 0.92,
      "reasoning": "Similar to courses you've completed...",
      "difficulty": "intermediate",
      "prerequisites": ["Python Fundamentals"],
      "description": "Master advanced Python concepts..."
    }
  ],
  "strategy_used": "hybrid",
  "generated_at": "2026-01-03T14:30:00Z"
}
```

**POST /api/recommend/learning-path**
```json
Request:
{
  "student_id": 1,
  "goal": "become a machine learning engineer",
  "num_courses": 8
}

Response:
{
  "goal": "become a machine learning engineer",
  "current_level": "beginner",
  "estimated_duration": "6-8 months",
  "path": [
    {
      "step": 1,
      "course": "Python Fundamentals",
      "status": "completed",
      "duration": "4 weeks"
    },
    {
      "step": 2,
      "course": "Data Structures & Algorithms",
      "status": "recommended",
      "duration": "6 weeks"
    }
  ]
}
```

---

### **Analysis Endpoints**

**POST /api/analyze-sentiment**
```json
Request:
{
  "text": "I love this course! The instructor is amazing.",
  "options": {
    "include_emotion": true,
    "include_reasoning": true
  }
}

Response:
{
  "sentiment": "positive",
  "score": 0.95,
  "emotion": "joy",
  "confidence": 0.97,
  "reasoning": "Strong positive language with enthusiasm"
}
```

**POST /api/analyze-feedback**
```json
Request:
{
  "feedback": [
    {
      "student_id": 1,
      "text": "Great course!",
      "course": "Python Fundamentals",
      "timestamp": "2026-01-03T10:00:00Z"
    }
  ],
  "generate_report": true
}

Response:
{
  "summary": {
    "total_feedback": 20,
    "positive_percentage": 65.0,
    "negative_percentage": 25.0,
    "neutral_percentage": 10.0,
    "average_score": 0.42
  },
  "alerts": [
    {
      "student_id": 7,
      "priority": "critical",
      "category": "at_risk_alert",
      "text": "Thinking about dropping..."
    }
  ],
  "topics": [
    {
      "topic": "Homework Difficulty",
      "frequency": 0.45,
      "sentiment": "negative"
    }
  ],
  "report_id": "report_20260103_143000",
  "report_url": "/api/analysis/reports/report_20260103_143000"
}
```

---

### **Student Endpoints**

**GET /api/students/{student_id}**
```json
Response:
{
  "student_id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "gpa": 3.7,
  "completed_courses": ["Python Fundamentals", "Web Development"],
  "enrolled_courses": ["Data Structures"],
  "total_courses": 3,
  "join_date": "2025-09-01"
}
```

**GET /api/students/{student_id}/performance**
```json
Response:
{
  "student_id": 1,
  "gpa": 3.7,
  "total_credits": 12,
  "course_grades": [
    {
      "course": "Python Fundamentals",
      "grade": 88.5,
      "status": "completed"
    }
  ],
  "study_time_per_week": 15,
  "assignment_completion_rate": 0.95,
  "predicted_next_semester_gpa": 3.8
}
```

---

### **Prediction Endpoints**

**POST /api/predict-performance**
```json
Request:
{
  "student_id": 1,
  "course": "Machine Learning Fundamentals"
}

Response:
{
  "student_id": 1,
  "course": "Machine Learning Fundamentals",
  "predicted_grade": 85.3,
  "confidence": 0.82,
  "risk_level": "low",
  "recommendations": [
    "Course matches your skill level",
    "Prerequisites completed successfully"
  ]
}
```

---

## 🔒 Security Features

### **1. API Key Authentication**
```python
# Each request must include API key in header
headers = {
    "X-API-Key": "your-api-key-here"
}
```

### **2. Rate Limiting**
- 100 requests per minute per API key
- 1000 requests per hour
- Prevent abuse and DDoS

### **3. CORS Configuration**
```python
# Allow specific origins
allowed_origins = [
    "http://localhost:3000",  # React dev
    "https://yourdomain.com"  # Production
]
```

### **4. Input Validation**
- Pydantic models validate all inputs
- Type checking
- Range validation
- Required field enforcement

### **5. Error Handling**
```json
// Consistent error response format
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid student_id",
    "details": {
      "field": "student_id",
      "issue": "Must be positive integer"
    }
  },
  "timestamp": "2026-01-03T14:30:00Z"
}
```

---

## 📊 API Documentation (Auto-Generated)

FastAPI automatically generates:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Features:
- Interactive testing
- Request/response examples
- Model schemas
- Authentication testing

---

## 🧪 Testing Strategy

### **1. Unit Tests** (pytest)
```python
def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "student_id": 1,
        "message": "Hello"
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### **2. Integration Tests**
```python
def test_recommendation_flow():
    # Create student
    # Get recommendations
    # Verify recommendations match student profile
```

### **3. Load Testing**
- Test with 100+ concurrent users
- Measure response times
- Identify bottlenecks

---

## 🚀 Deployment Plan (Step 8 Preview)

### **Platform Options:**
1. **Railway** (Easiest)
   - Free tier available
   - Automatic deployments from GitHub
   - Built-in database

2. **Render** (Popular)
   - Free tier with limitations
   - Easy Python deployment
   - Good documentation

3. **Heroku** (Classic)
   - Well-established
   - Add-ons available
   - Paid plans needed

4. **AWS/GCP/Azure** (Enterprise)
   - Most powerful
   - Requires more setup
   - Best for scale

---

## 💰 Cost Estimates

**Development (Local):**
- OpenAI API: $0.50-2.00/day during testing
- FastAPI: Free
- Total: Minimal

**Production (1000 users/month):**
- API Hosting: $0-15/month (Railway/Render free tier)
- OpenAI API: $20-50/month
- Database: $0-10/month
- **Total: ~$20-75/month**

Very affordable for a full AI-powered platform! 💰

---

## 📝 Implementation Steps

### **Phase 1: Setup (30 min)**
1. Install FastAPI and dependencies
2. Create project structure
3. Setup main.py with basic configuration
4. Test with hello world endpoint

### **Phase 2: Core Endpoints (2 hours)**
5. Implement chat endpoint
6. Implement recommendation endpoint
7. Implement sentiment analysis endpoint
8. Test each endpoint

### **Phase 3: Additional Features (1.5 hours)**
9. Student endpoints
10. Prediction endpoints
11. Feedback analysis endpoint
12. API documentation refinement

### **Phase 4: Security & Polish (1 hour)**
13. Add authentication
14. Implement rate limiting
15. Error handling
16. CORS configuration

### **Phase 5: Testing (30 min)**
17. Write tests
18. Manual testing
19. Documentation
20. Prepare for deployment

---

## ✅ Success Criteria

By the end of Step 6, you'll have:
- ✅ Fully functional REST API with 8+ endpoints
- ✅ Automatic API documentation (Swagger UI)
- ✅ Authentication and rate limiting
- ✅ All AI features accessible via HTTP
- ✅ Input validation and error handling
- ✅ Ready for frontend integration
- ✅ Deployment-ready code

---

## 🎯 What You'll Learn

**Technical Skills:**
- REST API design principles
- FastAPI framework
- Pydantic data validation
- API authentication
- Rate limiting
- CORS configuration
- API documentation
- Async programming in Python

**Software Engineering:**
- API design patterns
- Microservices architecture
- Request/response modeling
- Error handling strategies
- Security best practices
- Testing strategies

---

## 🔮 Next Steps After Step 6

**Step 7: Frontend Integration (React)**
- Build chat interface
- Course recommendation UI
- Admin dashboard
- Student portal

**Step 8: Deployment**
- Deploy API to cloud
- Configure environment variables
- Set up monitoring
- Go live! 🚀

---

## 📚 Required Dependencies

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
python-multipart==0.0.6
slowapi==0.1.9  # Rate limiting
python-jose[cryptography]==3.3.0  # JWT tokens
```

---

## 🎉 Why This Step is Exciting

After Step 6, you'll have:
- ✨ A **real web service** that anyone can use
- 🌐 API endpoints accessible from any programming language
- 📱 Ready for mobile, web, or desktop apps
- 🔌 Easily testable with tools like Postman
- 📊 Beautiful auto-generated documentation
- 🚀 Production-ready architecture

**Your AI features will be accessible to the world!** 🌍

---

**Ready to build the API? Let's turn your AI features into a web service!** 🚀

# Step 6: REST API Backend - Example API Calls

## Table of Contents
1. [Chat Examples](#chat-examples)
2. [Recommendation Examples](#recommendation-examples)
3. [Analysis Examples](#analysis-examples)
4. [Student Examples](#student-examples)
5. [Prediction Examples](#prediction-examples)

---

## Chat Examples

### 1. Send Chat Message
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "message": "What courses should I take to improve my data science skills?"
  }'
```

**Response:**
```json
{
  "response": "Based on your current profile...",
  "session_id": "uuid-here",
  "recommendations": ["Machine Learning Fundamentals", "Python for Data Science"],
  "timestamp": "2025-06-15T10:30:00"
}
```

### 2. Get Chat History
```bash
curl -X GET "http://localhost:8000/api/chat/history/1?limit=10" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "student_id": 1,
  "messages": [
    {
      "role": "user",
      "content": "What courses should I take?",
      "timestamp": "2025-06-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "Based on your profile...",
      "timestamp": "2025-06-15T10:30:05"
    }
  ],
  "total_messages": 2
}
```

---

## Recommendation Examples

### 1. Get Personalized Recommendations
```bash
curl -X POST "http://localhost:8000/api/recommend" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "top_n": 5,
    "strategy": "hybrid",
    "difficulty_filter": "intermediate",
    "category_filter": "data_science"
  }'
```

**Response:**
```json
{
  "student_id": 1,
  "recommendations": [
    {
      "course": "Machine Learning Fundamentals",
      "score": 0.95,
      "reason": "Matches your skills and interests in AI",
      "difficulty": "intermediate",
      "category": "data_science"
    },
    {
      "course": "Deep Learning with PyTorch",
      "score": 0.89,
      "reason": "Natural progression after ML Fundamentals",
      "difficulty": "advanced",
      "category": "data_science"
    }
  ],
  "strategy_used": "hybrid",
  "timestamp": "2025-06-15T10:35:00"
}
```

### 2. Get Course Explanation
```bash
curl -X GET "http://localhost:8000/api/recommend/explain/Machine%20Learning%20Fundamentals" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "course": "Machine Learning Fundamentals",
  "explanation": "This course introduces core concepts of machine learning including supervised and unsupervised learning, regression, classification, and neural networks. Prerequisites include Python programming and basic statistics.",
  "difficulty": "intermediate",
  "prerequisites": ["Python Programming", "Statistics Basics"],
  "learning_outcomes": [
    "Understand ML algorithms",
    "Build predictive models",
    "Evaluate model performance"
  ]
}
```

### 3. Generate Learning Path
```bash
curl -X POST "http://localhost:8000/api/recommend/learning-path" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "goal": "Become a Machine Learning Engineer"
  }'
```

**Response:**
```json
{
  "student_id": 1,
  "goal": "Become a Machine Learning Engineer",
  "path": [
    {
      "step": 1,
      "course": "Python Programming",
      "duration": "8 weeks",
      "status": "completed"
    },
    {
      "step": 2,
      "course": "Machine Learning Fundamentals",
      "duration": "12 weeks",
      "status": "recommended"
    },
    {
      "step": 3,
      "course": "Deep Learning",
      "duration": "10 weeks",
      "status": "future"
    }
  ],
  "estimated_completion": "6 months"
}
```

---

## Analysis Examples

### 1. Sentiment Analysis
```bash
curl -X POST "http://localhost:8000/api/analysis/sentiment" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This course is amazing! I learned so much.",
    "include_emotions": true,
    "include_reasoning": true
  }'
```

**Response:**
```json
{
  "text": "This course is amazing! I learned so much.",
  "sentiment": "positive",
  "score": 0.95,
  "confidence": 0.92,
  "emotions": {
    "joy": 0.8,
    "excitement": 0.6,
    "satisfaction": 0.7
  },
  "reasoning": "Enthusiastic language with positive adjectives and learning progress indication"
}
```

### 2. Text Classification
```bash
curl -X POST "http://localhost:8000/api/analysis/classify" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I need help with the assignment deadline",
    "include_priority": true
  }'
```

**Response:**
```json
{
  "text": "I need help with the assignment deadline",
  "category": "administrative",
  "confidence": 0.88,
  "priority": "medium",
  "suggested_action": "Forward to academic advisor"
}
```

### 3. Comprehensive Feedback Analysis
```bash
curl -X POST "http://localhost:8000/api/analysis/feedback" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": [
      {
        "student_id": 1,
        "course": "Python Programming",
        "text": "Great course but assignments are too hard",
        "rating": 4
      },
      {
        "student_id": 2,
        "course": "Python Programming",
        "text": "Instructor is excellent, learned a lot",
        "rating": 5
      }
    ],
    "generate_report": true
  }'
```

**Response:**
```json
{
  "summary": {
    "total_feedback": 2,
    "average_sentiment": 0.75,
    "positive_count": 2,
    "negative_count": 0,
    "neutral_count": 0,
    "average_rating": 4.5
  },
  "alerts": [
    {
      "type": "attention_needed",
      "message": "Assignment difficulty mentioned as concern",
      "severity": "medium",
      "affected_count": 1
    }
  ],
  "top_topics": [
    {"topic": "instructor quality", "frequency": 1},
    {"topic": "assignment difficulty", "frequency": 1}
  ],
  "report_id": "report_20250615_103000",
  "insights": [
    "Overall positive sentiment (75% positive)",
    "Assignment difficulty is a concern for some students",
    "Instructor quality highly praised"
  ]
}
```

### 4. Batch Sentiment Analysis
```bash
curl -X POST "http://localhost:8000/api/analysis/batch-sentiment" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "This course is excellent",
      "I am struggling with the material",
      "The instructor is helpful"
    ]
  }'
```

**Response:**
```json
{
  "results": [
    {"text": "This course is excellent", "sentiment": "positive", "score": 0.95},
    {"text": "I am struggling...", "sentiment": "negative", "score": 0.65},
    {"text": "The instructor is helpful", "sentiment": "positive", "score": 0.88}
  ],
  "summary": {
    "total": 3,
    "positive": 2,
    "negative": 1,
    "neutral": 0,
    "average_score": 0.83
  }
}
```

---

## Student Examples

### 1. Get Student Profile
```bash
curl -X GET "http://localhost:8000/api/students/1" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "student_id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "gpa": 3.7,
  "completed_courses": ["Python Programming", "Data Structures"],
  "enrolled_courses": ["Machine Learning Fundamentals"],
  "total_courses": 3,
  "join_date": "2024-09-01"
}
```

### 2. Get Student Courses
```bash
curl -X GET "http://localhost:8000/api/students/1/courses?status=all" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "student_id": 1,
  "courses": [
    {
      "course_name": "Python Programming",
      "status": "completed",
      "grade": 92.0
    },
    {
      "course_name": "Machine Learning Fundamentals",
      "status": "enrolled",
      "progress": 50.0
    }
  ],
  "total_courses": 2,
  "filter": "all"
}
```

### 3. Get Student Performance
```bash
curl -X GET "http://localhost:8000/api/students/1/performance" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "student_id": 1,
  "gpa": 3.7,
  "total_credits": 9,
  "course_grades": [
    {"course": "Python Programming", "grade": 92.0, "status": "completed"},
    {"course": "Data Structures", "grade": 88.0, "status": "completed"},
    {"course": "ML Fundamentals", "grade": 0.0, "status": "in_progress"}
  ],
  "study_time_per_week": 15.5,
  "assignment_completion_rate": 0.95,
  "predicted_next_semester_gpa": 3.8
}
```

### 4. Enroll in Course
```bash
curl -X POST "http://localhost:8000/api/students/1/enroll?course_name=Deep%20Learning" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "message": "Enrollment successful",
  "student_id": 1,
  "course": "Deep Learning",
  "timestamp": "2025-06-15T10:45:00"
}
```

### 5. List All Students
```bash
curl -X GET "http://localhost:8000/api/students?limit=10&offset=0" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "students": [
    {
      "student_id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "gpa": 3.7,
      "completed_courses_count": 2,
      "enrolled_courses_count": 1
    }
  ],
  "total": 50,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

---

## Prediction Examples

### 1. Predict Performance
```bash
curl -X POST "http://localhost:8000/api/predict/performance" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course": "Deep Learning"
  }'
```

**Response:**
```json
{
  "student_id": 1,
  "course": "Deep Learning",
  "predicted_grade": 87.5,
  "confidence": 0.82,
  "risk_level": "low",
  "recommendations": [
    "Course matches your skill level",
    "Prerequisites completed successfully"
  ]
}
```

### 2. Assess At-Risk Status
```bash
curl -X POST "http://localhost:8000/api/predict/risk?student_id=1" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "student_id": 1,
  "risk_level": "low",
  "risk_score": 0.15,
  "risk_factors": ["No significant risk factors identified"],
  "recommended_interventions": [
    "Continue current approach",
    "Maintain regular check-ins"
  ],
  "confidence": 0.85,
  "requires_immediate_action": false
}
```

### 3. Get Feature Importance
```bash
curl -X GET "http://localhost:8000/api/predict/features" \
  -H "X-API-Key: dev-api-key-change-in-production"
```

**Response:**
```json
{
  "features": [
    {"feature": "current_gpa", "importance": 0.45},
    {"feature": "study_time_week", "importance": 0.25},
    {"feature": "assignment_completion_rate", "importance": 0.20},
    {"feature": "engagement_score", "importance": 0.10}
  ],
  "model_type": "Random Forest Regressor",
  "note": "Higher values indicate stronger influence on predictions"
}
```

### 4. Batch Predictions
```bash
curl -X POST "http://localhost:8000/api/predict/batch?student_id=1" \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "courses": ["Deep Learning", "NLP", "Computer Vision"]
  }'
```

**Response:**
```json
{
  "student_id": 1,
  "predictions": [
    {
      "course": "Deep Learning",
      "predicted_grade": 87.5,
      "confidence": 0.82,
      "risk_level": "low"
    },
    {
      "course": "Computer Vision",
      "predicted_grade": 85.0,
      "confidence": 0.79,
      "risk_level": "low"
    },
    {
      "course": "NLP",
      "predicted_grade": 82.0,
      "confidence": 0.75,
      "risk_level": "medium"
    }
  ],
  "total_courses": 3,
  "best_fit": "Deep Learning",
  "average_predicted_grade": 84.83
}
```

---

## Python Client Example

```python
import requests
import json

class StudentPortalAPI:
    def __init__(self, base_url="http://localhost:8000", api_key="dev-api-key-change-in-production"):
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def chat(self, student_id, message):
        """Send chat message to AI advisor"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            headers=self.headers,
            json={"student_id": student_id, "message": message}
        )
        return response.json()
    
    def get_recommendations(self, student_id, top_n=5, strategy="hybrid"):
        """Get course recommendations"""
        response = requests.post(
            f"{self.base_url}/api/recommend",
            headers=self.headers,
            json={"student_id": student_id, "top_n": top_n, "strategy": strategy}
        )
        return response.json()
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        response = requests.post(
            f"{self.base_url}/api/analysis/sentiment",
            headers=self.headers,
            json={"text": text, "include_emotions": True}
        )
        return response.json()
    
    def predict_performance(self, student_id, course):
        """Predict student performance in course"""
        response = requests.post(
            f"{self.base_url}/api/predict/performance",
            headers=self.headers,
            json={"student_id": student_id, "course": course}
        )
        return response.json()

# Usage
api = StudentPortalAPI()

# Chat with advisor
chat_response = api.chat(1, "What courses should I take?")
print(json.dumps(chat_response, indent=2))

# Get recommendations
recommendations = api.get_recommendations(1, top_n=3)
print(json.dumps(recommendations, indent=2))

# Analyze feedback sentiment
sentiment = api.analyze_sentiment("This course is excellent!")
print(json.dumps(sentiment, indent=2))

# Predict performance
prediction = api.predict_performance(1, "Deep Learning")
print(json.dumps(prediction, indent=2))
```

---

## JavaScript/React Client Example

```javascript
class StudentPortalAPI {
    constructor(baseUrl = 'http://localhost:8000', apiKey = 'dev-api-key-change-in-production') {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    async request(endpoint, method = 'GET', body = null) {
        const options = {
            method,
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${this.baseUrl}${endpoint}`, options);
        return await response.json();
    }

    async chat(studentId, message) {
        return await this.request('/api/chat', 'POST', {
            student_id: studentId,
            message: message
        });
    }

    async getRecommendations(studentId, topN = 5) {
        return await this.request('/api/recommend', 'POST', {
            student_id: studentId,
            top_n: topN,
            strategy: 'hybrid'
        });
    }

    async analyzeSentiment(text) {
        return await this.request('/api/analysis/sentiment', 'POST', {
            text: text,
            include_emotions: true
        });
    }

    async predictPerformance(studentId, course) {
        return await this.request('/api/predict/performance', 'POST', {
            student_id: studentId,
            course: course
        });
    }
}

// Usage
const api = new StudentPortalAPI();

// Chat with advisor
api.chat(1, 'What courses should I take?')
    .then(response => console.log(response));

// Get recommendations
api.getRecommendations(1, 3)
    .then(recommendations => console.log(recommendations));
```

---

## Error Response Examples

### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "field": "student_id",
      "error": "Must be greater than 0"
    }
  },
  "timestamp": "2025-06-15T10:30:00"
}
```

### 401 Unauthorized
```json
{
  "error": {
    "code": "MISSING_API_KEY",
    "message": "API key is required. Provide X-API-Key header."
  },
  "timestamp": "2025-06-15T10:30:00"
}
```

### 404 Not Found
```json
{
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "Student with ID 999 not found"
  },
  "timestamp": "2025-06-15T10:30:00"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded: 30 per 1 minute"
}
```

### 500 Internal Server Error
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred"
  },
  "timestamp": "2025-06-15T10:30:00"
}
```

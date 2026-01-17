# 🧪 Quick Testing Guide - Student Portal API

## Server Status
✅ **Running at:** http://localhost:8000  
📚 **Docs:** http://localhost:8000/docs  
🔑 **API Key:** `dev-api-key-change-in-production`

---

## Option 1: Interactive Testing (Easiest!) 🎯

### Open Swagger UI: http://localhost:8000/docs

**Quick Test Steps:**

1. **Click "Authorize"** (green button at top right)
   - Enter: `dev-api-key-change-in-production`
   - Click "Authorize" → "Close"

2. **Try Health Check:**
   - Click `GET /` 
   - Click "Try it out" → "Execute"
   - ✅ Should show API version and enabled features

3. **Get Student Profile:**
   - Click `GET /api/students/{student_id}`
   - Click "Try it out"
   - Enter `1` for student_id
   - Click "Execute"
   - ✅ See Alice Johnson's profile!

4. **Get Recommendations:**
   - Click `POST /api/recommend`
   - Click "Try it out"
   - Use this JSON (or edit the example):
   ```json
   {
     "student_id": 1,
     "top_n": 5,
     "strategy": "hybrid"
   }
   ```
   - Click "Execute"
   - ✅ See personalized course recommendations!

5. **Test Sentiment Analysis:**
   - Click `POST /api/analysis/sentiment`
   - Click "Try it out"
   - Try this:
   ```json
   {
     "text": "This course is amazing! I learned so much.",
     "include_emotions": true
   }
   ```
   - Click "Execute"
   - ✅ See sentiment score and emotions!

---

## Option 2: PowerShell Script 💻

```powershell
# Run this in PowerShell
.\test_api.ps1
```

Tests 5 endpoints automatically and shows results.

---

## Option 3: Python Script 🐍

```powershell
# Install requests if needed
pip install requests

# Run tests
python test_api.py
```

Runs 10 comprehensive tests covering all major features.

---

## Option 4: Manual curl Commands 🔧

### Health Check (No API key needed)
```powershell
curl http://localhost:8000/
```

### Get Student Profile
```powershell
curl -X GET "http://localhost:8000/api/students/1" `
  -H "X-API-Key: dev-api-key-change-in-production"
```

### Get Recommendations
```powershell
curl -X POST "http://localhost:8000/api/recommend" `
  -H "X-API-Key: dev-api-key-change-in-production" `
  -H "Content-Type: application/json" `
  -d '{"student_id": 1, "top_n": 5, "strategy": "hybrid"}'
```

### Sentiment Analysis
```powershell
curl -X POST "http://localhost:8000/api/analysis/sentiment" `
  -H "X-API-Key: dev-api-key-change-in-production" `
  -H "Content-Type: application/json" `
  -d '{"text": "This course is excellent!", "include_emotions": true}'
```

### Predict Performance
```powershell
curl -X POST "http://localhost:8000/api/predict/performance" `
  -H "X-API-Key: dev-api-key-change-in-production" `
  -H "Content-Type: application/json" `
  -d '{"student_id": 1, "course": "Deep Learning"}'
```

---

## Quick Feature Overview

| Feature | Endpoint | Description |
|---------|----------|-------------|
| 🏥 Health | `GET /` | Check API status |
| 👤 Students | `GET /api/students/{id}` | Get profile |
| 🎓 Recommendations | `POST /api/recommend` | Get course suggestions |
| 💬 Chat | `POST /api/chat` | Talk to AI advisor |
| 😊 Sentiment | `POST /api/analysis/sentiment` | Analyze feedback |
| 🏷️ Classification | `POST /api/analysis/classify` | Categorize text |
| 📊 Prediction | `POST /api/predict/performance` | Predict grades |
| ⚠️ Risk | `POST /api/predict/risk` | At-risk assessment |

---

## Example Responses

### Student Profile
```json
{
  "student_id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "gpa": 3.7,
  "completed_courses": ["Python Programming", "Data Structures"],
  "enrolled_courses": ["Machine Learning Fundamentals"]
}
```

### Recommendations
```json
{
  "recommendations": [
    {
      "course": "Deep Learning",
      "score": 0.95,
      "reason": "Matches your AI interests"
    }
  ]
}
```

### Sentiment Analysis
```json
{
  "sentiment": "positive",
  "score": 0.95,
  "confidence": 0.92,
  "emotions": {
    "joy": 0.8,
    "excitement": 0.6
  }
}
```

---

## Troubleshooting

**❌ Connection refused:**
- Make sure server is running: Check terminal for "Application startup complete"
- Server should be at http://localhost:8000

**❌ 401/403 errors:**
- Check API key is correct: `dev-api-key-change-in-production`
- Make sure you clicked "Authorize" in Swagger UI

**❌ 404 errors:**
- Student ID must exist (try ID 1, 2, or 3)
- Check endpoint URL is correct

**❌ Rate limit exceeded:**
- Wait 1 minute and try again
- Default limits: 60-100 requests per minute

---

## 🎉 Recommended Testing Flow

1. **Start with Swagger UI** - It's the easiest!
2. **Try these in order:**
   - Health check (GET /)
   - Student profile (GET /api/students/1)
   - Recommendations (POST /api/recommend)
   - Sentiment analysis (POST /api/analysis/sentiment)
3. **Explore other endpoints** - All 25 are documented!
4. **Try the Python script** for automated testing

---

## Next Steps

Once testing is complete:
- ✅ Step 6 Complete!
- 📱 Step 7: Build React frontend
- 🚀 Step 8: Deploy to production

**Questions?** Check [STEP_6_EXAMPLES.md](STEP_6_EXAMPLES.md) for more examples!

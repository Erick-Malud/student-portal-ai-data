"""
API Testing Script - Student Portal
Run this while the API server is running (uvicorn api.main:app --reload)
"""

import requests
import json

API_URL = "http://localhost:8000"
API_KEY = "dev-api-key-change-in-production"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_response(response):
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        print(f"\nStatus Code: {response.status_code}")
    except:
        print(f"Response: {response.text}")
        print(f"Status Code: {response.status_code}")

# Test 1: Health Check
print_section("1. Health Check")
response = requests.get(f"{API_URL}/")
print_response(response)

# Test 2: Get Student Profile
print_section("2. Get Student Profile (ID=1)")
response = requests.get(f"{API_URL}/api/students/1", headers=headers)
print_response(response)

# Test 3: Get Course Recommendations
print_section("3. Get Course Recommendations")
data = {
    "student_id": 1,
    "top_n": 3,
    "strategy": "hybrid"
}
response = requests.post(f"{API_URL}/api/recommend", headers=headers, json=data)
print_response(response)

# Test 4: List All Courses
print_section("4. List Available Courses")
response = requests.get(f"{API_URL}/api/recommend/courses", headers=headers)
print_response(response)

# Test 5: Sentiment Analysis
print_section("5. Sentiment Analysis")
data = {
    "text": "This course is amazing! I learned so much and the instructor was excellent.",
    "include_emotions": True,
    "include_reasoning": True
}
response = requests.post(f"{API_URL}/api/analysis/sentiment", headers=headers, json=data)
print_response(response)

# Test 6: Text Classification
print_section("6. Text Classification")
data = {
    "text": "I need help with the assignment deadline",
    "include_priority": True
}
response = requests.post(f"{API_URL}/api/analysis/classify", headers=headers, json=data)
print_response(response)

# Test 7: Performance Prediction
print_section("7. Performance Prediction")
data = {
    "student_id": 1,
    "course": "Deep Learning"
}
response = requests.post(f"{API_URL}/api/predict/performance", headers=headers, json=data)
print_response(response)

# Test 8: At-Risk Assessment
print_section("8. At-Risk Student Assessment")
response = requests.post(f"{API_URL}/api/predict/risk?student_id=1", headers=headers)
print_response(response)

# Test 9: Chat with AI Advisor
print_section("9. Chat with AI Advisor")
data = {
    "student_id": 1,
    "message": "What courses should I take to improve my data science skills?"
}
response = requests.post(f"{API_URL}/api/chat", headers=headers, json=data)
print_response(response)

# Test 10: Student Performance Metrics
print_section("10. Student Performance Metrics")
response = requests.get(f"{API_URL}/api/students/1/performance", headers=headers)
print_response(response)

print("\n" + "="*60)
print("  All Tests Complete!")
print("="*60)

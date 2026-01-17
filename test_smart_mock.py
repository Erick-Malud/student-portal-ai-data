import json
import urllib.request
import urllib.error
import time

BASE_URL = "http://127.0.0.1:8000/api/chat"
HEADERS = {
    "X-API-Key": "dev-api-key-change-in-production",
    "Content-Type": "application/json"
}

def test_chat(student_id, message, description):
    print(f"\n--- TEST: {description} ---")
    print(f"Input: Student ID='{student_id}', Message='{message}'")
    
    data = {
        "student_id": student_id,
        "message": message
    }
    json_data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(BASE_URL, data=json_data, headers=HEADERS, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            print(f"Status: {status_code}")
            
            data = json.loads(response_body)
            summary = data.get("student_summary") or {}
            
            intent = summary.get("intent", "N/A")
            perf = summary.get("performance_level", "N/A")
            student_name = summary.get("name", "N/A")
            
            # Print condensed response
            print(f"Response Preview: {data['response'][:100]}...")
            print(f"Student Found: {student_name}")
            print(f"Intent Detected: {intent}")
            print(f"Performance Level: {perf}")
            
            recs = data.get('recommendations', [])
            print(f"Recs: {recs}")
            
            sugg_courses = data.get('suggested_courses', [])
            if sugg_courses:
                codes = [c.get('course_code') for c in sugg_courses]
                print(f"Suggested Courses: {codes}")
            else:
                print("Suggested Courses: None")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("Running Smart Mock Mode Tests...")
    print(f"Target: {BASE_URL}")
    
    # 1. Next Courses (Intent Detection)
    test_chat("S002", "What courses should I take next?", "1. NEXT_COURSES Intent")

    # 2. Semester Plan (Intent + Low Enrollment logic)
    test_chat("S010", "Can you suggest my next semester plan?", "2. SEMESTER_PLAN Intent (Low Enrollment)")

    # 3. Difficulty/Challenge (Intent + Enrichment logic)
    test_chat("S011", "I want more challenging subjects.", "3. DIFFICULTY Intent")

    # 4. Career (Intent + Normalization of 's022' to 'S022')
    test_chat("s022", "Which courses will help my future career?", "4. CAREER Intent + ID Normalization")

    # 5. Unknown Student (Friendly 200 OK)
    test_chat("S999", "Hello", "5. Unknown Student Handling")

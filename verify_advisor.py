
try:
    from ai.student_advisor import AIStudentAdvisor
except ImportError:
    # Fix python path if running from root
    import sys
    import os
    sys.path.append(os.getcwd())
    from ai.student_advisor import AIStudentAdvisor

def test_advisor():
    print("="*60)
    print("🤖 VERIFYING AI STUDENT ADVISOR")
    print("="*60)

    # 1. Initialize
    print("\n1️⃣  Initializing Advisor (Connecting to DB & OpenAI)...")
    try:
        advisor = AIStudentAdvisor()
    except Exception as e:
        print(f"❌ FATAL: Could not initialize advisor. Error: {e}")
        return

    # 2. Test Student Data Retrieval
    student_id = "S005"  # John Smith
    print(f"\n2️⃣  Testing Context for Student {student_id} (John Smith)...")
    
    # Question 1: Data Retrieval
    q1 = "What courses have I completed?"
    print(f"   User: {q1}")
    res1 = advisor.chat(student_id, q1)
    # Handle older version of returning string vs dict
    ans1 = res1.get('response') if isinstance(res1, dict) else res1
    print(f"   AI: {ans1[:150]}...") # Truncate for readability

    # 3. Test Reasoning/Prediction
    print(f"\n3️⃣  Testing Reasoning & Advice...")
    q2 = "Based on my grades, what should I study next?"
    print(f"   User: {q2}")
    res2 = advisor.chat(student_id, q2)
    ans2 = res2.get('response') if isinstance(res2, dict) else res2
    print(f"   AI: {ans2[:150]}...")

    print("\n✅ Verification functionality test complete.")

if __name__ == "__main__":
    test_advisor()

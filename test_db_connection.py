"""
Test script to verify database connection and data loading
"""

from ai.student_data_loader import StudentDataLoader
from db_config import get_connection

print("=" * 60)
print("🧪 Testing Database Connection")
print("=" * 60)

# Test 1: Direct database connection
print("\n1️⃣  Testing direct database connection...")
try:
    conn = get_connection()
    print("✅ Database connection successful!")
    
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT COUNT(*) as count FROM students")
        result = cur.fetchone()
        print(f"✅ Found {result['count']} students in database")
        
        cur.execute("SELECT student_id, name FROM students LIMIT 5")
        rows = cur.fetchall()
        print("\n📋 First 5 students:")
        for row in rows:
            print(f"   - {row['student_id']}: {row['name']}")
    
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test 2: StudentDataLoader with database
print("\n2️⃣  Testing StudentDataLoader with database...")
try:
    loader = StudentDataLoader(use_database=True)
    all_students = loader.get_all_students()
    print(f"✅ Loaded {len(all_students)} students via StudentDataLoader")
    
    print("\n📋 First 5 students:")
    for student in all_students[:5]:
        print(f"   - {student['student_id']}: {student['name']}")
    
    # Test lookup
    print("\n3️⃣  Testing student lookup...")
    test_ids = ["S002", "s002", "2"]
    for test_id in test_ids:
        student = loader.get_student_by_id(test_id)
        if student:
            print(f"✅ Found student with ID '{test_id}': {student['name']}")
        else:
            print(f"❌ Could not find student with ID '{test_id}'")
            
except Exception as e:
    print(f"❌ StudentDataLoader failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: StudentDataLoader with JSON fallback
print("\n4️⃣  Testing StudentDataLoader with JSON fallback...")
try:
    loader_json = StudentDataLoader(use_database=False)
    all_students_json = loader_json.get_all_students()
    print(f"✅ Loaded {len(all_students_json)} students from JSON file")
    
    print("\n📋 First 5 students from JSON:")
    for student in all_students_json[:5]:
        print(f"   - {student['student_id']}: {student['name']}")
        
except Exception as e:
    print(f"❌ JSON fallback failed: {e}")

print("\n" + "=" * 60)
print("🏁 Testing Complete!")
print("=" * 60)

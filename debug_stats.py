
import mysql.connector
from db_config import get_connection

def test_stats_query(student_id):
    print(f"Testing stats for {student_id}")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Resolve Student ID
        print("Resolving student ID...")
        cursor.execute("SELECT id FROM students WHERE student_id = %s", (student_id,))
        s_row = cursor.fetchone()
        
        if not s_row:
            print("Student not found")
            return

        db_id = s_row['id']
        print(f"Found DB ID: {db_id}")

        # 2. Academic Record
        print("Fetching academic record...")
        cursor.execute("""
            SELECT c.name as course_name, c.course_code, e.grade, e.status, e.term
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = %s
            ORDER BY e.term DESC, c.course_code ASC
        """, (db_id,))
        academic_record = cursor.fetchall()
        print(f"Records found: {len(academic_record)}")

        # 3. Attendance
        print("Fetching attendance...")
        cursor.execute("""
            SELECT date, status, c.course_code 
            FROM attendance a
            JOIN courses c ON a.course_id = c.id
            WHERE a.student_id = %s
            ORDER BY date ASC
        """, (db_id,))
        attendance_logs = cursor.fetchall()
        print(f"Attendance logs found: {len(attendance_logs)}")

        conn.close()
        print("Success!")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stats_query("S002")

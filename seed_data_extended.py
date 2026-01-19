"""
seed_data_extended.py

Populates the database with:
1. Ensures every student has at least 4 courses
2. Assigns random grades to Course history
3. Generates Attendance records
"""

import mysql.connector
import random
from datetime import datetime, timedelta
from db_config import get_connection

def seed_data():
    print("🌱 Seeding Extended Data...")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get all students
        cursor.execute("SELECT id, student_id, name FROM students")
        students = cursor.fetchall()
        
        # Get all courses
        cursor.execute("SELECT id, course_code FROM courses")
        courses = cursor.fetchall()
        course_ids = [c['id'] for c in courses]

        if not courses:
            print("❌ No courses found. Run the basic setup first.")
            return

        for student in students:
            s_id_db = student['id']
            print(f"Processing {student['name']} ({student['student_id']})...")

            # 1. Get current enrollments
            cursor.execute("SELECT id, course_id, status FROM enrollments WHERE student_id = %s", (s_id_db,))
            existing_enrollments = cursor.fetchall()
            existing_course_ids = [e['course_id'] for e in existing_enrollments]
            
            # 2. Ensure 4 courses
            courses_needed = 4 - len(existing_enrollments)
            if courses_needed > 0:
                available_courses = [cid for cid in course_ids if cid not in existing_course_ids]
                to_enroll = random.sample(available_courses, min(len(available_courses), courses_needed))
                
                for cid in to_enroll:
                    # Decide if it's a completed course or active
                    # 70% chance it's completed (history), 30% active
                    is_completed = random.random() < 0.7
                    status = 'completed' if is_completed else 'enrolled'
                    
                    # Insert enrollment
                    term = 'Spring 2025' if not is_completed else 'Fall 2024'
                    cursor.execute(
                        "INSERT INTO enrollments (student_id, course_id,  enrollment_date, status, term) VALUES (%s, %s, %s, %s, %s)",
                        (s_id_db, cid, datetime.now().date(), status, term)
                    )
                    existing_enrollments.append({'course_id': cid, 'status': status})
                    print(f"  - Added course ID {cid} ({status})")

            # 3. Update Grades and Attendance
            # Re-fetch specific enrollment IDs just in case
            cursor.execute("SELECT id, course_id, status FROM enrollments WHERE student_id = %s", (s_id_db,))
            current_recs = cursor.fetchall()

            for rec in current_recs:
                enrollment_id = rec['id']
                course_id = rec['course_id']
                status = rec['status']

                # Assign Grade if completed and null
                if status == 'completed':
                    # Random realistic grade
                    grade = random.randint(65, 98)
                    cursor.execute("UPDATE enrollments SET grade = %s WHERE id = %s AND grade IS NULL", (grade, enrollment_id))
                
                # Generate Attendance (only for enrolled/active courses usually, but let's do recent history for all)
                # Generate 10 sessions over the last 10 weeks
                for i in range(10):
                    date_val = datetime.now() - timedelta(days=i*7)
                    
                    # 85% present, 10% absent, 5% late
                    rand = random.random()
                    if rand < 0.85:
                        att_status = 'present'
                    elif rand < 0.95:
                        att_status = 'absent'
                    else:
                        att_status = 'late'

                    # Check existence to avoid duplicate spamming if run twice
                    cursor.execute(
                        "SELECT id FROM attendance WHERE student_id=%s AND course_id=%s AND date=%s",
                        (s_id_db, course_id, date_val.date())
                    )
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO attendance (student_id, course_id, date, status) VALUES (%s, %s, %s, %s)",
                            (s_id_db, course_id, date_val.date(), att_status)
                        )

        conn.commit()
        print("\n✅ Database populated successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()

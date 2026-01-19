import json
import os
import mysql.connector
from db_config import get_connection
import db_migration_extended
import seed_data_extended
from dotenv import load_dotenv

load_dotenv()

def create_base_schema():
    print("🏗️ Creating base database schema...")
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Students Table
        print("- Creating 'students' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                age INT,
                course VARCHAR(100),
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Courses Table
        print("- Creating 'courses' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_code VARCHAR(20) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(100)
            )
        """)
        
        # 3. Enrollments Table
        print("- Creating 'enrollments' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                course_id INT NOT NULL,
                enrollment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                grade INT NULL,
                status VARCHAR(20) DEFAULT 'enrolled',
                term VARCHAR(20) DEFAULT 'Spring 2025',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("✅ Base schema created successfully.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating schema: {err}")
    finally:
        cursor.close()
        conn.close()

def import_students_from_json():
    print("\n📂 Importing students from students.json...")
    
    if not os.path.exists("students.json"):
        print("⚠️ students.json not found. Skipping import.")
        return

    with open("students.json", "r") as f:
        students_data = json.load(f)
        
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    try:
        for s in students_data:
            # Check if exists
            cursor.execute("SELECT id FROM students WHERE student_id = %s", (s['student_id'],))
            if cursor.fetchone():
                continue
                
            cursor.execute("""
                INSERT INTO students (student_id, name, age, course, email)
                VALUES (%s, %s, %s, %s, %s)
            """, (s['student_id'], s['name'], s['age'], s['course'], s.get('email', '')))
            count += 1
            
        conn.commit()
        print(f"✅ Imported {count} new students.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error importing data: {err}")
    finally:
        cursor.close()
        conn.close()

def seed_courses():
    print("\n📚 Seeding initial courses...")
    conn = get_connection()
    cursor = conn.cursor()
    
    courses = [
        ("CS101", "Intro to Computer Science", "IT"),
        ("CS102", "Data Structures", "IT"),
        ("DS201", "Data Analysis", "Data Science"),
        ("BU101", "Business Management", "Business"),
        ("ENG101", "English Composition", "Arts"),
        ("MK101", "Marketing Basics", "Business"),
        ("AI301", "Artificial Intelligence", "Data Science"),
        ("DB101", "Database Systems", "IT")
    ]
    
    count = 0
    try:
        for code, name, dept in courses:
            # Check if exists
            cursor.execute("SELECT id FROM courses WHERE course_code = %s", (code,))
            if cursor.fetchone():
                continue
                
            cursor.execute("""
                INSERT INTO courses (course_code, name, department)
                VALUES (%s, %s, %s)
            """, (code, name, dept))
            count += 1
            
        conn.commit()
        print(f"✅ seeded {count} new courses.")
        
    except mysql.connector.Error as err:
        print(f"❌ Error seeding courses: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Railway Database Setup...")
    print("-------------------------------------")
    
    # 1. Create Base Tables
    create_base_schema()
    
    # 2. Import JSON Data
    import_students_from_json()

    # 2.5 Seed Courses (Required for Enrollments)
    seed_courses()
    
    # 3. Run Extended Migrations (Grades, Attendance tables)
    print("\n🔄 Running Extended Migrations...")
    db_migration_extended.run_migration()
    
    # 4. Seed Extended Data (Courses, Enrollments, Grades)
    print("\n🌱 Seeding Extended Data...")
    seed_data_extended.seed_data()
    
    print("\n-------------------------------------")
    print("✨ Database setup complete! You can now use your app on Render.")

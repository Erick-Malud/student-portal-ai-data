"""
db_migration_extended.py

Updates the database schema to support:
1. Grades and Status in Enrollments (Academic Record)
2. Attendance Tracking
"""

import mysql.connector
from db_config import get_connection

def run_migration():
    print("🚀 Starting Database Migration...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Update Enrollments Table
        print("📊 Updating 'enrollments' table...")
        
        # Check if columns exist to avoid errors on re-run
        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'grade'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE enrollments ADD COLUMN grade FLOAT NULL")
            print("  - Added 'grade' column")

        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE enrollments ADD COLUMN status ENUM('enrolled', 'completed', 'dropped') DEFAULT 'enrolled'")
            print("  - Added 'status' column")

        cursor.execute("SHOW COLUMNS FROM enrollments LIKE 'term'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE enrollments ADD COLUMN term VARCHAR(20) DEFAULT 'Fall 2025'")
            print("  - Added 'term' column")

        # 2. Create Attendance Table
        print("📅 Creating 'attendance' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            date DATE NOT NULL,
            status ENUM('present', 'absent', 'late') NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            INDEX (student_id),
            INDEX (course_id)
        )
        """)
        print("  - 'attendance' table ready")

        conn.commit()
        print("\n✅ Migration completed successfully!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_migration()

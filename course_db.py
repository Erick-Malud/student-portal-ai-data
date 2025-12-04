"""
course_db.py

Course management for the Student Portal using MySQL.

Concepts:
- Separate module for courses (clean architecture).
- Dataclass Course as a data model.
- DB operations: INSERT, SELECT with filters (LIKE).
"""

from dataclasses import dataclass

from db_config import get_connection


# ---------- Data model ----------

@dataclass
class Course:
    """
    Represents a single course.

    Attributes:
        course_code: e.g., "IT101"
        name: e.g., "Intro to IT"
        department: e.g., "Information Technology"
    """
    course_code: str
    name: str
    department: str


# ---------- Course portal using DB ----------

class CoursePortalDB:
    """
    Handles all course-related operations:

        - add_course()
        - list_courses()
        - search_courses()
        - show_course_stats()

    This class talks directly to the `courses` table in MySQL.
    """

    def __init__(self) -> None:
        # No persistent connection; we open/close per operation (simple & safe).
        pass

    def add_course(self) -> None:
        """
        Add a new course into the database.

        Uses parameterized INSERT to prevent SQL injection.
        """
        print("\n➕ Add new course (DB)")

        course_code = input("Course code (e.g., IT301): ").strip()
        name = input("Course name (e.g., Advanced Web Dev): ").strip()
        department = input("Department (e.g., Information Technology): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO courses (course_code, name, department)
                    VALUES (%s, %s, %s)
                    """,
                    (course_code, name, department),
                )
            conn.commit()
            print(f"✅ Course added: {course_code} - {name}\n")
        finally:
            conn.close()

    def list_courses(self) -> None:
        """
        List all courses from the database.

        Demonstrates:
        - SELECT queries
        - ORDER BY name
        """
        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT course_code, name, department
                    FROM courses
                    ORDER BY name
                    """
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            print("\n(No courses found in DB)\n")
            return

        print("\n📚 Course List (from DB):")
        print("Code    | Name                        | Department")
        print("-" * 70)
        for row in rows:
            print(
                f"{row['course_code']:7} | "
                f"{row['name']:26} | "
                f"{row['department']}"
            )
        print()

    def search_courses(self) -> None:
        """
        Search courses by code, name or department.

        Uses LIKE with %keyword% on multiple columns.
        """
        keyword = input("\nSearch keyword (code/name/department): ").strip()
        like_pattern = f"%{keyword}%"

        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT course_code, name, department
                    FROM courses
                    WHERE course_code LIKE %s
                       OR name        LIKE %s
                       OR department  LIKE %s
                    ORDER BY name
                    """,
                    (like_pattern, like_pattern, like_pattern),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            print("🔍 No matching courses in DB.\n")
            return

        print("\n🔍 Course Search Results (from DB):")
        print("Code    | Name                        | Department")
        print("-" * 70)
        for row in rows:
            print(
                f"{row['course_code']:7} | "
                f"{row['name']:26} | "
                f"{row['department']}"
            )
        print()

    def show_course_stats(self) -> None:
        """
        Show basic statistics for courses:
        - Total courses
        - Courses by department
        """
        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                # Total courses
                cur.execute("SELECT COUNT(*) AS total FROM courses")
                total_courses = cur.fetchone()["total"]

                # Count courses by department
                cur.execute(
                    """
                    SELECT department, COUNT(*) AS count
                    FROM courses
                    GROUP BY department
                    """
                )
                dept_counts = cur.fetchall()
        finally:
            conn.close()

        print("\n📊 Course Statistics")
        print(f"Total courses: {total_courses}")
        print("\nCourses by department:")
        for row in dept_counts:
            print(f" - {row['department']}: {row['count']}")
        print()

    def edit_course(self) -> None:
        """
        Edit an existing course (by course_code).
        """
        code = input("\nEnter course code to edit (e.g., IT101): ").strip()

        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM courses WHERE course_code = %s",
                    (code,),
                )
                row = cur.fetchone()

                if row is None:
                    print(f"❌ No course found with code {code}\n")
                    return

                print("\nCurrent values (press Enter to keep):")
                print(f"Name:       {row['name']}")
                print(f"Department: {row['department']}\n")

                new_name = input("New course name: ").strip()
                new_dept = input("New department: ").strip()

                name = new_name or row["name"]
                dept = new_dept or row["department"]

                cur.execute(
                    """
                    UPDATE courses
                    SET name = %s, department = %s
                    WHERE course_code = %s
                    """,
                    (name, dept, code),
                )
            conn.commit()
            print(f"✅ Course {code} updated.\n")
        finally:
            conn.close()

    def delete_course(self) -> None:
        """
        Delete a course (by course_code).

        Enrollments will be removed if FK is ON DELETE CASCADE.
        """
        code = input("\nEnter course code to delete (e.g., IT101): ").strip()

        confirm = input(f"Are you sure you want to delete {code}? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Delete cancelled.\n")
            return

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM courses WHERE course_code = %s",
                    (code,),
                )
            conn.commit()
            if cur.rowcount == 0:
                print(f"❌ No course found with code {code}\n")
            else:
                print(f"✅ Course {code} deleted.\n")
        finally:
            conn.close()


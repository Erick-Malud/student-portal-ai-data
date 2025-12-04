"""
portal_db.py

Student Portal that uses MySQL database instead of JSON.

Concepts covered:
- Using mysql-connector-python.
- Using db_config.get_connection for DB access.
- Executing SELECT / INSERT queries with placeholders (%s).
- Fetching rows and printing them.
"""

from typing import List

from db_config import get_connection
from student import Student


class StudentPortalDB:
    """
    Student portal implementation that reads/writes data from/to MySQL.

    Methods:
        - add_student()
        - list_students()
        - search_students()
        - show_stats()
    """

    def __init__(self) -> None:
        # For now, we open/close a connection per operation (simpler).
        pass

    # ---------- Helper ----------

    def _fetch_all_students(self) -> List[Student]:
        """
        Load all students from the database and convert rows to Student objects.
        """
        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT student_id, name, age, course, email
                    FROM students
                    ORDER BY id
                    """
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        return [
            Student(
                student_id=row["student_id"],
                name=row["name"],
                age=row["age"],
                course=row["course"],
                email=row["email"],
            )
            for row in rows
        ]

    # ---------- Core features ----------

    def add_student(self) -> None:
        """Insert a new student into the database."""
        print("\n➕ Add new student (DB)")

        student_id = input("Student ID (e.g., S010): ").strip()
        name = input("Full name: ").strip()

        while True:
            age_str = input("Age: ").strip()
            try:
                age = int(age_str)
                break
            except ValueError:
                print("❌ Please enter a valid integer for age.")

        course = input("Course/Program (e.g., IT, Business): ").strip()
        email = input("Email: ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO students (student_id, name, age, course, email)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (student_id, name, age, course, email),
                )
            conn.commit()
            print(f"✅ Student added to DB: {student_id} - {name}\n")
        finally:
            conn.close()

    def list_students(self) -> None:
        """List all students from DB."""
        students = self._fetch_all_students()

        if not students:
            print("\n(No students found in DB)\n")
            return

        print("\n📋 Student List (from DB):")
        print("ID      | Name                 | Age | Course      | Email")
        print("-" * 70)
        for s in students:
            print(
                f"{s.student_id:6} | {s.name:20} | {s.age:3} | {s.course:10} | {s.email}"
            )
        print()

    def search_students(self) -> None:
        """Search students by ID, name or course using LIKE."""
        keyword = input("\nSearch keyword (ID/name/course): ").strip()
        like_pattern = f"%{keyword}%"

        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT student_id, name, age, course, email
                    FROM students
                    WHERE student_id LIKE %s
                       OR name       LIKE %s
                       OR course     LIKE %s
                    ORDER BY name
                    """,
                    (like_pattern, like_pattern, like_pattern),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            print("🔍 No matching students in DB.\n")
            return

        print("\n🔍 Search Results (from DB):")
        print("ID      | Name                 | Age | Course      | Email")
        print("-" * 70)
        for row in rows:
            print(
                f"{row['student_id']:6} | {row['name']:20} | {row['age']:3} | "
                f"{row['course']:10} | {row['email']}"
            )
        print()

    def show_stats(self) -> None:
        """Show total students and count per course."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # total students
                cur.execute("SELECT COUNT(*) FROM students")
                total_students = cur.fetchone()[0]

                # count by course
                cur.execute(
                    """
                    SELECT course, COUNT(*) AS total
                    FROM students
                    GROUP BY course
                    ORDER BY total DESC
                    """
                )
                course_rows = cur.fetchall()
        finally:
            conn.close()

        print(f"\n📊 Total students (DB): {total_students}")
        if course_rows:
            print("📚 Students by course (DB):")
            for course, total in course_rows:
                print(f" - {course}: {total}")
        print()

    def edit_student(self) -> None:
        """
        Edit an existing student (by student_id like 'S001').

        - Ask for student_id
        - Load current values
        - Ask new values (Enter = keep old)
        - Update the row
        """
        code = input("\nEnter student ID to edit (e.g., S001): ").strip()

        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT * FROM students WHERE student_id = %s",
                    (code,),
                )
                row = cur.fetchone()

                if row is None:
                    print(f"❌ No student found with ID {code}\n")
                    return

                print("\nCurrent values (press Enter to keep):")
                print(f"Name:    {row['name']}")
                print(f"Age:     {row['age']}")
                print(f"Course:  {row['course']}")
                print(f"Email:   {row['email']}\n")

                new_name = input("New name: ").strip()
                new_age_str = input("New age: ").strip()
                new_course = input("New course: ").strip()
                new_email = input("New email: ").strip()

                # keep old values if blank
                name = new_name or row["name"]
                course = new_course or row["course"]
                email = new_email or row["email"]

                if new_age_str:
                    try:
                        age = int(new_age_str)
                    except ValueError:
                        print("❌ Invalid age. Keeping old value.")
                        age = row["age"]
                else:
                    age = row["age"]

                cur.execute(
                    """
                    UPDATE students
                    SET name = %s, age = %s, course = %s, email = %s
                    WHERE student_id = %s
                    """,
                    (name, age, course, email, code),
                )
            conn.commit()
            print(f"✅ Student {code} updated.\n")
        finally:
            conn.close()

    def delete_student(self) -> None:
        """
        Delete a student (by student_id).

        Note:
        - Enrollments will also be deleted if FK is ON DELETE CASCADE.
        """
        code = input("\nEnter student ID to delete (e.g., S001): ").strip()

        confirm = input(f"Are you sure you want to delete {code}? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Delete cancelled.\n")
            return

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM students WHERE student_id = %s",
                    (code,),
                )
            conn.commit()
            if cur.rowcount == 0:
                print(f"❌ No student found with ID {code}\n")
            else:
                print(f"✅ Student {code} deleted.\n")
        finally:
            conn.close()


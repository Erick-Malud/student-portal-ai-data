"""
enrollment_db.py

Enrollment management for the Student Portal.

Features:
- enroll_student_in_course()
- show_student_courses()
- show_course_students()

Works with the `enrollments` table and uses JOINs with `students` and `courses`.
"""

from db_config import get_connection


class EnrollmentPortalDB:
    """Handles all enrollment-related operations."""

    def __init__(self) -> None:
        pass

    def enroll_student_in_course(self) -> None:
        """
        Enroll a student (by student_id like 'S001')
        into a course (by course_code like 'IT101').
        """
        print("\n➕ Enroll student in course")

        student_code = input("Student ID (e.g., S001): ").strip()
        course_code = input("Course code (e.g., IT101): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Find student DB id
                cur.execute(
                    "SELECT id FROM students WHERE student_id = %s",
                    (student_code,),
                )
                row = cur.fetchone()
                if row is None:
                    print(f"❌ No student found with ID {student_code}\n")
                    return
                student_id = row[0]

                # Find course DB id
                cur.execute(
                    "SELECT id FROM courses WHERE course_code = %s",
                    (course_code,),
                )
                row = cur.fetchone()
                if row is None:
                    print(f"❌ No course found with code {course_code}\n")
                    return
                course_id = row[0]

                # Optional: avoid duplicate enrollment
                cur.execute(
                    """
                    SELECT id FROM enrollments
                    WHERE student_id = %s AND course_id = %s
                    """,
                    (student_id, course_id),
                )
                if cur.fetchone():
                    print("⚠️ Student is already enrolled in this course.\n")
                    return

                # Insert enrollment
                cur.execute(
                    """
                    INSERT INTO enrollments (student_id, course_id)
                    VALUES (%s, %s)
                    """,
                    (student_id, course_id),
                )
            conn.commit()
            print(f"✅ Enrolled {student_code} into {course_code}\n")
        finally:
            conn.close()

    def show_student_courses(self) -> None:
        """
        Show all courses for a given student_id (e.g., 'S001').
        Uses JOIN between students, enrollments, and courses.
        """
        student_code = input("\nStudent ID (e.g., S001): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT s.student_id,
                           s.name,
                           c.course_code,
                           c.name
                    FROM enrollments e
                    JOIN students s ON e.student_id = s.id
                    JOIN courses  c ON e.course_id = c.id
                    WHERE s.student_id = %s
                    ORDER BY c.course_code
                    """,
                    (student_code,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            print("🔍 No courses found for that student.\n")
            return

        print("\n📚 Courses for student:")
        first = rows[0]
        print(f"Student: {first[0]} - {first[1]}")
        print("Enrolled in:")
        for _, _, code, name in rows:
            print(f" - {code}: {name}")
        print()

    def show_course_students(self) -> None:
        """
        Show all students enrolled in a specific course_code (e.g., 'IT101').
        """
        course_code = input("\nCourse code (e.g., IT101): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.course_code,
                           c.name,
                           s.student_id,
                           s.name
                    FROM enrollments e
                    JOIN students s ON e.student_id = s.id
                    JOIN courses  c ON e.course_id = c.id
                    WHERE c.course_code = %s
                    ORDER BY s.student_id
                    """,
                    (course_code,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()

        if not rows:
            print("🔍 No students found for that course.\n")
            return

        print("\n👨‍🎓 Students in course:")
        first = rows[0]
        print(f"Course: {first[0]} - {first[1]}")
        print("Enrolled students:")
        for _, _, sid, sname in rows:
            print(f" - {sid}: {sname}")
        print()

    def show_enrollment_stats(self) -> None:
        """
        Show statistics for enrollments:
        - Total enrollments
        - Students per course
        - Courses per student
        """

        conn = get_connection()
        try:
            with conn.cursor(dictionary=True) as cur:

                # Total enrollments
                cur.execute("SELECT COUNT(*) AS total FROM enrollments")
                total_enrollments = cur.fetchone()["total"]

                # Students per course
                cur.execute("""
                    SELECT c.course_code, c.name, COUNT(e.id) AS num_students
                    FROM courses c
                    LEFT JOIN enrollments e ON c.id = e.course_id
                    GROUP BY c.id
                    ORDER BY num_students DESC
                """)
                students_per_course = cur.fetchall()

                # Courses per student
                cur.execute("""
                    SELECT s.student_id, s.name, COUNT(e.id) AS num_courses
                    FROM students s
                    LEFT JOIN enrollments e ON s.id = e.student_id
                    GROUP BY s.id
                    ORDER BY num_courses DESC
                """)
                courses_per_student = cur.fetchall()

        finally:
            conn.close()

        print("\n📈 Enrollment Statistics")
        print(f"Total enrollments: {total_enrollments}")

        print("\nStudents per course:")
        for row in students_per_course:
            print(f" - {row['course_code']} ({row['name']}): {row['num_students']} students")

        print("\nCourses per student:")
        for row in courses_per_student:
            print(f" - {row['student_id']} ({row['name']}): {row['num_courses']} courses")

        print()

    def edit_enrollment(self) -> None:
        """
        Change a student's enrollment from one course to another.

        - Ask for student_id (e.g., S001)
        - Ask for current course_code (e.g., IT101)
        - Ask for new course_code (e.g., DS101)
        """
        student_code = input("\nStudent ID (e.g., S001): ").strip()
        old_course_code = input("Current course code (e.g., IT101): ").strip()
        new_course_code = input("New course code (e.g., DS101): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # find student id
                cur.execute("SELECT id FROM students WHERE student_id = %s", (student_code,))
                s_row = cur.fetchone()
                if s_row is None:
                    print(f"❌ No student found with ID {student_code}\n")
                    return
                student_id = s_row[0]

                # find old course id
                cur.execute("SELECT id FROM courses WHERE course_code = %s", (old_course_code,))
                c_old = cur.fetchone()
                if c_old is None:
                    print(f"❌ No course found with code {old_course_code}\n")
                    return
                old_course_id = c_old[0]

                # find new course id
                cur.execute("SELECT id FROM courses WHERE course_code = %s", (new_course_code,))
                c_new = cur.fetchone()
                if c_new is None:
                    print(f"❌ No course found with code {new_course_code}\n")
                    return
                new_course_id = c_new[0]

                # update one enrollment row
                cur.execute(
                    """
                    UPDATE enrollments
                    SET course_id = %s
                    WHERE student_id = %s AND course_id = %s
                    LIMIT 1
                    """,
                    (new_course_id, student_id, old_course_id),
                )
            conn.commit()
            if cur.rowcount == 0:
                print("❌ No matching enrollment found to update.\n")
            else:
                print(f"✅ Updated enrollment for {student_code}: {old_course_code} → {new_course_code}\n")
        finally:
            conn.close()

    def delete_enrollment(self) -> None:
        """
        Delete a specific enrollment (student_id + course_code).
        """
        student_code = input("\nStudent ID (e.g., S001): ").strip()
        course_code = input("Course code (e.g., IT101): ").strip()

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # find ids
                cur.execute("SELECT id FROM students WHERE student_id = %s", (student_code,))
                s_row = cur.fetchone()
                if s_row is None:
                    print(f"❌ No student found with ID {student_code}\n")
                    return
                student_id = s_row[0]

                cur.execute("SELECT id FROM courses WHERE course_code = %s", (course_code,))
                c_row = cur.fetchone()
                if c_row is None:
                    print(f"❌ No course found with code {course_code}\n")
                    return
                course_id = c_row[0]

                # delete
                cur.execute(
                    "DELETE FROM enrollments WHERE student_id = %s AND course_id = %s",
                    (student_id, course_id),
                )
            conn.commit()
            if cur.rowcount == 0:
                print("❌ No such enrollment found.\n")
            else:
                print(f"✅ Enrollment deleted for {student_code} in {course_code}\n")
        finally:
            conn.close()



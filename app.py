"""
app.py

Main entry point for the Student Portal Management System (DB version).

We now have:
- StudentPortalDB   (student_db)
- CoursePortalDB    (course_db)
- EnrollmentPortalDB (enrollment_db)

Main menu is split into 3 sections (Student, Course, Enrollment).
"""

from portal_db import StudentPortalDB
from course_db import CoursePortalDB
from enrollment_db import EnrollmentPortalDB


def student_menu(student_portal: StudentPortalDB) -> None:
    """Sub-menu for student management."""
    while True:
        print("\n--- Student Management ---")
        print("1. Add student(s)")
        print("2. List all students")
        print("3. Search students")
        print("4. Show student statistics")
        print("5. Edit student")
        print("6. Delete student")
        print("7. Back to main menu")
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            student_portal.add_student()
        elif choice == "2":
            student_portal.list_students()
        elif choice == "3":
            student_portal.search_students()
        elif choice == "4":
            student_portal.show_stats()
        elif choice == "5":
            student_portal.edit_student()
        elif choice == "6":
            student_portal.delete_student()
        elif choice == "7":
            break
        else:
            print("❌ Invalid choice.\n")



def course_menu(course_portal: CoursePortalDB) -> None:
    """Sub-menu for course management."""
    while True:
        print("\n--- Course Management ---")
        print("1. Add course")
        print("2. List all courses")
        print("3. Search courses")
        print("4. Course statistics")
        print("5. Edit course")
        print("6. Delete course")
        print("7. Back to main menu")
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            course_portal.add_course()
        elif choice == "2":
            course_portal.list_courses()
        elif choice == "3":
            course_portal.search_courses()
        elif choice == "4":
            course_portal.show_course_stats()
        elif choice == "5":
            course_portal.edit_course()
        elif choice == "6":
            course_portal.delete_course()
        elif choice == "7":
            break
        else:
            print("❌ Invalid choice.\n")



def enrollment_menu(enrollment_portal: EnrollmentPortalDB) -> None:
    """Sub-menu for enrollment management."""
    while True:
        print("\n--- Enrollment Management ---")
        print("1. Enroll student in course")
        print("2. Show a student's courses")
        print("3. Show students in a course")
        print("4. Enrollment statistics")
        print("5. Edit enrollment")
        print("6. Delete enrollment")
        print("7. Back to main menu")
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            enrollment_portal.enroll_student_in_course()
        elif choice == "2":
            enrollment_portal.show_student_courses()
        elif choice == "3":
            enrollment_portal.show_course_students()
        elif choice == "4":
            enrollment_portal.show_enrollment_stats()
        elif choice == "5":
            enrollment_portal.edit_enrollment()
        elif choice == "6":
            enrollment_portal.delete_enrollment()
        elif choice == "7":
            break
        else:
            print("❌ Invalid choice.\n")



def main() -> None:
    student_portal = StudentPortalDB()
    course_portal = CoursePortalDB()
    enrollment_portal = EnrollmentPortalDB()

    while True:
        print("\n========== Student Portal Management System (DB) ==========")
        print("1. Student menu")
        print("2. Course menu")
        print("3. Enrollment menu")
        print("4. Exit")
        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            student_menu(student_portal)
        elif choice == "2":
            course_menu(course_portal)
        elif choice == "3":
            enrollment_menu(enrollment_portal)
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.\n")


if __name__ == "__main__":
    main()

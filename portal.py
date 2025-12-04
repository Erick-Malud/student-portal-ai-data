"""
portal.py

Defines the StudentPortal class for managing students.

Python concepts:
- CONSTANT for data file name.
- LIST of Student objects held in memory.
- FILE operations (JSON read/write).
- METHODS for CRUD:
    - add_student
    - list_students
    - search_students
    - show_stats
- LOOPS & CONDITIONS inside methods.
"""

import json
from pathlib import Path
from typing import List

from student import Student  # our model class


DATA_FILE = "students.json"  # constant: file for data storage


class StudentPortal:
    """
    Main class that manages all student-related operations.

    Responsibilities:
    - Load existing students from JSON.
    - Add new students.
    - List and search students.
    - Show simple statistics.
    - Save changes back to JSON.
    """

    def __init__(self, data_file: str = DATA_FILE) -> None:
        self.data_file: Path = Path(data_file)
        self.students: List[Student] = []

        # Load data at startup (if file exists)
        self.load_data()

    # ---------- FILE OPERATIONS ----------

    def load_data(self) -> None:
        """
        Load students from JSON file if it exists.

        Concepts:
        - Path.exists() to check file.
        - json.load() to get Python list of dicts.
        - list comprehension to convert dicts → Student objects.
        """
        if self.data_file.exists():
            try:
                with self.data_file.open("r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    self.students = [Student.from_dict(item) for item in raw_data]
            except json.JSONDecodeError:
                print("⚠️  Warning: Could not read students.json. Starting with empty data.")
                self.students = []
        else:
            self.students = []

    def save_data(self) -> None:
        """
        Save all current students into JSON file.

        Concepts:
        - [s.to_dict() for s in self.students]: list comprehension.
        - json.dump() with indent for readability.
        """
        data = [s.to_dict() for s in self.students]
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("💾 Student data saved.\n")

    # ---------- CORE FEATURES ----------

    def add_student(self) -> None:
        """
        Add a new student from user input.

        Concepts:
        - input() to read values.
        - validation of age with try/except.
        - Creating Student object.
        - Appending to list & saving to file.
        """
        print("\n➕ Add new student")

        student_id = input("Student ID (e.g., S001): ").strip()
        name = input("Full name: ").strip()

        # validate age as integer
        while True:
            age_str = input("Age: ").strip()
            try:
                age = int(age_str)
                break
            except ValueError:
                print("❌ Please enter a valid integer for age.")

        course = input("Course/Program (e.g., IT, Business): ").strip()
        email = input("Email: ").strip()

        student = Student(
            student_id=student_id,
            name=name,
            age=age,
            course=course,
            email=email,
        )

        self.students.append(student)
        self.save_data()
        print(f"✅ Student added: {student_id} - {name}\n")

    def list_students(self) -> None:
        """
        List all students in a formatted table.

        Concepts:
        - if not self.students: handle empty list.
        - enumerate() to show index numbers.
        - f-strings for nice formatting.
        """
        if not self.students:
            print("\n(No students found)\n")
            return

        print("\n📋 Student List:")
        print("ID      | Name                 | Age | Course      | Email")
        print("-" * 65)
        for s in self.students:
            print(
                f"{s.student_id:6} | {s.name:20} | {s.age:3} | {s.course:10} | {s.email}"
            )
        print()

    def search_students(self) -> None:
        """
        Search students by name, ID, or course.

        Concepts:
        - lower() for case-insensitive search.
        - list comprehension for filtering.
        """
        keyword = input("\nSearch by name/ID/course: ").strip().lower()
        results = [
            s
            for s in self.students
            if keyword in s.student_id.lower()
            or keyword in s.name.lower()
            or keyword in s.course.lower()
        ]

        if not results:
            print("🔍 No matching students found.\n")
            return

        print("\n🔍 Search Results:")
        print("ID      | Name                 | Age | Course      | Email")
        print("-" * 65)
        for s in results:
            print(
                f"{s.student_id:6} | {s.name:20} | {s.age:3} | {s.course:10} | {s.email}"
            )
        print()

    def show_stats(self) -> None:
        """
        Show simple statistics about students.

        Concepts:
        - len() for total count.
        - dictionaries (course_counts) for grouping.
        - for loop to count per course.
        """
        total = len(self.students)
        print(f"\n📊 Total students: {total}")

        # count students by course
        course_counts: dict[str, int] = {}
        for s in self.students:
            course_counts[s.course] = course_counts.get(s.course, 0) + 1

        if course_counts:
            print("📚 Students by course:")
            for course, count in course_counts.items():
                print(f" - {course}: {count}")
        print()

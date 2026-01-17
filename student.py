"""
student.py

Defines the Student class for the Student Portal Management System.

Python concepts:
- CLASS (OOP) with attributes for each student.
- @dataclass for clean data containers.
- TYPE HINTS for readability and tooling.
- METHODS to_dict() / from_dict() for JSON conversion.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Student:
    """
    Represents a single student.

    Attributes:
        student_id: unique identifier (e.g., "S001")
        name: full name of the student
        age: age as an integer
        course: main course or program (e.g., "IT", "Business")
        email: contact email
        enrolled_courses: list of currently active courses
        completed_courses: list of finished courses
        grades: dictionary of course grades
    """

    student_id: str
    name: str
    age: int
    course: str
    email: str
    enrolled_courses: List[str] = field(default_factory=list)
    completed_courses: List[str] = field(default_factory=list)
    grades: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert this Student object into a plain dictionary.

        Why?
        - json.dump() and json.load() use dicts & lists, not custom classes.
        """
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "course": self.course,
            "email": self.email,
            "enrolled_courses": self.enrolled_courses,
            "completed_courses": self.completed_courses,
            "grades": self.grades
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Create a Student object from a dictionary.

        Used when:
        - Loading data from students.json.
        """
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            age=int(data["age"]),
            course=data["course"],
            email=data["email"],
            enrolled_courses=data.get("enrolled_courses", []),
            completed_courses=data.get("completed_courses", []),
            grades=data.get("grades", {})
        )

    def get_completed_courses(self) -> List[str]:
        """Get list of completed courses"""
        return self.completed_courses

    def get_enrolled_courses(self) -> List[str]:
        """Get list of currently enrolled courses"""
        return self.enrolled_courses

    def complete_course(self, course_name: str, grade: float = None):
        """Mark a course as completed"""
        if course_name not in self.completed_courses:
            self.completed_courses.append(course_name)
        if grade is not None:
            self.grades[course_name] = grade


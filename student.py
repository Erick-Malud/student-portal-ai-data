"""
student.py

Defines the Student class for the Student Portal Management System.

Python concepts:
- CLASS (OOP) with attributes for each student.
- @dataclass for clean data containers.
- TYPE HINTS for readability and tooling.
- METHODS to_dict() / from_dict() for JSON conversion.
"""

from dataclasses import dataclass


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
    """

    student_id: str
    name: str
    age: int
    course: str
    email: str

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
        )

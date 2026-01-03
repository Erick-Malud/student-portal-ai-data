"""
Student Data Loader - Step 3
Handles loading and querying student data from students.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from difflib import SequenceMatcher


class StudentDataLoader:
    """Load and query student data efficiently"""
    
    def __init__(self, data_file: str = "students.json"):
        """Initialize with path to students.json"""
        self.data_file = Path(data_file)
        self.students: List[Dict] = []
        self.students_by_id: Dict[int, Dict] = {}
        self.students_by_name: Dict[str, Dict] = {}
        
        if not self.data_file.exists():
            # Try parent directory
            parent_path = Path(__file__).parent.parent / data_file
            if parent_path.exists():
                self.data_file = parent_path
            else:
                raise FileNotFoundError(f"Students data file not found: {data_file}")
        
        self.load_students()
    
    def load_students(self) -> List[Dict]:
        """Load all students from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
            
            # Build indexes for fast lookup
            for student in self.students:
                student_id = student.get('id')
                name = student.get('name', '').lower()
                
                if student_id:
                    self.students_by_id[student_id] = student
                if name:
                    self.students_by_name[name] = student
            
            print(f"✓ Loaded {len(self.students)} students from {self.data_file.name}")
            return self.students
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in students file: {e}")
        except Exception as e:
            raise Exception(f"Error loading students: {e}")
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict]:
        """Get specific student by ID"""
        return self.students_by_id.get(student_id)
    
    def get_student_by_name(self, name: str, fuzzy: bool = True) -> Optional[Dict]:
        """
        Search for student by name (case-insensitive)
        
        Args:
            name: Student name to search for
            fuzzy: If True, use fuzzy matching for partial names
        
        Returns:
            Student dict if found, None otherwise
        """
        name_lower = name.lower().strip()
        
        # Exact match
        if name_lower in self.students_by_name:
            return self.students_by_name[name_lower]
        
        # Fuzzy matching
        if fuzzy:
            best_match = None
            best_score = 0.0
            
            for student_name, student in self.students_by_name.items():
                # Check if search term is in student name
                if name_lower in student_name:
                    return student
                
                # Calculate similarity score
                score = SequenceMatcher(None, name_lower, student_name).ratio()
                if score > best_score and score > 0.6:  # 60% similarity threshold
                    best_score = score
                    best_match = student
            
            return best_match
        
        return None
    
    def get_all_students(self) -> List[Dict]:
        """Get list of all students"""
        return self.students
    
    def search_students(self, query: str) -> List[Dict]:
        """
        Search students by name, email, or other fields
        
        Args:
            query: Search query (case-insensitive)
        
        Returns:
            List of matching students
        """
        query_lower = query.lower().strip()
        results = []
        
        for student in self.students:
            # Search in name
            if query_lower in student.get('name', '').lower():
                results.append(student)
                continue
            
            # Search in email
            if query_lower in student.get('email', '').lower():
                results.append(student)
                continue
            
            # Search in courses
            courses = student.get('courses', [])
            if any(query_lower in course.lower() for course in courses):
                results.append(student)
                continue
        
        return results
    
    def get_student_summary(self, student_id: int) -> Optional[str]:
        """
        Generate a formatted summary of student data for AI context
        
        Returns:
            Formatted string with student info, or None if not found
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return None
        
        # Calculate statistics
        stats = self.calculate_student_stats(student_id)
        if not stats:
            return None
        
        # Build summary
        summary_parts = [
            f"Student Profile:",
            f"- Name: {student.get('name', 'Unknown')}",
            f"- ID: {student_id}",
            f"- Email: {student.get('email', 'N/A')}",
            f"",
            f"Academic Performance:",
            f"- GPA: {stats['avg_grade']:.1f}",
            f"- Courses Completed: {stats['courses_completed']}",
            f"- Active Enrollments: {stats['active_enrollments']}",
        ]
        
        # Add course grades if available
        if stats['grades']:
            summary_parts.append("")
            summary_parts.append("Course Grades:")
            for course, grade in stats['grades'].items():
                summary_parts.append(f"  • {course}: {grade}")
        
        return "\n".join(summary_parts)
    
    def calculate_student_stats(self, student_id: int) -> Optional[Dict]:
        """
        Calculate statistics for a student
        
        Returns:
            Dict with GPA, course count, grades, etc.
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return None
        
        grades = student.get('grades', {})
        courses = student.get('courses', [])
        
        # Calculate average grade (GPA)
        if grades:
            avg_grade = sum(grades.values()) / len(grades)
        else:
            avg_grade = 0.0
        
        # Count completed courses (those with grades)
        courses_completed = len(grades)
        
        # Active enrollments (courses without grades yet)
        active_enrollments = len(courses) - courses_completed
        
        return {
            'student_id': student_id,
            'name': student.get('name', 'Unknown'),
            'avg_grade': avg_grade,
            'courses_completed': courses_completed,
            'active_enrollments': active_enrollments,
            'grades': grades,
            'courses': courses,
            'email': student.get('email', 'N/A')
        }
    
    def get_all_stats(self) -> Dict:
        """
        Calculate statistics across all students
        
        Returns:
            Dict with overall statistics
        """
        total_students = len(self.students)
        all_grades = []
        all_courses = []
        
        for student in self.students:
            grades = student.get('grades', {})
            courses = student.get('courses', [])
            
            if grades:
                all_grades.extend(grades.values())
            all_courses.extend(courses)
        
        # Calculate averages
        avg_gpa = sum(all_grades) / len(all_grades) if all_grades else 0.0
        avg_courses_per_student = len(all_courses) / total_students if total_students > 0 else 0.0
        
        # Count risk levels
        at_risk = 0
        average = 0
        excelling = 0
        
        for student in self.students:
            grades = student.get('grades', {})
            if grades:
                student_avg = sum(grades.values()) / len(grades)
                if student_avg < 70:
                    at_risk += 1
                elif student_avg < 85:
                    average += 1
                else:
                    excelling += 1
        
        return {
            'total_students': total_students,
            'avg_gpa': avg_gpa,
            'avg_courses_per_student': avg_courses_per_student,
            'at_risk_count': at_risk,
            'average_count': average,
            'excelling_count': excelling,
            'total_grades': len(all_grades),
            'unique_courses': len(set(all_courses))
        }
    
    def get_students_by_risk_level(self) -> Dict[str, List[Dict]]:
        """
        Categorize students by risk level based on GPA
        
        Returns:
            Dict with 'at_risk', 'average', 'excelling' lists
        """
        categorized = {
            'at_risk': [],      # GPA < 70
            'average': [],      # GPA 70-85
            'excelling': []     # GPA > 85
        }
        
        for student in self.students:
            grades = student.get('grades', {})
            if not grades:
                continue
            
            avg_grade = sum(grades.values()) / len(grades)
            student_info = {
                'id': student.get('id'),
                'name': student.get('name'),
                'gpa': avg_grade
            }
            
            if avg_grade < 70:
                categorized['at_risk'].append(student_info)
            elif avg_grade < 85:
                categorized['average'].append(student_info)
            else:
                categorized['excelling'].append(student_info)
        
        return categorized


# Convenience functions for quick access
def load_student_data(data_file: str = "students.json") -> StudentDataLoader:
    """Quick function to create and return a StudentDataLoader instance"""
    return StudentDataLoader(data_file)


def get_student_info(student_id_or_name, data_file: str = "students.json") -> Optional[Dict]:
    """
    Quick function to get student info by ID or name
    
    Args:
        student_id_or_name: Student ID (int) or name (str)
        data_file: Path to students.json
    
    Returns:
        Student dict if found, None otherwise
    """
    loader = StudentDataLoader(data_file)
    
    if isinstance(student_id_or_name, int):
        return loader.get_student_by_id(student_id_or_name)
    else:
        return loader.get_student_by_name(str(student_id_or_name))


if __name__ == "__main__":
    """Test the student data loader"""
    print("=" * 60)
    print("Testing Student Data Loader")
    print("=" * 60)
    
    try:
        # Load data
        loader = StudentDataLoader()
        
        print(f"\n1. Total Students: {len(loader.get_all_students())}")
        
        # Test get by ID
        print("\n2. Testing get_student_by_id(1):")
        student = loader.get_student_by_id(1)
        if student:
            print(f"   Found: {student.get('name')}")
        
        # Test get by name
        print("\n3. Testing get_student_by_name('alice'):")
        student = loader.get_student_by_name("alice")
        if student:
            print(f"   Found: {student.get('name')} (ID: {student.get('id')})")
        
        # Test student summary
        print("\n4. Testing get_student_summary(1):")
        summary = loader.get_student_summary(1)
        if summary:
            print(summary)
        
        # Test statistics
        print("\n5. Testing calculate_student_stats(1):")
        stats = loader.calculate_student_stats(1)
        if stats:
            print(f"   GPA: {stats['avg_grade']:.1f}")
            print(f"   Courses Completed: {stats['courses_completed']}")
        
        # Test overall stats
        print("\n6. Overall Statistics:")
        overall = loader.get_all_stats()
        print(f"   Total Students: {overall['total_students']}")
        print(f"   Average GPA: {overall['avg_gpa']:.1f}")
        print(f"   At Risk: {overall['at_risk_count']}")
        print(f"   Average: {overall['average_count']}")
        print(f"   Excelling: {overall['excelling_count']}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

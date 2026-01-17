"""
Student Data Loader - Step 3
Handles loading and querying student data from database or JSON file
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from difflib import SequenceMatcher


class StudentDataLoader:
    """Load and query student data efficiently"""
    
    def __init__(self, data_file: str = "students.json", use_database: bool = False):
        """
        Initialize data loader
        
        Args:
            data_file: Path to students.json (fallback if database fails)
            use_database: If True, load from MySQL database; if False, use JSON file
        """
        self.data_file = Path(data_file)
        self.use_database = use_database
        self.students: List[Dict] = []
        self.students_by_id: Dict[int, Dict] = {}
        self.students_by_name: Dict[str, Dict] = {}
        
        if not use_database and not self.data_file.exists():
            # Try parent directory
            parent_path = Path(__file__).parent.parent / data_file
            if parent_path.exists():
                self.data_file = parent_path
            else:
                raise FileNotFoundError(f"Students data file not found: {data_file}")
        
        self.load_students()
    
    def load_students(self) -> List[Dict]:
        """Load all students from database or JSON file"""
        if self.use_database:
            try:
                self._load_from_database()
            except Exception as e:
                print(f"⚠️  Database loading failed: {e}")
                print("📄 Falling back to JSON file...")
                self._load_from_json()
        else:
            self._load_from_json()
        
        return self.students
    
    def _load_from_database(self):
        """Load students from MySQL database"""
        try:
            # Import here to avoid circular import
            import sys
            from pathlib import Path
            
            # Add parent directory to path to import db_config
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            from db_config import get_connection
            
            conn = get_connection()
            try:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT student_id, name, age, course, email
                        FROM students
                        ORDER BY id
                    """)
                    rows = cur.fetchall()
                    self.students = rows
            finally:
                conn.close()
            
            print(f"✅ Loaded {len(self.students)} students from database")
            self._build_indexes()
            
        except Exception as e:
            raise Exception(f"Failed to load from database: {e}")
    
    def _load_from_json(self):
        """Load students from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
            
            print(f"✅ Loaded {len(self.students)} students from JSON file")
            self._build_indexes()
            
        except Exception as e:
            raise Exception(f"Failed to load from JSON: {e}")
    
    def _build_indexes(self):
        """Build indexes for fast lookup"""
        for student in self.students:
            # Support both 'id' and 'student_id' fields
            student_id = student.get('id') or student.get('student_id')
            name = student.get('name', '').lower()
            
            if student_id:
                # Store with both the original type and as integer if possible
                self.students_by_id[student_id] = student
                
                # For string IDs, also store lowercase version for case-insensitive lookup
                if isinstance(student_id, str):
                    self.students_by_id[student_id.lower()] = student
                    self.students_by_id[student_id.upper()] = student
                    
                    # Try to extract numeric ID (e.g., "S001" -> 1)
                    if student_id[0].isalpha():
                        try:
                            numeric_id = int(student_id[1:])
                            self.students_by_id[numeric_id] = student
                        except:
                            pass
            if name:
                self.students_by_name[name] = student
    
    def get_student_by_id(self, student_id) -> Optional[Dict]:
        """
        Get specific student by ID
        Supports both string IDs (e.g., 'S001') and integer IDs (e.g., 1)
        """
        # First try direct look up
        student = self.students_by_id.get(student_id)
        if student:
            return student
            
        # Try type conversion
        try:
            # If string input looks like number, try as int
            if isinstance(student_id, str) and student_id.isdigit():
                return self.students_by_id.get(int(student_id))
            
            # If int input, try as string
            if isinstance(student_id, int):
                return self.students_by_id.get(str(student_id))
        except:
            pass
            
        return None
    
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
def load_student_data(data_file: str = "students.json", use_database: bool = True) -> StudentDataLoader:
    """
    Quick function to create and return a StudentDataLoader instance
    
    Args:
        data_file: Path to students.json (fallback)
        use_database: If True, load from MySQL database; if False, use JSON file
    """
    return StudentDataLoader(data_file, use_database=use_database)


def get_student_info(student_id_or_name, data_file: str = "students.json", use_database: bool = True) -> Optional[Dict]:
    """
    Quick function to get student info by ID or name
    
    Args:
        student_id_or_name: Student ID (int or str) or name (str)
        data_file: Path to students.json (fallback)
        use_database: If True, load from MySQL database; if False, use JSON file
    
    Returns:
        Student dict if found, None otherwise
    """
    loader = StudentDataLoader(data_file, use_database=use_database)
    
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

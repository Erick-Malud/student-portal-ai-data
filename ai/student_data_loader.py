"""
Student Data Loader - Step 3
Handles loading and querying student data from database or JSON file
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher


class StudentDataLoader:
    """Load and query student data efficiently"""

    def __init__(self, data_file: str = "students.json", use_database: bool = False):
        self.use_database = use_database

        # ✅ Always resolve students.json reliably (works with uvicorn, vercel, etc.)
        self.data_file = self._resolve_data_file(data_file)

        self.students: List[Dict] = []
        self.students_by_id: Dict[Any, Dict] = {}
        self.students_by_name: Dict[str, Dict] = {}

        self.load_students()

    def _resolve_data_file(self, data_file: str) -> Path:
        """
        Find students.json reliably by walking up directories from this file.
        """
        p = Path(data_file)
        if p.exists():
            return p.resolve()

        here = Path(__file__).resolve()
        for parent in [here.parent, *here.parents]:
            candidate = parent / data_file
            if candidate.exists():
                return candidate.resolve()

        # If DB mode, we still keep a fallback path (but file might not exist)
        return Path(data_file).resolve()

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

        # ✅ Normalize student_id -> id for internal consistency
        for student in self.students:
            if "id" not in student and "student_id" in student:
                student["id"] = student["student_id"]

        return self.students

    def _load_from_database(self):
        """Load students from MySQL database"""
        try:
            import sys
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            from db_config import get_connection

            conn = get_connection()
            try:
                with conn.cursor(dictionary=True) as cur:
                    cur.execute("""
                        SELECT id, student_id, name, age, course, email
                        FROM students
                        ORDER BY id
                    """)
                    rows = cur.fetchall()

                    for student in rows:
                        student_db_id = student["id"]
                        student["grades"] = {}
                        student["courses"] = []

                        cur.execute("""
                            SELECT c.course_code, e.grade, e.status
                            FROM enrollments e
                            JOIN courses c ON e.course_id = c.id
                            WHERE e.student_id = %s
                        """, (student_db_id,))

                        enrollments = cur.fetchall()
                        for enroll in enrollments:
                            code = enroll["course_code"]
                            grade = enroll["grade"]
                            student["courses"].append(code)
                            if grade is not None:
                                student["grades"][code] = grade

                    self.students = rows
            finally:
                conn.close()

            print(f"✅ Loaded {len(self.students)} students from database")
            self._build_indexes()

        except Exception as e:
            raise Exception(f"Failed to load from database: {e}")

    def _load_from_json(self):
        """Load students from JSON file"""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Students data file not found: {self.data_file}")

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.students = json.load(f)

            if not isinstance(self.students, list):
                raise ValueError("students.json must contain a LIST of students")

            print(f"✅ Loaded {len(self.students)} students from JSON file: {self.data_file}")
            self._build_indexes()

        except Exception as e:
            raise Exception(f"Failed to load from JSON: {e}")

    def _build_indexes(self):
        """Build indexes for fast lookup"""
        self.students_by_id.clear()
        self.students_by_name.clear()

        for student in self.students:
            student_id = student.get("id") or student.get("student_id")
            name = (student.get("name") or "").strip().lower()

            if student_id is not None:
                # store original
                self.students_by_id[student_id] = student

                # store string variants
                sid_str = str(student_id).strip()
                self.students_by_id[sid_str] = student
                self.students_by_id[sid_str.lower()] = student
                self.students_by_id[sid_str.upper()] = student

                # if pattern like S002 -> 2
                if sid_str and sid_str[0].isalpha():
                    num_part = sid_str[1:]
                    if num_part.isdigit():
                        self.students_by_id[int(num_part)] = student

            if name:
                self.students_by_name[name] = student

    def get_student_by_id(self, student_id) -> Optional[Dict]:
        """
        Get specific student by ID (supports 'S002', 's002', '  S002  ', 2, '2')
        """
        if student_id is None:
            return None

        key = str(student_id).strip()
        if not key:
            return None

        # direct
        found = self.students_by_id.get(student_id)
        if found:
            return found

        # normalized string lookups
        found = self.students_by_id.get(key) or self.students_by_id.get(key.upper()) or self.students_by_id.get(key.lower())
        if found:
            return found

        # numeric fallback
        if key.isdigit():
            return self.students_by_id.get(int(key))

        return None

    def get_student_by_name(self, name: str, fuzzy: bool = True) -> Optional[Dict]:
        name_lower = name.lower().strip()

        if name_lower in self.students_by_name:
            return self.students_by_name[name_lower]

        if fuzzy:
            best_match = None
            best_score = 0.0

            for student_name, student in self.students_by_name.items():
                if name_lower in student_name:
                    return student

                score = SequenceMatcher(None, name_lower, student_name).ratio()
                if score > best_score and score > 0.6:
                    best_score = score
                    best_match = student

            return best_match

        return None

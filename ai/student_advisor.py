# ai/student_advisor.py
from __future__ import annotations
from typing import Any, Dict, Optional, List, Union, Set
from datetime import datetime
import random
import re

try:
    # Your project has this
    from ai.student_data_loader import StudentDataLoader
    from api.config import settings
    from ai.context_manager import ContextManager
except Exception:
    StudentDataLoader = None  # type: ignore
    settings = None  # type: ignore
    ContextManager = None  # type: ignore


class AIStudentAdvisor:
    """
    Deterministic (data-first) Student Advisor:
    - For GRADES/ATTENDANCE/ENROLLMENTS/COURSES and FOLLOW-UP "Why" questions:
      returns correct answers from dataset (NO generic greeting).
    - For other questions: returns a helpful generic response (you can later connect OpenAI).
    """

    def __init__(self):
        if StudentDataLoader is None:
            raise RuntimeError("StudentDataLoader import failed. Check ai/student_data_loader.py")
        if settings is None:
            raise RuntimeError("Settings import failed. Check api/config.py")
        if ContextManager is None:
            raise RuntimeError("ContextManager import failed. Check ai/context_manager.py")
        self.data_loader = StudentDataLoader(
            data_file=settings.STUDENTS_FILE,
            use_database=settings.USE_DATABASE,
        )
        self.context_manager = ContextManager()

        # Remember previous intent per student (so "Why?" can refer to last answer)
        self._last_intent_by_student: Dict[str, str] = {}
        # Track pending confirmations (e.g., full academic record) and follow-ups
        self._pending_confirm_by_student: Dict[str, str] = {}
        self._pending_followup_by_student: Dict[str, str] = {}
        self._last_course_by_student: Dict[str, Dict[str, Any]] = {}
        self._rng = random.Random()

    def reset_state(self, student_id: Union[str, int, None] = None) -> None:
        """Reset conversation state for a student or all students."""
        if student_id is None:
            self._last_intent_by_student.clear()
            self._pending_confirm_by_student.clear()
            self._pending_followup_by_student.clear()
            self._last_course_by_student.clear()
            return

        sid = self._normalize_student_id(student_id)
        if not sid:
            return
        self._last_intent_by_student.pop(sid, None)
        self._pending_confirm_by_student.pop(sid, None)
        self._pending_followup_by_student.pop(sid, None)
        self._last_course_by_student.pop(sid, None)

    # ---------- Public API ----------
    def chat(self, student_id: Union[str, int, None], message: str) -> Dict[str, Any]:
        sid = self._normalize_student_id(student_id)
        msg = (message or "").strip()

        # If no student id, ask for it (avoid greeting loop)
        if not sid:
            return self._wrap(
                "Please provide your Student ID (e.g., S003) so I can check your records.",
                recommendations=[],
                mode="rule"
            )

        # Load stats (single source of truth)
        stats = self._safe_student_stats(sid)
        if not stats:
            return self._wrap(
                f"I couldn't find a student with ID {sid}. Please check the ID and try again.",
                recommendations=[],
                mode="rule"
            )

        # Handle follow-up strategies for GPA improvement
        if self._wants_specific_strategies(msg):
            pending_followup = self._pending_followup_by_student.get(sid)
            if pending_followup == "GPA_STRATEGIES":
                self._pending_followup_by_student.pop(sid, None)
                return self._gpa_strategies(stats, sid)

        if self._is_course_strategy_request(msg):
            return self._gpa_strategies(stats, sid)

        # Handle confirmation flow ("yes" -> full record)
        confirmation = self._detect_confirmation(msg)
        pending = self._pending_confirm_by_student.get(sid)
        if confirmation is True:
            last_intent = self._last_intent_by_student.get(sid)
            if pending == "ACADEMIC_RECORD" or last_intent in [
                "GRADES",
                "ATTENDANCE",
                "ENROLLMENTS",
                "COURSES",
                "COMPLETED_COURSES",
            ]:
                self._pending_confirm_by_student.pop(sid, None)
                return self._answer_academic_record(stats, sid)
        if confirmation is False and pending == "ACADEMIC_RECORD":
            self._pending_confirm_by_student.pop(sid, None)
            return self._wrap(
                "Okay. Tell me which part you want (grades, attendance, enrollments, or courses).",
                recommendations=[],
                mode="rule"
            )

        # Multi-intent detection (e.g., "attendance and grades")
        intents = self._detect_intents(msg)
        is_explain = self._is_explain_request(msg)
        is_count = self._is_count_request(msg)

        # If user asks for full academic record, ask for confirmation
        if "ACADEMIC_RECORD" in intents:
            self._pending_confirm_by_student[sid] = "ACADEMIC_RECORD"
            return self._wrap(
                "I can show your full academic record (grades, attendance, enrollments, courses). "
                "Type 'yes' to display everything.",
                recommendations=[],
                mode="rule"
            )

        # Detect intent & resolve follow-ups
        detected = self._detect_intent(msg)
        intent = self._resolve_followup_intent(detected, msg, sid)
        course_match = self._find_course_match(msg, stats)
        attendance_detail = self._detect_attendance_detail(msg)
        attendance_details = self._detect_attendance_details(msg)
        is_course_status = self._is_course_status_request(msg)
        is_course_enroll_date = self._is_course_enrollment_date_request(msg)
        is_course_enroll_check = self._is_course_enrollment_check_request(msg)
        is_course_enroll_possible = self._is_course_enrollment_eligibility_request(msg)
        is_course_info = self._is_course_info_request(msg) or intent == "COURSE_INFO"
        is_course_compare = self._is_course_compare_request(msg)
        is_course_recommend = self._is_course_recommend_request(msg)

        # Greeting-only messages should get a friendly, time-based response
        if intent == "UNKNOWN" and self._detect_greeting(msg):
            return self._greeting_response(stats, sid)

        # If user requests multiple topics, combine responses
        intents_no_record = [i for i in intents if i != "ACADEMIC_RECORD"]
        if is_course_compare:
            compare_text = self._answer_course_compare(msg)
            if compare_text:
                return self._wrap(compare_text, recommendations=[], mode="rule")
        if is_course_recommend or "RECOMMENDATIONS" in intents_no_record:
            return self._answer_course_recommendations(stats, sid)
        if intent == "GPA_STRATEGIES" or "GPA_STRATEGIES" in intents_no_record:
            return self._gpa_strategies(stats, sid)
        if is_course_enroll_date:
            codes = self._extract_course_codes(msg)
            if codes:
                return self._answer_enrollment_check_or_date_by_code(stats, sid, codes, is_date=True)
        if is_course_enroll_date:
            course = course_match or self._find_course_match(msg, stats)
            if course:
                self._last_intent_by_student[sid] = "COURSES"
                self._last_course_by_student[sid] = course
                return self._answer_course_enrollment_date(stats, sid, course)
            course_ref = self._extract_course_reference(msg)
            if course_ref:
                self._last_intent_by_student[sid] = "COURSES"
                return self._answer_course_not_found(stats, sid, course_ref)

        if is_course_enroll_possible and not is_count:
            course = course_match or self._last_course_by_student.get(sid)
            if course:
                self._last_intent_by_student[sid] = "COURSES"
                self._last_course_by_student[sid] = course
                return self._answer_course_enrollment_eligibility(stats, sid, course)
            if "this course" in msg.lower() or "that course" in msg.lower():
                last_course = self._last_course_by_student.get(sid)
                if last_course:
                    self._last_intent_by_student[sid] = "COURSES"
                    return self._answer_course_enrollment_eligibility(stats, sid, last_course)
                return self._wrap(
                    "Please tell me the course name or code so I can check enrollment eligibility.",
                    recommendations=[],
                    mode="rule"
                )
            course_ref = self._extract_course_reference(msg)
            if course_ref:
                self._last_intent_by_student[sid] = "COURSES"
                return self._answer_course_not_found(stats, sid, course_ref)
            return self._wrap(
                "Please tell me the course name or code so I can check enrollment eligibility.",
                recommendations=[],
                mode="rule"
            )

        if "ENROLLMENTS" in intents_no_record and "COMPLETED_COURSES" in intents_no_record and self._is_course_list_request(msg):
            return self._answer_multi_intents(stats, sid, ["ENROLLMENTS", "COMPLETED_COURSES"], False)
        if "ENROLLMENTS" in intents_no_record and self._is_course_list_request(msg):
            return self._answer_enrollments(stats, sid)
        if "COURSE_INFO" in intents_no_record:
            course_info = self._find_course_info(msg, course_match)
            if course_info:
                self._last_intent_by_student[sid] = "COURSE_INFO"
                if course_info.get("type") == "single":
                    self._last_course_by_student[sid] = course_info.get("course")
                return self._answer_course_info(stats, sid, course_info, msg)
        if len(intents_no_record) > 1:
            if is_count:
                return self._answer_multi_counts(stats, sid, intents_no_record)
            return self._answer_multi_intents(stats, sid, intents_no_record, is_explain)

        if intent == "GRADES" and course_match:
            self._last_course_by_student[sid] = course_match
            return self._answer_course_grade(stats, sid, course_match)

        if "ENROLLMENTS" in intents_no_record and self._is_course_list_request(msg):
            return self._answer_enrollments(stats, sid)

        if is_course_info and not is_count and not (
            is_course_status or is_course_enroll_date or is_course_enroll_check or is_course_enroll_possible
        ):
            course_info = self._find_course_info(msg, course_match)
            if course_info:
                self._last_intent_by_student[sid] = "COURSE_INFO"
                if course_info.get("type") == "single":
                    self._last_course_by_student[sid] = course_info.get("course")
                return self._answer_course_info(stats, sid, course_info, msg)
            course_ref = self._extract_course_reference(msg)
            if course_ref:
                self._last_intent_by_student[sid] = "COURSES"
                return self._wrap(
                    f"I could not find {course_ref} in the official course list. Please verify the unit code or name.",
                    recommendations=[],
                    mode="rule"
                )
            return self._wrap(
                "Please tell me the unit code or unit name so I can provide details.",
                recommendations=[],
                mode="rule"
            )

        if course_match and is_course_enroll_check:
            self._last_intent_by_student[sid] = "COURSES"
            self._last_course_by_student[sid] = course_match
            return self._answer_course_enrollment_check(stats, sid, course_match)
        if is_course_enroll_check:
            codes = self._extract_course_codes(msg)
            if codes:
                return self._answer_enrollment_check_or_date_by_code(stats, sid, codes, is_date=False)

        if course_match and is_course_enroll_date:
            self._last_intent_by_student[sid] = "COURSES"
            self._last_course_by_student[sid] = course_match
            return self._answer_course_enrollment_date(stats, sid, course_match)

        if course_match and is_course_status and not is_count:
            self._last_intent_by_student[sid] = "COURSES"
            self._last_course_by_student[sid] = course_match
            return self._answer_course_status(stats, sid, course_match)
        if (is_course_status or is_course_enroll_date or is_course_enroll_check) and not course_match and not is_count:
            if is_course_status and self._is_course_overview_request(msg):
                self._last_intent_by_student[sid] = "COURSES"
                return self._answer_courses(stats, sid)
            course_ref = self._extract_course_reference(msg)
            if course_ref:
                self._last_intent_by_student[sid] = "COURSES"
                return self._answer_course_not_found(stats, sid, course_ref)

        if intent == "COMPLETED_COURSES" and not is_count:
            return self._answer_completed_courses(stats, sid)

        if intent == "ENROLLMENTS" and not is_count:
            return self._answer_enrollments(stats, sid)

        if attendance_details and intent in ["ATTENDANCE", "UNKNOWN", "WHY"]:
            if len(attendance_details) > 1:
                self._last_intent_by_student[sid] = "ATTENDANCE"
                return self._answer_attendance_multi(stats, sid, attendance_details, course_match)
            if attendance_detail:
                self._last_intent_by_student[sid] = "ATTENDANCE"
                return self._answer_attendance_detail(stats, sid, attendance_detail, course_match)

        # If we found a real intent, remember it
        if intent != "UNKNOWN":
            self._last_intent_by_student[sid] = intent

        # Answer data-first intents
        if intent == "GRADES":
            if is_count:
                return self._count_grades(stats, sid)
            return self._answer_grades(stats, sid)

        if intent == "GPA":
            if self._is_gpa_improve_request(msg):
                return self._improve_gpa(stats, sid)
            return self._answer_gpa(stats, sid)

        if intent == "ATTENDANCE":
            if is_count:
                return self._count_attendance(stats, sid)
            return self._answer_attendance(stats, sid)

        if intent == "ENROLLMENTS":
            if is_count:
                return self._count_enrollments(stats, sid)
            return self._answer_enrollments(stats, sid)

        if intent == "COURSES":
            if is_count:
                return self._count_courses(stats, sid)
            return self._answer_courses(stats, sid)

        if intent == "COMPLETED_COURSES":
            if is_count:
                return self._count_completed_courses(stats, sid)
            return self._answer_completed_courses(stats, sid)

        if intent == "JOIN_DATE":
            return self._answer_join_date(stats, sid)

        if intent == "WHY_GRADES":
            return self._explain_grades(stats, sid)

        if intent == "WHY_GPA":
            return self._explain_gpa(stats, sid)

        if intent == "WHY_ATTENDANCE":
            return self._explain_attendance(stats, sid)

        if intent == "WHY_ENROLLMENTS":
            return self._explain_enrollments(stats, sid)

        if intent == "WHY_COURSES":
            return self._explain_courses(stats, sid)

        # Other questions (fallback – NOT greeting spam)
        return self._wrap(
            "I can help with grades, attendance, enrollments, and courses. "
            "Try: 'What is my grades?', 'My attendance', 'Enrollments', or ask 'Why?' or 'Explain' after those. "
            "If you want your full academic record, type 'yes'.",
            recommendations=[],
            mode="rule"
        )

    # ---------- Intent ----------
    def _detect_intent(self, message: str) -> str:
        m = (message or "").lower()

        grade_words = ["grade", "grades", "mark", "marks", "score", "scores", "result", "results"]
        gpa_words = ["gpa", "grade point", "grade-point", "grade point average", "grade-point average"]
        att_words = ["attendance", "absent", "present", "late", "missed"]
        enr_words = ["enroll", "enrol", "enrollment", "enrolment", "registered", "registration", "how many courses"]
        course_words = ["courses", "course", "subjects", "subject", "units", "unit", "classes", "class"]
        record_words = [
            "academic record", "record", "transcript", "full record",
            "all info", "all information", "full details", "everything"
        ]
        completed_words = [
            "completed", "complete", "completed courses", "completed course", "finished", "finish",
            "passed", "done", "completed classes", "finished courses", "finished course"
        ]
        join_words = [
            "joined", "join date", "enrolled date", "enrollment date", "created at", "created_at",
            "when did i join", "when did i enroll", "when was i enrolled", "when was i created"
        ]
        recommend_words = [
            "recommend", "recommendation", "recommendations",
            "recomend", "recomendation", "recomendations",
            "reccomend", "reccomendation", "reccomendations",
            "suggest", "suggestion", "suggestions"
        ]

        if self._is_course_strategy_request(m):
            return "GPA_STRATEGIES"
        if self._is_course_info_request(m):
            return "COURSE_INFO"

        if any(w in m for w in gpa_words):
            return "GPA"
        if any(w in m for w in recommend_words):
            return "RECOMMENDATIONS"
        if any(w in m for w in grade_words):
            # “why my grades …” also contains grades keyword -> handled by follow-up resolver
            return "GRADES"
        if any(w in m for w in att_words):
            return "ATTENDANCE"
        if any(w in m for w in join_words):
            return "JOIN_DATE"
        if any(w in m for w in enr_words):
            return "ENROLLMENTS"
        if any(w in m for w in completed_words):
            return "COMPLETED_COURSES"
        if ("complete" in m or "completed" in m or "finish" in m or "finished" in m or "passed" in m or "done" in m) and (
            "course" in m or "courses" in m or "class" in m or "classes" in m or "subject" in m or "subjects" in m
        ):
            return "COMPLETED_COURSES"
        if any(w in m for w in course_words):
            return "COURSES"

        if any(w in m for w in record_words):
            return "ACADEMIC_RECORD"

        if "why" in m or "explain" in m or m.strip() in ["how", "how?"] or m.strip().startswith("why "):
            return "WHY"

        return "UNKNOWN"

    def _detect_greeting(self, message: str) -> bool:
        m = (message or "").lower().strip()
        greeting_phrases = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "good day", "greetings", "sain uu", "sain baina uu"
        ]
        return any(p in m for p in greeting_phrases)

    def _is_explain_request(self, message: str) -> bool:
        m = (message or "").lower().strip()
        return any(k in m for k in ["why", "explain", "reason"])

    def _is_count_request(self, message: str) -> bool:
        m = (message or "").lower()
        count_phrases = ["how many", "how much", "number of", "count of", "total"]
        return any(p in m for p in count_phrases)

    def _is_course_status_request(self, message: str) -> bool:
        m = (message or "").lower()
        if any(w in m for w in ["attendance", "absent", "present", "late", "lateness", "missed"]):
            return False
        if self._is_course_list_request(m) or any(w in m for w in ["list", "show", "overview"]):
            return False
        status_words = [
            "status", "enrolled", "completed", "complete", "in progress", "under progress",
            "failed", "withdrawn", "passed", "taking", "currently"
        ]
        return any(w in m for w in status_words)

    def _is_course_overview_request(self, message: str) -> bool:
        m = (message or "").lower()
        return any(p in m for p in [
            "course status overview",
            "status overview",
            "course overview",
            "overview of my courses",
            "overview"
        ])

    def _is_course_compare_request(self, message: str) -> bool:
        m = (message or "").lower()
        compare_words = ["compare", "difference", "diff", "versus", "vs", "which is harder", "harder", "easier"]
        return any(w in m for w in compare_words)

    def _is_course_recommend_request(self, message: str) -> bool:
        m = (message or "").lower()
        return any(w in m for w in [
            "recommend", "recommendation", "recommendations",
            "recomend", "recomendation", "recomendations",
            "reccomend", "reccomendation", "reccomendations",
            "suggest", "suggestion", "suggestions"
        ])

    def _is_course_enrollment_date_request(self, message: str) -> bool:
        m = (message or "").lower()
        date_words = [
            "when", "what date", "which date", "date", "term", "semester",
            "enrolled on", "enrolled date", "enrollment date", "joined date", "created at"
        ]
        enroll_words = ["enroll", "enrolled", "enrollment", "join", "joined"]
        return any(w in m for w in date_words) and any(w in m for w in enroll_words)

    def _is_course_enrollment_check_request(self, message: str) -> bool:
        m = (message or "").lower().strip()
        question_words = ["did", "do", "am", "are", "is", "was", "were", "have"]
        enroll_words = ["enroll", "enrolled", "enrollment", "registered", "registration"]
        if any(w in m for w in question_words) and any(w in m for w in enroll_words):
            return True
        if "am i enrolled" in m or "are i enrolled" in m:
            return True
        if "have i enrolled" in m or "have i" in m and "enrolled" in m:
            return True
        if "enrolled in" in m and "?" in m:
            return True
        return False

    def _is_course_enrollment_eligibility_request(self, message: str) -> bool:
        m = (message or "").lower().strip()
        if not m:
            return False
        enroll_words = ["enroll", "enrolled", "enrollment", "register", "registered", "take"]
        intent_words = ["can i", "am i", "eligible", "next semester", "next year"]
        if any(w in m for w in enroll_words) and any(w in m for w in intent_words):
            return True
        if "this course" in m and any(w in m for w in enroll_words):
            return True
        return False

    def _is_course_info_request(self, message: str) -> bool:
        m = (message or "").lower().strip()
        if not m:
            return False
        if self._is_course_enrollment_check_request(m) or self._is_course_enrollment_date_request(m):
            return False
        status_words = ["status", "enrolled", "enrollment", "registered", "grade", "completed", "in progress", "under progress"]
        if any(w in m for w in status_words):
            return False
        enroll_list_words = ["enrolled", "enrollment", "registered", "currently taking", "current courses", "currently enrolled", "taking"]
        if any(w in m for w in enroll_list_words):
            return False
        if self._is_course_list_request(m) or self._is_credit_request(m):
            return True
        if self._extract_department_query(m):
            return True
        if self._extract_course_codes(m):
            return True
        if self._contains_catalog_course_name(m):
            return True
        info_words = ["information", "info", "details", "about", "syllabus", "outline", "units", "unit", "explain", "describe", "what is", "what's"]
        course_words = ["course", "subject", "class", "module"]
        if any(w in m for w in info_words) and (any(w in m for w in course_words) or self._contains_catalog_course_name(m)):
            return True
        if any(p in m for p in ["tell me about", "give me information", "give me info on", "show me about", "show me details", "show me info"]):
            return True
        return False

    def _is_course_list_request(self, message: str) -> bool:
        m = (message or "").lower()
        list_phrases = [
            "list all", "show all", "all courses", "all units", "available courses", "available units",
            "what courses are available", "what units are available", "show available", "list available",
            "list my", "list enrolled", "list completed", "show enrolled", "show completed",
            "currently taking", "current courses", "courses am i taking", "courses i am taking"
        ]
        return any(p in m for p in list_phrases)

    def _is_credit_request(self, message: str) -> bool:
        m = (message or "").lower()
        return "credit" in m or "credits" in m or "credit points" in m

    def _wants_course_description(self, message: str) -> bool:
        m = (message or "").lower()
        return any(k in m for k in ["explain", "describe", "about", "details", "info", "information", "what is", "what's"])

    def _course_catalog(self) -> List[Dict[str, Any]]:
        return [
            {"course_code": "IT201", "course_name": "Web Development", "department": "Information Technology", "credit": None, "name": "Web Development"},
            {"course_code": "BUS101", "course_name": "Business Fundamentals", "department": "Business", "credit": None, "name": "Business Fundamentals"},
            {"course_code": "DS101", "course_name": "Data Science Basics", "department": "Data & Analytics", "credit": None, "name": "Data Science Basics"},
            {"course_code": "ENG101", "course_name": "Academic English", "department": "Languages", "credit": None, "name": "Academic English"},
            {"course_code": "IT101", "course_name": "Intro to IT", "department": "Information Technology", "credit": None, "name": "Intro to IT"},
            {"course_code": "IT202", "course_name": "Networking Basics", "department": "Information Technology", "credit": None, "name": "Networking Basics"},
            {"course_code": "IT303", "course_name": "Database Systems", "department": "Information Technology", "credit": None, "name": "Database Systems"},
            {"course_code": "DS202", "course_name": "Data Visualization", "department": "Data & Analytics", "credit": None, "name": "Data Visualization"},
            {"course_code": "ML101", "course_name": "Machine Learning Fundamentals", "department": "Data & Analytics", "credit": None, "name": "Machine Learning Fundamentals"},
            {"course_code": "MGT201", "course_name": "Project Management", "department": "Management", "credit": None, "name": "Project Management"},
            {"course_code": "COM101", "course_name": "Communication Skills", "department": "General Studies", "credit": None, "name": "Communication Skills"},
        ]

    def _extract_course_codes(self, message: str) -> List[str]:
        if not message:
            return []
        codes = re.findall(r"\b[A-Za-z]{2,4}\d{2,4}\b", message)
        return [c.upper() for c in codes]

    def _extract_department_query(self, message: str) -> Optional[str]:
        if not message:
            return None
        m = message.lower()
        dept_context = any(w in m for w in [
            "department", "departments", "course", "courses", "unit", "units", "list", "show", "available", "all"
        ])
        aliases = {
            "Information Technology": ["information technology", "it", "info tech"],
            "Data & Analytics": ["data & analytics", "data and analytics", "data analytics"],
            "Business": ["business"],
            "Languages": ["languages", "language"],
            "Management": ["management"],
            "General Studies": ["general studies", "general study"],
        }
        tokens = set(re.findall(r"[A-Za-z0-9]+", m))
        for dept, dept_aliases in aliases.items():
            for alias in dept_aliases:
                if alias == "it":
                    if "it" in tokens and any(w in m for w in ["course", "courses", "unit", "units", "department"]):
                        return dept
                    continue
                if alias in m and dept_context:
                    return dept
        return None

    def _contains_catalog_course_name(self, message: str) -> bool:
        m = (message or "").lower()
        for course in self._course_catalog():
            name = str(course.get("course_name") or "").lower()
            if name and name in m:
                return True
        return False

    def _best_course_name_matches(self, message: str) -> List[Dict[str, Any]]:
        def tokenize(text: str) -> List[str]:
            return re.findall(r"[A-Za-z0-9]+", text.lower())

        stop_words = {
            "course", "courses", "unit", "units", "class", "classes", "subject", "subjects",
            "about", "info", "information", "details", "explain", "describe", "tell", "me",
            "please", "can", "you", "give", "what", "is", "the", "of", "in", "for", "credit", "credits"
        }
        q_tokens = [t for t in tokenize(message) if t not in stop_words]
        if not q_tokens:
            return []

        scored = []
        for course in self._course_catalog():
            name = str(course.get("course_name") or "")
            name_tokens = tokenize(name)
            if not name_tokens:
                continue
            score = len(set(q_tokens) & set(name_tokens))
            if score > 0:
                scored.append((score, course))

        scored.sort(key=lambda x: (-x[0], str(x[1].get("course_code") or "")))
        return [c for _, c in scored]

    def _answer_course_compare(self, message: str) -> Optional[str]:
        catalog = self._course_catalog()
        if not catalog:
            return None

        codes = self._extract_course_codes(message)
        courses = []
        for code in codes:
            match = next((c for c in catalog if str(c.get("course_code") or "").upper() == code), None)
            if match:
                courses.append(match)

        if len(courses) < 2:
            name_matches = self._best_course_name_matches(message)
            for c in name_matches:
                if c not in courses:
                    courses.append(c)
                if len(courses) >= 2:
                    break

        if len(courses) < 2:
            return "Please tell me the two course codes or names you want to compare."

        a, b = courses[0], courses[1]
        a_text = f"{a.get('course_code')} - {a.get('course_name')} - {a.get('department')} - Credit: {self._format_credit(a.get('credit'))}"
        b_text = f"{b.get('course_code')} - {b.get('course_name')} - {b.get('department')} - Credit: {self._format_credit(b.get('credit'))}"

        m = (message or "").lower()
        hardness_note = ""
        if any(w in m for w in ["harder", "easier", "which is harder"]):
            hardness_note = " I do not have difficulty data to say which is harder. Please check the handbook."

        return f"Comparison:\n- {a_text}\n- {b_text}.{hardness_note}"

    def _answer_course_recommendations(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        catalog = self._course_catalog()
        if not catalog:
            return self._wrap(
                f"{name}, I do not have a course catalog to recommend from right now.",
                recommendations=[],
                mode="rule"
            )

        records = self._get_course_records(stats)
        completed = self._filter_course_records(records, {"completed"})
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})

        completed_codes = {str(r.get("course_code") or "").upper() for r in completed if r.get("course_code")}
        active_codes = {str(r.get("course_code") or "").upper() for r in active if r.get("course_code")}

        candidates = [
            c for c in catalog
            if str(c.get("course_code") or "").upper() not in completed_codes
            and str(c.get("course_code") or "").upper() not in active_codes
        ]

        if not candidates:
            return self._wrap(
                f"{name}, you are already enrolled in or have completed all catalog courses available.",
                recommendations=[],
                mode="rule"
            )

        dept_counts: Dict[str, int] = {}
        for rec in active + completed:
            code = str(rec.get("course_code") or "").upper()
            match = next((c for c in catalog if str(c.get("course_code") or "").upper() == code), None)
            dept = match.get("department") if match else None
            if dept:
                dept_counts[dept] = dept_counts.get(dept, 0) + 1

        if dept_counts:
            candidates.sort(key=lambda c: (-dept_counts.get(c.get("department") or "", 0), str(c.get("course_code") or "")))

        top = candidates[:3]
        recommend_lines = [
            f"- {c.get('course_code')} - {c.get('course_name')} ({c.get('department')})"
            for c in top
        ]

        enrolled_text = ", ".join([self._format_course_record(r) for r in active]) if active else "None"
        completed_text = ", ".join([self._format_course_record(r) for r in completed]) if completed else "None"

        response = (
            f"Hi {name}! You are currently enrolled in: {enrolled_text}. "
            f"Completed courses: {completed_text}. "
            "Based on this, you can enroll in these courses next semester or next year:\n"
            + "\n".join(recommend_lines)
        )
        return self._wrap(response, recommendations=[], mode="rule")

    def _is_gpa_improve_request(self, message: str) -> bool:
        m = (message or "").lower()
        improve_phrases = [
            "improve", "increase", "raise", "boost", "higher", "better", "get higher", "get better"
        ]
        return "gpa" in m and any(p in m for p in improve_phrases)

    def _wants_specific_strategies(self, message: str) -> bool:
        m = (message or "").lower().strip()
        m_clean = re.sub(r"[^a-z0-9\s]", "", m)
        phrases = [
            "specific strategies", "specific strategy", "more strategies", "detailed strategies",
            "give me strategies", "show me strategies", "want strategies",
            "please help me", "please help", "help me"
        ]
        if m_clean in [
            "yes", "yes please", "yes please help me", "please", "please help me", "help me"
        ]:
            return True
        return "strategy" in m_clean or any(p in m_clean for p in phrases) or m_clean in [
            "yes, i want specific strategies", "yes i want specific strategies"
        ]

    def _is_course_strategy_request(self, message: str) -> bool:
        m = (message or "").lower().strip()
        m_clean = re.sub(r"[^a-z0-9\s]", "", m)
        if "strategy" not in m_clean:
            return False
        phrases = [
            "per course", "by course", "each course", "for each course",
            "specific strategies per course", "break down", "breakdown"
        ]
        return "course" in m_clean or any(p in m_clean for p in phrases)

    def _detect_intents(self, message: str) -> List[str]:
        m = (message or "").lower()

        grade_words = ["grade", "grades", "mark", "marks", "score", "scores", "result", "results"]
        gpa_words = ["gpa", "grade point", "grade-point", "grade point average", "grade-point average"]
        att_words = ["attendance", "absent", "present", "late", "missed"]
        enr_words = [
            "enroll", "enrol", "enrollment", "enrolment", "registered", "registration",
            "how many courses", "currently taking", "current courses", "currently enrolled", "taking"
        ]
        course_words = ["courses", "course", "subjects", "subject", "units", "unit", "classes", "class"]
        record_words = [
            "academic record", "record", "transcript", "full record",
            "all info", "all information", "full details", "everything"
        ]
        completed_words = [
            "completed", "completed courses", "completed course", "finished", "finish",
            "passed", "done", "completed classes", "finished courses", "finished course"
        ]
        join_words = [
            "joined", "join date", "enrolled date", "enrollment date", "created at", "created_at",
            "when did i join", "when did i enroll", "when was i enrolled", "when was i created"
        ]
        recommend_words = [
            "recommend", "recommendation", "recommendations",
            "recomend", "recomendation", "recomendations",
            "reccomend", "reccomendation", "reccomendations",
            "suggest", "suggestion", "suggestions"
        ]
        intents = []
        if self._is_course_strategy_request(m):
            intents.append("GPA_STRATEGIES")
        if self._is_course_info_request(m):
            intents.append("COURSE_INFO")
        if any(w in m for w in gpa_words):
            intents.append("GPA")
        if any(w in m for w in recommend_words):
            intents.append("RECOMMENDATIONS")
        if any(w in m for w in grade_words):
            intents.append("GRADES")
        if any(w in m for w in att_words):
            intents.append("ATTENDANCE")
        join_hit = any(w in m for w in join_words)
        enrolled_hit = any(w in m for w in enr_words) and not join_hit
        if enrolled_hit:
            intents.append("ENROLLMENTS")
        completed_hit = any(w in m for w in completed_words) or (
            ("complete" in m or "completed" in m or "finish" in m or "finished" in m or "passed" in m or "done" in m)
            and ("course" in m or "courses" in m or "class" in m or "classes" in m or "subject" in m or "subjects" in m)
        )
        if completed_hit:
            intents.append("COMPLETED_COURSES")
        if any(w in m for w in course_words) and not completed_hit and not enrolled_hit and not join_hit:
            intents.append("COURSES")
        if any(w in m for w in record_words):
            intents.append("ACADEMIC_RECORD")
        if join_hit:
            intents.append("JOIN_DATE")

        # Deduplicate but preserve order
        seen = set()
        ordered = []
        for i in intents:
            if i not in seen:
                ordered.append(i)
                seen.add(i)
        return ordered

    def _detect_confirmation(self, message: str) -> Optional[bool]:
        m = (message or "").lower().strip()
        if m in ["yes", "y", "yep", "sure", "ok", "okay", "please"]:
            return True
        if m in ["no", "nope", "nah", "not now"]:
            return False
        return None

    def _detect_attendance_detail(self, message: str) -> Optional[str]:
        m = (message or "").lower()
        if "absent" in m or "absence" in m or "missed" in m or "miss" in m:
            return "absent"
        if "late" in m or "lateness" in m:
            return "late"
        if "present" in m or "attend" in m or "attendance" in m:
            return "present"
        return None

    def _detect_attendance_details(self, message: str) -> List[str]:
        m = (message or "").lower()
        details = []
        if any(w in m for w in ["absent", "absence", "missed", "miss", "absences"]):
            details.append("absent")
        if any(w in m for w in ["late", "lateness", "late arrivals", "late arrival"]):
            details.append("late")
        if any(w in m for w in ["present", "attend", "attendance"]):
            details.append("present")
        return details

    def _answer_attendance_multi(
        self,
        stats: Dict[str, Any],
        sid: str,
        details: List[str],
        course: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        att = stats.get("attendance") or {}
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)

        course_name = None
        if course:
            course_name = course.get("course_name") or course.get("course_code")

        parts = []
        if "absent" in details:
            parts.append(f"{absent} absence(s)")
        if "late" in details:
            parts.append(f"{late} late arrival(s)")
        if "present" in details:
            parts.append(f"{attended} attended")

        suffix = f" for {course_name}" if course_name else ""
        return self._wrap(
            f"{name}, you have {', '.join(parts)}{suffix}.",
            recommendations=[],
            mode="rule"
        )

    def _find_course_match(self, message: str, stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        m = (message or "").lower()
        records = self._get_course_records(stats)
        if not records:
            return None

        def normalize_token(token: str) -> str:
            t = token.lower().strip()
            if t.endswith("ing") and len(t) > 4:
                t = t[:-3]
            return t

        def tokenize(text: str) -> List[str]:
            return [normalize_token(t) for t in re.findall(r"[A-Za-z0-9]+", text.lower())]

        def score_match(text: str) -> int:
            if not text:
                return 0
            t = text.lower().strip()
            if not t:
                return 0
            if t in m:
                return len(t)
            return 0

        message_tokens = set(tokenize(m))

        best = None
        best_score = 0
        for rec in records:
            code = str(rec.get("course_code") or "")
            name = str(rec.get("course_name") or "")
            score = max(score_match(code), score_match(name))
            if score == 0 and name:
                name_tokens = tokenize(name)
                if name_tokens and all(t in message_tokens for t in name_tokens):
                    score = len(" ".join(name_tokens))
            if score > best_score:
                best = rec
                best_score = score

        if best_score > 0:
            return best

        # Fallback: check DB course catalog if available
        catalog_match = self._find_course_in_catalog(message)
        if catalog_match:
            return {
                "course_code": catalog_match.get("course_code"),
                "course_name": catalog_match.get("name") or catalog_match.get("course_code"),
                "status": "not_enrolled",
                "grade": None,
            }

        return None

    def _find_course_in_catalog(self, message: str) -> Optional[Dict[str, Any]]:
        if not hasattr(self.data_loader, "find_course_in_catalog"):
            return None
        try:
            return self.data_loader.find_course_in_catalog(message)
        except Exception:
            return None

    def _extract_course_reference(self, message: str) -> Optional[str]:
        if not message:
            return None
        m = message.strip()
        code_match = re.search(r"\b[A-Za-z]{2,4}\d{2,4}\b", m)
        if code_match:
            return code_match.group(0).upper()

        stop_words = {
            "show", "list", "me", "my", "status", "grade", "grades", "enrolled", "enroll",
            "completed", "complete", "did", "i", "am", "is", "are", "the", "a",
            "an", "please", "can", "you", "tell", "about", "course", "courses",
            "subject", "subjects", "class", "classes", "in", "progress", "under", "overview",
            "this", "that"
        }
        tokens = re.findall(r"[A-Za-z0-9]+", m)
        if not tokens:
            return None
        filtered = [t for t in tokens if t.lower() not in stop_words]
        if not filtered:
            return None
        words = []
        for t in filtered:
            if any(ch.isdigit() for ch in t):
                words.append(t.upper())
            else:
                words.append(t.capitalize())
        return " ".join(words)

    def _resolve_followup_intent(self, detected: str, message: str, sid: str) -> str:
        m = (message or "").lower().strip()

        last = self._last_intent_by_student.get(sid, "UNKNOWN")

        # If the user asks "why/explain ..." and also mentions grades/attendance etc
        if "why" in m or "explain" in m or "reason" in m:
            if "gpa" in m:
                return "WHY_GPA"
            if any(w in m for w in ["grade", "grades", "gpa", "mark", "score", "result"]):
                return "WHY_GRADES"
            if any(w in m for w in ["attendance", "absent", "late", "missed"]):
                return "WHY_ATTENDANCE"
            if any(w in m for w in ["enroll", "enrol", "enrollment", "registered", "registration"]):
                return "WHY_ENROLLMENTS"
            if any(w in m for w in ["course", "courses", "subject", "subjects", "class", "classes"]):
                return "WHY_COURSES"

        # Pure follow-up: "Why/Explain?" => use last intent
        if detected in ["WHY", "UNKNOWN"] and (
            m in ["why", "why?", "how", "how?", "explain", "explain?"] or "explain" in m or "why" in m
        ):
            if last == "GPA":
                return "WHY_GPA"
            if last == "GRADES":
                return "WHY_GRADES"
            if last == "ATTENDANCE":
                return "WHY_ATTENDANCE"
            if last == "ENROLLMENTS":
                return "WHY_ENROLLMENTS"
            if last == "COURSES":
                return "WHY_COURSES"

        # If detected a normal intent, keep it
        return detected

    # ---------- Answers ----------
    def _answer_grades(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}

        if not isinstance(grades, dict) or not grades:
            records = self._get_course_records(stats)
            completed = self._filter_course_records(records, {"completed"})
            active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
            enrolled_text = ", ".join([self._format_course_record(r) for r in active]) if active else "None"
            completed_text = ", ".join([self._format_course_record(r) for r in completed]) if completed else "None"
            if not completed:
                return self._wrap(
                    f"Hi {name}! You don't have grades yet because you have no completed courses. "
                    f"Enrolled courses: {enrolled_text}. {self._full_record_prompt()}",
                    [],
                    mode="rule"
                )
            return self._wrap(
                f"Hi {name}! I can't find grades data for your completed courses yet. "
                f"Completed courses: {completed_text}. Enrolled courses: {enrolled_text}. {self._full_record_prompt()}",
                [],
                mode="rule"
            )

        # Compute average
        vals = []
        parts = []
        for k, v in grades.items():
            try:
                g = float(v)
                vals.append(g)
                parts.append(f"{k}: {int(g) if g.is_integer() else g}")
            except Exception:
                continue

        avg = sum(vals) / len(vals) if vals else 0.0
        return self._wrap(
            f"Welcome back, {name}! Here are your grades: {', '.join(parts)}. "
            f"Your average is {avg:.1f}. {self._full_record_prompt()}",
            recommendations=[],
            mode="rule"
        )

    def _answer_gpa(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        gpa = self._calculate_gpa(stats)
        if gpa is None:
            return self._wrap(
                f"Hi {name}! I can't calculate your GPA yet because grade data is missing.",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! Your current GPA is {gpa:.2f}.",
            recommendations=[],
            mode="rule"
        )

    def _answer_course_grade(self, stats: Dict[str, Any], sid: str, course: Dict[str, Any]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        course_name = course.get("course_name") or course.get("course_code") or "the course"
        status = (course.get("status") or "").lower()
        grade = course.get("grade")

        if grade is not None:
            return self._wrap(
                f"{name}, your grade for {course_name} is {grade:.0f}%.",
                recommendations=[],
                mode="rule"
            )

        if status == "enrolled":
            return self._wrap(
                f"{name}, {course_name} is currently marked as enrolled and does not have a final grade yet.",
                recommendations=[],
                mode="rule"
            )

        return self._wrap(
            f"{name}, I could not find a finalized grade for {course_name} yet.",
            recommendations=[],
            mode="rule"
        )

    def _answer_course_status(self, stats: Dict[str, Any], sid: str, course: Dict[str, Any]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        course_name = course.get("course_name") or course.get("course_code") or "the course"
        status = self._status_label(course.get("status") or "")
        grade = course.get("grade")

        if str(course.get("status") or "") == "not_enrolled":
            return self._wrap(
                f"{name}, {course_name} is not marked as enrolled or completed in your record.",
                recommendations=[],
                mode="rule"
            )

        if grade is not None:
            return self._wrap(
                f"{name}, {course_name} is marked as {status}. Your recorded grade is {grade:.0f}%.",
                recommendations=[],
                mode="rule"
            )

        return self._wrap(
            f"{name}, {course_name} is currently marked as {status}.",
            recommendations=[],
            mode="rule"
        )

    def _answer_course_enrollment_date(self, stats: Dict[str, Any], sid: str, course: Dict[str, Any]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        code = course.get("course_code") or ""
        cname = course.get("course_name") or code or "the course"
        status_raw = str(course.get("status") or "")
        if status_raw == "not_enrolled":
            return self._wrap(
                f"{name}, you are not enrolled in {code} - {cname}.",
                recommendations=[],
                mode="rule"
            )

        enroll_date = self._format_date_only(course.get("enrollment_date") or course.get("enrolled_date"))
        term = course.get("term")
        if enroll_date:
            return self._wrap(
                f"{name}, you enrolled in {code} - {cname} on {enroll_date}.",
                recommendations=[],
                mode="rule"
            )
        if term:
            return self._wrap(
                f"{name}, you enrolled in {code} - {cname} in {term}.",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"{name}, I don't have the enrollment date for {code} - {cname} on file yet.",
            recommendations=[],
            mode="rule"
        )

    def _answer_course_enrollment_check(self, stats: Dict[str, Any], sid: str, course: Dict[str, Any]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        code = course.get("course_code") or ""
        cname = course.get("course_name") or code or "the course"
        status_raw = str(course.get("status") or "")
        if status_raw == "not_enrolled":
            return self._wrap(
                f"{name}, you did not enroll in {code} - {cname}.",
                recommendations=[],
                mode="rule"
            )

        enroll_date = self._format_date_only(course.get("enrollment_date") or course.get("enrolled_date"))
        if enroll_date:
            return self._wrap(
                f"{name}, yes. You enrolled in {code} - {cname} on {enroll_date}.",
                recommendations=[],
                mode="rule"
            )

        return self._wrap(
            f"{name}, yes. You enrolled in {code} - {cname}, but I don't have the enrollment date on file yet.",
            recommendations=[],
            mode="rule"
        )

    def _answer_enrollment_check_or_date_by_code(
        self,
        stats: Dict[str, Any],
        sid: str,
        codes: List[str],
        is_date: bool,
    ) -> Dict[str, Any]:
        name = stats.get("name")
        name_prefix = f"{name}, " if name else ""
        records = self._get_course_records(stats)
        parts: List[str] = []

        for code in codes:
            catalog_course = self._find_course_in_catalog(code)
            if not catalog_course:
                parts.append(f"I can't find {code} in the unit catalog. Please check the code.")
                continue

            unit_name = catalog_course.get("course_name") or catalog_course.get("name") or code
            credit_text = self._format_credit(catalog_course.get("credit"))
            lines = [
                f"Unit Code: {code}",
                f"Unit Name: {unit_name}",
                f"Department: {catalog_course.get('department') or ''}",
                f"Credit: {credit_text}",
            ]
            if credit_text == "Not provided":
                lines.append("Note: Credit not provided. Please check with admin/handbook.")

            record = next(
                (r for r in records if str(r.get("course_code") or "").upper() == code.upper()),
                None,
            )
            status = self._normalize_status(record.get("status")) if record else ""
            enrolled = status in ["enrolled", "in_progress", "under_progress"]

            if is_date:
                if not enrolled:
                    lines.append(
                        f"{name_prefix}you are not enrolled in {code} - {unit_name}, so there is no enrollment date."
                    )
                else:
                    enroll_date = self._format_date_only(
                        record.get("enrollment_date") or record.get("enrolled_date")
                    )
                    term = record.get("term")
                    if enroll_date:
                        term_text = f" (Term: {term})" if term else ""
                        lines.append(
                            f"You enrolled in {code} - {unit_name} on {enroll_date}{term_text}."
                        )
                    else:
                        lines.append(
                            "You are enrolled in "
                            f"{code} - {unit_name}, but the enrollment date/term is not available. "
                            "Please check the portal or admin."
                        )
            else:
                if enrolled:
                    lines.append(f"{name_prefix}you are enrolled in {code} - {unit_name}.")
                else:
                    lines.append(f"{name_prefix}you are not enrolled in {code} - {unit_name}.")

            parts.append("\n".join(lines))

        return self._wrap("\n\n".join(parts), recommendations=[], mode="rule")

    def _answer_course_enrollment_eligibility(self, stats: Dict[str, Any], sid: str, course: Dict[str, Any]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        code = course.get("course_code") or ""
        cname = course.get("course_name") or code or "the course"
        status = self._normalize_status(course.get("status"))
        if not status and code:
            records = self._get_course_records(stats)
            match = next((r for r in records if str(r.get("course_code") or "").upper() == str(code).upper()), None)
            if match:
                status = self._normalize_status(match.get("status"))
                if match.get("course_name"):
                    cname = match.get("course_name")
        catalog_course = self._find_course_in_catalog(code or cname)
        in_catalog = catalog_course is not None

        details = catalog_course or {
            "course_code": code,
            "course_name": cname,
            "department": course.get("department") or "",
            "credit": course.get("credit"),
        }

        def _course_info_lines(info: Dict[str, Any]) -> List[str]:
            return [
                f"Unit Code: {info.get('course_code') or ''}",
                f"Unit Name: {info.get('course_name') or info.get('name') or ''}",
                f"Department: {info.get('department') or ''}",
                f"Credit: {self._format_credit(info.get('credit'))}",
            ]

        if not in_catalog:
            response = (
                f"{name}, no, you can't enroll in {code} - {cname} next semester or next year because it is not in the catalog right now."
            )
            return self._wrap(response, recommendations=[], mode="rule")

        if status in ["enrolled", "in_progress", "under_progress"]:
            lines = [
                f"{name}, no, you can't enroll in {code} - {cname} next semester or next year because you are already enrolled.",
                *(_course_info_lines(details)),
            ]
            return self._wrap("\n".join(lines), recommendations=[], mode="rule")

        if status == "completed":
            lines = [
                f"{name}, no, you can't enroll in {code} - {cname} next semester or next year because you already completed it.",
                *(_course_info_lines(details)),
            ]
            return self._wrap("\n".join(lines), recommendations=[], mode="rule")

        if status in ["failed", "withdrawn"]:
            lines = [
                f"{name}, yes, you can enroll in {code} - {cname} next semester or next year.",
                *(_course_info_lines(details)),
            ]
            return self._wrap("\n".join(lines), recommendations=[], mode="rule")

        lines = [
            f"{name}, yes, you can enroll in {code} - {cname} next semester or next year.",
            *(_course_info_lines(details)),
        ]
        return self._wrap("\n".join(lines), recommendations=[], mode="rule")

    def _answer_course_info(self, stats: Dict[str, Any], sid: str, course_info: Dict[str, Any], message: str) -> Dict[str, Any]:
        info_type = course_info.get("type")
        if info_type == "clarify":
            options = course_info.get("options") or []
            if not options:
                return self._wrap(
                    "Which unit did you mean? Please share the unit code or full unit name.",
                    recommendations=[],
                    mode="rule"
                )
            option_text = "; ".join([
                f"{c.get('course_code')} - {c.get('course_name')}" for c in options
            ])
            return self._wrap(
                f"Which unit did you mean? {option_text}.",
                recommendations=[],
                mode="rule"
            )

        if info_type == "list":
            courses = course_info.get("courses") or []
            if not courses:
                return self._wrap(
                    "I could not find any matching units in the official course list.",
                    recommendations=[],
                    mode="rule"
                )
            lines = [
                f"- {c.get('course_code')} - {c.get('course_name')} - {c.get('department')} - Credit: {self._format_credit(c.get('credit'))}"
                for c in courses
            ]
            text = "\n".join(lines)
            if any(self._format_credit(c.get("credit")) == "Not provided" for c in courses):
                text = f"{text}\nCredit: Not provided. Please check with admin/handbook for official credit values."
            return self._wrap(text, recommendations=[], mode="rule")

        course = course_info.get("course") or course_info
        code = course.get("course_code") or ""
        cname = course.get("course_name") or course.get("name") or code or ""
        dept = course.get("department") or ""
        credit = self._format_credit(course.get("credit"))

        lines = [
            f"Unit Code: {code}",
            f"Unit Name: {cname}",
            f"Department: {dept}",
            f"Credit: {credit}",
        ]

        if credit == "Not provided":
            lines.append("Note: Credit not provided. Please check with admin/handbook.")

        if self._wants_course_description(message):
            lines.append(f"Overview: Focuses on foundational concepts and practical skills related to {cname}.")
            lines.append("Typical skills: core concepts, terminology, and applied practice.")

        return self._wrap("\n".join(lines), recommendations=[], mode="rule")

    def _find_course_info(self, message: str, course_match: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        catalog = self._course_catalog()
        if not catalog:
            return None

        codes = self._extract_course_codes(message)
        if codes:
            matched = []
            for code in codes:
                for course in catalog:
                    if str(course.get("course_code") or "").upper() == code:
                        matched.append(course)
                        break
            if matched:
                if len(matched) == 1:
                    return {"type": "single", "course": matched[0]}
                return {"type": "list", "courses": matched}

        name_matches = self._best_course_name_matches(message)
        if name_matches:
            top_score_matches = name_matches[:3]
            if len(top_score_matches) == 1:
                return {"type": "single", "course": top_score_matches[0]}
            return {"type": "clarify", "options": top_score_matches}

        dept = self._extract_department_query(message)
        if dept:
            dept_courses = [c for c in catalog if c.get("department") == dept]
            if self._is_course_list_request(message) or any(w in message.lower() for w in ["courses", "units"]):
                return {"type": "list", "courses": dept_courses}
            return {"type": "clarify", "options": dept_courses[:3]}

        if self._is_course_list_request(message):
            return {"type": "list", "courses": catalog}

        if course_match:
            code = course_match.get("course_code") or ""
            name = course_match.get("course_name") or ""
            for course in catalog:
                if code and str(course.get("course_code") or "").upper() == str(code).upper():
                    return {"type": "single", "course": course}
                if name and str(course.get("course_name") or "").lower() == str(name).lower():
                    return {"type": "single", "course": course}

        return None

    def _fallback_course_info_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "course_code": "IT201",
                "course_name": "Web Development",
                "department": "Information Technology",
                "credit": None,
                "name": "Web Development",
            },
            {
                "course_code": "BUS101",
                "course_name": "Business Fundamentals",
                "department": "Business",
                "credit": None,
                "name": "Business Fundamentals",
            },
            {
                "course_code": "DS101",
                "course_name": "Data Science Basics",
                "department": "Data & Analytics",
                "credit": None,
                "name": "Data Science Basics",
            },
            {
                "course_code": "ENG101",
                "course_name": "Academic English",
                "department": "Languages",
                "credit": None,
                "name": "Academic English",
            },
            {
                "course_code": "IT101",
                "course_name": "Intro to IT",
                "department": "Information Technology",
                "credit": None,
                "name": "Intro to IT",
            },
            {
                "course_code": "IT202",
                "course_name": "Networking Basics",
                "department": "Information Technology",
                "credit": None,
                "name": "Networking Basics",
            },
            {
                "course_code": "IT303",
                "course_name": "Database Systems",
                "department": "Information Technology",
                "credit": None,
                "name": "Database Systems",
            },
            {
                "course_code": "DS202",
                "course_name": "Data Visualization",
                "department": "Data & Analytics",
                "credit": None,
                "name": "Data Visualization",
            },
            {
                "course_code": "ML101",
                "course_name": "Machine Learning Fundamentals",
                "department": "Data & Analytics",
                "credit": None,
                "name": "Machine Learning Fundamentals",
            },
            {
                "course_code": "MGT201",
                "course_name": "Project Management",
                "department": "Management",
                "credit": None,
                "name": "Project Management",
            },
            {
                "course_code": "COM101",
                "course_name": "Communication Skills",
                "department": "General Studies",
                "credit": None,
                "name": "Communication Skills",
            },
        ]

    def _format_credit(self, credit: Optional[Any]) -> str:
        if credit is None or str(credit).strip() == "":
            return "Not provided"
        return str(credit)

    def _answer_course_not_found(self, stats: Dict[str, Any], sid: str, course_ref: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        return self._wrap(
            f"{name}, I could not find {course_ref} in the course catalog or your record.",
            recommendations=[],
            mode="rule"
        )

    def _answer_attendance(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        att = stats.get("attendance") or {}

        # Support multiple key names
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)

        if total <= 0:
            return self._wrap(
                f"Hi {name}! I can't find attendance data for you yet. {self._full_record_prompt()}",
                [],
                mode="rule"
            )

        rate = (attended / total) * 100
        return self._wrap(
            f"Welcome back, {name}! Your attendance rate is {rate:.1f}% ({attended}/{total} attended). "
            f"Late: {late}, Absent: {absent}. {self._full_record_prompt()}",
            recommendations=[],
            mode="rule"
        )

    def _answer_attendance_detail(
        self,
        stats: Dict[str, Any],
        sid: str,
        detail: str,
        course: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        att = stats.get("attendance") or {}
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)

        course_name = None
        if course:
            course_name = course.get("course_name") or course.get("course_code")

        if total <= 0 and detail != "present":
            return self._wrap(
                f"{name}, I do not have attendance records available yet.",
                recommendations=[],
                mode="rule"
            )

        if detail == "absent":
            if absent > 0:
                suffix = f" for {course_name}" if course_name else ""
                return self._wrap(
                    f"{name}, yes. You have {absent} recorded absence(s){suffix}.",
                    recommendations=[],
                    mode="rule"
                )
            return self._wrap(
                f"{name}, there are no recorded absences in your attendance history.",
                recommendations=[],
                mode="rule"
            )

        if detail == "late":
            if late > 0:
                suffix = f" for {course_name}" if course_name else ""
                return self._wrap(
                    f"{name}, you were late {late} time(s){suffix}.",
                    recommendations=[],
                    mode="rule"
                )
            return self._wrap(
                f"{name}, there are no recorded late arrivals in your attendance history.",
                recommendations=[],
                mode="rule"
            )

        if detail == "present":
            if total <= 0:
                return self._wrap(
                    f"{name}, I do not have attendance records available yet.",
                    recommendations=[],
                    mode="rule"
                )
            rate = (attended / total) * 100 if total else 0
            return self._wrap(
                f"{name}, your attendance rate is {rate:.1f}% ({attended}/{total} attended).",
                recommendations=[],
                mode="rule"
            )

        return self._answer_attendance(stats, sid)

    def _answer_enrollments(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        courses = [self._format_course_record(r) for r in active]
        if not courses:
            return self._wrap(
                f"Hi {name}! I can't find active enrollments in your record yet. {self._full_record_prompt()}",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! Your current enrollment count is {len(courses)}. Enrolled courses: {', '.join(courses)}. "
            f"{self._full_record_prompt()}",
            recommendations=[],
            mode="rule"
        )

    def _answer_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        # Same as enrollments, but wording
        name = stats.get("name", "Student")
        overview = self._course_overview_text(stats)
        return self._wrap(
            f"Hi {name}! {overview} {self._full_record_prompt()}",
            recommendations=[],
            mode="rule"
        )

    def _answer_completed_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        completed = self._filter_course_records(records, {"completed"})
        courses = [self._format_course_record(r) for r in completed]
        if not courses:
            return self._wrap(
                f"Hi {name}! I can't find completed courses in your record yet. {self._full_record_prompt()}",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! Your completed courses are: {', '.join(courses)}. {self._full_record_prompt()}",
            recommendations=[],
            mode="rule"
        )

    def _answer_join_date(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        join_date = stats.get("join_date") or stats.get("created_at")
        if not join_date:
            return self._wrap(
                f"Hi {name}! I don't have your enrollment date on file yet.",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! Your enrollment date is {join_date}.",
            recommendations=[],
            mode="rule"
        )

    def _answer_academic_record(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")

        grades = stats.get("grades") or stats.get("course_grades") or {}
        if isinstance(grades, dict) and grades:
            grade_parts = [f"{k}: {v}" for k, v in grades.items()]
            grades_text = ", ".join(grade_parts)
        else:
            grades_text = "No grade data available"

        att = stats.get("attendance") or {}
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)
        if total > 0:
            rate = (attended / total) * 100
            attendance_text = f"{rate:.1f}% ({attended}/{total} attended), late: {late}, absent: {absent}"
        else:
            attendance_text = "No attendance data available"

        enrolled = stats.get("enrolled_courses") or stats.get("courses") or []
        if isinstance(enrolled, dict):
            enrolled = list(enrolled.keys())
        enrolled_text = ", ".join([str(c) for c in enrolled]) if enrolled else "None"

        completed = stats.get("completed_courses") or []
        completed_text = ", ".join([str(c) for c in completed]) if completed else "None"

        record = stats.get("academic_record") or []
        record_lines = []
        if isinstance(record, list) and record:
            for rec in record:
                code = rec.get("course_code") or ""
                cname = rec.get("course_name") or code
                term = rec.get("term") or ""
                status = rec.get("status") or ""
                grade = rec.get("grade")
                grade_text = f", grade: {grade}" if grade is not None else ""
                term_text = f" ({term})" if term else ""
                record_lines.append(f"- {code} - {cname}{term_text} - {status}{grade_text}")
        record_text = "\n".join(record_lines) if record_lines else "- No course history available"

        response = (
            f"Here is your full academic record, {name}:\n"
            f"Grades: {grades_text}\n"
            f"Attendance: {attendance_text}\n"
            f"Enrolled courses: {enrolled_text}\n"
            f"Completed courses: {completed_text}\n"
            f"Course history:\n{record_text}"
        )

        return self._wrap(response, recommendations=[], mode="rule")

    # ---------- Explanations for "Why" ----------
    def _explain_grades(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}
        if not isinstance(grades, dict) or not grades:
            return self._wrap(f"{name}, I don't have grade data to explain yet.", [], mode="rule")

        vals = []
        items = []
        for k, v in grades.items():
            try:
                g = float(v)
                vals.append(g)
                items.append((k, g))
            except Exception:
                pass

        if not vals:
            return self._wrap(f"{name}, I couldn't compute your average from the current grade data.", [], mode="rule")

        avg = sum(vals) / len(vals)
        low_course, low_val = min(items, key=lambda x: x[1])
        high_course, high_val = max(items, key=lambda x: x[1])

        below = [f"{c} ({v:.0f})" for c, v in items if v < avg]
        below_txt = ", ".join(below) if below else "None"

        records = self._get_course_records(stats)
        completed = self._filter_course_records(records, {"completed"})
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})

        completed_names = [
            f"{r.get('course_name') or r.get('course_code')} ({r.get('course_code') or r.get('course_name')})"
            for r in completed
        ]
        active_names = [
            f"{r.get('course_name') or r.get('course_code')} ({r.get('course_code') or r.get('course_name')})"
            for r in active
        ]
        completed_text = ", ".join(completed_names) if completed_names else "None"
        active_text = ", ".join(active_names) if active_names else "None"

        return self._wrap(
            f"{name}, your average is {avg:.1f} because it’s the mean of your course scores. "
            f"Your highest is {high_course}: {high_val:.0f} and your lowest is {low_course}: {low_val:.0f}. "
            f"Your completed course count is {len(completed)}: {completed_text}. "
            f"You have {len(active)} enrolled course(s): {active_text}. "
            "This means your overall grade average may change after these courses are completed. "
            f"Courses below your average: {below_txt}. "
            f"If you lift the lowest subject(s), your average will rise quickly.",
            recommendations=[],
            mode="rule"
        )

    def _explain_gpa(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}
        if not isinstance(grades, dict) or not grades:
            return self._wrap(
                f"{name}, I don't have grade data to explain your GPA yet.",
                recommendations=[],
                mode="rule"
            )
        gpa = self._calculate_gpa(stats)
        if gpa is None:
            return self._wrap(
                f"{name}, I can't compute your GPA from the current data.",
                recommendations=[],
                mode="rule"
            )
        vals = []
        items = []
        for k, v in grades.items():
            try:
                g = float(v)
                vals.append(g)
                items.append((k, g))
            except Exception:
                continue
        avg = sum(vals) / len(vals) if vals else 0.0
        if not items:
            return self._wrap(
                f"{name}, I can't compute details for your GPA without numeric grades.",
                recommendations=[],
                mode="rule"
            )

        low_course, low_val = min(items, key=lambda x: x[1])
        high_course, high_val = max(items, key=lambda x: x[1])
        below = [f"{c} ({v:.0f})" for c, v in items if v < avg]
        below_txt = ", ".join(below) if below else "None"

        records = self._get_course_records(stats)
        completed = self._filter_course_records(records, {"completed"})
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})

        completed_names = [
            f"{r.get('course_name') or r.get('course_code')} ({r.get('course_code') or r.get('course_name')})"
            for r in completed
        ]
        active_names = [
            f"{r.get('course_name') or r.get('course_code')} ({r.get('course_code') or r.get('course_name')})"
            for r in active
        ]
        completed_text = ", ".join(completed_names) if completed_names else "None"
        active_text = ", ".join(active_names) if active_names else "None"

        return self._wrap(
            f"{name}, your GPA is {gpa:.2f} based on your course scores. "
            f"Your average score is {avg:.1f}, and that average is used to estimate GPA. "
            f"Your highest is {high_course}: {high_val:.0f} and your lowest is {low_course}: {low_val:.0f}. "
            f"Your completed course count is {len(completed)}: {completed_text}. "
            f"You have {len(active)} enrolled course(s): {active_text}. "
            "This means your GPA may change after these courses are completed. "
            f"Courses below your average: {below_txt}. "
            f"If you lift the lowest subject(s), your GPA will rise quickly.",
            recommendations=[],
            mode="rule"
        )

    def _improve_gpa(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}
        if not isinstance(grades, dict) or not grades:
            return self._wrap(
                f"Hi {name}! I need grade data to suggest GPA improvements."
                " Please ask your instructor to update your grades.",
                recommendations=[],
                mode="rule"
            )

        items = []
        for k, v in grades.items():
            try:
                items.append((k, float(v)))
            except Exception:
                continue

        if not items:
            return self._wrap(
                f"Hi {name}! I can't analyze your GPA without numeric grades.",
                recommendations=[],
                mode="rule"
            )

        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        active_codes = {r.get("course_code") for r in active if r.get("course_code")}

        active_items = [item for item in items if item[0] in active_codes]
        focus_items = active_items if active_items else items

        focus_items.sort(key=lambda x: x[1])
        lowest = focus_items[:2]
        low_text = ", ".join([f"{c} ({v:.0f})" for c, v in lowest])

        active_text = ", ".join([
            f"{r.get('course_name') or r.get('course_code')} ({r.get('course_code') or r.get('course_name')})"
            for r in active
        ]) if active else "None"

        tips = (
            f"You can still improve your GPA through your enrolled course(s): {active_text}. "
            f"Focus first on your lowest-scoring enrolled course(s): {low_text}. "
            "Aim for a 5-10 point increase there, then reinforce attendance and assignment completion. "
            "If you want, I can break down specific strategies per course."
        )
        self._pending_followup_by_student[sid] = "GPA_STRATEGIES"
        return self._wrap(
            f"Hi {name}! To raise your GPA: {tips}",
            recommendations=[],
            mode="rule"
        )

    def _gpa_strategies(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        if not active:
            return self._wrap(
                f"Hi {name}! I can provide course-specific strategies once you have enrolled courses.",
                recommendations=[],
                mode="rule"
            )

        grades = stats.get("grades") or stats.get("course_grades") or {}
        score_by_code = {}
        if isinstance(grades, dict):
            for k, v in grades.items():
                try:
                    score_by_code[k] = float(v)
                except Exception:
                    continue

        course_items = []
        for rec in active:
            code = rec.get("course_code")
            cname = rec.get("course_name") or code
            score = score_by_code.get(code)
            course_items.append((code, cname, score))

        course_items.sort(key=lambda item: (item[2] is None, item[2] if item[2] is not None else 0, item[0] or ""))

        lines = [f"Specific strategies per enrolled course for {name}:"]
        for code, cname, score in course_items:
            if score is None:
                header = f"- {code} - {cname}:"
            else:
                header = f"- {code} - {cname} (current: {score:.0f}):"
            lines.append(header)
            lines.append("  1) Create a weekly study plan with two focused blocks for this course.")
            lines.append("  2) Review lecture notes within 24 hours and summarize key concepts.")
            lines.append("  3) Practice problems or quizzes every week; track mistakes and redo them.")
            lines.append("  4) Start assignments early and use office hours for hard topics.")

        return self._wrap("\n".join(lines), recommendations=[], mode="rule")

    def _explain_attendance(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        att = stats.get("attendance") or {}
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)

        if total <= 0:
            return self._wrap(f"{name}, I don't have attendance data to explain yet.", [], mode="rule")

        rate = (attended / total) * 100
        return self._wrap(
            f"{name}, your attendance is {rate:.1f}% because you attended {attended} out of {total} classes. "
            f"Late: {late}, Absent: {absent}. "
            f"To increase your rate, reduce absences first (each missed class lowers the ratio).",
            recommendations=[],
            mode="rule"
        )

    def _explain_enrollments(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        courses = [self._format_course_record(r) for r in active]

        return self._wrap(
            f"{name}, your enrollment count is {len(courses)} because these are the courses currently marked as enrolled "
            f"in your record: {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

    def _explain_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        overview = self._course_overview_text(stats)
        return self._wrap(
            f"{name}, here is how your course status is determined based on your record. {overview}",
            recommendations=[],
            mode="rule"
        )

    def _answer_multi_intents(
        self,
        stats: Dict[str, Any],
        sid: str,
        intents: List[str],
        is_explain: bool,
    ) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        ordered = [
            "GRADES",
            "ATTENDANCE",
            "COMPLETED_COURSES",
            "COURSES",
            "ENROLLMENTS",
        ]
        ordered_intents = [i for i in ordered if i in intents]

        parts = []
        for intent in ordered_intents:
            if is_explain:
                text = self._explain_section(stats, sid, intent)
            else:
                text = self._data_section(stats, sid, intent)
            if text:
                parts.append(text)

        if not parts:
            return self._wrap(
                "I could not find matching information for that request.",
                recommendations=[],
                mode="rule"
            )

        header = f"Here is a combined summary for you, {name}:"
        response = header + "\n" + "\n".join(parts) + f"\n{self._full_record_prompt()}"
        return self._wrap(response, recommendations=[], mode="rule")

    def _answer_multi_counts(self, stats: Dict[str, Any], sid: str, intents: List[str]) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        ordered = [
            "GRADES",
            "ATTENDANCE",
            "COMPLETED_COURSES",
            "COURSES",
            "ENROLLMENTS",
        ]
        ordered_intents = [i for i in ordered if i in intents]

        parts = []
        for intent in ordered_intents:
            text = self._count_section(stats, sid, intent)
            if text:
                parts.append(text)

        if not parts:
            return self._wrap(
                "I could not find matching counts for that request.",
                recommendations=[],
                mode="rule"
            )

        header = f"Here are the counts you requested, {name}:"
        response = header + "\n" + "\n".join(parts)
        return self._wrap(response, recommendations=[], mode="rule")

    def _count_section(self, stats: Dict[str, Any], sid: str, intent: str) -> str:
        if intent == "GRADES":
            grades = stats.get("grades") or stats.get("course_grades") or {}
            if not isinstance(grades, dict) or not grades:
                return "Grades count: 0"
            return f"Grades count: {len(grades)}"

        if intent == "ATTENDANCE":
            att = stats.get("attendance") or {}
            total = int(att.get("total_classes", att.get("total", 0)) or 0)
            attended = int(att.get("attended", att.get("present", 0)) or 0)
            late = int(att.get("late", 0) or 0)
            absent = int(att.get("absent", max(total - attended, 0)) or 0)
            return f"Attendance totals: {total} classes, {attended} attended, {late} late, {absent} absent"

        if intent == "COMPLETED_COURSES":
            records = self._get_course_records(stats)
            completed = self._filter_course_records(records, {"completed"})
            return f"Completed courses count: {len(completed)}"

        if intent in ["COURSES", "ENROLLMENTS"]:
            records = self._get_course_records(stats)
            active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
            return f"Active courses count: {len(active)}"

        return ""

    def _count_grades(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}
        count = len(grades) if isinstance(grades, dict) else 0
        return self._wrap(
            f"Hi {name}! You have {count} graded course(s) in your record.",
            recommendations=[],
            mode="rule"
        )

    def _count_attendance(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        att = stats.get("attendance") or {}
        total = int(att.get("total_classes", att.get("total", 0)) or 0)
        attended = int(att.get("attended", att.get("present", 0)) or 0)
        late = int(att.get("late", 0) or 0)
        absent = int(att.get("absent", max(total - attended, 0)) or 0)
        return self._wrap(
            f"Hi {name}! Attendance totals: {total} classes, {attended} attended, {late} late, {absent} absent.",
            recommendations=[],
            mode="rule"
        )

    def _count_enrollments(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        courses = [self._format_course_record(r) for r in active]
        if not courses:
            return self._wrap(
                f"Hi {name}! You are not currently enrolled in any courses.",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! You are currently enrolled in {len(courses)} course(s): {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

    def _count_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
        courses = [self._format_course_record(r) for r in active]
        if not courses:
            return self._wrap(
                f"Hi {name}! You do not have any active courses in progress.",
                recommendations=[],
                mode="rule"
            )
        return self._wrap(
            f"Hi {name}! You have {len(courses)} active course(s) in progress: {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

    def _count_completed_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        records = self._get_course_records(stats)
        completed = self._filter_course_records(records, {"completed"})
        return self._wrap(
            f"Hi {name}! You have completed {len(completed)} course(s).",
            recommendations=[],
            mode="rule"
        )

    def _data_section(self, stats: Dict[str, Any], sid: str, intent: str) -> str:
        if intent == "GRADES":
            grades = stats.get("grades") or stats.get("course_grades") or {}
            if not isinstance(grades, dict) or not grades:
                return "Grades: No grade data available"
            vals = []
            parts = []
            for k, v in grades.items():
                try:
                    g = float(v)
                    vals.append(g)
                    parts.append(f"{k}: {int(g) if g.is_integer() else g}")
                except Exception:
                    continue
            avg = sum(vals) / len(vals) if vals else 0.0
            return f"Grades: {', '.join(parts)}. Average: {avg:.1f}"

        if intent == "ATTENDANCE":
            att = stats.get("attendance") or {}
            total = int(att.get("total_classes", att.get("total", 0)) or 0)
            attended = int(att.get("attended", att.get("present", 0)) or 0)
            late = int(att.get("late", 0) or 0)
            absent = int(att.get("absent", max(total - attended, 0)) or 0)
            if total <= 0:
                return "Attendance: No attendance data available"
            rate = (attended / total) * 100
            return f"Attendance: {rate:.1f}% ({attended}/{total} attended), late: {late}, absent: {absent}"

        if intent == "COMPLETED_COURSES":
            records = self._get_course_records(stats)
            completed = self._filter_course_records(records, {"completed"})
            if not completed:
                return "Completed courses: None"
            courses = ", ".join([self._format_course_record(r) for r in completed])
            return f"Completed courses: {courses}"

        if intent == "ENROLLMENTS":
            records = self._get_course_records(stats)
            active = self._filter_course_records(records, {"enrolled", "in_progress", "under_progress"})
            if not active:
                return "Enrolled courses: None"
            courses = ", ".join([self._format_course_record(r) for r in active])
            return f"Enrolled courses: {courses}"

        if intent == "COURSES":
            return self._course_overview_text(stats)

        return ""

    def _explain_section(self, stats: Dict[str, Any], sid: str, intent: str) -> str:
        if intent == "GRADES":
            grades = stats.get("grades") or stats.get("course_grades") or {}
            if not isinstance(grades, dict) or not grades:
                return "Grades: No grade data available to explain"
            vals = []
            items = []
            for k, v in grades.items():
                try:
                    g = float(v)
                    vals.append(g)
                    items.append((k, g))
                except Exception:
                    pass
            if not vals:
                return "Grades: No numeric grades available to explain"
            avg = sum(vals) / len(vals)
            low_course, low_val = min(items, key=lambda x: x[1])
            high_course, high_val = max(items, key=lambda x: x[1])
            return (
                f"Grades: Average is {avg:.1f} based on your course scores. "
                f"Highest is {high_course}: {high_val:.0f}, lowest is {low_course}: {low_val:.0f}."
            )

        if intent == "ATTENDANCE":
            att = stats.get("attendance") or {}
            total = int(att.get("total_classes", att.get("total", 0)) or 0)
            attended = int(att.get("attended", att.get("present", 0)) or 0)
            late = int(att.get("late", 0) or 0)
            absent = int(att.get("absent", max(total - attended, 0)) or 0)
            if total <= 0:
                return "Attendance: No attendance data available to explain"
            rate = (attended / total) * 100
            return (
                f"Attendance: {rate:.1f}% because you attended {attended} of {total} classes. "
                f"Late: {late}, absent: {absent}."
            )

        if intent in ["COURSES", "ENROLLMENTS", "COMPLETED_COURSES"]:
            return f"Courses: {self._course_overview_text(stats)}"

        return ""

    def _course_overview_text(self, stats: Dict[str, Any]) -> str:
        records = self._get_course_records(stats)
        if not records:
            return "Course status overview: No course data available"

        groups = self._group_course_records(records)
        lines = ["Course status overview:"]
        order = [
            "completed",
            "enrolled",
            "in_progress",
            "under_progress",
            "failed",
            "withdrawn",
            "other",
        ]
        for status in order:
            items = groups.get(status, [])
            label = self._status_label(status)
            if items:
                lines.append(f"{label}: {', '.join(items)}")
            else:
                lines.append(f"{label}: None")
        return "\n".join(lines)

    def _get_course_records(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        records = stats.get("academic_record") or []
        if isinstance(records, list) and records:
            normalized = []
            for rec in records:
                normalized.append(self._normalize_course_record(rec))
            return normalized

        grades = stats.get("grades") or {}
        enrolled = stats.get("enrolled_courses") or []
        all_courses = stats.get("courses") or []
        if isinstance(enrolled, dict):
            enrolled = list(enrolled.keys())
        if isinstance(all_courses, dict):
            all_courses = list(all_courses.keys())
        completed = stats.get("completed_courses") or []
        if not completed and isinstance(grades, dict) and grades:
            completed = list(grades.keys())
        if enrolled and completed:
            enrolled = [c for c in enrolled if c not in completed]

        records = []
        for code in completed:
            records.append(self._normalize_course_record({
                "course_code": code,
                "course_name": code,
                "status": "completed",
                "grade": grades.get(code) if isinstance(grades, dict) else None,
            }))
        for code in enrolled:
            records.append(self._normalize_course_record({
                "course_code": code,
                "course_name": code,
                "status": "enrolled",
                "grade": None,
            }))

        if all_courses:
            for code in all_courses:
                if code in completed or code in enrolled:
                    continue
                records.append(self._normalize_course_record({
                    "course_code": code,
                    "course_name": code,
                    "status": "in_progress",
                    "grade": None,
                }))
        return records

    def _normalize_course_record(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        code = str(rec.get("course_code") or rec.get("course") or "").strip()
        name = str(rec.get("course_name") or code).strip() or code
        if name == code:
            catalog_name = self._resolve_course_name_from_catalog(code)
            if catalog_name:
                name = catalog_name
        status = self._normalize_status(rec.get("status"))
        grade = rec.get("grade")
        if not status:
            status = "completed" if grade is not None else "enrolled"
        return {
            "course_code": code,
            "course_name": name,
            "status": status,
            "grade": grade,
        }

    def _resolve_course_name_from_catalog(self, code: str) -> Optional[str]:
        if not code:
            return None
        if not hasattr(self.data_loader, "find_course_in_catalog"):
            return None
        try:
            course = self.data_loader.find_course_in_catalog(code)
        except Exception:
            return None
        if not course:
            return None
        return str(course.get("name") or "").strip() or None

    def _normalize_status(self, status: Any) -> str:
        if not status:
            return ""
        s = str(status).strip().lower().replace(" ", "_")
        if s in ["inprogress", "in_progress"]:
            return "in_progress"
        if s in ["underprogress", "under_progress"]:
            return "under_progress"
        return s

    def _status_label(self, status: str) -> str:
        labels = {
            "completed": "Completed",
            "enrolled": "Enrolled",
            "in_progress": "In progress",
            "under_progress": "Under progress",
            "failed": "Failed",
            "withdrawn": "Withdrawn",
            "other": "Other",
        }
        return labels.get(status, status.title())

    def _format_date_only(self, value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date().isoformat()
        if hasattr(value, "isoformat"):
            iso = value.isoformat()
            return iso.split("T")[0] if "T" in iso else iso
        text = str(value).strip()
        if not text:
            return None
        if "T" in text:
            return text.split("T")[0]
        if " " in text:
            return text.split(" ")[0]
        return text

    def _group_course_records(self, records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        for rec in records:
            status = rec.get("status") or "other"
            if status not in [
                "completed",
                "enrolled",
                "in_progress",
                "under_progress",
                "failed",
                "withdrawn",
            ]:
                status = "other"
            groups.setdefault(status, []).append(self._format_course_record(rec))
        return groups

    def _format_course_record(self, rec: Dict[str, Any]) -> str:
        code = rec.get("course_code") or ""
        name = rec.get("course_name") or code
        status = self._status_label(rec.get("status") or "")
        grade = rec.get("grade")
        if grade is not None:
            return f"{code} - {name} (Status: {status}, Grade: {grade})"
        return f"{code} - {name} (Status: {status})"

    def _filter_course_records(self, records: List[Dict[str, Any]], statuses: Set[str]) -> List[Dict[str, Any]]:
        filtered = []
        for rec in records:
            status = rec.get("status") or ""
            if status in statuses:
                filtered.append(rec)
        return filtered

    # ---------- Helpers ----------
    def _normalize_student_id(self, student_id: Union[str, int, None]) -> Optional[str]:
        if student_id is None:
            return None
        s = str(student_id).strip().upper()
        if not s:
            return None
        # allow "003" => "S003" if your dataset uses S### (optional)
        if s.isdigit():
            s = f"S{int(s):03d}"
        return s

    def _safe_student_stats(self, sid: str) -> Optional[Dict[str, Any]]:
        try:
            # Your code already uses calculate_student_stats somewhere
            if hasattr(self.data_loader, "calculate_student_stats"):
                return self.data_loader.calculate_student_stats(sid)
        except Exception:
            pass

        # fallback: get_student_by_id
        try:
            if hasattr(self.data_loader, "get_student_by_id"):
                student = self.data_loader.get_student_by_id(sid)
                if not student:
                    return None
                grades = student.get("grades", {})
                enrolled = student.get("enrolled_courses") or student.get("courses", [])
                completed = student.get("completed_courses", [])
                if not completed and grades:
                    completed = list(grades.keys())
                if enrolled and completed:
                    enrolled = [c for c in enrolled if c not in completed]

                academic_record = student.get("academic_record")
                if not academic_record:
                    academic_record = []
                    course_codes = list(dict.fromkeys(completed + enrolled))
                    for code in course_codes:
                        grade = grades.get(code)
                        status = "completed" if grade is not None or code in completed else "enrolled"
                        academic_record.append({
                            "course_code": code,
                            "course_name": code,
                            "term": "Fall 2025",
                            "status": status,
                            "grade": grade,
                        })

                attendance = student.get("attendance", {})
                if "summary" not in attendance:
                    total = attendance.get("total_classes", 0)
                    attended = attendance.get("attended", 0)
                    late = attendance.get("late", 0)
                    absent = attendance.get("absent", 0)
                    present = attendance.get("present")
                    if present is None:
                        present = max(attended - late, 0)
                    if total == 0 and (present or late or absent):
                        total = present + late + absent
                    if attended == 0 and (present or late):
                        attended = present + late
                    attendance.update({
                        "total_classes": total,
                        "attended": attended,
                        "present": present,
                        "summary": {
                            "present": present,
                            "absent": absent,
                            "late": late,
                        },
                    })
                # minimal stats shape
                return {
                    "student_id": sid,
                    "name": student.get("name", "Student"),
                    "join_date": student.get("join_date") or student.get("created_at"),
                    "grades": grades,
                    "attendance": attendance,
                    "enrolled_courses": enrolled,
                    "completed_courses": completed,
                    "academic_record": academic_record,
                }
        except Exception:
            return None
        return None

    def _wrap(self, text: str, recommendations: List[str], mode: str = "rule") -> Dict[str, Any]:
        return {
            "response": text,
            "recommendations": recommendations or [],
            "mode": mode
        }

    def _calculate_gpa(self, stats: Dict[str, Any]) -> Optional[float]:
        # If GPA is provided, prefer it
        gpa = stats.get("gpa")
        if isinstance(gpa, (int, float)):
            return float(gpa)

        grades = stats.get("grades") or stats.get("course_grades") or {}
        if not isinstance(grades, dict) or not grades:
            return None

        vals = []
        for v in grades.values():
            try:
                vals.append(float(v))
            except Exception:
                continue
        if not vals:
            return None

        avg = sum(vals) / len(vals)
        # Simple 0-100 to 0-4.0 mapping
        gpa_est = (avg / 100.0) * 4.0
        return max(0.0, min(4.0, gpa_est))

    def _get_daypart(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        if 12 <= hour < 18:
            return "afternoon"
        return "evening"

    def _full_record_prompt(self) -> str:
        return "If you'd like your full academic record, type 'yes'."

    def _greeting_response(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        daypart = self._get_daypart()
        greetings = [
            f"Good {daypart}, {name}.",
            f"Good {daypart}, {name}. Welcome back.",
            f"Hello {name}, good {daypart}.",
            f"Hi {name}! Good {daypart}.",
        ]
        openers = [
            "I'm here to help with your academic record. What would you like to review?",
            "I can help with courses, grades, and attendance. What would you like to check?",
            "How can I support your studies today?",
        ]
        greeting = self._rng.choice(greetings)
        opener = self._rng.choice(openers)
        self._pending_confirm_by_student[sid] = "ACADEMIC_RECORD"
        return self._wrap(
            f"{greeting} {opener}",
            recommendations=[],
            mode="rule"
        )

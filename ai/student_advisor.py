# ai/student_advisor.py
from __future__ import annotations
from typing import Any, Dict, Optional, List, Union

try:
    # Your project has this
    from ai.student_data_loader import StudentDataLoader
except Exception:
    StudentDataLoader = None  # type: ignore


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
        self.data_loader = StudentDataLoader()

        # Remember previous intent per student (so "Why?" can refer to last answer)
        self._last_intent_by_student: Dict[str, str] = {}

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

        # Detect intent & resolve follow-ups
        detected = self._detect_intent(msg)
        intent = self._resolve_followup_intent(detected, msg, sid)

        # If we found a real intent, remember it
        if intent != "UNKNOWN":
            self._last_intent_by_student[sid] = intent

        # Answer data-first intents
        if intent == "GRADES":
            return self._answer_grades(stats, sid)

        if intent == "ATTENDANCE":
            return self._answer_attendance(stats, sid)

        if intent == "ENROLLMENTS":
            return self._answer_enrollments(stats, sid)

        if intent == "COURSES":
            return self._answer_courses(stats, sid)

        if intent == "WHY_GRADES":
            return self._explain_grades(stats, sid)

        if intent == "WHY_ATTENDANCE":
            return self._explain_attendance(stats, sid)

        if intent == "WHY_ENROLLMENTS":
            return self._explain_enrollments(stats, sid)

        # Other questions (fallback – NOT greeting spam)
        return self._wrap(
            "I can help with grades, attendance, enrollments, and courses. "
            "Try: 'What is my grades?', 'My attendance', 'Enrollments', or ask 'Why?' after those.",
            recommendations=[],
            mode="rule"
        )

    # ---------- Intent ----------
    def _detect_intent(self, message: str) -> str:
        m = (message or "").lower()

        grade_words = ["grade", "grades", "gpa", "mark", "marks", "score", "scores", "result", "results"]
        att_words = ["attendance", "absent", "present", "late", "missed"]
        enr_words = ["enroll", "enrol", "enrollment", "enrolment", "registered", "registration", "how many courses"]
        course_words = ["courses", "course", "subjects", "subject", "units", "unit", "classes", "class"]

        if any(w in m for w in grade_words):
            # “why my grades …” also contains grades keyword -> handled by follow-up resolver
            return "GRADES"
        if any(w in m for w in att_words):
            return "ATTENDANCE"
        if any(w in m for w in enr_words):
            return "ENROLLMENTS"
        if any(w in m for w in course_words):
            return "COURSES"

        if m.strip() in ["why", "why?", "how", "how?"] or m.strip().startswith("why "):
            return "WHY"

        return "UNKNOWN"

    def _resolve_followup_intent(self, detected: str, message: str, sid: str) -> str:
        m = (message or "").lower().strip()

        last = self._last_intent_by_student.get(sid, "UNKNOWN")

        # If the user asks "why ..." and also mentions grades/attendance etc
        if "why" in m:
            if any(w in m for w in ["grade", "grades", "gpa", "mark", "score", "result"]):
                return "WHY_GRADES"
            if any(w in m for w in ["attendance", "absent", "late", "missed"]):
                return "WHY_ATTENDANCE"
            if any(w in m for w in ["enroll", "enrol", "enrollment", "registered", "registration"]):
                return "WHY_ENROLLMENTS"

        # Pure follow-up: "Why?" => use last intent
        if detected in ["WHY", "UNKNOWN"] and (m in ["why", "why?", "how", "how?"]):
            if last == "GRADES":
                return "WHY_GRADES"
            if last == "ATTENDANCE":
                return "WHY_ATTENDANCE"
            if last == "ENROLLMENTS":
                return "WHY_ENROLLMENTS"

        # If detected a normal intent, keep it
        return detected

    # ---------- Answers ----------
    def _answer_grades(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        grades = stats.get("grades") or stats.get("course_grades") or {}

        if not isinstance(grades, dict) or not grades:
            return self._wrap(f"Hi {name}! I can't find grades data for you yet.", [], mode="rule")

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
            f"Welcome back, {name}! Here are your grades: {', '.join(parts)}. Your average is {avg:.1f}.",
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
            return self._wrap(f"Hi {name}! I can't find attendance data for you yet.", [], mode="rule")

        rate = (attended / total) * 100
        return self._wrap(
            f"Welcome back, {name}! Your attendance rate is {rate:.1f}% ({attended}/{total} attended). "
            f"Late: {late}, Absent: {absent}.",
            recommendations=[],
            mode="rule"
        )

    def _answer_enrollments(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        name = stats.get("name", "Student")
        courses = stats.get("enrolled_courses") or stats.get("courses") or []
        if isinstance(courses, dict):
            courses = list(courses.keys())

        courses = [str(c) for c in courses]
        return self._wrap(
            f"Hi {name}! Your current enrollment count is {len(courses)}. Enrolled courses: {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

    def _answer_courses(self, stats: Dict[str, Any], sid: str) -> Dict[str, Any]:
        # Same as enrollments, but wording
        name = stats.get("name", "Student")
        courses = stats.get("enrolled_courses") or stats.get("courses") or []
        if isinstance(courses, dict):
            courses = list(courses.keys())
        courses = [str(c) for c in courses]
        return self._wrap(
            f"Hi {name}! You are currently taking: {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

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

        return self._wrap(
            f"{name}, your average is {avg:.1f} because it’s the mean of your course scores. "
            f"Your highest is {high_course}: {high_val:.0f} and your lowest is {low_course}: {low_val:.0f}. "
            f"Courses below your average: {below_txt}. "
            f"If you lift the lowest subject(s), your average will rise quickly.",
            recommendations=[],
            mode="rule"
        )

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
        courses = stats.get("enrolled_courses") or stats.get("courses") or []
        if isinstance(courses, dict):
            courses = list(courses.keys())
        courses = [str(c) for c in courses]

        return self._wrap(
            f"{name}, your enrollment count is {len(courses)} because these are the courses currently marked as enrolled "
            f"in your record: {', '.join(courses)}.",
            recommendations=[],
            mode="rule"
        )

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
                # minimal stats shape
                return {
                    "student_id": sid,
                    "name": student.get("name", "Student"),
                    "grades": student.get("grades", {}),
                    "attendance": student.get("attendance", {}),
                    "enrolled_courses": student.get("enrolled_courses", student.get("courses", []))
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

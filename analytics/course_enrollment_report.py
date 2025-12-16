import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# -----------------------------
# DB connection (same as before)
# Covers: reusable engine for Pandas SQL reads
# -----------------------------
engine = create_engine("mysql+pymysql://root:@localhost/student_portal")


# -----------------------------
# Load a JOIN report (enrollments + courses)
# Covers: SQL JOIN (core skill for analytics + real reporting)
# -----------------------------
query = """
SELECT
    e.id AS enrollment_id,
    e.student_id,
    e.course_id,
    e.enrolled_at,
    c.course_code,
    c.name AS course_name,
    c.department
FROM enrollments e
JOIN courses c ON c.id = e.course_id
ORDER BY e.enrolled_at DESC
"""

df = pd.read_sql(query, engine)

print("\n📌 Joined Enrollment Report Preview:")
print(df.head())


# -----------------------------
# Stats: total enrollments + enrollments by course name
# Covers: groupby + sort (analytics summaries)
# -----------------------------
print("\n📊 Report Statistics")
print(f"Total enrollments: {len(df)}")
print(f"Unique students: {df['student_id'].nunique()}")
print(f"Unique courses: {df['course_id'].nunique()}")

enrollments_by_course = (
    df.groupby("course_name")
      .size()
      .sort_values(ascending=False)
)

print("\n📚 Enrollments by course (name):")
print(enrollments_by_course)


# -----------------------------
# Chart: Top courses by enrollments
# Covers: visualization for dashboard-ready charts
# -----------------------------
plt.figure(figsize=(10, 4))
enrollments_by_course.plot(kind="bar")
plt.title("Enrollments by Course (Joined Report)")
plt.xlabel("Course Name")
plt.ylabel("Enrollments")
plt.tight_layout()
plt.show()


# -----------------------------
# Optional: Save report for React dashboard later
# Covers: file export (CSV) for API/dashboard usage
# -----------------------------
df.to_csv("analytics/enrollment_report.csv", index=False)
print("\n✅ Saved: analytics/enrollment_report.csv")

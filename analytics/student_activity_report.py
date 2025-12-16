import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:@localhost/student_portal")

query = """
SELECT
    s.student_id,
    s.name,
    s.email,
    s.course AS primary_course,
    COUNT(e.id) AS total_enrollments
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.id
GROUP BY s.student_id, s.name, s.email, s.course
ORDER BY total_enrollments DESC, s.name ASC
"""

df = pd.read_sql(query, engine)

print("\n👤 Student Activity Report Preview:")
print(df.head(10))

print("\n📊 Student Activity Stats")
print(f"Total students: {len(df)}")
print(f"Students with 0 enrollments: {(df['total_enrollments'] == 0).sum()}")
print(f"Max enrollments by a student: {df['total_enrollments'].max()}")

# Chart: top 10 students
top10 = df.head(10).copy()

plt.figure(figsize=(10, 4))
plt.bar(top10["name"], top10["total_enrollments"])
plt.title("Top 10 Students by Enrollments")
plt.xlabel("Student Name")
plt.ylabel("Enrollments")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.show()

# Save for React dashboard later
df.to_csv("analytics/student_activity_report.csv", index=False)
print("\n✅ Saved: analytics/student_activity_report.csv")

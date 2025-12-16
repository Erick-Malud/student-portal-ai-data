import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# -----------------------------
# DB connection
# -----------------------------
# Covers: DB connection string + reusable SQLAlchemy engine (best practice)
engine = create_engine("mysql+pymysql://root:@localhost/student_portal")


# -----------------------------
# Load enrollments into Pandas
# -----------------------------
# Covers: SQL -> Pandas DataFrame (this is the core of analytics work)
df_enrollments = pd.read_sql("SELECT * FROM enrollments", engine)

# Optional: show preview so you know data loaded correctly
print("\n📌 Enrollment Data Preview:")
print(df_enrollments.head())


# -----------------------------
# Basic enrollment statistics
# -----------------------------
# Covers: DataFrame size + unique counts
total_enrollments = len(df_enrollments)

# Change column name here if your table uses different naming
# Common choices: student_id / course_code / course_id
unique_students = df_enrollments["student_id"].nunique()
unique_courses = df_enrollments["course_code"].nunique() if "course_code" in df_enrollments.columns else None

print("\n📊 Enrollment Statistics")
print(f"Total enrollments: {total_enrollments}")
print(f"Unique students enrolled: {unique_students}")

if unique_courses is not None:
    print(f"Unique courses enrolled: {unique_courses}")


# -----------------------------
# Enrollments by course
# -----------------------------
# Covers: groupby + sorting (top courses)
course_col = "course_code" if "course_code" in df_enrollments.columns else "course_id"
enrollments_by_course = df_enrollments.groupby(course_col).size().sort_values(ascending=False)

print("\n📚 Enrollments by course:")
print(enrollments_by_course)


# -----------------------------
# Chart 1: Bar chart (top courses)
# -----------------------------
# Covers: visualization of grouped data
plt.figure(figsize=(9, 4))
enrollments_by_course.plot(kind="bar")
plt.title("Enrollments by Course")
plt.xlabel("Course")
plt.ylabel("Number of Enrollments")
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 2: Pie chart (share of enrollments)
# -----------------------------
# Covers: distribution visualization (very common in reporting)
plt.figure(figsize=(6, 6))
enrollments_by_course.plot(kind="pie", autopct="%1.1f%%")
plt.title("Enrollment Share by Course")
plt.ylabel("")  # removes default y label
plt.tight_layout()
plt.show()

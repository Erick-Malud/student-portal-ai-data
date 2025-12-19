"""
Month 3 - Step 1: Descriptive Statistics

What this script covers:
- Loading data from MySQL into Pandas
- Descriptive statistics (mean, median, std, percentiles)
- Understanding distributions
- First EDA-style outputs
"""

import pandas as pd
from sqlalchemy import create_engine


# -----------------------------
# Database connection
# -----------------------------
engine = create_engine("mysql+pymysql://root:@localhost/student_portal")


# -----------------------------
# Load tables
# -----------------------------
students = pd.read_sql("SELECT * FROM students", engine)
enrollments = pd.read_sql("SELECT * FROM enrollments", engine)


# -----------------------------
# Basic dataset overview
# -----------------------------
print("\n📌 DATA OVERVIEW")
print(f"Total students: {len(students)}")
print(f"Total enrollments: {len(enrollments)}")


# -----------------------------
# Descriptive statistics: Age
# -----------------------------
print("\n📊 STUDENT AGE STATISTICS")
print(students["age"].describe())

print("\n📈 Additional age metrics")
print(f"Mean age: {students['age'].mean():.2f}")
print(f"Median age: {students['age'].median():.2f}")
print(f"Standard deviation: {students['age'].std():.2f}")


# -----------------------------
# Enrollment count per student
# -----------------------------
enrollments_per_student = (
    enrollments.groupby("student_id")
    .size()
    .reset_index(name="total_enrollments")
)

print("\n📊 ENROLLMENTS PER STUDENT (preview)")
print(enrollments_per_student.head())


# -----------------------------
# Merge with student info
# -----------------------------
student_activity = students.merge(
    enrollments_per_student,
    left_on="id",
    right_on="student_id",
    how="left"
)

student_activity["total_enrollments"] = student_activity["total_enrollments"].fillna(0)

print("\n📊 STUDENT ACTIVITY SUMMARY")
print(student_activity[["name", "age", "total_enrollments"]].head())


# -----------------------------
# Descriptive stats: enrollments
# -----------------------------
print("\n📈 ENROLLMENT STATISTICS PER STUDENT")
print(student_activity["total_enrollments"].describe())

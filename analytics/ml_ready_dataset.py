"""
Month 3 - Step 5: ML-Ready Dataset Preparation

What this script covers:
- Feature selection
- Handling missing values
- Encoding categorical variables
- Creating a clean ML-ready CSV
"""

import pandas as pd
from sqlalchemy import create_engine


# -----------------------------
# DB connection
# -----------------------------
engine = create_engine("mysql+pymysql://root:@localhost/student_portal")


# -----------------------------
# Load data
# -----------------------------
students = pd.read_sql("SELECT * FROM students", engine)
enrollments = pd.read_sql("SELECT * FROM enrollments", engine)


# -----------------------------
# Feature engineering
# -----------------------------
# Count enrollments per student
enrollments_per_student = (
    enrollments.groupby("student_id")
    .size()
    .reset_index(name="total_enrollments")
)

data = students.merge(
    enrollments_per_student,
    left_on="id",
    right_on="student_id",
    how="left"
)

data["total_enrollments"] = data["total_enrollments"].fillna(0)

# Rename for clarity
data.rename(columns={"course": "primary_course"}, inplace=True)


# -----------------------------
# Select ML features
# -----------------------------
ml_data = data[[
    "age",
    "primary_course",
    "total_enrollments"
]].copy()


# -----------------------------
# Encode categorical variables
# -----------------------------
# One-Hot Encoding for primary_course
ml_data = pd.get_dummies(
    ml_data,
    columns=["primary_course"],
    drop_first=True
)


# -----------------------------
# Final checks
# -----------------------------
print("\n📊 ML Dataset Preview:")
print(ml_data.head())

print("\n📊 Dataset Info:")
print(ml_data.info())


# -----------------------------
# Save ML-ready dataset
# -----------------------------
ml_data.to_csv("analytics/ml_ready_dataset.csv", index=False)
print("\n✅ ML-ready dataset saved: analytics/ml_ready_dataset.csv")

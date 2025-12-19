"""
Month 3 - Step 2: Distributions & Outliers

What this script covers:
- Histograms (distribution shape)
- Box plots (outlier detection)
- Understanding skew and spread
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
# Enrollments per student
# -----------------------------
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


# -----------------------------
# Distribution: Student age
# -----------------------------
plt.figure(figsize=(6, 4))
sns.histplot(data["age"], bins=10, kde=True)
plt.title("Distribution of Student Age")
plt.xlabel("Age")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()


# -----------------------------
# Box plot: Student age (outliers)
# -----------------------------
plt.figure(figsize=(6, 2))
sns.boxplot(x=data["age"])
plt.title("Age Outliers (Box Plot)")
plt.tight_layout()
plt.show()


# -----------------------------
# Distribution: Enrollments per student
# -----------------------------
plt.figure(figsize=(6, 4))
sns.histplot(data["total_enrollments"], bins=10, kde=True)
plt.title("Distribution of Enrollments per Student")
plt.xlabel("Enrollments")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()


# -----------------------------
# Box plot: Enrollment outliers
# -----------------------------
plt.figure(figsize=(6, 2))
sns.boxplot(x=data["total_enrollments"])
plt.title("Enrollment Outliers (Box Plot)")
plt.tight_layout()
plt.show()


# -----------------------------
# Identify outliers numerically (IQR method)
# -----------------------------
Q1 = data["total_enrollments"].quantile(0.25)
Q3 = data["total_enrollments"].quantile(0.75)
IQR = Q3 - Q1

outliers = data[
    (data["total_enrollments"] < Q1 - 1.5 * IQR) |
    (data["total_enrollments"] > Q3 + 1.5 * IQR)
]

print("\n🚨 Enrollment Outliers (IQR method):")
print(outliers[["name", "age", "total_enrollments"]])

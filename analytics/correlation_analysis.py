"""
Month 3 - Step 3: Correlation Analysis

What this script covers:
- Correlation coefficients (Pearson)
- Correlation matrix
- Heatmap visualization
- Interpreting relationships between variables
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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
# Prepare analysis dataset
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
# Correlation calculation
# -----------------------------
corr_value = data["age"].corr(data["total_enrollments"])

print("\n📊 Correlation Result")
print(f"Correlation between age and total enrollments: {corr_value:.3f}")


# -----------------------------
# Correlation matrix
# -----------------------------
corr_matrix = data[["age", "total_enrollments"]].corr()

print("\n📊 Correlation Matrix")
print(corr_matrix)


# -----------------------------
# Heatmap visualization
# -----------------------------
plt.figure(figsize=(4, 3))
sns.heatmap(
    corr_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.show()

"""
Month 3 - Step 4: Exploratory Data Analysis (EDA) Report

What this script covers:
- Translating statistics into insights
- Summarising distributions
- Interpreting correlations
- Producing a mini text-based EDA report
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
# Prepare dataset
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
# Core statistics
# -----------------------------
avg_age = data["age"].mean()
median_age = data["age"].median()
std_age = data["age"].std()

avg_enrollments = data["total_enrollments"].mean()
max_enrollments = data["total_enrollments"].max()

corr_age_enroll = data["age"].corr(data["total_enrollments"])


# -----------------------------
# Generate EDA insights
# -----------------------------
report = []

report.append("📊 EXPLORATORY DATA ANALYSIS REPORT\n")
report.append(f"Total students analysed: {len(data)}\n")

report.append("1️⃣ Student Age Distribution")
report.append(f"- Average age: {avg_age:.2f}")
report.append(f"- Median age: {median_age:.2f}")
report.append(f"- Standard deviation: {std_age:.2f}")

if avg_age > median_age:
    report.append("- Age distribution is slightly right-skewed.\n")
else:
    report.append("- Age distribution is fairly balanced.\n")

report.append("2️⃣ Enrollment Behaviour")
report.append(f"- Average enrollments per student: {avg_enrollments:.2f}")
report.append(f"- Maximum enrollments by a single student: {max_enrollments}")

if max_enrollments > avg_enrollments * 3:
    report.append("- A small number of students are highly active (possible power users).\n")
else:
    report.append("- Enrollment activity is relatively evenly distributed.\n")

report.append("3️⃣ Relationship Between Age and Enrollment")
report.append(f"- Correlation coefficient: {corr_age_enroll:.3f}")

if abs(corr_age_enroll) < 0.2:
    report.append("- There is little to no linear relationship between age and enrollments.\n")
elif corr_age_enroll > 0:
    report.append("- Older students tend to enroll slightly more.\n")
else:
    report.append("- Younger students tend to enroll slightly more.\n")

report.append("4️⃣ EDA Conclusion")
report.append("- Age alone is not a strong predictor of enrollment activity.")
report.append("- Enrollment behaviour varies more by individual than by age.")
report.append("- Dataset is suitable for feature engineering and machine learning.\n")


# -----------------------------
# Output report
# -----------------------------
print("\n".join(report))

with open("analytics/eda_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print("\n✅ EDA report saved to analytics/eda_report.txt")

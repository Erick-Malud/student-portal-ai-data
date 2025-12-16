import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# -----------------------------
# DB connection (SQLAlchemy)
# -----------------------------
# Covers: DB connection string + engine creation (reusable)
engine = create_engine("mysql+pymysql://root:@localhost/student_portal")


# -----------------------------
# Load data into Pandas
# -----------------------------
# Covers: Pandas DataFrame + SQL query to fetch table data
df_students = pd.read_sql("SELECT * FROM students", engine)


# -----------------------------
# Basic statistics (Students)
# -----------------------------
# Covers: aggregation functions, descriptive stats
total_students = len(df_students)
avg_age = df_students["age"].mean()
min_age = df_students["age"].min()
max_age = df_students["age"].max()

print("\n📊 Student Statistics")
print(f"Total students: {total_students}")
print(f"Average age: {avg_age:.2f}")
print(f"Youngest age: {min_age}")
print(f"Oldest age: {max_age}")


# -----------------------------
# Grouping (students per course)
# -----------------------------
# Covers: groupby + sorting (very important for analytics)
students_by_course = df_students.groupby("course").size().sort_values(ascending=False)

print("\n📚 Students by course:")
print(students_by_course)


# -----------------------------
# Visualization (Bar Chart)
# -----------------------------
# Covers: first real chart from DB → DataFrame → chart
plt.figure(figsize=(8, 4))
students_by_course.plot(kind="bar")
plt.title("Students by Course")
plt.xlabel("Course")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()

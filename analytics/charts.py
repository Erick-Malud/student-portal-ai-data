# analytics/charts.py
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("analytics/outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def save_show(fig_name: str):
    path = OUTPUT_DIR / fig_name
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    print(f"✅ Saved: {path}")
    plt.show()

def chart_enrollments_by_course():
    df = pd.read_csv("analytics/enrollment_report.csv")
    counts = df["course_name"].value_counts().sort_values(ascending=False)

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Enrollments by Course")
    plt.xlabel("Course")
    plt.ylabel("Enrollments")
    plt.xticks(rotation=30, ha="right")
    save_show("01_enrollments_by_course.png")

def chart_students_by_primary_course():
    df = pd.read_csv("analytics/student_activity_report.csv")
    counts = df["primary_course"].fillna("None").value_counts().sort_values(ascending=False)

    plt.figure()
    counts.plot(kind="bar")
    plt.title("Students by Primary Course")
    plt.xlabel("Primary Course")
    plt.ylabel("Students")
    plt.xticks(rotation=30, ha="right")
    save_show("02_students_by_primary_course.png")

def chart_students_with_zero_enrollments():
    df = pd.read_csv("analytics/student_activity_report.csv")
    zero = (df["total_enrollments"] == 0).sum()
    nonzero = (df["total_enrollments"] > 0).sum()

    plt.figure()
    plt.bar(["0 enrollments", "1+ enrollments"], [zero, nonzero])
    plt.title("Students with vs without Enrollments")
    plt.xlabel("Group")
    plt.ylabel("Students")
    save_show("03_students_zero_vs_nonzero.png")

if __name__ == "__main__":
    chart_enrollments_by_course()
    chart_students_by_primary_course()
    chart_students_with_zero_enrollments()

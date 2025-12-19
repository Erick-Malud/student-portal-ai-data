# analytics/ml/model_evaluation.py

from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def project_paths():
    this_file = Path(__file__).resolve()
    analytics_dir = this_file.parents[1]
    outputs_dir = analytics_dir / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    data_csv = analytics_dir / "student_activity_report.csv"
    return outputs_dir, data_csv


def load_data(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing file: {csv_path}\n"
            f"Run first:\n"
            f"  python analytics/student_activity_report.py"
        )
    return pd.read_csv(csv_path)


def prepare_features(df: pd.DataFrame):
    df["active"] = (df["total_enrollments"] > 0).astype(int)

    X = pd.get_dummies(
        df[["primary_course"]],
        columns=["primary_course"],
        drop_first=False
    )
    y = df["active"]

    return X, y


def main():
    print("🧪 Month 4 — Step 4: Model Evaluation & Cross-Validation")

    outputs_dir, data_csv = project_paths()
    df = load_data(data_csv)

    X, y = prepare_features(df)

    model = LogisticRegression(max_iter=1000)

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")

    report = (
        "Model Evaluation Report\n"
        "------------------------\n"
        f"Cross-validation accuracy scores: {cv_scores}\n"
        f"Mean accuracy: {cv_scores.mean():.4f}\n"
        f"Std deviation: {cv_scores.std():.4f}\n"
    )

    report_path = outputs_dir / "ml_model_evaluation.txt"
    report_path.write_text(report, encoding="utf-8")

    print("\n📊 Cross-Validation Results")
    print(report)
    print(f"✅ Saved evaluation report: {report_path}")

    print("\n🎯 Interpretation:")
    print("- Small std deviation → stable model")
    print("- Large std deviation → possible overfitting")

    print("\n🎉 Step 4 completed successfully!")


if __name__ == "__main__":
    main()

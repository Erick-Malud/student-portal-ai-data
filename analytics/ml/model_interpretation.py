# analytics/ml/model_interpretation.py

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


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
    print("🔍 Month 4 — Step 5: Model Interpretation")

    outputs_dir, data_csv = project_paths()
    df = load_data(data_csv)

    X, y = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Train interpretable model
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Feature importance
    importances = model.feature_importances_
    feature_names = X.columns

    importance_df = (
        pd.DataFrame({
            "feature": feature_names,
            "importance": importances
        })
        .sort_values(by="importance", ascending=False)
    )

    print("\n📊 Feature Importance (Top)")
    print(importance_df.head(10))

    # Save table
    table_path = outputs_dir / "ml_feature_importance_table.csv"
    importance_df.to_csv(table_path, index=False)

    # Plot
    top_n = 10
    top_features = importance_df.head(top_n)

    plt.figure()
    plt.barh(
        top_features["feature"][::-1],
        top_features["importance"][::-1]
    )
    plt.title("Top Feature Importances (Classification Model)")
    plt.xlabel("Importance")
    plt.tight_layout()

    plot_path = outputs_dir / "ml_feature_importance_classification.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()

    print(f"\n✅ Saved importance table: {table_path}")
    print(f"✅ Saved importance chart: {plot_path}")

    print("\n🎉 Month 4 — Step 5 completed successfully!")


if __name__ == "__main__":
    main()

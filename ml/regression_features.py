# analytics/ml/regression_features.py
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def project_paths():
    """
    Finds paths safely no matter where you run the script from.
    This avoids the common 'analytics/analytics/...' mistake.
    """
    this_file = Path(__file__).resolve()  # .../student-portal/analytics/ml/regression_features.py
    analytics_dir = this_file.parents[1]  # .../student-portal/analytics
    outputs_dir = analytics_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # expected from Month 2 step: analytics/student_activity_report.csv
    data_csv = analytics_dir / "student_activity_report.csv"
    return analytics_dir, outputs_dir, data_csv


def load_data(data_csv: Path) -> pd.DataFrame:
    if not data_csv.exists():
        raise FileNotFoundError(
            f"Missing file: {data_csv}\n"
            f"Generate it first by running:\n"
            f"  python analytics/student_activity_report.py"
        )
    df = pd.read_csv(data_csv)
    return df


def build_features(df: pd.DataFrame):
    """
    Target (y): total_enrollments
    Features (X):
      - total_enrollments is NOT included in X (to avoid leakage)
      - has_enrollments (0/1)
      - one-hot encoded primary_course
    """

    required = {"primary_course", "total_enrollments"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}. Found: {list(df.columns)}")

    # Make sure total_enrollments is numeric
    df["total_enrollments"] = pd.to_numeric(df["total_enrollments"], errors="coerce").fillna(0).astype(int)

    # Feature: has_enrollments
    df["has_enrollments"] = (df["total_enrollments"] > 0).astype(int)

    # One-hot encode primary_course
    X = pd.get_dummies(df[["primary_course", "has_enrollments"]], columns=["primary_course"], drop_first=False)

    # Target
    y = df["total_enrollments"].values

    return X, y


def evaluate_model(name: str, model, X_train, X_test, y_train, y_test, outputs_dir: Path):
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)

    metrics_text = (
        f"Model: {name}\n"
        f"MAE : {mae:.4f}\n"
        f"RMSE: {rmse:.4f}\n"
        f"R^2 : {r2:.4f}\n"
        f"Test size: {len(y_test)}\n"
    )

    out_file = outputs_dir / f"ml_{name.lower().replace(' ', '_')}_metrics.txt"
    out_file.write_text(metrics_text, encoding="utf-8")

    print("\n📌", metrics_text)
    print(f"✅ Saved metrics: {out_file}")

    return preds, (mae, rmse, r2)


def save_feature_importance(rf_model, feature_names, outputs_dir: Path, top_n: int = 15):
    importances = rf_model.feature_importances_
    idx = np.argsort(importances)[::-1][:top_n]

    top_features = [feature_names[i] for i in idx]
    top_values = importances[idx]

    plt.figure()
    plt.barh(top_features[::-1], top_values[::-1])
    plt.title("Top Feature Importances (Random Forest)")
    plt.xlabel("Importance")
    plt.tight_layout()

    out_path = outputs_dir / "ml_feature_importance.png"
    plt.savefig(out_path, dpi=200)
    plt.close()

    print(f"✅ Saved chart: {out_path}")


def main():
    print("📦 Step 2: Feature engineering + model comparison")

    analytics_dir, outputs_dir, data_csv = project_paths()
    print(f"📁 Analytics folder: {analytics_dir}")
    print(f"📄 Data file: {data_csv}")

    df = load_data(data_csv)
    print("\n🔎 Data preview:")
    print(df.head())

    X, y = build_features(df)
    print("\n🧩 Feature columns:")
    print(list(X.columns))

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    # 1) Linear Regression
    lin = LinearRegression()
    evaluate_model("Linear Regression", lin, X_train, X_test, y_train, y_test, outputs_dir)

    # 2) Random Forest Regression (more powerful model)
    rf = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1
    )
    evaluate_model("Random Forest", rf, X_train, X_test, y_train, y_test, outputs_dir)

    # Feature importance chart
    save_feature_importance(rf, X.columns.tolist(), outputs_dir)

    print("\n🎉 Step 2 complete! Check analytics/outputs/ for results.")


if __name__ == "__main__":
    main()

"""
Month 4 - Machine Learning (Baseline Regression)

Goal:
- Use your exported analytics CSV to build a simple regression model
- Predict total_enrollments
- Evaluate with MAE / RMSE / R2
- Save charts + model output

Input CSV (created earlier):
- analytics/student_activity_report.csv

Output:
- analytics/outputs/ml_pred_vs_actual.png
- analytics/outputs/ml_residuals.png
- analytics/outputs/regression_baseline_model.joblib
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib


# ---------- Paths ----------
ANALYTICS_DIR = Path(__file__).resolve().parents[1]
INPUT_CSV = ANALYTICS_DIR / "student_activity_report.csv"

OUTPUT_DIR = ANALYTICS_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = OUTPUT_DIR / "regression_baseline_model.joblib"
PRED_PLOT_PATH = OUTPUT_DIR / "ml_pred_vs_actual.png"
RESID_PLOT_PATH = OUTPUT_DIR / "ml_residuals.png"


def load_data() -> pd.DataFrame:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"❌ Missing file: {INPUT_CSV}\n"
            "Run your activity report script first to generate:\n"
            "  python analytics/student_activity_report.py"
        )

    df = pd.read_csv(INPUT_CSV)

    # Expected columns (from your preview):
    # student_id, name, email, primary_course, total_enrollments
    # Some versions may include age; if not, we still train with categorical features.
    return df


def build_pipeline(feature_cols, numeric_cols, categorical_cols) -> Pipeline:
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    model = LinearRegression()

    pipe = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipe


def save_pred_plot(y_test, y_pred):
    plt.figure()
    plt.scatter(y_test, y_pred)
    plt.xlabel("Actual total_enrollments")
    plt.ylabel("Predicted total_enrollments")
    plt.title("Regression Baseline: Predicted vs Actual")
    plt.savefig(PRED_PLOT_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def save_residual_plot(y_test, y_pred):
    residuals = y_test - y_pred
    plt.figure()
    plt.hist(residuals, bins=10)
    plt.xlabel("Residual (Actual - Predicted)")
    plt.ylabel("Count")
    plt.title("Regression Baseline: Residual Distribution")
    plt.savefig(RESID_PLOT_PATH, dpi=200, bbox_inches="tight")
    plt.close()


def main():
    print("📥 Loading data...")
    df = load_data()

    # ---- Target ----
    if "total_enrollments" not in df.columns:
        raise ValueError("❌ CSV must include 'total_enrollments' column.")

    y = df["total_enrollments"].astype(float)

    # ---- Features ----
    # Use whatever features exist in your report.
    # We'll try to use age if it exists, and also primary_course.
    candidate_features = ["age", "primary_course"]
    feature_cols = [c for c in candidate_features if c in df.columns]

    if not feature_cols:
        raise ValueError(
            "❌ No usable feature columns found.\n"
            "Expected at least one of: age, primary_course\n"
            f"Your CSV columns are: {list(df.columns)}"
        )

    X = df[feature_cols].copy()

    numeric_cols = [c for c in feature_cols if c in ["age"]]
    categorical_cols = [c for c in feature_cols if c not in numeric_cols]

    print(f"✅ Using features: {feature_cols}")
    print("🧪 Splitting train/test...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42
    )

    pipe = build_pipeline(feature_cols, numeric_cols, categorical_cols)

    print("🤖 Training baseline model (Linear Regression)...")
    pipe.fit(X_train, y_train)

    print("📊 Evaluating...")
    y_pred = pipe.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n✅ Baseline Results")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²  : {r2:.4f}")

    print("\n💾 Saving model + charts...")
    joblib.dump(pipe, MODEL_PATH)

    save_pred_plot(y_test, y_pred)
    save_residual_plot(y_test, y_pred)

    print(f"✅ Saved model: {MODEL_PATH}")
    print(f"✅ Saved chart: {PRED_PLOT_PATH}")
    print(f"✅ Saved chart: {RESID_PLOT_PATH}")
    print("\n🎯 Done! Next we can improve the model + add more features.")


if __name__ == "__main__":
    main()

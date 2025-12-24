# ml/model_evaluation.py
"""
Month 4 — Step 7: Model Comparison & Evaluation
Compare Linear Regression vs Random Forest for predicting total_enrollments
"""

from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import joblib


def setup_paths():
    """Setup project directories"""
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "analytics" / "ml_ready_dataset.csv"
    out_dir = base_dir / "ml" / "outputs"
    model_dir = base_dir / "ml" / "models"
    
    # Create directories if they don't exist
    out_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    return data_path, out_dir, model_dir


def load_ml_data(data_path: Path):
    """Load and prepare ML-ready dataset"""
    print(f"📂 Loading data from: {data_path}")
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"❌ Missing file: {data_path}\n"
            f"Run first: python analytics/ml_ready_dataset.py"
        )
    
    df = pd.read_csv(data_path)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    
    return df


def prepare_features_target(df: pd.DataFrame):
    """
    Separate features (X) and target (y)
    
    Target: total_enrollments (what we're predicting)
    Features: everything else (age, course columns)
    """
    # Target variable (what we want to predict)
    target_col = "total_enrollments"
    
    if target_col not in df.columns:
        raise ValueError(f"❌ Target column '{target_col}' not found in dataset!")
    
    # Features (all columns except target)
    X = df.drop(columns=[target_col])
    
    # Target (what we're predicting)
    y = df[target_col]
    
    print(f"\n📊 Data Shape:")
    print(f"   Features (X): {X.shape}")
    print(f"   Target (y): {y.shape}")
    print(f"   Feature columns: {list(X.columns)}")
    
    return X, y


def train_linear_regression(X_train, y_train, X_test):
    """Train Linear Regression model"""
    print("\n🔵 Training Linear Regression...")
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    print("   ✅ Linear Regression trained")
    
    return model, predictions


def train_random_forest(X_train, y_train, X_test):
    """Train Random Forest model"""
    print("\n🌲 Training Random Forest...")
    
    model = RandomForestRegressor(
        n_estimators=100,      # 100 trees in the forest
        max_depth=10,          # Maximum depth of each tree
        random_state=42,       # For reproducibility
        n_jobs=-1              # Use all CPU cores
    )
    
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    print("   ✅ Random Forest trained")
    
    return model, predictions


def evaluate_model(name: str, y_true, y_pred):
    """
    Calculate evaluation metrics
    
    Metrics:
    - RMSE: Root Mean Squared Error (lower is better)
    - MAE: Mean Absolute Error (lower is better)  
    - R²: R-squared score (higher is better, max 1.0)
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    print(f"\n📊 {name} Results:")
    print(f"   RMSE: {rmse:.4f}")
    print(f"   MAE:  {mae:.4f}")
    print(f"   R²:   {r2:.4f}")
    
    return {
        "model": name,
        "rmse": rmse,
        "mae": mae,
        "r2": r2
    }


def create_comparison_report(lr_metrics, rf_metrics, out_dir: Path):
    """Create detailed comparison report"""
    
    # Determine which model is better (lower RMSE = better)
    if rf_metrics["rmse"] < lr_metrics["rmse"]:
        winner = "Random Forest"
        improvement = ((lr_metrics["rmse"] - rf_metrics["rmse"]) / lr_metrics["rmse"]) * 100
    else:
        winner = "Linear Regression"
        improvement = ((rf_metrics["rmse"] - lr_metrics["rmse"]) / rf_metrics["rmse"]) * 100
    
    report = f"""
╔════════════════════════════════════════════════════════════╗
║          MODEL COMPARISON REPORT                           ║
║          Month 4 — Step 7                                  ║
╚════════════════════════════════════════════════════════════╝

📊 EVALUATION METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Model 1: Linear Regression
  • RMSE:  {lr_metrics["rmse"]:.4f}
  • MAE:   {lr_metrics["mae"]:.4f}
  • R²:    {lr_metrics["r2"]:.4f}

Model 2: Random Forest
  • RMSE:  {rf_metrics["rmse"]:.4f}
  • MAE:   {rf_metrics["mae"]:.4f}
  • R²:    {rf_metrics["r2"]:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏆 WINNER: {winner}

📈 Improvement: {improvement:.2f}% reduction in RMSE

📝 INTERPRETATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• RMSE (Root Mean Squared Error):
  - Measures average prediction error
  - Lower is better
  - {winner} has lower RMSE → more accurate predictions

• R² (R-squared):
  - Measures how much variance is explained
  - Range: 0 to 1 (higher is better)
  - Linear Regression: {lr_metrics["r2"]:.1%} variance explained
  - Random Forest: {rf_metrics["r2"]:.1%} variance explained

🎯 RECOMMENDATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use {winner} for production deployment.

Reasoning:
{'- Better captures non-linear patterns in student behavior' if winner == 'Random Forest' else '- Simpler model with good performance, easier to interpret'}
{'- Handles feature interactions more effectively' if winner == 'Random Forest' else '- Faster predictions and lower computational cost'}
- {improvement:.1f}% better prediction accuracy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    report_path = out_dir / "ml_model_evaluation.txt"
    report_path.write_text(report, encoding="utf-8")
    
    print("\n" + report)
    print(f"\n💾 Saved report: {report_path}")
    
    return winner


def save_individual_metrics(lr_metrics, rf_metrics, out_dir: Path):
    """Save individual model metrics to separate files"""
    
    # Linear Regression metrics
    lr_report = f"""Linear Regression Metrics
========================
RMSE: {lr_metrics["rmse"]:.4f}
MAE:  {lr_metrics["mae"]:.4f}
R²:   {lr_metrics["r2"]:.4f}
"""
    lr_path = out_dir / "ml_linear_regression_metrics.txt"
    lr_path.write_text(lr_report, encoding="utf-8")
    
    # Random Forest metrics
    rf_report = f"""Random Forest Metrics
=====================
RMSE: {rf_metrics["rmse"]:.4f}
MAE:  {rf_metrics["mae"]:.4f}
R²:   {rf_metrics["r2"]:.4f}
"""
    rf_path = out_dir / "ml_random_forest_metrics.txt"
    rf_path.write_text(rf_report, encoding="utf-8")
    
    print(f"   💾 Saved: {lr_path.name}")
    print(f"   💾 Saved: {rf_path.name}")


def save_best_model(lr_model, rf_model, winner: str, model_dir: Path):
    """Save the best performing model"""
    
    best_model = rf_model if winner == "Random Forest" else lr_model
    model_path = model_dir / "best_model.joblib"
    
    joblib.dump(best_model, model_path)
    
    print(f"\n💾 Best model saved: {model_path}")
    print(f"   Model type: {winner}")


def main():
    """Main execution function"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Month 4 — Step 7: Model Comparison & Evaluation          ║")
    print("║  Linear Regression vs Random Forest                       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Step 1: Setup paths
    data_path, out_dir, model_dir = setup_paths()
    
    # Step 2: Load data
    df = load_ml_data(data_path)
    
    # Step 3: Prepare features and target
    X, y = prepare_features_target(df)
    
    # Step 4: Split data (80% train, 20% test)
    print("\n🔀 Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set:     {len(X_test)} samples")
    
    # Step 5: Train Linear Regression
    lr_model, lr_predictions = train_linear_regression(X_train, y_train, X_test)
    lr_metrics = evaluate_model("Linear Regression", y_test, lr_predictions)
    
    # Step 6: Train Random Forest
    rf_model, rf_predictions = train_random_forest(X_train, y_train, X_test)
    rf_metrics = evaluate_model("Random Forest", y_test, rf_predictions)
    
    # Step 7: Create comparison report
    print("\n" + "="*60)
    winner = create_comparison_report(lr_metrics, rf_metrics, out_dir)
    
    # Step 8: Save individual metrics
    print("\n💾 Saving individual metrics...")
    save_individual_metrics(lr_metrics, rf_metrics, out_dir)
    
    # Step 9: Save best model
    save_best_model(lr_model, rf_model, winner, model_dir)
    
    print("\n" + "="*60)
    print("🎉 Step 7 completed successfully!")
    print("="*60)
    print("\n📁 Generated files:")
    print(f"   • {out_dir / 'ml_model_evaluation.txt'}")
    print(f"   • {out_dir / 'ml_linear_regression_metrics.txt'}")
    print(f"   • {out_dir / 'ml_random_forest_metrics.txt'}")
    print(f"   • {model_dir / 'best_model.joblib'}")
    
    print("\n🎯 Next Step:")
    print("   Run: python ml/model_interpretation.py")
    print("   (Feature importance & model interpretation)\n")


if __name__ == "__main__":
    main()

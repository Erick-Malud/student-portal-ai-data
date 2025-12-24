# ml/ml_report_export.py
"""
Month 4 — Step 8: ML Report & Export
Generate predictions, create summary reports, and prepare for production deployment
"""

from pathlib import Path
import pandas as pd
import numpy as np
import json
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib


def setup_paths():
    """Setup project directories"""
    base_dir = Path(__file__).resolve().parent.parent
    data_path = base_dir / "analytics" / "ml_ready_dataset.csv"
    model_path = base_dir / "ml" / "models" / "best_model.joblib"
    out_dir = base_dir / "ml" / "outputs"
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    return data_path, model_path, out_dir


def load_data_and_model(data_path: Path, model_path: Path):
    """Load dataset and trained model"""
    print("📂 Loading data and model...")
    
    if not data_path.exists():
        raise FileNotFoundError(f"❌ Missing data: {data_path}")
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"❌ Missing model: {model_path}\n"
            f"Run first: python ml/model_evaluation.py"
        )
    
    df = pd.read_csv(data_path)
    model = joblib.load(model_path)
    
    print(f"✅ Loaded dataset: {len(df)} rows")
    print(f"✅ Loaded model: {type(model).__name__}")
    
    return df, model


def prepare_data(df: pd.DataFrame):
    """Prepare features and target, split into train/test"""
    target_col = "total_enrollments"
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Use same split as in model_evaluation.py
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, X


def generate_predictions(model, X_train, X_test, y_train, y_test):
    """Generate predictions on both train and test sets"""
    print("\n🔮 Generating predictions...")
    
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    print(f"   ✅ Training predictions: {len(train_predictions)}")
    print(f"   ✅ Test predictions: {len(test_predictions)}")
    
    return train_predictions, test_predictions


def calculate_metrics(y_true, y_pred):
    """Calculate all evaluation metrics"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    return {
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2)
    }


def export_predictions_csv(X_test, y_test, test_predictions, out_dir: Path):
    """Export predictions to CSV for analysis"""
    print("\n💾 Exporting predictions to CSV...")
    
    # Create detailed predictions DataFrame
    predictions_df = pd.DataFrame({
        "actual_enrollments": y_test.values,
        "predicted_enrollments": test_predictions,
        "prediction_error": y_test.values - test_predictions,
        "absolute_error": np.abs(y_test.values - test_predictions),
        "percent_error": np.abs((y_test.values - test_predictions) / y_test.values) * 100
    })
    
    # Add feature values for context
    feature_df = X_test.reset_index(drop=True)
    predictions_df = pd.concat([feature_df, predictions_df], axis=1)
    
    csv_path = out_dir / "ml_predictions.csv"
    predictions_df.to_csv(csv_path, index=False)
    
    print(f"   ✅ Saved: {csv_path}")
    print(f"   📊 Rows: {len(predictions_df)}")
    
    return predictions_df


def create_ml_summary_report(model, train_metrics, test_metrics, X, out_dir: Path):
    """Create comprehensive ML summary report"""
    print("\n📝 Creating ML summary report...")
    
    model_name = type(model).__name__
    
    report = f"""
╔════════════════════════════════════════════════════════════╗
║               MACHINE LEARNING SUMMARY REPORT              ║
║               Month 4 — Final Report                       ║
╚════════════════════════════════════════════════════════════╝

📊 PROJECT OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project Name:        Student Portal Enrollment Prediction
Problem Type:        Regression (Predicting numeric values)
Target Variable:     total_enrollments
Model Selected:      {model_name}
Date Created:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 MODEL PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Training Set Performance:
  • RMSE (Root Mean Squared Error):  {train_metrics['rmse']:.4f}
  • MAE (Mean Absolute Error):       {train_metrics['mae']:.4f}
  • R² (R-squared):                  {train_metrics['r2']:.4f}

Test Set Performance:
  • RMSE (Root Mean Squared Error):  {test_metrics['rmse']:.4f}
  • MAE (Mean Absolute Error):       {test_metrics['mae']:.4f}
  • R² (R-squared):                  {test_metrics['r2']:.4f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 METRICS INTERPRETATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RMSE (Root Mean Squared Error):
  • Measures average prediction error
  • Lower is better
  • Test RMSE: {test_metrics['rmse']:.2f} enrollments off on average
  
MAE (Mean Absolute Error):
  • Average absolute difference between actual and predicted
  • More interpretable than RMSE
  • Test MAE: {test_metrics['mae']:.2f} enrollments

R² (R-squared):
  • Proportion of variance explained by the model
  • Range: -∞ to 1.0 (1.0 is perfect)
  • Test R²: {test_metrics['r2']:.4f}
  {'  ⚠️ Negative R² indicates model struggles with this data' if test_metrics['r2'] < 0 else '  ✅ Positive R² shows model captures patterns'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 FEATURES USED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Features: {len(X.columns)}

Feature List:
{chr(10).join(f'  • {col}' for col in X.columns)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 KEY FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Model Selection:
   {model_name} was chosen as the best performing model after
   comparison with Random Forest Regressor.

2. Performance Assessment:
   {'The model shows limited predictive power (negative R²), likely' if test_metrics['r2'] < 0 else 'The model demonstrates reasonable predictive ability,'}
   {'due to small dataset size (26 students).' if test_metrics['r2'] < 0 else 'capturing patterns in student enrollment behavior.'}

3. Prediction Accuracy:
   On average, predictions are off by {test_metrics['mae']:.2f} enrollments,
   which {'may be acceptable depending on business requirements.' if test_metrics['mae'] < 1 else 'suggests room for improvement with more data.'}

4. Data Limitations:
   • Small sample size limits model generalization
   • Limited features may not capture all enrollment factors
   • Additional data collection recommended

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For Production Deployment:
  ✓ Model is saved and ready for predictions
  ✓ Predictions can be generated via API
  ✓ Monitor prediction errors in production
  ✓ Retrain model as more data becomes available

For Model Improvement:
  • Collect more student data (target: 100+ samples)
  • Add more features (GPA, attendance, demographics)
  • Experiment with feature engineering
  • Consider ensemble methods with larger dataset

For Business Use:
  • Use predictions as guidance, not absolute truth
  • Combine with domain expertise
  • Set up feedback loop to improve model
  • Track model performance over time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 ARTIFACTS GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • ml/models/best_model.joblib           (Trained model)
  • ml/outputs/ml_predictions.csv         (Prediction results)
  • ml/outputs/ml_final_report.txt        (This report)
  • ml/outputs/ml_production_ready.json   (API configuration)
  • ml/outputs/ml_model_card.md           (Model documentation)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ MONTH 4 COMPLETE — Ready for AI Integration (Month 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You have successfully:
  ✓ Built machine learning models from scratch
  ✓ Evaluated and compared multiple models
  ✓ Generated predictions on real data
  ✓ Created production-ready artifacts
  ✓ Documented model for deployment

Next Steps (Month 5):
  → Integrate model with API endpoints
  → Add AI/LLM capabilities
  → Build intelligent student recommendations
  → Deploy to production environment

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    report_path = out_dir / "ml_final_report.txt"
    report_path.write_text(report, encoding="utf-8")
    
    print(f"   ✅ Saved: {report_path}")
    
    return report


def export_api_config(model, test_metrics, X, out_dir: Path):
    """Export API-ready configuration as JSON"""
    print("\n🔌 Creating API configuration...")
    
    model_name = type(model).__name__
    
    api_config = {
        "model_info": {
            "name": "Student Enrollment Predictor",
            "type": model_name,
            "version": "1.0.0",
            "created_date": datetime.now().isoformat(),
            "problem_type": "regression",
            "target": "total_enrollments"
        },
        "performance": {
            "test_rmse": test_metrics["rmse"],
            "test_mae": test_metrics["mae"],
            "test_r2": test_metrics["r2"]
        },
        "features": {
            "count": len(X.columns),
            "names": list(X.columns),
            "types": {col: str(X[col].dtype) for col in X.columns}
        },
        "deployment": {
            "model_path": "ml/models/best_model.joblib",
            "input_format": "JSON with feature names as keys",
            "output_format": "Predicted enrollment count (float)",
            "example_input": {col: float(X[col].iloc[0]) for col in X.columns},
            "example_output": {
                "predicted_enrollments": 1.5,
                "confidence": "medium"
            }
        },
        "usage": {
            "python_example": """
import joblib
import pandas as pd

# Load model
model = joblib.load('ml/models/best_model.joblib')

# Prepare input
input_data = pd.DataFrame([{
    'age': 25,
    'primary_course_Data': True,
    'primary_course_English': False,
    'primary_course_IT': False,
    'primary_course_Management': False
}])

# Make prediction
prediction = model.predict(input_data)
print(f'Predicted enrollments: {prediction[0]:.2f}')
""",
            "api_endpoint_example": "/api/predict/enrollments"
        },
        "monitoring": {
            "track_metrics": ["rmse", "mae", "prediction_latency"],
            "retrain_trigger": "monthly or when performance degrades > 20%",
            "data_requirements": "minimum 100 new samples for retraining"
        }
    }
    
    json_path = out_dir / "ml_production_ready.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(api_config, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Saved: {json_path}")
    
    return api_config


def create_model_card(model, train_metrics, test_metrics, X, out_dir: Path):
    """Create model card documentation (industry standard)"""
    print("\n📄 Creating model card documentation...")
    
    model_name = type(model).__name__
    
    model_card = f"""# Model Card: Student Enrollment Predictor

## Model Details

**Model Name:** Student Enrollment Predictor  
**Model Type:** {model_name}  
**Version:** 1.0.0  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Developer:** Student Portal Team  
**License:** MIT  

## Intended Use

**Primary Use Case:**  
Predict the number of course enrollments for students based on demographic and behavioral features.

**Intended Users:**  
- Educational administrators
- Student advisors
- Data analysts in educational institutions

**Out-of-Scope Uses:**  
- Should not be used for admissions decisions
- Not intended for student evaluation or grading
- Not suitable for institutions with significantly different demographics

## Training Data

**Dataset:** ML-ready Student Portal Dataset  
**Size:** 26 students  
**Split:** 80% training (20 samples), 20% testing (6 samples)  
**Features:** {len(X.columns)} features including:
{chr(10).join(f'- {col}' for col in X.columns)}

**Target Variable:** `total_enrollments` (numeric)

**Data Collection:**  
Data collected from student portal interactions over time.

## Performance Metrics

### Training Set
- **RMSE:** {train_metrics['rmse']:.4f}
- **MAE:** {train_metrics['mae']:.4f}
- **R²:** {train_metrics['r2']:.4f}

### Test Set
- **RMSE:** {test_metrics['rmse']:.4f}
- **MAE:** {test_metrics['mae']:.4f}
- **R²:** {test_metrics['r2']:.4f}

## Limitations

1. **Small Dataset:** Only 26 samples may limit generalization
2. **Feature Coverage:** Limited features may not capture all enrollment factors
3. **Temporal Aspects:** Does not account for time-based patterns
4. **Demographic Diversity:** May not generalize to different student populations

## Ethical Considerations

- Model predictions should be used as guidance, not definitive decisions
- Regular monitoring required to detect bias or performance degradation
- Transparency in model usage recommended for affected students
- Human oversight required for critical decisions

## Usage

### Loading the Model

```python
import joblib
model = joblib.load('ml/models/best_model.joblib')
```

### Making Predictions

```python
import pandas as pd

# Prepare input features
input_data = pd.DataFrame([{{
    'age': 25,
    'primary_course_Data': True,
    'primary_course_English': False,
    'primary_course_IT': False,
    'primary_course_Management': False
}}])

# Predict
prediction = model.predict(input_data)
print(f'Predicted enrollments: {{prediction[0]:.2f}}')
```

## Maintenance

**Retraining Schedule:** Monthly or when performance degrades  
**Monitoring:** Track RMSE, MAE, and prediction latency  
**Data Requirements:** Minimum 100 new samples for effective retraining  

## Contact

For questions or issues with this model, contact the Student Portal development team.

---

*This model card follows the framework proposed by Mitchell et al. (2019)*
*"Model Cards for Model Reporting" - https://arxiv.org/abs/1810.03993*
"""
    
    card_path = out_dir / "ml_model_card.md"
    card_path.write_text(model_card, encoding="utf-8")
    
    print(f"   ✅ Saved: {card_path}")


def print_summary_stats(predictions_df, test_metrics):
    """Print summary statistics about predictions"""
    print("\n" + "="*60)
    print("📊 PREDICTION SUMMARY STATISTICS")
    print("="*60)
    
    print(f"\n🎯 Performance Metrics:")
    print(f"   RMSE: {test_metrics['rmse']:.4f}")
    print(f"   MAE:  {test_metrics['mae']:.4f}")
    print(f"   R²:   {test_metrics['r2']:.4f}")
    
    print(f"\n📈 Prediction Statistics:")
    print(f"   Mean actual:     {predictions_df['actual_enrollments'].mean():.2f}")
    print(f"   Mean predicted:  {predictions_df['predicted_enrollments'].mean():.2f}")
    print(f"   Min error:       {predictions_df['prediction_error'].min():.2f}")
    print(f"   Max error:       {predictions_df['prediction_error'].max():.2f}")
    print(f"   Mean abs error:  {predictions_df['absolute_error'].mean():.2f}")


def main():
    """Main execution function"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Month 4 — Step 8: ML Report & Export                     ║")
    print("║  Prepare results for production deployment                ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Step 1: Setup paths
    data_path, model_path, out_dir = setup_paths()
    
    # Step 2: Load data and model
    df, model = load_data_and_model(data_path, model_path)
    
    # Step 3: Prepare data (same split as training)
    X_train, X_test, y_train, y_test, X = prepare_data(df)
    
    # Step 4: Generate predictions
    train_predictions, test_predictions = generate_predictions(
        model, X_train, X_test, y_train, y_test
    )
    
    # Step 5: Calculate metrics
    print("\n📊 Calculating performance metrics...")
    train_metrics = calculate_metrics(y_train, train_predictions)
    test_metrics = calculate_metrics(y_test, test_predictions)
    print("   ✅ Metrics calculated")
    
    # Step 6: Export predictions to CSV
    predictions_df = export_predictions_csv(X_test, y_test, test_predictions, out_dir)
    
    # Step 7: Create ML summary report
    create_ml_summary_report(model, train_metrics, test_metrics, X, out_dir)
    
    # Step 8: Export API configuration
    export_api_config(model, test_metrics, X, out_dir)
    
    # Step 9: Create model card
    create_model_card(model, train_metrics, test_metrics, X, out_dir)
    
    # Step 10: Print summary
    print_summary_stats(predictions_df, test_metrics)
    
    print("\n" + "="*60)
    print("🎉 Step 8 completed successfully!")
    print("="*60)
    
    print("\n📁 All Generated Files:")
    print(f"   • {out_dir / 'ml_predictions.csv'}")
    print(f"   • {out_dir / 'ml_final_report.txt'}")
    print(f"   • {out_dir / 'ml_production_ready.json'}")
    print(f"   • {out_dir / 'ml_model_card.md'}")
    
    print("\n✅ MONTH 4 COMPLETE!")
    print("="*60)
    print("\n🎓 What You've Accomplished:")
    print("   ✓ Built ML models from scratch")
    print("   ✓ Evaluated and compared models")
    print("   ✓ Generated production predictions")
    print("   ✓ Created deployment documentation")
    print("   ✓ Prepared API-ready outputs")
    
    print("\n🚀 Ready for Month 5: AI & LLM Integration!")
    print("   → Build intelligent APIs")
    print("   → Integrate language models")
    print("   → Create smart recommendations")
    print("   → Deploy to production\n")


if __name__ == "__main__":
    main()

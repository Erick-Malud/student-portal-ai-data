# Model Card: Student Enrollment Predictor

## Model Details

**Model Name:** Student Enrollment Predictor  
**Model Type:** LinearRegression  
**Version:** 1.0.0  
**Date:** 2025-12-24  
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
**Features:** 5 features including:
- age
- primary_course_Data
- primary_course_English
- primary_course_IT
- primary_course_Management

**Target Variable:** `total_enrollments` (numeric)

**Data Collection:**  
Data collected from student portal interactions over time.

## Performance Metrics

### Training Set
- **RMSE:** 1.6250
- **MAE:** 1.3551
- **R²:** 0.4184

### Test Set
- **RMSE:** 2.2812
- **MAE:** 1.9265
- **R²:** -3.2577

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
input_data = pd.DataFrame([{
    'age': 25,
    'primary_course_Data': True,
    'primary_course_English': False,
    'primary_course_IT': False,
    'primary_course_Management': False
}])

# Predict
prediction = model.predict(input_data)
print(f'Predicted enrollments: {prediction[0]:.2f}')
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

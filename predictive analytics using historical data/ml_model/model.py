import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import sys

# Add root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

class StudentPerformancePredictor:
    """
    Predictive Analytics Engine using Linear Regression.
    Predicts student final exam marks based on historical academic parameters.
    """

    FEATURE_NAMES = [
        'attendance_percentage',
        'study_hours',
        'previous_semester_marks',
        'assignment_marks',
        'internal_marks'
    ]
    
    TARGET_NAME = 'final_exam_marks'

    def __init__(self):
        self.model = None
        self.scaler = None
        self.metrics = {}
        self.load_model()

    def preprocess_dataframe(self, df):
        """Clean, validate, and convert dataframe columns."""
        clean_df = df.copy()
        
        # Ensure target and features are present
        cols = self.FEATURE_NAMES + [self.TARGET_NAME]
        for col in cols:
            if col in clean_df.columns:
                clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')
        
        # Drop rows with NaN in features or target
        clean_df = clean_df.dropna(subset=cols)

        # Clip values to realistic academic boundaries
        clean_df['attendance_percentage'] = clean_df['attendance_percentage'].clip(0, 100)
        clean_df['study_hours'] = clean_df['study_hours'].clip(0, 70)
        clean_df['previous_semester_marks'] = clean_df['previous_semester_marks'].clip(0, 100)
        clean_df['assignment_marks'] = clean_df['assignment_marks'].clip(0, 100)
        clean_df['internal_marks'] = clean_df['internal_marks'].clip(0, 100)
        clean_df['final_exam_marks'] = clean_df['final_exam_marks'].clip(0, 100)

        return clean_df

    def train(self, df):
        """
        Trains the Linear Regression model on historical student data.
        Calculates and persists MAE, MSE, RMSE, and R2 score.
        """
        clean_df = self.preprocess_dataframe(df)

        if len(clean_df) < 5:
            raise ValueError("Insufficient records for model training. Minimum 5 valid records required.")

        X = clean_df[self.FEATURE_NAMES]
        y = clean_df[self.TARGET_NAME]

        # Use train_test_split if dataset has 10+ samples, otherwise use full dataset
        if len(clean_df) >= 10:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y

        # Standard Scaling
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Linear Regression Model
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)

        # Evaluation
        y_pred = self.model.predict(X_test_scaled)
        y_pred_clipped = np.clip(y_pred, 0, 100)

        mae = float(mean_absolute_error(y_test, y_pred_clipped))
        mse = float(mean_squared_error(y_test, y_pred_clipped))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_test, y_pred_clipped))

        # Extract feature coefficients
        coefficients = {}
        for feature, coeff in zip(self.FEATURE_NAMES, self.model.coef_):
            coefficients[feature] = round(float(coeff), 4)

        self.metrics = {
            'mae': round(mae, 4),
            'mse': round(mse, 4),
            'rmse': round(rmse, 4),
            'r2_score': round(r2, 4),
            'intercept': round(float(self.model.intercept_), 4),
            'coefficients': coefficients,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'total_samples': len(clean_df)
        }

        # Save model artifacts
        self.save_model()
        return self.metrics

    def save_model(self):
        """Persists trained model, scaler, and evaluation metrics to disk."""
        os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
        if self.model and self.scaler:
            joblib.dump(self.model, Config.MODEL_PATH)
            joblib.dump(self.scaler, Config.SCALER_PATH)
            with open(Config.METRICS_PATH, 'w') as f:
                json.dump(self.metrics, f, indent=4)

    def load_model(self):
        """Loads trained model, scaler, and evaluation metrics from disk."""
        if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.SCALER_PATH):
            try:
                self.model = joblib.load(Config.MODEL_PATH)
                self.scaler = joblib.load(Config.SCALER_PATH)
                if os.path.exists(Config.METRICS_PATH):
                    with open(Config.METRICS_PATH, 'r') as f:
                        self.metrics = json.load(f)
                return True
            except Exception as e:
                print(f"Error loading model artifacts: {e}")
                return False
        return False

    def get_performance_category(self, score):
        """Categorizes predicted marks into academic performance bands."""
        if score >= 85:
            return {
                'category': 'Excellent',
                'badge': 'bg-success',
                'color': '#10b981',
                'description': 'Demonstrates exceptional mastery of course concepts and strong academic discipline.'
            }
        elif score >= 70:
            return {
                'category': 'Good',
                'badge': 'bg-primary',
                'color': '#3b82f6',
                'description': 'Solid understanding of core concepts with consistent academic progress.'
            }
        elif score >= 50:
            return {
                'category': 'Average',
                'badge': 'bg-warning text-dark',
                'color': '#f59e0b',
                'description': 'Meets basic standards, but requires targeted effort in study hours and attendance to improve.'
            }
        else:
            return {
                'category': 'Needs Improvement',
                'badge': 'bg-danger',
                'color': '#ef4444',
                'description': 'At risk of underperforming. Immediate intervention in study routine and attendance recommended.'
            }

    def generate_recommendations(self, inputs, predicted_score):
        """Generates tailored academic advice based on feature values and prediction."""
        recs = []
        att = inputs.get('attendance_percentage', 0)
        hours = inputs.get('study_hours', 0)
        prev = inputs.get('previous_semester_marks', 0)
        assign = inputs.get('assignment_marks', 0)
        internal = inputs.get('internal_marks', 0)

        if att < 75:
            recs.append("Attendance is below 75%. Increasing lecture attendance will directly improve concept retention.")
        else:
            recs.append("Great attendance record! Maintaining high attendance supports consistent comprehension.")

        if hours < 15:
            recs.append("Weekly study hours are relatively low. Aim for at least 15-20 hours of focused study per week.")
        elif hours >= 25:
            recs.append("Excellent study commitment! Ensure balanced revision and healthy rest schedules.")

        if internal < 60 or assign < 60:
            recs.append("Focus on improving continuous evaluation scores (assignments and internal tests).")

        if predicted_score < 70:
            recs.append("Recommended action: Join peer study groups and consult subject mentors for weak topics.")

        return recs

    def predict(self, feature_dict):
        """
        Predicts final exam marks for given student feature dictionary.
        Returns predicted score, performance category, and academic insights.
        """
        if not self.model or not self.scaler:
            raise RuntimeError("Model is not trained yet. Please train the model first.")

        # Extract features in correct order
        features_array = np.array([[
            float(feature_dict['attendance_percentage']),
            float(feature_dict['study_hours']),
            float(feature_dict['previous_semester_marks']),
            float(feature_dict['assignment_marks']),
            float(feature_dict['internal_marks'])
        ]])

        # Scale features
        scaled_features = self.scaler.transform(features_array)

        # Predict
        predicted_mark = float(self.model.predict(scaled_features)[0])
        predicted_mark_clipped = float(np.clip(predicted_mark, 0, 100))
        predicted_mark_rounded = round(predicted_mark_clipped, 2)

        # Category and Recommendations
        cat_info = self.get_performance_category(predicted_mark_rounded)
        recommendations = self.generate_recommendations(feature_dict, predicted_mark_rounded)

        return {
            'predicted_final_marks': predicted_mark_rounded,
            'category': cat_info['category'],
            'category_badge': cat_info['badge'],
            'category_color': cat_info['color'],
            'category_description': cat_info['description'],
            'recommendations': recommendations,
            'inputs': feature_dict
        }

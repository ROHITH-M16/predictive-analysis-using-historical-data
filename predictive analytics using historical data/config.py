import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'predictive-analytics-msc-secret-key-2026'
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'student_analytics.db')
    SAMPLE_CSV_PATH = os.path.join(BASE_DIR, 'data', 'sample_students.csv')
    MODEL_PATH = os.path.join(BASE_DIR, 'ml_model', 'student_model.pkl')
    SCALER_PATH = os.path.join(BASE_DIR, 'ml_model', 'scaler.pkl')
    METRICS_PATH = os.path.join(BASE_DIR, 'ml_model', 'model_metrics.json')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data')
    ALLOWED_EXTENSIONS = {'csv'}

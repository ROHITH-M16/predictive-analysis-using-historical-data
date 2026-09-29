import os
import random
import pandas as pd
import numpy as np
import sys

# Ensure root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config
from database.db import get_db_connection, init_db, get_students_dataframe
from ml_model.model import StudentPerformancePredictor

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohan", "Priya", "Aditya", "Sneha", "Vikram", "Kavya", "Rahul", "Neha",
    "Siddharth", "Pooja", "Arjun", "Divya", "Karan", "Ishita", "Varun", "Riya", "Aman", "Tanvi",
    "Yash", "Meera", "Suresh", "Bhavna", "Nikhil", "Simran", "Rajesh", "Swati", "Amit", "Shruti",
    "Gaurav", "Deepika", "Manish", "Sonam", "Alok", "Nisha", "Tarun", "Payal", "Harsh", "Kirti",
    "Alex", "Sophia", "Liam", "Emma", "Noah", "Olivia", "Ethan", "Ava", "Mason", "Isabella"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Rao", "Gupta", "Singh", "Kumar", "Joshi", "Nair", "Reddy",
    "Mehta", "Deshmukh", "Chopra", "Bhat", "Iyer", "Kulkarni", "Aggarwal", "Das", "Roy", "Malhotra",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
]

def generate_sample_students(count=120, seed=42):
    """Generates synthetic historical student records with realistic statistical correlations."""
    np.random.seed(seed)
    random.seed(seed)

    records = []
    
    for i in range(1, count + 1):
        student_id = f"STU-{i:03d}"
        student_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        
        # Generate correlated student performance metrics
        # Base student capability factor (0.4 to 1.0)
        capability = np.random.uniform(0.4, 1.0)
        
        # Attendance: correlated with capability
        attendance = float(np.clip(np.random.normal(loc=70 + 25 * capability, scale=8), 50.0, 99.5))
        
        # Study hours per week (5 to 38 hours)
        study_hours = float(np.clip(np.random.normal(loc=10 + 20 * capability, scale=4), 4.0, 40.0))
        
        # Previous semester marks (40 to 98)
        prev_marks = float(np.clip(np.random.normal(loc=45 + 48 * capability, scale=7), 40.0, 98.0))
        
        # Assignment marks (45 to 99)
        assignment_marks = float(np.clip(np.random.normal(loc=50 + 45 * capability, scale=6), 45.0, 99.0))
        
        # Internal exam marks (40 to 98)
        internal_marks = float(np.clip(np.random.normal(loc=45 + 46 * capability, scale=6.5), 40.0, 98.0))
        
        # Calculate final exam marks based on weighted regression formula + random noise
        raw_final = (
            0.20 * attendance +
            0.65 * study_hours +
            0.35 * prev_marks +
            0.15 * assignment_marks +
            0.15 * internal_marks +
            np.random.normal(0, 3.5) # realistic variance
        )
        
        # Scale to ensure reasonable range (30 to 98)
        final_marks = float(np.clip(raw_final, 32.0, 98.5))
        
        records.append({
            'student_id': student_id,
            'student_name': student_name,
            'attendance_percentage': round(attendance, 1),
            'study_hours': round(study_hours, 1),
            'previous_semester_marks': round(prev_marks, 1),
            'assignment_marks': round(assignment_marks, 1),
            'internal_marks': round(internal_marks, 1),
            'final_exam_marks': round(final_marks, 1)
        })

    return pd.DataFrame(records)

def seed_database_and_csv(force=False):
    """Saves sample data to CSV and populates database if empty or if force=True."""
    os.makedirs(os.path.dirname(Config.SAMPLE_CSV_PATH), exist_ok=True)
    
    # Generate DataFrame
    df = generate_sample_students(count=120)
    
    # Save CSV
    df.to_csv(Config.SAMPLE_CSV_PATH, index=False)
    print(f"[OK] Created sample CSV dataset with {len(df)} records at: {Config.SAMPLE_CSV_PATH}")

    # Ensure DB is initialized
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0 or force:
        if force:
            cursor.execute("DELETE FROM students")
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO students (
                    student_id, student_name, attendance_percentage, study_hours,
                    previous_semester_marks, assignment_marks, internal_marks, final_exam_marks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['student_id'],
                row['student_name'],
                row['attendance_percentage'],
                row['study_hours'],
                row['previous_semester_marks'],
                row['assignment_marks'],
                row['internal_marks'],
                row['final_exam_marks']
            ))
        conn.commit()
        print(f"[OK] Seeded database with {len(df)} sample records.")
    else:
        print(f"[INFO] Database already contains {count} records. Skipping DB re-seeding.")
    
    conn.close()

    # Train initial model
    predictor = StudentPerformancePredictor()
    db_df = get_students_dataframe()
    if len(db_df) > 0:
        metrics = predictor.train(db_df)
        print(f"[OK] Initialized ML Model. R2 Score: {metrics['r2_score']}, MAE: {metrics['mae']}")

if __name__ == '__main__':
    seed_database_and_csv(force=True)

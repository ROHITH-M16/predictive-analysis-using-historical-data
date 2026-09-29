import sqlite3
import pandas as pd
import os
import sys

# Ensure root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if students table doesn't exist."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        with open(schema_path, 'r') as f:
            cursor.executescript(f.read())
        conn.commit()
    conn.close()

def get_all_students(search_query=None):
    """Retrieves all student records, with optional search filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        query = """
            SELECT * FROM students 
            WHERE student_id LIKE ? OR student_name LIKE ? 
            ORDER BY id DESC
        """
        param = f"%{search_query}%"
        cursor.execute(query, (param, param))
    else:
        cursor.execute("SELECT * FROM students ORDER BY id DESC")
    
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

def get_student_by_id(db_id):
    """Retrieves a single student record by its database primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (db_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_student(student_data):
    """Inserts a new student record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Auto-generate student_id if missing or blank
    if not student_data.get('student_id'):
        cursor.execute("SELECT MAX(id) FROM students")
        max_id = cursor.fetchone()[0] or 0
        student_data['student_id'] = f"STU-{max_id + 1001}"
        
    query = """
        INSERT INTO students (
            student_id, student_name, attendance_percentage, study_hours,
            previous_semester_marks, assignment_marks, internal_marks, final_exam_marks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (
        student_data['student_id'],
        student_data['student_name'],
        float(student_data['attendance_percentage']),
        float(student_data['study_hours']),
        float(student_data['previous_semester_marks']),
        float(student_data['assignment_marks']),
        float(student_data['internal_marks']),
        float(student_data['final_exam_marks'])
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_student(db_id, student_data):
    """Updates an existing student record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE students SET 
            student_id = ?,
            student_name = ?,
            attendance_percentage = ?,
            study_hours = ?,
            previous_semester_marks = ?,
            assignment_marks = ?,
            internal_marks = ?,
            final_exam_marks = ?
        WHERE id = ?
    """
    cursor.execute(query, (
        student_data['student_id'],
        student_data['student_name'],
        float(student_data['attendance_percentage']),
        float(student_data['study_hours']),
        float(student_data['previous_semester_marks']),
        float(student_data['assignment_marks']),
        float(student_data['internal_marks']),
        float(student_data['final_exam_marks']),
        db_id
    ))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_student(db_id):
    """Deletes a student record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (db_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_students_dataframe():
    """Returns all student records as a Pandas DataFrame for ML training."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def get_student_stats():
    """Calculates overall statistical metrics from student records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_students,
            AVG(attendance_percentage) as avg_attendance,
            AVG(study_hours) as avg_study_hours,
            AVG(previous_semester_marks) as avg_previous_marks,
            AVG(assignment_marks) as avg_assignment_marks,
            AVG(internal_marks) as avg_internal_marks,
            AVG(final_exam_marks) as avg_final_marks,
            MIN(final_exam_marks) as min_final_marks,
            MAX(final_exam_marks) as max_final_marks
        FROM students
    """)
    row = cursor.fetchone()
    conn.close()
    
    if not row or row['total_students'] == 0:
        return {
            'total_students': 0,
            'avg_attendance': 0,
            'avg_study_hours': 0,
            'avg_previous_marks': 0,
            'avg_assignment_marks': 0,
            'avg_internal_marks': 0,
            'avg_final_marks': 0,
            'min_final_marks': 0,
            'max_final_marks': 0
        }
    
    return {
        'total_students': row['total_students'],
        'avg_attendance': round(row['avg_attendance'] or 0, 2),
        'avg_study_hours': round(row['avg_study_hours'] or 0, 2),
        'avg_previous_marks': round(row['avg_previous_marks'] or 0, 2),
        'avg_assignment_marks': round(row['avg_assignment_marks'] or 0, 2),
        'avg_internal_marks': round(row['avg_internal_marks'] or 0, 2),
        'avg_final_marks': round(row['avg_final_marks'] or 0, 2),
        'min_final_marks': round(row['min_final_marks'] or 0, 2),
        'max_final_marks': round(row['max_final_marks'] or 0, 2)
    }

def clear_all_students():
    """Clears all records from students table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()

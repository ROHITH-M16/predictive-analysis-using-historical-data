import os
import io
import csv
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

from config import Config
from database.db import (
    init_db, get_all_students, get_student_by_id, add_student,
    update_student, delete_student, get_students_dataframe, get_student_stats, clear_all_students
)
from ml_model.model import StudentPerformancePredictor
from ml_model.generate_sample_data import seed_database_and_csv

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Predictor Engine
predictor = StudentPerformancePredictor()

# Initialize DB on app startup
with app.app_context():
    init_db()
    # Check if DB needs initial seeding
    df = get_students_dataframe()
    if len(df) == 0:
        seed_database_and_csv(force=True)
    else:
        # Ensure model is trained on startup
        try:
            predictor.train(df)
        except Exception as e:
            print(f"Initial model training notice: {e}")

# Helper for CSV validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# --- WEB PAGE ROUTES ---

@app.route('/')
def dashboard():
    """Renders main dashboard page."""
    stats = get_student_stats()
    metrics = predictor.metrics or {}
    return render_template('index.html', stats=stats, metrics=metrics)

@app.route('/students')
def students_page():
    """Renders student records management page."""
    return render_template('students.html')

@app.route('/predict')
def predict_page():
    """Renders single-student prediction page."""
    return render_template('predict.html')

@app.route('/analytics')
def analytics_page():
    """Renders data visual analytics page."""
    return render_template('analytics.html')

@app.route('/model-info')
def model_info_page():
    """Renders machine learning model diagnostics page."""
    metrics = predictor.metrics or {}
    return render_template('model_info.html', metrics=metrics)


# --- REST API ENDPOINTS ---

@app.route('/api/students', methods=['GET'])
def api_get_students():
    """Returns list of students with optional search filter."""
    search_query = request.args.get('search', '').strip()
    students = get_all_students(search_query=search_query if search_query else None)
    
    # Calculate performance category for each student
    for s in students:
        mark = s.get('final_exam_marks', 0)
        cat_info = predictor.get_performance_category(mark)
        s['category'] = cat_info['category']
        s['category_badge'] = cat_info['badge']

    return jsonify({'success': True, 'count': len(students), 'data': students})

@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    """Fetches details for a single student."""
    student = get_student_by_id(id)
    if not student:
        return jsonify({'success': False, 'message': 'Student record not found'}), 404
    
    cat_info = predictor.get_performance_category(student['final_exam_marks'])
    student['category'] = cat_info['category']
    student['category_badge'] = cat_info['badge']
    return jsonify({'success': True, 'data': student})

@app.route('/api/students', methods=['POST'])
def api_add_student():
    """Adds a new student record and auto-retrains the ML model."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Basic validation
        required_fields = ['student_name', 'attendance_percentage', 'study_hours',
                           'previous_semester_marks', 'assignment_marks', 'internal_marks', 'final_exam_marks']
        for field in required_fields:
            if field not in data or data[field] == '':
                return jsonify({'success': False, 'message': f'Field {field} is required.'}), 400

        new_id = add_student(data)
        
        # Auto-retrain model with updated dataset
        df = get_students_dataframe()
        if len(df) >= 5:
            predictor.train(df)

        return jsonify({'success': True, 'message': 'Student record added successfully', 'id': new_id}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['PUT'])
def api_update_student(id):
    """Updates an existing student record and auto-retrains the ML model."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        updated = update_student(id, data)
        if not updated:
            return jsonify({'success': False, 'message': 'Student not found or no changes made'}), 404

        # Auto-retrain model with updated dataset
        df = get_students_dataframe()
        if len(df) >= 5:
            predictor.train(df)

        return jsonify({'success': True, 'message': 'Student record updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/<int:id>', methods=['DELETE'])
def api_delete_student(id):
    """Deletes a student record and auto-retrains the ML model."""
    try:
        deleted = delete_student(id)
        if not deleted:
            return jsonify({'success': False, 'message': 'Student record not found'}), 404

        # Auto-retrain model
        df = get_students_dataframe()
        if len(df) >= 5:
            predictor.train(df)

        return jsonify({'success': True, 'message': 'Student record deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/students/upload-csv', methods=['POST'])
def api_upload_csv():
    """Parses uploaded CSV file, bulk inserts records into SQLite DB, and retrains model."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No CSV file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file format. Please upload a .csv file.'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        required_cols = {'student_name', 'attendance_percentage', 'study_hours',
                         'previous_semester_marks', 'assignment_marks', 'internal_marks', 'final_exam_marks'}
        
        # Normalize header column names (lowercase, strip spaces)
        if not csv_input.fieldnames:
            return jsonify({'success': False, 'message': 'CSV file is empty or invalid.'}), 400

        field_map = {col.strip().lower(): col for col in csv_input.fieldnames}
        
        missing = required_cols - set(field_map.keys())
        if missing:
            return jsonify({'success': False, 'message': f'CSV missing required columns: {", ".join(missing)}'}), 400

        added_count = 0
        error_count = 0

        for row in csv_input:
            try:
                record = {
                    'student_id': row.get(field_map.get('student_id', ''), '').strip(),
                    'student_name': row.get(field_map.get('student_name'), '').strip(),
                    'attendance_percentage': float(row.get(field_map.get('attendance_percentage'))),
                    'study_hours': float(row.get(field_map.get('study_hours'))),
                    'previous_semester_marks': float(row.get(field_map.get('previous_semester_marks'))),
                    'assignment_marks': float(row.get(field_map.get('assignment_marks'))),
                    'internal_marks': float(row.get(field_map.get('internal_marks'))),
                    'final_exam_marks': float(row.get(field_map.get('final_exam_marks')))
                }
                add_student(record)
                added_count += 1
            except Exception as row_err:
                error_count += 1
                continue

        # Auto-retrain model
        df = get_students_dataframe()
        if len(df) >= 5:
            predictor.train(df)

        return jsonify({
            'success': True,
            'message': f'Successfully imported {added_count} student records. (Errors: {error_count})',
            'added_count': added_count,
            'error_count': error_count
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing CSV file: {str(e)}'}), 500

@app.route('/api/students/sample-csv', methods=['GET'])
def api_download_sample_csv():
    """Serves sample CSV template for users to download."""
    if os.path.exists(Config.SAMPLE_CSV_PATH):
        return send_file(
            Config.SAMPLE_CSV_PATH,
            mimetype='text/csv',
            as_attachment=True,
            download_name='sample_students_data.csv'
        )
    return jsonify({'success': False, 'message': 'Sample CSV not found'}), 404

@app.route('/api/students/reset-sample-data', methods=['POST'])
def api_reset_sample_data():
    """Resets database back to default sample dataset."""
    try:
        seed_database_and_csv(force=True)
        return jsonify({'success': True, 'message': 'Database reset to 120 sample records successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Predicts student final exam mark based on input feature values."""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        required_features = ['attendance_percentage', 'study_hours',
                            'previous_semester_marks', 'assignment_marks', 'internal_marks']
        
        for feat in required_features:
            if feat not in data:
                return jsonify({'success': False, 'message': f'Missing feature: {feat}'}), 400
        
        result = predictor.predict(data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analytics-data', methods=['GET'])
def api_analytics_data():
    """Provides structured data payload for Chart.js charts and visual dashboard."""
    students = get_all_students()
    stats = get_student_stats()

    categories_count = {
        'Excellent': 0,
        'Good': 0,
        'Average': 0,
        'Needs Improvement': 0
    }

    scatter_attendance = []
    scatter_study_hours = []
    scatter_previous_marks = []

    for s in students:
        mark = s['final_exam_marks']
        cat_info = predictor.get_performance_category(mark)
        cat_name = cat_info['category']
        categories_count[cat_name] = categories_count.get(cat_name, 0) + 1

        scatter_attendance.append({
            'x': s['attendance_percentage'],
            'y': mark,
            'name': s['student_name'],
            'id': s['student_id']
        })
        scatter_study_hours.append({
            'x': s['study_hours'],
            'y': mark,
            'name': s['student_name'],
            'id': s['student_id']
        })
        scatter_previous_marks.append({
            'x': s['previous_semester_marks'],
            'y': mark,
            'name': s['student_name'],
            'id': s['student_id']
        })

    return jsonify({
        'success': True,
        'stats': stats,
        'category_distribution': categories_count,
        'scatter_attendance': scatter_attendance,
        'scatter_study_hours': scatter_study_hours,
        'scatter_previous_marks': scatter_previous_marks,
        'metrics': predictor.metrics or {}
    })

@app.route('/api/model/metrics', methods=['GET'])
def api_model_metrics():
    """Returns Linear Regression evaluation metrics (MAE, MSE, RMSE, R2 Score)."""
    return jsonify({
        'success': True,
        'metrics': predictor.metrics or {}
    })

@app.route('/api/model/retrain', methods=['POST'])
def api_model_retrain():
    """Triggers retraining of the Linear Regression model on current DB state."""
    try:
        df = get_students_dataframe()
        if len(df) < 5:
            return jsonify({'success': False, 'message': 'Minimum 5 student records required to train model.'}), 400
        
        metrics = predictor.train(df)
        return jsonify({
            'success': True,
            'message': 'Model retrained successfully!',
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("=================================================================")
    print(" PREDICTIVE ANALYTICS SYSTEM FOR STUDENT PERFORMANCE (M.Sc CS)")
    print(" Running Flask App on http://127.0.0.1:5000")
    print("=================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)

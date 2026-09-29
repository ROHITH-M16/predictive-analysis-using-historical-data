DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    student_name TEXT NOT NULL,
    attendance_percentage REAL NOT NULL,
    study_hours REAL NOT NULL,
    previous_semester_marks REAL NOT NULL,
    assignment_marks REAL NOT NULL,
    internal_marks REAL NOT NULL,
    final_exam_marks REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

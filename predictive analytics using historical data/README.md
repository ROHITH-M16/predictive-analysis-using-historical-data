# Predictive Analytics Using Historical Data

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)

A complete full-stack machine learning college project designed for an **M.Sc Computer Science** curriculum. This system uses historical student academic performance data to train a **Linear Regression** model that predicts future student final exam performance, categorizes students into academic bands, and provides actionable recommendations.

---

## 📌 Project Objectives

1. **Academic Analytics**: Leverage historical academic indicators (attendance, study hours, previous semester performance, assignment marks, and internal test marks) to forecast student final exam scores.
2. **Predictive Modeling**: Train and evaluate a Multiple Linear Regression model using `Scikit-learn` with metrics including **MAE**, **MSE**, **RMSE**, and **R² Score**.
3. **Data Management**: Provide full CRUD operations for managing student records alongside bulk CSV dataset import/export.
4. **Visual Analytics**: Interactive dashboard featuring Chart.js scatter plots and distribution visualizations to expose underlying feature correlations.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, FontAwesome 6 |
| **Data Visualization** | Chart.js 4.4, MathJax 3 (LaTeX Math Rendering) |
| **Backend Web Framework** | Python 3.11, Flask 3.0 |
| **Machine Learning** | Scikit-Learn (`LinearRegression`, `StandardScaler`, `train_test_split`) |
| **Data Processing** | Pandas, NumPy, Joblib |
| **Database** | SQLite 3 |

---

## 📂 Project Structure

```
Predictive analytics using historical data/
│
├── app.py                      # Flask Application Server (Routes & API endpoints)
├── config.py                   # Central Application Configuration
├── requirements.txt            # Python Package Dependencies
├── README.md                   # Comprehensive Documentation & Setup Guide
│
├── database/
│   ├── db.py                   # SQLite Helper Functions & CRUD Interface
│   ├── schema.sql              # Database Schema Definition
│   └── student_analytics.db    # SQLite Database File (Created at runtime)
│
├── ml_model/
│   ├── model.py                # ML Engine (Preprocessing, Training, Evaluation, Prediction)
│   ├── generate_sample_data.py # Dataset Generator (120+ Sample Student Records & Seeding)
│   ├── student_model.pkl       # Saved Trained Scikit-Learn Model
│   ├── scaler.pkl              # Saved Feature StandardScaler
│   └── model_metrics.json      # Persisted Evaluation Metrics (MAE, MSE, RMSE, R²)
│
├── data/
│   └── sample_students.csv     # Historical Sample Dataset (120 Student Records)
│
├── static/
│   ├── css/
│   │   └── style.css           # Modern Dashboard & Responsive Glassmorphic CSS
│   └── js/
│       ├── dashboard.js        # Dashboard Charts & Quick Predict UI
│       ├── students.js         # Student CRUD, Pagination, Search, CSV Upload JS
│       └── predict.js          # Interactive Prediction Page & Score Ring Logic
│
└── templates/
    ├── base.html               # Base HTML Layout with Navigation & Sidebar
    ├── index.html              # Responsive Dashboard Page
    ├── students.html           # Student Historical Data Management Page
    ├── predict.html            # Single Student Mark Prediction Page
    ├── analytics.html          # Feature Relationship & Scatter Plot Analytics Page
    └── model_info.html         # ML Model Diagnostics & Metrics Page
```

---

## 📊 Dataset Schema (8 Required Fields)

Each record in the dataset includes:

| Field Name | Type | Description | Range / Unit |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Unique Identifier (e.g., `STU-001`) | Primary Key |
| `student_name` | String | Full Name of the Student | Text |
| `attendance_percentage` | Float | Class Attendance Rate | `0.0 - 100.0%` |
| `study_hours` | Float | Weekly Independent Study Time | `0.0 - 60.0 hrs/wk` |
| `previous_semester_marks` | Float | Score in Previous Academic Semester | `0.0 - 100.0%` |
| `assignment_marks` | Float | Score in Coursework / Assignments | `0.0 - 100.0%` |
| `internal_marks` | Float | Mid-term / Internal Examination Score | `0.0 - 100.0%` |
| `final_exam_marks` | Float | Target Outcome Variable (Final Mark) | `0.0 - 100.0%` |

---

## 🤖 Machine Learning Pipeline

### 1. Model Architecture
- **Algorithm**: Multiple Linear Regression
- **Mathematical Form**:
  $$\hat{y} = \beta_0 + \beta_1 (\text{Attendance}) + \beta_2 (\text{StudyHours}) + \beta_3 (\text{PrevMarks}) + \beta_4 (\text{Assignment}) + \beta_5 (\text{Internal})$$

### 2. Preprocessing & Scaling
- Automatic handling of missing or non-numeric values.
- Boundary clipping (`0 - 100%`) for realistic percentage outputs.
- Feature standardization using `StandardScaler`:
  $$z = \frac{x - \mu}{\sigma}$$

### 3. Performance Categories
Predicted final marks are automatically mapped to four academic performance tiers:
- 🟢 **Excellent**: $\text{Marks} \ge 85\%$
- 🔵 **Good**: $70\% \le \text{Marks} < 85\%$
- 🟡 **Average**: $50\% \le \text{Marks} < 70\%$
- 🔴 **Needs Improvement**: $\text{Marks} < 50\%$

### 4. Evaluation Metrics
The system computes real-time evaluation statistics:
- **MAE** (Mean Absolute Error): Average magnitude of errors.
- **MSE** (Mean Squared Error): Penalizes larger prediction deviations.
- **RMSE** (Root Mean Squared Error): Error expressed in same scale as target variable.
- **$R^2$ Score**: Coefficient of Determination measuring variance explained (typically **0.88 - 0.92** on sample data).

---

## ⚡ Quick Start & Execution Guide (Windows)

### Prerequisites
- **Python 3.10+** installed on your system.
- Standard web browser (Chrome, Edge, Firefox).

### Step 1: Clone / Open Project Directory
Open PowerShell or Command Prompt in the project folder:
```powershell
cd "d:\Predictive analytics using historical data"
```

### Step 2: (Optional) Create & Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

### Step 4: Seed Sample Data & Initialize Model
Run the data generator to seed SQLite database with 120 student records and train the initial Linear Regression model:
```powershell
python ml_model/generate_sample_data.py
```
*Output:*
```text
[OK] Created sample CSV dataset with 120 records at: ...\data\sample_students.csv
[OK] Seeded database with 120 sample records.
[OK] Initialized ML Model. R2 Score: 0.9048, MAE: 2.3211
```

### Step 5: Start Flask Application
```powershell
python app.py
```
Open your web browser and visit:
👉 **`http://127.0.0.1:5000`**

---

## 🌐 Application Page Guide

1. **Dashboard (`/`)**:
   - KPI Summary Cards (Total Students, Mean Attendance, Mean Study Hours, Model R² Score).
   - Interactive Performance Category Breakdown (Chart.js Doughnut Chart).
   - Quick Predict Widget for rapid inference testing.
   - Live Model Evaluation Summary Card.

2. **Student Records (`/students`)**:
   - Paginated, searchable table of historical student data.
   - **Add Record**: Form modal to insert new student data.
   - **Edit / Delete**: Update existing student parameters or remove records.
   - **CSV Upload**: Bulk import records from custom `.csv` files.
   - **Download Sample CSV**: Download formatted template file.
   - **Auto-Retraining**: Automatically updates and retrains the ML model upon any data modification!

3. **Predict Marks (`/predict`)**:
   - Input range sliders and synchronized numerical boxes for all 5 feature inputs.
   - Dynamic score ring calculation showing expected final exam marks out of 100.
   - Performance tier badge with color highlights.
   - Personalized academic recommendations & intervention advice based on feature values.

4. **Data Analytics (`/analytics`)**:
   - **Attendance vs. Final Marks** Scatter Plot.
   - **Study Hours vs. Final Marks** Scatter Plot.
   - **Previous Sem Marks vs. Final Marks** Scatter Plot.
   - Overall Performance Category Bar Chart.

5. **ML Model Diagnostics (`/model-info`)**:
   - Numerical display of MAE, MSE, RMSE, and R² Score.
   - Mathematical formula breakdown with MathJax LaTeX rendering.
   - Standardized Feature Coefficients Bar Chart highlighting feature impact.
   - One-click **"Retrain Model Now"** button with live status feedback.

---

## 📝 Sample CSV Format

When uploading custom dataset files via the CSV upload feature, ensure your file follows this column header structure:

```csv
student_id,student_name,attendance_percentage,study_hours,previous_semester_marks,assignment_marks,internal_marks,final_exam_marks
STU-001,Aarav Sharma,92.5,24.0,85.0,88.0,84.0,89.5
STU-002,Ananya Verma,78.0,16.5,72.0,75.0,70.0,73.5
STU-003,Rohan Patel,62.0,10.0,55.0,60.0,58.0,56.0
```

---

## 🎓 Academic Credit & Project Specifications

- **Title**: Predictive Analytics Using Historical Data
- **Domain**: Data Mining & Machine Learning Applications in Education
- **Degree Program**: M.Sc Computer Science
- **Core Algorithm**: Multiple Linear Regression (`sklearn.linear_model.LinearRegression`)

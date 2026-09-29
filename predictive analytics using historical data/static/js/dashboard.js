// Dashboard Visuals and Quick Predict Script

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardAnalytics();
    setupQuickPredictForm();
});

let categoryChartInstance = null;
let scatterChartInstance = null;

function loadDashboardAnalytics() {
    fetch('/api/analytics-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderCategoryChart(data.category_distribution);
                renderDashboardScatterChart(data.scatter_attendance);
            }
        })
        .catch(err => console.error("Error loading dashboard analytics:", err));
}

function renderCategoryChart(dist) {
    const ctx = document.getElementById('categoryDoughnutChart');
    if (!ctx) return;

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    const labels = Object.keys(dist);
    const values = Object.values(dist);

    categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#10b981', // Excellent - Emerald
                    '#3b82f6', // Good - Blue
                    '#f59e0b', // Average - Amber
                    '#ef4444'  // Needs Improvement - Red
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: { family: 'Plus Jakarta Sans', size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${context.raw} Students`;
                        }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

function renderDashboardScatterChart(scatterData) {
    const ctx = document.getElementById('attendanceScatterChart');
    if (!ctx) return;

    if (scatterChartInstance) {
        scatterChartInstance.destroy();
    }

    scatterChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Student Record',
                data: scatterData,
                backgroundColor: 'rgba(79, 70, 229, 0.6)',
                borderColor: '#4f46e5',
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const point = context.raw;
                            return `${point.name} (${point.id}): Attendance ${point.x}%, Final ${point.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Attendance Percentage (%)', font: { weight: 'bold' } },
                    min: 40,
                    max: 100
                },
                y: {
                    title: { display: true, text: 'Final Exam Marks', font: { weight: 'bold' } },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

function setupQuickPredictForm() {
    const form = document.getElementById('quickPredictForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const payload = {
            attendance_percentage: parseFloat(document.getElementById('qp_attendance').value),
            study_hours: parseFloat(document.getElementById('qp_study_hours').value),
            previous_semester_marks: parseFloat(document.getElementById('qp_prev_marks').value),
            assignment_marks: parseFloat(document.getElementById('qp_assignment').value),
            internal_marks: parseFloat(document.getElementById('qp_internal').value)
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Predicting...';

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Predict Marks';

            if (data.success) {
                const resDiv = document.getElementById('quickPredictResult');
                resDiv.classList.remove('d-none');
                document.getElementById('qp_score').innerText = data.data.predicted_final_marks;
                
                const badge = document.getElementById('qp_category_badge');
                badge.className = `badge ${data.data.category_badge} fs-6 px-3 py-2`;
                badge.innerText = data.data.category;

                resDiv.scrollIntoView({ behavior: 'smooth' });
            } else {
                showNotification(data.message || 'Error making prediction', 'danger');
            }
        })
        .catch(err => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-2"></i>Predict Marks';
            showNotification('Server communication error', 'danger');
        });
    });
}

// Student Performance Prediction Handler

document.addEventListener('DOMContentLoaded', function() {
    setupSlidersSync();
    setupPredictionForm();
});

function setupSlidersSync() {
    const pairs = [
        { slider: 'p_attendance_slider', input: 'p_attendance' },
        { slider: 'p_study_hours_slider', input: 'p_study_hours' },
        { slider: 'p_prev_marks_slider', input: 'p_prev_marks' },
        { slider: 'p_assignment_slider', input: 'p_assignment' },
        { slider: 'p_internal_slider', input: 'p_internal' }
    ];

    pairs.forEach(pair => {
        const sliderEl = document.getElementById(pair.slider);
        const inputEl = document.getElementById(pair.input);

        if (sliderEl && inputEl) {
            sliderEl.addEventListener('input', function() {
                inputEl.value = this.value;
            });
            inputEl.addEventListener('input', function() {
                sliderEl.value = this.value;
            });
        }
    });
}

function setupPredictionForm() {
    const form = document.getElementById('predictForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const payload = {
            attendance_percentage: parseFloat(document.getElementById('p_attendance').value),
            study_hours: parseFloat(document.getElementById('p_study_hours').value),
            previous_semester_marks: parseFloat(document.getElementById('p_prev_marks').value),
            assignment_marks: parseFloat(document.getElementById('p_assignment').value),
            internal_marks: parseFloat(document.getElementById('p_internal').value)
        };

        const submitBtn = document.getElementById('predictBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Analyzing Historical Model...';

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-chart-pie me-2"></i>Generate Final Exam Prediction';

            if (data.success) {
                renderPredictionResult(data.data);
            } else {
                showNotification(data.message || 'Error executing prediction model', 'danger');
            }
        })
        .catch(err => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fa-solid fa-chart-pie me-2"></i>Generate Final Exam Prediction';
            showNotification('Server communication failure', 'danger');
        });
    });
}

function renderPredictionResult(res) {
    const cardContainer = document.getElementById('predictionResultCard');
    cardContainer.classList.remove('d-none');

    // Score Ring Animation
    const scoreVal = document.getElementById('resPredictedScore');
    const ringCircle = document.getElementById('scoreRing');
    
    scoreVal.innerText = res.predicted_final_marks;
    if (ringCircle) {
        ringCircle.style.borderColor = res.category_color;
    }

    // Category Badge & Description
    const categoryBadge = document.getElementById('resCategoryBadge');
    categoryBadge.className = `badge ${res.category_badge} px-4 py-2 fs-6 shadow-sm`;
    categoryBadge.innerText = res.category;

    document.getElementById('resCategoryDesc').innerText = res.category_description;

    // Recommendations list
    const recList = document.getElementById('resRecommendationsList');
    recList.innerHTML = '';
    res.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.className = 'list-group-item bg-transparent border-0 px-0 d-flex align-items-start gap-2 text-dark';
        li.innerHTML = `<i class="fa-solid fa-circle-check text-success mt-1"></i> <span>${rec}</span>`;
        recList.appendChild(li);
    });

    // Scroll smoothly to results
    cardContainer.scrollIntoView({ behavior: 'smooth' });
}

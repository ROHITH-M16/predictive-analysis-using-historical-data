// Student Records CRUD & CSV Upload Handler

let allStudents = [];
let currentPage = 1;
const pageSize = 10;
let deleteStudentDbId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadStudents();

    // Event listeners
    document.getElementById('searchInput')?.addEventListener('input', function(e) {
        loadStudents(e.target.value);
    });

    document.getElementById('studentForm')?.addEventListener('submit', handleSaveStudent);
    document.getElementById('confirmDeleteBtn')?.addEventListener('click', handleConfirmDelete);
    document.getElementById('uploadCsvForm')?.addEventListener('submit', handleUploadCsv);
    document.getElementById('resetSampleDataBtn')?.addEventListener('click', handleResetSampleData);
});

function loadStudents(searchQuery = '') {
    const tableBody = document.getElementById('studentsTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="10" class="text-center py-4">
                <i class="fa-solid fa-spinner fa-spin fs-4 text-primary mb-2 d-block"></i>
                Loading student records...
            </td>
        </tr>
    `;

    const url = searchQuery ? `/api/students?search=${encodeURIComponent(searchQuery)}` : '/api/students';

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                allStudents = data.data;
                currentPage = 1;
                renderStudentsTable();
            } else {
                tableBody.innerHTML = `<tr><td colspan="10" class="text-center text-danger py-4">Failed to load data: ${data.message}</td></tr>`;
            }
        })
        .catch(err => {
            tableBody.innerHTML = `<tr><td colspan="10" class="text-center text-danger py-4">Server error while loading students.</td></tr>`;
        });
}

function renderStudentsTable() {
    const tableBody = document.getElementById('studentsTableBody');
    const paginationEl = document.getElementById('pagination');
    const recordCountEl = document.getElementById('recordCount');

    if (!tableBody) return;

    if (allStudents.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-5 text-muted">
                    <i class="fa-solid fa-folder-open fs-2 mb-2 d-block text-secondary"></i>
                    No student records found. Add a record or upload a CSV file.
                </td>
            </tr>
        `;
        if (recordCountEl) recordCountEl.innerText = 'Showing 0 records';
        if (paginationEl) paginationEl.innerHTML = '';
        return;
    }

    // Pagination calculations
    const totalPages = Math.ceil(allStudents.length / pageSize);
    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, allStudents.length);
    const pageStudents = allStudents.slice(startIdx, endIdx);

    let html = '';
    pageStudents.forEach(s => {
        html += `
            <tr>
                <td class="fw-bold text-primary">${escapeHtml(s.student_id)}</td>
                <td class="fw-semibold text-dark">${escapeHtml(s.student_name)}</td>
                <td><span class="badge bg-light text-dark border">${s.attendance_percentage}%</span></td>
                <td>${s.study_hours} hrs/wk</td>
                <td>${s.previous_semester_marks}</td>
                <td>${s.assignment_marks}</td>
                <td>${s.internal_marks}</td>
                <td class="fw-bold text-dark">${s.final_exam_marks}</td>
                <td><span class="badge ${s.category_badge}">${s.category}</span></td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="openEditModal(${s.id})" title="Edit Record">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="openDeleteModal(${s.id}, '${escapeJs(s.student_name)}')" title="Delete Record">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tableBody.innerHTML = html;

    if (recordCountEl) {
        recordCountEl.innerText = `Showing ${startIdx + 1} to ${endIdx} of ${allStudents.length} records`;
    }

    renderPagination(totalPages);
}

function renderPagination(totalPages) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl || totalPages <= 1) {
        if (paginationEl) paginationEl.innerHTML = '';
        return;
    }

    let phtml = '';
    phtml += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage - 1})">Previous</button>
        </li>
    `;

    for (let p = 1; p <= totalPages; p++) {
        if (p === 1 || p === totalPages || (p >= currentPage - 1 && p <= currentPage + 1)) {
            phtml += `
                <li class="page-item ${p === currentPage ? 'active' : ''}">
                    <button class="page-link" onclick="changePage(${p})">${p}</button>
                </li>
            `;
        } else if (p === currentPage - 2 || p === currentPage + 2) {
            phtml += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    phtml += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <button class="page-link" onclick="changePage(${currentPage + 1})">Next</button>
        </li>
    `;

    paginationEl.innerHTML = phtml;
}

function changePage(page) {
    currentPage = page;
    renderStudentsTable();
}

function openAddModal() {
    document.getElementById('studentModalTitle').innerText = 'Add New Student Record';
    document.getElementById('studentDbId').value = '';
    document.getElementById('studentForm').reset();
    
    const modal = new bootstrap.Modal(document.getElementById('studentModal'));
    modal.show();
}

function openEditModal(dbId) {
    fetch(`/api/students/${dbId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const s = data.data;
                document.getElementById('studentModalTitle').innerText = 'Edit Student Record';
                document.getElementById('studentDbId').value = s.id;
                document.getElementById('m_student_id').value = s.student_id;
                document.getElementById('m_student_name').value = s.student_name;
                document.getElementById('m_attendance').value = s.attendance_percentage;
                document.getElementById('m_study_hours').value = s.study_hours;
                document.getElementById('m_prev_marks').value = s.previous_semester_marks;
                document.getElementById('m_assignment').value = s.assignment_marks;
                document.getElementById('m_internal').value = s.internal_marks;
                document.getElementById('m_final_marks').value = s.final_exam_marks;

                const modal = new bootstrap.Modal(document.getElementById('studentModal'));
                modal.show();
            } else {
                showNotification(data.message, 'danger');
            }
        });
}

function handleSaveStudent(e) {
    e.preventDefault();
    const dbId = document.getElementById('studentDbId').value;
    const payload = {
        student_id: document.getElementById('m_student_id').value.trim(),
        student_name: document.getElementById('m_student_name').value.trim(),
        attendance_percentage: parseFloat(document.getElementById('m_attendance').value),
        study_hours: parseFloat(document.getElementById('m_study_hours').value),
        previous_semester_marks: parseFloat(document.getElementById('m_prev_marks').value),
        assignment_marks: parseFloat(document.getElementById('m_assignment').value),
        internal_marks: parseFloat(document.getElementById('m_internal').value),
        final_exam_marks: parseFloat(document.getElementById('m_final_marks').value)
    };

    const method = dbId ? 'PUT' : 'POST';
    const url = dbId ? `/api/students/${dbId}` : '/api/students';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('studentModal'))?.hide();
            showNotification(dbId ? 'Student record updated and model retrained!' : 'Student record added and model retrained!');
            loadStudents();
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(err => showNotification('Error saving student record', 'danger'));
}

function openDeleteModal(dbId, studentName) {
    deleteStudentDbId = dbId;
    document.getElementById('deleteStudentName').innerText = studentName;
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

function handleConfirmDelete() {
    if (!deleteStudentDbId) return;

    fetch(`/api/students/${deleteStudentDbId}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            bootstrap.Modal.getInstance(document.getElementById('deleteModal'))?.hide();
            if (data.success) {
                showNotification('Student record deleted successfully.');
                loadStudents();
            } else {
                showNotification(data.message, 'danger');
            }
        });
}

function handleUploadCsv(e) {
    e.preventDefault();
    const fileInput = document.getElementById('csvFileInput');
    if (!fileInput.files.length) {
        showNotification('Please select a CSV file to upload', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const uploadBtn = document.getElementById('uploadCsvSubmitBtn');
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Uploading & Retraining...';

    fetch('/api/students/upload-csv', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up me-2"></i>Upload Dataset';
        
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('uploadCsvModal'))?.hide();
            showNotification(data.message, 'success');
            loadStudents();
        } else {
            showNotification(data.message, 'danger');
        }
    })
    .catch(err => {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up me-2"></i>Upload Dataset';
        showNotification('Error processing CSV upload', 'danger');
    });
}

function handleResetSampleData() {
    if (!confirm("Are you sure you want to reset the database to default 120 sample records?")) return;

    fetch('/api/students/reset-sample-data', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message);
                loadStudents();
            } else {
                showNotification(data.message, 'danger');
            }
        });
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function escapeJs(text) {
    if (!text) return '';
    return text.replace(/'/g, "\\'");
}

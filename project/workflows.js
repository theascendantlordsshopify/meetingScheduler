/* ========================= PROFILE DROPDOWN ============================ */
const profileBtn = document.getElementById("profileBtn");
const dropdownMenu = document.getElementById("dropdownMenu");

if (profileBtn && dropdownMenu) {
    profileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        dropdownMenu.style.display =
            dropdownMenu.style.display === "flex" ? "none" : "flex";
    });

    document.addEventListener("click", () => {
        dropdownMenu.style.display = "none";
    });
}

/* ====================== WORKFLOWS FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadWorkflows();
    setupSearch();
    setupFilters();
});

async function loadWorkflows() {
    try {
        const workflowsResponse = await window.api.getWorkflows();
        const workflows = workflowsResponse.results || workflowsResponse;
        renderWorkflows(workflows);
    } catch (error) {
        console.error('Failed to load workflows:', error);
        showError('Failed to load workflows');
    }
}

function renderWorkflows(workflows) {
    const tableBody = document.querySelector('#workflowTable tbody');
    if (!tableBody) return;

    tableBody.innerHTML = '';

    workflows.forEach(workflow => {
        const row = document.createElement('tr');
        
        const statusClass = workflow.status === 'active' ? 'status-active' : 'status-paused';
        const lastEdited = formatDate(workflow.updated_at);
        
        row.innerHTML = `
            <td>${workflow.name}</td>
            <td class="${statusClass}">${workflow.status_display}</td>
            <td>${lastEdited}</td>
            <td class="actions">
                <a href="#" onclick="editWorkflow(${workflow.id})">Edit</a> |
                <a href="#" onclick="duplicateWorkflow(${workflow.id})">Duplicate</a> |
                <a href="#" onclick="deleteWorkflow(${workflow.id})">Delete</a>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

function setupSearch() {
    const searchInput = document.getElementById('search');
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.toLowerCase();
                filterWorkflows(query);
            }, 300);
        });
    }
}

function setupFilters() {
    const statusFilter = document.getElementById('statusFilter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', (e) => {
            const status = e.target.value;
            filterWorkflowsByStatus(status);
        });
    }
}

function filterWorkflows(query) {
    const rows = document.querySelectorAll('#workflowTable tbody tr');
    
    rows.forEach(row => {
        const workflowName = row.cells[0].textContent.toLowerCase();
        
        if (workflowName.includes(query) || query === '') {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function filterWorkflowsByStatus(status) {
    const rows = document.querySelectorAll('#workflowTable tbody tr');
    
    rows.forEach(row => {
        const workflowStatus = row.cells[1].textContent.toLowerCase();
        
        if (status === 'All' || workflowStatus.includes(status.toLowerCase())) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

async function editWorkflow(workflowId) {
    try {
        // Navigate to workflow edit page or open modal
        window.location.href = `/workflow/editWorkflow.html?id=${workflowId}`;
    } catch (error) {
        console.error('Failed to edit workflow:', error);
    }
}

async function duplicateWorkflow(workflowId) {
    try {
        await window.api.duplicateWorkflow(workflowId);
        await loadWorkflows();
        showSuccess('Workflow duplicated successfully!');
    } catch (error) {
        console.error('Failed to duplicate workflow:', error);
        showError('Failed to duplicate workflow');
    }
}

async function deleteWorkflow(workflowId) {
    if (confirm('Are you sure you want to delete this workflow?')) {
        try {
            await window.api.deleteWorkflow(workflowId);
            await loadWorkflows();
            showSuccess('Workflow deleted successfully!');
        } catch (error) {
            console.error('Failed to delete workflow:', error);
            showError('Failed to delete workflow');
        }
    }
}
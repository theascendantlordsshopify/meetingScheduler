const searchInput = document.getElementById("search");
const filterSelect = document.getElementById("statusFilter");
const tableRows = document.querySelectorAll("#workflowTable tbody tr");

function filterTable() {
    const searchText = searchInput.value.toLowerCase();
    const statusFilter = filterSelect.value;

    tableRows.forEach(row => {
    const name = row.cells[0].textContent.toLowerCase();
    const status = row.cells[1].textContent;

    const matchesSearch = name.includes(searchText);
    const matchesStatus = statusFilter === "All" || status === statusFilter;

    row.style.display = matchesSearch && matchesStatus ? "" : "none";
    });
}

searchInput.addEventListener("keyup", filterTable);
filterSelect.addEventListener("change", filterTable);
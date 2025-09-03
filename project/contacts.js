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

/* ====================== CONTACTS FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadContacts();
    setupContactModal();
    setupFilters();
    setupSearch();
});

async function loadContacts() {
    try {
        const contactsResponse = await window.api.getContacts();
        const contacts = contactsResponse.results || contactsResponse;
        renderContacts(contacts);
    } catch (error) {
        console.error('Failed to load contacts:', error);
        showError('Failed to load contacts');
    }
}

function renderContacts(contacts) {
    const tbody = document.getElementById('cm-contacts-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    contacts.forEach(contact => {
        const row = document.createElement('tr');
        
        // Format tags
        const tagsHtml = contact.tags.map(tag => 
            `<span class="cm-tag-style cm-tag-${tag.name.toLowerCase()}">${tag.name}</span>`
        ).join(' ');
        
        // Format upcoming meeting
        const upcomingMeeting = contact.upcoming_meeting 
            ? `${contact.upcoming_meeting.title} - ${formatDate(contact.upcoming_meeting.date)}`
            : 'None';
        
        // Format last meeting date
        const lastMeetingDate = contact.last_meeting_date 
            ? formatDate(contact.last_meeting_date)
            : 'Never';

        row.innerHTML = `
            <td>${contact.full_name}</td>
            <td>${contact.email}</td>
            <td>${contact.company || 'N/A'}</td>
            <td>${tagsHtml}</td>
            <td>${upcomingMeeting}</td>
            <td>${lastMeetingDate}</td>
            <td>${contact.total_meetings}</td>
        `;
        
        tbody.appendChild(row);
    });
}

function setupContactModal() {
    const modal = document.getElementById("cm-new-contact-modal");
    const openBtn = document.getElementById("cm-new-contact-btn");
    const closeBtn = modal?.querySelector(".cm-close-button");
    const cancelBtn = document.getElementById("cm-cancel-new-contact");
    const form = document.getElementById("cm-new-contact-form");

    if (openBtn) {
        openBtn.addEventListener("click", () => {
            modal.style.display = "flex";
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            modal.style.display = "none";
        });
    }

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const contactData = {
                first_name: formData.get('name').split(' ')[0] || '',
                last_name: formData.get('name').split(' ').slice(1).join(' ') || '',
                email: formData.get('email'),
                company: formData.get('organization'),
                tag_ids: Array.from(formData.getAll('tags')).map(Number)
            };

            try {
                await window.api.createContact(contactData);
                modal.style.display = "none";
                form.reset();
                await loadContacts();
                showSuccess('Contact created successfully!');
            } catch (error) {
                console.error('Failed to create contact:', error);
                showError('Failed to create contact: ' + error.message);
            }
        });
    }
}

function setupFilters() {
    // Tag filter
    const tagFilterBtn = document.getElementById("cm-tag-filter-btn");
    const tagDropdown = document.getElementById("cm-tag-dropdown");

    if (tagFilterBtn) {
        tagFilterBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            tagDropdown.classList.toggle("show");
        });
    }

    // Organization filter
    const orgFilterBtn = document.getElementById("cm-organization-filter-btn");
    const orgDropdown = document.getElementById("cm-organization-dropdown");

    if (orgFilterBtn) {
        orgFilterBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            orgDropdown.classList.toggle("show");
        });
    }

    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
        document.querySelectorAll('.cm-dropdown-content').forEach(dropdown => {
            dropdown.classList.remove("show");
        });
    });
}

function setupSearch() {
    const searchInput = document.getElementById("cm-search-input");
    
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(async () => {
                const query = e.target.value.trim();
                if (query) {
                    try {
                        const results = await window.api.searchContacts(query);
                        renderContacts(results.contacts);
                    } catch (error) {
                        console.error('Search failed:', error);
                    }
                } else {
                    loadContacts();
                }
            }, 300);
        });
    }
}
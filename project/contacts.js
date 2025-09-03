// Initial dummy contacts data
const initialDummyContacts = [
    {
        name: "Sophia Bennett",
        email: "sophia.bennett@example.com",
        organization: "Tech Innovators Inc.",
        tags: ["Client"],
        upcomingMeeting: { date: "Oct 28, 2024", title: "Project Kickoff" },
        lastMeetingDate: "Sep 15, 2024",
        totalMeetings: 3
    },
    {
        name: "Ethan Carter",
        email: "ethan.carter@example.com",
        organization: "Global Solutions Ltd.",
        tags: ["Partner"],
        upcomingMeeting: { date: "Nov 10, 2024", title: "Quarterly Review" },
        lastMeetingDate: "Oct 5, 2024",
        totalMeetings: 4
    },
    {
        name: "Olivia Davis",
        email: "olivia.davis@example.com",
        organization: "Creative Minds Agency",
        tags: ["Internal"],
        upcomingMeeting: { date: "Oct 28, 2024", title: "Team Sync" },
        lastMeetingDate: "Sep 20, 2024",
        totalMeetings: 2
    },
    {
        name: "Liam Foster",
        email: "liam.foster@example.com",
        organization: "Data Dynamics Corp.",
        tags: ["Client"],
        upcomingMeeting: { date: "Nov 5, 2024", title: "Strategy Session" },
        lastMeetingDate: "Oct 1, 2024",
        totalMeetings: 4
    },
    {
        name: "Ava Green",
        email: "ava.green@example.com",
        organization: "Marketing Masters LLC",
        tags: ["Partner"],
        upcomingMeeting: { date: "Oct 27, 2024", title: "Campaign Planning" },
        lastMeetingDate: "Sep 25, 2024",
        totalMeetings: 3
    },
    {
        name: "Noah Harris",
        email: "noah.harris@example.com",
        organization: "Financial Futures Group",
        tags: ["Client"],
        upcomingMeeting: { date: "Nov 12, 2024", title: "Investment Review" },
        lastMeetingDate: "Oct 8, 2024",
        totalMeetings: 6
    },
    {
        name: "Isabella Jones",
        email: "isabella.jones@example.com",
        organization: "Software Solutions Co.",
        tags: ["Internal"],
        upcomingMeeting: { date: "Oct 30, 2024", title: "Product Update" },
        lastMeetingDate: "Sep 22, 2024",
        totalMeetings: 4
    },
    {
        name: "Jackson King",
        email: "jackson.king@example.com",
        organization: "Design Dynamics Studio",
        tags: ["Partner"],
        upcomingMeeting: { date: "Nov 8, 2024", title: "Creative Briefing" },
        lastMeetingDate: "Oct 3, 2024",
        totalMeetings: 4
    },
    {
        name: "Mia Lewis",
        email: "mia.lewis@example.com",
        organization: "Healthcare Innovations Inc.",
        tags: ["Client"],
        upcomingMeeting: { date: "Oct 29, 2024", title: "Partnership Discussion" },
        lastMeetingDate: "Sep 28, 2024",
        totalMeetings: 3
    },
    {
        name: "Aiden Morgan",
        email: "aiden.morgan@example.com",
        organization: "Consulting Strategies LLC",
        tags: ["Partner"],
        upcomingMeeting: { date: "Nov 15, 2024", title: "Business Development" },
        lastMeetingDate: "Oct 10, 2024",
        totalMeetings: 5
    }
];

// Load contacts from local storage or use dummy data if not found
let contacts = [];
try {
    const storedContacts = localStorage.getItem('contacts');
    if (storedContacts) {
        contacts = JSON.parse(storedContacts);
    } else {
        contacts = [...initialDummyContacts]; // Use initial dummy data if nothing in local storage
    }
} catch (e) {
    console.error("Error loading contacts from local storage:", e);
    contacts = [...initialDummyContacts]; // Fallback to dummy data on error
}

// Function to save contacts to local storage
function saveContactsToLocalStorage() {
    try {
        localStorage.setItem('contacts', JSON.stringify(contacts));
    } catch (e) {
        console.error("Error saving contacts to local storage:", e);
    }
}

let currentFilters = {
    search: '',
    tags: [],
    organizations: [],
    recentActivity: []
};

// Get references to DOM elements using the new prefixed IDs
const contactsTableBody = document.getElementById('cm-contacts-table-body');
const contactSearchInput = document.getElementById('cm-search-input'); // Renamed searchInput
const tagFilterBtn = document.getElementById('cm-tag-filter-btn');
const tagDropdown = document.getElementById('cm-tag-dropdown');
const organizationFilterBtn = document.getElementById('cm-organization-filter-btn');
const organizationDropdown = document.getElementById('cm-organization-dropdown');
const recentActivityFilterBtn = document.getElementById('cm-recent-activity-filter-btn');
const recentActivityDropdown = document.getElementById('cm-recent-activity-dropdown');

const newContactBtn = document.getElementById('cm-new-contact-btn');
const newContactModal = document.getElementById('cm-new-contact-modal');
const newContactForm = document.getElementById('cm-new-contact-form');
const cancelNewContactBtn = document.getElementById('cm-cancel-new-contact');

const addToGroupBtn = document.getElementById('cm-add-to-group-btn');
const addToGroupModal = document.getElementById('cm-add-to-group-modal');
const cancelAddToGroupBtn = document.getElementById('cm-cancel-add-to-group');

// Function to render contacts table
function renderContacts(filteredContacts) {
    contactsTableBody.innerHTML = ''; // Clear existing rows
    if (filteredContacts.length === 0) {
        contactsTableBody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-500">No contacts found matching your criteria.</td></tr>`;
        return;
    }

    filteredContacts.forEach(contact => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="font-medium text-gray-900">${contact.name}</td>
            <td class="text-gray-600">${contact.email}</td>
            <td class="text-gray-600">${contact.organization}</td>
            <td>
                ${contact.tags.map(tag => `<span class="cm-tag-style cm-tag-${tag.toLowerCase()}">${tag}</span>`).join('')}
            </td>
            <td class="text-gray-600">
                ${contact.upcomingMeeting ? `${contact.upcomingMeeting.date} - ${contact.upcomingMeeting.title}` : 'N/A'}
            </td>
            <td class="text-gray-600">${contact.lastMeetingDate || 'N/A'}</td>
            <td class="text-gray-600">${contact.totalMeetings}</td>
        `;
        contactsTableBody.appendChild(row);
    });
}

// Function to apply all filters and re-render
function applyFilters() {
    let filtered = [...contacts];

    // Search filter
    if (currentFilters.search) {
        const searchTerm = currentFilters.search.toLowerCase();
        filtered = filtered.filter(contact =>
            contact.name.toLowerCase().includes(searchTerm) ||
            contact.email.toLowerCase().includes(searchTerm) ||
            contact.organization.toLowerCase().includes(searchTerm)
        );
    }

    // Tag filter
    if (currentFilters.tags.length > 0) {
        filtered = filtered.filter(contact =>
            contact.tags.some(tag => currentFilters.tags.includes(tag))
        );
    }

    // Organization filter
    if (currentFilters.organizations.length > 0) {
        filtered = filtered.filter(contact =>
            currentFilters.organizations.includes(contact.organization)
        );
    }

    // Recent Activity filter (simplified for dummy data)
    if (currentFilters.recentActivity.length > 0) {
        const now = new Date();
        filtered = filtered.filter(contact => {
            if (!contact.lastMeetingDate) return false;
            const lastMeeting = new Date(contact.lastMeetingDate);
            const diffTime = Math.abs(now - lastMeeting);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (currentFilters.recentActivity.includes("Last 7 Days") && diffDays <= 7) return true;
            if (currentFilters.recentActivity.includes("Last 30 Days") && diffDays <= 30) return true;
            if (currentFilters.recentActivity.includes("Last 90 Days") && diffDays <= 90) return true;
            return false;
        });
    }

    renderContacts(filtered);
}

// Event Listeners for Search and Filters

// Search Input
contactSearchInput.addEventListener('input', (e) => { // Updated variable name here
    currentFilters.search = e.target.value;
    applyFilters();
});

// Toggle Dropdown visibility
function toggleDropdown(button, dropdown) {
    dropdown.classList.toggle('show');
    // Close other dropdowns
    document.querySelectorAll('.cm-dropdown-content').forEach(otherDropdown => {
        if (otherDropdown !== dropdown) {
            otherDropdown.classList.remove('show');
        }
    });
}

tagFilterBtn.addEventListener('click', () => toggleDropdown(tagFilterBtn, tagDropdown));
organizationFilterBtn.addEventListener('click', () => toggleDropdown(organizationFilterBtn, organizationDropdown));
recentActivityFilterBtn.addEventListener('click', () => toggleDropdown(recentActivityFilterBtn, recentActivityDropdown));

// Close dropdowns when clicking outside
window.addEventListener('click', (e) => {
    if (!tagFilterBtn.contains(e.target) && !tagDropdown.contains(e.target)) {
        tagDropdown.classList.remove('show');
    }
    if (!organizationFilterBtn.contains(e.target) && !organizationDropdown.contains(e.target)) {
        organizationDropdown.classList.remove('show');
    }
    if (!recentActivityFilterBtn.contains(e.target) && !recentActivityDropdown.contains(e.target)) {
        recentActivityDropdown.classList.remove('show');
    }
});

// Tag Checkbox Listener
tagDropdown.addEventListener('change', (e) => {
    if (e.target.classList.contains('cm-tag-checkbox')) {
        currentFilters.tags = Array.from(tagDropdown.querySelectorAll('.cm-tag-checkbox:checked')).map(cb => cb.value);
        applyFilters();
    }
});

// Organization Checkbox Listener (Dynamically populated)
organizationDropdown.addEventListener('change', (e) => {
    if (e.target.classList.contains('cm-organization-checkbox')) {
        currentFilters.organizations = Array.from(organizationDropdown.querySelectorAll('.cm-organization-checkbox:checked')).map(cb => cb.value);
        applyFilters();
    }
});

// Recent Activity Checkbox Listener
recentActivityDropdown.addEventListener('change', (e) => {
    if (e.target.classList.contains('cm-activity-checkbox')) {
        currentFilters.recentActivity = Array.from(recentActivityDropdown.querySelectorAll('.cm-activity-checkbox:checked')).map(cb => cb.value);
        applyFilters();
    }
});

// Populate Organization Filter Dropdown
function populateOrganizationFilter() {
    // Get unique organizations from the current contacts array
    const organizations = [...new Set(contacts.map(contact => contact.organization))].sort();
    organizationDropdown.innerHTML = ''; // Clear existing options
    organizations.forEach(org => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" value="${org}" class="cm-organization-checkbox"> ${org}`;
        organizationDropdown.appendChild(label);
    });
}

// Modal Functionality
function openModal(modal) {
    modal.style.display = 'flex';
}

function closeModal(modal) {
    modal.style.display = 'none';
}

newContactBtn.addEventListener('click', () => openModal(newContactModal));
newContactModal.querySelector('.cm-close-button').addEventListener('click', () => closeModal(newContactModal));
cancelNewContactBtn.addEventListener('click', () => closeModal(newContactModal));

addToGroupBtn.addEventListener('click', () => openModal(addToGroupModal));
addToGroupModal.querySelector('.cm-close-button').addEventListener('click', () => closeModal(addToGroupModal));
cancelAddToGroupBtn.addEventListener('click', () => closeModal(addToGroupModal));

// Close modals if clicking outside content
window.addEventListener('click', (event) => {
    if (event.target === newContactModal) {
        closeModal(newContactModal);
    }
    if (event.target === addToGroupModal) {
        closeModal(addToGroupModal);
    }
});

// Form Validation for New Contact
newContactForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent default form submission

    let isValid = true;

    // Validate Name
    const nameInput = document.getElementById('cm-contact-name');
    const nameError = document.getElementById('cm-name-error');
    if (nameInput.value.trim() === '') {
        nameError.style.display = 'block';
        isValid = false;
    } else {
        nameError.style.display = 'none';
    }

    // Validate Email
    const emailInput = document.getElementById('cm-contact-email');
    const emailError = document.getElementById('cm-email-error');
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(emailInput.value.trim())) {
        emailError.style.display = 'block';
        isValid = false;
    } else {
        emailError.style.display = 'none';
    }

    // Validate Tags (at least one selected)
    const tagsSelect = document.getElementById('cm-contact-tags');
    const tagsError = document.getElementById('cm-tags-error');
    if (tagsSelect.selectedOptions.length === 0) {
        tagsError.style.display = 'block';
        isValid = false;
    } else {
        tagsError.style.display = 'none';
    }

    if (isValid) {
        // Create new contact object
        const newContact = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            organization: document.getElementById('cm-contact-organization').value.trim(),
            tags: Array.from(tagsSelect.selectedOptions).map(option => option.value),
            upcomingMeeting: null, // New contacts won't have an upcoming meeting initially
            lastMeetingDate: null,
            totalMeetings: 0
        };

        // Add to contacts array
        contacts.push(newContact);
        saveContactsToLocalStorage(); // Save updated contacts to local storage
        console.log('New Contact Added:', newContact);

        // Re-render table with new contact
        applyFilters();
        populateOrganizationFilter(); // Re-populate organization filter to include new org if any

        // Close modal and reset form
        closeModal(newContactModal);
        newContactForm.reset();
        // Hide error messages after successful submission
        nameError.style.display = 'none';
        emailError.style.display = 'none';
        tagsError.style.display = 'none';
    }
});

// Initial render on page load
document.addEventListener('DOMContentLoaded', () => {
    populateOrganizationFilter(); // Populate organizations based on initial or loaded data
    applyFilters(); // Render initial contacts
});

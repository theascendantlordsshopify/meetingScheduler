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

/* ====================== EVENT TYPES FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadEventTypes();
    setupEventTypeModal();
    setupViewToggle();
});

async function loadEventTypes() {
    try {
        const eventTypesResponse = await window.api.getEventTypes();
        const eventTypes = eventTypesResponse.results || eventTypesResponse;
        renderEventTypes(eventTypes);
    } catch (error) {
        console.error('Failed to load event types:', error);
        showError('Failed to load event types');
    }
}

function renderEventTypes(eventTypes) {
    const container = document.querySelector('.event-cards');
    if (!container) return;

    container.innerHTML = '';

    eventTypes.forEach(eventType => {
        const card = document.createElement('div');
        card.className = 'event-card';
        
        card.innerHTML = `
            <img src="${eventType.image || 'images/event1.jpg'}" alt="${eventType.name}" />
            <div class="event-content">
                <h4 class="event-title">${eventType.name}</h4>
                <p class="event-duration">${eventType.duration} min</p>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function setupEventTypeModal() {
    const modal = document.getElementById("newEventModal");
    const openBtn = document.getElementById("openModalBtn");
    const closeBtn = document.getElementById("closeModal");
    const createBtn = document.getElementById("createEventBtn");

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

    if (createBtn) {
        createBtn.addEventListener("click", async () => {
            const title = document.getElementById("eventTitle").value;
            const duration = document.getElementById("eventDuration").value;
            const imageFile = document.getElementById("eventImage").files[0];

            if (!title || !duration) {
                alert("Please fill in all fields.");
                return;
            }

            try {
                // Parse duration to minutes
                const durationInMinutes = parseDurationToMinutes(duration);
                
                // Create event type via API
                const eventTypeData = {
                    name: title,
                    duration: durationInMinutes,
                    description: `${title} event`,
                    location_type: 'zoom',
                    color: '#1D9CA4'
                };
                
                // If image is provided, we'd need to handle file upload
                // For now, we'll create without image and add it later
                await window.api.createEventType(eventTypeData);
                
                // Reload event types
                await loadEventTypes();
                
                // Close modal and reset form
                modal.style.display = "none";
                document.getElementById("eventTitle").value = "";
                document.getElementById("eventDuration").value = "";
                document.getElementById("eventImage").value = "";
                
                showSuccess('Event type created successfully!');
            } catch (error) {
                console.error('Failed to create event type:', error);
                alert('Failed to create event type: ' + error.message);
            }
        });
    }
}

function setupViewToggle() {
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const eventCards = document.querySelector('.event-cards');

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (btn.textContent === 'List') {
                eventCards.classList.add('list-view');
            } else {
                eventCards.classList.remove('list-view');
            }
        });
    });
}

function parseDurationToMinutes(durationStr) {
    const lower = durationStr.toLowerCase();
    if (lower.includes('hour')) {
        const hours = parseFloat(lower);
        return hours * 60;
    } else if (lower.includes('min')) {
        return parseInt(lower);
    } else {
        // Try to parse as number (assume minutes)
        const num = parseInt(durationStr);
        return isNaN(num) ? 30 : num; // Default to 30 minutes
    }
}
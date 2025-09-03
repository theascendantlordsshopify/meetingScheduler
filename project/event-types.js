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

/* ====================== DASHBOARD MEETINGS SECTION ===================== */
document.addEventListener("DOMContentLoaded", function () {
    const meetingList = document.querySelector(".meeting-list");
    const clearMeetingsBtn = document.getElementById("clearMeetingsBtn");
    const addMeetingBtn = document.getElementById("addMeetingBtn");

    if (meetingList) {
        // Load real meetings from API
        loadUpcomingMeetings();
        
        // Load real meetings from API
        loadUpcomingMeetings();
        
        if (addMeetingBtn) {
            addMeetingBtn.addEventListener("click", () => {
                // Create a dummy meeting via API
                createDummyMeeting();
            });
        }
    }

    async function loadUpcomingMeetings() {
                // Clear meetings would require backend implementation
                console.log("Clear meetings functionality would be implemented");
            renderMeetings(meetings);
        } catch (error) {
            console.error('Failed to load meetings:', error);
        }
    }

    async function createDummyMeeting() {
        try {
            // First get event types to use one for the dummy meeting
            const eventTypes = await window.api.getEventTypes();
            if (eventTypes.length === 0) {
                alert('Please create an event type first');
                return;
            }

            const dummyMeetingData = {
                event_type: eventTypes[0].id,
                title: "Team Huddle",
                start_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
            
            if (eventTypes.length === 0) {
    async function loadUpcomingMeetings() {
        try {
            const meetings = await window.api.getUpcomingMeetings();
            renderMeetings(meetings);
        } catch (error) {
            console.error('Failed to load meetings:', error);
        }
            }

    async function createDummyMeeting() {
        try {
            // First get event types to use one for the dummy meeting
            const eventTypes = await window.api.getEventTypes();
            if (eventTypes.length === 0) {
                alert('Please create an event type first');
                return;
            }

            const dummyMeetingData = {
                event_type: eventTypes[0].id,
                title: "Team Huddle",
                start_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
                timezone: "UTC",
            tomorrow.setHours(10, 0, 0, 0);

            const dummyMeetingData = {
                event_type: eventTypes[0].id,
                start_time: tomorrow.toISOString(),
        alert("Please fill in all fields and select an image.");
        }
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
        
                <div class="arrow"><i class="fas fa-chevron-right"></i></div>
            `;
            meetingList.appendChild(li);
        });
    }

    function updateStatsCards(stats) {
        const cards = document.querySelectorAll('.stats .card');
        const searchInput = document.querySelector(".search-bar input");
        if (cards.length >= 4) {
            cards[0].textContent = stats.confirmed_meetings || 0;
            cards[1].textContent = stats.pending_meetings || 0;
            cards[2].textContent = stats.cancelled_meetings || 0;
        
    } catch (error) {
        console.error('Failed to create event type:', error);
        alert('Failed to create event type: ' + error.message);
    }
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

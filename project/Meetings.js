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

/* ====================== MEETINGS FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadMeetings();
    setupFilters();
});

async function loadMeetings() {
    try {
        const meetingsResponse = await window.api.getMeetings();
        const meetings = meetingsResponse.results || meetingsResponse;
        renderMeetings(meetings);
    } catch (error) {
        console.error('Failed to load meetings:', error);
        showError('Failed to load meetings');
    }
}

function renderMeetings(meetings) {
    const meetingList = document.querySelector('.meeting-list');
    if (!meetingList) return;

    meetingList.innerHTML = '';

    meetings.forEach(meeting => {
        const meetingDiv = document.createElement('div');
        meetingDiv.className = 'meeting';
        
        // Get appropriate icon based on event type or meeting type
        const icon = getMeetingIcon(meeting.event_type_name);
        const meetingTime = formatDateTime(meeting.start_time);
        
        meetingDiv.innerHTML = `
            <div class="meeting-left">
                <div class="icon-circle">${icon}</div>
                <div class="meeting-details">
                    <div class="meeting-title">${meeting.title}</div>
                    <div class="meeting-time">${meetingTime}</div>
                </div>
            </div>
            <div class="view-button">
                <a href="#" onclick="viewMeeting(${meeting.id})">View</a>
            </div>
        `;
        
        meetingList.appendChild(meetingDiv);
    });
}

function getMeetingIcon(eventTypeName) {
    const name = eventTypeName?.toLowerCase() || '';
    if (name.includes('demo')) return '🖥';
    if (name.includes('review')) return '📝';
    if (name.includes('1:1') || name.includes('one')) return '👤';
    if (name.includes('team')) return '👥';
    if (name.includes('call')) return '📞';
    return '📅'; // Default icon
}

function setupFilters() {
    const filterSelects = document.querySelectorAll('.filters select');
    
    filterSelects.forEach(select => {
        select.addEventListener('change', async () => {
            // Implement filtering logic
            await loadMeetings();
        });
    });
}

async function viewMeeting(meetingId) {
    try {
        const meeting = await window.api.getMeeting(meetingId);
        // Implement meeting detail view
        console.log('Meeting details:', meeting);
    } catch (error) {
        console.error('Failed to load meeting details:', error);
    }
}
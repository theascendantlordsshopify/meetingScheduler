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

/* ====================== AVAILABILITY FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadAvailabilityData();
    setupAvailabilityControls();
    setupTimeZoneDetection();
    setupSaveButton();
});

async function loadAvailabilityData() {
    try {
        const overview = await window.api.getAvailabilityOverview();
        renderWeeklyAvailability(overview.weekly_availability);
        renderBufferTime(overview.buffer_time);
        renderTimeZoneSettings(overview.timezone_settings);
        renderCalendarIntegrations(overview.calendar_integrations);
        renderDateOverrides(overview.date_overrides);
    } catch (error) {
        console.error('Failed to load availability data:', error);
        showError('Failed to load availability settings');
    }
}

function renderWeeklyAvailability(weeklyAvailability) {
    const weeksWrapper = document.getElementById('weeks-wrapper');
    if (!weeksWrapper) return;

    weeksWrapper.innerHTML = '';

    // Group availability by weekday
    const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const availabilityByDay = {};

    weeklyAvailability.forEach(slot => {
        if (!availabilityByDay[slot.weekday]) {
            availabilityByDay[slot.weekday] = [];
        }
        availabilityByDay[slot.weekday].push(slot);
    });

    weekdays.forEach((dayName, index) => {
        const daySlots = availabilityByDay[index] || [];
        const dayBlock = createDayBlock(dayName, index, daySlots);
        weeksWrapper.appendChild(dayBlock);
    });
}

function createDayBlock(dayName, weekdayIndex, slots) {
    const dayBlock = document.createElement('div');
    dayBlock.className = 'day-block';
    
    const timeRange = slots.length > 0 
        ? `${slots[0].start_time} - ${slots[slots.length - 1].end_time}`
        : 'Unavailable';

    dayBlock.innerHTML = `
        <div class="day-header">
            <div class="header">
                <span>${dayName}</span>
                <label class="toggle">
                    <input type="checkbox" ${slots.length > 0 ? 'checked' : ''}>
                    <span class="slider"></span>
                </label>
            </div>
            <div class="time-range">${timeRange}</div>
            <div class="arrow">▼</div>
        </div>
        <div class="day-body">
            <div class="time-slots" id="slots-${weekdayIndex}">
                ${renderTimeSlots(slots, weekdayIndex)}
            </div>
            <button class="add-slot" onclick="addTimeSlot(${weekdayIndex})">+ Add time slot</button>
        </div>
    `;

    // Add click handler for expansion
    const header = dayBlock.querySelector('.day-header');
    header.addEventListener('click', () => {
        dayBlock.classList.toggle('expanded');
    });

    return dayBlock;
}

function renderTimeSlots(slots, weekdayIndex) {
    return slots.map((slot, index) => `
        <div class="time-select-group">
            <input type="time" value="${slot.start_time}" onchange="updateTimeSlot(${weekdayIndex}, ${index}, 'start', this.value)">
            <span>to</span>
            <input type="time" value="${slot.end_time}" onchange="updateTimeSlot(${weekdayIndex}, ${index}, 'end', this.value)">
            <button class="delete-slot" onclick="deleteTimeSlot(${weekdayIndex}, ${index})">×</button>
        </div>
    `).join('');
}

function renderBufferTime(bufferTime) {
    if (!bufferTime) return;

    const beforeSelect = document.getElementById('before-event');
    const afterSelect = document.getElementById('after-event');
    const lunchStart = document.getElementById('lunch-start');
    const lunchEnd = document.getElementById('lunch-end');

    if (beforeSelect) beforeSelect.value = bufferTime.before_meeting || '';
    if (afterSelect) afterSelect.value = bufferTime.after_meeting || '';
    if (lunchStart) lunchStart.value = bufferTime.lunch_start_time || '';
    if (lunchEnd) lunchEnd.value = bufferTime.lunch_end_time || '';
}

function renderTimeZoneSettings(timezoneSettings) {
    if (!timezoneSettings) return;

    const timezoneSelect = document.getElementById('timezone');
    if (timezoneSelect) {
        // Populate timezone options
        populateTimezones();
        timezoneSelect.value = timezoneSettings.timezone || 'UTC';
    }
}

function renderCalendarIntegrations(integrations) {
    const googleCheckbox = document.getElementById('google-calendar');
    const outlookCheckbox = document.getElementById('outlook-calendar');
    const googleStatus = document.getElementById('google-status');
    const outlookStatus = document.getElementById('outlook-status');

    const googleIntegration = integrations.find(i => i.provider_name === 'Google Calendar');
    const outlookIntegration = integrations.find(i => i.provider_name === 'Outlook Calendar');

    if (googleCheckbox && googleStatus) {
        googleCheckbox.checked = !!googleIntegration;
        googleStatus.textContent = googleIntegration ? 'Connected' : 'Not Connected';
    }

    if (outlookCheckbox && outlookStatus) {
        outlookCheckbox.checked = !!outlookIntegration;
        outlookStatus.textContent = outlookIntegration ? 'Connected' : 'Not Connected';
    }
}

function renderDateOverrides(overrides) {
    const container = document.getElementById('exceptions-container');
    if (!container) return;

    container.innerHTML = '';

    overrides.forEach((override, index) => {
        const row = document.createElement('div');
        row.className = 'exception-row';
        
        row.innerHTML = `
            <input type="date" value="${override.date}">
            <input type="checkbox" id="unavailable-${index}" ${!override.is_available ? 'checked' : ''}>
            <label for="unavailable-${index}">Mark as unavailable</label>
            <button onclick="removeException(${index})">Remove</button>
        `;
        
        container.appendChild(row);
    });
}

function setupAvailabilityControls() {
    // Add exception button
    const addExceptionBtn = document.getElementById('add-exception');
    if (addExceptionBtn) {
        addExceptionBtn.addEventListener('click', addNewException);
    }
}

function setupTimeZoneDetection() {
    // Auto-detect timezone
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const hint = document.getElementById('timezoneHint');
    if (hint) {
        hint.textContent = `Auto-detected: ${userTimezone}. You can override this setting.`;
    }
}

function setupSaveButton() {
    const saveBtn = document.getElementById('save-publish');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAvailabilitySettings);
    }
}

async function saveAvailabilitySettings() {
    try {
        // Collect all availability data
        const availabilityData = collectAvailabilityData();
        
        // Save to backend
        await window.api.updateWeeklyAvailability(availabilityData.weekly);
        await window.api.updateBufferTime(availabilityData.buffer);
        
        showSuccess('Availability settings saved successfully!');
    } catch (error) {
        console.error('Failed to save availability:', error);
        showError('Failed to save availability settings');
    }
}

function collectAvailabilityData() {
    // This would collect all the form data and format it for the API
    // Implementation would depend on the specific form structure
    return {
        weekly: [],
        buffer: {}
    };
}

function populateTimezones() {
    const timezoneSelect = document.getElementById('timezone');
    if (!timezoneSelect) return;

    const commonTimezones = [
        'UTC',
        'America/New_York',
        'America/Chicago',
        'America/Denver',
        'America/Los_Angeles',
        'Europe/London',
        'Europe/Paris',
        'Europe/Berlin',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Kolkata',
        'Australia/Sydney'
    ];

    timezoneSelect.innerHTML = '';
    commonTimezones.forEach(tz => {
        const option = document.createElement('option');
        option.value = tz;
        option.textContent = tz.replace('_', ' ');
        timezoneSelect.appendChild(option);
    });
}

function addNewException() {
    const container = document.getElementById('exceptions-container');
    const index = container.children.length;
    
    const row = document.createElement('div');
    row.className = 'exception-row';
    
    row.innerHTML = `
        <input type="date">
        <input type="checkbox" id="unavailable-${index}">
        <label for="unavailable-${index}">Mark as unavailable</label>
        <button onclick="removeException(${index})">Remove</button>
    `;
    
    container.appendChild(row);
}

function removeException(index) {
    const container = document.getElementById('exceptions-container');
    const rows = container.querySelectorAll('.exception-row');
    if (rows[index]) {
        rows[index].remove();
    }
}

function addTimeSlot(weekdayIndex) {
    const slotsContainer = document.getElementById(`slots-${weekdayIndex}`);
    const newSlot = document.createElement('div');
    newSlot.className = 'time-select-group';
    
    const slotIndex = slotsContainer.children.length;
    newSlot.innerHTML = `
        <input type="time" value="09:00" onchange="updateTimeSlot(${weekdayIndex}, ${slotIndex}, 'start', this.value)">
        <span>to</span>
        <input type="time" value="17:00" onchange="updateTimeSlot(${weekdayIndex}, ${slotIndex}, 'end', this.value)">
        <button class="delete-slot" onclick="deleteTimeSlot(${weekdayIndex}, ${slotIndex})">×</button>
    `;
    
    slotsContainer.appendChild(newSlot);
}

function deleteTimeSlot(weekdayIndex, slotIndex) {
    const slotsContainer = document.getElementById(`slots-${weekdayIndex}`);
    const slots = slotsContainer.querySelectorAll('.time-select-group');
    if (slots[slotIndex]) {
        slots[slotIndex].remove();
    }
}

function updateTimeSlot(weekdayIndex, slotIndex, type, value) {
    // Update the time slot data
    console.log(`Updated ${type} time for weekday ${weekdayIndex}, slot ${slotIndex}: ${value}`);
}
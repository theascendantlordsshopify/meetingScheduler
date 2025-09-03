// ===================================================
// ---------------- Per-Day Availability--------------
const daysFull = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function createTimeSlot(start = "09:00", end = "12:00", body, restoreBtn, addBtn) {
    const slot = document.createElement("div");
    slot.classList.add("time-select-group");

    const startInput = document.createElement("input");
    startInput.type = "time";
    startInput.value = start;

    const endInput = document.createElement("input");
    endInput.type = "time";
    endInput.value = end;

    const delBtn = document.createElement("button");
    delBtn.className = "delete-slot";
    delBtn.innerHTML = "&times;";
    delBtn.onclick = () => {
        slot.remove();
        checkOverlaps();
        if (body.querySelectorAll(".time-select-group").length === 0) {
            restoreBtn.style.display = "inline-block";
            addBtn.style.display = "none";
        }
    };

    slot.appendChild(startInput);
    slot.appendChild(document.createTextNode(" to "));
    slot.appendChild(endInput);
    slot.appendChild(delBtn);

    startInput.addEventListener("input", checkOverlaps);
    endInput.addEventListener("input", checkOverlaps);

    return slot;
}

function createDayBlock(day) {
    const block = document.createElement("div");
    block.className = "day-block";

    const header = document.createElement("div");
    header.className = "day-header";

    const dayName = document.createElement("span");
    dayName.textContent = day;

    const arrow = document.createElement("span");
    arrow.className = "arrow";
    arrow.textContent = "▾";

    header.appendChild(dayName);
    header.appendChild(arrow);
    block.appendChild(header);

    const body = document.createElement("div");
    body.className = "day-body";

    const addBtn = document.createElement("button");
    addBtn.className = "add-slot";
    addBtn.textContent = "Add another time slot";

    const restoreBtn = document.createElement("button");
    restoreBtn.className = "add-slot";
    restoreBtn.textContent = "Add a time slot";
    restoreBtn.style.display = "none";

    addBtn.onclick = () => {
        const newSlot = createTimeSlot("09:00", "12:00", body, restoreBtn, addBtn);
        body.insertBefore(newSlot, addBtn);
        checkOverlaps();
    };

    restoreBtn.onclick = () => {
        const newSlot = createTimeSlot("09:00", "12:00", body, restoreBtn, addBtn);
        body.insertBefore(newSlot, restoreBtn);
        restoreBtn.style.display = "none";
        addBtn.style.display = "inline-block";
        checkOverlaps();
    };

    // Default slot
    body.appendChild(createTimeSlot("09:00", "12:00", body, restoreBtn, addBtn));
    body.appendChild(addBtn);
    body.appendChild(restoreBtn);

    header.onclick = () => block.classList.toggle("expanded");

    block.appendChild(body);
    return block;
}

function checkOverlaps() {
    document.querySelectorAll(".day-body").forEach(body => {
        body.querySelectorAll(".overlap-msg").forEach(msg => msg.remove());

        const slots = Array.from(body.querySelectorAll(".time-select-group")).map(slot => {
            const start = parseTime(slot.querySelectorAll("input")[0].value);
            const end = parseTime(slot.querySelectorAll("input")[1].value);
            return { start, end, el: slot };
        });

        for (let i = 0; i < slots.length; i++) {
            for (let j = i + 1; j < slots.length; j++) {
                if (slots[i].start < slots[j].end && slots[j].start < slots[i].end) {
                    showOverlap(slots[i].el);
                    showOverlap(slots[j].el);
                }
            }
        }
    });
}

function parseTime(t) {
    const [h, m] = t.split(":").map(Number);
    return h * 60 + m;
}

function showOverlap(el) {
    const msg = document.createElement("div");
    msg.className = "overlap-msg";
    msg.textContent = "Times overlap with another set of times.";
    el.insertAdjacentElement("afterend", msg);
}

function addWeek() {
    const weekDiv = document.createElement("div");
    weekDiv.className = "week-container";

    // Remove Week Button
    const removeWeekBtn = document.createElement("button");
    removeWeekBtn.className = "remove-week-btn";
    removeWeekBtn.textContent = "Remove week";
    removeWeekBtn.onclick = () => {
        weekDiv.remove();
        if (document.querySelectorAll(".week-container").length === 0) {
            document.getElementById("add-week-btn").style.display = "block";
        }
    };

    const container = document.createElement("div");
    daysFull.forEach(day => container.appendChild(createDayBlock(day)));

    // Add Another Week Button
    const addAnotherWeekBtn = document.createElement("button");
    addAnotherWeekBtn.className = "add-another-week-btn";
    addAnotherWeekBtn.textContent = "+ Add another week";
    addAnotherWeekBtn.onclick = () => addWeek();

    weekDiv.appendChild(removeWeekBtn);
    weekDiv.appendChild(container);
    weekDiv.appendChild(addAnotherWeekBtn);

    document.getElementById("weeks-wrapper").appendChild(weekDiv);
    document.getElementById("add-week-btn").style.display = "none";
}

// Initialize with one week
addWeek();
checkOverlaps();

// =====================================================
// One-time exceptions

    let count = 1;

    document.getElementById("add-exception").addEventListener("click", function () {
        const container = document.getElementById("exceptions-container");

        const row = document.createElement("div");
        row.className = "exception-row";

        const dateInput = document.createElement("input");
        dateInput.type = "date";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = "unavailable-" + count;

        const label = document.createElement("label");
        label.setAttribute("for", "unavailable-" + count);
        label.textContent = "Mark as unavailable";

        row.appendChild(dateInput);
        row.appendChild(checkbox);
        row.appendChild(label);

        container.appendChild(row);

        count++;
    });

// =====================================================         
// Populate Time Zone Dropdown
const timezoneSelect = document.getElementById('timezone');
const timeZones = Intl.supportedValuesOf ? Intl.supportedValuesOf('timeZone') : [
    "UTC", "America/New_York", "Europe/London", "Asia/Tokyo"
];

timezoneSelect.innerHTML = "";
timeZones.forEach(zone => {
    const option = document.createElement('option');
    option.value = zone;
    option.textContent = zone.replace('_', ' ');
    timezoneSelect.appendChild(option);
});

// Auto-detect user time zone
const detectedTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
if (detectedTimeZone) {
    timezoneSelect.value = detectedTimeZone;
}

// =====================================================
const googleCheckbox = document.getElementById('google-calendar');
const outlookCheckbox = document.getElementById('outlook-calendar');
const googleStatus = document.getElementById('google-status');
const outlookStatus = document.getElementById('outlook-status');
const previewSwitch = document.getElementById('preview-switch');
const popup = document.getElementById('popup');
const popupText = document.getElementById('popup-text');

// Calendar checkbox logic
googleCheckbox.addEventListener('change', () => {
    if (googleCheckbox.checked) {
        googleStatus.textContent = 'Connected';
    } else {
        googleStatus.textContent = 'Disconnected';
        showPopup('Google Calendar is not connected!');
    }
});

outlookCheckbox.addEventListener('change', () => {
    if (outlookCheckbox.checked) {
        outlookStatus.textContent = 'Connected';
    } else {
        outlookStatus.textContent = 'Disconnected';
        showPopup('Outlook Calendar is not connected!');
    }
});

// Toggle Preview mode
document.getElementById('preview-toggle').addEventListener('click', () => {
    previewSwitch.classList.toggle('active');
});

function showPopup(message) {
    popupText.textContent = message;
    popup.style.display = 'block';
}

function closePopup() {
    popup.style.display = 'none';
}

document.addEventListener("DOMContentLoaded", () => {
  const saveBtn = document.getElementById("save-publish");

  saveBtn.addEventListener("click", (e) => {
    e.preventDefault();

    // === Collect field values ===
    const beforeEvent = document.getElementById("before-event").value;
    const afterEvent = document.getElementById("after-event").value;
    const lunchStart = document.getElementById("lunch-start").value;
    const lunchEnd = document.getElementById("lunch-end").value;
    const timezone = document.getElementById("timezone").value;
    const googleConnected = document.getElementById("google-calendar").checked;
    const outlookConnected = document.getElementById("outlook-calendar").checked;

    // === Validation Checks ===
    if (!beforeEvent || !afterEvent) {
      alert("⚠️ Please select buffer times (before & after event).");
      return;
    }

    if (lunchStart && lunchEnd && lunchStart >= lunchEnd) {
      alert("⚠️ Lunch break start time must be earlier than end time.");
      return;
    }

    if (!timezone) {
      alert("⚠️ Please select a time zone.");
      return;
    }

    if (!googleConnected && !outlookConnected) {
      alert("⚠️ Please connect at least one calendar (Google/Outlook).");
      return;
    }

    // === If everything is valid ===
    alert("✅ Your availability settings have been saved & published!");
  });
});

// === Popup Close Function (already in your HTML) ===
function closePopup() {
  document.getElementById("popup").style.display = "none";
}

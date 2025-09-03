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
        if (addMeetingBtn) {
            addMeetingBtn.addEventListener("click", () => {
                const dummyMeeting = {
                    title: "Team Huddle",
                    time: "Fri, Jul 19, 2:00 PM",
                };

                const meetings = getMeetings();
                meetings.push(dummyMeeting);
                saveMeetings(meetings);
                renderMeetings();
            });
        }

        if (clearMeetingsBtn) {
            clearMeetingsBtn.addEventListener("click", () => {
                localStorage.removeItem("meetings");
                renderMeetings();
            });
        }

        renderMeetings();
    }

    function getMeetings() {
        return JSON.parse(localStorage.getItem("meetings")) || [];
    }

    function saveMeetings(data) {
        localStorage.setItem("meetings", JSON.stringify(data));
    }

    function renderMeetings() {
        const meetings = getMeetings();
        const allLis = meetingList.querySelectorAll("li");
        allLis.forEach((li, index) => {
            if (index >= 4) li.remove();
        });

        meetings.forEach((meeting) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <div class="icon"><i class="fas fa-clock"></i></div>
                <div class="info"><strong>${meeting.title}</strong><br /><span>${meeting.time}</span></div>
                <div class="arrow"><i class="fas fa-chevron-right"></i></div>
            `;
            meetingList.appendChild(li);
        });
    }
});

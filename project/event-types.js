/* ======================== EVENT TYPES PAGE (Hammad) ===================== */
// Grid/List toggle
const toggleBtns = document.querySelectorAll(".toggle-btn");
const viewToggle = document.querySelector(".view-toggle");
const eventCardsContainer = document.querySelector(".event-cards");

toggleBtns.forEach((btn, index) => {
    btn.addEventListener("click", () => {
        toggleBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        // Move the active pill
        viewToggle.classList.toggle("list-active", index === 1);

        // Apply list view to cards
        if (index === 1) {
            eventCardsContainer.classList.add("list-view");
        } else {
            eventCardsContainer.classList.remove("list-view");
        }
    });
});
// Updated search for event-card structure
const searchInput = document.querySelector(".search-bar input"); // This is a different searchInput, specific to event types

searchInput?.addEventListener("input", function () {
    const query = this.value.toLowerCase();
    const cards = document.querySelectorAll(".event-card");

    cards.forEach((card) => {
        const titleElement = card.querySelector(".event-title");
        const title = titleElement?.textContent.toLowerCase() || "";

        // Show or hide the card based on title match
        if (title.includes(query)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    });
});
// === New Event Modal Logic ===
const modal = document.getElementById("newEventModal");
const openBtn = document.querySelector(".add-event-type-btn");
const closeBtn = document.getElementById("closeModal");

openBtn.addEventListener("click", () => {
    modal.style.display = "flex";
});

closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
});

// Optional: Close modal if user clicks outside
window.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.style.display = "none";
    }
});

// === Create New Event ===
const createBtn = document.getElementById("createEventBtn");

createBtn.addEventListener("click", () => {
    const title = document.getElementById("eventTitle").value.trim();
    const duration = document.getElementById("eventDuration").value.trim();
    const imageInput = document.getElementById("eventImage");
    const imageFile = imageInput.files[0];

    // Using a custom message box instead of alert()
    if (!title || !duration || !imageFile) {
        // You would typically implement a custom modal or message display here
        // For demonstration, we'll log to console or use a simple div
        console.error("Please fill in all fields and select an image.");
        // Example of a simple message div (requires HTML element with id="messageBox")
        const messageBox = document.getElementById('messageBox');
        if (messageBox) {
            messageBox.textContent = "Please fill in all fields and select an image.";
            messageBox.style.display = 'block';
            setTimeout(() => messageBox.style.display = 'none', 3000); // Hide after 3 seconds
        }
        return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
        const imageUrl = e.target.result;

        // Create a new card
        const newCard = document.createElement("div");
        newCard.className = "event-card";

        newCard.innerHTML = `
            <img src="${imageUrl}" alt="${title}" />
            <div class="event-content">
                <h4 class="event-title">${title}</h4>
                <p class="event-duration">${duration}</p>
            </div>
        `;

        eventCardsContainer.appendChild(newCard);
        modal.style.display = "none";

        // Clear modal inputs
        document.getElementById("eventTitle").value = "";
        document.getElementById("eventDuration").value = "";
        imageInput.value = "";

        // Re-apply search if active
        if (searchInput.value.trim() !== "") {
            const event = new Event("input");
            searchInput.dispatchEvent(event);
        }
    };

    reader.readAsDataURL(imageFile);
});
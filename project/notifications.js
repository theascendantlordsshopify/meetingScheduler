// Switch active tab
const tabs = document.querySelectorAll(".tab");
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
  });
});

// Mark all as read
function markAllRead() {
  alert("All notifications marked as read ✅");
}

// === SEARCH FUNCTIONALITY FOR NOTIFICATIONS ===
document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.querySelector(".search-bar");
  const notifications = document.querySelectorAll(".notification-card");

  searchInput.addEventListener("keyup", () => {
    const query = searchInput.value.toLowerCase();

    notifications.forEach(card => {
      const title = card.querySelector(".title").textContent.toLowerCase();
      const desc = card.querySelector(".desc").textContent.toLowerCase();

      if (title.includes(query) || desc.includes(query)) {
        card.style.display = "flex"; // Show matching
      } else {
        card.style.display = "none"; // Hide non-matching
      }
    });
  });
});

// integrations.js

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.querySelector(".search-bar");
  const cards = document.querySelectorAll(".card");

  searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase().trim();

    cards.forEach((card) => {
      const title = card.querySelector("h3").textContent.toLowerCase();
      const description = card.querySelector("p").textContent.toLowerCase();

      if (title.includes(query) || description.includes(query)) {
        card.style.display = "block"; // show matching card
      } else {
        card.style.display = "none"; // hide non-matching card
      }
    });
  });
});

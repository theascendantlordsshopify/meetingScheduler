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

/* ====================== INTEGRATIONS FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadIntegrations();
    setupSearch();
    setupTags();
});

async function loadIntegrations() {
    try {
        const [providers, userIntegrations, recentlyConnected] = await Promise.all([
            window.api.getIntegrationProviders(),
            window.api.getUserIntegrations(),
            window.api.getRecentlyConnected()
        ]);
        
        renderRecentlyConnected(recentlyConnected.integrations);
        renderAllIntegrations(providers, userIntegrations);
    } catch (error) {
        console.error('Failed to load integrations:', error);
        showError('Failed to load integrations');
    }
}

function renderRecentlyConnected(recentIntegrations) {
    const recentSection = document.querySelector('h2:contains("Recently Connected")');
    if (!recentSection) return;

    const cardsContainer = recentSection.nextElementSibling;
    if (!cardsContainer) return;

    cardsContainer.innerHTML = '';

    recentIntegrations.forEach(integration => {
        const card = createIntegrationCard(integration, true);
        cardsContainer.appendChild(card);
    });
}

function renderAllIntegrations(providers, userIntegrations) {
    const allSection = document.querySelector('h2:contains("All Integrations")');
    if (!allSection) return;

    let cardsContainer = allSection.nextElementSibling;
    
    // Clear all existing cards containers after "All Integrations"
    while (cardsContainer && cardsContainer.classList.contains('cards')) {
        const nextContainer = cardsContainer.nextElementSibling;
        cardsContainer.innerHTML = '';
        cardsContainer = nextContainer;
    }

    // Group providers by category and render
    const categories = groupProvidersByCategory(providers);
    let currentContainer = allSection.nextElementSibling;

    Object.entries(categories).forEach(([category, categoryProviders]) => {
        if (!currentContainer) {
            currentContainer = document.createElement('div');
            currentContainer.className = 'cards';
            allSection.parentNode.insertBefore(currentContainer, allSection.nextSibling);
        }

        categoryProviders.forEach(provider => {
            const card = createProviderCard(provider, userIntegrations);
            currentContainer.appendChild(card);
        });

        currentContainer = currentContainer.nextElementSibling;
    });
}

function groupProvidersByCategory(providers) {
    return providers.reduce((groups, provider) => {
        const category = provider.category || 'other';
        if (!groups[category]) {
            groups[category] = [];
        }
        groups[category].push(provider);
        return groups;
    }, {});
}

function createIntegrationCard(integration, isConnected = false) {
    const card = document.createElement('div');
    card.className = 'card';
    
    card.innerHTML = `
        <img src="${integration.provider_logo || './logos/default.png'}" alt="${integration.provider_name}">
        <h3>${integration.provider_name}</h3>
        <p>${getProviderDescription(integration.provider_category)}</p>
    `;
    
    return card;
}

function createProviderCard(provider, userIntegrations) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const isConnected = userIntegrations.some(ui => ui.provider === provider.id);
    
    card.innerHTML = `
        <img src="${provider.logo_url || './logos/default.png'}" alt="${provider.name}">
        <h3>${provider.name}</h3>
        <p>${provider.description}</p>
        ${isConnected ? '<span class="connected-badge">✓ Connected</span>' : ''}
    `;
    
    if (!isConnected) {
        card.addEventListener('click', () => connectIntegration(provider.id));
    }
    
    return card;
}

function getProviderDescription(category) {
    const descriptions = {
        'calendar': 'Sync events and availability',
        'video': 'Host video meetings',
        'communication': 'Get notified about new events',
        'crm': 'Manage Customer relationships',
        'productivity': 'Organize your work',
        'automation': 'Automate tasks'
    };
    return descriptions[category] || 'Enhance your workflow';
}

async function connectIntegration(providerId) {
    try {
        await window.api.connectIntegration({
            provider_id: providerId,
            settings: {}
        });
        
        alert('Integration connected successfully!');
        await loadIntegrations(); // Reload to show updated status
    } catch (error) {
        console.error('Failed to connect integration:', error);
        alert('Failed to connect integration: ' + error.message);
    }
}

function setupSearch() {
    const searchBar = document.querySelector('.search-bar');
    
    if (searchBar) {
        searchBar.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            filterIntegrationCards(query);
        });
    }
}

function filterIntegrationCards(query) {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        
        if (title.includes(query) || description.includes(query) || query === '') {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function setupTags() {
    const tags = document.querySelectorAll('.tag');
    
    tags.forEach(tag => {
        tag.addEventListener('click', () => {
            const category = tag.textContent.toLowerCase();
            filterByCategory(category);
        });
    });
}

function filterByCategory(category) {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
        const description = card.querySelector('p').textContent.toLowerCase();
        
        if (category === 'calendar' && description.includes('calendar')) {
            card.style.display = 'block';
        } else if (category === 'video conferencing' && description.includes('video')) {
            card.style.display = 'block';
        } else if (category === 'crm' && description.includes('customer')) {
            card.style.display = 'block';
        } else if (category === 'productivity' && (description.includes('organize') || description.includes('manage'))) {
            card.style.display = 'block';
        } else if (category === 'automation' && description.includes('automate')) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}
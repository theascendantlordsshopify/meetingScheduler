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

/* ====================== NOTIFICATIONS FUNCTIONALITY ===================== */
document.addEventListener("DOMContentLoaded", function () {
    loadNotifications();
    setupTabs();
    setupSearch();
    setupMarkAllRead();
});

async function loadNotifications() {
    try {
        const notificationsResponse = await window.api.getNotifications();
        const notifications = notificationsResponse.results || notificationsResponse;
        renderNotifications(notifications);
    } catch (error) {
        console.error('Failed to load notifications:', error);
        showError('Failed to load notifications');
    }
}

function renderNotifications(notifications) {
    const container = document.querySelector('.main-wrapper');
    if (!container) return;

    // Remove existing notification cards
    const existingCards = container.querySelectorAll('.notification-card');
    existingCards.forEach(card => card.remove());

    notifications.forEach(notification => {
        const card = document.createElement('div');
        card.className = 'notification-card';
        
        const icon = getNotificationIcon(notification.category);
        
        card.innerHTML = `
            <div class="icon">${icon}</div>
            <div class="content">
                <div class="title">${notification.title}</div>
                <div class="time">${notification.time_ago}</div>
                <div class="desc">${notification.message}</div>
            </div>
            <div class="menu" onclick="showNotificationMenu(${notification.id})">⋮</div>
        `;
        
        // Add click handler to mark as read
        card.addEventListener('click', () => markAsRead(notification.id));
        
        container.appendChild(card);
    });
}

function getNotificationIcon(category) {
    const icons = {
        'meeting_updates': '<i class="fa-regular fa-calendar-days"></i>',
        'reminders': '<i class="fa-solid fa-bell"></i>',
        'cancellations': '<i class="fa-solid fa-xmark"></i>',
        'system_alerts': '<i class="fa-solid fa-triangle-exclamation"></i>'
    };
    return icons[category] || '<i class="fa-solid fa-bell"></i>';
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Load notifications for the selected category
            const category = tab.textContent.toLowerCase().replace(' ', '_');
            await loadNotificationsByCategory(category);
        });
    });
}

async function loadNotificationsByCategory(category) {
    try {
        if (category === 'all') {
            await loadNotifications();
        } else {
            const categoriesData = await window.api.getNotificationsByCategory();
            const categoryNotifications = categoriesData[category]?.notifications || [];
            renderNotifications(categoryNotifications);
        }
    } catch (error) {
        console.error('Failed to load notifications by category:', error);
    }
}

function setupSearch() {
    const searchBar = document.querySelector('.search-bar');
    
    if (searchBar) {
        let searchTimeout;
        searchBar.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.trim();
                filterNotifications(query);
            }, 300);
        });
    }
}

function filterNotifications(query) {
    const cards = document.querySelectorAll('.notification-card');
    
    cards.forEach(card => {
        const title = card.querySelector('.title').textContent.toLowerCase();
        const desc = card.querySelector('.desc').textContent.toLowerCase();
        const searchQuery = query.toLowerCase();
        
        if (title.includes(searchQuery) || desc.includes(searchQuery) || query === '') {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

function setupMarkAllRead() {
    // This function would be called by the "Mark all as read" button
    window.markAllRead = async function() {
        try {
            await window.api.markAllNotificationsRead();
            await loadNotifications();
            showSuccess('All notifications marked as read');
        } catch (error) {
            console.error('Failed to mark all as read:', error);
            showError('Failed to mark notifications as read');
        }
    };
}

async function markAsRead(notificationId) {
    try {
        await window.api.markNotificationRead(notificationId);
        // Reload notifications to reflect the change
        await loadNotifications();
    } catch (error) {
        console.error('Failed to mark notification as read:', error);
    }
}

function showNotificationMenu(notificationId) {
    // Implement notification menu (delete, mark as read, etc.)
    console.log('Show menu for notification:', notificationId);
}
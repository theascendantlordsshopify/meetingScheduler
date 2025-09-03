// API Configuration and Client
class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('authToken');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('authToken', token);
    }

    // Remove authentication token
    removeToken() {
        this.token = null;
        localStorage.removeItem('authToken');
    }

    // Get headers with authentication
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Token ${this.token}`;
        }
        
        return headers;
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Authentication methods
    async login(email, password) {
        const response = await this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        if (response.token) {
            this.setToken(response.token);
        }
        
        return response;
    }

    async register(userData) {
        const response = await this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        if (response.token) {
            this.setToken(response.token);
        }
        
        return response;
    }

    async logout() {
        await this.request('/auth/logout/', { method: 'POST' });
        this.removeToken();
    }

    async getProfile() {
        return await this.request('/auth/profile/');
    }

    async getDashboardStats() {
        return await this.request('/auth/dashboard/stats/');
    }

    // Event Types
    async getEventTypes() {
        return await this.request('/events/');
    }

    async createEventType(eventData) {
        return await this.request('/events/', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    }

    async updateEventType(id, eventData) {
        return await this.request(`/events/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(eventData)
        });
    }

    async deleteEventType(id) {
        return await this.request(`/events/${id}/`, {
            method: 'DELETE'
        });
    }

    // Meetings
    async getMeetings() {
        return await this.request('/meetings/');
    }

    async createMeeting(meetingData) {
        return await this.request('/meetings/', {
            method: 'POST',
            body: JSON.stringify(meetingData)
        });
    }

    async getMeetingStats() {
        return await this.request('/meetings/stats/');
    }

    async getUpcomingMeetings() {
        return await this.request('/meetings/upcoming/');
    }

    async confirmMeeting(id) {
        return await this.request(`/meetings/${id}/confirm/`, {
            method: 'POST'
        });
    }

    async cancelMeeting(id, reason = '') {
        return await this.request(`/meetings/${id}/cancel/`, {
            method: 'POST',
            body: JSON.stringify({ reason })
        });
    }

    // Availability
    async getAvailabilityOverview() {
        return await this.request('/availability/overview/');
    }

    async getWeeklyAvailability() {
        return await this.request('/availability/weekly/');
    }

    async updateWeeklyAvailability(availabilityData) {
        return await this.request('/availability/weekly/bulk-update/', {
            method: 'POST',
            body: JSON.stringify({ availability_data: availabilityData })
        });
    }

    async getBufferTime() {
        return await this.request('/availability/buffer-time/');
    }

    async updateBufferTime(bufferData) {
        return await this.request('/availability/buffer-time/', {
            method: 'PUT',
            body: JSON.stringify(bufferData)
        });
    }

    // Contacts
    async getContacts() {
        return await this.request('/contacts/');
    }

    async createContact(contactData) {
        return await this.request('/contacts/', {
            method: 'POST',
            body: JSON.stringify(contactData)
        });
    }

    async getContactStats() {
        return await this.request('/contacts/stats/');
    }

    async searchContacts(query) {
        return await this.request(`/contacts/search/?q=${encodeURIComponent(query)}`);
    }

    // Workflows
    async getWorkflows() {
        return await this.request('/workflows/');
    }

    async createWorkflow(workflowData) {
        return await this.request('/workflows/', {
            method: 'POST',
            body: JSON.stringify(workflowData)
        });
    }

    async getWorkflowStats() {
        return await this.request('/workflows/stats/');
    }

    // Integrations
    async getIntegrationProviders() {
        return await this.request('/integrations/providers/');
    }

    async getUserIntegrations() {
        return await this.request('/integrations/');
    }

    async connectIntegration(integrationData) {
        return await this.request('/integrations/connect/', {
            method: 'POST',
            body: JSON.stringify(integrationData)
        });
    }

    async getRecentlyConnected() {
        return await this.request('/integrations/recently-connected/');
    }

    // Notifications
    async getNotifications() {
        return await this.request('/notifications/');
    }

    async getUnreadNotifications() {
        return await this.request('/notifications/unread/');
    }

    async markNotificationRead(id) {
        return await this.request(`/notifications/${id}/read/`, {
            method: 'POST'
        });
    }

    async markAllNotificationsRead() {
        return await this.request('/notifications/mark-all-read/', {
            method: 'POST'
        });
    }

    async getNotificationsByCategory() {
        return await this.request('/notifications/categories/');
    }
}

// Create global API client instance
window.api = new APIClient();

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

function formatDateTime(dateString) {
    return `${formatDate(dateString)} — ${formatTime(dateString)}`;
}

function showError(message) {
    console.error(message);
    // You can implement a toast notification system here
    alert(`Error: ${message}`);
}

function showSuccess(message) {
    console.log(message);
    // You can implement a toast notification system here
}

// Check authentication status
function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token && !window.location.pathname.includes('login') && !window.location.pathname.includes('getStarted')) {
        window.location.href = '/screens/getStarted/login.html';
        return false;
    }
    return true;
}

// Initialize authentication check on page load
document.addEventListener('DOMContentLoaded', () => {
    if (!window.location.pathname.includes('screens/')) {
        checkAuth();
    }
});
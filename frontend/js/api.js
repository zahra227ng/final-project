// API Client Utility for Backend Communication
const API_BASE_URL = window.location.origin;

async function makeRequest(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers
    };
    
    if (body && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json().catch(() => ({}));
        
        if (!response.ok) {
            // Auto logout if token expires/invalid
            if (response.status === 401 && token) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                showNotification('Session expired. Please log in again.', 'danger');
                checkAuth(); // Redirects to login view
            }
            const errorMsg = data.message || `API Error (Status ${response.status})`;
            throw new Error(errorMsg);
        }
        
        return data;
    } catch (error) {
        console.error(`Request to ${endpoint} failed:`, error);
        throw error;
    }
}

// Global Notification utility to show toast-like notifications
function showNotification(message, type = 'success') {
    // Create notifications container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        container.style.pointerEvents = 'none';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.padding = '12px 24px';
    toast.style.borderRadius = '8px';
    toast.style.fontWeight = '600';
    toast.style.fontSize = '0.9rem';
    toast.style.color = 'white';
    toast.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    toast.style.pointerEvents = 'auto';
    toast.style.animation = 'slideIn 0.3s ease forwards';
    
    if (type === 'success') {
        toast.style.backgroundColor = 'var(--success)';
    } else if (type === 'danger') {
        toast.style.backgroundColor = 'var(--danger)';
    } else if (type === 'warning') {
        toast.style.backgroundColor = 'var(--warning)';
    } else {
        toast.style.backgroundColor = 'var(--primary)';
    }
    
    container.appendChild(toast);
    
    // Slide in keyframe injection
    if (!document.getElementById('slide-in-animation')) {
        const style = document.createElement('style');
        style.id = 'slide-in-animation';
        style.innerHTML = `
            @keyframes slideIn {
                from { transform: translateX(120%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(120%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

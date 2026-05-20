// Authentication Module
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Auth Forms Listeners
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Goal Form Listener
    const goalForm = document.getElementById('goal-form');
    if (goalForm) {
        goalForm.addEventListener('submit', handleGoalUpdate);
    }
});

function checkAuth() {
    const token = localStorage.getItem('token');
    const authContainer = document.getElementById('auth-container');
    const appContainer = document.getElementById('app-container');
    
    if (token) {
        authContainer.style.display = 'none';
        appContainer.style.display = 'grid';
        
        // Load Profile & Init Modules
        loadUserProfile();
        switchView('dashboard');
    } else {
        authContainer.style.display = 'flex';
        appContainer.style.display = 'none';
        showAuthCard('login');
    }
}

function showAuthCard(type) {
    const loginCard = document.getElementById('login-card');
    const registerCard = document.getElementById('register-card');
    
    if (type === 'login') {
        loginCard.style.display = 'block';
        registerCard.style.display = 'none';
    } else {
        loginCard.style.display = 'none';
        registerCard.style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await makeRequest('/api/auth/login', 'POST', { email, password });
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        showNotification(`Welcome back, ${response.user.username}!`, 'success');
        checkAuth();
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    if (password !== confirmPassword) {
        showNotification('Passwords do not match.', 'danger');
        return;
    }
    
    try {
        const response = await makeRequest('/api/auth/register', 'POST', { username, email, password });
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        showNotification('Registration successful! Welcome.', 'success');
        checkAuth();
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showNotification('Logged out successfully.', 'success');
    checkAuth();
}

async function handleGoalUpdate(e) {
    e.preventDefault();
    const dailyGoal = parseInt(document.getElementById('goal-minutes').value);
    
    try {
        const response = await makeRequest('/api/auth/update_goal', 'PUT', { daily_goal_minutes: dailyGoal });
        localStorage.setItem('user', JSON.stringify(response.user));
        showNotification('Daily study goal updated successfully!', 'success');
        closeModal('goal-modal');
        loadUserProfile();
        if (typeof loadAnalytics === 'function') {
            loadAnalytics();
        }
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

function loadUserProfile() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return;
    
    const user = JSON.parse(userStr);
    
    // Set text elements across app
    const headerUsername = document.getElementById('header-username');
    if (headerUsername) headerUsername.textContent = user.username;
    
    const avatar = document.getElementById('profile-avatar-char');
    if (avatar) avatar.textContent = user.username.charAt(0).toUpperCase();
    
    const sidebarUsername = document.getElementById('sidebar-username');
    if (sidebarUsername) sidebarUsername.textContent = user.username;
    
    const streakVal = document.getElementById('header-streak-value');
    if (streakVal) streakVal.textContent = user.streak;
}

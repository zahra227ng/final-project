// Dashboard View & Navigation Controller
function switchView(viewId) {
    // 1. Toggle Sidebar Active Item
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(viewId)) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 2. Toggle View Panel Active State
    const panels = document.querySelectorAll('.view-panel');
    panels.forEach(panel => {
        if (panel.id === `${viewId}-view`) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });

    // 3. Trigger Specific View Initializers
    if (viewId === 'dashboard') {
        loadDashboardData();
    } else if (viewId === 'planner') {
        if (typeof loadPlanner === 'function') loadPlanner();
    } else if (viewId === 'quiz') {
        if (typeof loadQuizView === 'function') loadQuizView();
    } else if (viewId === 'analytics') {
        if (typeof loadAnalytics === 'function') loadAnalytics();
    }
}

async function loadDashboardData() {
    try {
        const [analytics, recommendations] = await Promise.all([
            makeRequest('/api/ai/analytics'),
            makeRequest('/api/ai/recommendations')
        ]);
        
        // Populate stats metrics
        document.getElementById('dash-streak-count').textContent = `${analytics.streak} Days`;
        document.getElementById('dash-total-time').textContent = `${Math.round(analytics.total_minutes)} mins`;
        document.getElementById('dash-today-time').textContent = `${Math.round(analytics.today_minutes)} mins`;
        document.getElementById('dash-goal-text').textContent = `Goal: ${analytics.daily_goal} mins`;
        
        // Streak counter header update
        const headerStreak = document.getElementById('header-streak-value');
        if (headerStreak) headerStreak.textContent = analytics.streak;
        
        // Progress goal bar update
        const progressPercentage = Math.min(Math.round((analytics.today_minutes / analytics.daily_goal) * 100), 100);
        document.getElementById('dash-goal-percentage').textContent = `${progressPercentage}%`;
        document.getElementById('dash-goal-bar-fill').style.width = `${progressPercentage}%`;
        
        const goalBadge = document.getElementById('header-goal-badge');
        if (goalBadge) {
            goalBadge.textContent = analytics.goal_reached ? 'Goal Achieved! 🎉' : 'Study Goal In Progress';
            goalBadge.className = analytics.goal_reached ? 'goal-indicator' : 'goal-indicator warning';
            if (!analytics.goal_reached) {
                goalBadge.style.backgroundColor = 'var(--warning-light)';
                goalBadge.style.color = 'var(--warning)';
            } else {
                goalBadge.style.backgroundColor = 'var(--success-light)';
                goalBadge.style.color = 'var(--success)';
            }
        }
        
        // Render recommendations cards
        renderRecommendations(recommendations);
        
        // Render quick activity preview bar
        renderDashboardActivity(analytics.activity_breakdown);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function renderRecommendations(recs) {
    const container = document.getElementById('dashboard-recommendations');
    if (!container) return;
    
    container.innerHTML = '';
    
    recs.forEach(rec => {
        const card = document.createElement('div');
        card.className = `card recommendation-card ${rec.priority}-priority`;
        
        // CSS Style prioritization
        let priorityStyle = '';
        if (rec.priority === 'high') {
            card.style.borderLeft = '5px solid var(--danger)';
        } else if (rec.priority === 'medium') {
            card.style.borderLeft = '5px solid var(--warning)';
        } else {
            card.style.borderLeft = '5px solid var(--primary)';
        }
        
        card.innerHTML = `
            <div class="card-header" style="margin-bottom: 10px;">
                <span class="task-badge cs" style="background: var(--primary-light); color: var(--primary); font-size: 0.7rem;">${rec.category}</span>
                <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">${rec.priority} priority</span>
            </div>
            <h4 style="margin-bottom: 8px; font-size: 1rem;">${rec.title}</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">${rec.suggestion}</p>
        `;
        
        container.appendChild(card);
    });
}

function renderDashboardActivity(activities) {
    const container = document.getElementById('dashboard-activity-summary');
    if (!container) return;
    
    container.innerHTML = '';
    const keys = Object.keys(activities);
    
    if (keys.length === 0) {
        container.innerHTML = `<p style="font-size: 0.9rem; color: var(--text-muted); text-align: center; padding: 20px 0;">No activities logged yet. Start studying or complete a quiz!</p>`;
        return;
    }
    
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-bar-container';
    
    // Find maximum value to normalize scale
    const maxVal = Math.max(...Object.values(activities));
    
    keys.forEach(key => {
        const val = activities[key];
        const percent = maxVal > 0 ? (val / maxVal) * 100 : 0;
        
        const row = document.createElement('div');
        row.className = 'chart-bar-row';
        row.innerHTML = `
            <span class="chart-bar-label" style="text-transform: capitalize;">${key}</span>
            <div class="chart-bar-track">
                <div class="chart-bar-fill" style="width: ${percent}%; background: var(--primary);"></div>
            </div>
            <span class="chart-bar-value">${val} mins</span>
        `;
        chartContainer.appendChild(row);
    });
    
    container.appendChild(chartContainer);
}

// Modal Toggle Helpers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
}

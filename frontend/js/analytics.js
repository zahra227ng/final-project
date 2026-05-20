// Subject Performance & Study Analytics View Controller
async function loadAnalytics() {
    try {
        const data = await makeRequest('/api/ai/analytics');
        
        // 1. Populate Text Metrics
        document.getElementById('anal-total-hours').textContent = `${Math.round(data.total_minutes / 60 * 10) / 10} hrs`;
        document.getElementById('anal-today-mins').textContent = `${Math.round(data.today_minutes)} mins`;
        document.getElementById('anal-avg-quiz').textContent = data.quiz_stats.average_score > 0 ? `${data.quiz_stats.average_score}%` : 'N/A';
        document.getElementById('anal-streak-badge').textContent = `${data.streak} Days`;
        
        // 2. Render Vertical 7-Day History Chart
        renderWeeklyChart(data.history_breakdown);
        
        // 3. Render Subject Duration Breakdown (Horizontal Bars)
        renderSubjectBreakdownChart(data.subject_breakdown);
        
        // 4. Render Quiz Subject Averages
        renderQuizAveragesChart(data.quiz_stats.subject_averages);
        
    } catch (error) {
        showNotification('Failed to load analytics.', 'danger');
    }
}

function renderWeeklyChart(history) {
    const container = document.getElementById('anal-weekly-chart-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    const days = Object.keys(history);
    const mins = Object.values(history);
    const maxMins = Math.max(...mins, 30); // scale max value or default 30 mins
    
    // Create chart structure using flexbox/grid layout
    const chartWrapper = document.createElement('div');
    chartWrapper.style.display = 'flex';
    chartWrapper.style.justifyContent = 'space-between';
    chartWrapper.style.alignItems = 'flex-end';
    chartWrapper.style.height = '180px';
    chartWrapper.style.width = '100%';
    chartWrapper.style.padding = '0 10px';
    chartWrapper.style.marginTop = '20px';
    
    days.forEach((day, idx) => {
        const value = mins[idx];
        const heightPct = Math.min((value / maxMins) * 100, 100);
        
        const column = document.createElement('div');
        column.style.display = 'flex';
        column.style.flexDirection = 'column';
        column.style.alignItems = 'center';
        column.style.width = '12%';
        
        column.innerHTML = `
            <div style="font-size: 0.75rem; font-weight: bold; color: var(--text-secondary); margin-bottom: 6px;">${value > 0 ? value + 'm' : ''}</div>
            <div style="width: 100%; height: 130px; background: var(--bg-hover); border-radius: 6px; display: flex; align-items: flex-end; overflow: hidden;">
                <div style="width: 100%; height: ${heightPct}%; background: var(--primary); border-radius: 6px; transition: height 0.8s ease;"></div>
            </div>
            <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); margin-top: 8px;">${day}</div>
        `;
        chartWrapper.appendChild(column);
    });
    
    container.appendChild(chartWrapper);
}

function renderSubjectBreakdownChart(breakdown) {
    const container = document.getElementById('anal-subject-chart-container');
    if (!container) return;
    
    container.innerHTML = '';
    const keys = Object.keys(breakdown);
    
    if (keys.length === 0) {
        container.innerHTML = `<p style="font-size: 0.9rem; color: var(--text-muted); text-align: center; padding: 20px 0;">Start logging study time in Pomodoro to populate breakdown.</p>`;
        return;
    }
    
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-bar-container';
    
    const maxVal = Math.max(...Object.values(breakdown));
    
    keys.forEach(key => {
        const val = breakdown[key];
        const percent = maxVal > 0 ? (val / maxVal) * 100 : 0;
        
        const row = document.createElement('div');
        row.className = 'chart-bar-row';
        row.innerHTML = `
            <span class="chart-bar-label" style="text-transform: capitalize;">${key}</span>
            <div class="chart-bar-track">
                <div class="chart-bar-fill" style="width: ${percent}%; background: var(--success);"></div>
            </div>
            <span class="chart-bar-value">${val} mins</span>
        `;
        chartContainer.appendChild(row);
    });
    
    container.appendChild(chartContainer);
}

function renderQuizAveragesChart(averages) {
    const container = document.getElementById('anal-quiz-chart-container');
    if (!container) return;
    
    container.innerHTML = '';
    const keys = Object.keys(averages);
    
    if (keys.length === 0) {
        container.innerHTML = `<p style="font-size: 0.9rem; color: var(--text-muted); text-align: center; padding: 20px 0;">No quiz averages available. Take a quiz to view metrics!</p>`;
        return;
    }
    
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-bar-container';
    
    keys.forEach(key => {
        const val = averages[key];
        
        const row = document.createElement('div');
        row.className = 'chart-bar-row';
        
        // Style depending on score
        let barColor = 'var(--primary)';
        if (val >= 80) barColor = 'var(--success)';
        else if (val < 50) barColor = 'var(--danger)';
        
        row.innerHTML = `
            <span class="chart-bar-label" style="text-transform: capitalize;">${key}</span>
            <div class="chart-bar-track">
                <div class="chart-bar-fill" style="width: ${val}%; background: ${barColor};"></div>
            </div>
            <span class="chart-bar-value">${Math.round(val)}%</span>
        `;
        chartContainer.appendChild(row);
    });
    
    container.appendChild(chartContainer);
}

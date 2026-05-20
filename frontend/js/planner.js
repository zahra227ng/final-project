// Smart Planner View Controller
let currentTasksList = [];

async function loadPlanner() {
    try {
        const tasks = await makeRequest('/api/tasks');
        currentTasksList = tasks;
        renderTasks(tasks);
    } catch (error) {
        showNotification('Failed to load tasks.', 'danger');
    }
}

function renderTasks(tasks) {
    const pendingList = document.getElementById('pending-tasks-list');
    const completedList = document.getElementById('completed-tasks-list');
    
    if (!pendingList || !completedList) return;
    
    pendingList.innerHTML = '';
    completedList.innerHTML = '';
    
    const pendingTasks = tasks.filter(t => t.status !== 'completed');
    const completedTasks = tasks.filter(t => t.status === 'completed');
    
    // Render Pending
    if (pendingTasks.length === 0) {
        pendingList.innerHTML = `<li style="padding: 15px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No pending tasks. Add a new task to get started!</li>`;
    } else {
        pendingTasks.forEach(task => {
            const li = createTaskItemElement(task);
            pendingList.appendChild(li);
        });
    }
    
    // Render Completed
    if (completedTasks.length === 0) {
        completedList.innerHTML = `<li style="padding: 15px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No completed tasks yet. Finish your goals to see them here!</li>`;
    } else {
        completedTasks.forEach(task => {
            const li = createTaskItemElement(task);
            completedList.appendChild(li);
        });
    }
}

function createTaskItemElement(task) {
    const li = document.createElement('li');
    li.className = `task-item ${task.status === 'completed' ? 'completed' : ''}`;
    
    const formattedDate = task.due_date ? new Date(task.due_date).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}) : 'No date';
    const subClass = getSubjectClass(task.subject);
    
    li.innerHTML = `
        <div class="task-item-content">
            <input type="checkbox" class="task-checkbox" ${task.status === 'completed' ? 'checked' : ''} onclick="toggleTaskStatus(${task.id}, '${task.status}')">
            <div>
                <span class="task-item-text">${task.title}</span>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; display: flex; gap: 10px; align-items: center;">
                    <span class="task-badge ${subClass}" style="padding: 2px 8px; font-size: 0.7rem;">${task.subject}</span>
                    <span>Due: ${formattedDate}</span>
                    <span>🍅 ${task.completed_pomodoros}/${task.estimated_pomodoros}</span>
                </div>
                ${task.description ? `<p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 6px;">${task.description}</p>` : ''}
            </div>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            ${task.status !== 'completed' ? `
                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; font-weight: 500;" onclick="focusOnTask(${task.id})">
                    Focus ⏱️
                </button>
            ` : ''}
            <button class="btn btn-danger" style="padding: 6px; border-radius: var(--border-radius-sm);" onclick="deleteTask(${task.id})">
                🗑️
            </button>
        </div>
    `;
    
    return li;
}

function getSubjectClass(subject) {
    const sub = (subject || '').toLowerCase();
    if (sub.includes('computer') || sub.includes('code') || sub.includes('cs')) return 'cs';
    if (sub.includes('math') || sub.includes('calc')) return 'math';
    if (sub.includes('software') || sub.includes('agile')) return 'se';
    return 'general';
}

async function toggleTaskStatus(taskId, currentStatus) {
    const nextStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
        const payload = { status: nextStatus };
        if (nextStatus === 'completed') {
            // Assume we finished estimated pomodoros
            const task = currentTasksList.find(t => t.id === taskId);
            if (task) {
                payload.completed_pomodoros = task.estimated_pomodoros;
            }
        }
        await makeRequest(`/api/tasks/${taskId}`, 'PUT', payload);
        showNotification(nextStatus === 'completed' ? 'Task completed! Study hours logged.' : 'Task set to pending.', 'success');
        loadPlanner();
        if (typeof loadDashboardData === 'function') loadDashboardData();
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
        await makeRequest(`/api/tasks/${taskId}`, 'DELETE');
        showNotification('Task deleted successfully.', 'success');
        loadPlanner();
        if (typeof loadDashboardData === 'function') loadDashboardData();
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

// Redirects task to the Pomodoro timer module
function focusOnTask(taskId) {
    const task = currentTasksList.find(t => t.id === taskId);
    if (!task) return;
    
    // Set Pomodoro subject selector and task text
    const pomodoroSubject = document.getElementById('pomodoro-subject');
    if (pomodoroSubject) {
        // Find option or inject custom value
        let found = false;
        for (let i = 0; i < pomodoroSubject.options.length; i++) {
            if (pomodoroSubject.options[i].value.toLowerCase() === task.subject.toLowerCase()) {
                pomodoroSubject.selectedIndex = i;
                found = true;
                break;
            }
        }
        if (!found) {
            const newOption = new Option(task.subject, task.subject);
            pomodoroSubject.add(newOption);
            pomodoroSubject.selectedIndex = pomodoroSubject.options.length - 1;
        }
    }
    
    const activeTaskLabel = document.getElementById('pomodoro-active-task-label');
    if (activeTaskLabel) {
        activeTaskLabel.textContent = `Focusing on: ${task.title}`;
        activeTaskLabel.dataset.taskId = task.id;
    }
    
    // Switch to Pomodoro view
    switchView('pomodoro');
}

// Add task form submission
document.addEventListener('DOMContentLoaded', () => {
    const addTaskForm = document.getElementById('add-task-form');
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('task-title').value;
            const description = document.getElementById('task-description').value;
            const due_date = document.getElementById('task-due-date').value;
            const subject = document.getElementById('task-subject').value;
            const estimated_pomodoros = parseInt(document.getElementById('task-pomo-est').value);
            
            try {
                await makeRequest('/api/tasks', 'POST', {
                    title, description, due_date, subject, estimated_pomodoros
                });
                showNotification('Task created successfully!', 'success');
                addTaskForm.reset();
                closeModal('task-modal');
                loadPlanner();
                if (typeof loadDashboardData === 'function') loadDashboardData();
            } catch (error) {
                showNotification(error.message, 'danger');
            }
        });
    }
});

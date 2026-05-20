// Pomodoro Timer Module
let pomoInterval = null;
let pomoTimeLeft = 25 * 60; // 25 minutes default
let pomoIsRunning = false;
let pomoMode = 'work'; // 'work' or 'break'

const DEFAULT_WORK_MINS = 25;
const DEFAULT_BREAK_MINS = 5;

document.addEventListener('DOMContentLoaded', () => {
    initPomodoroUI();
});

function initPomodoroUI() {
    const playBtn = document.getElementById('pomo-play');
    const pauseBtn = document.getElementById('pomo-pause');
    const resetBtn = document.getElementById('pomo-reset');
    
    if (playBtn) playBtn.addEventListener('click', startPomodoro);
    if (pauseBtn) pauseBtn.addEventListener('click', pausePomodoro);
    if (resetBtn) resetBtn.addEventListener('click', resetPomodoro);
    
    // Quick Mode Changers
    const workModeBtn = document.getElementById('pomo-mode-work');
    const breakModeBtn = document.getElementById('pomo-mode-break');
    
    if (workModeBtn) workModeBtn.addEventListener('click', () => setPomodoroMode('work'));
    if (breakModeBtn) breakModeBtn.addEventListener('click', () => setPomodoroMode('break'));
    
    updatePomodoroDisplay();
}

function startPomodoro() {
    if (pomoIsRunning) return;
    
    pomoIsRunning = true;
    togglePomodoroControls();
    
    pomoInterval = setInterval(() => {
        pomoTimeLeft--;
        updatePomodoroDisplay();
        
        if (pomoTimeLeft <= 0) {
            clearInterval(pomoInterval);
            pomoIsRunning = false;
            playChimeSound();
            
            if (pomoMode === 'work') {
                handleWorkSessionCompleted();
            } else {
                handleBreakSessionCompleted();
            }
        }
    }, 1000);
}

function pausePomodoro() {
    if (!pomoIsRunning) return;
    clearInterval(pomoInterval);
    pomoIsRunning = false;
    togglePomodoroControls();
}

function resetPomodoro() {
    clearInterval(pomoInterval);
    pomoIsRunning = false;
    
    const workMins = parseInt(document.getElementById('pomo-work-input').value) || DEFAULT_WORK_MINS;
    const breakMins = parseInt(document.getElementById('pomo-break-input').value) || DEFAULT_BREAK_MINS;
    
    pomoTimeLeft = (pomoMode === 'work' ? workMins : breakMins) * 60;
    
    updatePomodoroDisplay();
    togglePomodoroControls();
}

function setPomodoroMode(mode) {
    pomoMode = mode;
    
    const timerCircle = document.querySelector('.timer-circle');
    if (timerCircle) {
        timerCircle.className = `timer-circle ${mode}`;
    }
    
    const workModeBtn = document.getElementById('pomo-mode-work');
    const breakModeBtn = document.getElementById('pomo-mode-break');
    
    if (workModeBtn && breakModeBtn) {
        if (mode === 'work') {
            workModeBtn.classList.add('active');
            breakModeBtn.classList.remove('active');
        } else {
            workModeBtn.classList.remove('active');
            breakModeBtn.classList.add('active');
        }
    }
    
    resetPomodoro();
}

function updatePomodoroDisplay() {
    const mins = Math.floor(pomoTimeLeft / 60);
    const secs = pomoTimeLeft % 60;
    
    const displayMins = mins.toString().padStart(2, '0');
    const displaySecs = secs.toString().padStart(2, '0');
    
    const displayEl = document.getElementById('pomo-display');
    if (displayEl) displayEl.textContent = `${displayMins}:${displaySecs}`;
    
    const labelEl = document.getElementById('pomo-label');
    if (labelEl) labelEl.textContent = pomoMode === 'work' ? 'Focus Session' : 'Short Break';
}

function togglePomodoroControls() {
    const playBtn = document.getElementById('pomo-play');
    const pauseBtn = document.getElementById('pomo-pause');
    
    if (playBtn && pauseBtn) {
        if (pomoIsRunning) {
            playBtn.style.display = 'none';
            pauseBtn.style.display = 'inline-flex';
        } else {
            playBtn.style.display = 'inline-flex';
            pauseBtn.style.display = 'none';
        }
    }
}

async function handleWorkSessionCompleted() {
    const subject = document.getElementById('pomodoro-subject').value;
    const workMins = parseInt(document.getElementById('pomo-work-input').value) || DEFAULT_WORK_MINS;
    
    showNotification('Great job! Focus session completed. Logged study progress.', 'success');
    
    try {
        // 1. Post Study Log
        await makeRequest('/api/ai/study_log', 'POST', {
            subject: subject,
            duration_minutes: workMins,
            activity_type: 'pomodoro'
        });
        
        // 2. Increment completed Pomodoro count on active task if linked
        const labelEl = document.getElementById('pomodoro-active-task-label');
        if (labelEl && labelEl.dataset.taskId) {
            const taskId = parseInt(labelEl.dataset.taskId);
            
            // Fetch task to find current completed count
            if (typeof currentTasksList !== 'undefined') {
                const task = currentTasksList.find(t => t.id === taskId);
                if (task) {
                    const updatedCount = task.completed_pomodoros + 1;
                    await makeRequest(`/api/tasks/${taskId}`, 'PUT', {
                        completed_pomodoros: updatedCount
                    });
                }
            }
        }
        
        // Refresh views
        if (typeof loadDashboardData === 'function') loadDashboardData();
        if (typeof loadPlanner === 'function') loadPlanner();
        
        // Auto transition to break mode
        setPomodoroMode('break');
        startPomodoro();
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

function handleBreakSessionCompleted() {
    showNotification('Break is over! Time to get back to work.', 'warning');
    setPomodoroMode('work');
}

// Synthesizes a clean chimes alarm sound using browser Web Audio API (no external file needed!)
function playChimeSound() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Tone 1
        const osc1 = audioCtx.createOscillator();
        const gain1 = audioCtx.createGain();
        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5
        gain1.gain.setValueAtTime(0.5, audioCtx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
        osc1.start(audioCtx.currentTime);
        osc1.stop(audioCtx.currentTime + 0.5);
        
        // Tone 2 after delay
        setTimeout(() => {
            const osc2 = audioCtx.createOscillator();
            const gain2 = audioCtx.createGain();
            osc2.connect(gain2);
            gain2.connect(audioCtx.destination);
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(880.00, audioCtx.currentTime); // A5
            gain2.gain.setValueAtTime(0.5, audioCtx.currentTime);
            gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.8);
            osc2.start(audioCtx.currentTime);
            osc2.stop(audioCtx.currentTime + 0.8);
        }, 300);
    } catch (err) {
        console.warn('AudioContext not supported or allowed by user interaction:', err);
    }
}

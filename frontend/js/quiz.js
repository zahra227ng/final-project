// Quiz View & Active Game Controller
let activeQuiz = null;
let currentQuestionIndex = 0;
let userAnswers = [];

async function loadQuizView() {
    try {
        // Reset state
        hideQuizPanels();
        document.getElementById('quiz-setup-panel').style.display = 'block';
        
        // Load past quizzes
        const history = await makeRequest('/api/quiz/history');
        renderQuizHistory(history);
    } catch (error) {
        showNotification('Failed to load quiz history.', 'danger');
    }
}

function hideQuizPanels() {
    document.getElementById('quiz-setup-panel').style.display = 'none';
    document.getElementById('quiz-active-panel').style.display = 'none';
    document.getElementById('quiz-results-panel').style.display = 'none';
}

function renderQuizHistory(history) {
    const list = document.getElementById('quiz-history-list');
    if (!list) return;
    
    list.innerHTML = '';
    
    if (history.length === 0) {
        list.innerHTML = `<li style="padding: 15px; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No quizzes taken yet. Generate one above to test your skills!</li>`;
        return;
    }
    
    history.forEach(item => {
        const li = document.createElement('li');
        li.className = 'task-item';
        
        const scorePct = item.score !== null ? Math.round((item.score / item.total_questions) * 100) : null;
        const scoreText = scorePct !== null ? `${item.score}/${item.total_questions} (${scorePct}%)` : 'Pending';
        const dateStr = new Date(item.created_at).toLocaleDateString(undefined, {month: 'short', day: 'numeric', year: 'numeric'});
        
        li.innerHTML = `
            <div>
                <span class="task-item-text" style="font-size: 0.95rem;">${item.title}</span>
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; display: flex; gap: 10px; align-items: center;">
                    <span class="task-badge cs" style="font-size: 0.7rem;">${item.subject || 'General'}</span>
                    <span>Taken on: ${dateStr}</span>
                </div>
            </div>
            <span class="task-badge" style="font-size: 0.8rem; font-weight: bold; background: ${scorePct >= 70 ? 'var(--success-light)' : 'var(--danger-light)'}; color: ${scorePct >= 70 ? 'var(--success)' : 'var(--danger)'};">
                Score: ${scoreText}
            </span>
        `;
        list.appendChild(li);
    });
}

// Generate Quiz trigger
document.addEventListener('DOMContentLoaded', () => {
    const genBtn = document.getElementById('quiz-generate-btn');
    if (genBtn) {
        genBtn.addEventListener('click', generateNewQuiz);
    }
});

async function generateNewQuiz() {
    const subject = document.getElementById('quiz-subject').value;
    const topic = document.getElementById('quiz-topic').value;
    
    try {
        showNotification('Generating quiz with AI Study Buddy rules...', 'primary');
        const quiz = await makeRequest('/api/quiz/generate', 'POST', { subject, topic });
        startActiveQuiz(quiz);
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

function startActiveQuiz(quiz) {
    activeQuiz = quiz;
    currentQuestionIndex = 0;
    userAnswers = [];
    
    hideQuizPanels();
    document.getElementById('quiz-active-panel').style.display = 'block';
    document.getElementById('quiz-active-title').textContent = quiz.title;
    
    renderCurrentQuestion();
}

function renderCurrentQuestion() {
    const question = activeQuiz.questions[currentQuestionIndex];
    const total = activeQuiz.total_questions;
    
    document.getElementById('quiz-progress-text').textContent = `Question ${currentQuestionIndex + 1} of ${total}`;
    document.getElementById('quiz-progress-bar-fill').style.width = `${((currentQuestionIndex + 1) / total) * 100}%`;
    document.getElementById('quiz-question-text').textContent = question.question;
    
    const optionsContainer = document.getElementById('quiz-options-container');
    optionsContainer.innerHTML = '';
    
    question.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'quiz-option';
        btn.innerHTML = `<span style="font-weight: bold; margin-right: 10px;">${String.fromCharCode(65 + idx)}.</span> ${opt}`;
        btn.onclick = () => selectOption(idx);
        optionsContainer.appendChild(btn);
    });
    
    // Hide explanation box and next controls
    document.getElementById('quiz-explanation-container').style.display = 'none';
    document.getElementById('quiz-next-controls').style.display = 'none';
}

function selectOption(selectedIdx) {
    userAnswers.push(selectedIdx);
    
    const question = activeQuiz.questions[currentQuestionIndex];
    const correctIdx = question.correct;
    
    const optionBtns = document.querySelectorAll('.quiz-option');
    
    optionBtns.forEach((btn, idx) => {
        btn.disabled = true; // Block multiple clicks
        btn.style.cursor = 'default';
        
        if (idx === correctIdx) {
            btn.classList.add('correct');
        } else if (idx === selectedIdx) {
            btn.classList.add('incorrect');
        }
    });
    
    // Show Explanation
    const explanationBox = document.getElementById('quiz-explanation-text');
    explanationBox.textContent = question.explanation;
    document.getElementById('quiz-explanation-container').style.display = 'block';
    
    // Show next button / submit control
    const nextBtn = document.getElementById('quiz-next-btn');
    if (currentQuestionIndex + 1 === activeQuiz.total_questions) {
        nextBtn.textContent = 'Finish Quiz & Submit 🚀';
    } else {
        nextBtn.textContent = 'Next Question ➡️';
    }
    
    document.getElementById('quiz-next-controls').style.display = 'block';
    
    // Wire button listener
    nextBtn.onclick = handleQuizNextStep;
}

function handleQuizNextStep() {
    if (currentQuestionIndex + 1 < activeQuiz.total_questions) {
        currentQuestionIndex++;
        renderCurrentQuestion();
    } else {
        submitQuizResults();
    }
}

async function submitQuizResults() {
    try {
        showNotification('Evaluating quiz scores...', 'primary');
        const results = await makeRequest('/api/quiz/submit', 'POST', {
            quiz_id: activeQuiz.id,
            answers: userAnswers
        });
        
        renderQuizResultsCard(results);
    } catch (error) {
        showNotification(error.message, 'danger');
    }
}

function renderQuizResultsCard(results) {
    hideQuizPanels();
    document.getElementById('quiz-results-panel').style.display = 'block';
    
    const scorePct = Math.round((results.score / results.total_questions) * 100);
    document.getElementById('quiz-result-score-text').textContent = `${results.score} / ${results.total_questions}`;
    document.getElementById('quiz-result-percentage').textContent = `${scorePct}%`;
    
    // Setup message and visual styling
    const feedbackMsg = document.getElementById('quiz-result-feedback');
    const radialScore = document.getElementById('quiz-result-radial');
    
    if (scorePct >= 80) {
        feedbackMsg.textContent = 'Excellent! You have mastered this topic. 🌟';
        feedbackMsg.style.color = 'var(--success)';
        radialScore.style.borderLeftColor = 'var(--success)';
    } else if (scorePct >= 50) {
        feedbackMsg.textContent = 'Good effort! Review the explanations below to improve. 📖';
        feedbackMsg.style.color = 'var(--warning)';
        radialScore.style.borderLeftColor = 'var(--warning)';
    } else {
        feedbackMsg.textContent = 'Needs review. We recommend testing yourself again soon! 🎯';
        feedbackMsg.style.color = 'var(--danger)';
        radialScore.style.borderLeftColor = 'var(--danger)';
    }
    
    // Render detailed explanations list
    const answersList = document.getElementById('quiz-results-answers-list');
    answersList.innerHTML = '';
    
    results.details.forEach(item => {
        const div = document.createElement('div');
        div.style.marginBottom = '25px';
        div.style.padding = '15px';
        div.style.background = 'var(--bg-hover)';
        div.style.borderRadius = 'var(--border-radius-md)';
        div.style.borderLeft = item.is_correct ? '4px solid var(--success)' : '4px solid var(--danger)';
        
        div.innerHTML = `
            <h5 style="margin-bottom: 8px; font-size: 0.95rem;">${item.question}</h5>
            <div style="font-size: 0.85rem; margin-bottom: 6px;">
                <span style="color: ${item.is_correct ? 'var(--success)' : 'var(--danger)'}; font-weight: 600;">
                    Your Answer: ${item.user_answer}
                </span>
                ${!item.is_correct ? `<br><span style="color: var(--success); font-weight: 600;">Correct Answer: ${item.correct_answer}</span>` : ''}
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); border-top: 1px solid var(--border-color); padding-top: 6px; margin-top: 6px;">
                <strong>Explanation:</strong> ${item.explanation}
            </p>
        `;
        answersList.appendChild(div);
    });
    
    // Refresh dashboard stats
    if (typeof loadDashboardData === 'function') loadDashboardData();
}

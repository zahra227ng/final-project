// AI Tutor Chatbot Controller
document.addEventListener('DOMContentLoaded', () => {
    const sendBtn = document.getElementById('chat-send-btn');
    const chatInput = document.getElementById('chat-input');
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }
    
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
    
    // Quick chips click bindings
    const chips = document.querySelectorAll('.chat-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            if (chatInput) {
                chatInput.value = chip.textContent;
                sendChatMessage();
            }
        });
    });
});

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const container = document.getElementById('chat-messages-container');
    
    if (!input || !container) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Clear Input
    input.value = '';
    
    // 1. Add User Bubble
    appendChatBubble(message, 'user');
    
    // Scroll bottom
    scrollChatBottom();
    
    // 2. Add Loading Indicator
    const loadingId = appendLoadingIndicator();
    scrollChatBottom();
    
    try {
        // Post message to backend
        const result = await makeRequest('/api/ai/chat', 'POST', { message });
        
        // Remove loading
        removeLoadingIndicator(loadingId);
        
        // 3. Add Bot Bubble
        appendChatBubble(result.response, 'bot');
        scrollChatBottom();
        
        // Refresh dashboard to show study minutes updated
        if (typeof loadDashboardData === 'function') loadDashboardData();
    } catch (error) {
        removeLoadingIndicator(loadingId);
        appendChatBubble(`Error: ${error.message}. Please try again.`, 'bot');
        scrollChatBottom();
    }
}

function appendChatBubble(text, sender) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;
    
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    
    // Simple markdown helper to support bolding and spacing in text responses
    const formattedText = text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
    bubble.innerHTML = formattedText;
    container.appendChild(bubble);
}

function appendLoadingIndicator() {
    const container = document.getElementById('chat-messages-container');
    if (!container) return null;
    
    const loadingId = 'loading-' + Date.now();
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble bot';
    bubble.id = loadingId;
    bubble.innerHTML = `
        <div style="display: flex; gap: 4px; align-items: center; justify-content: center; height: 20px;">
            <div class="dot-bounce" style="width: 6px; height: 6px; border-radius: 50%; background: var(--text-secondary); animation: bounce 1.4s infinite ease-in-out; animation-delay: -0.32s;"></div>
            <div class="dot-bounce" style="width: 6px; height: 6px; border-radius: 50%; background: var(--text-secondary); animation: bounce 1.4s infinite ease-in-out; animation-delay: -0.16s;"></div>
            <div class="dot-bounce" style="width: 6px; height: 6px; border-radius: 50%; background: var(--text-secondary); animation: bounce 1.4s infinite ease-in-out;"></div>
        </div>
        <style>
            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1.0); }
            }
        </style>
    `;
    container.appendChild(bubble);
    return loadingId;
}

function removeLoadingIndicator(loadingId) {
    if (!loadingId) return;
    const indicator = document.getElementById(loadingId);
    if (indicator) indicator.remove();
}

function scrollChatBottom() {
    const container = document.getElementById('chat-messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

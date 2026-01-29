const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const chatMessages = document.getElementById('chatMessages');
const typingIndicator = document.getElementById('typingIndicator');
const sendButton = document.getElementById('sendButton');
const themeToggle = document.getElementById('themeToggle');

// Dark mode toggle
themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
});

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

// Auto-scroll to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add message to chat
function addMessage(content, isUser, conversationId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'agent'}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const p = document.createElement('p');
    p.textContent = content;

    contentDiv.appendChild(p);

    // Add feedback buttons for agent messages
    if (!isUser && conversationId) {
        const feedbackDiv = createFeedbackButtons(conversationId);
        contentDiv.appendChild(feedbackDiv);
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    scrollToBottom();
}

// Create feedback buttons
function createFeedbackButtons(conversationId) {
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'feedback-buttons';
    feedbackDiv.dataset.conversationId = conversationId;

    const thumbsUp = document.createElement('button');
    thumbsUp.className = 'feedback-btn thumbs-up';
    thumbsUp.innerHTML = '&#x1F44D;';
    thumbsUp.title = 'Helpful';
    thumbsUp.onclick = () => submitFeedback(conversationId, 1, feedbackDiv);

    const thumbsDown = document.createElement('button');
    thumbsDown.className = 'feedback-btn thumbs-down';
    thumbsDown.innerHTML = '&#x1F44E;';
    thumbsDown.title = 'Not helpful';
    thumbsDown.onclick = () => submitFeedback(conversationId, -1, feedbackDiv);

    feedbackDiv.appendChild(thumbsUp);
    feedbackDiv.appendChild(thumbsDown);

    return feedbackDiv;
}

// Submit feedback to server
async function submitFeedback(conversationId, rating, feedbackDiv) {
    // Disable buttons immediately
    const buttons = feedbackDiv.querySelectorAll('.feedback-btn');
    buttons.forEach(btn => btn.disabled = true);

    try {
        const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                rating: rating
            })
        });

        const data = await response.json();

        if (data.success) {
            // Replace buttons with thank you message
            feedbackDiv.innerHTML = '<span class="feedback-thanks">Thanks for feedback!</span>';
        } else {
            // Re-enable buttons on error
            buttons.forEach(btn => btn.disabled = false);
            console.error('Feedback error:', data.error);
        }
    } catch (error) {
        // Re-enable buttons on error
        buttons.forEach(btn => btn.disabled = false);
        console.error('Feedback error:', error);
    }
}

// Show/hide typing indicator
function setTyping(show) {
    typingIndicator.classList.toggle('show', show);
    if (show) scrollToBottom();
}

// Send message
async function sendMessage(message) {
    // Disable input while sending
    messageInput.disabled = true;
    sendButton.disabled = true;
    setTyping(true);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        setTyping(false);

        if (data.error) {
            addMessage('Sorry, something went wrong. Please try again.', false);
        } else {
            // Pass conversation_id for feedback tracking
            addMessage(data.response, false, data.conversation_id);
        }
    } catch (error) {
        setTyping(false);
        addMessage('Connection error. Please check if the server is running.', false);
    }

    // Re-enable input
    messageInput.disabled = false;
    sendButton.disabled = false;
    messageInput.focus();
}

// Handle form submit
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, true);

    // Clear input
    messageInput.value = '';

    // Send to server
    sendMessage(message);
});

// Focus input on load
messageInput.focus();

// Stats elements
const statusIndicator = document.getElementById('statusIndicator');
const queriesToday = document.getElementById('queriesToday');
const avgResponseTime = document.getElementById('avgResponseTime');

// Fetch and display stats
async function fetchStats() {
    try {
        const response = await fetch('/stats');
        const data = await response.json();

        if (data.online) {
            statusIndicator.textContent = 'Online';
            statusIndicator.classList.remove('offline');
        } else {
            statusIndicator.textContent = 'Offline';
            statusIndicator.classList.add('offline');
        }

        queriesToday.textContent = data.queries_today || 0;
        avgResponseTime.textContent = data.avg_response_time_ms
            ? `${Math.round(data.avg_response_time_ms)}ms`
            : '-';
    } catch (error) {
        statusIndicator.textContent = 'Offline';
        statusIndicator.classList.add('offline');
        console.error('Failed to fetch stats:', error);
    }
}

// Fetch stats on load and periodically
fetchStats();
setInterval(fetchStats, 30000); // Refresh every 30 seconds

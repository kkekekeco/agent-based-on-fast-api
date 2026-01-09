// DOM Elements
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const messagesContainer = document.getElementById('messages');
const thinkingContainer = document.getElementById('thinkingContainer');
const thinkingText = document.getElementById('thinkingText');
const welcomeMessage = document.getElementById('welcomeMessage');
const chatContainer = document.getElementById('chatContainer');
const chatList = document.getElementById('chatList');
const modelDropdown = document.getElementById('modelDropdown');
const selectedModelText = document.getElementById('selectedModelText');
const sidebar = document.getElementById('sidebar');

// State
let currentChatId = null;
let selectedModel = 'grok-4-fast';
let chats = {};

// Thinking phrases
const thinkingPhrases = [
    "Thinking...",
    "Searching the web...",
    "Analyzing information...",
    "Reading pages...",
    "Processing results...",
    "Formulating response..."
];

let thinkingInterval = null;
let currentPhraseIndex = 0;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadChats();
    renderChatList();

    // Load last selected model
    const savedModel = localStorage.getItem('selectedModel');
    if (savedModel) {
        selectModel(savedModel, false);
    }

    // If no active chat, show welcome
    if (!currentChatId) {
        showWelcome();
    }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.model-selector')) {
        modelDropdown.classList.remove('show');
    }
});

// Auto-resize textarea
userInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
});

// Handle Enter key
userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

// Handle form submission
chatForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const query = userInput.value.trim();
    if (!query) return;

    // Create new chat if none exists
    if (!currentChatId) {
        createNewChat(false);
    }

    // Hide welcome message
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }

    // Add user message
    addMessage(query, 'user');

    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';

    // Disable send button
    sendButton.disabled = true;

    // Show thinking indicator
    showThinking();

    try {
        const response = await fetch('/agent/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                model: selectedModel
            })
        });

        const data = await response.json();

        // Hide thinking indicator
        hideThinking();

        if (response.ok) {
            addMessage(data.response, 'assistant', data.tool_calls);
        } else {
            addMessage('Sorry, an error occurred. Please try again.', 'assistant');
        }
    } catch (error) {
        hideThinking();
        addMessage('Connection error. Please check if the server is running.', 'assistant');
        console.error('Error:', error);
    }

    // Re-enable send button
    sendButton.disabled = false;
    userInput.focus();
});

// === Chat Session Management ===

function loadChats() {
    const saved = localStorage.getItem('chats');
    if (saved) {
        chats = JSON.parse(saved);
    }

    const lastChatId = localStorage.getItem('currentChatId');
    if (lastChatId && chats[lastChatId]) {
        loadChat(lastChatId);
    }
}

function saveChats() {
    localStorage.setItem('chats', JSON.stringify(chats));
    localStorage.setItem('currentChatId', currentChatId || '');
}

function createNewChat(shouldRender = true) {
    const id = 'chat_' + Date.now();
    chats[id] = {
        id,
        title: 'New Chat',
        messages: [],
        timestamp: Date.now(),
        model: selectedModel
    };
    currentChatId = id;
    saveChats();

    if (shouldRender) {
        renderChatList();
        clearMessages();
        showWelcome();
    }
}

function loadChat(chatId) {
    if (!chats[chatId]) return;

    currentChatId = chatId;
    const chat = chats[chatId];

    // Clear and render messages
    clearMessages();
    hideWelcome();

    chat.messages.forEach(msg => {
        renderMessage(msg.content, msg.role, msg.toolCalls);
    });

    saveChats();
    renderChatList();
    scrollToBottom();
}

function deleteChat(chatId, event) {
    event.stopPropagation();

    delete chats[chatId];

    if (currentChatId === chatId) {
        currentChatId = null;
        clearMessages();
        showWelcome();
    }

    saveChats();
    renderChatList();
}

function clearAllChats() {
    if (confirm('Are you sure you want to clear all chat history?')) {
        chats = {};
        currentChatId = null;
        saveChats();
        renderChatList();
        clearMessages();
        showWelcome();
    }
}

function renderChatList() {
    const sortedChats = Object.values(chats).sort((a, b) => b.timestamp - a.timestamp);

    chatList.innerHTML = sortedChats.map(chat => `
        <div class="chat-item ${chat.id === currentChatId ? 'active' : ''}" onclick="loadChat('${chat.id}')">
            <span class="chat-item-icon">💬</span>
            <span class="chat-item-title">${escapeHtml(chat.title)}</span>
            <button class="chat-item-delete" onclick="deleteChat('${chat.id}', event)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
            </button>
        </div>
    `).join('');
}

// === Model Selection ===

function toggleModelDropdown() {
    modelDropdown.classList.toggle('show');
}

function selectModel(model, save = true) {
    selectedModel = model;
    selectedModelText.textContent = model;

    // Update checkmarks
    document.querySelectorAll('.model-check').forEach(el => el.textContent = '');
    const check = document.getElementById(`check-${model}`);
    if (check) check.textContent = '✓';

    // Close dropdown
    modelDropdown.classList.remove('show');

    if (save) {
        localStorage.setItem('selectedModel', model);
    }
}

// === Sidebar ===

function toggleSidebar() {
    sidebar.classList.toggle('show');
    sidebar.classList.toggle('collapsed');
}

// === Messages ===

function addMessage(content, role, toolCalls = null) {
    if (!currentChatId) return;

    // Save to chat
    const chat = chats[currentChatId];
    chat.messages.push({ content, role, toolCalls });

    // Update title from first user message
    if (role === 'user' && chat.messages.length === 1) {
        chat.title = content.slice(0, 40) + (content.length > 40 ? '...' : '');
    }

    chat.timestamp = Date.now();
    saveChats();
    renderChatList();

    // Render message
    renderMessage(content, role, toolCalls);
}

function renderMessage(content, role, toolCalls = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = role === 'user' ? '👤' : '🤖';

    let toolCallsHtml = '';
    if (toolCalls && toolCalls.length > 0) {
        toolCallsHtml = '<div class="tool-calls">';
        toolCalls.forEach(tc => {
            const args = JSON.parse(tc.arguments);
            const argDisplay = args.query || args.url || '';
            toolCallsHtml += `
                <div class="tool-call">
                    <span class="tool-call-icon">🔧</span>
                    <span class="tool-call-name">${tc.name}</span>
                    <span class="tool-call-args">${escapeHtml(argDisplay)}</span>
                </div>
            `;
        });
        toolCallsHtml += '</div>';
    }

    const formattedContent = formatContent(content);

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            ${formattedContent}
            ${toolCallsHtml}
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function clearMessages() {
    messagesContainer.innerHTML = '';
}

function showWelcome() {
    if (welcomeMessage) {
        welcomeMessage.style.display = 'block';
    }
}

function hideWelcome() {
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
}

// === Utilities ===

function formatContent(content) {
    if (!content) return '';

    let formatted = escapeHtml(content);

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');

    // Inline code
    formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    // Headers
    formatted = formatted.replace(/^### (.*?)(<br>|$)/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*?)(<br>|$)/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*?)(<br>|$)/gm, '<h1>$1</h1>');

    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showThinking() {
    thinkingContainer.style.display = 'block';
    currentPhraseIndex = 0;
    thinkingText.textContent = thinkingPhrases[0];

    thinkingInterval = setInterval(() => {
        currentPhraseIndex = (currentPhraseIndex + 1) % thinkingPhrases.length;
        thinkingText.textContent = thinkingPhrases[currentPhraseIndex];
    }, 2000);

    scrollToBottom();
}

function hideThinking() {
    thinkingContainer.style.display = 'none';
    if (thinkingInterval) {
        clearInterval(thinkingInterval);
        thinkingInterval = null;
    }
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function useSuggestion(text) {
    userInput.value = text;
    userInput.focus();
    chatForm.dispatchEvent(new Event('submit'));
}

// Project management
let currentProject = 'General';

// Load projects
function loadProjects() {
    fetch('/api/projects')
        .then(r => r.json())
        .then(data => {
            const projectList = document.getElementById('projectList');
            if (projectList) {
                projectList.innerHTML = '';
                
                // Add General project first
                addProjectItem('General', true);
                
                // Add other projects
                data.projects.forEach(project => {
                    if (project !== 'General') {
                        addProjectItem(project);
                    }
                });
            }
        });
}

// Add project to list
function addProjectItem(name, isActive = false) {
    const projectList = document.getElementById('projectList');
    const div = document.createElement('div');
    div.className = 'project-item' + (isActive ? ' active' : '');
    div.innerHTML = `
        <i class="fas fa-folder${isActive ? '-open' : ''}"></i>
        <span>${name}</span>
        <button class="project-delete" data-project="${name}" title="Delete">
            <i class="fas fa-trash"></i>
        </button>
    `;
    
    div.addEventListener('click', function(e) {
        if (!e.target.closest('.project-delete')) {
            switchProject(name);
        }
    });
    
    projectList.appendChild(div);
}

// Switch project
function switchProject(projectName) {
    if (currentProject === projectName) return;
    
    // Save current chat
    saveCurrentChat();
    
    // Switch project
    currentProject = projectName;
    
    // Load project chat for current agent
    loadProjectChat(projectName, currentAgent);
    
    // Update UI
    document.querySelectorAll('.project-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-project="${projectName}"]`).closest('.project-item').classList.add('active');
}

// Update sendMessage to include project
window.sendMessage = function() {
    // ... existing code ...
    
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id: 'minimal_' + Date.now(),
            agent_type: currentAgent,
            project_name: currentProject,  // NEW
            message: message
        })
    })
    // ... rest of code ...
};
// minimal.js - Simple, error-free JavaScript

console.log('Minimal JS loading...');

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing...');
    
    // Hide loading overlay
    var loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        console.log('Loading overlay hidden');
    }
    
    // Initialize variables
    var currentAgent = 'basic';
    var isTyping = false;
    
    // Bind agent selection
    var agentOptions = document.querySelectorAll('.agent-option');
    agentOptions.forEach(function(option) {
        option.addEventListener('click', function() {
            // Remove active class from all
            agentOptions.forEach(function(opt) {
                opt.classList.remove('active');
            });
            
            // Add active class to clicked
            this.classList.add('active');
            
            // Update current agent
            currentAgent = this.dataset.agent;
            
            // Update header
            var agentNames = {
                'basic': 'Basic Agent',
                'enhanced': 'Enhanced Agent',
                'creative': 'Creative Agent'
            };
            
            var header = document.getElementById('currentAgent');
            if (header) {
                header.textContent = agentNames[currentAgent] || 'AI Agent';
            }
            
            console.log('Agent changed to:', currentAgent);
        });
    });
    
    // Send message function
    window.sendMessage = function() {
        if (isTyping) return;
        
        var input = document.getElementById('messageInput');
        var message = input.value.trim();
        
        if (!message) return;
        
        // Clear input
        input.value = '';
        
        // Add user message
        addMessage('user', message);
        
        // Show typing
        isTyping = true;
        var typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
        }
        
        // Hide welcome message
        var welcomeMessage = document.getElementById('welcomeMessage');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        // Send to API
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: 'minimal_' + Date.now(),
                agent_type: currentAgent,
                message: message
            })
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            if (data.error) {
                throw new Error(data.error);
            }
            addMessage('assistant', data.response || 'No response');
        })
        .catch(function(error) {
            console.error('API Error:', error);
            addMessage('assistant', 'I received: "' + message + '". (Note: Check if LM Studio is running)');
        })
        .finally(function() {
            isTyping = false;
            if (typingIndicator) {
                typingIndicator.style.display = 'none';
            }
        });
    };
    
    // Add message to chat
    function addMessage(role, content) {
        var chatContainer = document.getElementById('chatContainer');
        if (!chatContainer) return;
        
        var messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + role;
        
        var sender = role === 'user' ? 'You' : 'Assistant';
        var timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = '<div class="message-content">' +
                               '<div class="message-header">' +
                               '<span class="message-sender">' + sender + '</span>' +
                               '<span class="message-time">' + timestamp + '</span>' +
                               '</div>' +
                               '<div class="message-text">' + escapeHtml(content) + '</div>' +
                               '</div>';
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Simple HTML escaping
    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Bind send button
    var sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', window.sendMessage);
    }
    
    // Bind enter key in input
    var messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                window.sendMessage();
            }
        });
        
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }
    
    // Bind clear chat
    var clearButton = document.getElementById('clearChatBtn');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            if (confirm('Clear the chat?')) {
                var chatContainer = document.getElementById('chatContainer');
                if (chatContainer) {
                    chatContainer.innerHTML = '<div class="welcome-message" id="welcomeMessage">' +
                                             '<div class="welcome-content">' +
                                             '<div class="welcome-icon">' +
                                             '<i class="fas fa-robot"></i>' +
                                             '</div>' +
                                             '<h2>Chat Cleared</h2>' +
                                             '<p>Select an agent type and start chatting.</p>' +
                                             '</div>' +
                                             '</div>';
                }
            }
        });
    }
    
    // Bind new chat
    var newChatButton = document.getElementById('newChatBtn');
    if (newChatButton) {
        newChatButton.addEventListener('click', function() {
            if (confirm('Start a new chat?')) {
                var chatContainer = document.getElementById('chatContainer');
                if (chatContainer) {
                    chatContainer.innerHTML = '<div class="welcome-message" id="welcomeMessage">' +
                                             '<div class="welcome-content">' +
                                             '<div class="welcome-icon">' +
                                             '<i class="fas fa-robot"></i>' +
                                             '</div>' +
                                             '<h2>New Chat</h2>' +
                                             '<p>Select an agent type and start chatting.</p>' +
                                             '</div>' +
                                             '</div>';
                }
            }
        });
    }
    
    // Bind quick prompts
    var promptCards = document.querySelectorAll('.prompt-card');
    promptCards.forEach(function(card) {
        card.addEventListener('click', function() {
            var prompt = this.dataset.prompt;
            if (messageInput && prompt) {
                messageInput.value = prompt;
                messageInput.focus();
                messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
            }
        });
    });
    
    console.log('Minimal interface ready!');
});
// Global variables
let messageCount = 0;
let isGenerating = false;
let currentViewMode = 'split';
let currentSessionId = null;
let conversationTitle = 'New Conversation';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Try to load PDF after a short delay
    setTimeout(loadPDFEmbed, 1000);
    
    // Initialize session info
    updateSessionInfo();
});

// =====================================================
// VIEW MODE FUNCTIONS
// =====================================================

function setViewMode(mode) {
    const chatPanel = document.getElementById('chatPanel');
    const pdfPanel = document.getElementById('pdfPanel');
    const container = document.getElementById('mainContainer');
    
    // Reset all states
    chatPanel.classList.remove('hidden', 'expanded');
    pdfPanel.classList.remove('hidden', 'expanded');
    container.classList.remove('fullscreen');
    
    currentViewMode = mode;
    
    switch(mode) {
        case 'split':
            // Default split view - do nothing, reset above handles it
            addMessage("⚌ Split view activated", 'system');
            break;
        case 'chat':
            pdfPanel.classList.add('hidden');
            chatPanel.classList.add('expanded');
            addMessage("💬 Chat-only mode activated", 'system');
            break;
        case 'pdf':
            chatPanel.classList.add('hidden');
            pdfPanel.classList.add('expanded');
            addMessage("📄 PDF-only mode activated", 'system');
            break;
    }
}

// =====================================================
// PDF FUNCTIONS
// =====================================================

function loadPDFEmbed() {
    const pdfViewer = document.getElementById('pdfViewer');
    const pdfPlaceholder = document.getElementById('pdfPlaceholder');
    
    console.log('Attempting to load PDF...');
    
    // Try multiple methods to display the PDF
    const pdfUrl = 'output.pdf?t=' + new Date().getTime();
    
    // Method 1: Try with embed tag
    pdfViewer.innerHTML = `
        <embed src="${pdfUrl}" type="application/pdf" class="pdf-container" />
        <div id="embedFallback" style="display: none;">
            <div class="pdf-placeholder">
                <div class="icon">📄</div>
                <h3>PDF Viewer Not Supported</h3>
                <p>Your browser doesn't support embedded PDF viewing.</p>
                <a href="output.pdf" target="_blank" class="fallback-link">📄 View PDF in New Tab</a>
                <button class="fallback-link" onclick="tryIframeMethod()">🔄 Try Alternative Method</button>
            </div>
        </div>
    `;
    
    // Check if embed loaded successfully after 3 seconds
    setTimeout(checkPDFLoad, 3000);
}

function checkPDFLoad() {
    const embed = document.querySelector('embed');
    if (embed) {
        // Try to access the embed's document to see if it loaded
        try {
            if (embed.offsetHeight === 0 || embed.offsetWidth === 0) {
                console.log('Embed tag failed, showing fallback');
                showEmbedFallback();
            } else {
                console.log('PDF loaded successfully with embed tag');
                addMessage("✅ Resume loaded successfully!", 'system');
            }
        } catch (e) {
            console.log('Error checking embed:', e);
            showEmbedFallback();
        }
    }
}

function showEmbedFallback() {
    const fallback = document.getElementById('embedFallback');
    if (fallback) {
        fallback.style.display = 'block';
    }
}

function tryIframeMethod() {
    const pdfViewer = document.getElementById('pdfViewer');
    const pdfUrl = 'output.pdf?t=' + new Date().getTime();
    
    pdfViewer.innerHTML = `
        <iframe src="${pdfUrl}" class="pdf-container" frameborder="0">
            <div class="pdf-placeholder">
                <div class="icon">📄</div>
                <h3>PDF Cannot Be Displayed</h3>
                <p>Please use the button below to view the PDF.</p>
                <a href="output.pdf" target="_blank" class="fallback-link">📄 View PDF in New Tab</a>
            </div>
        </iframe>
    `;
    
    addMessage("🔄 Trying alternative PDF display method...", 'system');
}

function refreshPDF() {
    addMessage("🔄 Compiling resume from LaTeX...", 'system');
    
    // Show loading state
    const refreshButton = document.querySelector('[onclick="refreshPDF()"]');
    const originalText = refreshButton.innerHTML;
    refreshButton.innerHTML = '⏳ Compiling...';
    refreshButton.disabled = true;
    
    fetch('/compile_resume', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessage("✅ " + data.message, 'system');
            
            // If PDF was generated, reload the PDF viewer
            if (data.pdf_generated) {
                setTimeout(() => {
                    loadPDFEmbed();
                    addMessage("📄 Resume PDF refreshed successfully!", 'system');
                }, 500);
            } else {
                addMessage("📝 LaTeX file ready. Manual compilation required for PDF.", 'system');
            }
        } else {
            addMessage("❌ " + data.message, 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error compiling resume. Please check if LaTeX is installed.", 'system');
    })
    .finally(() => {
        // Restore button state
        refreshButton.innerHTML = originalText;
        refreshButton.disabled = false;
    });
}

function openPDFNewTab() {
    window.open('output.pdf', '_blank');
    addMessage("👁️ Opened PDF in new tab!", 'system');
}

function downloadPDF() {
    const link = document.createElement('a');
    link.href = 'output.pdf';
    link.download = 'my-resume.pdf';
    link.click();
    addMessage("📥 Resume downloaded!", 'system');
}

// =====================================================
// CHAT FUNCTIONS
// =====================================================

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isGenerating) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show loading
    showLoading(true);
    
    // Make actual API call to Groq
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.error) {
            addMessage(`❌ Error: ${data.response || data.error}`, 'system');
        } else {
            addMessage(data.response, 'ai');
            
            // Update session info
            if (data.session_id) {
                currentSessionId = data.session_id;
                conversationTitle = data.conversation_title || 'New Conversation';
                updateSessionInfo();
            }
            
            // Check if the AI response indicates resume was updated
            if (data.response.includes('Resume updated and compiled successfully') ||
                data.response.includes('✅ Resume updated')) {
                setTimeout(() => {
                    loadPDFEmbed();
                }, 1000);
            }
            
            // Check if we should refresh PDF based on content keywords
            else if (messageCount > 2 && (
                message.toLowerCase().includes('experience') ||
                message.toLowerCase().includes('education') ||
                message.toLowerCase().includes('skill') ||
                message.toLowerCase().includes('project') ||
                message.toLowerCase().includes('certification')
            )) {
                setTimeout(() => {
                    refreshPDF();
                    addMessage("✅ Resume updated! Check the preview on the right.", 'system');
                }, 1000);
            }
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Error:', error);
        addMessage('❌ Connection error. Please check your internet connection and try again.', 'system');
    });
}

function addMessage(text, type) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    messageCount++;
}

function addTemplate(type) {
    const templates = {
        education: "I have a Bachelor's degree in [Your Major] from [University Name], graduated in [Year] with GPA [X.X]",
        experience: "I worked as [Job Title] at [Company Name] from [Start Date] to [End Date], where I [key achievement]",
        skills: "My technical skills include: [Programming Languages], [Tools/Software], [Frameworks]",
        projects: "I worked on a project called [Project Name] where I [description of what you built/achieved]",
        certifications: "I have certifications in [Certification Name] from [Issuing Organization] obtained in [Year]"
    };
    
    const messageInput = document.getElementById('messageInput');
    messageInput.value = templates[type];
    messageInput.focus();
}

function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    const sendButton = document.getElementById('sendButton');
    
    if (show) {
        loadingIndicator.classList.add('show');
        sendButton.disabled = true;
        isGenerating = true;
    } else {
        loadingIndicator.classList.remove('show');
        sendButton.disabled = false;
        isGenerating = false;
    }
}

// =====================================================
// MEMORY MANAGEMENT FUNCTIONS
// =====================================================

function updateSessionInfo() {
    const sessionInfo = document.getElementById('currentSessionInfo');
    if (currentSessionId) {
        sessionInfo.textContent = `Session: ${conversationTitle}`;
    } else {
        sessionInfo.textContent = 'No active conversation';
    }
}

function newConversation() {
    fetch('/start_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            currentSessionId = data.session_id;
            conversationTitle = 'New Conversation';
            updateSessionInfo();
            
            // Clear chat messages
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="message system">
                    🆕 New conversation started! Previous conversation has been saved.
                </div>
                <div class="message ai">
                    Hello! I'm your AI resume assistant. I can help you create a professional resume. What would you like to start with?
                </div>
            `;
            messageCount = 0;
            
            addMessage("✅ Started new conversation!", 'system');
        } else {
            addMessage("❌ Failed to start new conversation", 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error starting new conversation", 'system');
    });
}

function showConversationHistory() {
    fetch('/get_conversation_history')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.messages.length > 0) {
            const historyWindow = window.open('', 'ConversationHistory', 'width=800,height=600');
            let historyHTML = `
                <html>
                <head>
                    <title>Conversation History</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
                        .human { background: #e3f2fd; }
                        .ai { background: #f3e5f5; }
                        .timestamp { font-size: 0.8em; color: #666; }
                    </style>
                </head>
                <body>
                    <h2>Conversation History: ${data.metadata.title}</h2>
                    <p>Created: ${new Date(data.metadata.created_at).toLocaleString()}</p>
                    <p>Messages: ${data.metadata.message_count}</p>
                    <hr>
            `;
            
            data.messages.forEach(msg => {
                historyHTML += `
                    <div class="message ${msg.type}">
                        <strong>${msg.type === 'human' ? 'You' : 'AI'}:</strong> ${msg.content}
                        <div class="timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
                    </div>
                `;
            });
            
            historyHTML += '</body></html>';
            historyWindow.document.write(historyHTML);
        } else {
            addMessage("📋 No conversation history available", 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error loading conversation history", 'system');
    });
}

function loadConversations() {
    fetch('/list_conversations')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.conversations.length > 0) {
            let conversationList = "💬 Saved Conversations:\n\n";
            data.conversations.forEach((conv, index) => {
                conversationList += `${index + 1}. ${conv.title}\n`;
                conversationList += `   Created: ${new Date(conv.created_at).toLocaleDateString()}\n`;
                conversationList += `   Messages: ${conv.message_count}\n\n`;
            });
            
            const choice = prompt(conversationList + "Enter conversation number to load (or cancel):");
            if (choice && !isNaN(choice)) {
                const selectedIndex = parseInt(choice) - 1;
                if (selectedIndex >= 0 && selectedIndex < data.conversations.length) {
                    switchToConversation(data.conversations[selectedIndex].session_id);
                }
            }
        } else {
            addMessage("💬 No saved conversations found", 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error loading conversations", 'system');
    });
}

function switchToConversation(sessionId) {
    fetch('/switch_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            currentSessionId = data.session_id;
            addMessage(`✅ ${data.message}`, 'system');
            
            // Load conversation history
            loadConversationHistory();
        } else {
            addMessage("❌ Failed to switch conversation", 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error switching conversation", 'system');
    });
}

function loadConversationHistory() {
    fetch('/get_conversation_history')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="message system">
                    📋 Loaded conversation: ${data.metadata.title}
                </div>
            `;
            
            data.messages.forEach(msg => {
                addMessage(msg.content, msg.type === 'human' ? 'user' : 'ai');
            });
            
            conversationTitle = data.metadata.title;
            updateSessionInfo();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error loading conversation history", 'system');
    });
}

function exportConversation() {
    fetch('/get_conversation_history')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.messages.length > 0) {
            let exportText = `Conversation: ${data.metadata.title}\n`;
            exportText += `Created: ${new Date(data.metadata.created_at).toLocaleString()}\n`;
            exportText += `Messages: ${data.metadata.message_count}\n\n`;
            exportText += "=".repeat(50) + "\n\n";
            
            data.messages.forEach(msg => {
                exportText += `${msg.type === 'human' ? 'You' : 'AI'}: ${msg.content}\n`;
                exportText += `Time: ${new Date(msg.timestamp).toLocaleString()}\n\n`;
            });
            
            const blob = new Blob([exportText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `conversation_${data.metadata.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            
            addMessage("📤 Conversation exported successfully!", 'system');
        } else {
            addMessage("📤 No conversation to export", 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error exporting conversation", 'system');
    });
}

// =====================================================
// LATEX GENERATION FUNCTIONS
// =====================================================

function generateLatexResume() {
    addMessage("🎯 Compiling LaTeX from output.tex file...", 'system');
    
    // Show loading state
    const generateButton = document.querySelector('[onclick="generateLatexResume()"]');
    const originalText = generateButton.innerHTML;
    generateButton.innerHTML = '⏳ Compiling...';
    generateButton.disabled = true;
    
    fetch('/compile_resume', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessage("✅ " + data.message, 'system');
            
            // If PDF was generated, reload the PDF viewer
            if (data.pdf_generated) {
                setTimeout(() => {
                    loadPDFEmbed();
                    addMessage("📄 Resume PDF updated and refreshed in preview!", 'system');
                }, 500);
            } else {
                addMessage("📝 LaTeX file saved. Manual compilation required for PDF.", 'system');
            }
        } else {
            addMessage("❌ " + data.message, 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error compiling resume. Please check if LaTeX is installed and output.tex exists.", 'system');
    })
    .finally(() => {
        // Restore button state
        generateButton.innerHTML = originalText;
        generateButton.disabled = false;
    });
}

function testLLMTool() {
    addMessage("🧪 Testing LLM tool integration...", 'system');
    
    fetch('/test_tool', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addMessage(`✅ LLM Tool Test Results:
📄 Response: ${data.response_content.substring(0, 200)}...
🔧 Has tool calls: ${data.has_tool_calls}
📞 Tool calls count: ${data.tool_calls_count}
🛠️ Tools used: ${data.tool_calls.map(tc => tc.name).join(', ') || 'None'}`, 'system');
            
            if (data.tool_calls_count > 0) {
                addMessage("✅ Tool integration working! LLM can call the write_latex tool.", 'system');
            } else {
                addMessage("⚠️ LLM responded but didn't use tools. Check system prompt.", 'system');
            }
        } else {
            addMessage("❌ Tool test failed: " + data.message, 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error testing tool integration.", 'system');
    });
}

function debugMemory() {
    addMessage("🔍 Checking memory status...", 'system');
    
    fetch('/debug_memory', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const info = data.debug_info;
            let message = `🧠 Memory Debug Info:
📊 Session ID: ${info.current_session_id || 'None'}
📈 Total conversations: ${info.total_conversations}`;

            if (info.current_conversation) {
                const conv = info.current_conversation;
                message += `
💬 Current conversation:
   📝 Messages: ${conv.message_count}
   📅 Created: ${conv.metadata.created_at}
   🏷️ Title: ${conv.metadata.title}`;

                if (conv.message_sizes && conv.message_sizes.length > 0) {
                    message += `
📏 Recent message sizes:`;
                    conv.message_sizes.forEach((msg, i) => {
                        const truncated = msg.original_length !== msg.length ? ' (truncated)' : '';
                        message += `\n   ${i+1}. ${msg.type}: ${msg.length} chars${truncated}`;
                    });
                }
            } else {
                message += `\n⚠️ No active conversation`;
            }

            addMessage(message, 'system');
        } else {
            addMessage("❌ Memory debug failed: " + data.error, 'system');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage("❌ Error checking memory status.", 'system');
    });
}

// =====================================================
// KEYBOARD SHORTCUTS
// =====================================================

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                setViewMode('split');
                break;
            case '2':
                e.preventDefault();
                setViewMode('chat');
                break;
            case '3':
                e.preventDefault();
                setViewMode('pdf');
                break;
            case 'n':
                e.preventDefault();
                newConversation();
                break;
            case 'h':
                e.preventDefault();
                showConversationHistory();
                break;
            case 'g':
                e.preventDefault();
                generateLatexResume();
                break;
            case 'd':
                e.preventDefault();
                debugMemory();
                break;
        }
    }
}); 
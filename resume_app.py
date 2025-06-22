from flask import Flask, send_file, request, jsonify, session
import os
import uuid
from datetime import datetime
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Global conversation storage - Simple implementation
conversation_messages = {}  # session_id -> list of messages
conversation_metadata = {}  # session_id -> metadata (timestamp, title, etc.)

# Initialize LangChain Groq client
llm = None
try:
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7,
            max_tokens=500,
            timeout=30,
            max_retries=2,
            api_key=api_key  # Using environment variable for security
        )
        print("✅ LangChain Groq client initialized successfully!")
        print(f"🤖 Using model: llama3-8b-8192")
    else:
        print("⚠️  GROQ_API_KEY not found in environment variables")
        print("💡 Please create a .env file with your GROQ_API_KEY")
        print("🔗 Get your API key from: https://console.groq.com/keys")
except Exception as e:
    print(f"❌ Error initializing LangChain Groq client: {e}")

def get_or_create_conversation_memory(session_id):
    """Get existing conversation messages or create a new conversation"""
    if session_id not in conversation_messages:
        conversation_messages[session_id] = []
        conversation_metadata[session_id] = {
            'created_at': datetime.now().isoformat(),
            'title': 'New Conversation',
            'message_count': 0
        }
    return conversation_messages[session_id]

def save_conversation_message(session_id, human_message, ai_message):
    """Save messages to conversation storage"""
    messages = get_or_create_conversation_memory(session_id)
    
    # Add human message
    messages.append({
        'type': 'human',
        'content': human_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Add AI message
    messages.append({
        'type': 'ai',
        'content': ai_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Update metadata
    conversation_metadata[session_id]['message_count'] += 2
    conversation_metadata[session_id]['last_updated'] = datetime.now().isoformat()
    
    # Auto-generate title from first message if still "New Conversation"
    if (conversation_metadata[session_id]['title'] == 'New Conversation' and 
        conversation_metadata[session_id]['message_count'] == 2):
        title = human_message[:50] + "..." if len(human_message) > 50 else human_message
        conversation_metadata[session_id]['title'] = title

@app.route('/start_session', methods=['POST'])
def start_session():
    """Start a new conversation session"""
    session_id = str(uuid.uuid4())
    session['conversation_id'] = session_id
    
    # Initialize memory for the session
    get_or_create_conversation_memory(session_id)
    
    return jsonify({
        'session_id': session_id,
        'status': 'success',
        'message': 'New conversation started!'
    })

@app.route('/get_conversation_history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for current session"""
    session_id = session.get('conversation_id')
    
    if not session_id or session_id not in conversation_messages:
        return jsonify({
            'messages': [],
            'session_id': None,
            'message': 'No active conversation'
        })
    
    messages = conversation_messages[session_id]
    
    return jsonify({
        'messages': messages,
        'session_id': session_id,
        'metadata': conversation_metadata.get(session_id, {}),
        'status': 'success'
    })

@app.route('/list_conversations', methods=['GET'])
def list_conversations():
    """List all conversation sessions"""
    conversations = []
    for session_id, metadata in conversation_metadata.items():
        conversations.append({
            'session_id': session_id,
            'title': metadata['title'],
            'created_at': metadata['created_at'],
            'last_updated': metadata.get('last_updated', metadata['created_at']),
            'message_count': metadata['message_count']
        })
    
    # Sort by last updated (most recent first)
    conversations.sort(key=lambda x: x['last_updated'], reverse=True)
    
    return jsonify({
        'conversations': conversations,
        'total_count': len(conversations),
        'status': 'success'
    })

@app.route('/switch_conversation', methods=['POST'])
def switch_conversation():
    """Switch to a different conversation"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in conversation_messages:
        return jsonify({
            'error': 'Conversation not found',
            'status': 'error'
        }), 404
    
    session['conversation_id'] = session_id
    
    return jsonify({
        'session_id': session_id,
        'status': 'success',
        'message': f'Switched to conversation: {conversation_metadata[session_id]["title"]}'
    })

@app.route('/delete_conversation', methods=['DELETE'])
def delete_conversation():
    """Delete a conversation"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id in conversation_messages:
        del conversation_messages[session_id]
        del conversation_metadata[session_id]
        
        # If this was the current session, clear it
        if session.get('conversation_id') == session_id:
            session.pop('conversation_id', None)
        
        return jsonify({
            'status': 'success',
            'message': 'Conversation deleted'
        })
    
    return jsonify({
        'error': 'Conversation not found',
        'status': 'error'
    }), 404

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and generate AI responses using LangChain Groq with memory"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        if not llm:
            return jsonify({
                'response': "❌ Groq API is not connected. Please check your API key configuration.\n\n" +
                           "📋 Setup steps:\n" +
                           "1. Get your API key from https://console.groq.com/keys\n" +
                           "2. Create a .env file in the Niti-AI directory\n" +
                           "3. Add: GROQ_API_KEY=your_api_key_here\n" +
                           "4. Restart the application",
                'error': 'API_NOT_CONFIGURED'
            }), 503
        
        # Get or create session
        session_id = session.get('conversation_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['conversation_id'] = session_id
        
        # Get conversation messages
        conversation_history = get_or_create_conversation_memory(session_id)
        
        # Create a system prompt for resume building
        system_prompt = """You are an expert LaTeX resume generator and AI resume building assistant. Your job is to help users create professional resumes by:

**PRIMARY RESPONSIBILITIES:**
1. Gathering information about their education, experience, skills, and achievements
2. Providing guidance on resume formatting and content
3. Asking relevant follow-up questions to get complete information
4. Being encouraging and professional

**WHEN GENERATING RESUMES:**
- ALWAYS follow the exact LaTeX template structure provided in the codebase
- NEVER generate single-line LaTeX code - maintain proper indentation and line breaks
- Use only the defined custom commands: \\resumeSubheading, \\resumeProjectHeading, \\resumeItem, etc.
- Maintain exact section order: Heading, Professional Summary, Technical Skills, Experience, Projects, Achievements, Certifications, Education
- Use FontAwesome icons (\\faEnvelope, \\faPhone, \\faLinkedin, \\faGithub) in contact information
- Ensure proper spacing with \\vspace commands
- Generate clean, well-structured, multi-line LaTeX code

**ALIGNMENT AND INDENTATION RULES:**
- Use consistent 2-space or 4-space indentation for nested elements
- Align \\resumeItem entries with proper indentation under \\resumeItemListStart
- Align \\resumeSubheading parameters on separate lines with consistent spacing
- Maintain proper alignment for tabular environments and custom commands
- Keep section headers (\\section{}) at the left margin
- Indent all content within environments (\\begin{} ... \\end{})
- Align closing braces } with their corresponding opening elements
- Use consistent spacing between sections and subsections

**CONVERSATION GUIDELINES:**
- Keep responses concise but helpful (under 200 words)
- Ask for specific details that would make their resume stronger
- Be conversational and supportive
- Reference previous messages from conversation history
- Guide users through the resume creation process step by step

Remember: Always prioritize proper LaTeX formatting and structure when generating resumes."""

        # Build messages with conversation history
        messages = [SystemMessage(content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history:
            if msg['type'] == 'human':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['type'] == 'ai':
                messages.append(AIMessage(content=msg['content']))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Make API call using LangChain
        response = llm.invoke(messages)
        
        ai_response = response.content
        
        # Save the conversation to memory
        save_conversation_message(session_id, user_message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'status': 'success',
            'session_id': session_id,
            'conversation_title': conversation_metadata[session_id]['title']
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat endpoint: {e}")
        
        # Provide more specific error messages
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            return jsonify({
                'response': "❌ Invalid API key. Please check your GROQ_API_KEY in the .env file.\n\n" +
                           "🔑 Make sure your API key is correct and active.",
                'error': 'INVALID_API_KEY'
            }), 401
        elif "429" in error_msg or "rate_limit" in error_msg.lower():
            return jsonify({
                'response': "⏳ Rate limit exceeded. Please wait a moment and try again.",
                'error': 'RATE_LIMIT'
            }), 429
        else:
            return jsonify({
                'response': f"❌ Error generating response: {error_msg}",
                'error': 'API_ERROR'
            }), 500

@app.route('/')
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Resume Builder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }

        .container {
            display: flex;
            height: 100vh;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        /* Panel States */
        .chat-panel {
            width: 45%;
            display: flex;
            flex-direction: column;
            background: #f8f9fa;
            border-right: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }

        .pdf-panel {
            width: 55%;
            display: flex;
            flex-direction: column;
            background: #ffffff;
            transition: all 0.3s ease;
        }

        /* Hidden state */
        .chat-panel.hidden {
            width: 0;
            min-width: 0;
            overflow: hidden;
        }

        .pdf-panel.hidden {
            width: 0;
            min-width: 0;
            overflow: hidden;
        }

        /* Expanded states */
        .chat-panel.expanded {
            width: 100%;
        }

        .pdf-panel.expanded {
            width: 100%;
        }

        /* Chat Interface Styles */
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: relative;
        }

        .chat-header h1 {
            font-size: 1.8em;
            margin-bottom: 5px;
        }

        .chat-header p {
            opacity: 0.9;
            font-size: 0.9em;
        }

        .panel-controls {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            gap: 5px;
        }
        
        .chat-header .panel-controls {
            right: 15px;
        }
        
        .pdf-header .panel-controls {
            right: 15px;
        }

        .panel-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 6px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.3s ease;
        }

        .panel-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 85%;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease-in;
        }

        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .message.ai {
            background: #e9ecef;
            color: #333;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }

        .message.system {
            background: #d4edda;
            color: #155724;
            text-align: center;
            margin: 10px auto;
            font-size: 0.9em;
            max-width: 70%;
        }

        .quick-actions {
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }

        .quick-actions h4 {
            margin-bottom: 10px;
            color: #495057;
            font-size: 0.9em;
        }

        .action-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .action-button {
            background: #e9ecef;
            color: #495057;
            border: 1px solid #ced4da;
            padding: 6px 12px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.3s ease;
        }

        .action-button:hover {
            background: #dee2e6;
            border-color: #adb5bd;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        .chat-input-container {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }

        .chat-input {
            display: flex;
            gap: 10px;
        }

        .chat-input textarea {
            flex: 1;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            font-size: 14px;
            resize: none;
            outline: none;
            transition: border-color 0.3s ease;
            font-family: inherit;
        }

        .chat-input textarea:focus {
            border-color: #667eea;
        }

        .send-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            font-size: 14px;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }

        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        /* PDF Viewer Styles */
        .pdf-header {
            background: #343a40;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        .pdf-title {
            font-size: 1.2em;
            font-weight: 600;
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
        }

        .pdf-controls {
            display: flex;
            gap: 10px;
        }

        .pdf-button {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            transition: background-color 0.3s ease;
        }

        .pdf-button:hover {
            background: #5a6268;
        }

        .pdf-button.primary {
            background: #007bff;
        }

        .pdf-button.primary:hover {
            background: #0056b3;
        }

        .pdf-viewer {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
            position: relative;
        }

        .pdf-container {
            width: 100%;
            height: 100%;
            border: none;
            background: white;
        }

        .pdf-placeholder {
            text-align: center;
            color: #6c757d;
            padding: 40px;
        }

        .pdf-placeholder .icon {
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.5;
        }

        .pdf-placeholder h3 {
            margin-bottom: 10px;
            font-size: 1.5em;
        }

        .pdf-placeholder p {
            font-size: 1em;
            line-height: 1.5;
        }

        .fallback-link {
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px;
            transition: background-color 0.3s ease;
        }

        .fallback-link:hover {
            background: #0056b3;
        }

        /* Fullscreen mode */
        .fullscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 999;
            background: white;
        }

        .fullscreen .pdf-viewer {
            height: calc(100vh - 60px);
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .chat-panel, .pdf-panel {
                width: 100% !important;
            }
            
            .chat-panel {
                height: 60vh;
            }
            
            .pdf-panel {
                height: 40vh;
            }
        }
    </style>
</head>
<body>
    <div class="container" id="mainContainer">
        <!-- Chat Interface -->
        <div class="chat-panel" id="chatPanel">
            <div class="chat-header">
                <div class="panel-controls">
                    <button class="panel-btn" onclick="setViewMode('split')" title="Split View">⚌ Split</button>
                    <button class="panel-btn" onclick="setViewMode('chat')" title="Chat Only">💬 Chat</button>
                    <button class="panel-btn" onclick="setViewMode('pdf')" title="PDF Only">📄 PDF</button>
                </div>
                <h1>🤖 AI Resume Builder</h1>
                <p>Tell me about your experience, skills, and achievements</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message system">
                    👋 Welcome! I'm here to help you create a professional resume. Let's start by telling me about yourself.
                </div>
                <div class="message ai">
                    Hello! I'm your AI resume assistant. I can help you create a professional resume based on your:
                    <br><br>
                    • Education background
                    <br>• Work experience
                    <br>• Skills and certifications
                    <br>• Projects and achievements
                    <br><br>
                    What would you like to start with? Try the quick action buttons below or just tell me about yourself!
                </div>
                <div class="message system">
                    📄 Your existing resume should be loading in the preview. Use the view controls in the chat header to customize your layout!
                </div>
            </div>
            
            <div class="quick-actions">
                <h4>🚀 Quick Actions:</h4>
                <div class="action-buttons">
                    <button class="action-button" onclick="addTemplate('education')">🎓 Add Education</button>
                    <button class="action-button" onclick="addTemplate('experience')">💼 Add Experience</button>
                    <button class="action-button" onclick="addTemplate('skills')">⚡ Add Skills</button>
                    <button class="action-button" onclick="addTemplate('projects')">🛠️ Add Projects</button>
                    <button class="action-button" onclick="addTemplate('certifications')">🏆 Add Certifications</button>
                </div>
            </div>
            
            <div class="conversation-controls" style="padding: 15px 20px; background: #f8f9fa; border-top: 1px solid #e9ecef;">
                <h4 style="margin-bottom: 10px; color: #495057; font-size: 0.9em;">💾 Conversation:</h4>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="action-button" onclick="newConversation()" title="Start new conversation">🆕 New Chat</button>
                    <button class="action-button" onclick="showConversationHistory()" title="View conversation history">📋 History</button>
                    <button class="action-button" onclick="loadConversations()" title="Load saved conversations">💬 Saved</button>
                    <button class="action-button" onclick="exportConversation()" title="Export current conversation">📤 Export</button>
                </div>
                <div id="conversationInfo" style="margin-top: 8px; font-size: 0.8em; color: #6c757d;">
                    <span id="currentSessionInfo">No active conversation</span>
                </div>
            </div>
            
            <div class="loading" id="loadingIndicator">
                <div class="spinner"></div>
                <p>Generating your resume...</p>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input">
                    <textarea 
                        id="messageInput" 
                        placeholder="Type your message here... (e.g., 'I have a Bachelor's in Computer Science from MIT')"
                        rows="3"
                    ></textarea>
                    <button class="send-button" id="sendButton" onclick="sendMessage()">
                        Send 🚀
                    </button>
                </div>
            </div>
        </div>
        
        <!-- PDF Viewer -->
        <div class="pdf-panel" id="pdfPanel">
            <div class="pdf-header">
                <div class="pdf-title">📄 Live Resume Preview</div>
                <div class="pdf-controls">
                    <button class="pdf-button" onclick="refreshPDF()">🔄 Refresh</button>
                    <button class="pdf-button" onclick="openPDFNewTab()">👁️ View PDF</button>
                    <button class="pdf-button primary" onclick="downloadPDF()">📥 Download</button>
                </div>
                <div class="panel-controls" style="right: 15px;">
                    <button class="panel-btn" onclick="setViewMode('split')" title="Split View">⚌ Split</button>
                    <button class="panel-btn" onclick="setViewMode('chat')" title="Chat Only">💬 Chat</button>
                    <button class="panel-btn" onclick="setViewMode('pdf')" title="PDF Only">📄 PDF</button>
                </div>
            </div>
            
            <div class="pdf-viewer" id="pdfViewer">
                <div class="pdf-placeholder" id="pdfPlaceholder">
                    <div class="icon">📄</div>
                    <h3>Loading Resume...</h3>
                    <p>If the PDF doesn't appear, your browser might not support embedded PDFs.</p>
                    <a href="output.pdf" target="_blank" class="fallback-link">📄 View PDF in New Tab</a>
                    <br>
                    <button class="fallback-link" onclick="loadPDFEmbed()" style="border: none; cursor: pointer;">🔄 Try Loading Again</button>
                </div>
            </div>
        </div>
    </div>

    <script>
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
        });

        // View Mode Functions
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
                        <button class="fallback-link" onclick="tryIframeMethod()" style="border: none; cursor: pointer;">🔄 Try Alternative Method</button>
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
                    
                    // Check if we should refresh PDF based on content keywords
                    if (messageCount > 2 && (
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

        function simulateAIResponse(userMessage) {
            const responses = [
                "Great! I've noted that information. Could you tell me more about your work experience?",
                "Excellent! I'm building your resume section by section. What about your key skills?",
                "Perfect! I'm updating your resume now. The PDF will refresh shortly.",
                "Thanks for the details! I've added that to your resume. Anything else you'd like to include?",
                "Wonderful! Your resume is looking great. Let me generate the updated version for you.",
                "I've processed that information. Would you like to add any projects or certifications?",
                "That's valuable information! I'm incorporating it into your resume layout."
            ];
            
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse, 'ai');
            
            // Simulate PDF refresh after some messages
            if (messageCount > 2 && messageCount % 3 === 0) {
                setTimeout(() => {
                    refreshPDF();
                    addMessage("✅ Resume updated! Check the preview on the right.", 'system');
                }, 500);
            }
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

        function refreshPDF() {
            loadPDFEmbed();
            addMessage("🔄 PDF refreshed!", 'system');
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

        // Memory management functions
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
                    exportText += "=" * 50 + "\n\n";
                    
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

        // Initialize session info on page load
        document.addEventListener('DOMContentLoaded', function() {
            updateSessionInfo();
        });

        // Keyboard shortcuts
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
                }
            }
        });
    </script>
</body>
</html>"""

@app.route('/output.pdf')
def serve_pdf():
    """Serve the PDF file with proper headers"""
    if os.path.exists('output.pdf'):
        return send_file('output.pdf', 
                        as_attachment=False, 
                        mimetype='application/pdf',
                        download_name='resume.pdf')
    else:
        return "<h1>PDF not found</h1><p>The output.pdf file doesn't exist in the current directory.</p>", 404

@app.route('/download')
def download_pdf():
    """Download the PDF file"""
    if os.path.exists('output.pdf'):
        return send_file('output.pdf', as_attachment=True, download_name='resume.pdf')
    else:
        return "<h1>PDF not found</h1><p>The output.pdf file doesn't exist in the current directory.</p>", 404

if __name__ == '__main__':
    print("🚀 Starting AI Resume Builder with LangChain...")
    print("📁 Current directory:", os.getcwd())
    print("📄 Available files:", [f for f in os.listdir('.') if f.endswith(('.pdf', '.html'))])
    
    # Check if API key is configured
    if not os.getenv('GROQ_API_KEY'):
        print("\n⚠️  GROQ_API_KEY not found!")
        print("📋 Setup instructions:")
        print("1. Create a .env file in this directory (Niti-AI folder)")
        print("2. Add this line: GROQ_API_KEY=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")
        print("3. Restart the application")
        print("\n💡 The app will still run, but chat won't work until API key is configured.")
        print("🔒 Note: I moved your hardcoded API key to environment variables for security!")
    else:
        print("✅ GROQ_API_KEY found!")
    
    print("\n🌐 Open your browser and go to: http://localhost:5000")
    print("💡 Your existing output.pdf will be displayed in the preview!")
    print("📋 View Controls: Integrated in chat and PDF headers")
    print("⌨️  Keyboard Shortcuts: Ctrl+1/2/3 for view modes")
    print("🤖 LangChain + Groq AI chatbot is ready!")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

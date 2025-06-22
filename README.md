# AI Resume Builder

An intelligent resume builder powered by Google Gemini AI that generates professional LaTeX resumes with real-time compilation and PDF preview. The application features a modern web interface with conversation memory and LinkedIn integration capabilities.

## 🚀 Features

- **AI-Powered Resume Generation**: Uses Google Gemini 2.0 Flash model for intelligent resume creation
- **Real-time LaTeX Compilation**: Automatic compilation to PDF with live preview
- **Conversation Memory**: Maintains chat history across sessions
- **LinkedIn Integration**: Optional LinkedIn profile data fetching (when configured)
- **Professional Templates**: ATS-friendly LaTeX templates with modern formatting
- **Tool-Based Architecture**: LangChain tools for modular functionality
- **Responsive UI**: Clean, modern interface with keyboard shortcuts
- **Session Management**: Multiple conversation support with switching capability

## 📋 Prerequisites

### Required Software
- **Python 3.8+**
- **LaTeX Distribution** (one of the following):
  - [MiKTeX](https://miktex.org/download) (Windows)
  - [TeX Live](https://www.tug.org/texlive/) (Cross-platform)
  - [MacTeX](https://www.tug.org/mactex/) (macOS)

### API Keys
- **Google Gemini API Key** (required)
  - Get from: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **LinkedIn API Key** (optional)
  - Required for LinkedIn profile integration

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-builder.git
cd ai-resume-builder
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd RESUME-BUILDER-INITIAL-FULL-FUNCTIONING
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the `RESUME-BUILDER-INITIAL-FULL-FUNCTIONING` directory:

```env
# Google Gemini API (Required)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# LinkedIn API (Optional - for LinkedIn integration)
LINKEDIN_API_KEY=your_linkedin_api_key_here
```

### 5. Install LaTeX (if not already installed)

#### Windows (MiKTeX)
1. Download from [MiKTeX Downloads](https://miktex.org/download)
2. Run installer and follow instructions
3. The app will auto-detect common installation paths

#### macOS (MacTeX)
```bash
# Using Homebrew
brew install --cask mactex
```

#### Linux (TeX Live)
```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# CentOS/RHEL
sudo yum install texlive-scheme-full
```

## 🚀 Quick Start

### 1. Start the Application
```bash
cd RESUME-BUILDER-INITIAL-FULL-FUNCTIONING
python app_backend.py
```

### 2. Access the Web Interface
Open your browser and navigate to:
```
http://localhost:5001
```

### 3. Create Your First Resume
1. Click "Start New Chat" 
2. Type: "Create my resume with the following information: [your details]"
3. The AI will generate a professional LaTeX resume
4. View the PDF preview in real-time
5. Download when satisfied

## 💬 Usage Examples

### Basic Resume Creation
```
Create my resume:
- Name: John Doe
- Email: john.doe@email.com
- Phone: (555) 123-4567
- Experience: Software Engineer at Tech Corp (2020-2024)
- Education: BS Computer Science, University XYZ
- Skills: Python, JavaScript, React, SQL
```

### Resume Updates
```
Update my resume to add these new skills: Docker, Kubernetes, AWS
```

### LinkedIn Integration
```
Use LinkedIn tool to fetch my profile data and create a resume
```

## 🔧 Configuration

### LaTeX Compilation Settings
The app automatically detects LaTeX installations in common locations:
- Windows: MiKTeX paths
- macOS: MacTeX paths  
- Linux: TeX Live paths

### Conversation Memory
- Conversations are stored in-memory
- Maximum 100 messages per conversation
- Messages are auto-truncated if too long
- Session switching supported

### LinkedIn Integration
When LinkedIn API is configured:
1. Set `LINKEDIN_API_KEY` in `.env`
2. Use the dropdown in the UI to enable LinkedIn mode
3. The AI can fetch and use LinkedIn profile data

## 📁 Project Structure

```
RESUME-BUILDER-INITIAL-FULL-FUNCTIONING/
├── app_backend.py          # Main Flask application
├── requirements.txt        # Python dependencies
├── system_prompt.txt       # AI system prompt
├── templates/
│   └── index.html         # Main web interface
├── static/
│   ├── css/
│   │   └── style.css      # Styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── output.tex             # Generated LaTeX (auto-created)
├── output.pdf             # Generated PDF (auto-created)
└── .env                   # Environment variables (create this)
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/chat` | POST | Send message to AI |
| `/start_session` | POST | Start new conversation |
| `/get_conversation_history` | GET | Get chat history |
| `/list_conversations` | GET | List all conversations |
| `/switch_conversation` | POST | Switch between conversations |
| `/delete_conversation` | DELETE | Delete conversation |
| `/compile_resume` | POST | Compile existing LaTeX |
| `/output.pdf` | GET | Serve generated PDF |
| `/download` | GET | Download PDF file |

## ⌨️ Keyboard Shortcuts

- `Ctrl + 1`: Chat-only view
- `Ctrl + 2`: Split view (chat + PDF)
- `Ctrl + 3`: PDF-only view
- `Enter`: Send message
- `Shift + Enter`: New line in message

## 🔧 Troubleshooting

### Chat Not Working
- Verify `GOOGLE_API_KEY` is set correctly in `.env`
- Check API key validity at Google AI Studio
- Restart the application after adding environment variables

### PDF Compilation Issues
- Ensure LaTeX is properly installed
- Check LaTeX installation with: `pdflatex --version`
- Windows: Try running as administrator
- Check console logs for specific LaTeX errors

### LinkedIn Integration Issues
- Verify `LINKEDIN_API_KEY` in `.env`
- Check LinkedIn API quota and permissions
- Ensure proper API scopes are configured

## 🏗️ Development

### Adding New Features
1. Tools: Add to the tools section in `app_backend.py`
2. Routes: Add new Flask routes as needed
3. Frontend: Modify `static/js/app.js` and templates
4. Styling: Update `static/css/style.css`

### Testing
```bash
# Test LaTeX generation
curl -X POST http://localhost:5001/test_tool

# Debug memory
curl http://localhost:5001/debug_memory
```

## 📦 Dependencies

### Python Packages
- Flask: Web framework
- LangChain: AI orchestration
- Google Generative AI: AI model integration
- python-dotenv: Environment management

### External Tools
- LaTeX distribution (MiKTeX/TeX Live/MacTeX)
- PDF viewer (browser built-in)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) for AI orchestration
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [Flask](https://flask.palletsprojects.com/) for web framework
- LaTeX community for resume templates 
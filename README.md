# 🤖 AI Resume Builder

A modern web application that combines AI-powered resume generation with real-time PDF preview. Built with Flask and featuring an intuitive chat interface.

## ✨ Features

- **AI Chat Interface**: Interactive chat to gather your professional information
- **Real-time PDF Preview**: Live preview of your resume as it's being built
- **Flexible View Modes**: Split view, chat-only, PDF-only, and fullscreen modes
- **Quick Action Templates**: Pre-built templates for education, experience, skills, etc.
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **LaTeX Resume Generation**: Professional resume formatting using LaTeX
- **Download & Share**: Easy PDF download and sharing capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- LaTeX distribution (for PDF generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-resume-builder.git
   cd ai-resume-builder
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask
   ```

3. **Install LaTeX (if not already installed)**
   - **Windows**: Install MiKTeX or TeX Live
   - **macOS**: Install MacTeX
   - **Linux**: Install texlive-full

4. **Run the application**
   ```bash
   python resume_app.py
   ```
   
   Or use the Windows batch file:
   ```bash
   start_server.bat
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎮 Usage

### View Controls
- **⚌ Split**: Default split view (chat + PDF)
- **💬 Chat**: Chat-only mode
- **📄 PDF**: PDF-only mode
- **⛶ Full**: Fullscreen PDF mode

### Keyboard Shortcuts
- `Ctrl+1`: Split view
- `Ctrl+2`: Chat-only mode
- `Ctrl+3`: PDF-only mode
- `Ctrl+4`: Fullscreen PDF
- `Escape`: Exit fullscreen

### Quick Actions
Use the built-in templates to quickly add:
- 🎓 Education background
- 💼 Work experience
- ⚡ Skills and technologies
- 🛠️ Projects and achievements
- 🏆 Certifications

## 📁 Project Structure

```
ai-resume-builder/
├── resume_app.py          # Main Flask application
├── app.py                 # LaTeX resume generator
├── start_server.bat       # Windows startup script
├── output.pdf             # Generated resume (sample)
├── output.tex             # LaTeX source file
└── README.md              # This file
```

## 🔧 Configuration

The application includes a sample resume for "Raghunandhan G" to demonstrate functionality. To customize:

1. Edit the personal information in `app.py`
2. Modify the LaTeX template as needed
3. Run the resume generator to create your PDF

## 🌟 Features in Detail

### AI Chat Interface
- Natural language processing for resume building
- Context-aware responses and suggestions
- Progressive information gathering
- Real-time feedback and confirmations

### PDF Preview System
- Multiple fallback methods for browser compatibility
- Automatic refresh when resume is updated
- Download and external viewing options
- Mobile-responsive PDF display

### View Management
- Dynamic panel resizing and hiding
- Smooth animations and transitions
- Persistent view state management
- Keyboard navigation support

## 🔮 Future Enhancements

- [ ] Integration with actual LLM APIs (OpenAI, Claude, etc.)
- [ ] Multiple resume templates and themes
- [ ] Export to different formats (Word, HTML, etc.)
- [ ] Resume analysis and improvement suggestions
- [ ] Cloud storage and sharing capabilities
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask web framework
- LaTeX for professional document formatting
- Modern CSS and JavaScript for responsive UI
- Icons and emojis for enhanced user experience

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for job seekers worldwide** 
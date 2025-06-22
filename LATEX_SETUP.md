# LaTeX Setup Guide for Windows

## Problem
The application requires LaTeX to compile resume files to PDF. If you're seeing errors like:
- "pdflatex did not succeed"
- "MiKTeX cannot retrieve attributes"
- "pdflatex not found"

## Quick Fix Solutions

### Option 1: Install MiKTeX (Recommended)
1. **Download MiKTeX**: Go to https://miktex.org/download
2. **Install**: Run the installer with default settings
3. **Update**: After installation, open MiKTeX Console and update packages
4. **Add to PATH**: The installer should add MiKTeX to your system PATH automatically

### Option 2: Install TeX Live
1. **Download**: Go to https://www.tug.org/texlive/
2. **Install**: Follow the installation instructions
3. **Add to PATH**: Make sure the bin directory is in your system PATH

### Option 3: Use Online LaTeX Compiler (Temporary)
If you can't install LaTeX locally:
1. The app saves LaTeX code to `output.tex`
2. Copy the content and paste it into an online compiler like:
   - Overleaf (https://www.overleaf.com/)
   - ShareLaTeX
   - LaTeX Online

## Verify Installation
After installing, test in Command Prompt:
```cmd
pdflatex --version
```

You should see version information if LaTeX is properly installed.

## Troubleshooting

### Error: "MiKTeX cannot retrieve attributes"
- **Solution**: Run MiKTeX Console as administrator and update all packages
- Or reinstall MiKTeX with administrator privileges

### Error: "pdflatex not found"
- **Solution**: Add LaTeX to your system PATH:
  1. Search "Environment Variables" in Windows
  2. Edit System Environment Variables
  3. Add the MiKTeX bin directory (usually `C:\Program Files\MiKTeX\miktex\bin\x64\`)

### Error: "Permission denied"
- **Solution**: Run the application as administrator
- Or change the working directory permissions

## Application Features
Once LaTeX is working:
- ✅ AI can write LaTeX code to `output.tex`
- ✅ "Generate LaTeX" button compiles PDF
- ✅ PDF preview updates automatically
- ✅ Download compiled resume as PDF

## Need Help?
If you're still having issues:
1. Check the console output when starting the app
2. The app will test all common LaTeX installation paths
3. Look for specific error messages to identify the problem 
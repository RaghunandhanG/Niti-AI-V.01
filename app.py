import subprocess
import os

# Step 1: Define your LaTeX code
latex_code = r"""
%-------------------------
% Resume in Latex
%-------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\setlength{\multicolsep}{-3.0pt}
\setlength{\columnsep}{-1pt}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Section formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Unicode support for ATS
\pdfgentounicode=1

% Custom commands
\newcommand{\resumeItem}[1]{\item\small{{#1 \vspace{-2pt}}}}
\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textbf{\small #2} \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}

%-------------------------------------------
% RESUME STARTS HERE

\begin{document}

%----------HEADING----------
\begin{center}
    {\Huge \scshape Raghunandhan G} \\ \vspace{1pt}
    \small \raisebox{-0.1\height}\faEnvelope\ \href{mailto:raghunandhan.22me@kct.ac}{raghunandhan.22me@kct.ac} ~ 
    \raisebox{-0.1\height}\faPhone\ +91 8220398055 ~ 
    \href{https://linkedin.com/in/raghunandhang}{\raisebox{-0.2\height}\faLinkedin\ \underline{linkedin.com/in/raghunandhang}} ~ 
    \href{https://github.com/RaghunandhanG}{\raisebox{-0.2\height}\faGithub\ \underline{github.com/RaghunandhanG}}
    \vspace{-8pt}
\end{center}

%-----------PROFESSIONAL SUMMARY-----------
\section{Professional Summary}
Aspiring AI Engineer with a strong foundation in machine learning and a background in mechanical engineering, specializing in Natural Language Processing (NLP) and Generative AI. Deeply committed to continuous learning and innovation, I actively explore and apply advanced AI techniques. Possess strong mathematical capabilities that enable a deep understanding of machine learning algorithms and their practical implementations.

%-----------SKILLS-----------
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
    \item \textbf{Programming Languages}{: Python, Java}
    \item \textbf{Machine Learning Tools}{: Sci-Kit Learn,Tensorflow, NLTK, Keras}
    \item \textbf{Generative AI \& Agents}{: LangChain, LangGraph,Phidata}
    \item \textbf{Data Analysis}{: Exploratory Data Analysis, Data Visualization, Pandas, Seaborn,MySQL}
    \item \textbf{Development Tools}{: Streamlit, Git \& GitHub,}
    \item \textbf{Soft Skills}{: Communication, Critical Thinking, Presentation Skills}
\end{itemize}

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {AI Developer}{Sept. 2023 -- Present}
      {iQube, Kumaraguru College of Technology}{Coimbatore, Tamil Nadu}
      \resumeItemListStart
        \resumeItem{Collaborated with cross-functional teams to design and implement AI-driven solutions, enhancing operational efficiency.}
        \resumeItem{Developed and optimized ML models for classification, regression, and clustering tasks using TensorFlow and PyTorch.}
        \resumeItem{Performed exploratory data analysis (EDA) to inform model design and feature engineering.}
        \resumeItem{Implemented NLP techniques for text analysis, sentiment detection, and chatbots, enhancing user interactions.}
        \resumeItem{Deployed advanced object detection and computer vision models using Ultralytics for real-time applications.}
      \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
  \resumeSubHeadingListStart

    \resumeProjectHeading
      {\textbf{WelVision} $|$ \emph{Python, Computer Vision}}{Ongoing}
      \resumeItemListStart
        \resumeItem{Collaborating with WelVision to develop a computer vision-based solution using Ultralytics to detect defects in rollers of roller bearings.}
        \resumeItem{Improved defect identification efficiency and accuracy using advanced object detection techniques.}
      \resumeItemListEnd

    \resumeProjectHeading
      {\textbf{ML Automation} $|$ \emph{Python, Machine Learning}}{}
      \resumeItemListStart
        \resumeItem{Developed a user-friendly application enabling users to create basic ML models by uploading CSV files.}
      \resumeItemListEnd

    \resumeProjectHeading
      {\textbf{SGPA Calculator} $|$ \emph{Python, Automation}}{}
      \resumeItemListStart
        \resumeItem{Created an application that calculates SGPA by processing uploaded result PDFs.}
      \resumeItemListEnd

    \resumeProjectHeading
      {\textbf{Admission Enrollment Automation} $|$ \emph{Python, Web Automation}}{}
      \resumeItemListStart
        \resumeItem{Designed a system where scanned documents are uploaded to auto-fill student details on the website.}
      \resumeItemListEnd

  \resumeSubHeadingListEnd

  %-----------ACHIEVEMENTS-----------
\section{Achievements}
  \resumeSubHeadingListStart
    \resumeItem{\textbf{Mahatma Gandhi Merit Scholarship Award} (2023 -- 2024): Awarded for excellence in academics.}
    \resumeItem{\textbf{SN Bose Award} (2024 -- 2025): Recognized for emerging excellence in innovation in RIG.}
  \resumeSubHeadingListEnd
  
%-----------CERTIFICATIONS-----------
%-----------CERTIFICATIONS-----------
\section{Certifications}
  \resumeSubHeadingListStart
    \resumeItem{\textbf{AWS Academy Machine Learning Foundation}: Gained foundational knowledge of machine learning principles, tools, and practices on AWS.}
    \resumeItem{\textbf{Advanced Learning Algorithms – DeepLearning.AI}: Studied optimization algorithms, regularization, and deep learning best practices.}
    \resumeItem{\textbf{Unsupervised Learning, Recommenders, Reinforcement Learning – DeepLearning.AI}: Learned clustering, anomaly detection, recommendation systems, and RL fundamentals.}
     \resumeItem{\textbf{MySQL Problem Solving Basics – HackerRank}: Practiced SQL query formulation and database problem solving.}
    \resumeItem{\textbf{Intro to Deep Learning – Kaggle}: Understood the basics of deep learning and neural networks.}
    \resumeItem{\textbf{Python – Kaggle}: Built strong programming fundamentals in Python for data science tasks.}
    \resumeItem{\textbf{Data Visualization – Kaggle}: Explored essential data visualization techniques using Python libraries.}
  \resumeSubHeadingListEnd


%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Kumaraguru College of Technology}{Expected May 2026}
      {B.E. in Mechanical Engineering; \textbf{CGPA: 8.46}}{Coimbatore, Tamil Nadu}
  \resumeSubHeadingListEnd

\end{document}
"""

# Step 2: Write to a .tex file
with open("output.tex", "w", encoding="utf-8") as f:
    f.write(latex_code)

# Step 3: Compile using pdflatex
result = subprocess.run(
    ["pdflatex", "output.tex"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Step 4: Check the result
if result.returncode == 0:
    print("✅ PDF created successfully.")
else:
    print("❌ Error in PDF creation.")
    print(result.stderr)
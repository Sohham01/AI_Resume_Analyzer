# 📄 AI Resume Analyzer

An interactive, premium, AI-powered application designed to audit resumes, analyze keyword alignment with job descriptions, optimize experience statements using the STAR method, and practice custom mock interview questions. Powered by **Google's Gemini 2.5 Flash** and built with **Streamlit**.

---

## ✨ Key Features

1. **📊 ATS Resume Audit**
   - Drag-and-drop PDF resume uploading.
   - Live raw text extraction and validation.
   - Comprehensive ATS Scoring (color-coded based on alignment).
   - Card views identifying **Strengths**, **Weaknesses**, **Formatting Guidelines**, and cataloging **detected skills** alongside **missing industry skills**.
   - Downloadable Markdown audit reports.

2. **🎯 Job Description Matcher**
   - Side-by-side comparison of candidate resume contents against role requirements.
   - Alignment progress bar with matching scores.
   - Side-by-side tagging for **Matched Keywords** vs. **Missing Keywords**.
   - Actionable tailoring recommendations to narrow qualification gaps.

3. **✍️ STAR Bullet Optimizer**
   - Active sandbox for optimizing weak experience statements.
   - Generates three STAR-focused variations (Situation, Task, Action, Result) targeting:
     - *Technical Depth & Action*
     - *Business Impact & Metrics*
     - *Leadership & Scale*

4. **🎙️ Interview Prep Assistant**
   - Analyzes resume sections to generate 5 highly custom, challenging interview questions.
   - Collapsible response blue-prints mapping out ideal answers with the STAR breakdown.

---

## 🎨 Design System & Aesthetics
This application is styled with a custom CSS overlay establishing:
- **Google Font Integration**: Styled using `Outfit` typography.
- **Glassmorphic Theme**: Card panels (`.card`, `.score-card`) with blurred backdrop filters, minimal borders, and neon-indigo glow highlights.
- **Color-Coded Badges**: Dynamic chip tags differentiating tech skills (indigo), soft skills (green), and missing skills (red).
- **Responsive Elements**: Center-focused score metrics and custom scrollbar animations.

---

## 📂 Project Architecture

```
├── .streamlit/
│   └── secrets.toml          # API credentials (gitignored)
├── assets/
│   └── styles.css            # Custom CSS overlay
├── reports/                  # Generated audit files (gitignored)
├── uploads/                  # Temporary upload files (gitignored)
├── utils/
│   ├── __init__.py
│   ├── gemini_analyzer.py    # Gemini API prompt wrappers (JSON Response format)
│   └── pdf_reader.py         # PDF PLumber text extractor
├── .gitignore                # Git exclusions
├── app.py                    # Main UI entry point
├── README.md                 # Project documentation
└── requirements.txt          # Python packages list
```

---

## 🚀 Getting Started

### Prerequisites
Make sure you have Python 3.10+ installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
# On Windows (Command Prompt)
.venv\Scripts\activate.bat
# On Windows (PowerShell)
.venv\Scripts\Activate.ps1
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.streamlit/secrets.toml` file in the root folder and add your Gemini API Key:
```toml
GEMINI_API_KEY = "your-api-key-here"
```
*Note: You can also override the API Key inside the sidebar once the application is running.*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🔒 Security & Privacy
- Resumes are processed in-memory and are not permanently stored on any database.
- Make sure to keep `.streamlit/secrets.toml` excluded from public commits to avoid exposing your API credentials.

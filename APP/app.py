import json
import streamlit as st
from pathlib import Path

from utils.pdf_reader import extract_text
import utils.gemini_analyzer as analyzer


# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------
# STYLING & ASSETS
# ---------------------------------------------------
def load_css():
    css_file = Path(__file__).parent / "assets" / "styles.css"
    if css_file.exists():
        with open(css_file, encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    else:
        st.warning("Styling system CSS file not found.")

load_css()


# ---------------------------------------------------
# STATE MANAGEMENT
# ---------------------------------------------------
# Initialize session states to persist analysis outputs
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""
if "resume_name" not in st.session_state:
    st.session_state["resume_name"] = ""
if "ats_analysis" not in st.session_state:
    st.session_state["ats_analysis"] = None
if "jd_match" not in st.session_state:
    st.session_state["jd_match"] = None
if "bullet_optimizations" not in st.session_state:
    st.session_state["bullet_optimizations"] = None
if "interview_prep" not in st.session_state:
    st.session_state["interview_prep"] = None


# ---------------------------------------------------
# SIDEBAR CONFIGURATION
# ---------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ API Configuration")
    
    # Custom API Key Input
    custom_api_key = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        help="If left blank, the app will attempt to use the pre-configured global key.",
        placeholder="AIzaSy..."
    )
    
    # API Status Check
    default_key_exists = "GEMINI_API_KEY" in st.secrets
    active_key = custom_api_key if custom_api_key.strip() != "" else st.secrets.get("GEMINI_API_KEY", "")
    
    if active_key:
        st.success("✅ API Key Configured")
    else:
        st.error("❌ No API Key Configured. Please enter one above.")

    st.markdown("---")
    st.markdown("### 💡 App Quick Guide")
    st.markdown(
        """
        1. **Upload Resume**: Start in the **ATS Resume Audit** tab and upload a PDF resume.
        2. **Analyze ATS Fit**: Get a full audit of strengths, weaknesses, formatting suggestions, and skills.
        3. **JD Match**: Compare your resume to any job description to identify missing keywords.
        4. **Optimize Bullets**: Rewrite weak accomplishments into strong STAR statements.
        5. **Interview Prep**: Generate tailored interview questions based on your resume.
        """
    )
    
    # Reset button
    if st.button("🔄 Clear App Cache / Reset", use_container_width=True):
        st.session_state["resume_text"] = ""
        st.session_state["resume_name"] = ""
        st.session_state["ats_analysis"] = None
        st.session_state["jd_match"] = None
        st.session_state["bullet_optimizations"] = None
        st.session_state["interview_prep"] = None
        st.rerun()


# ---------------------------------------------------
# HERO / HEADER
# ---------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>📄 AI Resume Analyzer</h1>
        <p>Analyze your resume, optimize alignment with target job descriptions, rewrite bullet points with the STAR method, and practice custom interview questions — powered by Google Gemini AI.</p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------
# TABS SYSTEM
# ---------------------------------------------------
tab_ats, tab_jd, tab_bullet, tab_interview = st.tabs([
    "📊 ATS Resume Audit", 
    "🎯 Job Description Matcher", 
    "✍️ Bullet Point Optimizer", 
    "🎙️ Interview Prep Assistant"
])


# ---------------------------------------------------
# TAB 1: ATS Resume Audit
# ---------------------------------------------------
with tab_ats:
    st.markdown("<h2 class='section-title'>Analyze Resume ATS Score & Structure</h2>", unsafe_allow_html=True)
    
    col_upload, col_action = st.columns([3, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload your resume in PDF format:",
            type=["pdf"],
            help="Upload a single-page or multi-page PDF resume."
        )
        
    with col_action:
        st.write("")  # Spacing
        st.write("")  # Spacing
        btn_analyze = st.button("🔥 Run ATS Analysis", type="primary", use_container_width=True, disabled=uploaded_file is None)
        
    # PDF Parsing Logic
    if uploaded_file is not None:
        if st.session_state["resume_name"] != uploaded_file.name:
            with st.spinner("Extracting text from PDF resume..."):
                try:
                    text = extract_text(uploaded_file)
                    st.session_state["resume_text"] = text
                    st.session_state["resume_name"] = uploaded_file.name
                    # Clear previous analysis if a new file is uploaded
                    st.session_state["ats_analysis"] = None
                    st.session_state["jd_match"] = None
                    st.session_state["interview_prep"] = None
                    st.success(f"Successfully extracted text from '{uploaded_file.name}'!")
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
                    
        # Preview Text Expander
        if st.session_state["resume_text"] != "":
            with st.expander("🔍 Preview Extracted Resume Text"):
                st.text_area("Extracted Resume Text (Read-Only):", st.session_state["resume_text"], height=200, disabled=True)
                
    # Run API Analysis
    if btn_analyze and st.session_state["resume_text"] != "":
        with st.spinner("Gemini is auditing your resume..."):
            result = analyzer.analyze_resume(st.session_state["resume_text"], custom_api_key)
            if "error" in result:
                st.error(result["message"])
            else:
                st.session_state["ats_analysis"] = result
                st.success("ATS Analysis completed!")
                st.rerun()

    # Display ATS Report
    analysis = st.session_state["ats_analysis"]
    if analysis:
        # Score Class based on range
        score = analysis.get("ats_score", 0)
        score_class = "score-excellent" if score >= 75 else ("score-good" if score >= 50 else "score-needs-work")
        
        # Display Score Card in center
        st.markdown(
            f"""
            <div class="score-container">
                <div class="score-card {score_class}">
                    <div class="score-value">{score}/100</div>
                    <div class="score-label">Overall ATS Score</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Score explanation card
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">💡 Analysis Summary</div>
                <p style="margin-top: 10px; line-height: 1.6;">{analysis.get('score_explanation', '')}</p>
                <hr style="border-color: rgba(255,255,255,0.08); margin: 15px 0;">
                <p style="font-style: italic; font-weight: 300;">{analysis.get('summary', '')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Detailed feedback columns
        col_feedback1, col_feedback2 = st.columns(2)
        
        with col_feedback1:
            # Strengths
            strengths_html = "".join([f"<li>{s}</li>" for s in analysis.get("strengths", [])])
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">✅ Strong Aspects</div>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        {strengths_html if strengths_html else '<li>No major strengths detected.</li>'}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Formatting Improvements
            format_html = "".join([f"<li>{f}</li>" for f in analysis.get("formatting_improvements", [])])
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">🛠️ Formatting & ATS Parsability</div>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        {format_html if format_html else '<li>Formatting looks clean and parsable.</li>'}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with col_feedback2:
            # Weaknesses
            weaknesses_html = "".join([f"<li>{w}</li>" for w in analysis.get("weaknesses", [])])
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">⚠️ Gaps & Areas to Improve</div>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        {weaknesses_html if weaknesses_html else '<li>No major weaknesses found.</li>'}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Skills Catalog
            tech_tags = "".join([f"<span class='tag'>{skill}</span>" for skill in analysis.get("technical_skills", [])])
            soft_tags = "".join([f"<span class='tag tag-soft'>{skill}</span>" for skill in analysis.get("soft_skills", [])])
            missing_tags = "".join([f"<span class='tag tag-missing'>{skill}</span>" for skill in analysis.get("missing_skills", [])])
            
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">🔑 Technical Skills Detected</div>
                    <div class="tag-container">{tech_tags if tech_tags else 'None detected.'}</div>
                </div>
                
                <div class="card">
                    <div class="card-title">🗣️ Soft Skills Detected</div>
                    <div class="tag-container">{soft_tags if soft_tags else 'None detected.'}</div>
                </div>
                
                <div class="card">
                    <div class="card-title">❌ Expected Skills Missing</div>
                    <p style="font-size: 13px; color: #94a3b8; margin-bottom: 8px;">These skills are commonly expected for your profile but were absent:</p>
                    <div class="tag-container">{missing_tags if missing_tags else 'No missing skills identified.'}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Export Report
        st.markdown("### 📥 Export ATS Report")
        report_markdown = f"""# ATS Resume Audit Report - {st.session_state["resume_name"]}
        
## Overall Score: {score}/100

### Executive Summary
{analysis.get('summary', '')}

### Explanation
{analysis.get('score_explanation', '')}

### Key Strengths
{chr(10).join(['- ' + s for s in analysis.get('strengths', [])])}

### Areas for Improvement
{chr(10).join(['- ' + w for w in analysis.get('weaknesses', [])])}

### Technical Skills Found
{', '.join(analysis.get('technical_skills', []))}

### Soft Skills Found
{', '.join(analysis.get('soft_skills', []))}

### Recommended Missing Skills
{', '.join(analysis.get('missing_skills', []))}

### Formatting Recommendations
{chr(10).join(['- ' + f for f in analysis.get('formatting_improvements', [])])}
"""
        st.download_button(
            label="Download Detailed PDF/Markdown Report",
            data=report_markdown,
            file_name=f"ATS_Audit_Report_{Path(st.session_state['resume_name']).stem}.md",
            mime="text/markdown",
            use_container_width=True
        )


# ---------------------------------------------------
# TAB 2: Job Description Matcher
# ---------------------------------------------------
with tab_jd:
    st.markdown("<h2 class='section-title'>Compare Resume with Target Job Description</h2>", unsafe_allow_html=True)
    
    if st.session_state["resume_text"] == "":
        st.warning("⚠️ Please upload a resume in the first tab ('ATS Resume Audit') before matching against a Job Description.")
    else:
        # User JD Input
        jd_input = st.text_area(
            "Paste the Job Description / Role requirements here:",
            height=250,
            placeholder="Requirements:\n- 3+ years experience with Python...\n- Expertise in database design..."
        )
        
        btn_match = st.button("🎯 Analyze Keyword Match", type="primary", use_container_width=True, disabled=jd_input.strip() == "")
        
        if btn_match:
            with st.spinner("Comparing resume contents with Job Description requirements..."):
                match_result = analyzer.match_job_description(st.session_state["resume_text"], jd_input, custom_api_key)
                if "error" in match_result:
                    st.error(match_result["message"])
                else:
                    st.session_state["jd_match"] = match_result
                    st.success("Comparison completed!")
                    st.rerun()
                    
        # Display Match Results
        jd_match = st.session_state["jd_match"]
        if jd_match:
            match_score = jd_match.get("match_score", 0)
            
            # Color indicator
            bar_color = "#10b981" if match_score >= 75 else ("#f59e0b" if match_score >= 50 else "#ef4444")
            
            st.markdown("### 📊 Matching Metrics")
            st.markdown(
                f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 5px;">
                        <span>Keyword & Skill Alignment</span>
                        <span style="color: {bar_color};">{match_score}% Match</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" style="width: {match_score}%; background: {bar_color};"></div>
                    </div>
                    <div class="card-title">🔍 Alignment Summary</div>
                    <p style="line-height: 1.6; margin-top: 10px;">{jd_match.get('match_explanation', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            col_keywords1, col_keywords2 = st.columns(2)
            
            with col_keywords1:
                matched_tags = "".join([f"<span class='tag'>{kw}</span>" for kw in jd_match.get("matched_keywords", [])])
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title" style="color: #10b981;">✅ Matched Keywords ({len(jd_match.get("matched_keywords", []))})</div>
                        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 10px;">These skills from the Job Description were found in your resume:</p>
                        <div class="tag-container">{matched_tags if matched_tags else 'No direct keywords matched.'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_keywords2:
                missing_tags = "".join([f"<span class='tag tag-missing'>{kw}</span>" for kw in jd_match.get("missing_keywords", [])])
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title" style="color: #fca5a5;">❌ Missing Keywords ({len(jd_match.get("missing_keywords", []))})</div>
                        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 10px;">These critical keywords are present in the JD but missing from your resume:</p>
                        <div class="tag-container">{missing_tags if missing_tags else 'None! Perfect match.'}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            # Tailoring suggestions
            suggestions_html = "".join([f"<li>{s}</li>" for s in jd_match.get("tailoring_suggestions", [])])
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">✍️ Tailoring Recommendations</div>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        {suggestions_html if suggestions_html else '<li>No suggestions needed. Your resume matches perfectly.</li>'}
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------
# TAB 3: Bullet Point Optimizer
# ---------------------------------------------------
with tab_bullet:
    st.markdown("<h2 class='section-title'>STAR Method Bullet Point Optimizer</h2>", unsafe_allow_html=True)
    st.write(
        "Paste a weak bullet point or job description from your experience section. "
        "The optimizer will reframe it into an action-verb and results-oriented **STAR statement** (Situation, Task, Action, Result)."
    )
    
    # Input area
    bullet_input = st.text_area(
        "Enter your resume bullet point to optimize:",
        height=100,
        placeholder="Example: I worked on a team that built the database API."
    )
    
    btn_optimize = st.button("✍️ Optimize Statement", type="primary", use_container_width=True, disabled=bullet_input.strip() == "")
    
    if btn_optimize:
        with st.spinner("Rewriting bullet point using the STAR method..."):
            opt_result = analyzer.optimize_bullet_point(bullet_input, custom_api_key)
            if "error" in opt_result:
                st.error(opt_result["message"])
            else:
                st.session_state["bullet_optimizations"] = opt_result
                st.success("Optimizations generated!")
                st.rerun()
                
    # Display Optimizations
    opt_data = st.session_state["bullet_optimizations"]
    if opt_data:
        st.markdown("### 🛠️ Optimized Variations")
        st.markdown(f"**Original Statement:** *\"{opt_data.get('original', '')}\"*")
        st.write("")
        
        for idx, opt in enumerate(opt_data.get("optimizations", [])):
            focus = opt.get("focus", "Variation")
            text = opt.get("text", "")
            
            st.markdown(
                f"""
                <div class="card">
                    <div style="font-weight: bold; font-size: 15px; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.05em;">👉 Focus: {focus}</div>
                    <div style="font-size: 17px; margin-top: 10px; line-height: 1.5; color: #ffffff; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border-left: 3px solid #818cf8;">
                        "{text}"
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------
# TAB 4: Interview Prep Assistant
# ---------------------------------------------------
with tab_interview:
    st.markdown("<h2 class='section-title'>Targeted Interview Prep Questions</h2>", unsafe_allow_html=True)
    
    if st.session_state["resume_text"] == "":
        st.warning("⚠️ Please upload and parse your resume in the 'ATS Resume Audit' tab to unlock tailored interview preparation.")
    else:
        st.write("Below are custom interview questions generated based on your skills, experience gaps, and background.")
        
        btn_prep = st.button("🎙️ Generate Prep Questions", type="primary", use_container_width=True)
        
        if btn_prep:
            with st.spinner("Generating target interview questions..."):
                prep_result = analyzer.generate_interview_prep(st.session_state["resume_text"], custom_api_key)
                if "error" in prep_result:
                    st.error(prep_result["message"])
                else:
                    st.session_state["interview_prep"] = prep_result
                    st.success("Questions generated!")
                    st.rerun()
                    
        # Display questions
        prep_data = st.session_state["interview_prep"]
        if prep_data:
            st.markdown("### 💬 Mock Interview Questions")
            
            for idx, q_item in enumerate(prep_data.get("questions", [])):
                q_text = q_item.get("question", "")
                q_focus = q_item.get("focus", "Behavioral")
                q_outline = q_item.get("ideal_answer_outline", "")
                
                with st.expander(f"Question {idx+1}: {q_text} ({q_focus})"):
                    st.markdown("##### 🚀 Ideal Answer Blueprint (STAR Structure)")
                    st.write(q_outline)
                    st.info(
                        "💡 Tip: When answering, structure your response as: \n"
                        "1. **Situation**: 15% of your answer \n"
                        "2. **Task**: 15% of your answer \n"
                        "3. **Action**: 50% of your answer (what YOU did) \n"
                        "4. **Result**: 20% of your answer (quantifiable outcomes)"
                    )

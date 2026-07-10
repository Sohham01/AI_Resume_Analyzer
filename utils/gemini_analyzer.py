"""
gemini_analyzer.py

Handles communication with Google's Gemini API.
Takes resume text (and optional job description/bullets) as input
and returns structured JSON analysis reports.
"""

import json
import streamlit as st
import google.generativeai as genai


# ---------------------------------------------------
# Configure & Fetch Gemini Model
# ---------------------------------------------------

def get_model(api_key: str = None):
    """
    Configure genai with the correct API key and return a GenerativeModel instance.
    Falls back to st.secrets["GEMINI_API_KEY"] if custom_key is not provided.
    """
    key = api_key if api_key and api_key.strip() != "" else st.secrets.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key is missing. Please configure it in the sidebar or st.secrets.")
    
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-2.5-flash")


# ---------------------------------------------------
# Helper to clean and parse JSON responses
# ---------------------------------------------------

def clean_and_parse_json(response_text: str) -> dict:
    """
    Clean and parse the JSON string returned by Gemini.
    Removes Markdown fences if present.
    """
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    return json.loads(clean_text)


# ---------------------------------------------------
# 1. Main Resume ATS Audit Function
# ---------------------------------------------------

PROMPT_ATS = """
You are an expert ATS (Applicant Tracking System) recruiter and career coach.
Analyze the following resume thoroughly and return a structured JSON report.

The output MUST be a valid JSON object matching the following schema:
{{
  "ats_score": integer (0 to 100),
  "score_explanation": "string explaining why this score was given, and key highlights",
  "summary": "string providing a concise summary of the candidate's profile",
  "strengths": ["list of strings, representing strong aspects of the resume content/experience"],
  "weaknesses": ["list of strings, representing content or experience gaps"],
  "technical_skills": ["list of tech skills found (e.g. languages, tools, frameworks)"],
  "soft_skills": ["list of soft skills found"],
  "missing_skills": ["list of common important skills associated with this profile that are missing"],
  "formatting_improvements": ["list of action items for improving the document's structure, fonts, sections, or ATS-friendliness"]
}}

Ensure that formatting_improvements specifically audits resume structure (e.g., margins, font usage, missing contact info, tables/columns that might trip up older ATS scanners).

Resume Text:
{resume}
"""

def analyze_resume(resume_text: str, api_key: str = None) -> dict:
    """
    Analyzes the resume text and returns an ATS audit report in JSON format.
    """
    try:
        model = get_model(api_key)
        prompt = PROMPT_ATS.format(resume=resume_text)
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return clean_and_parse_json(response.text)
    except Exception as e:
        return {
            "error": True,
            "message": f"Gemini API Error: {str(e)}"
        }


# ---------------------------------------------------
# 2. Job Description Matcher Function
# ---------------------------------------------------

PROMPT_JD_MATCH = """
You are an expert recruiter matching a candidate's resume against a target Job Description (JD).
Compare the resume text and job description provided, and return a structured JSON comparison.

The output MUST be a valid JSON object matching the following schema:
{{
  "match_score": integer (0 to 100 representing suitability),
  "match_explanation": "string explaining the alignment, missing qualifications, or why the candidate is/isn't a good fit",
  "matched_keywords": ["list of skills or keywords from the JD that are present in the resume"],
  "missing_keywords": ["list of important skills or keywords from the JD that are missing from the resume"],
  "tailoring_suggestions": ["list of specific recommendations on how to customize their bullet points, summary, or skills section to align better with this JD"]
}}

Resume:
{resume}

Job Description:
{job_description}
"""

def match_job_description(resume_text: str, jd_text: str, api_key: str = None) -> dict:
    """
    Compares resume text to a job description and returns keywords, match score, and recommendations.
    """
    try:
        model = get_model(api_key)
        prompt = PROMPT_JD_MATCH.format(resume=resume_text, job_description=jd_text)
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return clean_and_parse_json(response.text)
    except Exception as e:
        return {
            "error": True,
            "message": f"Gemini API Error: {str(e)}"
        }


# ---------------------------------------------------
# 3. Bullet Point Optimizer Function
# ---------------------------------------------------

PROMPT_BULLET_OPTIMIZE = """
You are a professional resume writer and career coach.
Take the following single resume bullet point (or description block) and rewrite it to be far more impactful.
Rewrite it using the STAR (Situation, Task, Action, Result) methodology. Focus on starting with strong Action Verbs and incorporating quantifiable Metrics/Results where possible.

Return exactly 3 optimized variations with different focus areas, formatted in a structured JSON object:
{{
  "original": "string of the original text",
  "optimizations": [
    {{
      "text": "variation 1: focused on technical action and engineering depth",
      "focus": "Technical Depth & Action"
    }},
    {{
      "text": "variation 2: focused on quantifiable metrics, savings, or business outcomes",
      "focus": "Business Impact & Metrics"
    }},
    {{
      "text": "variation 3: focused on leadership, ownership, and scale of collaboration",
      "focus": "Leadership & Scale"
    }}
  ]
}}

Original Bullet Point:
{bullet_point}
"""

def optimize_bullet_point(bullet_text: str, api_key: str = None) -> dict:
    """
    Optimizes a single bullet point using the STAR method.
    """
    try:
        model = get_model(api_key)
        prompt = PROMPT_BULLET_OPTIMIZE.format(bullet_point=bullet_text)
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return clean_and_parse_json(response.text)
    except Exception as e:
        return {
            "error": True,
            "message": f"Gemini API Error: {str(e)}"
        }


# ---------------------------------------------------
# 4. Interview Prep Assistant Function
# ---------------------------------------------------

PROMPT_INTERVIEW_PREP = """
You are a senior hiring manager. Based on the candidate's resume, generate 5 highly custom, challenging, and relevant interview questions they are likely to face.
For each question, provide a detailed outline of what a great answer should cover using the STAR method.

Return the questions as a structured JSON object matching the following schema:
{{
  "questions": [
    {{
      "question": "The interview question text",
      "focus": "Behavioral / Technical / Case Study",
      "ideal_answer_outline": "Detailed suggestions on what to highlight (e.g. mention X technology, discuss scale of Y, show Z soft skill)"
    }}
  ]
}}

Resume:
{resume}
"""

def generate_interview_prep(resume_text: str, api_key: str = None) -> dict:
    """
    Generates customized interview prep questions and answer outlines.
    """
    try:
        model = get_model(api_key)
        prompt = PROMPT_INTERVIEW_PREP.format(resume=resume_text)
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return clean_and_parse_json(response.text)
    except Exception as e:
        return {
            "error": True,
            "message": f"Gemini API Error: {str(e)}"
        }
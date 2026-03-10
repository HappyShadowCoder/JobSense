"""
services/ai_analysis.py — LangChain + OpenAI chains for resume analysis
"""

import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# LLM setup
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

parser = StrOutputParser()


# Chain 1: Extract skills from resume 
resume_extraction_prompt = PromptTemplate.from_template("""
You are a resume parser. Extract all technical and professional skills from the resume below.

Return ONLY a JSON object in this exact format, nothing else:
{{
  "skills": ["skill1", "skill2", "skill3"],
  "experience_years": 0,
  "education": "degree name or null",
  "job_titles": ["title1", "title2"]
}}

Resume:
{resume_text}
""")

resume_chain = resume_extraction_prompt | llm | parser


# Chain 2: Extract skills from job description 
jd_extraction_prompt = PromptTemplate.from_template("""
You are a job description parser. Extract all required and preferred skills from the job description below.

Return ONLY a JSON object in this exact format, nothing else:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3", "skill4"],
  "role": "job title",
  "company": "company name or null"
}}

Job Description:
{jd_text}
""")

jd_chain = jd_extraction_prompt | llm | parser


#  Chain 3: Gap analysis + suggestions 
# ── Chain 3: Gap analysis + suggestions ───────────────────────────
gap_analysis_prompt = PromptTemplate.from_template("""
You are an experienced technical recruiter evaluating a {level} candidate fairly.

IMPORTANT RULES FOR SCORING:
- For "fresher" and "student" level: projects count AS MUCH as work experience
- A strong project using a required technology = that skill is matched
- Never penalise students for lack of work experience
- If the candidate has built real deployed projects, that is a major positive signal
- match_score should reflect realistic hiring probability, not just keyword matching

Candidate Skills: {resume_skills}
Required Skills: {required_skills}
Preferred Skills: {preferred_skills}
Role: {role}
Candidate Level: {level}

Scoring guide:
- 0.8 to 1.0 = Strong match, apply with confidence
- 0.6 to 0.8 = Good match, minor gaps
- 0.4 to 0.6 = Moderate match, some gaps to address
- 0.2 to 0.4 = Weak match, significant gaps
- 0.0 to 0.2 = Poor match, wrong role

Return ONLY a JSON object in this exact format, nothing else:
{{
  "matched_skills": ["skills present in both resume and JD"],
  "gap_skills": ["skills in JD but missing from resume"],
  "match_score": 0.75,
  "suggestions": [
    {{"type": "add_skill", "text": "Add X to your resume", "priority": "high"}},
    {{"type": "rewrite_bullet", "text": "Rewrite your project bullet to mention Y", "priority": "medium"}}
  ]
}}
""")

gap_chain = gap_analysis_prompt | llm | parser

def _safe_parse(raw: str, fallback: dict) -> dict:
    """Safely parse JSON from LLM output."""
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except Exception:
        return fallback

# Main analysis function 
def analyse_resume(resume_text: str, jd_text: str, level: str = "fresher") -> dict:
    """
    Run the full analysis pipeline.
    level: fresher | student | early_career | mid_level
    """

    # Step 1 — Extract resume skills
    resume_raw = resume_chain.invoke({"resume_text": resume_text})
    resume_data = _safe_parse(resume_raw, {"skills": [], "experience_years": 0})

    # Step 2 — Extract JD skills
    jd_raw = jd_chain.invoke({"jd_text": jd_text})
    jd_data = _safe_parse(jd_raw, {"required_skills": [], "preferred_skills": [], "role": "", "company": ""})

    # Step 3 — Gap analysis with level context
    gap_raw = gap_chain.invoke({
        "resume_skills":    json.dumps(resume_data.get("skills", [])),
        "required_skills":  json.dumps(jd_data.get("required_skills", [])),
        "preferred_skills": json.dumps(jd_data.get("preferred_skills", [])),
        "role":             jd_data.get("role", ""),
        "level":            level,
    })
    gap_data = _safe_parse(gap_raw, {"matched_skills": [], "gap_skills": [], "match_score": 0.0, "suggestions": []})

    return {
        "resume_skills":    resume_data.get("skills", []),
        "required_skills":  jd_data.get("required_skills", []),
        "preferred_skills": jd_data.get("preferred_skills", []),
        "jd_role":          jd_data.get("role", ""),
        "jd_company":       jd_data.get("company", ""),
        "matched_skills":   gap_data.get("matched_skills", []),
        "gap_skills":       gap_data.get("gap_skills", []),
        "match_score":      gap_data.get("match_score", 0.0),
        "suggestions":      gap_data.get("suggestions", []),
    }
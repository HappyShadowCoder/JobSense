"""
routes/analyses.py — AI Resume Analysis
Week 2 implementation — stub for now so the app boots.
"""

from flask import Blueprint, jsonify , request
from utils.clerk import clerk_required
from utils.db import query_all , execute , query_one
from services.ai_analysis import analyse_resume

analyses_bp = Blueprint("analyses", __name__)

@analyses_bp.get("/")
@clerk_required
def get_analyses():
    user_id = request.user_id
    rows = query_all(
        "SELECT * FROM analyses WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    return jsonify([dict(r) for r in rows]) , 200


@analyses_bp.post("/")
@clerk_required
def run_analysis():
    print("=== run_analysis called ===")
    user_id = request.user_id
    print("user_id:", user_id)
    
    data = request.get_json()
    print("data:", data)

    resume_id = data.get("resume_id")
    jd_text = data.get("jd_text" , "").strip()
    application_id = data.get("application_id")
    level = data.get("level", "fresher")

    print("resume_id:", resume_id)
    print("jd_text length:", len(jd_text))
    print("level:", level)

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400
    if not jd_text:
        return jsonify({"error": "jd_text is required"}), 400
    
    # Fetch resume
    resume = query_one(
        "SELECT * FROM resumes WHERE id = %s AND user_id = %s",
        (resume_id, user_id)
    )
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    
    try:
        result = analyse_resume(resume["raw_text"], jd_text, level)
        
        import json

        analysis = execute(
    """
    INSERT INTO analyses (
        user_id, resume_id, application_id, jd_text,
        jd_role, jd_company, required_skills,
        matched_skills, gap_skills, match_score, suggestions
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING *
    """,
    (
        user_id,
        resume_id,
        application_id,
        jd_text,
        result["jd_role"],
        result["jd_company"],
        result["required_skills"],
        result["matched_skills"],
        result["gap_skills"],
        result["match_score"],
        json.dumps(result["suggestions"]),
    ),
    returning=True
)

        return jsonify({
            **dict(analysis),
            "suggestions": result["suggestions"]
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500





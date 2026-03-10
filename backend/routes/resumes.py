"""
routes/resumes.py — Resume Upload & Parsing
"""

from flask import Blueprint, request, jsonify
from utils.clerk import clerk_required
from utils.db import query_all, execute
from services.resume_parser import parse_resume

resumes_bp = Blueprint("resumes", __name__)


# GET /api/resumes/
@resumes_bp.get("/")
@clerk_required
def get_resumes():
    user_id = request.user_id
    rows = query_all(
        "SELECT * FROM resumes WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    return jsonify([dict(r) for r in rows]), 200


# POST /api/resumes/ 
@resumes_bp.post("/")
@clerk_required
def upload_resume():
    user_id = request.user_id

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    original_filename = file.filename
    filename_lower = original_filename.lower()

    if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx")):
        return jsonify({"error": "Only PDF and DOCX files are supported"}), 400


    try:
        file_bytes = file.read()
        print("file_bytes type:", type(file_bytes))
        print("filename_lower:", filename_lower)
    
        raw_text = parse_resume(file_bytes, filename_lower)
        print("raw_text length:", len(raw_text))

        if not raw_text.strip():
            return jsonify({"error": "Could not extract text from file"}), 400

        resume = execute(
        """
        INSERT INTO resumes (user_id, file_name, raw_text, extracted_skills)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, original_filename, raw_text, []),
        returning=True
        )

        return jsonify(dict(resume)), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
"""
routes/resumes.py — Resume Upload & Parsing
Week 2 implementation — stub for now so the app boots.
"""

from flask import Blueprint, jsonify
from utils.clerk import clerk_required

resumes_bp = Blueprint("resumes", __name__)


@resumes_bp.get("/")
@clerk_required
def get_resumes():
    """Return all resumes for the logged-in user. Full impl in Week 2."""
    return jsonify([]), 200


@resumes_bp.post("/")
@clerk_required
def upload_resume():
    """Upload + parse resume. Full impl in Week 2."""
    return jsonify({"message": "Resume upload — coming in Week 2"}), 501

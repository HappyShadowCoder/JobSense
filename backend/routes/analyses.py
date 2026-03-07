"""
routes/analyses.py — AI Resume Analysis
Week 2 implementation — stub for now so the app boots.
"""

from flask import Blueprint, jsonify
from utils.clerk import clerk_required

analyses_bp = Blueprint("analyses", __name__)


@analyses_bp.get("/")
@clerk_required
def get_analyses():
    return jsonify([]), 200


@analyses_bp.post("/")
@clerk_required
def run_analysis():
    return jsonify({"message": "AI Analysis — coming in Week 2"}), 501

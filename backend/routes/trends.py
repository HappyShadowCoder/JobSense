"""
routes/trends.py — Skill Trends powered by ML model data
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.clerk import clerk_required
from utils.db import query_all
from ml.predict import get_top_categories
import json

trends_bp = Blueprint("trends", __name__)


@trends_bp.get("/")
@clerk_required
def get_trends():
    """
    Returns:
    1. Top skill categories from ML model (121k JDs)
    2. Top skills from user submitted JDs (from analyses table)
    """

    # ML model trends 
    ml_categories = get_top_categories()

    # User submitted JD trends (from analyses table) 
    rows = query_all(
        """
        SELECT required_skills 
        FROM analyses 
        WHERE required_skills IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 100
        """
    )

    # Count skill frequency from user JDs
    user_skill_counts = {}
    for row in rows:
        skills = row["required_skills"]
        if isinstance(skills, str):
            skills = json.loads(skills)
        for skill in skills:
            skill = skill.strip().lower()
            if skill:
                user_skill_counts[skill] = user_skill_counts.get(skill, 0) + 1

    top_user_skills = sorted(
        user_skill_counts.items(), key=lambda x: -x[1]
    )[:20]

    return jsonify({
        "ml_trends":   ml_categories[:20],   
        "user_trends": top_user_skills,       
    }), 200
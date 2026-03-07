"""
routes/trends.py — Skill Trends (populated by weekly cron)
Week 3 implementation — stub for now.
"""

from flask import Blueprint, jsonify
from utils.clerk import clerk_required

trends_bp = Blueprint("trends", __name__)


@trends_bp.get("/")
@clerk_required
def get_trends():
    return jsonify([]), 200

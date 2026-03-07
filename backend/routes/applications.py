"""
routes/applications.py — Job Application Tracker CRUD
"""

from flask import Blueprint, request, jsonify
from utils.clerk import clerk_required
from utils.db import query_one, query_all, execute

applications_bp = Blueprint("applications", __name__)

VALID_STATUSES = {"saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn"}


# ── GET /api/applications ──────────────────────────────────────────
@applications_bp.get("/")
@clerk_required
def get_applications():
    user_id = request.user_id
    status  = request.args.get("status")  # optional filter

    if status:
        rows = query_all(
            "SELECT * FROM applications WHERE user_id = %s AND status = %s ORDER BY applied_date DESC",
            (user_id, status)
        )
    else:
        rows = query_all(
            "SELECT * FROM applications WHERE user_id = %s ORDER BY applied_date DESC",
            (user_id,)
        )

    return jsonify([dict(r) for r in rows]), 200


# ── POST /api/applications ─────────────────────────────────────────
@applications_bp.post("/")
@clerk_required
def create_application():
    user_id = request.user_id
    data    = request.get_json()

    company      = data.get("company", "").strip()
    role         = data.get("role", "").strip()
    status       = data.get("status", "applied")
    applied_date = data.get("applied_date")   # "YYYY-MM-DD" or null
    source_url   = data.get("source_url")
    notes        = data.get("notes")

    if not company or not role:
        return jsonify({"error": "company and role are required"}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of: {', '.join(VALID_STATUSES)}"}), 400

    app = execute(
        """
        INSERT INTO applications (user_id, company, role, status, applied_date, source_url, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (user_id, company, role, status, applied_date, source_url, notes),
        returning=True
    )

    return jsonify(dict(app)), 201


# ── PATCH /api/applications/<id> ───────────────────────────────────
@applications_bp.patch("/<app_id>")
@clerk_required
def update_application(app_id):
    user_id = request.user_id
    data    = request.get_json()

    # Confirm ownership
    existing = query_one(
        "SELECT id FROM applications WHERE id = %s AND user_id = %s",
        (app_id, user_id)
    )
    if not existing:
        return jsonify({"error": "Application not found"}), 404

    # Build dynamic SET clause — only update fields that were sent
    allowed = {"company", "role", "status", "applied_date", "source_url", "notes"}
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    if "status" in updates and updates["status"] not in VALID_STATUSES:
        return jsonify({"error": f"Invalid status"}), 400

    set_clause = ", ".join(f"{k} = %s" for k in updates)
    values     = list(updates.values()) + [app_id]

    updated = execute(
        f"UPDATE applications SET {set_clause} WHERE id = %s RETURNING *",
        tuple(values),
        returning=True
    )

    return jsonify(dict(updated)), 200


# ── DELETE /api/applications/<id> ─────────────────────────────────
@applications_bp.delete("/<app_id>")
@clerk_required
def delete_application(app_id):
    user_id = request.user_id

    existing = query_one(
        "SELECT id FROM applications WHERE id = %s AND user_id = %s",
        (app_id, user_id)
    )
    if not existing:
        return jsonify({"error": "Application not found"}), 404

    execute("DELETE FROM applications WHERE id = %s", (app_id,))
    return jsonify({"message": "Deleted"}), 200


# ── GET /api/applications/stats ────────────────────────────────────
@applications_bp.get("/stats")
@clerk_required
def get_stats():
    """Return count per status — used by dashboard charts."""
    user_id = request.user_id
    rows = query_all(
        "SELECT status, COUNT(*) AS count FROM applications WHERE user_id = %s GROUP BY status",
        (user_id,)
    )
    return jsonify({r["status"]: r["count"] for r in rows}), 200

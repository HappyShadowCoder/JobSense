"""
JobSense Backend — Flask Application Entry Point
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB upload limit

    # ── Extensions ────────────────────────────────────────────
    CORS(app, origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")])

    # ── Register Blueprints (routes) ──────────────────────────
    from routes.applications import applications_bp
    from routes.resumes import resumes_bp
    from routes.analyses import analyses_bp
    from routes.trends import trends_bp

    app.register_blueprint(applications_bp, url_prefix="/api/applications")
    app.register_blueprint(resumes_bp,      url_prefix="/api/resumes")
    app.register_blueprint(analyses_bp,     url_prefix="/api/analyses")
    app.register_blueprint(trends_bp,       url_prefix="/api/trends")

    # ── Health check ──────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok", "app": "JobSense API"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=8000)

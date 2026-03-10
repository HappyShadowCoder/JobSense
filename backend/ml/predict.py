"""
ml/predict.py — Serve ML match score using trained embeddings
"""

import os
import json
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Load model artefacts once at startup ──────────────────────────
_model      = None
_embeddings = None
_embedder   = None
_metadata   = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load():
    global _model, _embeddings, _embedder, _metadata

    if _model is not None:
        return

    model_path      = os.path.join(BASE_DIR, "saved_models/skill_model.pkl")
    embeddings_path = os.path.join(BASE_DIR, "saved_models/jd_embeddings.npy")
    metadata_path   = os.path.join(BASE_DIR, "saved_models/metadata.json")

    print("Loading ML model artefacts...")
    _model      = joblib.load(model_path)
    _embeddings = np.load(embeddings_path)
    _embedder   = SentenceTransformer("all-MiniLM-L6-v2")

    with open(metadata_path) as f:
        _metadata = json.load(f)

    print(f"ML model loaded — {_metadata['total_jds']:,} JDs, dim={_metadata['embedding_dim']}")


def get_ml_score(resume_text: str, jd_text: str) -> float:
    """
    Compute semantic similarity between resume and JD.
    Returns a float between 0.0 and 1.0.
    """
    _load()

    # Encode both texts
    texts      = [resume_text[:512], jd_text[:512]]
    embeddings = _embedder.encode(
        texts,
        normalize_embeddings=True,
        device="mps",
        show_progress_bar=False,
    )

    # Cosine similarity — since embeddings are normalised, dot product = cosine similarity
    score = float(np.dot(embeddings[0], embeddings[1]))

    # Clamp to 0.0 - 1.0
    return max(0.0, min(1.0, score))


def get_top_categories() -> list:
    """Return top skill categories from training data — used for trends page."""
    _load()
    counts = _metadata.get("top_categories", [])
    return counts


def should_retrain(db_analysis_count: int) -> bool:
    """Check if enough new analyses have been submitted to trigger retraining."""
    _load()
    threshold = _metadata.get("retrain_threshold", 50)
    since     = _metadata.get("analyses_since_retrain", 0)
    return (db_analysis_count - since) >= threshold
"""
ml/train.py — Train semantic similarity model on LinkedIn job postings
Run from backend/: python ml/train.py
"""

import os
import re
import json
import joblib
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime


# ── Config ─────────────────────────────────────────────────────────
POSTINGS_PATH   = "ml/data/postings.csv"
JOB_SKILLS_PATH = "ml/data/jobs/job_skills.csv"
SKILLS_PATH     = "ml/data/mappings/skills.csv"
MODEL_PATH      = "ml/saved_models/skill_model.pkl"
EMBEDDINGS_PATH = "ml/saved_models/jd_embeddings.npy"
METADATA_PATH   = "ml/saved_models/metadata.json"
BATCH_SIZE      = 128
MAX_ROWS        = None  # use all rows


# ── Text cleaning ──────────────────────────────────────────────────
def clean_description(text: str) -> str:
    """
    Clean raw JD text:
    1. Remove HTML tags
    2. Remove URLs and emails
    3. Remove salary/pay/benefits boilerplate
    4. Remove special characters
    5. Normalise whitespace
    """
    if not isinstance(text, str) or len(text.strip()) == 0:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text)

    # Remove emails
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove salary lines — e.g. "Pay: $18-20/hour", "$50,000 - $80,000"
    text = re.sub(r"\$[\d,\.\-\/]+\s*(per|/|hour|yr|year|month|week)?", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"(pay|salary|compensation|wage)\s*:.*?\n", " ", text, flags=re.IGNORECASE)

    # Remove common boilerplate sections
    boilerplate = [
        r"equal opportunity employer.*",
        r"we are committed to.*diversity.*",
        r"all qualified applicants.*",
        r"job type\s*:.*",
        r"benefits\s*:.*",
        r"schedule\s*:.*",
        r"work location\s*:.*",
        r"expected hours\s*:.*",
        r"please send (resume|cv).*",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.DOTALL)

    # Remove special characters — keep letters, numbers, basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s\.\,\-\/\+\#]", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_skill(skill: str) -> str:
    if not isinstance(skill, str):
        return ""
    return skill.strip().lower()


# ── Load and merge ─────────────────────────────────────────────────
def load_and_merge() -> pd.DataFrame:
    print("Loading postings.csv...")
    df = pd.read_csv(
        POSTINGS_PATH,
        nrows=MAX_ROWS,
        usecols=["job_id", "title", "description", "company_name",
                 "formatted_experience_level", "location"]
    )
    print(f"Raw rows loaded        : {len(df):,}")

    # Drop nulls
    df = df.dropna(subset=["description", "title"])
    df = df.drop_duplicates(subset=["job_id"])
    print(f"After dedup/dropna     : {len(df):,}")

    # Drop very short descriptions
    df = df[df["description"].str.len() > 200]
    print(f"After length filter    : {len(df):,}")

    # Clean descriptions
    print("Cleaning descriptions...")
    df["clean_description"] = df["description"].apply(clean_description)

    # Drop rows where cleaning left too little text
    df = df[df["clean_description"].str.len() > 100]
    print(f"After text cleaning    : {len(df):,}")

    # Load and merge skill categories
    print("Loading skill mappings...")
    skills     = pd.read_csv(SKILLS_PATH)
    job_skills = pd.read_csv(JOB_SKILLS_PATH)

    skills["skill_name"] = skills["skill_name"].apply(clean_skill)
    skills     = skills.dropna(subset=["skill_name"])
    job_skills = job_skills.dropna(subset=["skill_abr"])

    job_skills = job_skills.merge(skills, on="skill_abr", how="left")
    job_skills = job_skills.dropna(subset=["skill_name"])

    skills_grouped = (
        job_skills.groupby("job_id")["skill_name"]
        .apply(list)
        .reset_index()
        .rename(columns={"skill_name": "skill_categories"})
    )

    df = df.merge(skills_grouped, on="job_id", how="left")
    df["skill_categories"] = df["skill_categories"].apply(
        lambda x: list(set(x)) if isinstance(x, list) else []
    )

    print(f"Final dataset size     : {len(df):,}")
    print(f"Jobs with skill tags   : {df['skill_categories'].apply(len).gt(0).sum():,}")
    return df


# ── Train ──────────────────────────────────────────────────────────
def train():
    os.makedirs("ml/saved_models", exist_ok=True)

    df = load_and_merge()

    # Skill category frequency for trends dashboard
    print("\nComputing skill category frequencies...")
    category_counts = {}
    for cats in df["skill_categories"]:
        for cat in cats:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Filter rare categories
    category_counts = {k: v for k, v in category_counts.items() if v >= 10}
    print(f"Skill categories (freq>=10): {len(category_counts)}")

    # Experience level distribution
    exp_dist = df["formatted_experience_level"].value_counts().to_dict()
    print(f"Experience levels: {exp_dist}")

    # Generate embeddings
    print(f"\nLoading sentence-transformers model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"Generating embeddings for {len(df):,} JDs...")
    print("Using MPS (M4 GPU)...")

    # Truncate to 512 chars — model context limit
    texts = df["clean_description"].str[:512].tolist()

    embeddings = embedder.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        device="mps",
        normalize_embeddings=True,  # crucial for cosine similarity
    )
    print(f"Embeddings shape: {embeddings.shape}")

    # Save model artefacts
    print("\nSaving artefacts...")
    joblib.dump({
        "category_counts": category_counts,
        "titles":          df["title"].tolist(),
        "job_ids":         df["job_id"].tolist(),
        "exp_levels":      df["formatted_experience_level"].tolist(),
        "skill_categories": df["skill_categories"].tolist(),
    }, MODEL_PATH)

    np.save(EMBEDDINGS_PATH, embeddings)

    top_categories = sorted(category_counts.items(), key=lambda x: -x[1])[:30]
    metadata = {
        "trained_at":             datetime.now().isoformat(),
        "total_jds":              len(df),
        "total_categories":       len(category_counts),
        "top_categories":         top_categories,
        "exp_distribution":       exp_dist,
        "retrain_threshold":      50,
        "analyses_since_retrain": 0,
        "embedding_model":        "all-MiniLM-L6-v2",
        "embedding_dim":          embeddings.shape[1],
    }
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)

    print("\n✅ Training complete!")
    print(f"   JDs trained on     : {len(df):,}")
    print(f"   Embedding dim      : {embeddings.shape[1]}")
    print(f"   Skill categories   : {len(category_counts)}")
    print(f"   Top 5 categories   : {[s[0] for s in top_categories[:5]]}")
    print(f"   Saved to           : ml/saved_models/")


if __name__ == "__main__":
    train()
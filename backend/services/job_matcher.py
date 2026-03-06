import pandas as pd
import os
from config import DATASET_FOLDER, MODEL_FOLDER

# Load real job descriptions + vectorizer
try:
    import joblib
    from sklearn.metrics.pairwise import cosine_similarity

    jobs = pd.read_csv(os.path.join(DATASET_FOLDER, "job_descriptions.csv"))
    vectorizer = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_vectorizer.pkl"))
    job_vectors = vectorizer.transform(jobs["description"])
    _use_ml = True
    print(f"[job_matcher] Loaded {len(jobs)} job descriptions with ML model")

except Exception as e:
    print(f"[job_matcher] ML model not available, using keyword fallback: {e}")
    _use_ml = False
    jobs = None
    vectorizer = None
    job_vectors = None

    FALLBACK_JOBS = [
        {"title": "INFORMATION-TECHNOLOGY", "keywords": ["python", "java", "sql", "git", "linux", "api"]},
        {"title": "FINANCE",                "keywords": ["accounting", "excel", "finance", "banking", "audit"]},
        {"title": "HR",                     "keywords": ["recruitment", "hr", "payroll", "training", "policy"]},
        {"title": "SALES",                  "keywords": ["sales", "crm", "negotiation", "targets", "clients"]},
        {"title": "HEALTHCARE",             "keywords": ["medical", "nursing", "clinical", "patient", "health"]},
        {"title": "ENGINEERING",            "keywords": ["autocad", "mechanical", "electrical", "design", "matlab"]},
        {"title": "TEACHER",                "keywords": ["teaching", "curriculum", "education", "students", "training"]},
        {"title": "BANKING",                "keywords": ["banking", "loans", "finance", "compliance", "risk"]},
    ]


def match_jobs(resume_text: str) -> list:
    """
    Returns top 5 matching jobs as list of dicts: [{job_title, score}]
    Uses cosine similarity with TF-IDF if model available,
    otherwise falls back to keyword scoring.
    """
    if _use_ml:
        from sklearn.metrics.pairwise import cosine_similarity
        resume_vector = vectorizer.transform([resume_text])
        similarity = cosine_similarity(resume_vector, job_vectors).flatten()
        top_indices = similarity.argsort()[-5:][::-1]

        return [
            {
                "job_title": jobs.iloc[i]["title"],
                "score": round(float(similarity[i]) * 100, 2)
            }
            for i in top_indices
        ]

    else:
        resume_lower = resume_text.lower()
        scored = []
        for job in FALLBACK_JOBS:
            matches = sum(1 for kw in job["keywords"] if kw in resume_lower)
            score = round((matches / len(job["keywords"])) * 100, 2)
            scored.append({"job_title": job["title"], "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:5]
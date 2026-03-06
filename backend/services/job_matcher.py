import pandas as pd
import os

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "..", "datasets")
MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "..", "models")

# Try loading pre-trained vectorizer and job dataset
# Falls back to keyword matching if model files are not present yet
_use_ml = False
jobs = None
vectorizer = None
job_vectors = None

try:
    from sklearn.metrics.pairwise import cosine_similarity
    import joblib

    jobs = pd.read_csv(os.path.join(DATASET_FOLDER, "job_descriptions.csv"))
    vectorizer = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_vectorizer.pkl"))
    job_vectors = vectorizer.transform(jobs["description"])
    _use_ml = True

except Exception as e:
    print(f"[job_matcher] ML model not available, using keyword fallback: {e}")

    # Fallback job list for development/testing
    FALLBACK_JOBS = [
        {"title": "Python Developer", "keywords": ["python", "django", "flask", "rest api"]},
        {"title": "Data Scientist", "keywords": ["python", "machine learning", "pandas", "numpy", "scikit-learn"]},
        {"title": "Frontend Developer", "keywords": ["javascript", "react", "html", "css", "node.js"]},
        {"title": "DevOps Engineer", "keywords": ["docker", "kubernetes", "aws", "linux", "ci/cd"]},
        {"title": "ML Engineer", "keywords": ["tensorflow", "pytorch", "deep learning", "nlp", "python"]},
        {"title": "Backend Developer", "keywords": ["java", "sql", "rest api", "spring", "microservices"]},
        {"title": "Cloud Architect", "keywords": ["aws", "azure", "gcp", "docker", "terraform"]},
        {"title": "Data Analyst", "keywords": ["sql", "excel", "python", "data analysis", "tableau"]},
    ]


def match_jobs(resume_text: str) -> list:
    """
    Returns top 5 job matches as list of dicts: [{job_title, score}, ...]
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
        # Keyword-based fallback scoring
        resume_lower = resume_text.lower()
        scored = []

        for job in FALLBACK_JOBS:
            matches = sum(1 for kw in job["keywords"] if kw in resume_lower)
            score = round((matches / len(job["keywords"])) * 100, 2)
            scored.append({"job_title": job["title"], "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:5]
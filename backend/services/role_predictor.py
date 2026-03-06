import os

MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "..", "models")

_use_ml = False
model = None
vectorizer = None

try:
    import joblib
    model = joblib.load(os.path.join(MODEL_FOLDER, "role_prediction.pkl"))
    vectorizer = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_vectorizer.pkl"))
    _use_ml = True
except Exception as e:
    print(f"[role_predictor] ML model not available, using keyword fallback: {e}")

ROLE_KEYWORDS = {
    "Data Scientist": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "scikit-learn", "statistics"],
    "Python Developer": ["python", "flask", "django", "fastapi", "rest api", "backend"],
    "Frontend Developer": ["react", "javascript", "html", "css", "vue", "angular", "typescript"],
    "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "jenkins", "aws", "terraform", "linux"],
    "Data Analyst": ["sql", "excel", "tableau", "power bi", "data analysis", "reporting"],
    "ML Engineer": ["tensorflow", "pytorch", "model deployment", "mlops", "feature engineering"],
    "Backend Developer": ["java", "spring", "sql", "microservices", "node.js", "api"],
    "Cloud Engineer": ["aws", "azure", "gcp", "cloud", "s3", "lambda", "terraform"],
    "Full Stack Developer": ["react", "node.js", "python", "sql", "javascript", "rest api"],
}


def predict_role(resume_text: str) -> str:
    """
    Returns the most likely job role based on the resume text.
    Uses ML model if available, otherwise falls back to keyword scoring.
    """
    if _use_ml:
        vector = vectorizer.transform([resume_text])
        return model.predict(vector)[0]

    # Keyword fallback
    resume_lower = resume_text.lower()
    scores = {}

    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in resume_lower)
        scores[role] = score

    best_role = max(scores, key=scores.get)

    # If no keywords matched at all, return generic
    if scores[best_role] == 0:
        return "Software Developer"

    return best_role
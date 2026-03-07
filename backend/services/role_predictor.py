import os
from config import MODEL_FOLDER

# Load trained Random Forest + TF-IDF vectorizer
try:
    import joblib
    model      = joblib.load(os.path.join(MODEL_FOLDER, "role_prediction.pkl"))
    vectorizer = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_vectorizer.pkl"))
    _use_ml    = True
    print("[role_predictor] ML model loaded successfully")
except Exception as e:
    print(f"[role_predictor] ML model not available, using keyword fallback: {e}")
    _use_ml    = False
    model      = None
    vectorizer = None

# ── Keyword fallback map ───────────────────────────────────────────────────
# Each role has PRIMARY keywords (weight 2) and SECONDARY keywords (weight 1).
# Web-related roles are split out clearly so HTML/CSS/JS resumes score correctly.
ROLE_KEYWORDS = {
    # ── Tech roles ──────────────────────────────────────────────
    "WEB-DEVELOPER": {
        "primary":   ["html", "css", "javascript", "frontend", "web development",
                      "react", "angular", "vue", "bootstrap", "jquery", "node.js",
                      "responsive", "ui", "ux", "web design"],
        "secondary": ["python", "git", "api", "github", "node", "typescript"],
    },
    "DATA-SCIENCE": {
        "primary":   ["machine learning", "deep learning", "data science", "nlp",
                      "tensorflow", "pytorch", "pandas", "numpy", "scikit",
                      "neural network", "computer vision", "model", "dataset"],
        "secondary": ["python", "sql", "statistics", "jupyter", "kaggle"],
    },
    "INFORMATION-TECHNOLOGY": {
        "primary":   ["linux", "networking", "system admin", "cybersecurity",
                      "cloud", "aws", "azure", "devops", "docker", "kubernetes",
                      "it support", "infrastructure", "server"],
        "secondary": ["python", "java", "sql", "git", "bash"],
    },
    "SOFTWARE-ENGINEER": {
        "primary":   ["software development", "backend", "api development",
                      "microservices", "spring", "django", "flask", "rest",
                      "java", "c++", "system design", "algorithms"],
        "secondary": ["python", "git", "sql", "agile", "testing"],
    },
    # ── Other domains ────────────────────────────────────────────
    "FINANCE":              {"primary": ["finance", "accounting", "audit", "tax", "budget", "financial analysis", "excel", "tally"], "secondary": ["banking", "investment", "gst"]},
    "HR":                   {"primary": ["recruitment", "human resources", "payroll", "onboarding", "hr policy", "talent acquisition"], "secondary": ["training", "performance"]},
    "SALES":                {"primary": ["sales", "crm", "revenue", "b2b", "targets", "negotiation", "clients"], "secondary": ["marketing", "lead generation"]},
    "HEALTHCARE":           {"primary": ["medical", "nursing", "clinical", "patient care", "hospital", "pharmacy"], "secondary": ["health", "diagnosis"]},
    "ENGINEERING":          {"primary": ["autocad", "mechanical", "electrical", "solidworks", "matlab", "cad", "circuit"], "secondary": ["design", "manufacturing"]},
    "TEACHER":              {"primary": ["teaching", "curriculum", "lesson plan", "students", "education", "school"], "secondary": ["training", "academic"]},
    "BANKING":              {"primary": ["banking", "loans", "compliance", "risk management", "branch", "investment"], "secondary": ["finance", "audit"]},
    "ACCOUNTANT":           {"primary": ["accounting", "tally", "gst", "bookkeeping", "ledger", "balance sheet"], "secondary": ["excel", "finance"]},
    "BUSINESS-DEVELOPMENT": {"primary": ["business development", "partnerships", "growth strategy", "leads", "b2b"], "secondary": ["sales", "negotiation"]},
    "DESIGNER":             {"primary": ["photoshop", "illustrator", "figma", "ui design", "ux design", "graphic design"], "secondary": ["canva", "sketch", "branding"]},
    "DIGITAL-MEDIA":        {"primary": ["social media", "content creation", "seo", "digital marketing", "campaigns"], "secondary": ["analytics", "branding"]},
    "CONSULTANT":           {"primary": ["consulting", "advisory", "stakeholders", "strategy", "recommendations"], "secondary": ["analysis", "presentation"]},
    "ADVOCATE":             {"primary": ["legal", "law", "litigation", "contracts", "court", "compliance"], "secondary": ["legal research", "drafting"]},
    "BPO":                  {"primary": ["bpo", "call center", "customer service", "inbound", "outbound", "support"], "secondary": ["communication", "crm"]},
    "CHEF":                 {"primary": ["chef", "cooking", "kitchen", "culinary", "menu", "food preparation"], "secondary": ["recipe", "hospitality"]},
    "FITNESS":              {"primary": ["fitness", "personal trainer", "gym", "nutrition", "workout", "wellness"], "secondary": ["exercise", "health"]},
    "PUBLIC-RELATIONS":     {"primary": ["public relations", "pr", "press release", "media relations", "branding"], "secondary": ["communication", "events"]},
}


def predict_role(resume_text: str) -> str:
    """
    Predicts the most likely job category from resume text.
    Uses trained ML model if available, else weighted keyword scoring.
    """
    if _use_ml:
        vector = vectorizer.transform([resume_text])
        return model.predict(vector)[0]

    resume_lower = resume_text.lower()
    scores = {}

    for role, kw_dict in ROLE_KEYWORDS.items():
        primary_hits   = sum(2 for kw in kw_dict["primary"]   if kw in resume_lower)
        secondary_hits = sum(1 for kw in kw_dict["secondary"] if kw in resume_lower)
        scores[role] = primary_hits + secondary_hits

    best_role  = max(scores, key=scores.get)
    best_score = scores[best_role]

    # Tie-breaking: if IT and WEB-DEVELOPER are tied, prefer WEB-DEVELOPER
    # when HTML/CSS are present (common for freshers)
    if best_score > 0:
        top_score = best_score
        top_roles = [r for r, s in scores.items() if s == top_score]
        if "WEB-DEVELOPER" in top_roles and any(kw in resume_lower for kw in ["html", "css", "web"]):
            return "WEB-DEVELOPER"
        return best_role

    return "INFORMATION-TECHNOLOGY"
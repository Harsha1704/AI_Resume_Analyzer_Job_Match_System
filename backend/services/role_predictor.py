import os
from config import MODEL_FOLDER

# Load trained Random Forest + TF-IDF vectorizer
try:
    import joblib
    model = joblib.load(os.path.join(MODEL_FOLDER, "role_prediction.pkl"))
    vectorizer = joblib.load(os.path.join(MODEL_FOLDER, "tfidf_vectorizer.pkl"))
    _use_ml = True
    print("[role_predictor] ML model loaded successfully")

except Exception as e:
    print(f"[role_predictor] ML model not available, using keyword fallback: {e}")
    _use_ml = False
    model = None
    vectorizer = None

# Keyword fallback map (24 categories from dataset)
ROLE_KEYWORDS = {
    "INFORMATION-TECHNOLOGY": ["python", "java", "javascript", "sql", "linux", "docker", "aws", "api", "git"],
    "FINANCE":                 ["finance", "accounting", "excel", "audit", "tax", "budget", "financial"],
    "HR":                      ["recruitment", "hr", "human resources", "payroll", "onboarding", "policy"],
    "SALES":                   ["sales", "crm", "targets", "revenue", "negotiation", "clients", "b2b"],
    "HEALTHCARE":              ["medical", "nursing", "clinical", "patient", "hospital", "health", "pharmacy"],
    "ENGINEERING":             ["autocad", "mechanical", "electrical", "solidworks", "matlab", "design"],
    "TEACHER":                 ["teaching", "curriculum", "education", "students", "lesson", "school"],
    "BANKING":                 ["banking", "loans", "compliance", "risk", "branch", "investment"],
    "ACCOUNTANT":              ["accounting", "tally", "gst", "bookkeeping", "ledger", "balance sheet"],
    "BUSINESS-DEVELOPMENT":    ["business development", "partnerships", "growth", "strategy", "leads"],
    "CONSULTANT":              ["consulting", "advisory", "stakeholders", "strategy", "recommendations"],
    "DESIGNER":                ["photoshop", "illustrator", "figma", "ui", "ux", "graphic", "design"],
    "DIGITAL-MEDIA":           ["social media", "content", "seo", "digital", "campaigns", "analytics"],
    "ADVOCATE":                ["legal", "law", "litigation", "contracts", "court", "compliance"],
    "AVIATION":                ["pilot", "aviation", "aircraft", "flight", "atc", "airline"],
    "CONSTRUCTION":            ["construction", "civil", "structural", "site", "blueprint", "architecture"],
    "AUTOMOBILE":              ["automobile", "vehicle", "engine", "maintenance", "workshop", "repair"],
    "BPO":                     ["bpo", "call center", "customer service", "support", "inbound", "outbound"],
    "AGRICULTURE":             ["agriculture", "farming", "crops", "soil", "irrigation", "agronomy"],
    "FITNESS":                 ["fitness", "trainer", "gym", "nutrition", "workout", "wellness"],
    "CHEF":                    ["chef", "cooking", "kitchen", "culinary", "menu", "food"],
    "APPAREL":                 ["fashion", "apparel", "textile", "garment", "merchandising", "retail"],
    "ARTS":                    ["art", "creative", "painting", "sculpture", "gallery", "artist"],
    "PUBLIC-RELATIONS":        ["pr", "public relations", "media", "press", "communication", "branding"],
}


def predict_role(resume_text: str) -> str:
    """
    Predicts the most likely job category from resume text.
    Uses trained Random Forest if available, else keyword scoring.
    """
    if _use_ml:
        vector = vectorizer.transform([resume_text])
        return model.predict(vector)[0]

    # Keyword fallback
    resume_lower = resume_text.lower()
    scores = {
        role: sum(1 for kw in keywords if kw in resume_lower)
        for role, keywords in ROLE_KEYWORDS.items()
    }

    best_role = max(scores, key=scores.get)
    return best_role if scores[best_role] > 0 else "INFORMATION-TECHNOLOGY"
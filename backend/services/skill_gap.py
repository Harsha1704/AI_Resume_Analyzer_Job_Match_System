import pandas as pd
import os
import re
from config import DATASET_FOLDER

# Load skills dataset
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    if 'match_term' in skills_data.columns:
        skills_data   = skills_data.dropna(subset=['match_term'])
        match_terms   = [str(t).lower().strip() for t in skills_data['match_term'].tolist()]
        display_names = skills_data['skill_name'].tolist()
    else:
        col           = 'skill' if 'skill' in skills_data.columns else skills_data.columns[0]
        match_terms   = [str(t).lower().strip() for t in skills_data[col].dropna().tolist()]
        display_names = match_terms
    print(f"[skill_gap] Loaded {len(match_terms)} skills from Kaggle dataset")
except Exception as e:
    print(f"[skill_gap] Could not load dataset, using fallback: {e}")
    match_terms   = []
    display_names = []

# ── Role-specific skill priorities ────────────────────────────────────────
# Missing skills are sorted so the most relevant ones for the predicted role
# appear at the top of the gap list.
ROLE_PRIORITY_SKILLS = {
    "WEB-DEVELOPER":    ["javascript", "react", "git", "sql", "typescript", "bootstrap",
                         "figma", "rest api", "mongodb", "docker", "aws", "node.js"],
    "DATA-SCIENCE":     ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "sql",
                         "matplotlib", "jupyter", "nlp", "deep learning", "computer vision",
                         "data analysis", "machine learning"],
    "SOFTWARE-ENGINEER":["git", "sql", "docker", "rest api", "java", "spring", "aws",
                         "kubernetes", "ci/cd", "microservices", "algorithms"],
    "INFORMATION-TECHNOLOGY": ["linux", "networking", "sql", "git", "docker", "aws",
                               "cybersecurity", "bash", "cloud", "azure"],
    "FINANCE":          ["excel", "tally", "gst", "financial modeling", "power bi",
                         "accounting", "python", "sql"],
    "HR":               ["recruitment", "payroll", "excel", "communication",
                         "hr software", "data analysis"],
    "SALES":            ["crm", "negotiation", "excel", "communication",
                         "salesforce", "data analysis"],
    "DESIGNER":         ["figma", "photoshop", "illustrator", "ui", "ux",
                         "sketch", "canva", "adobe xd"],
}

# Fallback priority for unknown roles
DEFAULT_PRIORITY = ["python", "sql", "git", "excel", "communication",
                    "docker", "aws", "data analysis", "machine learning", "rest api"]


def _match_skill(term: str, resume_lower: str) -> bool:
    if len(term) <= 3:
        return bool(re.search(r'\b' + re.escape(term) + r'\b', resume_lower))
    return term in resume_lower


def detect_skill_gap(resume_text: str, predicted_role: str = "") -> tuple:
    """
    Compares resume against skills dataset.
    Returns:
        present (list): skills found in the resume
        missing (list): top 10 missing skills, prioritized by predicted role
    """
    resume_lower = resume_text.lower()
    seen_present = set()
    seen_missing = set()
    present      = []
    missing_all  = []

    for term, name in zip(match_terms, display_names):
        term_lower = str(term).lower().strip()
        if term_lower in seen_present or term_lower in seen_missing:
            continue

        if _match_skill(term_lower, resume_lower):
            present.append(str(name))
            seen_present.add(term_lower)
        else:
            missing_all.append((term_lower, str(name)))
            seen_missing.add(term_lower)

    # ── Sort missing skills: role-priority ones come first ─────
    priority_list = ROLE_PRIORITY_SKILLS.get(predicted_role, DEFAULT_PRIORITY)

    def priority_score(item):
        term = item[0]
        for i, p in enumerate(priority_list):
            if p in term or term in p:
                return i          # lower index = higher priority
        return len(priority_list) # non-priority goes to end

    missing_sorted = sorted(missing_all, key=priority_score)
    missing_names  = [name for _, name in missing_sorted]

    return present, missing_names[:10]
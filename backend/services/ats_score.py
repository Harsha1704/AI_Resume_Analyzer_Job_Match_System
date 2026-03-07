import pandas as pd
import os
import re
from config import DATASET_FOLDER

# Core in-demand skills — used as the scoring denominator.
# Keeping this list focused (not 1869 raw dataset entries) gives
# meaningful ATS percentages (0-100%) instead of near-zero values.
CORE_SKILLS = [
    # Programming languages
    "python", "java", "javascript", "c++", "c#", "typescript", "r", "go", "swift", "kotlin",
    # Web
    "html", "css", "react", "node.js", "angular", "vue", "bootstrap", "jquery",
    # Backend / APIs
    "flask", "django", "spring", "express", "rest api", "graphql",
    # Data & ML
    "machine learning", "deep learning", "data analysis", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "nlp", "computer vision",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    # DevOps & Cloud
    "git", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "ci/cd",
    # Soft skills
    "communication", "leadership", "teamwork", "problem solving",
    "project management", "agile", "time management",
    # Tools
    "excel", "tableau", "power bi", "figma", "jira", "postman",
]

# Also load dataset skills for display — but only for matching, not scoring denominator
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    if 'match_term' in skills_data.columns:
        skills_data = skills_data.dropna(subset=['match_term'])
        _dataset_terms  = [str(t).lower().strip() for t in skills_data['match_term'].tolist()]
        _dataset_names  = skills_data['skill_name'].tolist()
    else:
        col = 'skill' if 'skill' in skills_data.columns else skills_data.columns[0]
        _dataset_terms = [str(t).lower().strip() for t in skills_data[col].dropna().tolist()]
        _dataset_names = _dataset_terms
    print(f"[ats_score] Loaded {len(_dataset_terms)} skills from dataset (using {len(CORE_SKILLS)} core skills for scoring)")
except Exception as e:
    print(f"[ats_score] Dataset not available, using core skills only: {e}")
    _dataset_terms = []
    _dataset_names = []


def _match_skill(term: str, resume_lower: str) -> bool:
    """Word-boundary match for short terms to avoid false positives."""
    if len(term) <= 3:
        return bool(re.search(r'\b' + re.escape(term) + r'\b', resume_lower))
    return term in resume_lower


def calculate_ats_score(resume_text: str):
    """
    Scores resume against CORE_SKILLS list for a meaningful 0-100% ATS score.
    Also returns all matched skills (including dataset skills) for display.

    Returns:
        score (float): % of core skills found (0-100)
        matched (list): all matched skill names for display
    """
    resume_lower = resume_text.lower()

    # Score against core skills (fixed denominator = len(CORE_SKILLS))
    core_matched = [sk for sk in CORE_SKILLS if _match_skill(sk, resume_lower)]
    score = round((len(core_matched) / len(CORE_SKILLS)) * 100, 1)

    # Build display list: use dataset names when available, else core matches
    display_matched = []
    seen = set()

    # First add dataset matches (richer display names)
    for term, name in zip(_dataset_terms, _dataset_names):
        if term not in seen and _match_skill(term, resume_lower):
            display_matched.append(str(name))
            seen.add(term)

    # Add any core matches not already covered
    for sk in core_matched:
        if sk not in seen:
            display_matched.append(sk.title())
            seen.add(sk)

    return score, display_matched
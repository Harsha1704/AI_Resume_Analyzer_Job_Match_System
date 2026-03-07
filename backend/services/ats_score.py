import pandas as pd
import os
import re
from config import DATASET_FOLDER

# Load real skills dataset from Kaggle
# The dataset has columns: skill_name, match_term, job_demand_score
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))

    # Use match_term for matching, skill_name for display
    if 'match_term' in skills_data.columns:
        skills_data = skills_data.dropna(subset=['match_term'])
        match_terms  = skills_data['match_term'].tolist()
        display_names = skills_data['skill_name'].tolist()
    else:
        # Fallback if old format
        col = 'skill' if 'skill' in skills_data.columns else skills_data.columns[0]
        match_terms   = skills_data[col].dropna().tolist()
        display_names = match_terms

    print(f"[ats_score] Loaded {len(match_terms)} skills from Kaggle dataset")

except Exception as e:
    print(f"[ats_score] Could not load dataset, using fallback: {e}")
    match_terms = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "communication", "leadership", "teamwork", "excel", "data analysis",
        "problem solving", "project management", "agile", "html", "css",
    ]
    display_names = match_terms


def calculate_ats_score(resume_text: str):
    """
    Scores resume against top in-demand skills from the Kaggle skills dataset.

    Uses match_term for matching (short, clean keywords extracted from full skill names)
    and displays skill_name (full name) in results.

    Returns:
        score (float): percentage of high-demand skills found (0-100)
        matched (list): deduplicated list of matched skill display names
    """
    if not match_terms:
        return 0.0, []

    resume_lower = resume_text.lower()
    seen = set()
    matched = []

    for term, name in zip(match_terms, display_names):
        term_lower = str(term).lower().strip()

        # Skip duplicates
        if term_lower in seen:
            continue

        # Word-boundary matching for short terms (<=3 chars) to avoid false positives
        # e.g. 'sql' shouldn't match inside 'consultation'
        if len(term_lower) <= 3:
            pattern = r'\b' + re.escape(term_lower) + r'\b'
            found = bool(re.search(pattern, resume_lower))
        else:
            found = term_lower in resume_lower

        if found:
            matched.append(str(name))
            seen.add(term_lower)

    score = (len(matched) / len(match_terms)) * 100
    return round(score, 2), matched
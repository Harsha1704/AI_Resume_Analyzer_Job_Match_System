import pandas as pd
import os
import re
from config import DATASET_FOLDER

# Load real skills dataset from Kaggle
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))

    if 'match_term' in skills_data.columns:
        skills_data = skills_data.dropna(subset=['match_term'])
        match_terms   = skills_data['match_term'].tolist()
        display_names = skills_data['skill_name'].tolist()
    else:
        col = 'skill' if 'skill' in skills_data.columns else skills_data.columns[0]
        match_terms   = skills_data[col].dropna().tolist()
        display_names = match_terms

    print(f"[skill_gap] Loaded {len(match_terms)} skills from Kaggle dataset")

except Exception as e:
    print(f"[skill_gap] Could not load dataset, using fallback: {e}")
    match_terms = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "communication", "leadership", "teamwork", "excel", "data analysis",
        "problem solving", "project management", "agile", "html", "css",
    ]
    display_names = match_terms


def detect_skill_gap(resume_text: str):
    """
    Compares resume against top in-demand skills from the Kaggle dataset.

    Returns:
        present (list): skill display names found in the resume
        missing (list): top 10 skill display names NOT found in the resume
    """
    resume_lower = resume_text.lower()
    seen_present = set()
    seen_missing = set()
    present = []
    missing = []

    for term, name in zip(match_terms, display_names):
        term_lower = str(term).lower().strip()
        name_str   = str(name)

        # Dedup by term
        if term_lower in seen_present or term_lower in seen_missing:
            continue

        # Word-boundary matching for short skills
        if len(term_lower) <= 3:
            pattern = r'\b' + re.escape(term_lower) + r'\b'
            found = bool(re.search(pattern, resume_lower))
        else:
            found = term_lower in resume_lower

        if found:
            present.append(name_str)
            seen_present.add(term_lower)
        else:
            missing.append(name_str)
            seen_missing.add(term_lower)

    return present, missing[:10]
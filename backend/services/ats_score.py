import pandas as pd
import os
from config import DATASET_FOLDER

# Load real skills dataset
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    # Column name from our Kaggle extraction is 'skill'
    col = "skill" if "skill" in skills_data.columns else skills_data.columns[0]
    all_skills = skills_data[col].dropna().tolist()
    print(f"[ats_score] Loaded {len(all_skills)} skills from dataset")

except Exception as e:
    print(f"[ats_score] Could not load dataset, using fallback: {e}")
    all_skills = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "communication", "leadership", "teamwork", "excel", "data analysis"
    ]


def calculate_ats_score(resume_text: str):
    """
    Matches resume text against known skills from the dataset.

    Returns:
        score (float): percentage of known skills found (0-100)
        matched (list): list of matched skill names
    """
    resume_lower = resume_text.lower()

    matched = [
        skill for skill in all_skills
        if str(skill).lower() in resume_lower
    ]

    if len(all_skills) == 0:
        return 0.0, []

    score = (len(matched) / len(all_skills)) * 100
    return round(score, 2), matched
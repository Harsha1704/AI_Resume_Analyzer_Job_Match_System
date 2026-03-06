import pandas as pd
import os
from config import DATASET_FOLDER

# Load real skills dataset
try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    col = "skill" if "skill" in skills_data.columns else skills_data.columns[0]
    required_skills = skills_data[col].dropna().tolist()
    print(f"[skill_gap] Loaded {len(required_skills)} skills from dataset")

except Exception as e:
    print(f"[skill_gap] Could not load dataset, using fallback: {e}")
    required_skills = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "communication", "leadership", "teamwork", "excel", "data analysis"
    ]


def detect_skill_gap(resume_text: str):
    """
    Compares resume skills against all known skills.

    Returns:
        present (list): skills found in the resume
        missing (list): top 10 skills NOT found in resume
    """
    resume_lower = resume_text.lower()

    present = []
    missing = []

    for skill in required_skills:
        if str(skill).lower() in resume_lower:
            present.append(skill)
        else:
            missing.append(skill)

    return present, missing[:10]
import pandas as pd
import os

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "..", "datasets")

try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    all_skills = skills_data["skills"].dropna().tolist()
except FileNotFoundError:
    # Fallback default skills list if CSV not found yet
    all_skills = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "gcp", "tensorflow", "pytorch", "scikit-learn", "pandas",
        "numpy", "rest api", "html", "css", "c++", "data analysis", "nlp",
        "communication", "problem solving", "teamwork", "agile", "linux"
    ]


def calculate_ats_score(resume_text: str):
    """
    Returns:
        score (float): percentage of known skills found in resume
        matched (list): list of matched skill names
    """
    resume_lower = resume_text.lower()

    matched = [skill for skill in all_skills if skill.lower() in resume_lower]

    if len(all_skills) == 0:
        return 0.0, []

    score = (len(matched) / len(all_skills)) * 100
    return round(score, 2), matched
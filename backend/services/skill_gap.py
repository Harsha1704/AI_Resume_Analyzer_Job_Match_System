import pandas as pd
import os

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "..", "datasets")

try:
    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))
    required_skills = skills_data["skills"].dropna().tolist()
except FileNotFoundError:
    required_skills = [
        "python", "java", "javascript", "sql", "machine learning", "deep learning",
        "flask", "django", "react", "node.js", "git", "docker", "kubernetes",
        "aws", "azure", "gcp", "tensorflow", "pytorch", "scikit-learn", "pandas",
        "numpy", "rest api", "html", "css", "c++", "data analysis", "nlp",
        "communication", "problem solving", "teamwork", "agile", "linux"
    ]


def detect_skill_gap(resume_text: str):
    """
    Returns:
        present (list): skills found in the resume
        missing (list): top 10 skills NOT found in the resume

    BUG FIXED: original code had `return present, missing[:10]` written as
    `return present, missing[:10]` with an accidental `and` keyword which
    evaluates as a boolean expression, not a tuple. Now correctly returns tuple.
    """
    resume_lower = resume_text.lower()

    present = []
    missing = []

    for skill in required_skills:
        if skill.lower() in resume_lower:
            present.append(skill)
        else:
            missing.append(skill)

    # BUG WAS HERE: `return present, missing[:10]` — fixed (no `and`)
    return present, missing[:10]
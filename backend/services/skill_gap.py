import pandas as pd
from config import DATASET_FOLDER

def analyze_skill_gap(resume_text: str, job_title: str):
    skills_df = pd.read_csv(f"{DATASET_FOLDER}/skills_dataset.csv")

    job_row = skills_df[skills_df["role"] == job_title]

    if job_row.empty:
        return []

    required_skills = job_row.iloc[0]["skills"].split()
    resume_words = set(resume_text.split())

    missing_skills = [skill for skill in required_skills if skill.lower() not in resume_words]

    return missing_skills
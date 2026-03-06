import pandas as pd
from backend.config import DATASET_FOLDER

skills_data = pd.read_csv(f"{DATASET_FOLDER}/skills_dataset.csv")

all_skills = skills_data["skills"].dropna().tolist()


def calculate_ats_score(resume_text):

    resume_text = resume_text.lower()

    matched = []

    for skill in all_skills:

        if skill.lower() in resume_text:
            matched.append(skill)

    score = (len(matched) / len(all_skills)) * 100

    return round(score, 2), matched
import pandas as pd
import os
import re
from config import DATASET_FOLDER
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load semantic model
model = SentenceTransformer("all-MiniLM-L6-v2")


CORE_SKILLS = [
    "python","java","javascript","c++","c#","typescript","r","go",
    "html","css","react","node.js","angular","vue","bootstrap",
    "flask","django","spring","express","rest api","graphql",
    "machine learning","deep learning","data analysis",
    "pandas","numpy","scikit-learn","tensorflow","pytorch","nlp",
    "sql","mysql","postgresql","mongodb","redis","sqlite",
    "git","docker","kubernetes","aws","azure","gcp","linux",
    "communication","leadership","teamwork","problem solving",
    "project management","agile","time management",
    "excel","tableau","power bi","figma","jira","postman"
]


# ---------------------------------------------------
# Skill matching
# ---------------------------------------------------
def _match_skill(skill, text):

    if len(skill) <= 3:
        return bool(re.search(r"\b" + re.escape(skill) + r"\b", text))

    return skill in text


# ---------------------------------------------------
# Extract skills
# ---------------------------------------------------
def extract_skills(text):

    text = text.lower()

    skills = set()

    for skill in CORE_SKILLS:

        if _match_skill(skill, text):
            skills.add(skill)

    return list(skills)


# ---------------------------------------------------
# Semantic similarity
# ---------------------------------------------------
def semantic_similarity(resume_text, job_description):

    emb1 = model.encode([resume_text])
    emb2 = model.encode([job_description])

    sim = cosine_similarity(emb1, emb2)[0][0]

    return sim * 100


# ---------------------------------------------------
# ATS SCORE
# ---------------------------------------------------
def calculate_ats_score(resume_text, job_description):

    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    resume_skills = extract_skills(resume_lower)
    jd_skills = extract_skills(jd_lower)

    if len(jd_skills) == 0:
        return 0, [], [], resume_skills

    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    skill_score = (len(matched) / len(jd_skills)) * 100

    semantic_score = semantic_similarity(resume_text, job_description)

    ats_score = round((0.6 * skill_score) + (0.4 * semantic_score), 1)

    return ats_score, matched, missing, resume_skills
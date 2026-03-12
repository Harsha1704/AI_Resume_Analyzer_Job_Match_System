import pandas as pd
import os
import re
from config import DATASET_FOLDER


# Core in-demand skills used for extraction
CORE_SKILLS = [

    # Programming languages
    "python","java","javascript","c++","c#","typescript","r","go","swift","kotlin",

    # Web
    "html","css","react","node.js","angular","vue","bootstrap","jquery",

    # Backend / APIs
    "flask","django","spring","express","rest api","graphql",

    # Data & ML
    "machine learning","deep learning","data analysis",
    "pandas","numpy","scikit-learn","tensorflow","pytorch","nlp","computer vision",

    # Databases
    "sql","mysql","postgresql","mongodb","redis","sqlite",

    # DevOps & Cloud
    "git","docker","kubernetes","aws","azure","gcp","linux","ci/cd",

    # Soft skills
    "communication","leadership","teamwork","problem solving",
    "project management","agile","time management",

    # Tools
    "excel","tableau","power bi","figma","jira","postman"
]


# ------------------------------------------------------------
# Load dataset skills (for richer skill display)
# ------------------------------------------------------------
try:

    skills_data = pd.read_csv(os.path.join(DATASET_FOLDER, "skills_dataset.csv"))

    if 'match_term' in skills_data.columns:

        skills_data = skills_data.dropna(subset=['match_term'])

        _dataset_terms = [
            str(t).lower().strip()
            for t in skills_data['match_term'].tolist()
        ]

        _dataset_names = skills_data['skill_name'].tolist()

    else:

        col = 'skill' if 'skill' in skills_data.columns else skills_data.columns[0]

        _dataset_terms = [
            str(t).lower().strip()
            for t in skills_data[col].dropna().tolist()
        ]

        _dataset_names = _dataset_terms


    print(f"[ATS] Loaded {len(_dataset_terms)} dataset skills")

except Exception as e:

    print(f"[ATS] Dataset not available: {e}")

    _dataset_terms = []
    _dataset_names = []


# ------------------------------------------------------------
# Skill matching function
# ------------------------------------------------------------
def _match_skill(term: str, text_lower: str) -> bool:
    """
    Word boundary match for short skills to avoid false positives
    """

    if len(term) <= 3:
        return bool(re.search(r'\b' + re.escape(term) + r'\b', text_lower))

    return term in text_lower


# ------------------------------------------------------------
# Extract skills from text
# ------------------------------------------------------------
def extract_skills(text: str):

    text_lower = text.lower()

    found_skills = set()

    for skill in CORE_SKILLS:

        if _match_skill(skill, text_lower):
            found_skills.add(skill)

    return list(found_skills)
# ------------------------------------------------------------
# ATS SCORE CALCULATION (Industry Style)
# ------------------------------------------------------------
def calculate_ats_score(resume_text: str, job_description: str):
    """
    Calculate ATS score based on job description skills.

    Returns:
        score (float)
        matched_skills (list)
        missing_skills (list)
        all_resume_skills (list)
    """

    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # Extract skills
    resume_skills = extract_skills(resume_lower)
    jd_skills = extract_skills(jd_lower)

    if len(jd_skills) == 0:
        return 0, [], [], resume_skills

    # Find matches
    matched_skills = list(set(resume_skills) & set(jd_skills))

    # Missing skills
    missing_skills = list(set(jd_skills) - set(resume_skills))

    # Score
    score = round((len(matched_skills) / len(jd_skills)) * 100, 1)

    return score, matched_skills, missing_skills, resume_skills


# ------------------------------------------------------------
# Display matched skills (dataset + core)
# ------------------------------------------------------------
def get_display_skills(resume_text: str):

    resume_lower = resume_text.lower()

    display_matched = []

    seen = set()

    # Dataset matches
    for term, name in zip(_dataset_terms, _dataset_names):

        if term not in seen and _match_skill(term, resume_lower):

            display_matched.append(str(name))

            seen.add(term)

    # Core matches
    for skill in CORE_SKILLS:

        if skill not in seen and _match_skill(skill, resume_lower):

            display_matched.append(skill.title())

            seen.add(skill)

    return display_matched
import re

# ==============================
# SKILL DATABASE
# ==============================

CORE_SKILLS = [
    "python","java","c++","sql","machine learning","deep learning",
    "data science","nlp","computer vision","pandas","numpy",
    "tensorflow","pytorch","scikit-learn","flask","django",
    "react","node","docker","kubernetes","aws","git"
]

TOOLS = [
    "docker","kubernetes","aws","azure","gcp",
    "tableau","powerbi","git","linux","spark"
]

EDUCATION = [
    "btech","b.tech","mtech","m.tech","bachelor",
    "master","phd","computer science","information technology"
]


# ==============================
# TEXT CLEANING
# ==============================

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    return text


# ==============================
# SKILL EXTRACTION
# ==============================

def extract_items(text, database):
    found = []
    for item in database:
        if item in text:
            found.append(item)
    return list(set(found))


# ==============================
# EXPERIENCE DETECTION
# ==============================

def detect_experience(text):

    exp_patterns = [
        r'\d+\s+years',
        r'\d+\s+year',
        r'\d+\s+months'
    ]

    exp_score = 0

    for pattern in exp_patterns:
        if re.search(pattern, text):
            exp_score = 100
            break

    return exp_score


# ==============================
# KEYWORD DENSITY SCORE
# ==============================

def keyword_score(resume, jd):

    resume_words = resume.split()
    jd_words = jd.split()

    match_count = 0

    for word in jd_words:
        if word in resume_words:
            match_count += 1

    if len(jd_words) == 0:
        return 0

    score = (match_count / len(jd_words)) * 100
    return round(score,2)


# ==============================
# MAIN ATS FUNCTION
# ==============================

def calculate_ats_score(resume_text, job_description):

    resume = clean_text(resume_text)
    jd = clean_text(job_description)

    # Skill extraction
    resume_skills = extract_items(resume, CORE_SKILLS)
    jd_skills = extract_items(jd, CORE_SKILLS)

    matched_skills = list(set(resume_skills) & set(jd_skills))

    if len(jd_skills) > 0:
        skill_score = (len(matched_skills) / len(jd_skills)) * 100
    else:
        skill_score = 0


    # Tool matching
    resume_tools = extract_items(resume, TOOLS)
    jd_tools = extract_items(jd, TOOLS)

    matched_tools = list(set(resume_tools) & set(jd_tools))

    if len(jd_tools) > 0:
        tool_score = (len(matched_tools) / len(jd_tools)) * 100
    else:
        tool_score = 0


    # Education matching
    resume_edu = extract_items(resume, EDUCATION)
    jd_edu = extract_items(jd, EDUCATION)

    matched_edu = list(set(resume_edu) & set(jd_edu))

    if len(jd_edu) > 0:
        edu_score = (len(matched_edu) / len(jd_edu)) * 100
    else:
        edu_score = 50   # default


    # Experience score
    exp_score = detect_experience(resume)


    # Keyword score
    key_score = keyword_score(resume, jd)


    # ==========================
    # FINAL ATS SCORE
    # ==========================

    final_score = (
        skill_score * 0.40 +
        tool_score * 0.15 +
        key_score * 0.20 +
        exp_score * 0.15 +
        edu_score * 0.10
    )

    final_score = round(final_score,2)

    result = {
        "ATS Score": final_score,
        "Matched Skills": matched_skills,
        "Missing Skills": list(set(jd_skills) - set(resume_skills)),
        "Matched Tools": matched_tools,
        "Resume Skills": resume_skills,
        "JD Skills": jd_skills
    }

    return result
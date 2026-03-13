import os
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATASET_FOLDER

model = SentenceTransformer("all-MiniLM-L6-v2")

JD_CSV_PATH = os.path.join(DATASET_FOLDER, "job_description.csv")
CHUNK_SIZE  = 5_000
TOP_N       = 5


# ── Role synonym map ──────────────────────────────────────────────────────────
ROLE_SYNONYMS = {
    "data science"     : ["data scien", "data analyst", "machine learning", "ml engineer", "ai engineer", "data engineer"],
    "data scientist"   : ["data scien", "data analyst", "machine learning", "ml engineer"],
    "machine learning" : ["machine learning", "ml engineer", "data scien", "ai engineer"],
    "software engineer": ["software engineer", "software developer", "backend", "fullstack", "full stack"],
    "frontend"         : ["frontend", "front end", "ui developer", "web developer", "react"],
    "backend"          : ["backend", "back end", "software engineer", "api developer"],
    "full stack"       : ["full stack", "fullstack", "software engineer", "web developer"],
    "web developer"    : ["web developer", "frontend", "full stack", "ui developer"],
    "devops"           : ["devops", "cloud engineer", "site reliability", "sre", "infrastructure"],
    "cloud engineer"   : ["cloud engineer", "devops", "aws", "azure", "gcp"],
    "cybersecurity"    : ["cybersecurity", "security engineer", "information security", "network security"],
    "network engineer" : ["network engineer", "network administrator", "wireless network"],
    "database"         : ["database", "sql developer", "dba", "data engineer"],
    "mobile developer" : ["mobile developer", "android", "ios", "flutter", "react native"],
    "android developer": ["android", "mobile developer", "kotlin", "java developer"],
    "ios developer"    : ["ios", "swift", "mobile developer"],
    "product manager"  : ["product manager", "product owner", "program manager"],
    "project manager"  : ["project manager", "program manager", "scrum master"],
    "ui ux"            : ["ui", "ux", "designer", "product designer", "figma"],
    "designer"         : ["designer", "ui", "ux", "graphic", "visual"],
    "marketing"        : ["marketing", "digital marketing", "social media", "seo", "growth"],
    "sales"            : ["sales", "account manager", "business development"],
    "hr"               : ["human resources", "hr", "talent acquisition", "recruiter"],
    "finance"          : ["finance", "financial analyst", "accountant", "investment"],
    "business analyst" : ["business analyst", "data analyst", "product analyst"],
    "content writer"   : ["content writer", "copywriter", "technical writer", "content creator"],
    "data engineer"    : ["data engineer", "etl", "pipeline", "spark", "hadoop", "data scien"],
    "nlp"              : ["nlp", "natural language", "data scien", "machine learning"],
    "computer vision"  : ["computer vision", "image processing", "deep learning", "data scien"],
}


def _clean(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def _get_search_keywords(predicted_role: str) -> list:
    role_lower = predicted_role.lower().strip()

    # Check synonym map (partial key match)
    for key, synonyms in ROLE_SYNONYMS.items():
        if key in role_lower or role_lower in key:
            return synonyms

    # Fallback: individual words from role name
    words = re.findall(r'[a-zA-Z]+', role_lower)
    return [role_lower] + [w for w in words if len(w) > 3]


def _row_matches_role(row_role, row_title, keywords) -> bool:
    combined = (str(row_role) + " " + str(row_title)).lower()
    return any(kw in combined for kw in keywords)


def _score_jd(resume_embedding, jd_text: str, resume_skills: list) -> float:
    if not jd_text:
        return 0.0

    jd_emb    = model.encode([jd_text])
    sem_score = float(cosine_similarity(resume_embedding, jd_emb)[0][0]) * 100

    jd_lower    = jd_text.lower()
    matched     = sum(1 for s in resume_skills if s.lower() in jd_lower)
    skill_score = (matched / max(len(resume_skills), 1)) * 100

    return round(0.5 * sem_score + 0.5 * skill_score, 2)


def match_jobs(resume_text: str, predicted_role: str, resume_skills: list,
               top_n: int = TOP_N) -> list:

    if not os.path.exists(JD_CSV_PATH):
        return [{"error": f"Dataset not found at {JD_CSV_PATH}"}]

    keywords   = _get_search_keywords(predicted_role)
    resume_emb = model.encode([resume_text])
    candidates = []

    use_cols = [
        "Job Title", "Role", "Job Description", "skills",
        "Company", "location", "Country", "Salary Range",
        "Work Type", "Experience", "Job Portal", "Benefits"
    ]

    try:
        reader = pd.read_csv(
            JD_CSV_PATH,
            usecols=lambda c: c in use_cols,
            chunksize=CHUNK_SIZE,
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=True,
        )
    except Exception as e:
        return [{"error": f"Failed to read dataset: {str(e)}"}]

    for chunk in reader:
        chunk["Role"]      = chunk["Role"].fillna("")
        chunk["Job Title"] = chunk["Job Title"].fillna("")

        mask = chunk.apply(
            lambda row: _row_matches_role(row["Role"], row["Job Title"], keywords),
            axis=1
        )
        filtered = chunk[mask]

        if filtered.empty:
            continue

        for _, row in filtered.iterrows():
            jd_text = (
                _clean(row.get("Job Description", "")) + " " +
                _clean(row.get("skills", ""))
            ).strip()

            score = _score_jd(resume_emb, jd_text, resume_skills)

            candidates.append({
                "Job Title"              : _clean(row.get("Job Title", "")),
                "Role"                   : _clean(row.get("Role", "")),
                "Company"                : _clean(row.get("Company", "")),
                "Location"               : _clean(row.get("location", "")) + ", " + _clean(row.get("Country", "")),
                "Salary Range"           : _clean(row.get("Salary Range", "")),
                "Work Type"              : _clean(row.get("Work Type", "")),
                "Experience"             : _clean(row.get("Experience", "")),
                "Job Portal"             : _clean(row.get("Job Portal", "")),
                "Benefits"               : _clean(row.get("Benefits", "")),
                "Match Score"            : score,
                "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
            })

        # Early exit once enough strong candidates found
        strong = [c for c in candidates if c["Match Score"] >= 60]
        if len(strong) >= top_n * 3:
            break

    if not candidates:
        return _fallback_match(resume_emb, resume_skills, top_n)

    candidates.sort(key=lambda x: x["Match Score"], reverse=True)
    return candidates[:top_n]


def _fallback_match(resume_emb, resume_skills: list, top_n: int) -> list:
    """
    If role filtering found nothing, scan first 20k rows and return
    best semantic matches regardless of role.
    """
    candidates   = []
    rows_scanned = 0

    use_cols = [
        "Job Title", "Role", "Job Description", "skills",
        "Company", "location", "Country", "Salary Range",
        "Work Type", "Experience", "Job Portal", "Benefits"
    ]

    try:
        reader = pd.read_csv(
            JD_CSV_PATH,
            usecols=lambda c: c in use_cols,
            chunksize=CHUNK_SIZE,
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=True,
        )

        for chunk in reader:
            chunk = chunk.fillna("")
            for _, row in chunk.iterrows():
                jd_text = (
                    _clean(row.get("Job Description", "")) + " " +
                    _clean(row.get("skills", ""))
                ).strip()
                score = _score_jd(resume_emb, jd_text, resume_skills)
                candidates.append({
                    "Job Title"              : _clean(row.get("Job Title", "")),
                    "Role"                   : _clean(row.get("Role", "")),
                    "Company"                : _clean(row.get("Company", "")),
                    "Location"               : _clean(row.get("location", "")) + ", " + _clean(row.get("Country", "")),
                    "Salary Range"           : _clean(row.get("Salary Range", "")),
                    "Work Type"              : _clean(row.get("Work Type", "")),
                    "Experience"             : _clean(row.get("Experience", "")),
                    "Job Portal"             : _clean(row.get("Job Portal", "")),
                    "Benefits"               : _clean(row.get("Benefits", "")),
                    "Match Score"            : score,
                    "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
                })

            rows_scanned += len(chunk)
            if rows_scanned >= 20_000:
                break

    except Exception:
        pass

    if not candidates:
        return [{"message": "No matching jobs found in dataset."}]

    candidates.sort(key=lambda x: x["Match Score"], reverse=True)
    return candidates[:top_n]


def get_best_jd_for_ats(resume_text: str, predicted_role: str,
                         resume_skills: list) -> str:
    matches = match_jobs(resume_text, predicted_role, resume_skills, top_n=1)

    if matches and "error" not in matches[0] and "message" not in matches[0]:
        return matches[0].get("Job Description Preview", "")

    return ""
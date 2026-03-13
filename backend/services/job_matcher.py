import os
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATASET_FOLDER

model = SentenceTransformer("all-MiniLM-L6-v2")

# Auto-detect filename — handles job_descriptions.csv and job_description.csv
_csv_candidates = ["job_descriptions.csv", "job_description.csv"]
JD_CSV_PATH = next(
    (os.path.join(DATASET_FOLDER, f) for f in _csv_candidates
     if os.path.exists(os.path.join(DATASET_FOLDER, f))),
    os.path.join(DATASET_FOLDER, "job_descriptions.csv")
)

CHUNK_SIZE = 5_000
TOP_N      = 5

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
    for key, synonyms in ROLE_SYNONYMS.items():
        if key in role_lower or role_lower in key:
            return synonyms
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
    jd_lower  = jd_text.lower()
    matched   = sum(1 for s in resume_skills if s.lower() in jd_lower)
    skill_score = (matched / max(len(resume_skills), 1)) * 100
    return round(0.5 * sem_score + 0.5 * skill_score, 2)


def _get_col(row, *candidates):
    """Get value from row trying multiple possible column name variants."""
    for c in candidates:
        if c in row.index and pd.notna(row[c]):
            return str(row[c]).strip()
    return ""


def match_jobs(resume_text: str, predicted_role: str, resume_skills: list,
               top_n: int = TOP_N) -> list:

    if not os.path.exists(JD_CSV_PATH):
        return [{"error": f"Dataset not found at {JD_CSV_PATH}. File name should be job_descriptions.csv"}]

    keywords   = _get_search_keywords(predicted_role)
    resume_emb = model.encode([resume_text])
    candidates = []

    try:
        # Read first chunk to detect actual column names
        sample = pd.read_csv(JD_CSV_PATH, nrows=1, encoding="utf-8", on_bad_lines="skip")
        actual_cols = set(sample.columns.tolist())

        # Map wanted columns to actual column names (case-insensitive)
        col_map = {}
        wanted = ["Job Title", "Role", "Job Description", "skills", "Company",
                  "location", "Country", "Salary Range", "Work Type",
                  "Experience", "Job Portal", "Benefits"]
        for w in wanted:
            for ac in actual_cols:
                if w.lower() == ac.lower():
                    col_map[w] = ac
                    break

        use_cols = list(col_map.values())

        reader = pd.read_csv(
            JD_CSV_PATH,
            usecols=use_cols if use_cols else None,
            chunksize=CHUNK_SIZE,
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=True,
        )
    except Exception as e:
        return [{"error": f"Failed to read dataset: {str(e)}"}]

    # Resolve actual column names to use
    role_col  = col_map.get("Role", "Role")
    title_col = col_map.get("Job Title", "Job Title")
    jd_col    = col_map.get("Job Description", "Job Description")
    sk_col    = col_map.get("skills", "skills")
    co_col    = col_map.get("Company", "Company")
    loc_col   = col_map.get("location", "location")
    cnt_col   = col_map.get("Country", "Country")
    sal_col   = col_map.get("Salary Range", "Salary Range")
    wt_col    = col_map.get("Work Type", "Work Type")
    exp_col   = col_map.get("Experience", "Experience")
    por_col   = col_map.get("Job Portal", "Job Portal")
    ben_col   = col_map.get("Benefits", "Benefits")

    for chunk in reader:
        chunk = chunk.fillna("")

        # Safe role/title filter
        r_col_exists = role_col in chunk.columns
        t_col_exists = title_col in chunk.columns

        if not r_col_exists and not t_col_exists:
            continue

        def row_matches(row):
            r = str(row[role_col]) if r_col_exists else ""
            t = str(row[title_col]) if t_col_exists else ""
            return _row_matches_role(r, t, keywords)

        mask     = chunk.apply(row_matches, axis=1)
        filtered = chunk[mask]

        if filtered.empty:
            continue

        for _, row in filtered.iterrows():
            jd_text = (
                _clean(row.get(jd_col, "")) + " " +
                _clean(row.get(sk_col, ""))
            ).strip()
            score = _score_jd(resume_emb, jd_text, resume_skills)

            candidates.append({
                "Job Title"              : _clean(row.get(title_col, "")),
                "Role"                   : _clean(row.get(role_col, "")),
                "Company"                : _clean(row.get(co_col, "")),
                "Location"               : _clean(row.get(loc_col, "")) + (", " + _clean(row.get(cnt_col, "")) if _clean(row.get(cnt_col, "")) else ""),
                "Salary Range"           : _clean(row.get(sal_col, "")),
                "Work Type"              : _clean(row.get(wt_col, "")),
                "Experience"             : _clean(row.get(exp_col, "")),
                "Job Portal"             : _clean(row.get(por_col, "")),
                "Benefits"               : _clean(row.get(ben_col, "")),
                "Match Score"            : score,
                "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
            })

        strong = [c for c in candidates if c["Match Score"] >= 60]
        if len(strong) >= top_n * 3:
            break

    if not candidates:
        return _fallback_match(resume_emb, resume_skills, top_n)

    candidates.sort(key=lambda x: x["Match Score"], reverse=True)
    return candidates[:top_n]


def _fallback_match(resume_emb, resume_skills: list, top_n: int) -> list:
    """Scan first 20k rows regardless of role — always returns something."""
    candidates   = []
    rows_scanned = 0
    try:
        reader = pd.read_csv(
            JD_CSV_PATH, chunksize=CHUNK_SIZE,
            on_bad_lines="skip", encoding="utf-8", low_memory=True,
        )
        for chunk in reader:
            chunk = chunk.fillna("")
            # Detect columns dynamically
            cols = chunk.columns.tolist()
            jd_col  = next((c for c in cols if "description" in c.lower()), None)
            sk_col  = next((c for c in cols if c.lower() == "skills"), None)
            t_col   = next((c for c in cols if "title" in c.lower()), None)
            r_col   = next((c for c in cols if c.lower() == "role"), None)
            co_col  = next((c for c in cols if "company" in c.lower() and "profile" not in c.lower()), None)
            loc_col = next((c for c in cols if c.lower() in ["location","city","loc"]), None)
            sal_col = next((c for c in cols if "salary" in c.lower()), None)
            wt_col  = next((c for c in cols if "work type" in c.lower() or c.lower()=="work type"), None)
            exp_col = next((c for c in cols if "experience" in c.lower()), None)

            for _, row in chunk.iterrows():
                jd_text = (
                    (_clean(row.get(jd_col,"")) if jd_col else "") + " " +
                    (_clean(row.get(sk_col,"")) if sk_col else "")
                ).strip()
                score = _score_jd(resume_emb, jd_text, resume_skills)
                candidates.append({
                    "Job Title"              : _clean(row.get(t_col,"")) if t_col else "",
                    "Role"                   : _clean(row.get(r_col,"")) if r_col else "",
                    "Company"                : _clean(row.get(co_col,"")) if co_col else "",
                    "Location"               : _clean(row.get(loc_col,"")) if loc_col else "",
                    "Salary Range"           : _clean(row.get(sal_col,"")) if sal_col else "",
                    "Work Type"              : _clean(row.get(wt_col,"")) if wt_col else "",
                    "Experience"             : _clean(row.get(exp_col,"")) if exp_col else "",
                    "Job Portal"             : "",
                    "Benefits"               : "",
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
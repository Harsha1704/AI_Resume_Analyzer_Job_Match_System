import os
import re
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATASET_FOLDER

model = SentenceTransformer("all-MiniLM-L6-v2")

_csv_candidates = ["job_descriptions.csv", "job_description.csv"]
JD_CSV_PATH = next(
    (os.path.join(DATASET_FOLDER, f) for f in _csv_candidates
     if os.path.exists(os.path.join(DATASET_FOLDER, f))),
    os.path.join(DATASET_FOLDER, "job_descriptions.csv")
)

CHUNK_SIZE   = 20_000   # read more rows per I/O operation   # larger chunks = fewer I/O reads
TOP_N        = 5
MAX_FILTER   = 150      # score top 150 matches — enough for top 5      # max role-filtered rows to score (keeps it fast)
FALLBACK_MAX = 5_000    # fallback scans first 5k rows only   # rows to scan in fallback

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


def _clean(val):
    if not isinstance(val, str):
        return ""
    return re.sub(r'\s+', ' ', val).strip()


def _get_search_keywords(predicted_role: str) -> list:
    role_lower = predicted_role.lower().strip()
    for key, synonyms in ROLE_SYNONYMS.items():
        if key in role_lower or role_lower in key:
            return synonyms
    words = re.findall(r'[a-zA-Z]+', role_lower)
    return [role_lower] + [w for w in words if len(w) > 3]


def _detect_columns(df: pd.DataFrame) -> dict:
    """Map logical names → actual column names using case-insensitive matching."""
    cols = df.columns.tolist()
    def find(candidates):
        for c in candidates:
            for ac in cols:
                if ac.lower().strip() == c.lower():
                    return ac
        return None

    return {
        "title"  : find(["job title", "title"]),
        "role"   : find(["role"]),
        "jd"     : find(["job description", "description"]),
        "skills" : find(["skills", "skill"]),
        "company": find(["company"]),
        "loc"    : find(["location", "city", "loc"]),
        "country": find(["country"]),
        "salary" : find(["salary range", "salary"]),
        "wtype"  : find(["work type", "worktype", "employment type"]),
        "exp"    : find(["experience"]),
        "portal" : find(["job portal", "portal", "source"]),
        "benefits": find(["benefits"]),
    }


def _batch_score(resume_emb, jd_texts: list, resume_skills: list) -> list:
    """
    Encode ALL jd_texts in ONE model call → 10-20x faster than one-by-one.
    Returns list of float scores.
    """
    if not jd_texts:
        return []

    # Single batch encode
    jd_embs    = model.encode(jd_texts, batch_size=64, show_progress_bar=False)
    sem_scores = cosine_similarity(resume_emb, jd_embs)[0] * 100  # shape (N,)

    scores = []
    for i, jd_text in enumerate(jd_texts):
        jd_lower    = jd_text.lower()
        matched     = sum(1 for s in resume_skills if s.lower() in jd_lower)
        skill_score = (matched / max(len(resume_skills), 1)) * 100
        scores.append(round(0.5 * float(sem_scores[i]) + 0.5 * skill_score, 2))

    return scores


def match_jobs(resume_text: str, predicted_role: str, resume_skills: list,
               top_n: int = TOP_N) -> list:

    if not os.path.exists(JD_CSV_PATH):
        return [{"error": f"Dataset not found: {JD_CSV_PATH}"}]

    keywords   = _get_search_keywords(predicted_role)
    resume_emb = model.encode([resume_text])  # shape (1, dim)

    # ── Step 1: Collect filtered rows (keyword match only, no encoding yet) ──
    filtered_rows = []

    try:
        reader = pd.read_csv(
            JD_CSV_PATH,
            chunksize=CHUNK_SIZE,
            on_bad_lines="skip",
            encoding="utf-8",
            low_memory=True,
        )
    except Exception as e:
        return [{"error": f"Failed to read dataset: {str(e)}"}]

    cm = None  # column map, detected on first chunk

    for chunk in reader:
        chunk = chunk.fillna("")
        if cm is None:
            cm = _detect_columns(chunk)

        role_col  = cm.get("role")
        title_col = cm.get("title")

        def matches(row):
            r = str(row[role_col])  if role_col  else ""
            t = str(row[title_col]) if title_col else ""
            combined = (r + " " + t).lower()
            return any(kw in combined for kw in keywords)

        mask     = chunk.apply(matches, axis=1)
        filtered = chunk[mask]
        filtered_rows.extend(filtered.to_dict("records"))

        # Stop collecting once we have enough candidates
        if len(filtered_rows) >= MAX_FILTER:
            break

    if not filtered_rows:
        return _fallback_match(resume_emb, resume_skills, top_n)

    # ── Step 2: Pre-filter by skill overlap (cheap, before encoding) ─────────
    jd_col  = cm.get("jd")
    sk_col  = cm.get("skills")
    filtered_rows = _skill_prefilter(filtered_rows, resume_skills, jd_col, sk_col, top_n=150)

    jd_texts = []
    for row in filtered_rows:
        jd  = _clean(row.get(jd_col,  "")) if jd_col  else ""
        sk  = _clean(row.get(sk_col,  "")) if sk_col  else ""
        jd_texts.append((jd + " " + sk).strip())

    scores = _batch_score(resume_emb, jd_texts, resume_skills)

    # ── Step 3: Build result dicts ────────────────────────────────────────────
    t_col   = cm.get("title")
    r_col   = cm.get("role")
    co_col  = cm.get("company")
    loc_col = cm.get("loc")
    cnt_col = cm.get("country")
    sal_col = cm.get("salary")
    wt_col  = cm.get("wtype")
    exp_col = cm.get("exp")
    por_col = cm.get("portal")
    ben_col = cm.get("benefits")

    results = []
    for row, jd_text, score in zip(filtered_rows, jd_texts, scores):
        loc = _clean(row.get(loc_col, "")) if loc_col else ""
        cnt = _clean(row.get(cnt_col, "")) if cnt_col else ""
        results.append({
            "Job Title"              : _clean(row.get(t_col,   "")) if t_col   else "",
            "Role"                   : _clean(row.get(r_col,   "")) if r_col   else "",
            "Company"                : _clean(row.get(co_col,  "")) if co_col  else "",
            "Location"               : (loc + (", " + cnt if cnt else "")).strip(", "),
            "Salary Range"           : _clean(row.get(sal_col, "")) if sal_col else "",
            "Work Type"              : _clean(row.get(wt_col,  "")) if wt_col  else "",
            "Experience"             : _clean(row.get(exp_col, "")) if exp_col else "",
            "Job Portal"             : _clean(row.get(por_col, "")) if por_col else "",
            "Benefits"               : _clean(row.get(ben_col, "")) if ben_col else "",
            "Match Score"            : score,
            "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
        })

    results.sort(key=lambda x: x["Match Score"], reverse=True)
    return results[:top_n]


def _fallback_match(resume_emb, resume_skills: list, top_n: int) -> list:
    """Scan first FALLBACK_MAX rows with batch encoding — fast fallback."""
    rows = []
    cm   = None
    try:
        reader = pd.read_csv(
            JD_CSV_PATH, chunksize=CHUNK_SIZE,
            on_bad_lines="skip", encoding="utf-8", low_memory=True,
        )
        collected = 0
        for chunk in reader:
            chunk = chunk.fillna("")
            if cm is None:
                cm = _detect_columns(chunk)
            rows.extend(chunk.to_dict("records"))
            collected += len(chunk)
            if collected >= FALLBACK_MAX:
                break
    except Exception:
        return [{"message": "No matching jobs found in dataset."}]

    if not rows or cm is None:
        return [{"message": "No matching jobs found in dataset."}]

    jd_col = cm.get("jd")
    sk_col = cm.get("skills")
    jd_texts = [
        (_clean(r.get(jd_col,"")) if jd_col else "") + " " +
        (_clean(r.get(sk_col,"")) if sk_col else "")
        for r in rows
    ]
    scores = _batch_score(resume_emb, jd_texts, resume_skills)

    t_col   = cm.get("title")
    r_col   = cm.get("role")
    co_col  = cm.get("company")
    loc_col = cm.get("loc")
    cnt_col = cm.get("country")
    sal_col = cm.get("salary")
    wt_col  = cm.get("wtype")
    exp_col = cm.get("exp")

    results = []
    for row, jd_text, score in zip(rows, jd_texts, scores):
        loc = _clean(row.get(loc_col,"")) if loc_col else ""
        cnt = _clean(row.get(cnt_col,"")) if cnt_col else ""
        results.append({
            "Job Title"              : _clean(row.get(t_col,  "")) if t_col  else "",
            "Role"                   : _clean(row.get(r_col,  "")) if r_col  else "",
            "Company"                : _clean(row.get(co_col, "")) if co_col else "",
            "Location"               : (loc + (", " + cnt if cnt else "")).strip(", "),
            "Salary Range"           : _clean(row.get(sal_col,"")) if sal_col else "",
            "Work Type"              : _clean(row.get(wt_col, "")) if wt_col  else "",
            "Experience"             : _clean(row.get(exp_col,"")) if exp_col else "",
            "Job Portal"             : "",
            "Benefits"               : "",
            "Match Score"            : score,
            "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
        })

    results.sort(key=lambda x: x["Match Score"], reverse=True)
    return results[:top_n]


def get_best_jd_for_ats(resume_text: str, predicted_role: str,
                         resume_skills: list) -> str:
    matches = match_jobs(resume_text, predicted_role, resume_skills, top_n=1)
    if matches and "error" not in matches[0] and "message" not in matches[0]:
        return matches[0].get("Job Description Preview", "")
    return ""


# ── Pre-filter by skill overlap before expensive encoding ────────────────────
def _skill_prefilter(rows: list, resume_skills: list, jd_col, sk_col, top_n=150) -> list:
    """
    Cheap string-match pre-filter. Keeps only rows with at least 1 skill overlap.
    Sorts by overlap count descending and returns top_n.
    This avoids encoding rows that have zero relevance.
    """
    if not resume_skills:
        return rows[:top_n]

    scored = []
    skills_lower = [s.lower() for s in resume_skills]

    for row in rows:
        jd_text = (
            str(row.get(jd_col, "")) + " " + str(row.get(sk_col, ""))
        ).lower()
        overlap = sum(1 for s in skills_lower if s in jd_text)
        if overlap > 0:
            scored.append((overlap, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    result = [r for _, r in scored[:top_n]]

    # If not enough overlap matches, pad with first rows
    if len(result) < 5:
        result = rows[:top_n]

    return result
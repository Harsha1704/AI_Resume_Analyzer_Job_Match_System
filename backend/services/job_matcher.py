import os
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import DATASET_FOLDER

# ── Model (shared with ats_score.py if already loaded there) ──────────────────
model = SentenceTransformer("all-MiniLM-L6-v2")

JD_CSV_PATH = os.path.join(DATASET_FOLDER, "job_description.csv")
CHUNK_SIZE  = 5_000      # rows per chunk — adjust if RAM is tight
TOP_N       = 5          # how many jobs to return


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def _role_keywords(predicted_role: str) -> list[str]:
    """Break predicted role into individual keywords for flexible matching."""
    words = re.findall(r'[a-zA-Z]+', predicted_role.lower())
    # Also keep the full phrase
    return [predicted_role.lower()] + [w for w in words if len(w) > 3]


def _row_matches_role(row_role: str, keywords: list[str]) -> bool:
    row_lower = str(row_role).lower()
    return any(kw in row_lower for kw in keywords)


def _score_jd(resume_embedding, jd_text: str, resume_skills: list[str]) -> float:
    """Semantic similarity + skill overlap score (0-100)."""
    if not jd_text:
        return 0.0

    # Semantic score
    jd_emb   = model.encode([jd_text])
    sem_score = float(cosine_similarity(resume_embedding, jd_emb)[0][0]) * 100

    # Skill overlap score
    jd_lower = jd_text.lower()
    matched  = sum(1 for s in resume_skills if s in jd_lower)
    skill_score = (matched / max(len(resume_skills), 1)) * 100

    return round(0.5 * sem_score + 0.5 * skill_score, 2)


# ── Main public function ──────────────────────────────────────────────────────

def match_jobs(resume_text: str, predicted_role: str, resume_skills: list[str],
               top_n: int = TOP_N) -> list[dict]:
    """
    Parameters
    ----------
    resume_text    : cleaned resume text
    predicted_role : role string from role_predictor (e.g. "Data Scientist")
    resume_skills  : list of skills extracted from resume
    top_n          : number of top jobs to return

    Returns
    -------
    List of dicts with job details + match score, sorted best-first.
    """

    if not os.path.exists(JD_CSV_PATH):
        return [{"error": f"Dataset not found at {JD_CSV_PATH}"}]

    keywords        = _role_keywords(predicted_role)
    resume_emb      = model.encode([resume_text])
    candidates      = []

    # Columns we actually need — reading only these saves significant memory
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
        # Filter rows that match the predicted role
        mask = chunk["Role"].apply(lambda r: _row_matches_role(r, keywords))
        filtered = chunk[mask]

        if filtered.empty:
            continue

        for _, row in filtered.iterrows():
            jd_text = _clean(row.get("Job Description", "")) + " " + _clean(row.get("skills", ""))
            score   = _score_jd(resume_emb, jd_text, resume_skills)

            candidates.append({
                "Job Title"   : _clean(row.get("Job Title", "")),
                "Role"        : _clean(row.get("Role", "")),
                "Company"     : _clean(row.get("Company", "")),
                "Location"    : _clean(row.get("location", "")) + ", " + _clean(row.get("Country", "")),
                "Salary Range": _clean(row.get("Salary Range", "")),
                "Work Type"   : _clean(row.get("Work Type", "")),
                "Experience"  : _clean(row.get("Experience", "")),
                "Job Portal"  : _clean(row.get("Job Portal", "")),
                "Benefits"    : _clean(row.get("Benefits", "")),
                "Match Score" : score,
                "Job Description Preview": jd_text[:300] + "..." if len(jd_text) > 300 else jd_text,
            })

        # Early exit once we have enough strong candidates to avoid scanning full file
        strong = [c for c in candidates if c["Match Score"] >= 70]
        if len(strong) >= top_n * 3:
            break

    if not candidates:
        return [{"message": f"No jobs found matching role: {predicted_role}"}]

    # Sort by score descending, return top N
    candidates.sort(key=lambda x: x["Match Score"], reverse=True)
    return candidates[:top_n]


# ── Best JD for ATS scoring ───────────────────────────────────────────────────

def get_best_jd_for_ats(resume_text: str, predicted_role: str,
                         resume_skills: list[str]) -> str:
    """
    Returns the single best-matching Job Description text from the dataset
    to be used as the reference JD in calculate_ats_score().
    """
    matches = match_jobs(resume_text, predicted_role, resume_skills, top_n=1)

    if matches and "Job Description Preview" not in matches[0].get("error", "x"):
        best = matches[0]
        return best.get("Job Description Preview", "")

    return ""
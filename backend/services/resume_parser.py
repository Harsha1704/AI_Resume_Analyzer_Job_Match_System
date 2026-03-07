import re

# ── Keywords grouped by category ──────────────────────────────────────────

SECTION_KEYWORDS = [
    "experience", "education", "skills", "summary", "objective",
    "projects", "certifications", "achievements", "internship",
    "employment", "work history", "professional", "career",
    "skills summary", "about me", "profile", "declaration",
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "degree", "university", "college", "school",
    "gpa", "cgpa", "percentage", "graduated", "coursework", "b.tech",
    "b.e", "m.tech", "bsc", "msc", "intermediate", "10th", "12th",
    "lpu", "lovely professional", "engineering", "technology",
]

TECH_SKILLS = [
    "python", "java", "javascript", "sql", "html", "css", "node",
    "react", "flask", "django", "machine learning", "deep learning",
    "c++", "c#", "git", "github", "aws", "docker", "tensorflow",
    "excel", "tableau", "power bi", "mongodb", "mysql",
]

SOFT_SKILLS = [
    "leadership", "communication", "problem-solving", "teamwork",
    "management", "analytical", "creative", "organized",
]

ACTION_VERBS = [
    "developed", "designed", "implemented", "built", "managed",
    "responsible", "led", "collaborated", "achieved", "created",
    "integrated", "leveraged", "provides", "allows", "features",
    "secured", "participated", "qualified", "explored",
]

CERTIFICATION_KEYWORDS = [
    "certified", "certification", "certificate", "course", "learning",
    "great learning", "coursera", "udemy", "nptel", "hackathon",
]

# ── Non-resume document signals ───────────────────────────────────────────
NON_RESUME_KEYWORDS = [
    "invoice", "bill to", "purchase order", "receipt", "total amount",
    "tax invoice", "order number", "unit price", "quantity",
    "dear sir", "dear madam", "to whom it may concern", "sincerely yours",
    "yours faithfully", "i am writing to",
    "abstract", "bibliography", "table of contents", "chapter ",
    "ingredients", "calories", "recipe",
    "patient name", "diagnosis", "prescription", "dosage",
    "balance sheet", "quarterly report", "profit and loss",
]

CONTACT_PATTERN = re.compile(
    r'(\+?\d[\d\s\-]{8,})|'
    r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}|'
    r'linkedin\.com/in/|github\.com/',
    re.IGNORECASE
)

DATE_PATTERN = re.compile(
    r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'
    r'[\s,]*\d{4}\b|'
    r'\b(19|20)\d{2}\s*[-–]\s*((19|20)\d{2}|present|current|now)\b|'
    r'\bsince\s+(19|20)\d{2}\b',
    re.IGNORECASE
)


def _count_hits(text_lower: str, keyword_list: list) -> int:
    return sum(1 for kw in keyword_list if kw in text_lower)


def is_resume(text: str) -> tuple:
    """
    Validates whether the extracted text looks like a real resume.
    Returns (True, "") or (False, reason_string).
    """
    if not text or not isinstance(text, str):
        return False, "No text could be extracted from the file."

    text_lower = text.lower()
    word_count = len(text.split())

    # ── 1. Too short ────────────────────────────────────────────
    if word_count < 30:
        return False, (
            f"The uploaded file is too short to be a resume "
            f"(only {word_count} words found). "
            "Please upload a complete resume."
        )

    # ── 2. Strong non-resume signals ────────────────────────────
    non_resume_hits = [kw for kw in NON_RESUME_KEYWORDS if kw in text_lower]
    if len(non_resume_hits) >= 3:
        return False, (
            "The uploaded file does not appear to be a resume. "
            f"It looks like a different type of document "
            f"(detected signals: {', '.join(non_resume_hits[:3])})."
        )

    # ── 3. Score across multiple categories ─────────────────────
    section_hits      = _count_hits(text_lower, SECTION_KEYWORDS)
    education_hits    = _count_hits(text_lower, EDUCATION_KEYWORDS)
    tech_hits         = _count_hits(text_lower, TECH_SKILLS)
    soft_hits         = _count_hits(text_lower, SOFT_SKILLS)
    action_hits       = _count_hits(text_lower, ACTION_VERBS)
    cert_hits         = _count_hits(text_lower, CERTIFICATION_KEYWORDS)
    has_contact       = bool(CONTACT_PATTERN.search(text))
    has_dates         = bool(DATE_PATTERN.search(text))

    score = (
        min(section_hits, 5)   * 2 +   # max 10 — section headings
        min(education_hits, 4) * 2 +   # max  8 — education details
        min(tech_hits, 5)      * 1 +   # max  5 — tech skills
        min(soft_hits, 3)      * 1 +   # max  3 — soft skills
        min(action_hits, 4)    * 1 +   # max  4 — action verbs
        min(cert_hits, 3)      * 1 +   # max  3 — certs/courses
        (4 if has_contact else 0)   +  # contact info bonus
        (3 if has_dates else 0)        # date range bonus
    )

    # ── 4. Decision — lowered threshold, fresher-friendly ───────
    if score < 6:
        return False, (
            "The uploaded file does not look like a resume. "
            "A valid resume should include sections like Education, "
            "Skills, Projects or Experience, contact details, and dates. "
            "Please upload your actual resume/CV."
        )

    return True, ""


def clean_text(text: str) -> str:
    """Remove extra whitespace and unusual characters."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s@.,\-/]', '', text)
    return text.strip()


def parse_resume(resume_text: str) -> str:
    if not resume_text or not isinstance(resume_text, str):
        return ""
    return clean_text(resume_text)
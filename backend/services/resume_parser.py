import re

# ── Keywords that strongly indicate a real resume ──────────────────────────
RESUME_KEYWORDS = [
    # sections
    "experience", "education", "skills", "summary", "objective",
    "projects", "certifications", "achievements", "internship",
    "employment", "work history", "professional", "career",
    # common resume content
    "bachelor", "master", "degree", "university", "college",
    "gpa", "cgpa", "graduated", "coursework",
    "python", "java", "sql", "excel", "machine learning", "deep learning",
    "communication", "leadership", "teamwork", "management",
    "developed", "designed", "implemented", "built", "managed",
    "responsible", "led", "collaborated", "achieved",
    # contact info patterns handled separately
]

# ── Keywords that indicate it's clearly NOT a resume ───────────────────────
NON_RESUME_KEYWORDS = [
    "invoice", "bill to", "purchase order", "receipt", "total amount",
    "tax invoice", "order number", "item description", "unit price",
    "dear sir", "dear madam", "to whom it may concern", "sincerely",
    "yours faithfully", "this letter", "i am writing",
    "article", "abstract", "introduction", "conclusion", "references",
    "chapter", "table of contents", "bibliography",
    "menu", "ingredients", "recipe", "calories",
    "patient name", "diagnosis", "prescription", "dosage",
    "balance sheet", "profit", "revenue", "quarterly report",
]

# ── Regex patterns for resume-specific content ─────────────────────────────
CONTACT_PATTERN  = re.compile(
    r'(\+?\d[\d\s\-]{8,})|'           # phone number
    r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}|' # email
    r'linkedin\.com/in/',              # linkedin
    re.IGNORECASE
)

DATE_PATTERN = re.compile(
    r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'
    r'[\s,]*\d{4}\b|'
    r'\b(19|20)\d{2}\s*[-–]\s*((19|20)\d{2}|present|current)\b',
    re.IGNORECASE
)


def is_resume(text: str) -> tuple[bool, str]:
    """
    Validates whether the given extracted text looks like a real resume.

    Returns:
        (True,  "")           → valid resume
        (False, reason_str)   → not a resume, with a human-readable reason
    """
    if not text or not isinstance(text, str):
        return False, "No text could be extracted from the file."

    text_lower = text.lower()
    word_count = len(text.split())

    # ── 1. Too short ────────────────────────────────────────────
    if word_count < 50:
        return False, (
            "The uploaded file is too short to be a resume "
            f"(only {word_count} words found). "
            "Please upload a complete resume."
        )

    # ── 2. Strong non-resume signals ────────────────────────────
    non_resume_hits = [kw for kw in NON_RESUME_KEYWORDS if kw in text_lower]
    if len(non_resume_hits) >= 2:
        return False, (
            "The uploaded file does not appear to be a resume. "
            f"It looks like a different type of document "
            f"(detected: {', '.join(non_resume_hits[:3])})."
        )

    # ── 3. Count resume keyword matches ─────────────────────────
    resume_hits = [kw for kw in RESUME_KEYWORDS if kw in text_lower]
    has_contact  = bool(CONTACT_PATTERN.search(text))
    has_dates    = bool(DATE_PATTERN.search(text))

    score = len(resume_hits) + (3 if has_contact else 0) + (2 if has_dates else 0)

    # ── 4. Decision threshold ────────────────────────────────────
    if score < 5:
        return False, (
            "The uploaded file does not look like a resume. "
            "A valid resume should include sections like Experience, "
            "Education, Skills, contact information, and relevant dates. "
            "Please upload your actual resume."
        )

    return True, ""


def clean_text(text: str) -> str:
    """Remove extra whitespace, special characters, normalize text."""
    text = re.sub(r'\s+', ' ', text)           # collapse multiple spaces/newlines
    text = re.sub(r'[^\w\s@.,\-/]', '', text)  # remove unusual special chars
    return text.strip()


def parse_resume(resume_text: str) -> str:
    """
    Accepts raw resume text (already extracted from PDF by the frontend)
    and returns a cleaned version ready for analysis.

    NOTE: PDF extraction is handled in the Streamlit frontend using pdfplumber,
    so this function only needs to clean/normalize the text.
    """
    if not resume_text or not isinstance(resume_text, str):
        return ""

    cleaned = clean_text(resume_text)
    return cleaned
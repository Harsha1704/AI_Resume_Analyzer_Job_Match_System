import re


def clean_text(text: str) -> str:
    """Remove extra whitespace, special characters, normalize text."""
    text = re.sub(r'\s+', ' ', text)          # collapse multiple spaces/newlines
    text = re.sub(r'[^\w\s@.,\-/]', '', text) # remove unusual special chars
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
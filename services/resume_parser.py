from utils.pdf_extractor import extract_text_from_pdf
from utils.text_cleaner import clean_text

def parse_resume(file_path: str) -> str:
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    return cleaned_text
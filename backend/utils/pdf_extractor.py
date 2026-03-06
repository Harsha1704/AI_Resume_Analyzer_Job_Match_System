import pdfplumber


def extract_text_from_pdf(file) -> str:
    """
    Extracts raw text from a PDF file object.
    Used when backend receives a PDF directly (not pre-extracted text).
    """
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[pdf_extractor] Error extracting PDF: {e}")
    return text.strip()
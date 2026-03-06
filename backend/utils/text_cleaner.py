import re


def clean_text(text: str) -> str:
    """
    Cleans raw resume text:
    - Removes HTML tags
    - Removes special characters
    - Collapses extra whitespace
    - Lowercases
    """
    text = str(text)
    text = re.sub(r'<.*?>', ' ', text)           # remove HTML tags
    text = re.sub(r'[^a-zA-Z0-9\s@.,\-/]', ' ', text)  # remove special chars
    text = re.sub(r'\s+', ' ', text)             # collapse spaces
    return text.strip()
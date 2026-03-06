def generate_suggestions(resume_text: str):
    suggestions = []

    if "project" not in resume_text:
        suggestions.append("Add project section to strengthen profile.")

    if "github" not in resume_text:
        suggestions.append("Add GitHub profile link.")

    if len(resume_text.split()) < 300:
        suggestions.append("Expand resume with more achievements.")

    return suggestions
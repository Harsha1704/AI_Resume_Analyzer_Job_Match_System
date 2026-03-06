def generate_suggestions(ats_score: float, missing_skills: list) -> list:
    """
    Returns actionable resume improvement suggestions.

    Args:
        ats_score (float): the ATS score percentage (0-100)
        missing_skills (list): list of skills not found in resume

    BUG FIXED: original app.py called generate_suggestions(parsed_resume)
    with 1 argument, but this function needs 2. app.py now correctly passes
    (ats_score, missing_skills).
    """
    suggestions = []

    if ats_score < 40:
        suggestions.append("Your ATS score is very low — add more relevant technical skills")

    if ats_score < 60:
        suggestions.append("Add more technical skills to improve your ATS score")

    if ats_score < 80:
        suggestions.append("Improve project descriptions with more detail and impact")

    if len(missing_skills) > 0:
        suggestions.append("Consider learning: " + ", ".join(missing_skills[:5]))

    suggestions.append("Add a GitHub profile link to showcase your projects")
    suggestions.append("Add measurable achievements (e.g. 'Reduced load time by 30%')")
    suggestions.append("Use action verbs: Built, Designed, Optimized, Led, Deployed")
    suggestions.append("Keep resume to 1-2 pages maximum")

    return suggestions
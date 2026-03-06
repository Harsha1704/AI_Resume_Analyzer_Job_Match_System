def generate_suggestions(ats_score: float, missing_skills: list) -> list:
    """
    Generates actionable resume improvement suggestions based on
    ATS score and detected skill gaps.
    """
    suggestions = []

    if ats_score < 40:
        suggestions.append("🔴 Very low ATS score — add more relevant technical and domain skills")

    if ats_score < 60:
        suggestions.append("🟠 Add more keywords matching your target job description")

    if ats_score < 80:
        suggestions.append("🟡 Improve project descriptions with specific tools and technologies used")

    if ats_score >= 80:
        suggestions.append("🟢 Great ATS score! Focus on quantifying your achievements")

    if len(missing_skills) > 0:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"📚 Consider learning these in-demand skills: {top_missing}")

    suggestions.append("🔗 Add your GitHub / LinkedIn / Portfolio links")
    suggestions.append("📏 Keep resume to 1-2 pages maximum")
    suggestions.append("📊 Add measurable achievements (e.g. 'Reduced load time by 30%')")
    suggestions.append("✍️ Use strong action verbs: Built, Designed, Optimized, Led, Deployed")
    suggestions.append("🎯 Tailor your resume for each specific job application")

    return suggestions
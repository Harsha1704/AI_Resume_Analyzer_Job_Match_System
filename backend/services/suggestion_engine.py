import re

# Contact/profile link patterns to check in resume text
GITHUB_PATTERN    = re.compile(r'github\.com/|github:', re.IGNORECASE)
LINKEDIN_PATTERN  = re.compile(r'linkedin\.com/in/|linkedin:', re.IGNORECASE)
PORTFOLIO_PATTERN = re.compile(r'portfolio|personal website|my website', re.IGNORECASE)


def generate_suggestions(ats_score: float, missing_skills: list, resume_text: str = "") -> list:
    """
    Generates actionable resume improvement suggestions based on
    ATS score, detected skill gaps, and what's already in the resume.
    """
    suggestions = []
    resume_lower = resume_text.lower() if resume_text else ""

    # ── ATS score-based tips ─────────────────────────────────────
    if ats_score < 40:
        suggestions.append("🔴 Low ATS score — add more relevant technical skills like Git, SQL, frameworks you've used")
    if ats_score < 60:
        suggestions.append("🟠 Add keywords from the job descriptions you're targeting")
    if ats_score < 80:
        suggestions.append("🟡 Improve project descriptions — mention specific tools, libraries, and technologies used")
    if ats_score >= 80:
        suggestions.append("🟢 Great ATS score! Focus on quantifying your achievements with numbers")

    # ── Skill gap tips ───────────────────────────────────────────
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"📚 Consider learning these in-demand skills: {top_missing}")

    # ── Contact / profile links (only suggest what's actually missing) ──
    missing_links = []
    if resume_text and not GITHUB_PATTERN.search(resume_text):
        missing_links.append("GitHub")
    if resume_text and not LINKEDIN_PATTERN.search(resume_text):
        missing_links.append("LinkedIn")
    if resume_text and not PORTFOLIO_PATTERN.search(resume_text):
        missing_links.append("Portfolio")

    if missing_links:
        suggestions.append(f"🔗 Consider adding these profile links: {', '.join(missing_links)}")
    # If all links already present — no suggestion needed

    # ── Universal tips ───────────────────────────────────────────
    suggestions.append("📏 Keep resume to 1–2 pages maximum")
    suggestions.append("📊 Add measurable achievements (e.g. 'Reduced load time by 30%', 'Trained model with 92% accuracy')")
    suggestions.append("✍️  Use strong action verbs: Built, Designed, Optimized, Led, Deployed")
    suggestions.append("🎯 Tailor your resume for each specific job application")

    # ── Fresher-specific tips ────────────────────────────────────
    if "git" not in resume_lower and resume_text:
        suggestions.append("💡 Add Git/GitHub to your skills — it's expected for all tech roles")
    if "sql" not in resume_lower and resume_text:
        suggestions.append("💡 Basic SQL knowledge is highly valued — consider adding it")

    return suggestions
import re

# ── Patterns to detect what's already in the resume ───────────────────────
GITHUB_PATTERN      = re.compile(r'github\.com/|github\s*:', re.IGNORECASE)
LINKEDIN_PATTERN    = re.compile(r'linkedin\.com/in/|linkedin\s*:', re.IGNORECASE)
PORTFOLIO_PATTERN   = re.compile(r'portfolio|personal\s+website', re.IGNORECASE)
METRICS_PATTERN     = re.compile(r'\d+\s*(%|percent|accuracy|ms|seconds|users|requests|records|k\b)', re.IGNORECASE)
ACTION_VERB_PATTERN = re.compile(r'\b(built|designed|optimized|deployed|led|developed|implemented|created|improved|reduced|increased|automated|architected|trained|fine.tuned)\b', re.IGNORECASE)
SUMMARY_PATTERN     = re.compile(r'\b(summary|objective|about me|profile)\b', re.IGNORECASE)
GIT_PATTERN         = re.compile(r'\bgit\b|\bgithub\b', re.IGNORECASE)
SQL_PATTERN         = re.compile(r'\bsql\b|\bmysql\b|\bpostgresql\b|\bsqlite\b', re.IGNORECASE)
CGPA_PATTERN        = re.compile(r'cgpa\s*:\s*na|cgpa\s*na', re.IGNORECASE)

# ── Role-specific important skills to recommend ────────────────────────────
ROLE_SKILL_TIPS = {
    "WEB-DEVELOPER": {
        "should_have": ["git", "javascript", "react", "sql", "rest api", "bootstrap", "figma"],
        "nice_to_have": ["typescript", "docker", "aws", "mongodb"],
    },
    "DATA-SCIENCE": {
        "should_have": ["python", "pandas", "numpy", "scikit-learn", "sql", "matplotlib", "jupyter"],
        "nice_to_have": ["tensorflow", "pytorch", "spark", "tableau", "power bi"],
    },
    "SOFTWARE-ENGINEER": {
        "should_have": ["git", "sql", "docker", "rest api", "algorithms", "data structures"],
        "nice_to_have": ["kubernetes", "aws", "ci/cd", "microservices"],
    },
    "INFORMATION-TECHNOLOGY": {
        "should_have": ["linux", "networking", "sql", "git", "cloud"],
        "nice_to_have": ["docker", "aws", "cybersecurity", "bash"],
    },
    "FINANCE": {
        "should_have": ["excel", "accounting", "tally", "gst", "financial modeling"],
        "nice_to_have": ["power bi", "python", "sql"],
    },
    "HR": {
        "should_have": ["recruitment", "payroll", "excel", "communication"],
        "nice_to_have": ["hr software", "data analysis", "python"],
    },
}


def _has(pattern, text):
    return bool(pattern.search(text))


def generate_suggestions(ats_score: float, missing_skills: list, resume_text: str = "") -> list:
    """
    Generates fully dynamic, resume-aware suggestions.
    Every tip is based on what's actually present or missing in THIS resume.
    """
    suggestions = []
    r = resume_text  # shorthand

    # ── 1. ATS score feedback with specific reason ─────────────
    if ats_score < 20:
        suggestions.append(
            f"🔴 ATS Score is {ats_score}% — very low. "
            "Add more technical skills, tools, and keywords you've actually used in projects."
        )
    elif ats_score < 40:
        suggestions.append(
            f"🟠 ATS Score is {ats_score}% — below average. "
            "Expand your Skills section with specific tools, libraries, and technologies from your projects."
        )
    elif ats_score < 60:
        suggestions.append(
            f"🟡 ATS Score is {ats_score}% — moderate. "
            "You're on the right track. Add more keywords matching your target job role."
        )
    elif ats_score < 80:
        suggestions.append(
            f"🟢 ATS Score is {ats_score}% — good. "
            "A few more relevant skills and quantified results will push you higher."
        )
    else:
        suggestions.append(
            f"🌟 ATS Score is {ats_score}% — excellent! "
            "Focus on quantifying your achievements with numbers and metrics."
        )

    # ── 2. Missing contact/profile links ──────────────────────
    if r:
        if not _has(GITHUB_PATTERN, r):
            suggestions.append("🔗 Add your GitHub profile link — essential for tech roles to showcase your code.")
        if not _has(LINKEDIN_PATTERN, r):
            suggestions.append("🔗 Add your LinkedIn profile — most recruiters verify candidates here.")
        if not _has(PORTFOLIO_PATTERN, r):
            suggestions.append("🌐 Consider adding a portfolio website link to showcase your projects live.")

    # ── 3. CGPA is NA — specific advice ───────────────────────
    if r and _has(CGPA_PATTERN, r):
        suggestions.append(
            "📝 Your CGPA shows as 'NA' — once you receive your grades, add your GPA/CGPA to strengthen your profile."
        )

    # ── 4. Metrics / quantification check ─────────────────────
    if r and not _has(METRICS_PATTERN, r):
        suggestions.append(
            "📊 None of your project descriptions have measurable results. "
            "Add numbers like: 'achieved 92% accuracy', 'reduced load time by 40%', 'handled 500+ users'."
        )

    # ── 5. Action verbs check ──────────────────────────────────
    if r:
        action_matches = ACTION_VERB_PATTERN.findall(r)
        if len(action_matches) < 3:
            suggestions.append(
                "✍️  Use stronger action verbs in project descriptions: "
                "Built, Designed, Deployed, Optimized, Trained, Automated, Implemented."
            )

    # ── 6. Summary/Objective section missing ──────────────────
    if r and not _has(SUMMARY_PATTERN, r):
        suggestions.append(
            "📌 Add a 2–3 line 'Summary' or 'Objective' section at the top — "
            "it gives recruiters an instant snapshot of who you are."
        )

    # ── 7. Git missing from skills ─────────────────────────────
    if r and not _has(GIT_PATTERN, r):
        suggestions.append(
            "💻 Git is not mentioned in your resume — add it to your Skills section. "
            "It is expected for every tech role."
        )

    # ── 8. SQL missing ─────────────────────────────────────────
    if r and not _has(SQL_PATTERN, r):
        suggestions.append(
            "🗄️  SQL is not listed — even basic SQL knowledge is highly valued. "
            "Consider learning it and adding it to your skills."
        )

    # ── 9. Top missing skills from the user's actual gap ──────
    if missing_skills:
        # Filter to only the most impactful ones (first 5)
        top = missing_skills[:5]
        suggestions.append(
            f"📚 Top in-demand skills not on your resume: {', '.join(top)}. "
            "Focus on these for your target role."
        )

    # ── 10. Resume length / formatting ────────────────────────
    if r:
        word_count = len(r.split())
        if word_count < 200:
            suggestions.append(
                f"📏 Your resume is quite short ({word_count} words). "
                "Expand your project descriptions with technical details, challenges, and outcomes."
            )
        elif word_count > 800:
            suggestions.append(
                f"📏 Your resume is long ({word_count} words). "
                "Try to keep it to 1–2 pages — focus on the most impactful content."
            )

    # ── 11. Always: tailoring reminder ────────────────────────
    suggestions.append(
        "🎯 Tailor your resume for each job application — "
        "match the keywords from the job description to pass ATS filters."
    )

    return suggestions
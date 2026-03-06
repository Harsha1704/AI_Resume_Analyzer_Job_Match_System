def recommend_career_path(match_score: float, missing_skills: list):
    if match_score > 0.8:
        return "You are highly aligned with this role."

    if missing_skills:
        return f"Improve skills: {', '.join(missing_skills[:3])}"

    return "Keep improving domain knowledge."
import os

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "..", "datasets")

_use_csv = False
career_data = None

try:
    import pandas as pd
    career_data = pd.read_csv(os.path.join(DATASET_FOLDER, "career_paths.csv"))
    _use_csv = True
except Exception as e:
    print(f"[career_path] Dataset not available, using fallback: {e}")

FALLBACK_PATHS = {
    "Python Developer": [
        "Senior Python Developer",
        "Backend Engineer",
        "Software Architect",
        "Engineering Manager"
    ],
    "Data Scientist": [
        "Senior Data Scientist",
        "ML Engineer",
        "AI Research Scientist",
        "Head of Data Science"
    ],
    "Frontend Developer": [
        "Senior Frontend Developer",
        "Full Stack Developer",
        "UI/UX Engineer",
        "Frontend Architect"
    ],
    "DevOps Engineer": [
        "Senior DevOps Engineer",
        "Site Reliability Engineer (SRE)",
        "Cloud Architect",
        "Platform Engineering Lead"
    ],
    "Data Analyst": [
        "Senior Data Analyst",
        "Business Intelligence Engineer",
        "Data Scientist",
        "Analytics Manager"
    ],
    "ML Engineer": [
        "Senior ML Engineer",
        "Applied Scientist",
        "AI/ML Architect",
        "Director of AI"
    ],
    "Backend Developer": [
        "Senior Backend Developer",
        "Software Architect",
        "Engineering Lead",
        "CTO"
    ],
    "Full Stack Developer": [
        "Senior Full Stack Developer",
        "Tech Lead",
        "Software Architect",
        "VP Engineering"
    ],
}


def recommend_career(role: str) -> list:
    """
    Returns a list of next career steps for a given role.
    Uses CSV dataset if available, otherwise uses built-in fallback map.
    """
    if _use_csv and career_data is not None:
        paths = career_data[career_data["current_role"] == role]
        if len(paths) > 0:
            return paths["next_role"].tolist()

    # Fallback map
    if role in FALLBACK_PATHS:
        return FALLBACK_PATHS[role]

    # Generic path if role not found
    return [
        f"Senior {role}",
        "Tech Lead",
        "Engineering Manager",
        "Director of Engineering"
    ]
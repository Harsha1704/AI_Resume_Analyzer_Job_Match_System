import pandas as pd
import os
from config import DATASET_FOLDER

# Load career paths CSV safely
_use_csv    = False
career_data = None

try:
    career_data = pd.read_csv(
        os.path.join(DATASET_FOLDER, "career_paths.csv"),
        on_bad_lines='skip',
        encoding='utf-8'
    )
    if 'current_role' in career_data.columns and 'next_role' in career_data.columns:
        _use_csv = True
        print(f"[career_path] Loaded {len(career_data)} career path entries")
    else:
        print(f"[career_path] CSV missing expected columns, using fallback. Columns found: {list(career_data.columns)}")
except Exception as e:
    print(f"[career_path] Could not load dataset, using fallback: {e}")

# ── Fallback career paths ──────────────────────────────────────────────────
FALLBACK_PATHS = {
    "WEB-DEVELOPER":           ["Senior Web Developer", "Frontend Lead", "Full Stack Developer", "Engineering Manager"],
    "SOFTWARE-ENGINEER":       ["Senior Software Engineer", "Tech Lead", "Principal Engineer", "CTO"],
    "DATA-SCIENCE":            ["Senior Data Scientist", "ML Engineer", "AI Research Lead", "Head of Data"],
    "INFORMATION-TECHNOLOGY":  ["Senior Developer", "Tech Lead", "Engineering Manager", "CTO"],
    "FINANCE":                 ["Senior Financial Analyst", "Finance Manager", "VP Finance", "CFO"],
    "HR":                      ["HR Manager", "HR Business Partner", "HR Director", "CHRO"],
    "SALES":                   ["Senior Sales Executive", "Sales Manager", "VP Sales", "CSO"],
    "HEALTHCARE":              ["Senior Clinician", "Medical Supervisor", "Medical Director", "CMO"],
    "ENGINEERING":             ["Senior Engineer", "Lead Engineer", "Engineering Director", "VP Engineering"],
    "TEACHER":                 ["Senior Teacher", "Head of Department", "Vice Principal", "Principal"],
    "BANKING":                 ["Senior Banker", "Branch Manager", "Regional Director", "Head of Banking"],
    "ACCOUNTANT":              ["Senior Accountant", "Finance Controller", "Head of Accounts", "CFO"],
    "BUSINESS-DEVELOPMENT":    ["BD Manager", "VP Business Development", "Chief Growth Officer"],
    "CONSULTANT":              ["Senior Consultant", "Principal Consultant", "Associate Partner", "Partner"],
    "DESIGNER":                ["Senior Designer", "Design Lead", "Creative Director", "VP Design"],
    "DIGITAL-MEDIA":           ["Senior Media Specialist", "Media Manager", "Head of Digital", "CMO"],
    "ADVOCATE":                ["Senior Advocate", "Associate Partner", "Partner", "Legal Director"],
    "AVIATION":                ["Senior Pilot", "Chief Pilot", "Flight Operations Manager", "Director of Operations"],
    "CONSTRUCTION":            ["Site Manager", "Project Manager", "Construction Director", "VP Construction"],
    "AUTOMOBILE":              ["Senior Technician", "Service Manager", "Regional Director"],
    "BPO":                     ["Team Lead", "Operations Manager", "Senior Manager", "VP Operations"],
    "AGRICULTURE":             ["Senior Agronomist", "Farm Manager", "Regional Agricultural Director"],
    "FITNESS":                 ["Senior Trainer", "Fitness Manager", "Regional Wellness Manager"],
    "CHEF":                    ["Sous Chef", "Head Chef", "Executive Chef", "F&B Director"],
    "APPAREL":                 ["Senior Designer", "Design Manager", "Design Director", "Brand Director"],
    "ARTS":                    ["Senior Artist", "Art Director", "Creative Director", "VP Creative"],
    "PUBLIC-RELATIONS":        ["Senior PR Specialist", "PR Manager", "Head of PR", "Communications Director"],
}


def recommend_career(role: str) -> list:
    """Returns list of next career steps for the predicted role."""
    if _use_csv and career_data is not None:
        paths = career_data[career_data["current_role"] == role]
        if len(paths) > 0:
            return paths["next_role"].tolist()

    if role in FALLBACK_PATHS:
        return FALLBACK_PATHS[role]

    return [f"Senior {role.title()}", "Team Lead", "Manager", "Director"]
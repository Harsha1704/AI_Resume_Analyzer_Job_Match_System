import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from services.resume_parser     import parse_resume, is_resume
from services.ats_score         import calculate_ats_score, extract_skills
from services.job_matcher       import match_jobs, get_best_jd_for_ats
from services.skill_gap         import detect_skill_gap
from services.role_predictor    import predict_role
from services.suggestion_engine import generate_suggestions
from services.career_path       import recommend_career

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "AI Resume Analyzer & Job Match System Running 🚀"


@app.route("/validate", methods=["POST"])
def validate_resume():
    data = request.get_json()
    if not data:
        return jsonify({"is_valid": False, "error": "No JSON received."}), 400

    resume_text = data.get("resume_text", "")
    valid, reason = is_resume(resume_text)

    if not valid:
        return jsonify({"is_valid": False, "error": reason}), 400

    return jsonify({"is_valid": True}), 200


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    resume_text = data.get("resume_text")
    if not resume_text:
        return jsonify({"error": "resume_text missing"}), 400

    # Step 1: Validate
    valid, reason = is_resume(resume_text)
    if not valid:
        return jsonify({"error": reason}), 422

    # Step 2: Parse & clean resume
    parsed_resume = parse_resume(resume_text)

    # Step 3: Predict role (needed early for JD lookup)
    role = predict_role(parsed_resume)

    # Step 4: Extract resume skills (needed for JD matching + ATS)
    resume_skills = extract_skills(parsed_resume)

    # Step 5: Find best matching JD from dataset
    best_jd = get_best_jd_for_ats(parsed_resume, role, resume_skills)

    # Fallback if no JD found in dataset
    if not best_jd:
        best_jd = (
            "Looking for a skilled professional with experience in "
            + role + ". Strong technical and communication skills required."
        )

    # Step 6: ATS Score against the real dataset JD
    ats_score, matched_skills, missing_from_jd, _ = calculate_ats_score(
        parsed_resume, best_jd
    )

    # Step 7: Top job matches from dataset
    jobs = match_jobs(parsed_resume, role, resume_skills, top_n=5)

    # Step 8: Skill gap (role-aware)
    present_skills, missing_skills = detect_skill_gap(parsed_resume, predicted_role=role)

    # Step 9: Suggestions
    suggestions = generate_suggestions(ats_score, missing_skills, parsed_resume)

    # Step 10: Career path
    career = recommend_career(role)

    return jsonify({
        "ATS Score"          : ats_score,
        "Matched Skills"     : matched_skills,
        "Missing from JD"    : missing_from_jd,
        "Predicted Role"     : role,
        "Job Matches"        : jobs,
        "Present Skills"     : present_skills,
        "Skill Gap"          : missing_skills,
        "Suggestions"        : suggestions,
        "Career Path"        : career,
        "JD Used for Scoring": best_jd[:200] + "..."
    })


if __name__ == "__main__":
    app.run(debug=False)
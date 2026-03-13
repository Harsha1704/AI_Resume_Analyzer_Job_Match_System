import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from services.resume_parser import parse_resume, is_resume
from services.ats_score import calculate_ats_score
from services.job_matcher import match_jobs
from services.skill_gap import detect_skill_gap
from services.role_predictor import predict_role
from services.suggestion_engine import generate_suggestions
from services.career_path import recommend_career

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "AI Resume Analyzer Backend Running Successfully 🚀"


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
    job_description = data.get("job_description")

    if not resume_text:
        return jsonify({"error": "resume_text missing"}), 400

    if not job_description:
        return jsonify({"error": "job_description missing"}), 400

    # Step 1: Validate resume
    valid, reason = is_resume(resume_text)

    if not valid:
        return jsonify({"error": reason}), 422

    # Step 2: Clean resume
    parsed_resume = parse_resume(resume_text)

    # Step 3: ATS Score
    ats_score, matched_skills, missing_skills, resume_skills = calculate_ats_score(
        parsed_resume, job_description
    )

    # Step 4: Predict Role
    role = predict_role(parsed_resume)

    # Step 5: Job Matches
    jobs = match_jobs(parsed_resume)

    # Step 6: Skill Gap
    present_skills, role_missing_skills = detect_skill_gap(
        parsed_resume, predicted_role=role
    )

    # Step 7: Suggestions
    suggestions = generate_suggestions(ats_score, role_missing_skills, parsed_resume)

    # Step 8: Career Path
    career = recommend_career(role)

    return jsonify(
        {
            "ATS Score": ats_score,
            "Matched Skills": matched_skills,
            "Missing Skills": missing_skills,
            "Resume Skills": resume_skills,
            "Predicted Role": role,
            "Job Matches": jobs,
            "Present Skills": present_skills,
            "Skill Gap": role_missing_skills,
            "Suggestions": suggestions,
            "Career Path": career,
        }
    )


if __name__ == "__main__":
    app.run(debug=False)
from flask import Flask, request, jsonify
from flask_cors import CORS

from services.resume_parser import parse_resume
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


@app.route("/analyze", methods=["POST"])
def analyze_resume():

    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    resume_text = data.get("resume_text")

    if not resume_text:
        return jsonify({"error": "resume_text missing"}), 400

    # parse_resume now just cleans the raw text (no PDF extraction needed here)
    parsed_resume = parse_resume(resume_text)

    # Returns (score_float, matched_skills_list)
    ats_score, matched_skills = calculate_ats_score(parsed_resume)

    jobs = match_jobs(parsed_resume)

    # Returns (present_skills_list, missing_skills_list)
    present_skills, missing_skills = detect_skill_gap(parsed_resume)

    role = predict_role(parsed_resume)

    # Fixed: pass ats_score and missing_skills as required by suggestion_engine
    suggestions = generate_suggestions(ats_score, missing_skills)

    career = recommend_career(role)

    return jsonify({
        "ATS Score": ats_score,
        "Matched Skills": matched_skills,
        "Predicted Role": role,
        "Job Matches": jobs,
        "Present Skills": present_skills,
        "Skill Gap": missing_skills,
        "Suggestions": suggestions,
        "Career Path": career
    })


if __name__ == "__main__":
    app.run(debug=True)
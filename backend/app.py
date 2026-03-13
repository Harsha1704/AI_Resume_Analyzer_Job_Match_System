import sys, os, concurrent.futures
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from services.resume_parser     import parse_resume, is_resume
from services.ats_score         import calculate_ats_score, extract_skills
from services.job_matcher       import match_jobs
from services.skill_gap         import detect_skill_gap
from services.role_predictor    import predict_role
from services.suggestion_engine import generate_suggestions
from services.career_path       import recommend_career

app = Flask(__name__)
CORS(app)

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


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

    # Step 2: Parse
    parsed_resume = parse_resume(resume_text)

    # Step 3: Predict role
    role = predict_role(parsed_resume)

    # Step 4: Extract skills
    resume_skills = extract_skills(parsed_resume)

    # Step 5: Launch job matching in background (ONE CSV scan only)
    job_future = _executor.submit(match_jobs, parsed_resume, role, resume_skills, 5)

    # Step 6: Fast steps run on main thread while CSV is being scanned
    present_skills, missing_skills = detect_skill_gap(parsed_resume, predicted_role=role)
    career = recommend_career(role)

    # Step 7: Wait for job results
    try:
        jobs = job_future.result(timeout=240)
    except concurrent.futures.TimeoutError:
        jobs = [{"message": "Job matching timed out. Try again."}]

    # Step 8: Extract best JD directly from top job match — NO second CSV scan
    best_jd = ""
    if jobs and "Job Description Preview" in jobs[0]:
        best_jd = jobs[0].get("Job Description Preview", "")

    if not best_jd:
        best_jd = (
            f"Looking for a skilled {role} professional with strong technical "
            "and communication skills. " + " ".join(resume_skills[:10])
        )

    # Step 9: ATS score
    ats_score, matched_skills, missing_from_jd, _ = calculate_ats_score(
        parsed_resume, best_jd
    )

    # Step 10: Suggestions with real ATS score
    suggestions = generate_suggestions(ats_score, missing_skills, parsed_resume)

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
    app.run(debug=False, threaded=True)
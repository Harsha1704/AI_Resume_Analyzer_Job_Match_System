import sys, os, concurrent.futures
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

# Thread pool — reused across requests (avoids thread creation overhead)
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

    # ── Run job matching in background thread while other steps run ───────────
    job_future = _executor.submit(match_jobs, parsed_resume, role, resume_skills, 5)

    # Step 5: Best JD for ATS (reuses top job match — fast, no extra CSV read)
    # We do this after submitting job_future so it runs concurrently
    best_jd_future = _executor.submit(get_best_jd_for_ats, parsed_resume, role, resume_skills)

    # Step 6: Skill gap, suggestions, career path run on main thread (fast)
    present_skills, missing_skills = detect_skill_gap(parsed_resume, predicted_role=role)
    suggestions = generate_suggestions(0, missing_skills, parsed_resume)  # temp score
    career      = recommend_career(role)

    # Step 7: Collect job results (wait here — but other steps already done)
    try:
        jobs   = job_future.result(timeout=240)
        best_jd = best_jd_future.result(timeout=10)
    except concurrent.futures.TimeoutError:
        jobs    = [{"message": "Job matching timed out. Try again."}]
        best_jd = ""

    if not best_jd:
        best_jd = (
            f"Looking for a skilled {role} professional with strong technical "
            "and communication skills."
        )

    # Step 8: ATS score with best JD
    ats_score, matched_skills, missing_from_jd, _ = calculate_ats_score(
        parsed_resume, best_jd
    )

    # Re-generate suggestions with real ATS score
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
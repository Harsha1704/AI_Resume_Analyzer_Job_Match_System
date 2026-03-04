from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from config import UPLOAD_FOLDER
from services.resume_parser import parse_resume
from services.job_matcher import match_jobs
from services.role_predictor import predict_role
from services.skill_gap import analyze_skill_gap
from services.suggestion_engine import generate_suggestions

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    file = request.files["resume"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    resume_text = parse_resume(file_path)

    jobs = match_jobs(resume_text)
    role = predict_role(resume_text)
    suggestions = generate_suggestions(resume_text)

    return jsonify({
        "predicted_role": role,
        "top_jobs": jobs,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    app.run(debug=True)
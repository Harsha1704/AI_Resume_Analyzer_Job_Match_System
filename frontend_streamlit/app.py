import streamlit as st
import requests
import pdfplumber

API_URL = "http://127.0.0.1:5000/analyze"

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("🤖 AI Resume Analyzer & Job Match System")
st.write("Upload your resume to analyze ATS score, skills, jobs and career path.")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])


def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


if uploaded_file is not None:

    st.success("✅ Resume Uploaded Successfully")

    with st.spinner("Extracting Resume Text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if len(resume_text.strip()) < 20:
        st.error("❌ Could not extract text from PDF. Make sure it's not a scanned image.")
        st.stop()

    st.subheader("📄 Extracted Resume Text (Preview)")
    st.write(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)

    with st.spinner("🔍 Sending Resume to AI Engine..."):
        try:
            response = requests.post(
                API_URL,
                json={"resume_text": resume_text},
                timeout=30
            )
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure Flask server is running on port 5000.")
            st.code("cd backend && python app.py", language="bash")
            st.stop()
        except Exception as e:
            st.error("❌ Backend connection failed")
            st.write(e)
            st.stop()

    if response.status_code != 200:
        st.error(f"❌ Backend returned error {response.status_code}")
        st.write(response.text)
        st.stop()

    result = response.json()
    st.success("✅ Analysis Completed!")

    # ── Row 1: ATS Score + Predicted Role ──────────────────────────────────
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 ATS Score")
        score = result.get("ATS Score", 0)
        st.metric("Score", f"{score} %")
        if score >= 80:
            st.success("Great ATS score! Your resume is well-optimized.")
        elif score >= 60:
            st.warning("Decent score. A few improvements can help.")
        else:
            st.error("Low ATS score. Follow the suggestions below.")

    with col2:
        st.subheader("🎯 Predicted Role")
        st.info(result.get("Predicted Role", "Unknown"))

    # ── Row 2: Job Matches ──────────────────────────────────────────────────
    st.divider()
    st.subheader("💼 Job Matches")

    job_matches = result.get("Job Matches", [])
    if not job_matches:
        st.write("No job matches found.")
    else:
        for job in job_matches:
            # Handles both dict {"job_title": ..., "score": ...} and plain strings
            if isinstance(job, dict):
                title = job.get("job_title", "Unknown")
                score_val = job.get("score", 0)
                st.write(f"• **{title}** — {score_val}% match")
            else:
                st.write(f"• {job}")

    # ── Row 3: Skill Gap ───────────────────────────────────────────────────
    st.divider()
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("✅ Present Skills")
        present = result.get("Present Skills", [])
        if present:
            st.write(", ".join(present))
        else:
            st.write("No recognized skills detected.")

    with col4:
        st.subheader("❗ Missing Skills (Skill Gap)")
        missing = result.get("Skill Gap", [])
        if not missing:
            st.write("No major skill gaps found!")
        else:
            for skill in missing:
                st.write(f"• {skill}")

    # ── Row 4: Suggestions ────────────────────────────────────────────────
    st.divider()
    st.subheader("💡 Resume Suggestions")
    suggestions = result.get("Suggestions", [])
    for tip in suggestions:
        st.write(f"• {tip}")

    # ── Row 5: Career Path ────────────────────────────────────────────────
    st.divider()
    st.subheader("🚀 Career Path")
    career = result.get("Career Path", [])
    for i, step in enumerate(career, 1):
        st.write(f"{i}. {step}")
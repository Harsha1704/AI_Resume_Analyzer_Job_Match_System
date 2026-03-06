import streamlit as st
import requests
import pdfplumber

API_URL = "http://127.0.0.1:5000/analyze"

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("AI Resume Analyzer & Job Match System")

st.write("Upload your resume to analyze ATS score, skills, jobs and career path.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])


def extract_text_from_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    return text


if uploaded_file is not None:

    st.success("Resume Uploaded Successfully")

    with st.spinner("Analyzing Resume..."):

        resume_text = extract_text_from_pdf(uploaded_file)

        if len(resume_text) < 20:
            st.error("Could not extract text from PDF")
            st.stop()

        response = requests.post(
            API_URL,
            json={"resume_text": resume_text}
        )

        if response.status_code != 200:
            st.error("Backend API error")
            st.stop()

        result = response.json()

    st.success("Analysis Completed")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("ATS Score")
        st.metric("Score", f"{result['ATS Score']} %")

    with col2:
        st.subheader("Predicted Role")
        st.write(result["Predicted Role"])

    st.subheader("Job Matches")

    for job in result["Job Matches"]:
        st.write("•", job)

    st.subheader("Skill Gap")

    for skill in result["Skill Gap"]:
        st.write("•", skill)

    st.subheader("Resume Suggestions")

    for tip in result["Suggestions"]:
        st.write("•", tip)

    st.subheader("Career Path")

    for step in result["Career Path"]:
        st.write("•", step)
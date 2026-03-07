import streamlit as st
import requests
import pdfplumber
from PIL import Image
import pytesseract
import io

API_URL      = "http://127.0.0.1:5000/analyze"
VALIDATE_URL = "http://127.0.0.1:5000/validate"

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("🤖 AI Resume Analyzer & Job Match System")
st.caption("Powered by Machine Learning | Trained on 2484 Real Resumes across 24 Industries")
st.write("Upload your resume to get ATS score, skill gap analysis, job matches and career path.")

# ── Session state init ─────────────────────────────────────────────────────
for key, default in {
    "last_file_name":    None,
    "validation_result": None,
    "validation_reason": "",
    "analysis_result":   None,
    "resume_text":       "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Text extraction helpers ────────────────────────────────────────────────
def extract_text_from_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_image(file) -> str:
    """Use OCR (Tesseract) to extract text from a resume image."""
    try:
        image = Image.open(file)
        # Convert to RGB if needed (handles RGBA PNGs etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as e:
        return ""


def extract_text(file, file_type: str) -> str:
    if file_type == "pdf":
        return extract_text_from_pdf(file)
    else:
        return extract_text_from_image(file)


# ── Error UI ───────────────────────────────────────────────────────────────
def show_invalid_resume_error(reason: str):
    st.error("❌ Invalid File — This doesn't appear to be a resume.")
    st.markdown(
        f"""
        <div style="
            background-color: #fff3cd;
            border-left: 5px solid #ff4b4b;
            padding: 16px 20px;
            border-radius: 6px;
            margin-top: 8px;
        ">
            <p style="margin:0; font-size:15px;">⚠️ <strong>Why was my file rejected?</strong></p>
            <p style="margin:6px 0 0 0; color:#555;">{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("#### ✅ What a valid resume should contain:")
    cols = st.columns(3)
    with cols[0]:
        st.info("👤 **Contact Info**\nName, email, phone, LinkedIn")
    with cols[1]:
        st.info("🎓 **Education**\nDegree, university, graduation year")
    with cols[2]:
        st.info("💼 **Experience / Projects**\nJob titles, companies, or projects")
    cols2 = st.columns(3)
    with cols2[0]:
        st.info("🛠️ **Skills**\nTechnical & soft skills")
    with cols2[1]:
        st.info("📁 **Projects / Certifications**\nRelevant work samples")
    with cols2[2]:
        st.info("📝 **Clear text**\nNot a blurry/low-res scan")
    st.warning(
        "💡 **Tip:** Make sure you are uploading your **resume/CV** and not "
        "an invoice, letter, academic calendar, or any other document."
    )


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


# ── File uploader — PDF + Images ──────────────────────────────────────────
st.markdown("#### 📎 Supported formats: PDF, JPG, JPEG, PNG")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# ── Detect file type ───────────────────────────────────────────────────────
if uploaded_file is not None:
    fname_lower = uploaded_file.name.lower()
    if fname_lower.endswith(".pdf"):
        file_type = "pdf"
        file_icon = "📄"
        file_label = "PDF"
    else:
        file_type = "image"
        file_icon = "🖼️"
        file_label = "Image"

    st.caption(f"{file_icon} Uploaded as **{file_label}**: `{uploaded_file.name}`")

    # ── Detect new file → reset state ─────────────────────────
    current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_file_name != current_file_id:
        st.session_state.last_file_name    = current_file_id
        st.session_state.validation_result = None
        st.session_state.validation_reason = ""
        st.session_state.analysis_result   = None
        st.session_state.resume_text       = ""

    # ── Step 1: Extract text ───────────────────────────────────
    if not st.session_state.resume_text:
        spinner_msg = "📖 Extracting text from PDF..." if file_type == "pdf" else "🔍 Running OCR on image..."
        with st.spinner(spinner_msg):
            st.session_state.resume_text = extract_text(uploaded_file, file_type)

    resume_text = st.session_state.resume_text

    if len(resume_text.strip()) < 20:
        if file_type == "image":
            st.error(
                "❌ Could not extract text from the image. "
                "Make sure the image is clear, well-lit, and not blurry. "
                "Try a higher resolution scan or photo."
            )
        else:
            st.error(
                "❌ Could not extract text from PDF. "
                "Make sure it's a text-based PDF, not a scanned image."
            )
        st.stop()

    # ── Step 2: Validate via backend ──────────────────────────
    if st.session_state.validation_result is None:
        with st.spinner("🔍 Validating document..."):
            try:
                val_response = requests.post(
                    VALIDATE_URL,
                    json={"resume_text": resume_text},
                    timeout=30
                )
                val_data = safe_json(val_response) or {}
                st.session_state.validation_result = (val_response.status_code == 200)
                st.session_state.validation_reason = val_data.get("error", "")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure Flask is running.")
                st.code("cd backend && python app.py", language="bash")
                st.stop()
            except Exception as e:
                st.error("❌ Validation request failed.")
                st.write(e)
                st.stop()

    # ── Step 3: Show error if invalid ─────────────────────────
    if not st.session_state.validation_result:
        show_invalid_resume_error(
            st.session_state.validation_reason or
            "The uploaded file does not appear to be a resume. "
            "Please upload a proper resume/CV."
        )
        st.stop()

    # ── Step 4: Valid — show preview ───────────────────────────
    st.success(f"✅ Resume Validated Successfully! ({file_label} uploaded)")

    # Show image preview for image uploads
    if file_type == "image":
        with st.expander(f"🖼️ Preview Uploaded Image"):
            uploaded_file.seek(0)
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

    with st.expander("📄 Preview Extracted Text"):
        st.write(resume_text[:800] + "..." if len(resume_text) > 800 else resume_text)

    # ── Step 5: Full analysis ──────────────────────────────────
    if st.session_state.analysis_result is None:
        with st.spinner("🧠 Analyzing with AI Engine..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"resume_text": resume_text},
                    timeout=120
                )
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Make sure Flask is running.")
                st.code("cd backend && python app.py", language="bash")
                st.stop()
            except Exception as e:
                st.error("❌ Backend connection failed.")
                st.write(e)
                st.stop()

        result = safe_json(response)

        if response.status_code == 422:
            show_invalid_resume_error((result or {}).get("error", "Invalid resume."))
            st.stop()
        elif response.status_code != 200 or result is None:
            st.error(f"❌ Backend error {response.status_code}")
            st.write(response.text)
            st.stop()

        st.session_state.analysis_result = result

    result = st.session_state.analysis_result
    st.success("✅ Analysis Complete!")
    st.divider()

    # ── Row 1: ATS Score + Predicted Role ─────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 ATS Score")
        score = result.get("ATS Score", 0)
        st.metric("Score", f"{score}%")
        if score >= 80:
            st.success("🟢 Excellent! Your resume is well optimized.")
        elif score >= 60:
            st.warning("🟡 Good. A few improvements can boost your score.")
        elif score >= 40:
            st.warning("🟠 Average. Add more relevant skills and keywords.")
        else:
            st.error("🔴 Low score. Follow the suggestions below.")
    with col2:
        st.subheader("🎯 Predicted Job Role")
        role = result.get("Predicted Role", "Unknown")
        st.info(f"**{role}**")
        st.caption("Predicted using Random Forest model trained on 2484 resumes")

    st.divider()

    # ── Row 2: Job Matches ─────────────────────────────────────
    st.subheader("💼 Top Job Matches")
    job_matches = result.get("Job Matches", [])
    if not job_matches:
        st.write("No job matches found.")
    else:
        cols = st.columns(min(len(job_matches), 5))
        for i, job in enumerate(job_matches[:5]):
            with cols[i]:
                title     = job.get("job_title", "Unknown") if isinstance(job, dict) else str(job)
                score_val = job.get("score", 0)             if isinstance(job, dict) else 0
                st.metric(title, f"{score_val}%")

    st.divider()

    # ── Row 3: Skills ──────────────────────────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("✅ Skills Found in Resume")
        present = result.get("Present Skills", [])
        if present:
            for skill in present:
                st.write(f"• {skill}")
        else:
            st.write("No recognized skills detected.")
    with col4:
        st.subheader("❗ Missing Skills (Skill Gap)")
        missing = result.get("Skill Gap", [])
        if not missing:
            st.write("No major skill gaps — great resume!")
        else:
            for skill in missing:
                st.write(f"• {skill}")

    st.divider()

    # ── Row 4: Suggestions ─────────────────────────────────────
    st.subheader("💡 Resume Improvement Suggestions")
    for tip in result.get("Suggestions", []):
        st.write(tip)

    st.divider()

    # ── Row 5: Career Path ─────────────────────────────────────
    st.subheader("🚀 Recommended Career Path")
    career = result.get("Career Path", [])
    if career:
        st.write(f"**{role}** → " + " → ".join(career))
        st.caption("Based on industry career progression data")
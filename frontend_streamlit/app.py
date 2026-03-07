import streamlit as st
import requests
import pdfplumber
from PIL import Image
import pytesseract
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API_URL      = "http://127.0.0.1:5000/analyze"
VALIDATE_URL = "http://127.0.0.1:5000/validate"

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeAI — Smart Career Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global reset ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #0a0a0f;
    color: #e8e8f0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 1400px !important; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0d0d1a 0%, #111128 50%, #0d0d1a 100%);
    border-bottom: 1px solid #1e1e3a;
    padding: 2.5rem 2rem 2rem;
    margin: 0 -2rem 2rem -2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 20%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #6366f1 40%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem 0;
    line-height: 1.1;
}
.hero-sub {
    font-size: 0.95rem;
    color: #6b7280;
    font-weight: 300;
    letter-spacing: 0.02em;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a78bfa;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Upload card ── */
.upload-card {
    background: #111120;
    border: 1.5px dashed #2a2a4a;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: border-color 0.3s;
    margin-bottom: 1.5rem;
}
.upload-card:hover { border-color: #6366f1; }
.upload-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e8f0;
    margin-bottom: 0.3rem;
}
.upload-sub { font-size: 0.82rem; color: #4b5563; }

/* ── Metric cards ── */
.metric-card {
    background: #111120;
    border: 1px solid #1e1e3a;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover { transform: translateY(-2px); border-color: #6366f1; }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #10b981);
    border-radius: 14px 14px 0 0;
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #e8e8f0;
    line-height: 1;
}
.metric-sub { font-size: 0.78rem; color: #4b5563; margin-top: 0.4rem; }

/* ── Section headers ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.8rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #2a2a4a, transparent);
}

/* ── Skill tags ── */
.skill-tag {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.2rem;
}
.skill-present {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    color: #10b981;
}
.skill-missing {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    color: #f87171;
}

/* ── Suggestion cards ── */
.suggestion-card {
    background: #111120;
    border: 1px solid #1e1e3a;
    border-left: 3px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: #c4c4d4;
    line-height: 1.5;
}

/* ── Career path ── */
.career-step {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #111120;
    border: 1px solid #1e1e3a;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    font-weight: 500;
    color: #a78bfa;
    margin: 0.25rem;
}
.career-arrow { color: #2a2a4a; font-size: 1rem; }

/* ── ATS band ── */
.ats-band {
    height: 8px;
    border-radius: 999px;
    background: #1a1a2e;
    overflow: hidden;
    margin: 0.5rem 0;
}
.ats-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
    transition: width 1s ease;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e1e3a, transparent);
    margin: 2rem 0;
}

/* ── Success / error banners ── */
.banner-success {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 10px;
    padding: 0.75rem 1.1rem;
    color: #10b981;
    font-size: 0.88rem;
    font-weight: 500;
    margin-bottom: 1rem;
}
.banner-error {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 10px;
    padding: 0.75rem 1.1rem;
    color: #f87171;
    font-size: 0.88rem;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* ── Streamlit widget overrides ── */
.stFileUploader > div { background: transparent !important; border: none !important; }
.stFileUploader label { color: #6b7280 !important; font-size: 0.82rem !important; }
div[data-testid="stExpander"] {
    background: #111120 !important;
    border: 1px solid #1e1e3a !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────
for key, default in {
    "last_file_name": None, "validation_result": None,
    "validation_reason": "", "analysis_result": None, "resume_text": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helpers ────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text += t + "\n"
    return text.strip()

def extract_text_from_image(file) -> str:
    try:
        img = Image.open(file)
        if img.mode != "RGB": img = img.convert("RGB")
        return pytesseract.image_to_string(img, lang="eng").strip()
    except:
        return ""

def safe_json(r):
    try: return r.json()
    except: return None

def ats_color(score):
    if score >= 80: return "#10b981"
    if score >= 60: return "#f59e0b"
    if score >= 40: return "#f97316"
    return "#ef4444"

def ats_label(score):
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Average"
    return "Needs Work"

def show_invalid_error(reason):
    st.markdown(f"""
    <div class="banner-error">❌ Invalid File — {reason}</div>
    <div style="background:#111120;border:1px solid #1e1e3a;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
        <p style="font-family:Syne,sans-serif;font-size:0.9rem;font-weight:700;color:#a78bfa;margin:0 0 0.8rem 0;">
            ✅ A valid resume should contain:
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;font-size:0.8rem;color:#6b7280;">
            <span>👤 Name & contact info</span>
            <span>🎓 Education details</span>
            <span>💼 Experience / Projects</span>
            <span>🛠️ Skills section</span>
            <span>📅 Dates & timelines</span>
            <span>📝 Clear readable text</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">🧠 AI-Powered Career Intelligence</div>
    <div class="hero-title">ResumeAI Dashboard</div>
    <div class="hero-sub">
        Upload your resume · Get ATS score · Discover skill gaps · Match jobs · Plan your career
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# UPLOAD SECTION
# ════════════════════════════════════════════════════════════════════════════
upload_col, info_col = st.columns([3, 2], gap="large")

with upload_col:
    st.markdown("""
    <div class="upload-title">📎 Upload Your Resume</div>
    <div class="upload-sub">Supports PDF · JPG · JPEG · PNG — up to 200MB</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload", type=["pdf","jpg","jpeg","png"],
        label_visibility="collapsed"
    )

with info_col:
    st.markdown("""
    <div style="background:#111120;border:1px solid #1e1e3a;border-radius:12px;padding:1.2rem 1.5rem;">
        <div style="font-family:Syne,sans-serif;font-size:0.85rem;font-weight:700;color:#a78bfa;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.08em;">
            What you'll get
        </div>
        <div style="font-size:0.82rem;color:#6b7280;line-height:2;">
            📊 ATS Compatibility Score<br>
            🎯 AI-Predicted Job Role<br>
            💼 Top 5 Job Matches<br>
            🛠️ Skill Gap Analysis<br>
            💡 Personalized Suggestions<br>
            🚀 Career Path Roadmap
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PROCESSING
# ════════════════════════════════════════════════════════════════════════════
if uploaded_file is not None:
    fname = uploaded_file.name.lower()
    file_type = "pdf" if fname.endswith(".pdf") else "image"
    file_icon = "📄" if file_type == "pdf" else "🖼️"

    # Detect new file
    fid = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_file_name != fid:
        st.session_state.last_file_name    = fid
        st.session_state.validation_result = None
        st.session_state.validation_reason = ""
        st.session_state.analysis_result   = None
        st.session_state.resume_text       = ""

    # Extract text
    if not st.session_state.resume_text:
        msg = "📖 Extracting text from PDF..." if file_type == "pdf" else "🔍 Running OCR on image..."
        with st.spinner(msg):
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file) if file_type == "pdf" else extract_text_from_image(uploaded_file)

    resume_text = st.session_state.resume_text

    if len(resume_text.strip()) < 20:
        hint = "Make sure image is clear and not blurry." if file_type == "image" else "Use a text-based PDF, not a scanned image."
        st.markdown(f'<div class="banner-error">❌ Could not extract text. {hint}</div>', unsafe_allow_html=True)
        st.stop()

    # Validate
    if st.session_state.validation_result is None:
        with st.spinner("🔍 Validating document..."):
            try:
                vr = requests.post(VALIDATE_URL, json={"resume_text": resume_text}, timeout=30)
                vd = safe_json(vr) or {}
                st.session_state.validation_result = (vr.status_code == 200)
                st.session_state.validation_reason = vd.get("error", "")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running. Start Flask: `cd backend && python app.py`")
                st.stop()

    if not st.session_state.validation_result:
        show_invalid_error(st.session_state.validation_reason or "File does not appear to be a resume.")
        st.stop()

    # Show image preview
    if file_type == "image":
        with st.expander(f"🖼️ Preview Uploaded Image"):
            uploaded_file.seek(0)
            st.image(uploaded_file, use_column_width=True)

    # Run analysis
    if st.session_state.analysis_result is None:
        with st.spinner("🧠 Running AI analysis..."):
            try:
                resp = requests.post(API_URL, json={"resume_text": resume_text}, timeout=120)
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend not running.")
                st.stop()
        result = safe_json(resp)
        if resp.status_code == 422:
            show_invalid_error((result or {}).get("error", "Invalid resume."))
            st.stop()
        elif resp.status_code != 200 or result is None:
            st.error(f"❌ Backend error {resp.status_code}: {resp.text}")
            st.stop()
        st.session_state.analysis_result = result

    result   = st.session_state.analysis_result
    score    = result.get("ATS Score", 0)
    role     = result.get("Predicted Role", "Unknown")
    jobs     = result.get("Job Matches", [])
    present  = result.get("Present Skills", [])
    missing  = result.get("Skill Gap", [])
    tips     = result.get("Suggestions", [])
    career   = result.get("Career Path", [])

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # ROW 1 — KEY METRICS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">📊 Resume Overview</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ATS Score</div>
            <div class="metric-value" style="color:{ats_color(score)}">{score}%</div>
            <div class="ats-band"><div class="ats-fill" style="width:{score}%"></div></div>
            <div class="metric-sub">{ats_label(score)}</div>
        </div>""", unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Predicted Role</div>
            <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;color:#a78bfa;margin:0.3rem 0;">
                {role.replace('-', ' ').title()}
            </div>
            <div class="metric-sub">Based on resume content</div>
        </div>""", unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Skills Found</div>
            <div class="metric-value">{len(present)}</div>
            <div class="metric-sub">Recognized skills in resume</div>
        </div>""", unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Skill Gaps</div>
            <div class="metric-value" style="color:#f87171">{len(missing)}</div>
            <div class="metric-sub">Top missing skills for role</div>
        </div>""", unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # ROW 2 — ATS GAUGE + JOB MATCHES
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    gauge_col, jobs_col = st.columns([1, 2], gap="large")

    with gauge_col:
        st.markdown('<div class="section-header">🎯 ATS Score</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 36, "color": "#e8e8f0", "family": "Syne"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#2a2a4a", "tickfont": {"color": "#4b5563", "size": 10}},
                "bar": {"color": ats_color(score), "thickness": 0.25},
                "bgcolor": "#111120",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  40], "color": "rgba(239,68,68,0.1)"},
                    {"range": [40, 60], "color": "rgba(249,115,22,0.1)"},
                    {"range": [60, 80], "color": "rgba(245,158,11,0.1)"},
                    {"range": [80,100], "color": "rgba(16,185,129,0.1)"},
                ],
                "threshold": {"line": {"color": ats_color(score), "width": 3}, "value": score}
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e8e8f0"}, height=220, margin=dict(t=20,b=10,l=20,r=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f'<div style="text-align:center;font-size:0.8rem;color:#6b7280;">Score: {ats_label(score)}</div>', unsafe_allow_html=True)

    with jobs_col:
        st.markdown('<div class="section-header">💼 Top Job Matches</div>', unsafe_allow_html=True)
        if jobs:
            job_titles = [j.get("job_title","").replace("-"," ").title() if isinstance(j,dict) else str(j) for j in jobs[:5]]
            job_scores = [j.get("score", 0) if isinstance(j,dict) else 0 for j in jobs[:5]]
            colors     = ["#6366f1","#8b5cf6","#a78bfa","#c4b5fd","#ddd6fe"]

            fig_bar = go.Figure(go.Bar(
                x=job_scores, y=job_titles,
                orientation='h',
                marker=dict(color=colors[:len(job_titles)], line=dict(width=0)),
                text=[f"{s}%" for s in job_scores],
                textposition='outside',
                textfont=dict(color="#e8e8f0", size=11),
            ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0,120], showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#c4c4d4", size=12)),
                margin=dict(t=10, b=10, l=10, r=60),
                height=220,
                bargap=0.3,
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.markdown('<div style="color:#4b5563;font-size:0.85rem;padding:1rem;">No job matches found.</div>', unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # ROW 3 — SKILLS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    skills_col, gap_col = st.columns(2, gap="large")

    with skills_col:
        st.markdown('<div class="section-header">✅ Skills Found</div>', unsafe_allow_html=True)
        if present:
            tags = "".join([f'<span class="skill-tag skill-present">{s}</span>' for s in present])
            st.markdown(f'<div style="line-height:2.2">{tags}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#4b5563;font-size:0.85rem;">No recognized skills detected.</div>', unsafe_allow_html=True)

    with gap_col:
        st.markdown('<div class="section-header">❗ Skill Gaps</div>', unsafe_allow_html=True)
        if missing:
            tags = "".join([f'<span class="skill-tag skill-missing">{s}</span>' for s in missing])
            st.markdown(f'<div style="line-height:2.2">{tags}</div>', unsafe_allow_html=True)
            # Mini radar of skill gap severity
            if len(missing) >= 3:
                top5 = missing[:5]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=[85,75,70,65,60][:len(top5)],
                    theta=[s[:15]+"…" if len(s)>15 else s for s in top5],
                    fill='toself',
                    fillcolor='rgba(239,68,68,0.12)',
                    line=dict(color='#f87171', width=2),
                    marker=dict(size=5, color="#f87171"),
                ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=False),
                        angularaxis=dict(tickfont=dict(color="#9ca3af", size=9), linecolor="#1e1e3a", gridcolor="#1a1a2e"),
                    ),
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                    height=200, margin=dict(t=20,b=20,l=40,r=40)
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.markdown('<div style="color:#10b981;font-size:0.85rem;">✨ No major skill gaps — great resume!</div>', unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # ROW 4 — SUGGESTIONS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">💡 Personalized Suggestions</div>', unsafe_allow_html=True)

    s_col1, s_col2 = st.columns(2, gap="large")
    for i, tip in enumerate(tips):
        col = s_col1 if i % 2 == 0 else s_col2
        with col:
            st.markdown(f'<div class="suggestion-card">{tip}</div>', unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # ROW 5 — CAREER PATH
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🚀 Career Path Roadmap</div>', unsafe_allow_html=True)

    if career:
        all_steps = [role.replace("-"," ").title()] + career
        steps_html = ""
        for i, step in enumerate(all_steps):
            is_current = (i == 0)
            color = "#10b981" if is_current else "#a78bfa"
            bg    = "rgba(16,185,129,0.12)" if is_current else "rgba(99,102,241,0.1)"
            border= "rgba(16,185,129,0.3)"  if is_current else "rgba(99,102,241,0.25)"
            label = "YOU ARE HERE" if is_current else f"Step {i}"
            steps_html += f"""
            <div style="display:inline-flex;flex-direction:column;align-items:center;margin:0.3rem;">
                <div style="font-size:0.6rem;color:{color};font-weight:600;letter-spacing:0.1em;margin-bottom:0.25rem;text-transform:uppercase">{label}</div>
                <div style="background:{bg};border:1px solid {border};border-radius:8px;padding:0.5rem 1rem;
                     font-size:0.82rem;font-weight:500;color:{color};white-space:nowrap;">{step}</div>
            </div>
            """
            if i < len(all_steps) - 1:
                steps_html += '<div style="display:inline-flex;align-items:center;margin:0.3rem;color:#2a2a4a;font-size:1.2rem;margin-top:1.3rem;">→</div>'

        st.markdown(f'<div style="display:flex;flex-wrap:wrap;align-items:flex-end;gap:0.2rem;padding:0.5rem 0;">{steps_html}</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem;color:#4b5563;margin-top:0.5rem;">Based on industry career progression data</div>', unsafe_allow_html=True)


    # ════════════════════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="custom-divider"></div>
    <div style="text-align:center;font-size:0.75rem;color:#2a2a4a;padding-bottom:1rem;">
        ResumeAI · Powered by Machine Learning · Trained on 2484 Real Resumes across 24 Industries
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Empty state ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📄</div>
        <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#4b5563;margin-bottom:0.5rem;">
            No resume uploaded yet
        </div>
        <div style="font-size:0.82rem;color:#374151;">
            Upload a PDF or image of your resume above to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
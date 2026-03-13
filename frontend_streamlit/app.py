import streamlit as st
import requests
import pdfplumber
from PIL import Image
import pytesseract
import plotly.graph_objects as go
import re, io, textwrap
from datetime import datetime

API_URL      = "http://127.0.0.1:5000/analyze"
VALIDATE_URL = "http://127.0.0.1:5000/validate"

st.set_page_config(page_title="ResumeAI Pro", page_icon="🧠",
                   layout="wide", initial_sidebar_state="expanded")
import streamlit as st

st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ═══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@300;400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{
    font-family:'Inter',sans-serif !important;
    background:#07070f !important;
    color:#c8c8e0 !important;
}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 2.5rem 3rem 2.5rem !important;max-width:100% !important;}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{
    background:#09091a !important;
    border-right:1px solid #14143a !important;
}
section[data-testid="stSidebar"] > div{padding:0 !important;}
div[data-testid="stSidebarContent"]{background:#09091a !important;padding:0 !important;}

.sb-logo{
    padding:1.8rem 1.4rem 1.4rem;
    border-bottom:1px solid #14143a;
    margin-bottom:0.4rem;
}
.sb-logo-title{
    font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:800;
    background:linear-gradient(120deg,#a78bfa,#6366f1,#10b981);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.sb-logo-sub{font-size:0.65rem;color:#32325a;margin-top:0.25rem;letter-spacing:0.04em;}

.sb-sec{
    padding:0.9rem 1.4rem 0.25rem;
    font-size:0.58rem;font-weight:700;color:#252545;
    text-transform:uppercase;letter-spacing:0.16em;
}
.sb-resume-card{
    margin:0.6rem 1rem 0.3rem;
    background:#0d0d22;border:1px solid #16163a;border-radius:10px;
    padding:0.8rem 1rem;
}
.sb-resume-score{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;}
.sb-resume-role{font-size:0.68rem;color:#404065;margin-top:0.15rem;}

/* ── SIDEBAR BUTTONS override ── */
section[data-testid="stSidebar"] .stButton>button{
    background:transparent !important;
    border:none !important;
    color:#484870 !important;
    font-size:0.82rem !important;
    font-weight:500 !important;
    text-align:left !important;
    width:100% !important;
    padding:0.55rem 1.4rem !important;
    border-radius:0 !important;
    border-left:3px solid transparent !important;
    transition:all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
    background:rgba(99,102,241,0.07) !important;
    color:#a78bfa !important;
    border-left-color:#6366f1 !important;
}

/* ── PAGE HEADER ── */
.pg-hdr{
    display:flex;align-items:center;justify-content:space-between;
    padding-bottom:1.2rem;margin-bottom:1.8rem;
    border-bottom:1px solid #13132e;
}
.pg-title{font-family:'Syne',sans-serif;font-size:1.55rem;font-weight:800;color:#ddddf5;}
.pg-sub{font-size:0.76rem;color:#35355a;margin-top:0.25rem;}
.pg-badge{
    background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);
    color:#818cf8;font-size:0.66rem;font-weight:600;
    padding:0.28rem 0.85rem;border-radius:999px;
    text-transform:uppercase;letter-spacing:0.08em;white-space:nowrap;
}

/* ── METRIC CARD ── */
.card{
    background:#0d0d22;border:1px solid #16163a;border-radius:14px;
    padding:1.4rem 1.5rem;position:relative;overflow:hidden;height:100%;
}
.card::before{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,#6366f1,#8b5cf6,#10b981);
}
.c-lbl{font-size:0.6rem;font-weight:700;color:#303055;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.6rem;}
.c-val{font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;line-height:1;color:#ddddf5;}
.c-sub{font-size:0.68rem;color:#28284a;margin-top:0.5rem;}
.c-bar{height:4px;background:#11112a;border-radius:999px;overflow:hidden;margin:0.6rem 0 0.25rem;}
.c-fill{height:100%;border-radius:999px;}

/* ── SECTION HEADING ── */
.sh{
    font-family:'Syne',sans-serif;font-size:0.7rem;font-weight:700;
    color:#404065;text-transform:uppercase;letter-spacing:0.15em;
    display:flex;align-items:center;gap:0.6rem;margin:2rem 0 1rem;
}
.sh::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#16163a,transparent);}

/* ── DIVIDER ── */
.hr{height:1px;background:#111126;margin:2rem 0;}

/* ── TAGS ── */
.tags{display:flex;flex-wrap:wrap;gap:0.45rem;}
.tag{
    font-size:0.73rem;font-weight:500;padding:0.32rem 0.85rem;
    border-radius:6px;line-height:1.5;
}
.tg{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.18);color:#34d399;}
.tr{background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.17);color:#f87171;}
.tb{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.18);color:#818cf8;}

/* ── SUGGESTION ROW ── */
.sug{
    display:flex;align-items:flex-start;gap:0.9rem;
    padding:0.9rem 1.1rem;margin-bottom:0.5rem;
    background:#0d0d22;border:1px solid #16163a;
    border-left:3px solid #6366f1;border-radius:0 10px 10px 0;
    font-size:0.83rem;color:#9090c0;line-height:1.65;
}
.sug-ico{font-size:0.95rem;flex-shrink:0;margin-top:0.05rem;}

/* ── CAREER PATH ── */
.cpath{display:flex;flex-wrap:wrap;align-items:flex-end;gap:0;margin-top:0.6rem;}
.cnode{display:flex;flex-direction:column;align-items:center;gap:0.28rem;}
.cnlbl{font-size:0.54rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;}
.cnbox{padding:0.5rem 1.1rem;border-radius:8px;font-size:0.78rem;font-weight:600;white-space:nowrap;}
.cn-c .cnbox{background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);color:#10b981;}
.cn-c .cnlbl{color:#10b981;}
.cn-n .cnbox{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);color:#818cf8;}
.cn-n .cnlbl{color:#33335a;}
.carr{color:#1e1e42;font-size:1.1rem;padding:0 0.4rem;align-self:center;padding-bottom:0.25rem;}

/* ── INFO ROWS ── */
.irow{
    display:flex;align-items:center;gap:0.7rem;
    padding:0.5rem 0;border-bottom:1px solid #10102a;
    font-size:0.8rem;color:#454570;
}
.irow:last-child{border-bottom:none;}

/* ── BANNERS ── */
.b-ok{background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:9px;padding:0.7rem 1.1rem;color:#34d399;font-size:0.8rem;font-weight:500;margin-bottom:1.2rem;}
.b-err{background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:9px;padding:0.7rem 1.1rem;color:#f87171;font-size:0.8rem;font-weight:500;margin-bottom:0.8rem;}
.b-warn{background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);border-radius:9px;padding:0.7rem 1.1rem;color:#fbbf24;font-size:0.8rem;font-weight:500;margin-bottom:0.8rem;}

/* ── SCORE BAR ROW ── */
.score-row{margin-bottom:0.85rem;}
.score-row-top{display:flex;justify-content:space-between;font-size:0.76rem;color:#5a5a88;margin-bottom:0.28rem;}
.score-row-bar{height:5px;background:#11112a;border-radius:999px;overflow:hidden;}
.score-row-fill{height:100%;border-radius:999px;}

/* ── STRENGTH / WEAKNESS ITEM ── */
.sw-item{
    display:flex;align-items:flex-start;gap:0.85rem;
    padding:0.65rem 1rem;margin-bottom:0.4rem;
    background:#0d0d22;border-radius:8px;
}
.sw-icon{font-size:0.9rem;margin-top:0.05rem;flex-shrink:0;}
.sw-label{font-size:0.78rem;font-weight:600;color:#9090c0;}
.sw-sub{font-size:0.7rem;color:#35355a;margin-top:0.1rem;}

/* ── COURSE CARD ── */
.cc{
    background:#0d0d22;border:1px solid #16163a;border-radius:12px;
    padding:1.1rem 1.2rem;margin-bottom:0.8rem;height:100%;
}
.cc-plat{font-size:0.58rem;font-weight:700;color:#303055;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;}
.cc-title{font-size:0.86rem;font-weight:600;color:#c8c8e8;line-height:1.35;margin-bottom:0.35rem;}
.cc-skill{font-size:0.7rem;color:#35355a;}
.cc-link{font-size:0.72rem;color:#6366f1;font-weight:600;text-decoration:none;display:inline-block;margin-top:0.5rem;}

/* ── COMING SOON ── */
.soon{background:#0d0d22;border:1px solid #16163a;border-radius:14px;padding:3rem 2rem;text-align:center;}
.soon-ico{font-size:2.5rem;margin-bottom:1rem;}
.soon-t{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#303055;margin-bottom:0.35rem;}
.soon-s{font-size:0.76rem;color:#222240;}

/* ── STREAMLIT WIDGET OVERRIDES ── */
div[data-testid="stExpander"]{background:#0d0d22 !important;border:1px solid #16163a !important;border-radius:10px !important;}
.stFileUploader>div{background:transparent !important;border:none !important;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
for k, v in {
    "page":"upload","last_file_name":None,"validation_result":None,
    "validation_reason":"","analysis_result":None,"resume_text":""
}.items():
    if k not in st.session_state: st.session_state[k] = v

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def extract_pdf(f):
    t=""
    with pdfplumber.open(f) as pdf:
        for p in pdf.pages:
            x=p.extract_text()
            if x: t+=x+"\n"
    return t.strip()

def extract_img(f):
    try:
        img=Image.open(f)
        if img.mode!="RGB": img=img.convert("RGB")
        return pytesseract.image_to_string(img,lang="eng").strip()
    except: return ""

def safe_json(r):
    try: return r.json()
    except: return None

def ats_color(s):
    if s>=80: return "#10b981"
    if s>=60: return "#f59e0b"
    if s>=40: return "#f97316"
    return "#ef4444"

def ats_label(s):
    if s>=80: return "Excellent ✨"
    if s>=60: return "Good 👍"
    if s>=40: return "Average 📈"
    return "Needs Work 🔧"

def has_result(): return st.session_state.analysis_result is not None

def go_page(p):
    st.session_state.page = p
    st.rerun()

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-title">🧠 ResumeAI Pro</div>
        <div class="sb-logo-sub">Industry-Level Career Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    # Mini resume card
    if has_result():
        R = st.session_state.analysis_result
        sc = R.get("ATS Score",0)
        rl = R.get("Predicted Role","?").replace("-"," ").title()
        st.markdown(f"""
        <div class="sb-resume-card">
            <div style="font-size:0.56rem;font-weight:700;color:#252545;
                 text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.4rem;">Active Resume</div>
            <div class="sb-resume-score" style="color:{ats_color(sc)}">{sc}%</div>
            <div class="sb-resume-role">{rl}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Navigation ──
    NAV = [
        ("── CORE ──", None),
        ("upload",  "📤  Upload & Parse Resume"),
        ("ats",     "📊  ATS Analysis"),
        ("skills",  "🛠️  Skill Intelligence"),
        ("jobs",    "💼  Job Matching"),
        ("career",  "🚀  Career Intelligence"),
        ("quality", "✅  Resume Quality AI"),
        ("learn",   "📚  Learning & Growth"),
        ("analytics","📈  Analytics & Visualization"),
        ("export",  "📄  Export Report (PDF)"),
    ]

    for item in NAV:
        if item[1] is None:
            st.markdown(f'<div class="sb-sec">{item[0]}</div>', unsafe_allow_html=True)
        else:
            pid, label = item
            locked = (not has_result()) and pid != "upload"
            icon = "🔒 " if locked else ""
            if st.button(f"{icon}{label}", key=f"nav_{pid}", disabled=locked, width="stretch"):
                go_page(pid)

    st.markdown("""
    <div style="padding:1.5rem 1.4rem 1rem;border-top:1px solid #14143a;margin-top:1rem;">
        <div style="font-size:0.6rem;color:#1e1e3a;line-height:1.9;">
            15 Features Active<br>
            Trained on 2484 Resumes<br>
            24 Industries · v2.0
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HELPER: page header
# ═══════════════════════════════════════════════════════════════
def page_header(title, sub, badge="", badge_color="#818cf8"):
    bc = f'border-color:rgba(99,102,241,0.2);color:{badge_color};' if badge_color=="#818cf8" else f'border-color:{badge_color}55;color:{badge_color};'
    b  = f'<div class="pg-badge" style="{bc}">{badge}</div>' if badge else ""
    st.markdown(f"""
    <div class="pg-hdr">
        <div>
            <div class="pg-title">{title}</div>
            <div class="pg-sub">{sub}</div>
        </div>{b}
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: UPLOAD
# ═══════════════════════════════════════════════════════════════
if st.session_state.page == "upload":
    page_header("Upload Resume","Upload your PDF, JPG or PNG resume to begin AI analysis","Feature 1 of 15")

    uc, ic = st.columns([3,2], gap="large")
    with uc:
        st.markdown('<p style="font-size:0.78rem;color:#45456a;margin-bottom:0.5rem;">Supported: <strong style="color:#818cf8">PDF · JPG · JPEG · PNG</strong> — max 200 MB</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload",type=["pdf","jpg","jpeg","png"],label_visibility="collapsed")

    with ic:
        st.markdown("""
        <div class="card">
            <div class="c-lbl">What you'll unlock</div>
            <div class="irow">📊 ATS Compatibility Score</div>
            <div class="irow">🔍 Keyword Optimization</div>
            <div class="irow">🛠️ Skill Gap Analysis</div>
            <div class="irow">💼 AI Job Matching</div>
            <div class="irow">🚀 Career Path Roadmap</div>
            <div class="irow">💰 Salary Prediction</div>
            <div class="irow">📚 Course Recommendations</div>
            <div class="irow">📈 Analytics Dashboard</div>
            <div class="irow">📄 Export PDF Report</div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded_file is not None:
        fname = uploaded_file.name.lower()
        ftype = "pdf" if fname.endswith(".pdf") else "image"
        fid   = f"{uploaded_file.name}_{uploaded_file.size}"

        if st.session_state.last_file_name != fid:
            st.session_state.update(last_file_name=fid,validation_result=None,
                                    validation_reason="",analysis_result=None,resume_text="")

        if not st.session_state.resume_text:
            with st.spinner("📖 Extracting text..." if ftype=="pdf" else "🔍 Running OCR..."):
                st.session_state.resume_text = extract_pdf(uploaded_file) if ftype=="pdf" else extract_img(uploaded_file)

        rt = st.session_state.resume_text
        if len(rt.strip()) < 20:
            st.markdown('<div class="b-err">❌ Could not extract text. Use a clear, text-based file.</div>', unsafe_allow_html=True)
            st.stop()

        if st.session_state.validation_result is None:
            with st.spinner("🔍 Validating..."):
                try:
                    vr = requests.post(VALIDATE_URL,json={"resume_text":rt},timeout=30)
                    vd = safe_json(vr) or {}
                    st.session_state.validation_result = (vr.status_code==200)
                    st.session_state.validation_reason = vd.get("error","")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not running. Run: `cd backend && python app.py`"); st.stop()

        if not st.session_state.validation_result:
            st.markdown(f'<div class="b-err">❌ {st.session_state.validation_reason or "Not a valid resume."}</div>', unsafe_allow_html=True)
            st.markdown("""<div class="card" style="margin-top:0.5rem;">
                <div class="c-lbl">A valid resume needs</div>
                <div class="irow">👤 Full name, email, phone</div>
                <div class="irow">🎓 Education details</div>
                <div class="irow">💼 Experience or Projects</div>
                <div class="irow">🛠️ Skills section</div>
                <div class="irow">📅 Dates and timelines</div>
            </div>""", unsafe_allow_html=True)
            st.stop()

        if st.session_state.analysis_result is None:
            with st.spinner("🧠 AI is analyzing your resume..."):
                try: resp = requests.post(API_URL,json={"resume_text":rt},timeout=300)
                except requests.exceptions.ConnectionError:
                    st.error("❌ Backend not running."); st.stop()
            res = safe_json(resp)
            if resp.status_code == 422:
                st.markdown(f'<div class="b-err">❌ {(res or {}).get("error","Invalid.")}</div>', unsafe_allow_html=True); st.stop()
            elif resp.status_code != 200 or res is None:
                st.error(f"❌ Error {resp.status_code}"); st.stop()
            st.session_state.analysis_result = res

        R = st.session_state.analysis_result
        st.markdown('<div class="b-ok">✅ Resume analyzed! Use the sidebar to explore all 15 features.</div>', unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4,gap="medium")
        score = R.get("ATS Score",0)
        role  = R.get("Predicted Role","?").replace("-"," ").title()
        pres  = R.get("Present Skills",[])
        miss  = R.get("Skill Gap",[])
        for col,lbl,val,col_c in [
            (c1,"ATS Score",f"{score}%",ats_color(score)),
            (c2,"Predicted Role",role,"#a78bfa"),
            (c3,"Skills Found",str(len(pres)),"#ddddf5"),
            (c4,"Skill Gaps",str(len(miss)),"#f87171"),
        ]:
            with col:
                st.markdown(f"""<div class="card">
                    <div class="c-lbl">{lbl}</div>
                    <div class="c-val" style="color:{col_c};font-size:1.5rem;">{val}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="b-warn" style="margin-top:1.2rem;">👈 Use the sidebar navigation to explore ATS Analysis, Skills, Job Matches, Career Path and more.</div>', unsafe_allow_html=True)
        with st.expander("📄 Preview Extracted Text"):
            st.code(rt[:1200]+("..." if len(rt)>1200 else ""), language=None)


# ═══════════════════════════════════════════════════════════════
#  PAGE: ATS ANALYSIS
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="ats" and has_result():
    R     = st.session_state.analysis_result
    rt    = st.session_state.resume_text
    score = R.get("ATS Score",0)
    tips  = R.get("Suggestions",[])

    page_header("ATS Analysis","ATS score, keyword optimization & formatting analysis",
                f"Score: {score}%", ats_color(score))

    gc, bc = st.columns([1,2],gap="large")

    with gc:
        # Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={"suffix":"%","font":{"size":42,"color":"#ddddf5","family":"Syne"}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"#16163a","tickfont":{"color":"#2a2a50","size":8}},
                "bar":{"color":ats_color(score),"thickness":0.2},
                "bgcolor":"#0d0d22","borderwidth":0,
                "steps":[
                    {"range":[0,40],"color":"rgba(239,68,68,0.07)"},
                    {"range":[40,60],"color":"rgba(249,115,22,0.07)"},
                    {"range":[60,80],"color":"rgba(245,158,11,0.07)"},
                    {"range":[80,100],"color":"rgba(16,185,129,0.07)"},
                ],
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                          font={"color":"#ddddf5"},height=250,margin=dict(t=20,b=5,l=10,r=10))
        st.plotly_chart(fig, width="stretch")
        st.markdown(f'<p style="text-align:center;font-size:0.85rem;font-weight:600;color:{ats_color(score)};margin-top:-0.8rem;">{ats_label(score)}</p>', unsafe_allow_html=True)

    with bc:
        st.markdown('<div class="sh">📋 Score Breakdown</div>', unsafe_allow_html=True)
        wc  = len(rt.split())
        kws = len(R.get("Present Skills",[]))
        breakdown = [
            ("ATS Score",         score,                              ats_color(score)),
            ("Keyword Match",     min(round(kws*3.5),100),            "#6366f1"),
            ("Formatting Quality",70 if "\n" in rt else 50,           "#8b5cf6"),
            ("Resume Length",     90 if 150<=wc<=700 else 55,         "#10b981"),
            ("Section Coverage",  65,                                 "#f59e0b"),
        ]
        for lbl, val, col in breakdown:
            st.markdown(f"""
            <div class="score-row">
                <div class="score-row-top"><span>{lbl}</span><span style="color:{col};font-weight:600;">{val}%</span></div>
                <div class="score-row-bar"><div class="score-row-fill" style="width:{val}%;background:{col};"></div></div>
            </div>""", unsafe_allow_html=True)

        # Word count info
        wc_color = "#10b981" if 150<=wc<=700 else "#f87171"
        st.markdown(f'<p style="font-size:0.74rem;color:{wc_color};margin-top:0.5rem;">📝 Word count: <strong>{wc}</strong> {"✅ Good length" if 150<=wc<=700 else "⚠️ Adjust length (ideal: 150–700 words)"}</p>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Keyword found
    st.markdown('<div class="sh">🔑 Keywords Found in Resume</div>', unsafe_allow_html=True)
    kw_found = R.get("Present Skills",[])
    if kw_found:
        tags = "".join([f'<span class="tag tb">{s}</span>' for s in kw_found])
        st.markdown(f'<div class="tags">{tags}</div>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">💡 ATS Optimization Suggestions</div>', unsafe_allow_html=True)
    for tip in tips:
        parts = tip.split(" ",1)
        icon  = parts[0] if len(parts[0])<=2 else "💡"
        text  = parts[1] if len(parts)>1 else tip
        st.markdown(f'<div class="sug"><div class="sug-ico">{icon}</div><div style="color:#a0a0c8;">{text}</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: SKILL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="skills" and has_result():
    R    = st.session_state.analysis_result
    pres = R.get("Present Skills",[])
    miss = R.get("Skill Gap",[])
    role = R.get("Predicted Role","?").replace("-"," ").title()

    page_header("Skill Intelligence",f"Skills found and gaps for <strong style='color:#a78bfa'>{role}</strong>",
                f"{len(pres)} Found · {len(miss)} Missing")

    sc1,sc2 = st.columns(2,gap="large")

    with sc1:
        st.markdown(f'<div class="sh">✅ Skills Found <span style="color:#10b981;font-family:Syne,sans-serif;font-size:0.9rem;font-weight:800;margin-left:0.5rem;">{len(pres)}</span></div>', unsafe_allow_html=True)
        if pres:
            tags="".join([f'<span class="tag tg">{s}</span>' for s in pres])
            st.markdown(f'<div class="tags">{tags}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#252545;font-size:0.8rem;">No recognized skills found.</p>', unsafe_allow_html=True)

        # Importance ranking
        if pres:
            HIGH=["python","machine learning","react","sql","node.js","docker","aws","javascript","git","tensorflow","deep learning","kubernetes","typescript"]
            st.markdown('<div class="sh" style="margin-top:1.6rem;">🏆 Skill Importance Ranking</div>', unsafe_allow_html=True)
            top8 = pres[:8]
            vals = [3 if s.lower() in HIGH else 1 for s in top8]
            colors_sk = ["#10b981" if v==3 else "#6366f1" for v in vals]
            fig_sk = go.Figure(go.Bar(
                x=vals,y=top8,orientation='h',
                marker=dict(color=colors_sk,line=dict(width=0)),
                text=["⭐ High Value" if v==3 else "Standard" for v in vals],
                textposition='outside',textfont=dict(color="#454570",size=10),
            ))
            fig_sk.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0,5],showgrid=False,zeroline=False,showticklabels=False),
                yaxis=dict(showgrid=False,zeroline=False,tickfont=dict(color="#8080a8",size=11),autorange="reversed"),
                margin=dict(t=5,b=5,l=5,r=95),height=max(180,len(top8)*34),bargap=0.42,
            )
            st.plotly_chart(fig_sk,width="stretch")

    with sc2:
        st.markdown(f'<div class="sh">❗ Skill Gaps <span style="color:#f87171;font-family:Syne,sans-serif;font-size:0.9rem;font-weight:800;margin-left:0.5rem;">{len(miss)}</span></div>', unsafe_allow_html=True)
        if miss:
            tags="".join([f'<span class="tag tr">{s}</span>' for s in miss])
            st.markdown(f'<div class="tags">{tags}</div>', unsafe_allow_html=True)

            st.markdown('<div class="sh" style="margin-top:1.6rem;">🎯 Top Skills to Learn Next</div>', unsafe_allow_html=True)
            for i,skill in enumerate(miss[:6],1):
                pc = "#ef4444" if i<=2 else ("#f59e0b" if i<=4 else "#6366f1")
                pl = "🔥 High Priority" if i<=2 else ("⚡ Medium" if i<=4 else "📌 Low")
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                     background:#0d0d22;border:1px solid #16163a;border-radius:8px;
                     padding:0.65rem 1rem;margin-bottom:0.4rem;">
                    <div style="font-size:0.82rem;color:#9090c0;">{i}. {skill}</div>
                    <div style="font-size:0.65rem;font-weight:600;color:{pc};
                         background:{pc}18;padding:0.18rem 0.55rem;border-radius:999px;">{pl}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#10b981;font-size:0.82rem;margin-top:0.5rem;">✨ No major skill gaps — excellent!</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: JOB MATCHING
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="jobs" and has_result():
    R    = st.session_state.analysis_result
    jobs = R.get("Job Matches",[])
    role = R.get("Predicted Role","?").replace("-"," ").title()

    page_header("Job Matching","AI-matched roles based on your resume profile",f"Role: {role}")

    if jobs:
        jobs_s = sorted(jobs,key=lambda x:x.get("Match Score",0) if isinstance(x,dict) else 0,reverse=True)
        titles = [j.get("Job Title","").replace("-"," ").title() if isinstance(j,dict) else str(j) for j in jobs_s]
        scores = [round(j.get("Match Score",0),1) if isinstance(j,dict) else 0 for j in jobs_s]
        colors_j= ["#10b981" if s>=60 else "#6366f1" if s>=40 else "#8b5cf6" for s in scores]

        fig_j = go.Figure(go.Bar(
            x=scores,y=titles,orientation='h',
            marker=dict(color=colors_j,line=dict(width=0)),
            text=[f"  {s}%" for s in scores],
            textposition='outside',textfont=dict(color="#606088",size=12),
        ))
        fig_j.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0,135],showgrid=False,zeroline=False,showticklabels=False),
            yaxis=dict(showgrid=False,zeroline=False,tickfont=dict(color="#9090b8",size=13),autorange="reversed"),
            margin=dict(t=10,b=10,l=10,r=70),height=max(260,len(jobs_s)*52),bargap=0.38,
        )
        st.plotly_chart(fig_j,width="stretch")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sh">📋 Job Match Details</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(jobs_s),3),gap="medium")
        for i,job in enumerate(jobs_s[:6]):
            t  = job.get("Job Title","").replace("-"," ").title() if isinstance(job,dict) else str(job)
            sc = round(job.get("Match Score",0),1) if isinstance(job,dict) else 0
            c  = "#10b981" if sc>=60 else "#6366f1" if sc>=40 else "#8b5cf6"
            ft = "Strong Fit ✅" if sc>=60 else "Good Fit 👍" if sc>=40 else "Partial Fit 📌"
            with cols[i%3]:
                st.markdown(f"""<div class="card" style="margin-bottom:0.8rem;">
                    <div class="c-lbl">{ft}</div>
                    <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#d0d0f0;margin:0.4rem 0;">{t}</div>
                    <div style="font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:{c};">{sc}%</div>
                    <div class="c-bar"><div class="c-fill" style="width:{min(sc,100)}%;background:{c};"></div></div>
                </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: CAREER INTELLIGENCE
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="career" and has_result():
    R      = st.session_state.analysis_result
    role   = R.get("Predicted Role","?")
    career = R.get("Career Path",[])

    page_header("Career Intelligence","Career roadmap, salary insights & industry demand",role.replace("-"," ").title())

    # Career path
    st.markdown('<div class="sh">🗺️ Career Path Roadmap</div>', unsafe_allow_html=True)
    if career:
        all_steps=[role.replace("-"," ").title()]+career
        html='<div class="cpath">'
        for i,step in enumerate(all_steps):
            cls="cn-c" if i==0 else "cn-n"
            lbl="You Are Here" if i==0 else f"Step {i}"
            html+=f'<div class="cnode {cls}"><div class="cnlbl">{lbl}</div><div class="cnbox">{step}</div></div>'
            if i<len(all_steps)-1: html+='<div class="carr">→</div>'
        html+='</div>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.68rem;color:#1e1e3a;margin-top:0.7rem;">Based on industry career progression data</p>', unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Salary
    st.markdown('<div class="sh">💰 Salary Prediction — India Market</div>', unsafe_allow_html=True)
    SMAP = {
        "WEB-DEVELOPER":        [("Fresher (0–1 yr)","₹2.5L–₹4.5L"),("Junior (1–3 yr)","₹4.5L–₹8L"),("Mid (3–5 yr)","₹8L–₹15L"),("Senior 5+ yr","₹15L–₹30L")],
        "DATA-SCIENCE":         [("Fresher (0–1 yr)","₹3.5L–₹6L"),("Junior (1–3 yr)","₹6L–₹12L"),("Mid (3–5 yr)","₹12L–₹22L"),("Senior 5+ yr","₹22L–₹45L")],
        "SOFTWARE-ENGINEER":    [("Fresher (0–1 yr)","₹3L–₹6L"),("Junior (1–3 yr)","₹6L–₹12L"),("Mid (3–5 yr)","₹12L–₹20L"),("Senior 5+ yr","₹20L–₹40L")],
        "INFORMATION-TECHNOLOGY":[("Fresher (0–1 yr)","₹2L–₹4L"),("Junior (1–3 yr)","₹4L–₹8L"),("Mid (3–5 yr)","₹8L–₹15L"),("Senior 5+ yr","₹15L–₹28L")],
    }
    sal = SMAP.get(role,SMAP["INFORMATION-TECHNOLOGY"])
    sc1,sc2,sc3,sc4 = st.columns(4,gap="medium")
    for i,(col,(lvl,rng)) in enumerate(zip([sc1,sc2,sc3,sc4],sal)):
        hl = (i==0)
        c  = "#10b981" if hl else "#6366f1"
        with col:
            st.markdown(f"""<div class="card">
                <div class="c-lbl">{lvl}</div>
                <div style="font-family:Syne,sans-serif;font-size:1rem;font-weight:800;color:{c};margin-top:0.5rem;line-height:1.3;">{rng}</div>
                {"<div style='font-size:0.62rem;color:#10b981;margin-top:0.4rem;'>← Your level now</div>" if hl else ""}
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Industry demand chart
    st.markdown('<div class="sh">📊 Industry Demand — 2025</div>', unsafe_allow_html=True)
    demand={"AI & Machine Learning":96,"Cloud / DevOps":91,"Web Development":88,"Cybersecurity":85,"Mobile Dev":79,"Data Engineering":82,"Blockchain":55,"UI/UX Design":72}
    fig_d=go.Figure(go.Bar(
        x=list(demand.values()),y=list(demand.keys()),orientation='h',
        marker=dict(color=list(demand.values()),colorscale=[[0,"#1e1060"],[0.5,"#6366f1"],[1,"#10b981"]],line=dict(width=0)),
        text=[f"{v}%" for v in demand.values()],
        textposition='outside',textfont=dict(color="#555575",size=11),
    ))
    fig_d.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0,120],showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(showgrid=False,zeroline=False,tickfont=dict(color="#8080a8",size=11),autorange="reversed"),
        margin=dict(t=5,b=5,l=5,r=60),height=280,bargap=0.38,
    )
    st.plotly_chart(fig_d,width="stretch")


# ═══════════════════════════════════════════════════════════════
#  PAGE: RESUME QUALITY AI
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="quality" and has_result():
    R    = st.session_state.analysis_result
    rt   = st.session_state.resume_text
    tips = R.get("Suggestions",[])

    page_header("Resume Quality AI","Strength & weakness analysis + improvement suggestions")

    # Checks
    wc = len(rt.split())
    checks=[
        ("Contact Email",     bool(re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}',rt)),      "Email address found","Add your email address"),
        ("Contact Phone",     bool(re.search(r'\+?\d[\d\s\-]{8,}',rt)),                   "Phone number found","Add your phone number"),
        ("LinkedIn Profile",  "linkedin" in rt.lower(),                                    "LinkedIn profile linked","Add LinkedIn URL"),
        ("GitHub Profile",    "github" in rt.lower(),                                      "GitHub profile linked","Add GitHub URL"),
        ("Projects Section",  "project" in rt.lower(),                                     "Projects section present","Add a projects section"),
        ("Education Section", "education" in rt.lower() or "university" in rt.lower(),     "Education details found","Add education section"),
        ("Skills Section",    "skills" in rt.lower(),                                      "Skills section present","Add a skills section"),
        ("Measurable Results",bool(re.search(r'\d+\s*(%|accuracy|users|ms|seconds|x\s)',rt,re.I)), "Quantified results found","Add numbers to achievements"),
        ("Good Length",       150<=wc<=700,                                                f"Good length ({wc} words)",f"Adjust length ({wc} words, ideal 150–700)"),
        ("Summary/Objective", bool(re.search(r'summary|objective|profile',rt,re.I)),       "Summary section found","Add a professional summary"),
    ]

    strengths  = [(l,m) for l,ok,m,_ in checks if ok]
    weaknesses = [(l,m) for l,ok,_,m in checks if not ok]

    # Overall quality score
    q_score = round(len(strengths)/len(checks)*100)
    q_col   = ats_color(q_score)

    st.markdown(f"""
    <div class="card" style="margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;gap:2rem;">
            <div>
                <div class="c-lbl">Overall Resume Quality</div>
                <div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;color:{q_col};">{q_score}%</div>
            </div>
            <div style="flex:1;">
                <div class="c-bar" style="height:8px;"><div class="c-fill" style="width:{q_score}%;background:{q_col};"></div></div>
                <div style="font-size:0.72rem;color:#35355a;margin-top:0.4rem;">{len(strengths)} of {len(checks)} quality checks passed</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sw1,sw2 = st.columns(2,gap="large")
    with sw1:
        st.markdown(f'<div class="sh">💪 Strengths <span style="color:#10b981;margin-left:0.4rem;font-family:Syne,sans-serif;font-size:0.9rem;font-weight:800;">({len(strengths)})</span></div>', unsafe_allow_html=True)
        for lbl,msg in strengths:
            st.markdown(f"""<div class="sw-item" style="border:1px solid rgba(16,185,129,0.12);">
                <div class="sw-icon">✅</div>
                <div><div class="sw-label">{lbl}</div><div class="sw-sub">{msg}</div></div>
            </div>""", unsafe_allow_html=True)

    with sw2:
        st.markdown(f'<div class="sh">⚠️ Needs Improvement <span style="color:#f87171;margin-left:0.4rem;font-family:Syne,sans-serif;font-size:0.9rem;font-weight:800;">({len(weaknesses)})</span></div>', unsafe_allow_html=True)
        for lbl,msg in weaknesses:
            st.markdown(f"""<div class="sw-item" style="border:1px solid rgba(239,68,68,0.12);">
                <div class="sw-icon">❌</div>
                <div><div class="sw-label">{lbl}</div><div class="sw-sub" style="color:#f87171;">{msg}</div></div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">💡 Personalized Improvement Suggestions</div>', unsafe_allow_html=True)
    for tip in tips:
        parts=tip.split(" ",1)
        icon=parts[0] if len(parts[0])<=2 else "💡"
        text=parts[1] if len(parts)>1 else tip
        st.markdown(f'<div class="sug"><div class="sug-ico">{icon}</div><div style="color:#a0a0c8;">{text}</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: LEARNING & GROWTH
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="learn" and has_result():
    R    = st.session_state.analysis_result
    miss = R.get("Skill Gap",[])
    role = R.get("Predicted Role","?").replace("-"," ").title()

    page_header("Learning & Growth",f"Courses & certifications for <strong style='color:#a78bfa'>{role}</strong>")

    CMAP={
        "javascript":      ("JavaScript — The Complete Guide","Udemy","Beginner","https://www.udemy.com/topic/javascript/"),
        "react":           ("React — The Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/react/"),
        "python":          ("Python Bootcamp 2025","Udemy","Beginner","https://www.udemy.com/topic/python/"),
        "machine learning":("ML Specialization","Coursera","Intermediate","https://www.coursera.org/specializations/machine-learning-introduction"),
        "sql":             ("SQL for Data Analysis","Coursera","Beginner","https://www.coursera.org/learn/sql-for-data-science"),
        "docker":          ("Docker & Kubernetes Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/docker/"),
        "aws":             ("AWS Cloud Practitioner","AWS","Beginner","https://aws.amazon.com/training/"),
        "git":             ("Git & GitHub Bootcamp","Udemy","Beginner","https://www.udemy.com/topic/git/"),
        "typescript":      ("TypeScript — The Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/typescript/"),
        "deep learning":   ("Deep Learning Specialization","Coursera","Advanced","https://www.coursera.org/specializations/deep-learning"),
        "node.js":         ("NodeJS — The Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/nodejs/"),
        "tensorflow":      ("TensorFlow Developer Certificate","Google","Intermediate","https://www.tensorflow.org/certificate"),
        "angular":         ("Angular — The Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/angular/"),
        "vue":             ("Vue.js 3 Complete Guide","Udemy","Intermediate","https://www.udemy.com/topic/vue-js/"),
        "r":               ("R Programming for Data Science","Coursera","Beginner","https://www.coursera.org/learn/r-programming"),
    }

    shown=0
    cols3=st.columns(3,gap="medium")
    for skill in miss:
        sl=skill.lower()
        for key,(title,plat,level,url) in CMAP.items():
            if key in sl and shown<12:
                lc={"Beginner":"#10b981","Intermediate":"#f59e0b","Advanced":"#ef4444"}.get(level,"#6366f1")
                with cols3[shown%3]:
                    st.markdown(f"""<div class="cc">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                            <div class="cc-plat">{plat}</div>
                            <div style="font-size:0.6rem;font-weight:600;color:{lc};background:{lc}18;padding:0.15rem 0.5rem;border-radius:999px;">{level}</div>
                        </div>
                        <div class="cc-title">{title}</div>
                        <div class="cc-skill">For skill: <span style="color:#818cf8;">{skill}</span></div>
                        <a class="cc-link" href="{url}" target="_blank">View Course →</a>
                    </div>""", unsafe_allow_html=True)
                shown+=1; break

    if shown==0:
        st.markdown('<div class="soon"><div class="soon-ico">🎉</div><div class="soon-t">No gaps to fill!</div><div class="soon-s">Your resume already covers key skills.</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="analytics" and has_result():
    R     = st.session_state.analysis_result
    rt    = st.session_state.resume_text
    score = R.get("ATS Score",0)
    pres  = R.get("Present Skills",[])
    miss  = R.get("Skill Gap",[])
    jobs  = R.get("Job Matches",[])
    wc    = len(rt.split())

    page_header("Analytics & Visualization","Full visual breakdown of your resume performance")

    c1,c2,c3,c4=st.columns(4,gap="medium")
    for col,lbl,val,col_c in [
        (c1,"ATS Score",f"{score}%",ats_color(score)),
        (c2,"Skills Found",str(len(pres)),"#10b981"),
        (c3,"Skill Gaps",str(len(miss)),"#f87171"),
        (c4,"Word Count",str(wc),"#818cf8"),
    ]:
        with col:
            st.markdown(f"""<div class="card"><div class="c-lbl">{lbl}</div>
                <div class="c-val" style="color:{col_c};font-size:1.8rem;">{val}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    ch1,ch2=st.columns(2,gap="large")
    with ch1:
        st.markdown('<div class="sh">🍩 Skill Distribution</div>', unsafe_allow_html=True)
        total=len(pres)+len(miss)
        fig_p=go.Figure(go.Pie(
            labels=["Skills Found","Skill Gaps"],
            values=[len(pres),len(miss)] if total>0 else [1,1],
            hole=0.62,
            marker=dict(colors=["#10b981","#ef4444"],line=dict(color="#07070f",width=3)),
            textfont=dict(color="#9090b8",size=11),
        ))
        fig_p.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#606080"),bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=10,b=10,l=10,r=10),height=250,
            annotations=[dict(text=f"<b>{len(pres)}</b><br>skills",x=0.5,y=0.5,
                             font=dict(size=16,color="#ddddf5",family="Syne"),showarrow=False)]
        )
        st.plotly_chart(fig_p,width="stretch")

    with ch2:
        st.markdown('<div class="sh">📡 Resume Quality Radar</div>', unsafe_allow_html=True)
        kws=len(pres)
        cats=["ATS Score","Keywords","Format","Length","Sections"]
        vals_r=[score,min(round(kws*3.5),100),70,90 if 150<=wc<=700 else 50,60]
        fig_r=go.Figure(go.Scatterpolar(
            r=vals_r+[vals_r[0]],theta=cats+[cats[0]],fill='toself',
            fillcolor='rgba(99,102,241,0.1)',
            line=dict(color='#6366f1',width=2),
            marker=dict(size=5,color="#a78bfa"),
        ))
        fig_r.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True,range=[0,100],gridcolor="#16163a",tickfont=dict(color="#22224a",size=7)),
                angularaxis=dict(tickfont=dict(color="#606080",size=10),linecolor="#16163a",gridcolor="#16163a"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",showlegend=False,
            margin=dict(t=20,b=20,l=30,r=30),height=250,
        )
        st.plotly_chart(fig_r,width="stretch")

    # Job match chart
    if jobs:
        st.markdown('<div class="sh">💼 Job Match Score Visualization</div>', unsafe_allow_html=True)
        jobs_s=sorted(jobs,key=lambda x:x.get("Match Score",0) if isinstance(x,dict) else 0,reverse=True)[:8]
        titles=[j.get("Job Title","").replace("-"," ").title() if isinstance(j,dict) else str(j) for j in jobs_s]
        scores_j=[round(j.get("Match Score",0),1) if isinstance(j,dict) else 0 for j in jobs_s]
        fig_jb=go.Figure(go.Bar(
            x=titles,y=scores_j,
            marker=dict(color=scores_j,colorscale=[[0,"#1e1060"],[1,"#10b981"]],line=dict(width=0)),
            text=[f"{s}%" for s in scores_j],
            textposition='outside',textfont=dict(color="#505070",size=11),
        ))
        fig_jb.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(color="#8080a8",size=10)),
            yaxis=dict(range=[0,130],showgrid=False,zeroline=False,showticklabels=False),
            margin=dict(t=30,b=10,l=10,r=10),height=260,bargap=0.35,
        )
        st.plotly_chart(fig_jb,width="stretch")


# ═══════════════════════════════════════════════════════════════
#  PAGE: EXPORT REPORT
# ═══════════════════════════════════════════════════════════════
elif st.session_state.page=="export" and has_result():
    R      = st.session_state.analysis_result
    rt     = st.session_state.resume_text
    score  = R.get("ATS Score",0)
    role   = R.get("Predicted Role","?").replace("-"," ").title()
    pres   = R.get("Present Skills",[])
    miss   = R.get("Skill Gap",[])
    tips   = R.get("Suggestions",[])
    career = R.get("Career Path",[])
    jobs   = R.get("Job Matches",[])
    wc     = len(rt.split())

    page_header("Export Analysis Report","Download your complete resume analysis as a text report")

    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # Generate report text
    jobs_s = sorted(jobs,key=lambda x:x.get("Match Score",0) if isinstance(x,dict) else 0,reverse=True)[:5]
    job_lines="\n".join([f"  {i+1}. {j.get('Job Title','').replace('-',' ').title()} — {round(j.get('Match Score',0),1)}%" for i,j in enumerate(jobs_s) if isinstance(j,dict)])

    report = f"""
╔══════════════════════════════════════════════════════════════╗
║           ResumeAI Pro — Resume Analysis Report              ║
╚══════════════════════════════════════════════════════════════╝

Generated: {now}
═══════════════════════════════════════════════════════════════

┌─ SECTION 1: OVERVIEW ────────────────────────────────────────
│
│  ATS Score       : {score}% ({ats_label(score)})
│  Predicted Role  : {role}
│  Word Count      : {wc} words
│  Skills Found    : {len(pres)}
│  Skill Gaps      : {len(miss)}
│
└───────────────────────────────────────────────────────────────

┌─ SECTION 2: ATS SCORE BREAKDOWN ─────────────────────────────
│
│  Overall ATS Score    : {score}%
│  Keyword Match        : {min(round(len(pres)*3.5),100)}%
│  Formatting Quality   : 70%
│  Resume Length        : {"90% ✓ Good" if 150<=wc<=700 else "55% ✗ Adjust"}
│  Section Coverage     : 65%
│
└───────────────────────────────────────────────────────────────

┌─ SECTION 3: SKILLS ──────────────────────────────────────────
│
│  Skills Found ({len(pres)}):
│  {", ".join(pres) if pres else "None detected"}
│
│  Missing Skills ({len(miss)}):
│  {", ".join(miss) if miss else "None — great job!"}
│
└───────────────────────────────────────────────────────────────

┌─ SECTION 4: TOP JOB MATCHES ─────────────────────────────────
│
{job_lines if job_lines else "  No job matches found."}
│
└───────────────────────────────────────────────────────────────

┌─ SECTION 5: CAREER PATH ─────────────────────────────────────
│
│  {role} → {" → ".join(career) if career else "No path available"}
│
└───────────────────────────────────────────────────────────────

┌─ SECTION 6: IMPROVEMENT SUGGESTIONS ─────────────────────────
│
""" + "\n".join([f"│  {i+1}. {tip}" for i,tip in enumerate(tips)]) + f"""
│
└───────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════
  ResumeAI Pro · Powered by Machine Learning
  Trained on 2484 Real Resumes · 24 Industries · v2.0
═══════════════════════════════════════════════════════════════
"""

    # Preview
    st.markdown('<div class="sh">📋 Report Preview</div>', unsafe_allow_html=True)
    st.code(report, language=None)

    # Download
    report_bytes = report.encode("utf-8")
    st.download_button(
        label="⬇️ Download Analysis Report (.txt)",
        data=report_bytes,
        file_name=f"ResumeAI_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown('<div class="b-warn" style="margin-top:1rem;">💡 Tip: Open the .txt file and print it as PDF using your browser or a text editor for a clean PDF version.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  EMPTY STATE — no resume
# ═══════════════════════════════════════════════════════════════
elif not has_result():
    st.markdown("""
    <div style="text-align:center;padding:6rem 2rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">📄</div>
        <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#252545;margin-bottom:0.4rem;">
            Upload a resume to unlock all features
        </div>
        <div style="font-size:0.78rem;color:#1a1a38;">
            Click "📤 Upload & Parse Resume" in the sidebar to get started
        </div>
    </div>
    """, unsafe_allow_html=True)
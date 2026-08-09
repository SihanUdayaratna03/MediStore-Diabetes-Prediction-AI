"""
MediStore AI — Streamlit interface for the v2 diabetes risk model.

An alternative UI to the React frontend; both are backed by the same
`models/v2/` artifacts.

Run from the project root:
    streamlit run apps/streamlit/app.py
"""

import sys
from pathlib import Path

# This script lives outside the `backend` package, so put the project root on
# sys.path to reuse the single source of truth for artifact locations.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import numpy as np
import joblib
import plotly.graph_objects as go
import base64
import json
import shap
import matplotlib.pyplot as plt

from backend.config import V2_MODEL, V2_SCALER, V2_EXPLAINER, V2_FEATURES


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MediStore AI · Diabetic Prediction",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ── Clean Light Theme CSS ─────────────────────────────────────────────────────
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }

/* ── Background ───────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: #f4f7f6;
    min-height: 100vh;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebarCollapseButton"] { display: none; }
#MainMenu, footer { visibility: hidden; }

.main .block-container {
    padding-top: 1rem;
    padding-left: 0; padding-right: 0;
}

/* ══════════════════════════════════════════════════════════════════════════
   LANDING PAGE STYLES
   ══════════════════════════════════════════════════════════════════════════ */
@keyframes fadeInUp {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.lp-hero {
    min-height: 100vh; display: flex; align-items: center;
    padding: 4rem 3rem 4rem 4rem; max-width: 680px;
    animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}
.lp-eyebrow {
    display: inline-flex; align-items: center; gap: 0.45rem;
    background: #e0f2fe; border: 1px solid #bae6fd;
    border-radius: 20px; padding: 0.3rem 0.9rem;
    font-size: 0.73rem; font-weight: 700; color: #0369a1;
    letter-spacing: 0.09em; text-transform: uppercase; margin-bottom: 1.2rem;
}
.lp-eyebrow-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #0ea5e9; box-shadow: 0 0 8px rgba(14,165,233,0.4);
}
.lp-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.6rem, 5.5vw, 4.2rem); font-weight: 800;
    color: #0f172a; line-height: 1.10; letter-spacing: -0.03em;
    margin-bottom: 1.2rem;
}
.lp-heading .accent {
    background: linear-gradient(120deg, #0284c7 0%, #0369a1 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.lp-subtext {
    font-size: 1.05rem; font-weight: 500; color: #475569;
    line-height: 1.72; max-width: 500px; margin-bottom: 2.4rem;
}
.lp-cta {
    display: inline-flex; align-items: center; gap: 0.55rem;
    background: #0369a1; color: #ffffff !important;
    border: none; border-radius: 8px; padding: 0.95rem 2.2rem;
    font-family: 'Space Grotesk', sans-serif; font-size: 0.95rem; font-weight: 700;
    letter-spacing: 0.07em; text-transform: uppercase; cursor: pointer;
    box-shadow: 0 4px 14px rgba(3,105,161,0.3);
    transition: all 0.2s;
}
.lp-cta:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(3,105,161,0.4); background: #075985; }
.lp-stats {
    display: flex; gap: 2.5rem; margin-top: 3rem;
    border-top: 1px solid #e2e8f0; padding-top: 1.8rem;
}
.lp-stat-val { font-family: 'Space Grotesk', sans-serif; font-size: 1.7rem; font-weight: 800; color: #0f172a; line-height: 1; }
.lp-stat-lbl { font-size: 0.74rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }

/* ══════════════════════════════════════════════════════════════════════════
   DASHBOARD STYLES
   ══════════════════════════════════════════════════════════════════════════ */
/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e2e8f0;
    box-shadow: 2px 0 10px rgba(0,0,0,0.03);
}
[data-testid="stSidebar"] * { color: #334155 !important; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1.2rem; }
[data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stSliderTrackActive"] { background: #0ea5e9 !important; }
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
    background: #ffffff !important; border: 2px solid #0ea5e9 !important; box-shadow: 0 0 4px rgba(14,165,233,0.3) !important;
}
[data-testid="stSidebar"] input {
    background: #f8fafc !important; border: 1px solid #cbd5e1 !important; border-radius: 6px !important; color: #0f172a !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label p {
    font-size: 0.8rem !important; font-weight: 600 !important; color: #475569 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #0ea5e9 !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 700 !important; font-size: 1rem !important;
    box-shadow: 0 4px 12px rgba(14,165,233,0.3) !important; transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover { transform: translateY(-2px) !important; background: #0284c7 !important; }
hr { border-color: #e2e8f0 !important; margin: 1.5rem 0 !important; }

/* Cards */
.card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 2rem 2.4rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    margin-bottom: 1.4rem; position: relative; overflow: hidden;
}

/* Dashboard navbar */
.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 2rem; background: #ffffff; border-bottom: 1px solid #e2e8f0;
    margin-bottom: 1.4rem; position: sticky; top: 0; z-index: 100;
}
.nav-brand { display: flex; align-items: center; gap: 0.75rem; }
.nav-logo {
    width: 36px; height: 36px; background: #0ea5e9; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: white;
}
.nav-name {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0f172a;
}
.nav-badge {
    background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 20px;
    padding: 0.25rem 0.8rem; font-size: 0.72rem; font-weight: 600; color: #475569;
    letter-spacing: 0.06em; text-transform: uppercase;
}
.nav-back {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
    padding: 0.38rem 0.9rem; font-size: 0.78rem; font-weight: 600; color: #475569;
    cursor: pointer; transition: background 0.18s;
}

/* Hero heading */
.hero-tag {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: #e0f2fe; border: 1px solid #bae6fd; border-radius: 20px;
    padding: 0.28rem 0.85rem; font-size: 0.75rem; font-weight: 700; color: #0284c7;
    letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.9rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif; font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight: 700;
    color: #0f172a; line-height: 1.12; letter-spacing: -0.02em; margin-bottom: 0.6rem;
}
.hero-sub {
    font-size: 1rem; font-weight: 400; color: #64748b; line-height: 1.6;
    max-width: 540px; margin-bottom: 2rem;
}
.stats-row { display: flex; flex-wrap: wrap; gap: 0.65rem; }
.stat {
    display: inline-flex; align-items: center; gap: 0.7rem;
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 0.75rem 1.4rem;
}
.stat-val { font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0f172a; }
.stat-lbl { font-size: 0.72rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }

/* Section heading */
.sh {
    font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0f172a;
    margin-bottom: 1.1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0;
    display: flex; align-items: center; gap: 0.5rem;
}

/* Result banners */
.result-banner {
    border-radius: 12px; padding: 1.4rem 1.8rem; font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1.2rem;
}
.rb-low  { background: #dcfce7; border: 1px solid #86efac; color: #166534; }
.rb-mod  { background: #fef9c3; border: 1px solid #fde047; color: #854d0e; }
.rb-high { background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; }

/* Probability bars */
.prob-label { font-size: 0.78rem; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.3rem; }
.prob-value { font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem; }
.bar-track { height: 8px; border-radius: 99px; background: #e2e8f0; overflow: hidden; margin-bottom: 1.2rem; }
.bar-fill  { height: 100%; border-radius: 99px; }

/* Factor badges */
.factor { display: flex; align-items: center; gap: 0.7rem; border-radius: 8px; padding: 0.65rem 1rem; margin: 0.35rem 0; font-size: 0.9rem; font-weight: 500; border: 1px solid transparent; }
.factor-r { background: #fee2e2; border-color: #fca5a5; color: #991b1b; }
.factor-y { background: #fef9c3; border-color: #fde047; color: #854d0e; }
.factor-g { background: #dcfce7; border-color: #86efac; color: #166534; }
.factor-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-r { background: #ef4444; }
.dot-y { background: #eab308; }
.dot-g { background: #22c55e; }

/* Rec list */
.rec-item {
    display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.7rem 0;
    border-bottom: 1px solid #f1f5f9; font-size: 0.93rem; color: #334155; line-height: 1.5;
}
.rec-item:last-child { border-bottom: none; }
.disclaimer {
    background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b;
    border-radius: 0 8px 8px 0; padding: 0.9rem 1.3rem; color: #92400e; font-size: 0.84rem; line-height: 1.6; margin-top: 1rem;
}
.sidebar-section {
    font-family: 'Space Grotesk', sans-serif; font-size: 0.75rem; font-weight: 700;
    color: #64748b; text-transform: uppercase; letter-spacing: 0.1em;
    padding: 1rem 0 0.4rem; border-top: 1px solid #e2e8f0; margin-top: 0.6rem;
}
.sidebar-section:first-of-type { border-top: none; margin-top: 0; padding-top: 0; }

[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important; color: #0f172a !important; font-weight: 800 !important; font-size: 2rem !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; }

/* Feature cards (landing) */
.feat-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 1.8rem 1.6rem; text-align: center; height: 100%; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.feat-icon { width: 52px; height: 52px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin: 0 auto 1rem; color: #0ea5e9; }
.feat-title { font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.55rem; }
.feat-body  { font-size: 0.86rem; color: #475569; line-height: 1.6; }
</style>
''', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL LOAD
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_artifacts():
    try:
        model = joblib.load(V2_MODEL)
        scaler = joblib.load(V2_SCALER)
        explainer = joblib.load(V2_EXPLAINER)
        with open(V2_FEATURES) as f:
            feature_names = json.load(f)
        return model, scaler, explainer, feature_names
    except FileNotFoundError:
        return None, None, None, None

def get_blur_text_html(text, class_name="", delay_ms=150):
    words = text.split(" ")
    spans = []
    for i, word in enumerate(words):
        delay = i * (delay_ms / 1000.0)
        span_html = f'<span class="blur-word {class_name}" style="animation-delay: {delay}s;">{word}</span>'
        spans.append(span_html)
    return f'<div style="display: flex; flex-wrap: wrap; column-gap: 0.3em; row-gap: 0.1em;">{"".join(spans)}</div>'


# ══════════════════════════════════════════════════════════════════════════════
#  ███████  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    # ── Hero layout: text left, background visible on the right ───────────
    hero_col, _ = st.columns([5, 4], gap="large")

    with hero_col:
        lp_heading_1 = get_blur_text_html("Clinical Precision", delay_ms=150)
        lp_heading_2 = get_blur_text_html("at Your Fingertips", delay_ms=150)
        
        st.markdown(f"""
        <div class="lp-hero">
          <div>
            <div class="lp-eyebrow">
              <div class="lp-eyebrow-dot"></div>
              Advanced Pharmacy Care
            </div>
            <div class="lp-heading">
              {lp_heading_1}
              {lp_heading_2}
            </div>
            <div class="lp-subtext">
              Empowering healthcare professionals with AI-driven insights for proactive diabetes management and personalized patient care.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Streamlit button triggers page switch
        if st.button("Access Risk Assessment", key="get_started_btn"):
            st.session_state.page = "dashboard"
            st.session_state.sidebar_state = "expanded"
            st.rerun()

        st.markdown("""
        <div class="lp-stats">
          <div class="lp-stat">
            <div class="lp-stat-val">~78%</div>
            <div class="lp-stat-lbl">Model Accuracy</div>
          </div>
          <div class="lp-stat">
            <div class="lp-stat-val">768</div>
            <div class="lp-stat-lbl">Training Samples</div>
          </div>
          <div class="lp-stat">
            <div class="lp-stat-val">8</div>
            <div class="lp-stat-lbl">Biomarkers Used</div>
          </div>
          <div class="lp-stat">
            <div class="lp-stat-val">SVM</div>
            <div class="lp-stat-lbl">Algorithm</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Style the Get Started button ──────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stMain"] .stButton > button {
        background: #00606b !important;
        color: #ffffff !important; border: none !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important; font-weight: 700 !important;
        letter-spacing: 0.05em !important; text-transform: uppercase !important;
        padding: 0.8rem 2.2rem !important;
        box-shadow: 0 4px 12px rgba(0, 96, 107, 0.4) !important;
        transition: background 0.18s, transform 0.18s !important;
        margin-bottom: 1rem !important;
    }
    [data-testid="stMain"] .stButton > button:hover {
        background: #008598 !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ██████  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:
    model, scaler, explainer, feature_names = load_artifacts()

    # ── Dashboard Navbar ──────────────────────────────────────────────────────
    nav_col1, nav_col2 = st.columns([1, 8])
    with nav_col1:
        if st.button("← Home", key="back_btn"):
            st.session_state.page = "landing"
            st.rerun()

    with nav_col2:
        st.markdown("""
        <div class="navbar" style="margin-bottom:0;">
          <div class="nav-brand">
            <div class="nav-logo">💊</div>
            <div>
              <div class="nav-name">MediStore AI</div>
              <div style="font-size:0.68rem;color:rgba(170,235,230,0.50);letter-spacing:0.05em;">Diabetic Prediction System</div>
            </div>
          </div>
          <div style="display:flex;gap:0.6rem;">
            <div class="nav-badge">🤖 SVM Model</div>
            <div class="nav-badge">🔒 Local &amp; Private</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Model check ───────────────────────────────────────────────────────────
    if model is None or scaler is None or explainer is None:
        st.markdown("""
        <div class="card" style="border-color:rgba(255,80,80,0.30);">
          <div style="display:flex;align-items:center;gap:1rem;">
            <div style="font-size:2rem;">⚠️</div>
            <div>
              <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;color:#ff8888;margin-bottom:0.3rem;">Model Files Not Found</div>
              <div style="color:rgba(200,230,228,0.75);font-size:0.9rem;">
                Ensure <code>diabetes_model_v2.pkl</code>, <code>scaler_v2.pkl</code>, and <code>shap_explainer.pkl</code> exist in <code>models/v2/</code>. Run <code>python -m backend.ml.train_v2</code> to regenerate them.
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # ── Hero card ─────────────────────────────────────────────────────────────
    hero_title_html = get_blur_text_html("MediStore Diabetic Prediction System", delay_ms=150)
    st.markdown(f"""
    <div class="card" style="padding:2rem 2.8rem 1.6rem;">
      <div class="card-accent"></div>
      <div class="hero-tag">💊 Clinical AI Tool · v2.0</div>
      <div class="hero-title">{hero_title_html}</div>
      <div class="hero-sub">AI-powered risk assessment · Support Vector Machine · Enter patient details in the sidebar</div>
      <div class="stats-row">
        <div class="stat"><div><div class="stat-val">SVM</div><div class="stat-lbl">Algorithm</div></div></div>
        <div class="stat"><div><div class="stat-val">~85%</div><div class="stat-lbl">Accuracy</div></div></div>
        <div class="stat"><div><div class="stat-val">768</div><div class="stat-lbl">Samples</div></div></div>
        <div class="stat"><div><div class="stat-val">16</div><div class="stat-lbl">Features</div></div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:0.8rem 0 1.4rem;">
          <div style="font-size:1.9rem;margin-bottom:0.5rem;">🩺</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#7fffd4;">Patient Information</div>
          <div style="font-size:0.75rem;color:rgba(170,235,230,0.55);margin-top:0.25rem;">Complete all fields for accurate results</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">👤 Demographics</div>', unsafe_allow_html=True)
        age         = st.slider("Age (years)", 21, 100, 30)
        pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)

        st.markdown('<div class="sidebar-section">🔬 Clinical Measurements</div>', unsafe_allow_html=True)
        glucose  = st.slider("Plasma Glucose (mg/dL)", 0, 200, 120)
        bp       = st.slider("Diastolic Blood Pressure (mm Hg)", 0, 130, 70)
        skin     = st.slider("Triceps Skin Thickness (mm)", 0, 100, 20)
        insulin  = st.slider("2-Hour Serum Insulin (mu U/ml)", 0, 900, 80)

        st.markdown('<div class="sidebar-section">📊 Indices</div>', unsafe_allow_html=True)
        bmi = st.number_input("Body Mass Index (BMI)", 10.0, 70.0, 25.0, 0.1)
        dpf = st.slider("Diabetes Pedigree Function", 0.0, 2.5, 0.5, 0.01)

        st.markdown("---")
        st.markdown(f"""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;
                    border-radius:12px;padding:0.9rem 1rem;margin-bottom:1rem;font-size:0.83rem;">
          <div style="color:#0369a1;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.07em;margin-bottom:0.5rem;font-size:0.72rem;">Input Summary</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem 1rem;">
            <span style="color:#64748b;">Age</span><span style="color:#0f172a;font-weight:600;">{age} yrs</span>
            <span style="color:#64748b;">Glucose</span><span style="color:#0f172a;font-weight:600;">{glucose} mg/dL</span>
            <span style="color:#64748b;">BMI</span><span style="color:#0f172a;font-weight:600;">{bmi:.1f}</span>
            <span style="color:#64748b;">Blood Pressure</span><span style="color:#0f172a;font-weight:600;">{bp} mm Hg</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        predict_btn = st.button("🔮 Run Prediction", type="primary", use_container_width=True)

        st.markdown("""
        <div style="text-align:center;padding-top:1rem;font-size:0.74rem;color:#94a3b8;">
          MediStore AI · Educational Use Only
        </div>""", unsafe_allow_html=True)

    # ── Prediction ────────────────────────────────────────────────────────────
    if predict_btn:
        glucose_bmi_ratio   = glucose / (bmi + 0.001)
        insulin_resistance  = glucose * insulin / 1000
        age_bmi_interaction = age * bmi
        bp_age_risk         = bp * age / 100
        glucose_age         = glucose * age / 100
        high_glucose_flag   = 1 if glucose > 125 else 0
        obese_flag          = 1 if bmi > 30 else 0
        high_risk_age_flag  = 1 if age > 45 else 0

        input_data = np.array([[
            pregnancies, glucose, bp, skin, insulin, bmi, dpf, age,
            glucose_bmi_ratio, insulin_resistance, age_bmi_interaction,
            bp_age_risk, glucose_age, high_glucose_flag, obese_flag, high_risk_age_flag
        ]])
        input_std  = scaler.transform(input_data)
        prediction = model.predict(input_std)[0]

        try:
            proba    = model.predict_proba(input_std)[0]
            prob_neg = proba[0] * 100
            prob_pos = proba[1] * 100
        except Exception:
            prob_pos = 100.0 if prediction == 1 else 0.0
            prob_neg = 100.0 - prob_pos

        if prediction == 0:
            rb_cls, rb_icon, rb_text = ("rb-low", "✅", "LOW RISK — Not Diabetic") if prob_pos < 30 else ("rb-mod", "⚠️", "MODERATE RISK — Not Diabetic")
            bar_color = "linear-gradient(90deg,#00c882,#00f5a0)" if prob_pos < 30 else "linear-gradient(90deg,#f5a623,#ffd200)"
        else:
            rb_cls, rb_icon, rb_text = ("rb-high", "🔴", "HIGH RISK — Diabetic") if prob_pos > 70 else ("rb-mod", "⚠️", "MODERATE RISK — Diabetic")
            bar_color = "linear-gradient(90deg,#ff4444,#ff7070)" if prob_pos > 70 else "linear-gradient(90deg,#f5a623,#ffd200)"

        gauge_color = "#00d482" if prob_pos < 30 else "#ffb300" if prob_pos < 70 else "#ff4444"

        # Results card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-accent"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sh">🎯 Prediction Results</div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([3, 2], gap="large")

        with col_left:
            st.markdown(f'<div class="result-banner {rb_cls}"><span style="font-size:1.5rem;">{rb_icon}</span><span>{rb_text}</span></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div>
              <div class="prob-label">Non-Diabetic Probability</div>
              <div class="prob-value">{prob_neg:.1f}%</div>
              <div class="bar-track"><div class="bar-fill" style="width:{prob_neg:.1f}%;background:linear-gradient(90deg,#00c882,#00f5a0);"></div></div>
              <div class="prob-label">Diabetic Probability</div>
              <div class="prob-value" style="color:{'#ef4444' if prob_pos>50 else '#0f172a'};">{prob_pos:.1f}%</div>
              <div class="bar-track"><div class="bar-fill" style="width:{prob_pos:.1f}%;background:{bar_color};"></div></div>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            fig = go.Figure(go.Indicator(
                mode  = "gauge+number+delta",
                value = prob_pos,
                delta = {"reference": 50, "suffix": "%", "font": {"color": "#aaa", "size": 13},
                         "decreasing": {"color": "#00d482"}, "increasing": {"color": "#ff5c5c"}},
                title = {"text": "DIABETES RISK SCORE", "font": {"color": "#64748b", "size": 11, "family": "Inter"}},
                number= {"suffix": "%", "font": {"color": "#0f172a", "size": 38, "family": "Space Grotesk"}},
                gauge = {
                    "axis": {"range": [0, 100], "tickvals": [0,25,50,75,100],
                             "ticktext": ["0","25","50","75","100"],
                             "tickcolor": "#cbd5e1",
                             "tickfont": {"color": "#94a3b8", "size": 10, "family": "Inter"}},
                    "bar":  {"color": gauge_color, "thickness": 0.24},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0,  30], "color": "rgba(0,200,130,0.13)"},
                        {"range": [30, 70], "color": "rgba(255,180,0,0.13)"},
                        {"range": [70,100], "color": "rgba(255,60,60,0.13)"},
                    ],
                    "threshold": {"line": {"color": "rgba(255,255,255,0.50)", "width": 2}, "thickness": 0.75, "value": 50},
                },
            ))
            fig.update_layout(height=290, margin=dict(l=10, r=10, t=55, b=5),
                              paper_bgcolor="rgba(0,0,0,0)", font={"family": "Inter"})
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Risk / Positive factors
        risks, goods = [], []
        if glucose > 125: risks.append(("r", "High plasma glucose (>125 mg/dL) — key diabetes marker"))
        elif glucose < 100: goods.append(("g", "Normal fasting glucose — within healthy range"))
        if bmi > 30: risks.append(("r", "Obesity — BMI >30 significantly raises diabetes risk"))
        elif 18.5 <= bmi <= 24.9: goods.append(("g", "Healthy BMI (18.5–24.9) — reduces metabolic risk"))
        elif bmi >= 25: risks.append(("y", "Overweight — BMI between 25–30, borderline risk"))
        if age > 45: risks.append(("y", "Age >45 — diabetes prevalence increases with age"))
        elif age < 35: goods.append(("g", "Younger age — lower baseline diabetes risk"))
        if bp > 80: risks.append(("r", "Elevated diastolic BP (>80 mm Hg) — metabolic risk factor"))
        elif 60 <= bp <= 80: goods.append(("g", "Diastolic blood pressure within normal range"))
        if dpf > 0.8: risks.append(("r", "High genetic predisposition (DPF >0.8)"))
        elif dpf > 0.5: risks.append(("y", "Moderate genetic predisposition (DPF >0.5)"))
        else: goods.append(("g", "Low genetic predisposition (DPF ≤0.5)"))
        if insulin > 200: risks.append(("y", "Elevated insulin — possible insulin resistance"))

        dot_map = {"r": "dot-r", "y": "dot-y", "g": "dot-g"}
        cls_map = {"r": "factor-r", "y": "factor-y", "g": "factor-g"}

        fc1, fc2 = st.columns(2, gap="medium")
        with fc1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sh">⚠️ Risk Factors <span style="background:rgba(255,65,65,0.20);border-radius:99px;padding:0.1rem 0.55rem;font-size:0.75rem;margin-left:auto;">{len(risks)}</span></div>', unsafe_allow_html=True)
            if risks:
                for lvl, txt in risks:
                    st.markdown(f'<div class="factor {cls_map[lvl]}"><div class="factor-dot {dot_map[lvl]}"></div><span>{txt}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="factor factor-g"><div class="factor-dot dot-g"></div><span>No significant risk factors identified</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with fc2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="sh">✅ Positive Indicators <span style="background:rgba(0,200,130,0.20);border-radius:99px;padding:0.1rem 0.55rem;font-size:0.75rem;margin-left:auto;">{len(goods)}</span></div>', unsafe_allow_html=True)
            if goods:
                for lvl, txt in goods:
                    st.markdown(f'<div class="factor {cls_map[lvl]}"><div class="factor-dot {dot_map[lvl]}"></div><span>{txt}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="factor factor-r"><div class="factor-dot dot-r"></div><span>No strong positive indicators detected</span></div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Recommendations
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sh">💡 Clinical Recommendations</div>', unsafe_allow_html=True)
        if prediction == 1:
            recs = [("🏥","Consult a healthcare professional or endocrinologist as soon as possible"),
                    ("🧪","Request a full diabetes panel: HbA1c, fasting plasma glucose, oral glucose tolerance test"),
                    ("📊","Begin self-monitoring of blood glucose — aim for pre-meal readings below 7 mmol/L"),
                    ("🥗","Reduce dietary refined sugars and processed carbohydrates; increase fibre intake"),
                    ("🏃","Start structured physical activity — 150 min/week moderate aerobic exercise"),
                    ("💊","Discuss pharmacological management options with your doctor")]
            item_col = "#ffcaca"
        else:
            recs = [("📅","Schedule annual blood glucose and HbA1c screening tests"),
                    ("🥗","Maintain a balanced diet — Mediterranean or low-GI dietary patterns recommended"),
                    ("🏃","Stay physically active — at least 150 minutes of moderate exercise per week"),
                    ("⚖️","Maintain a healthy weight; even 5–7% weight reduction lowers diabetes risk"),
                    ("💧","Stay well-hydrated — aim for 2–3 litres of water daily"),
                    ("😴","Prioritise 7–9 hours of quality sleep — poor sleep increases insulin resistance")]
            item_col = "#aaffd4"

        for icon, text in recs:
            st.markdown(f'<div class="rec-item"><div style="background:rgba(0,200,190,0.12);border:1px solid rgba(0,200,190,0.30);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{icon}</div><span style="color:{item_col};">{text}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="disclaimer">⚠️ <strong>Medical Disclaimer</strong> — This tool is for educational purposes only. It does <em>not</em> constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # SHAP Explainability Panel
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sh">🧠 Explainable AI (SHAP)</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85rem;color:#475569;margin-bottom:1rem;">This panel shows exactly how each biomarker influenced the AI\'s decision. Features pushing right (red) increase diabetes risk, while features pushing left (blue) lower it.</div>', unsafe_allow_html=True)
        
        try:
            shap_values = explainer(input_std)
            # Set matplotlib style for light theme
            plt.style.use('default')
            fig_shap, ax = plt.subplots(figsize=(8, 4.5))
            # Map feature names
            shap_values.feature_names = feature_names
            shap.plots.waterfall(shap_values[0], max_display=10, show=False)
            plt.tight_layout()
            
            # Save to buffer and display
            import io
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=150, bbox_inches='tight', transparent=True)
            buf.seek(0)
            st.image(buf, use_container_width=True)
            plt.close(fig_shap)
        except Exception as e:
            st.error(f"SHAP explanation could not be generated. Error: {str(e)}")
            
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # No prediction yet — feature cards
        c1, c2, c3 = st.columns(3, gap="medium")
        features = [
            ("🧬","Evidence-Based Model","Trained on an upgraded dataset with 16 clinical biomarkers, SMOTE balancing, and an XGBoost Ensemble for ~85%+ accuracy."),
            ("⚡","Instant Analysis","Probability scores, risk gauge, factor analysis, and clinical recommendations in under a second."),
            ("🔒","Private & Secure","All inference runs locally. No patient data is stored, logged, or sent to any external server."),
        ]
        for col, (icon, title, body) in zip([c1, c2, c3], features):
            with col:
                st.markdown(f'<div class="feat-card"><div class="feat-icon">{icon}</div><div class="feat-title">{title}</div><div class="feat-body">{body}</div></div>', unsafe_allow_html=True)
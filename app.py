import streamlit as st
import numpy as np
import joblib
import plotly.graph_objects as go
import base64, os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediStore · Diabetic Prediction System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

def img_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "background.png")
bg_b64  = img_to_b64(bg_path) if os.path.exists(bg_path) else ""

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Reset & base ─────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

/* ── Full background ──────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif;
    background-image: url("data:image/png;base64,{bg_b64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    min-height: 100vh;
}}
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: linear-gradient(
        160deg,
        rgba(2, 22, 38, 0.82) 0%,
        rgba(0, 38, 55, 0.76) 40%,
        rgba(0, 55, 65, 0.72) 100%
    );
    backdrop-filter: blur(2px);
}}
[data-testid="stAppViewContainer"] > .main {{
    background: transparent; position: relative; z-index: 1;
}}
[data-testid="stHeader"]  {{ background: transparent; }}
[data-testid="stToolbar"] {{ display: none; }}
#MainMenu, footer {{ visibility: hidden; }}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: rgba(1, 18, 30, 0.82) !important;
    backdrop-filter: blur(30px) saturate(200%);
    -webkit-backdrop-filter: blur(30px) saturate(200%);
    border-right: 1px solid rgba(0, 210, 200, 0.15);
    box-shadow: 8px 0 40px rgba(0,0,0,0.50);
}}
[data-testid="stSidebar"] * {{ color: #c8f0ee !important; }}
[data-testid="stSidebarContent"] {{ padding: 1rem 1.2rem; }}

/* Slider track */
[data-testid="stSidebar"] [data-baseweb="slider"] [data-testid="stSliderTrackActive"] {{
    background: linear-gradient(90deg, #00b8ae, #00dfd4) !important;
}}
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
    background: #00dfd4 !important;
    border: 2px solid rgba(255,255,255,0.4) !important;
    box-shadow: 0 0 12px rgba(0,220,210,0.6) !important;
}}

/* Number input */
[data-testid="stSidebar"] input {{
    background: rgba(0,220,210,0.07) !important;
    border: 1px solid rgba(0,220,210,0.30) !important;
    border-radius: 10px !important;
    color: #c8f0ee !important;
    font-family: 'Inter', sans-serif !important;
}}
[data-testid="stSidebar"] input:focus {{
    border-color: rgba(0,220,210,0.65) !important;
    box-shadow: 0 0 0 3px rgba(0,220,210,0.15) !important;
}}

/* Sidebar label */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSlider label p {{
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: rgba(180,240,236,0.70) !important;
}}

/* Predict button */
[data-testid="stSidebar"] .stButton > button {{
    background: linear-gradient(135deg, #00c8be 0%, #006f80 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.85rem 1rem !important;
    width: 100% !important;
    box-shadow: 0 6px 28px rgba(0,200,190,0.45), inset 0 1px 0 rgba(255,255,255,0.20) !important;
    transition: all 0.22s cubic-bezier(.4,0,.2,1) !important;
    cursor: pointer !important;
    text-transform: uppercase !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 14px 36px rgba(0,200,190,0.60) !important;
    background: linear-gradient(135deg, #00ddd2 0%, #008598 100%) !important;
}}
[data-testid="stSidebar"] .stButton > button:active {{
    transform: translateY(0) !important;
}}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr {{ border-color: rgba(0,210,200,0.15) !important; margin: 1rem 0 !important; }}

/* ── Glass card ───────────────────────────────────────────────────────── */
.card {{
    background: rgba(255,255,255,0.055);
    backdrop-filter: blur(28px) saturate(200%);
    -webkit-backdrop-filter: blur(28px) saturate(200%);
    border: 1px solid rgba(255,255,255,0.13);
    border-top: 1px solid rgba(255,255,255,0.22);
    border-radius: 24px;
    padding: 2rem 2.4rem;
    box-shadow:
        0 4px 24px rgba(0,0,0,0.30),
        0 1px 0 rgba(255,255,255,0.08) inset,
        0 -1px 0 rgba(0,0,0,0.15) inset;
    margin-bottom: 1.4rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}}
.card::after {{
    content: "";
    position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,220,210,0.4), transparent);
}}

/* ── Top-right accent corner ─────────────────────────────────────────── */
.card-accent {{
    position: absolute; top: 0; right: 0;
    width: 140px; height: 140px;
    background: radial-gradient(circle at top right, rgba(0,210,200,0.12), transparent 70%);
    border-radius: 0 24px 0 0;
    pointer-events: none;
}}

/* ── Nav bar ──────────────────────────────────────────────────────────── */
.navbar {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 1rem 2rem;
    background: rgba(0, 15, 25, 0.75);
    backdrop-filter: blur(30px);
    border-bottom: 1px solid rgba(0,210,200,0.15);
    border-radius: 0 0 20px 20px;
    margin-bottom: 1.6rem;
    position: sticky; top: 0; z-index: 100;
}}
.nav-brand {{
    display: flex; align-items: center; gap: 0.8rem;
}}
.nav-logo {{
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #00c8be, #006f80);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    box-shadow: 0 4px 14px rgba(0,200,190,0.40);
}}
.nav-name {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem; font-weight: 700;
    background: linear-gradient(120deg, #7fffd4, #00d4c8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.nav-badge {{
    background: rgba(0,210,200,0.15);
    border: 1px solid rgba(0,210,200,0.35);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.75rem; font-weight: 600;
    color: #7fffd4;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}

/* ── Hero ─────────────────────────────────────────────────────────────── */
.hero-tag {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(0,210,200,0.12);
    border: 1px solid rgba(0,210,200,0.30);
    border-radius: 20px;
    padding: 0.28rem 0.85rem;
    font-size: 0.75rem; font-weight: 700;
    color: #7fffd4; letter-spacing: 0.08em; text-transform: uppercase;
    margin-bottom: 0.9rem;
}}
.hero-tag::before {{
    content: "●"; color: #00d4c8; font-size: 0.6rem;
    animation: pulse-dot 2s infinite;
}}
@keyframes pulse-dot {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }}
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    background: linear-gradient(120deg, #a8fdf0 0%, #00d8cc 40%, #e0fffc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.12;
    letter-spacing: -0.03em;
    margin-bottom: 0.6rem;
}}
.hero-sub {{
    font-size: 1.02rem; font-weight: 400;
    color: rgba(180,240,238,0.72);
    line-height: 1.6; max-width: 540px;
    margin-bottom: 2rem;
}}

/* ── Stat pills ───────────────────────────────────────────────────────── */
.stats-row {{ display: flex; flex-wrap: wrap; gap: 0.65rem; }}
.stat {{
    display: inline-flex; align-items: center; gap: 0.7rem;
    background: rgba(0,210,200,0.09);
    border: 1px solid rgba(0,210,200,0.25);
    border-radius: 14px; padding: 0.75rem 1.4rem;
    transition: all 0.22s ease;
}}
.stat:hover {{
    background: rgba(0,210,200,0.17);
    border-color: rgba(0,210,200,0.50);
    transform: translateY(-2px);
}}
.stat-val {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.35rem; font-weight: 700; color: #7fffd4;
}}
.stat-lbl {{
    font-size: 0.72rem; font-weight: 600; color: rgba(170,235,230,0.65);
    text-transform: uppercase; letter-spacing: 0.08em;
}}

/* ── Section heading ──────────────────────────────────────────────────── */
.sh {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem; font-weight: 700; color: #7fffd4;
    margin-bottom: 1.1rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(0,210,200,0.18);
    display: flex; align-items: center; gap: 0.5rem;
}}

/* ── Result banner ────────────────────────────────────────────────────── */
.result-banner {{
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    display: flex; align-items: center; gap: 0.8rem;
    margin-bottom: 1.2rem;
    position: relative; overflow: hidden;
}}
.result-banner::before {{
    content: ""; position: absolute; inset: 0; opacity: 0.08;
    background: repeating-linear-gradient(
        45deg, transparent, transparent 6px,
        rgba(255,255,255,0.3) 6px, rgba(255,255,255,0.3) 7px
    );
}}
.rb-low  {{ background: rgba(0,200,130,0.14); border: 1.5px solid rgba(0,200,130,0.45); color: #96ffd6; }}
.rb-mod  {{ background: rgba(255,180,0,0.14);  border: 1.5px solid rgba(255,180,0,0.45);  color: #ffe89a; }}
.rb-high {{ background: rgba(255,60,60,0.14);  border: 1.5px solid rgba(255,60,60,0.45);  color: #ffb0b0; }}

/* ── Probability bars ─────────────────────────────────────────────────── */
.prob-label {{
    font-size: 0.78rem; font-weight: 600;
    color: rgba(170,235,230,0.70);
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 0.3rem;
}}
.prob-value {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem; font-weight: 700; color: #7fffd4;
    margin-bottom: 0.4rem;
}}
.bar-track {{
    height: 8px; border-radius: 99px;
    background: rgba(255,255,255,0.08);
    overflow: hidden; margin-bottom: 1.2rem;
}}
.bar-fill {{
    height: 100%; border-radius: 99px;
    transition: width 0.8s cubic-bezier(.4,0,.2,1);
}}

/* ── Factor badges ────────────────────────────────────────────────────── */
.factor {{
    display: flex; align-items: center; gap: 0.7rem;
    border-radius: 12px; padding: 0.65rem 1rem;
    margin: 0.35rem 0; font-size: 0.9rem; font-weight: 500;
    line-height: 1.4;
    border: 1px solid transparent;
    transition: transform 0.18s ease;
}}
.factor:hover {{ transform: translateX(4px); }}
.factor-r {{
    background: rgba(255,65,65,0.10);
    border-color: rgba(255,65,65,0.25);
    color: #ffc0c0;
}}
.factor-y {{
    background: rgba(255,185,0,0.10);
    border-color: rgba(255,185,0,0.25);
    color: #ffe89a;
}}
.factor-g {{
    background: rgba(0,200,130,0.10);
    border-color: rgba(0,200,130,0.25);
    color: #aaffd4;
}}
.factor-dot {{
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}}
.dot-r {{ background: #ff5c5c; box-shadow: 0 0 6px #ff5c5c; }}
.dot-y {{ background: #ffb800; box-shadow: 0 0 6px #ffb800; }}
.dot-g {{ background: #00d482; box-shadow: 0 0 6px #00d482; }}

/* ── Rec list ─────────────────────────────────────────────────────────── */
.rec-item {{
    display: flex; align-items: flex-start; gap: 0.75rem;
    padding: 0.7rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 0.93rem; color: rgba(200,240,238,0.85);
    line-height: 1.5;
}}
.rec-item:last-child {{ border-bottom: none; }}
.rec-icon {{ flex-shrink: 0; font-size: 1rem; margin-top: 0.05rem; }}

/* ── Disclaimer ───────────────────────────────────────────────────────── */
.disclaimer {{
    background: rgba(255,200,60,0.07);
    border: 1px solid rgba(255,200,60,0.22);
    border-left: 3px solid rgba(255,200,60,0.60);
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.3rem;
    color: rgba(255,240,170,0.85);
    font-size: 0.84rem; line-height: 1.75; margin-top: 1rem;
}}

/* ── Streamlit metric ─────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {{
    font-family: 'Space Grotesk', sans-serif !important;
    color: #7fffd4 !important; font-weight: 800 !important; font-size: 2rem !important;
}}
[data-testid="stMetricLabel"] {{ color: rgba(170,235,230,0.70) !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.07em !important; }}

/* ── Feature input row label ──────────────────────────────────────────── */
.sidebar-section {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    color: rgba(0,220,210,0.70);
    text-transform: uppercase; letter-spacing: 0.12em;
    padding: 0.6rem 0 0.3rem;
    border-top: 1px solid rgba(0,210,200,0.15);
    margin-top: 0.6rem;
}}

/* ── Landing feature card ─────────────────────────────────────────────── */
.feat-card {{
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.11);
    border-radius: 20px;
    padding: 1.8rem 1.6rem;
    text-align: center;
    transition: all 0.24s cubic-bezier(.4,0,.2,1);
    cursor: default;
    height: 100%;
}}
.feat-card:hover {{
    background: rgba(0,210,200,0.10);
    border-color: rgba(0,210,200,0.35);
    transform: translateY(-6px);
    box-shadow: 0 20px 48px rgba(0,0,0,0.30);
}}
.feat-icon {{
    width: 52px; height: 52px;
    background: linear-gradient(135deg, rgba(0,200,190,0.25), rgba(0,100,120,0.25));
    border: 1px solid rgba(0,210,200,0.30);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    margin: 0 auto 1rem;
    box-shadow: 0 4px 16px rgba(0,200,190,0.20);
}}
.feat-title {{ font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; color: #7fffd4; margin-bottom: 0.55rem; }}
.feat-body  {{ font-size: 0.86rem; color: rgba(170,235,230,0.72); line-height: 1.68; }}

/* ── CTA section ──────────────────────────────────────────────────────── */
.cta-box {{
    text-align: center; padding: 3.5rem 2rem;
}}
.cta-pulse {{
    width: 90px; height: 90px;
    background: linear-gradient(135deg, rgba(0,200,190,0.20), rgba(0,100,120,0.15));
    border: 2px solid rgba(0,210,200,0.35);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.4rem;
    margin: 0 auto 1.4rem;
    animation: pulse-ring 2.5s ease-in-out infinite;
    box-shadow: 0 0 0 0 rgba(0,210,200,0.35);
}}
@keyframes pulse-ring {{
    0%   {{ box-shadow: 0 0 0 0 rgba(0,210,200,0.40); }}
    70%  {{ box-shadow: 0 0 0 18px rgba(0,210,200,0.00); }}
    100% {{ box-shadow: 0 0 0 0 rgba(0,210,200,0.00); }}
}}
.cta-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem; font-weight: 700; color: #7fffd4;
    margin-bottom: 0.6rem;
}}
.cta-body {{
    color: rgba(180,240,238,0.72); font-size: 0.97rem;
    max-width: 480px; margin: 0 auto 0.5rem;
    line-height: 1.70;
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL LOAD
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_artifacts():
    try:
        return joblib.load("diabetes_model.pkl"), joblib.load("scaler_svm.pkl")
    except FileNotFoundError:
        return None, None


# ══════════════════════════════════════════════════════════════════════════════
#  NAV BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="navbar">
  <div class="nav-brand">
    <div class="nav-logo">💊</div>
    <div>
      <div class="nav-name">MediStore</div>
      <div style="font-size:0.7rem;color:rgba(170,235,230,0.55);letter-spacing:0.05em;">Diabetic Prediction System</div>
    </div>
  </div>
  <div style="display:flex;gap:0.6rem;align-items:center;">
    <div class="nav-badge">🤖 AI Powered</div>
    <div class="nav-badge">🔒 Local &amp; Private</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="card" style="padding:2.5rem 3rem 2rem;">
  <div class="card-accent"></div>
  <div class="hero-tag">💊 Clinical AI Tool · v2.0</div>
  <div class="hero-title">MediStore Diabetic<br>Prediction System</div>
  <div class="hero-sub">
    AI-powered diabetes risk assessment using a Support Vector Machine model
    trained on 768 clinical patient records. Get instant, evidence-based risk analysis.
  </div>
  <div class="stats-row">
    <div class="stat">
      <div><div class="stat-val">SVM</div><div class="stat-lbl">Algorithm</div></div>
    </div>
    <div class="stat">
      <div><div class="stat-val">~78%</div><div class="stat-lbl">Accuracy</div></div>
    </div>
    <div class="stat">
      <div><div class="stat-val">768</div><div class="stat-lbl">Samples</div></div>
    </div>
    <div class="stat">
      <div><div class="stat-val">8</div><div class="stat-lbl">Features</div></div>
    </div>
    <div class="stat">
      <div><div class="stat-val">Instant</div><div class="stat-lbl">Results</div></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL CHECK
# ══════════════════════════════════════════════════════════════════════════════
model, scaler = load_artifacts()

if model is None or scaler is None:
    st.markdown("""
    <div class="card" style="border-color:rgba(255,80,80,0.30);">
      <div style="display:flex;align-items:center;gap:1rem;">
        <div style="font-size:2rem;">⚠️</div>
        <div>
          <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;color:#ff8888;margin-bottom:0.3rem;">Model Files Not Found</div>
          <div style="color:rgba(200,230,228,0.75);font-size:0.9rem;">
            Ensure <code style="background:rgba(255,255,255,0.10);padding:0.15rem 0.4rem;border-radius:5px;">diabetes_model.pkl</code>
            and <code style="background:rgba(255,255,255,0.10);padding:0.15rem 0.4rem;border-radius:5px;">scaler_svm.pkl</code>
            exist in the project directory.
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:0.8rem 0 1.4rem;">
      <div style="font-size:1.9rem;margin-bottom:0.5rem;">🩺</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#7fffd4;">Patient Information</div>
      <div style="font-size:0.75rem;color:rgba(170,235,230,0.55);margin-top:0.25rem;letter-spacing:0.03em;">
        Complete all fields for accurate results
      </div>
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

    # Input summary
    st.markdown(f"""
    <div style="background:rgba(0,210,200,0.07);border:1px solid rgba(0,210,200,0.18);
                border-radius:12px;padding:0.9rem 1rem;margin-bottom:1rem;font-size:0.83rem;">
      <div style="color:rgba(0,220,210,0.75);font-weight:700;text-transform:uppercase;
                  letter-spacing:0.07em;margin-bottom:0.5rem;font-size:0.72rem;">Input Summary</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem 1rem;">
        <span style="color:rgba(170,235,230,0.60);">Age</span>
        <span style="color:#c8f0ee;font-weight:600;">{age} yrs</span>
        <span style="color:rgba(170,235,230,0.60);">Glucose</span>
        <span style="color:#c8f0ee;font-weight:600;">{glucose} mg/dL</span>
        <span style="color:rgba(170,235,230,0.60);">BMI</span>
        <span style="color:#c8f0ee;font-weight:600;">{bmi:.1f}</span>
        <span style="color:rgba(170,235,230,0.60);">Blood Pressure</span>
        <span style="color:#c8f0ee;font-weight:600;">{bp} mm Hg</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    predict_btn = st.button("🔮 Run Prediction", type="primary", use_container_width=True)  # noqa

    st.markdown("""
    <div style="text-align:center;padding-top:1rem;font-size:0.74rem;color:rgba(140,210,205,0.40);">
      MediStore AI · Educational Use Only
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
if predict_btn:
    input_data = np.array([[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]])
    input_std  = scaler.transform(input_data)
    prediction = model.predict(input_std)[0]

    try:
        proba    = model.predict_proba(input_std)[0]
        prob_neg = proba[0] * 100
        prob_pos = proba[1] * 100
    except Exception:
        prob_pos = 100.0 if prediction == 1 else 0.0
        prob_neg = 100.0 - prob_pos

    # ── Determine risk level ──────────────────────────────────────────────────
    if prediction == 0:
        if prob_pos < 30:
            rb_cls, rb_icon, rb_text = "rb-low",  "✅", "LOW RISK — Not Diabetic"
            bar_color = "linear-gradient(90deg,#00c882,#00f5a0)"
        else:
            rb_cls, rb_icon, rb_text = "rb-mod",  "⚠️", "MODERATE RISK — Not Diabetic"
            bar_color = "linear-gradient(90deg,#f5a623,#ffd200)"
    else:
        if prob_pos > 70:
            rb_cls, rb_icon, rb_text = "rb-high", "🔴", "HIGH RISK — Diabetic"
            bar_color = "linear-gradient(90deg,#ff4444,#ff7070)"
        else:
            rb_cls, rb_icon, rb_text = "rb-mod",  "⚠️", "MODERATE RISK — Diabetic"
            bar_color = "linear-gradient(90deg,#f5a623,#ffd200)"

    gauge_color = ("#00d482" if prob_pos < 30 else "#ffb300" if prob_pos < 70 else "#ff4444")

    # ── Results + Gauge ───────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-accent"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sh">🎯 Prediction Results</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown(f"""
        <div class="result-banner {rb_cls}">
          <span style="font-size:1.5rem;">{rb_icon}</span>
          <span>{rb_text}</span>
        </div>
        """, unsafe_allow_html=True)

        # Probability bars
        st.markdown(f"""
        <div style="margin-top:0.5rem;">
          <div class="prob-label">Non-Diabetic Probability</div>
          <div class="prob-value">{prob_neg:.1f}%</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{prob_neg:.1f}%;
              background:linear-gradient(90deg,#00c882,#00f5a0);"></div>
          </div>
          <div class="prob-label">Diabetic Probability</div>
          <div class="prob-value" style="color:{'#ffb0b0' if prob_pos>50 else '#7fffd4'};">{prob_pos:.1f}%</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{prob_pos:.1f}%;background:{bar_color};"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        fig = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = prob_pos,
            delta = {"reference": 50, "suffix": "%",
                     "font": {"color": "#aaa", "size": 13},
                     "decreasing": {"color": "#00d482"},
                     "increasing": {"color": "#ff5c5c"}},
            title = {"text": "DIABETES RISK SCORE",
                     "font": {"color": "rgba(170,235,230,0.65)", "size": 11,
                              "family": "Inter"}},
            number= {"suffix": "%", "font": {"color": "#7fffd4", "size": 38,
                                             "family": "Space Grotesk"}},
            gauge = {
                "axis": {"range": [0, 100],
                         "tickvals": [0,25,50,75,100],
                         "ticktext": ["0","25","50","75","100"],
                         "tickcolor": "rgba(150,220,215,0.40)",
                         "tickfont": {"color": "rgba(150,220,215,0.60)",
                                      "size": 10, "family": "Inter"},
                         },
                "bar":  {"color": gauge_color, "thickness": 0.24},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  30], "color": "rgba(0,200,130,0.13)"},
                    {"range": [30, 70], "color": "rgba(255,180,0,0.13)"},
                    {"range": [70,100], "color": "rgba(255,60,60,0.13)"},
                ],
                "threshold": {
                    "line": {"color": "rgba(255,255,255,0.50)", "width": 2},
                    "thickness": 0.75, "value": 50,
                },
            },
        ))
        fig.update_layout(
            height=290,
            margin=dict(l=10, r=10, t=55, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter"},
        )
        st.plotly_chart(fig, use_container_width=True)  # noqa

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Risk analysis + Positive indicators ──────────────────────────────────
    risks, goods = [], []
    if glucose > 125:
        risks.append(("r", "High plasma glucose (>125 mg/dL) — key diabetes marker"))
    elif glucose < 100:
        goods.append(("g", "Normal fasting glucose — within healthy range"))

    if bmi > 30:
        risks.append(("r", "Obesity — BMI >30 significantly raises diabetes risk"))
    elif 18.5 <= bmi <= 24.9:
        goods.append(("g", "Healthy BMI (18.5–24.9) — reduces metabolic risk"))
    elif bmi >= 25:
        risks.append(("y", "Overweight — BMI between 25–30, borderline risk"))

    if age > 45:
        risks.append(("y", "Age >45 — diabetes prevalence increases with age"))
    elif age < 35:
        goods.append(("g", "Younger age — lower baseline diabetes risk"))

    if bp > 80:
        risks.append(("r", "Elevated diastolic BP (>80 mm Hg) — metabolic risk factor"))
    elif 60 <= bp <= 80:
        goods.append(("g", "Diastolic blood pressure within normal range"))

    if dpf > 0.8:
        risks.append(("r", "High genetic predisposition (DPF >0.8) — family history risk"))
    elif dpf > 0.5:
        risks.append(("y", "Moderate genetic predisposition (DPF >0.5)"))
    else:
        goods.append(("g", "Low genetic predisposition (DPF ≤0.5)"))

    if insulin > 200:
        risks.append(("y", "Elevated insulin levels — possible insulin resistance"))
    elif insulin < 20 and glucose > 110:
        risks.append(("r", "Low insulin with high glucose — potential beta-cell issue"))

    dot_map   = {"r": "dot-r", "y": "dot-y", "g": "dot-g"}
    cls_map   = {"r": "factor-r", "y": "factor-y", "g": "factor-g"}

    fc1, fc2 = st.columns(2, gap="medium")

    with fc1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sh">⚠️ Risk Factors <span style="background:rgba(255,65,65,0.20);border-radius:99px;padding:0.1rem 0.55rem;font-size:0.75rem;margin-left:auto;">{len(risks)}</span></div>', unsafe_allow_html=True)
        if risks:
            for lvl, txt in risks:
                st.markdown(f"""
                <div class="factor {cls_map[lvl]}">
                  <div class="factor-dot {dot_map[lvl]}"></div>
                  <span>{txt}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="factor factor-g"><div class="factor-dot dot-g"></div><span>No significant risk factors identified</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with fc2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="sh">✅ Positive Indicators <span style="background:rgba(0,200,130,0.20);border-radius:99px;padding:0.1rem 0.55rem;font-size:0.75rem;margin-left:auto;">{len(goods)}</span></div>', unsafe_allow_html=True)
        if goods:
            for lvl, txt in goods:
                st.markdown(f"""
                <div class="factor {cls_map[lvl]}">
                  <div class="factor-dot {dot_map[lvl]}"></div>
                  <span>{txt}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="factor factor-r"><div class="factor-dot dot-r"></div><span>No strong positive indicators detected</span></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Recommendations ───────────────────────────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="sh">💡 Clinical Recommendations</div>', unsafe_allow_html=True)

    if prediction == 1:
        recs = [
            ("🏥", "Consult a healthcare professional or endocrinologist as soon as possible"),
            ("🧪", "Request a full diabetes panel: HbA1c, fasting plasma glucose, and oral glucose tolerance test"),
            ("📊", "Begin self-monitoring of blood glucose — aim for pre-meal readings below 7 mmol/L"),
            ("🥗", "Reduce dietary refined sugars and processed carbohydrates; increase fibre intake"),
            ("🏃", "Start a structured physical activity programme — 150 min/week moderate aerobic exercise"),
            ("💊", "Discuss pharmacological management options (e.g. Metformin) with your doctor"),
        ]
        col = "#ffcaca"
        icon_b = "rgba(255,65,65,0.15)"
        icon_bc = "rgba(255,65,65,0.35)"
    else:
        recs = [
            ("📅", "Schedule annual blood glucose and HbA1c screening tests"),
            ("🥗", "Maintain a balanced diet — Mediterranean or low-GI dietary patterns recommended"),
            ("🏃", "Stay physically active — at least 150 minutes of moderate exercise per week"),
            ("⚖️", "Maintain a healthy weight; even a 5–7% weight reduction lowers diabetes risk"),
            ("💧", "Stay well-hydrated — aim for 2–3 litres of water daily"),
            ("😴", "Prioritise 7–9 hours of quality sleep — poor sleep increases insulin resistance"),
        ]
        col = "#aaffd4"
        icon_b = "rgba(0,200,130,0.15)"
        icon_bc = "rgba(0,200,130,0.35)"

    for icon, text in recs:
        st.markdown(f"""
        <div class="rec-item">
          <div class="rec-icon" style="background:{icon_b};border:1px solid {icon_bc};
               border-radius:8px;width:32px;height:32px;display:flex;align-items:center;
               justify-content:center;flex-shrink:0;">{icon}</div>
          <span style="color:{col};">{text}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
      <strong>⚠️ Medical Disclaimer</strong> — This tool is intended for educational and informational
      purposes only. It does <em>not</em> constitute medical advice, diagnosis, or treatment.
      Always consult a qualified, licensed healthcare professional for any medical concerns or
      before making health-related decisions.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # ══════════════════════════════════════════════════════════════════════════
    #  LANDING PAGE
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div class="card">
      <div class="card-accent"></div>
      <div class="cta-box">
        <div class="cta-pulse">🩺</div>
        <div class="cta-title">Ready to Assess Diabetes Risk?</div>
        <div class="cta-body">
          Enter the patient's clinical measurements in the panel on the left,
          then click <strong style="color:#7fffd4;">Run Prediction</strong> to receive
          an AI-powered risk assessment with personalised clinical recommendations.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    features = [
        ("🧬", "Evidence-Based Model",
         "Trained on the benchmark Pima Indians Diabetes dataset — 768 patient records "
         "with 8 clinical biomarkers, validated through stratified train-test splits."),
        ("⚡", "Instant Analysis",
         "Receive probability scores, a colour-coded risk gauge, detailed factor "
         "analysis, and personalised clinical recommendations in under a second."),
        ("🔒", "Private & Secure",
         "All inference runs entirely on your local machine. No patient data is "
         "stored, logged, or transmitted to any external server."),
    ]
    for col, (icon, title, body) in zip([c1, c2, c3], features):
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-icon">{icon}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-body">{body}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Features row 2 ────────────────────────────────────────────────────────
    c4, c5, c6 = st.columns(3, gap="medium")
    features2 = [
        ("📊", "Probability Scores",
         "See exact diabetic and non-diabetic probabilities alongside an animated "
         "risk gauge, giving you full confidence in the prediction."),
        ("🩺", "Clinical Insights",
         "Detailed breakdown of individual risk factors — glucose, BMI, blood "
         "pressure, genetic predisposition, and more."),
        ("💡", "Smart Recommendations",
         "Receive actionable, evidence-based clinical recommendations tailored "
         "to the patient's specific risk profile and individual biomarkers."),
    ]
    for col, (icon, title, body) in zip([c4, c5, c6], features2):
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-icon">{icon}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-body">{body}</div>
            </div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:2rem 1rem 1rem;
                color:rgba(140,210,205,0.35);font-size:0.78rem;letter-spacing:0.04em;">
      MediStore Diabetic Prediction System · Built with Streamlit &amp; scikit-learn ·
      For educational use only
    </div>
    """, unsafe_allow_html=True)
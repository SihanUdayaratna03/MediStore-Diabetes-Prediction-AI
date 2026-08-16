"""
Central filesystem paths for MediStore AI.

Every module resolves datasets, model artifacts and figures through this file,
so the code behaves identically whether it is launched from the project root,
from inside `backend/`, or from a Docker container.
"""

from pathlib import Path

# backend/config.py -> backend/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ── Directories ────────────────────────────────────────────────────────────────
DATA_DIR      = PROJECT_ROOT / "data"
RAW_DATA_DIR  = DATA_DIR / "raw"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"          # generated; git-ignored

MODELS_DIR    = PROJECT_ROOT / "models"
MODELS_V2_DIR = MODELS_DIR / "v2"
MODELS_V3_DIR = MODELS_DIR / "v3"

REPORTS_DIR   = PROJECT_ROOT / "reports"
FIGURES_DIR   = REPORTS_DIR / "figures"

MCP_SERVERS_DIR = PROJECT_ROOT / "mcp_servers"

# ── Upload & session storage ───────────────────────────────────────────────────
UPLOADS_DIR      = PROJECT_ROOT / "data" / "uploads"         # raw uploaded files
SESSION_CHROMA_DIR = PROJECT_ROOT / "data" / "session_chroma"  # per-session vector DBs

# ── Datasets ───────────────────────────────────────────────────────────────────
PIMA_CSV   = RAW_DATA_DIR / "diabetes.csv"        # PIMA Indians (v2)
UCI130_CSV = RAW_DATA_DIR / "diabetic_data.csv"   # UCI 130-US Hospitals (v3)

# ── v2 artifacts — diabetes risk (PIMA) ────────────────────────────────────────
V2_MODEL     = MODELS_V2_DIR / "diabetes_model_v2.pkl"
V2_SCALER    = MODELS_V2_DIR / "scaler_v2.pkl"
V2_EXPLAINER = MODELS_V2_DIR / "shap_explainer.pkl"
V2_FEATURES  = MODELS_V2_DIR / "feature_names_v2.json"

# ── v3 artifacts — complication / readmission risk (UCI-130) ───────────────────
V3_MODEL     = MODELS_V3_DIR / "diabetes_model_v3.pkl"
V3_SCALER    = MODELS_V3_DIR / "scaler_v3.pkl"
V3_EXPLAINER = MODELS_V3_DIR / "shap_explainer_v3.pkl"
V3_FEATURES  = MODELS_V3_DIR / "feature_names_v3.json"


def ensure_dirs() -> None:
    """Create the output directories that training runs write into."""
    for directory in (MODELS_V2_DIR, MODELS_V3_DIR, FIGURES_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def ensure_upload_dirs() -> None:
    """Create upload and session-chroma directories on startup."""
    for directory in (UPLOADS_DIR, SESSION_CHROMA_DIR):
        directory.mkdir(parents=True, exist_ok=True)

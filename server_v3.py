"""
server_v3.py
────────────────────────────────────────────────────────────────────────────
MediStore AI — FastAPI backend for the Diabetes Complication Risk Predictor
Model  : XGBoost + LightGBM + Random Forest ensemble  (diabetes_model_v3.pkl)
Dataset: UCI Diabetes 130-US Hospitals (101 766 records)
Target : Early hospital readmission (<30 days) — proxy for poor glycaemic
         control and complication risk
Port   : 8001  (v2 SVM model runs on 8000)
────────────────────────────────────────────────────────────────────────────

Run with:
    python server_v3.py
    # or
    uvicorn server_v3:app --port 8001 --reload
"""

import base64
import io
import json
import os

import joblib
import matplotlib
import numpy as np
import shap

matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(title="MediStore AI — Complication Risk Predictor (v3)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load artifacts ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    model    = joblib.load(os.path.join(BASE_DIR, "diabetes_model_v3.pkl"))
    scaler   = joblib.load(os.path.join(BASE_DIR, "scaler_v3.pkl"))
    explainer = joblib.load(os.path.join(BASE_DIR, "shap_explainer_v3.pkl"))
    with open(os.path.join(BASE_DIR, "feature_names_v3.json")) as f:
        feature_names: list[str] = json.load(f)
    print("✅ v3 model artifacts loaded successfully!")
    print(f"   Features : {len(feature_names)}")
except Exception as exc:
    print(f"❌ Error loading v3 artifacts: {exc}")
    model = scaler = explainer = feature_names = None  # type: ignore[assignment]


# ── Pydantic request schema ────────────────────────────────────────────────────
class ComplicationInput(BaseModel):
    # Demographics
    gender: int = 1                        # 1=Male, 0=Female
    age: int = 55                          # ordinal midpoint (5,15,...,95)

    # Hospital visit info
    admission_type_id: int = 1
    discharge_disposition_id: int = 1
    admission_source_id: int = 7
    time_in_hospital: int = 3

    # Procedures & labs
    num_lab_procedures: int = 40
    num_procedures: int = 1
    num_medications: int = 15
    number_outpatient: int = 0
    number_emergency: int = 0
    number_inpatient: int = 0
    diag_1: int = 3                        # ICD-9 category (0-17)
    diag_2: int = 3
    diag_3: int = 7
    number_diagnoses: int = 9

    # Lab results (ordinal)
    max_glu_serum: int = 0                 # 0=None,1=Norm,2=>200,3=>300
    a1cresult: int = 0                     # 0=None,1=Norm,2=>7,3=>8

    # Key medications (0=No,1=Steady,2=Up,-1=Down)
    metformin: int = 0
    repaglinide: int = 0
    nateglinide: int = 0
    chlorpropamide: int = 0
    glimepiride: int = 0
    acetohexamide: int = 0
    glipizide: int = 0
    glyburide: int = 0
    tolbutamide: int = 0
    pioglitazone: int = 0
    rosiglitazone: int = 0
    acarbose: int = 0
    miglitol: int = 0
    troglitazone: int = 0
    tolazamide: int = 0
    insulin: int = 1
    glyburide_metformin: int = 0
    glipizide_metformin: int = 0
    glimepiride_pioglitazone: int = 0
    metformin_rosiglitazone: int = 0
    metformin_pioglitazone: int = 0

    # Flags
    change: int = 0                        # 1=medication changed, 0=no change
    diabetesmed: int = 1                   # 1=Yes, 0=No

    # Race (one-hot — at most one = 1)
    race_Asian: int = 0
    race_Caucasian: int = 1
    race_Hispanic: int = 0
    race_Other: int = 0


# ── Helpers ────────────────────────────────────────────────────────────────────
def build_feature_vector(d: ComplicationInput) -> np.ndarray:
    """
    Reconstruct the exact feature order expected by the v3 model.
    Matches feature_names_v3.json and engineer_features() in data_preprocessing_uci130.py.
    """
    # Engineered features
    med_procedure_ratio = d.num_medications / (d.num_procedures + 1)
    hospital_complexity = d.number_inpatient + d.number_emergency * 2
    total_prior_visits  = d.number_outpatient + d.number_inpatient
    multi_diag_endocrine = int(d.diag_1 == 3) + int(d.diag_2 == 3)
    is_emergency_admission = int(d.admission_source_id == 7)
    long_stay = int(d.time_in_hospital > 7)

    row = [
        d.gender,
        d.age,
        d.admission_type_id,
        d.discharge_disposition_id,
        d.admission_source_id,
        d.time_in_hospital,
        d.num_lab_procedures,
        d.num_procedures,
        d.num_medications,
        d.number_outpatient,
        d.number_emergency,
        d.number_inpatient,
        d.diag_1,
        d.diag_2,
        d.diag_3,
        d.number_diagnoses,
        d.max_glu_serum,
        d.a1cresult,
        d.metformin,
        d.repaglinide,
        d.nateglinide,
        d.chlorpropamide,
        d.glimepiride,
        d.acetohexamide,
        d.glipizide,
        d.glyburide,
        d.tolbutamide,
        d.pioglitazone,
        d.rosiglitazone,
        d.acarbose,
        d.miglitol,
        d.troglitazone,
        d.tolazamide,
        d.insulin,
        d.glyburide_metformin,       # 'glyburide-metformin' → field renamed for Pydantic
        d.glipizide_metformin,
        d.glimepiride_pioglitazone,
        d.metformin_rosiglitazone,
        d.metformin_pioglitazone,
        d.change,
        d.diabetesmed,
        d.race_Asian,
        d.race_Caucasian,
        d.race_Hispanic,
        d.race_Other,
        med_procedure_ratio,
        hospital_complexity,
        total_prior_visits,
        multi_diag_endocrine,
        is_emergency_admission,
        long_stay,
    ]
    return np.array([row], dtype=float)


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/")
def health():
    return {"status": "MediStore AI v3 API is running", "features": len(feature_names) if feature_names else 0}


@app.post("/predict_v3")
def predict_v3(data: ComplicationInput):
    if model is None:
        raise HTTPException(status_code=500, detail="v3 model artifacts are not loaded.")

    try:
        # Build & scale feature vector
        X = build_feature_vector(data)
        X_scaled = scaler.transform(X)

        # Predict
        prediction = int(model.predict(X_scaled)[0])
        try:
            proba    = model.predict_proba(X_scaled)[0]
            prob_neg = float(proba[0] * 100)
            prob_pos = float(proba[1] * 100)
        except Exception:
            prob_pos = 100.0 if prediction == 1 else 0.0
            prob_neg = 100.0 - prob_pos

        # SHAP waterfall plot (dark theme to match React frontend)
        plt.style.use("dark_background")
        shap_vals = explainer(X_scaled)
        shap_vals.feature_names = feature_names

        fig_shap, _ = plt.subplots(figsize=(7, 5))
        shap.plots.waterfall(shap_vals[0], max_display=12, show=False)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches="tight", transparent=True)
        buf.seek(0)
        shap_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close(fig_shap)

        return {
            "prediction": prediction,
            "probability_positive": prob_pos,
            "probability_negative": prob_neg,
            "shap_image_base64": f"data:image/png;base64,{shap_b64}",
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_v3:app", host="0.0.0.0", port=8001, reload=True)

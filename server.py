import os
import io
import base64
import json
import joblib
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import shap

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MediStore AI API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models
try:
    model = joblib.load("diabetes_model_v2.pkl")
    scaler = joblib.load("scaler_v2.pkl")
    explainer = joblib.load("shap_explainer.pkl")
    with open("feature_names_v2.json") as f:
        feature_names = json.load(f)
    print("✅ Models and artifacts loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    model, scaler, explainer, feature_names = None, None, None, None


class PatientData(BaseModel):
    pregnancies: int
    glucose: float
    blood_pressure: float
    skin_thickness: float
    insulin: float
    bmi: float
    dpf: float
    age: int

@app.get("/")
def read_root():
    return {"status": "MediStore AI API is running"}

@app.post("/predict")
def predict(data: PatientData):
    if model is None:
        raise HTTPException(status_code=500, detail="Models are not loaded.")

    try:
        # Extract base features
        pregnancies = data.pregnancies
        glucose = data.glucose
        bp = data.blood_pressure
        skin = data.skin_thickness
        insulin = data.insulin
        bmi = data.bmi
        dpf = data.dpf
        age = data.age

        # Feature Engineering (8 new features)
        glucose_bmi_ratio   = glucose / (bmi + 0.001)
        insulin_resistance  = glucose * insulin / 1000.0
        age_bmi_interaction = age * bmi
        bp_age_risk         = bp * age / 100.0
        glucose_age         = glucose * age / 100.0
        high_glucose_flag   = 1.0 if glucose > 125 else 0.0
        obese_flag          = 1.0 if bmi > 30 else 0.0
        high_risk_age_flag  = 1.0 if age > 45 else 0.0

        # Create input array (16 features)
        input_data = np.array([[
            pregnancies, glucose, bp, skin, insulin, bmi, dpf, age,
            glucose_bmi_ratio, insulin_resistance, age_bmi_interaction,
            bp_age_risk, glucose_age, high_glucose_flag, obese_flag, high_risk_age_flag
        ]])

        # Scale data
        input_std = scaler.transform(input_data)
        
        # Predict
        prediction = int(model.predict(input_std)[0])
        try:
            proba = model.predict_proba(input_std)[0]
            prob_neg = float(proba[0] * 100)
            prob_pos = float(proba[1] * 100)
        except Exception:
            prob_pos = 100.0 if prediction == 1 else 0.0
            prob_neg = 100.0 - prob_pos

        # Generate SHAP Explainability Plot
        shap_values = explainer(input_std)
        shap_values.feature_names = feature_names

        # Dark theme for the new frontend? The user wanted a "modern, professional, visually appealing UI that matches the existing background theme".
        # The previous background theme was dark. So we will generate a dark theme SHAP plot.
        plt.style.use('dark_background')
        fig_shap, ax = plt.subplots(figsize=(7, 4.5))
        
        # Waterfall plot
        shap.plots.waterfall(shap_values[0], max_display=10, show=False)
        plt.tight_layout()

        # Save plot to base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, bbox_inches='tight', transparent=True)
        buf.seek(0)
        shap_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig_shap)

        # Build response
        return {
            "prediction": prediction,
            "probability_positive": prob_pos,
            "probability_negative": prob_neg,
            "shap_image_base64": f"data:image/png;base64,{shap_base64}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

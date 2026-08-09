"""
verify_v3.py
─────────────────────────────────────────────────────────────────
Sanity-check script: loads all v3 model artifacts and runs a
test prediction to confirm everything works end-to-end.

Run from the project root AFTER training:
    python -m backend.ml.verify_v3
─────────────────────────────────────────────────────────────────
"""

import json
import sys
import numpy as np
import joblib

from backend.config import V3_MODEL, V3_SCALER, V3_EXPLAINER, V3_FEATURES

# These scripts print emoji status markers; Windows consoles default to cp1252,
# which cannot encode them and would abort the run mid-way.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 55)
print("  MediStore AI — v3 Artifact Verification")
print("=" * 55)

all_ok = True

# ── Load artifacts ─────────────────────────────────────────────
print("\n[1] Loading model artifacts...")
try:
    model         = joblib.load(V3_MODEL)
    scaler        = joblib.load(V3_SCALER)
    explainer     = joblib.load(V3_EXPLAINER)
    with open(V3_FEATURES) as f:
        feature_names = json.load(f)
    print(f"  ✅ model           : diabetes_model_v3.pkl")
    print(f"  ✅ scaler          : scaler_v3.pkl")
    print(f"  ✅ explainer       : shap_explainer_v3.pkl")
    print(f"  ✅ feature list    : feature_names_v3.json ({len(feature_names)} features)")
except FileNotFoundError as e:
    print(f"  ❌ Missing file: {e}")
    print("  → Run 'python -m backend.ml.train_v3' first to generate all artifacts.")
    sys.exit(1)

# ── Test prediction ─────────────────────────────────────────────
print("\n[2] Running a test prediction (all-zeros dummy input)...")
try:
    dummy_input  = np.zeros((1, len(feature_names)))
    dummy_scaled = scaler.transform(dummy_input)
    prediction   = model.predict(dummy_scaled)[0]
    proba        = model.predict_proba(dummy_scaled)[0]
    label        = "High-Risk (Positive)" if prediction == 1 else "Stable (Negative)"
    print(f"  ✅ Prediction  : {prediction} — {label}")
    print(f"  ✅ Probabilities: Stable={proba[0]:.4f} | High-Risk={proba[1]:.4f}")
except Exception as e:
    print(f"  ❌ Prediction failed: {e}")
    all_ok = False

# ── Test SHAP ──────────────────────────────────────────────────
print("\n[3] Testing SHAP explainer...")
try:
    shap_vals = explainer.shap_values(dummy_scaled)
    shap_arr  = np.array(shap_vals)
    print(f"  ✅ SHAP output shape: {shap_arr.shape}")
    print(f"  ✅ SHAP values sum   : {shap_vals.sum():.6f}")
except Exception as e:
    print(f"  ⚠️  SHAP test failed: {e}")
    all_ok = False

# ── Feature list preview ───────────────────────────────────────
print(f"\n[4] Feature list preview (first 15 of {len(feature_names)}):")
for i, name in enumerate(feature_names[:15]):
    print(f"  {i+1:>3}. {name}")
if len(feature_names) > 15:
    print(f"  ... and {len(feature_names) - 15} more (see feature_names_v3.json)")

# ── Final result ────────────────────────────────────────────────
print("\n" + "=" * 55)
if all_ok:
    print("  ✅ All checks passed!")
    print("  → Safe to update app.py to use v3 model files.")
else:
    print("  ⚠️  Some checks failed — review errors above.")
print("=" * 55)

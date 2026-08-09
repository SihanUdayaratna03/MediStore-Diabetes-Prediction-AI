"""
╔═══════════════════════════════════════════════════════════════╗
║  MediStore AI — UCI-130 Model Training Script                 ║
║  Version: 3.0                                                 ║
║  Dataset: UCI Diabetes 130-US Hospitals (101,766 records)     ║
║  Model: XGBoost + LightGBM + Random Forest Ensemble           ║
╚═══════════════════════════════════════════════════════════════╝

BEFORE RUNNING:
  1. Place 'diabetic_data.csv' in data/raw/
     Download from: https://archive.ics.uci.edu/dataset/296/
  2. Install dependencies:
     pip install -r requirements_uci130.txt

Run from the project root:
    python -m backend.ml.train_v3

    Or specify a different CSV path:
    python -m backend.ml.train_v3 --csv path/to/diabetic_data.csv
"""

import argparse
import json
import sys
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import shap

from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from backend.config import (
    UCI130_CSV, V3_MODEL, V3_SCALER, V3_EXPLAINER, V3_FEATURES,
    FIGURES_DIR, ensure_dirs,
)
from backend.ml.preprocessing_uci130 import preprocess

ensure_dirs()

# These scripts print emoji status markers; Windows consoles default to cp1252,
# which cannot encode them and would abort the run mid-way.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")

# ── CLI argument ───────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train MediStore UCI-130 model v3")
parser.add_argument(
    "--csv",
    default=str(UCI130_CSV),
    help="Path to the UCI-130 CSV file (default: data/raw/diabetic_data.csv)",
)
args = parser.parse_args()

# ══════════════════════════════════════════════════════════════════════════════
print("=" * 65)
print("  MediStore AI — UCI-130 Model Training v3.0")
print("=" * 65)

# ── Step 1: Load & Preprocess ──────────────────────────────────────────────────
print("\n[1/7] 📂 Loading and preprocessing UCI-130 dataset...")
df, feature_cols = preprocess(args.csv)

X = df[feature_cols].values
y = df["target"].values

print(f"\n      ✅ Features selected : {len(feature_cols)}")
print(f"      📊 Class balance     — Negative (0): {sum(y==0):,}  |  Positive (1): {sum(y==1):,}")
print(f"      📊 Positive rate     : {y.mean()*100:.1f}%  (early readmission rate)")

# ── Step 2: Train / Test Split ─────────────────────────────────────────────────
print("\n[2/7] ✂️  Splitting dataset (80% train / 20% test, stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"      Train : {len(X_train):,} samples")
print(f"      Test  : {len(X_test):,} samples")

# ── Step 3: SMOTE Balancing ────────────────────────────────────────────────────
print("\n[3/7] ⚖️  Balancing classes with SMOTE...")
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
print(f"      After SMOTE — Negative: {sum(y_train_bal==0):,}  |  Positive: {sum(y_train_bal==1):,}")

# ── Step 4: Feature Scaling ────────────────────────────────────────────────────
print("\n[4/7] 📏 Scaling features (StandardScaler)...")
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_bal)
X_test_s  = scaler.transform(X_test)
joblib.dump(scaler, V3_SCALER)
print("      ✅ Scaler saved: scaler_v3.pkl")

# ── Step 5: Build & Train Ensemble ────────────────────────────────────────────
print("\n[5/7] 🤖 Training XGBoost + LightGBM + Random Forest ensemble...")
print("      (This may take 3–8 minutes on a standard machine)")

xgb_model = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,
    reg_lambda=1.0,
    eval_metric="logloss",
    random_state=42,
    verbosity=0,
    n_jobs=-1,
)

lgbm_model = LGBMClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_samples=20,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    verbose=-1,
    n_jobs=-1,
)

rf_model = RandomForestClassifier(
    n_estimators=250,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
)

# Soft-voting ensemble — XGB and LGBM weighted higher (better calibration)
ensemble = VotingClassifier(
    estimators=[
        ("xgb",  xgb_model),
        ("lgbm", lgbm_model),
        ("rf",   rf_model),
    ],
    voting="soft",
    weights=[2, 2, 1],
)

ensemble.fit(X_train_s, y_train_bal)
print("      ✅ Ensemble training complete!")

# ── Step 6: Evaluate ──────────────────────────────────────────────────────────
print("\n[6/7] 📊 Evaluating model performance...")

y_pred      = ensemble.predict(X_test_s)
y_pred_prob = ensemble.predict_proba(X_test_s)[:, 1]
accuracy    = accuracy_score(y_test, y_pred)
auc_roc     = roc_auc_score(y_test, y_pred_prob)
cm          = confusion_matrix(y_test, y_pred)

print(f"\n      ════════════════════════════════════════════")
print(f"      Accuracy   : {accuracy * 100:.2f}%")
print(f"      AUC-ROC    : {auc_roc:.4f}")
print(f"      ════════════════════════════════════════════")
print(f"\n      Confusion Matrix:")
print(f"        TN = {cm[0,0]:>7,}   FP = {cm[0,1]:>7,}")
print(f"        FN = {cm[1,0]:>7,}   TP = {cm[1,1]:>7,}")
print(f"\n      Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Stable (0)", "High-Risk (1)"]))

# 5-Fold Cross-Validation on AUC-ROC
print("      Running 5-fold cross-validation (AUC-ROC)...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(ensemble, X_train_s, y_train_bal, cv=cv, scoring="roc_auc", n_jobs=-1)
print(f"      CV AUC-ROC : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"      CV Scores  : {[f'{s:.4f}' for s in cv_scores]}")

# ── Step 7: SHAP Explainability ───────────────────────────────────────────────
print("\n[7/7] 🔍 Computing SHAP values for explainability...")
print("      (Training standalone XGBoost for SHAP compatibility...)")

# VotingClassifier not directly supported by SHAP — use a standalone XGB
xgb_for_shap = XGBClassifier(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
    verbosity=0,
    n_jobs=-1,
)
xgb_for_shap.fit(X_train_s, y_train_bal)

explainer = shap.TreeExplainer(xgb_for_shap)

# Use a random sample of test data (computing on all 20k+ rows is slow)
np.random.seed(42)
shap_sample_idx = np.random.choice(len(X_test_s), size=min(2000, len(X_test_s)), replace=False)
X_shap = X_test_s[shap_sample_idx]
shap_values = explainer.shap_values(X_shap)

# Save SHAP feature importance bar chart (top 20 features)
plt.figure(figsize=(12, 8))
shap.summary_plot(
    shap_values,
    X_shap,
    feature_names=feature_cols,
    show=False,
    plot_type="bar",
    max_display=20,
)
plt.title("MediStore AI — Feature Importance (SHAP, UCI-130 v3)", fontsize=14, pad=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / "shap_feature_importance_v3.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close()
print("      ✅ SHAP chart saved    : shap_feature_importance_v3.png")

joblib.dump(explainer, V3_EXPLAINER)
print("      ✅ SHAP explainer saved: shap_explainer_v3.pkl")

# ── Save Main Model & Feature Names ──────────────────────────────────────────
joblib.dump(ensemble, V3_MODEL)
print("      ✅ Model saved         : diabetes_model_v3.pkl")

with open(V3_FEATURES, "w") as f:
    json.dump(feature_cols, f, indent=2)
print("      ✅ Feature list saved  : feature_names_v3.json")

# ── Final Summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  🎉 TRAINING COMPLETE!")
print("=" * 65)
print(f"  📈 Test Accuracy    : {accuracy*100:.2f}%")
print(f"  📈 Test AUC-ROC     : {auc_roc:.4f}")
print(f"  📈 CV AUC-ROC       : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"  📦 Features used    : {len(feature_cols)}")
print(f"  📦 Training rows    : {len(X_train_bal):,} (after SMOTE)")
print()
print("  📁 Output Files Created:")
print("     models/v3/diabetes_model_v3.pkl            ← Main prediction model")
print("     models/v3/scaler_v3.pkl                    ← Feature scaler")
print("     models/v3/shap_explainer_v3.pkl            ← SHAP explainability model")
print("     models/v3/feature_names_v3.json            ← Feature column list")
print("     reports/figures/shap_feature_importance_v3.png ← Feature importance chart")
print()
print("  ✅ Next Steps:")
print("     1. Run: python verify_uci130.py")
print("     2. Update app.py to load v3 model files")
print("=" * 65)

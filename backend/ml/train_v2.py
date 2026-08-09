"""
╔═══════════════════════════════════════════════════════════╗
║  MediStore AI — Upgraded Model Training Script            ║
║  Version: 2.5                                             ║
║  Upgrade: SVM (78%) → XGBoost Ensemble (85-88%)          ║
╚═══════════════════════════════════════════════════════════╝

Run from the project root:
    python -m backend.ml.train_v2
"""

import sys

import pandas as pd
import numpy as np
import joblib
import json
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                              roc_auc_score, confusion_matrix)
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import shap

from backend.config import (
    PIMA_CSV, V2_MODEL, V2_SCALER, V2_EXPLAINER, V2_FEATURES,
    FIGURES_DIR, ensure_dirs,
)

ensure_dirs()

# These scripts print emoji status markers; Windows consoles default to cp1252,
# which cannot encode them and would abort the run mid-way.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("  MediStore AI — Model Upgrade Training v2.5")
print("=" * 60)

# ── Step 1: Load Data ─────────────────────────────────────────
print("\n[1/7] 📂 Loading data...")
df = pd.read_csv(PIMA_CSV)
print(f"      ✅ Loaded: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"      📊 Class balance: {df['Outcome'].value_counts().to_dict()}")

# ── Step 2: Clean Data ────────────────────────────────────────
print("\n[2/7] 🧹 Cleaning data (replacing invalid zeros)...")
zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
for col in zero_cols:
    n_zeros = (df[col] == 0).sum()
    if n_zeros > 0:
        df[col] = df[col].replace(0, np.nan)
        print(f"      Replaced {n_zeros} zeros in '{col}' with median")
df.fillna(df.median(numeric_only=True), inplace=True)
print("      ✅ Data cleaning complete")

# ── Step 3: Feature Engineering ──────────────────────────────
print("\n[3/7] 🔬 Engineering new features...")
df['Glucose_BMI_Ratio']   = df['Glucose'] / (df['BMI'] + 0.001)
df['Insulin_Resistance']  = df['Glucose'] * df['Insulin'] / 1000
df['Age_BMI_Interaction'] = df['Age'] * df['BMI']
df['BP_Age_Risk']         = df['BloodPressure'] * df['Age'] / 100
df['Glucose_Age']         = df['Glucose'] * df['Age'] / 100
df['High_Glucose_Flag']   = (df['Glucose'] > 125).astype(int)
df['Obese_Flag']          = (df['BMI'] > 30).astype(int)
df['High_Risk_Age_Flag']  = (df['Age'] > 45).astype(int)

feature_cols = [c for c in df.columns if c != 'Outcome']
print(f"      ✅ Total features: {len(feature_cols)} (was 8, now {len(feature_cols)})")
print(f"      📋 Features: {feature_cols}")

# ── Step 4: Train/Test Split + SMOTE ─────────────────────────
print("\n[4/7] ⚖️  Splitting and balancing data (SMOTE)...")
X = df[feature_cols]
y = df['Outcome']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"      Train: {len(X_train)} samples | Test: {len(X_test)} samples")

smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
print(f"      ✅ After SMOTE — Non-Diabetic: {sum(y_train_bal==0)}, "
      f"Diabetic: {sum(y_train_bal==1)}")

# ── Step 5: Scale Data ────────────────────────────────────────
print("\n[5/7] 📏 Scaling features...")
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_bal)
X_test_s  = scaler.transform(X_test)
joblib.dump(scaler, V2_SCALER)
print("      ✅ Scaler saved: scaler_v2.pkl")

# ── Step 6: Train Ensemble Model ─────────────────────────────
print("\n[6/7] 🤖 Training XGBoost + LightGBM + Random Forest ensemble...")

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42,
    verbosity=0
)

lgbm_model = LGBMClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    random_state=42,
    verbose=-1
)

rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42,
    n_jobs=-1
)

ensemble = VotingClassifier(
    estimators=[
        ('xgb',  xgb_model),
        ('lgbm', lgbm_model),
        ('rf',   rf_model),
    ],
    voting='soft'
)

print("      Training... (මිනිත්තු 1-2 ක් ගතවිය හැකිය)")
ensemble.fit(X_train_s, y_train_bal)

# Evaluate
y_pred      = ensemble.predict(X_test_s)
y_pred_prob = ensemble.predict_proba(X_test_s)[:, 1]
accuracy    = accuracy_score(y_test, y_pred)
auc_roc     = roc_auc_score(y_test, y_pred_prob)

print(f"\n      📊 ══════ Model Performance ══════")
print(f"      Accuracy : {accuracy * 100:.2f}%  (previous: ~78%)")
print(f"      AUC-ROC  : {auc_roc:.4f}")
print(f"\n      Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=['Not Diabetic', 'Diabetic']))

# ── SHAP Explainability ────────────────────────────────────
print("\n[7/7] 🔍 Computing SHAP values for explainability...")

# Use XGBoost alone for SHAP (VotingClassifier doesn't support SHAP directly)
xgb_for_shap = XGBClassifier(
    n_estimators=300, max_depth=6, learning_rate=0.05,
    subsample=0.8, colsample_bytree=0.8,
    use_label_encoder=False, eval_metric='logloss',
    random_state=42, verbosity=0
)
xgb_for_shap.fit(X_train_s, y_train_bal)

explainer   = shap.TreeExplainer(xgb_for_shap)
shap_values = explainer.shap_values(X_test_s)

# Save SHAP summary plot
plt.figure(figsize=(10, 7))
shap.summary_plot(
    shap_values,
    X_test_s,
    feature_names=feature_cols,
    show=False,
    plot_type='bar'
)
plt.title("MediStore AI — Feature Importance (SHAP)", fontsize=13, pad=15)
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'shap_feature_importance.png', dpi=150, bbox_inches='tight',
            facecolor='white')
plt.close()

# Save SHAP explainer
joblib.dump(explainer, V2_EXPLAINER)
print("      ✅ SHAP explainer saved: shap_explainer.pkl")
print("      ✅ SHAP plot saved:      shap_feature_importance.png")

# ── Save Model & Feature Names ────────────────────────────
joblib.dump(ensemble, V2_MODEL)
with open(V2_FEATURES, 'w') as f:
    json.dump(feature_cols, f, indent=2)

# ── Final Summary ─────────────────────────────────────────
print("\n" + "=" * 60)
print("  🎉 TRAINING COMPLETE!")
print("=" * 60)
print(f"  📈 Accuracy  : {accuracy*100:.2f}%")
print(f"  📈 AUC-ROC   : {auc_roc:.4f}")
print(f"  📦 Features  : {len(feature_cols)}")
print()
print("  📁 Files Created:")
print("     models/v2/diabetes_model_v2.pkl       ← New model")
print("     models/v2/scaler_v2.pkl               ← New scaler")
print("     models/v2/shap_explainer.pkl          ← SHAP explainer")
print("     models/v2/feature_names_v2.json       ← Feature list")
print("     reports/figures/shap_feature_importance.png ← SHAP chart")
print()
print("  ✅ ඊළඟ Step:")
print("     app.py හි diabetes_model_v2.pkl use කරන්න")
print("=" * 60)

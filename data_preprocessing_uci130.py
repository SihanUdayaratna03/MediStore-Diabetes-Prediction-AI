"""
data_preprocessing_uci130.py
─────────────────────────────────────────────────────────────────
Cleans and prepares the UCI Diabetes 130-US Hospitals dataset.
Called by train_uci130.py — do not run standalone.

Dataset: https://archive.ics.uci.edu/dataset/296/
─────────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np


# ── Column name normalisation ──────────────────────────────────────────────────
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace from all column names and lowercase them."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


# ── Replace missing-value placeholders ────────────────────────────────────────
def replace_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    UCI-130 uses '?' as a missing value marker.
    Replace with NaN throughout.
    """
    df = df.replace("?", np.nan)
    return df


# ── Drop low-value / high-cardinality columns ─────────────────────────────────
DROP_COLUMNS = [
    "encounter_id",      # unique row identifier — no signal
    "patient_nbr",       # patient identifier — no signal
    "examide",           # near-zero variance
    "citoglipton",       # near-zero variance
    "weight",            # ~97% missing
    "payer_code",        # ~40% missing, not clinically relevant
    "medical_specialty", # ~49% missing
]


def drop_low_value_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_drop = [c for c in DROP_COLUMNS if c in df.columns]
    df = df.drop(columns=cols_to_drop)
    print(f"      Dropped {len(cols_to_drop)} low-value columns: {cols_to_drop}")
    return df


# ── Encode the target variable ────────────────────────────────────────────────
def encode_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map 'readmitted' to binary:
        '<30'  → 1  (high-risk: early readmission = poor diabetes management)
        '>30'  → 0  (low-risk: late or no readmission)
        'NO'   → 0  (low-risk)

    Clinical interpretation:
        1 = Diabetic patient with poor glycaemic control (early readmission risk)
        0 = Stable / well-managed diabetic patient
    """
    df["target"] = (df["readmitted"] == "<30").astype(int)
    df = df.drop(columns=["readmitted"])
    print(f"      Target class balance: {df['target'].value_counts().to_dict()}")
    return df


# ── Encode categorical columns ────────────────────────────────────────────────
def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Binary / ordinal encodings for key categorical features.
    All remaining object columns are one-hot encoded (drop_first=True).
    """
    # Gender
    if "gender" in df.columns:
        df["gender"] = df["gender"].map({"Male": 1, "Female": 0, "Unknown/Invalid": np.nan})

    # Age brackets → ordinal midpoint value
    age_map = {
        "[0-10)": 5,   "[10-20)": 15, "[20-30)": 25, "[30-40)": 35,
        "[40-50)": 45, "[50-60)": 55, "[60-70)": 65, "[70-80)": 75,
        "[80-90)": 85, "[90-100)": 95
    }
    if "age" in df.columns:
        df["age"] = df["age"].map(age_map)

    # Change in medication flag
    if "change" in df.columns:
        df["change"] = df["change"].map({"Ch": 1, "No": 0})

    # Diabetes medication flag
    if "diabetesmed" in df.columns:
        df["diabetesmed"] = df["diabetesmed"].map({"Yes": 1, "No": 0})

    # Medication dosage columns: "Up", "Down", "Steady", "No"
    med_cols = [
        "metformin", "repaglinide", "nateglinide", "chlorpropamide",
        "glimepiride", "acetohexamide", "glipizide", "glyburide",
        "tolbutamide", "pioglitazone", "rosiglitazone", "acarbose",
        "miglitol", "troglitazone", "tolazamide", "glyburide-metformin",
        "glipizide-metformin", "glimepiride-pioglitazone",
        "metformin-rosiglitazone", "metformin-pioglitazone", "insulin"
    ]
    med_map = {"No": 0, "Steady": 1, "Up": 2, "Down": -1}
    for col in med_cols:
        if col in df.columns:
            df[col] = df[col].map(med_map).fillna(0).astype(int)

    # One-hot encode remaining object columns
    obj_cols = df.select_dtypes(include="object").columns.tolist()
    obj_cols = [c for c in obj_cols if c != "target"]
    if obj_cols:
        df = pd.get_dummies(df, columns=obj_cols, drop_first=True, dtype=int)
        print(f"      One-hot encoded: {obj_cols}")

    return df


# ── ICD-9 Diagnosis grouping ──────────────────────────────────────────────────
def group_icd9(code) -> int:
    """Map an ICD-9 code string to a broad disease category integer (0-17)."""
    if pd.isna(code):
        return 0
    code_str = str(code).strip().upper()
    if code_str.startswith("V") or code_str.startswith("E"):
        return 8
    try:
        num = float(code_str)
    except ValueError:
        return 0

    if   1   <= num <= 139:  return 1   # Infectious / Parasitic
    elif 140 <= num <= 239:  return 2   # Neoplasms
    elif 240 <= num <= 279:  return 3   # Endocrine / Nutritional / Metabolic ← diabetes
    elif 280 <= num <= 289:  return 4   # Blood diseases
    elif 290 <= num <= 319:  return 5   # Mental disorders
    elif 320 <= num <= 389:  return 6   # Nervous system
    elif 390 <= num <= 459:  return 7   # Circulatory system
    elif 460 <= num <= 519:  return 8   # Respiratory
    elif 520 <= num <= 579:  return 9   # Digestive
    elif 580 <= num <= 629:  return 10  # Genitourinary
    elif 630 <= num <= 679:  return 11  # Pregnancy / Childbirth
    elif 680 <= num <= 709:  return 12  # Skin
    elif 710 <= num <= 739:  return 13  # Musculoskeletal
    elif 740 <= num <= 759:  return 14  # Congenital anomalies
    elif 760 <= num <= 779:  return 15  # Perinatal
    elif 780 <= num <= 799:  return 16  # Symptoms / Ill-defined
    elif 800 <= num <= 999:  return 17  # Injury / Poisoning
    return 0


def encode_diagnoses(df: pd.DataFrame) -> pd.DataFrame:
    """Replace raw ICD-9 code strings with disease-category integers."""
    for col in ["diag_1", "diag_2", "diag_3"]:
        if col in df.columns:
            df[col] = df[col].apply(group_icd9)
    return df


# ── A1c and glucose serum encoding ───────────────────────────────────────────
def encode_lab_results(df: pd.DataFrame) -> pd.DataFrame:
    """Ordinal-encode A1c result and max glucose serum columns."""
    if "a1cresult" in df.columns:
        a1c_map = {">8": 3, ">7": 2, "Norm": 1, "None": 0}
        df["a1cresult"] = df["a1cresult"].map(a1c_map).fillna(0).astype(int)

    if "max_glu_serum" in df.columns:
        glu_map = {">300": 3, ">200": 2, "Norm": 1, "None": 0}
        df["max_glu_serum"] = df["max_glu_serum"].map(glu_map).fillna(0).astype(int)

    return df


# ── Feature engineering ───────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create domain-driven features from existing columns."""

    # Ratio of medications to procedures (proxy for treatment intensity)
    if "num_medications" in df.columns and "num_procedures" in df.columns:
        df["med_procedure_ratio"] = (
            df["num_medications"] / (df["num_procedures"] + 1)
        )

    # Hospital complexity: weighted combination of inpatient + emergency visits
    if "number_inpatient" in df.columns and "number_emergency" in df.columns:
        df["hospital_complexity"] = (
            df["number_inpatient"] + df["number_emergency"] * 2
        )

    # Total number of prior visits
    if "number_outpatient" in df.columns and "number_inpatient" in df.columns:
        df["total_prior_visits"] = (
            df["number_outpatient"].fillna(0) +
            df["number_inpatient"].fillna(0)
        )

    # Is this an endocrine-related (diabetes) primary or secondary diagnosis?
    if "diag_1" in df.columns and "diag_2" in df.columns:
        df["multi_diag_endocrine"] = (
            (df["diag_1"] == 3).astype(int) +
            (df["diag_2"] == 3).astype(int)
        )

    # Emergency admission flag (admission_source_id == 7 is Emergency Room)
    if "admission_source_id" in df.columns:
        df["is_emergency_admission"] = (
            df["admission_source_id"] == 7
        ).astype(int)

    # Long hospital stay flag (> 7 days)
    if "time_in_hospital" in df.columns:
        df["long_stay"] = (df["time_in_hospital"] > 7).astype(int)

    return df


# ── Handle remaining missing values ───────────────────────────────────────────
def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill numeric NaNs with column median."""
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            df[col] = df[col].fillna(df[col].median())
    return df


# ── Master pipeline ───────────────────────────────────────────────────────────
def preprocess(csv_path: str) -> tuple:
    """
    Full preprocessing pipeline for the UCI-130 dataset.

    Parameters:
        csv_path (str): Path to diabetic_data.csv

    Returns:
        df          (pd.DataFrame): Cleaned DataFrame with 'target' column
        feature_cols (list[str]):   List of feature column names
    """
    print(f"\n  Loading CSV: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    print(f"  Raw shape: {df.shape}")

    # Run pipeline stages in order
    df = normalize_columns(df)
    df = replace_missing_values(df)
    df = drop_low_value_columns(df)
    df = encode_target(df)
    df = encode_lab_results(df)
    df = encode_diagnoses(df)
    df = encode_categoricals(df)
    df = engineer_features(df)
    df = impute_missing(df)

    # Keep only numeric columns (safety net)
    df = df.select_dtypes(include=[np.number])

    feature_cols = [c for c in df.columns if c != "target"]
    print(f"  Final shape: {df.shape} | Features: {len(feature_cols)}")
    return df, feature_cols

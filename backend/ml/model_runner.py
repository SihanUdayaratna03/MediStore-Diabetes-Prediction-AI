"""
model_runner.py
===============
Reusable ML prediction functions extracted from the API servers.
Intended for internal use by other backend modules.

Currently the prediction logic lives directly in:
  - backend/api/v2_server.py  (PIMA SVM model)
  - backend/api/v3_server.py  (UCI-130 Ensemble)

This module provides a clean interface if you want to call predictions
from within the RAG pipeline (e.g., to enrich patient context automatically).
"""

import joblib

from backend.config import V2_MODEL, V2_SCALER, V3_MODEL, V3_SCALER


def load_v2_artifacts():
    """Load v2 (PIMA SVM) model artifacts."""
    model  = joblib.load(V2_MODEL)
    scaler = joblib.load(V2_SCALER)
    return model, scaler


def load_v3_artifacts():
    """Load v3 (UCI-130 Ensemble) model artifacts."""
    model  = joblib.load(V3_MODEL)
    scaler = joblib.load(V3_SCALER)
    return model, scaler

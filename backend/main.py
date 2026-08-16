"""
MediStore RAG Backend — Uvicorn Entry Point
============================================
The CORRECT entry point for the RAG backend.

Run from the project root:
    uvicorn backend.main:app --reload --port 8002

Or with explicit host:
    uvicorn backend.main:app --host 0.0.0.0 --port 8002 --reload

Ports:
    8000 — v2 SVM prediction server  (backend.api.v2_server:app)
    8001 — v3 Ensemble server        (backend.api.v3_server:app)
    8002 — RAG Multi-Agent server    (backend.main:app)  ← THIS FILE
"""

from backend.app.main import create_app

app = create_app()

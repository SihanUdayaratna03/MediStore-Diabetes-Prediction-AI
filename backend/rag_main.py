"""
MediStore RAG Backend — Uvicorn Entry Point
============================================

Runs on port 8002 (ports 8000 and 8001 are used by the v2/v3 ML servers).

Start the server from the project root:
    uvicorn backend.main:app --reload --port 8002

Or with explicit host binding:
    uvicorn backend.main:app --host 0.0.0.0 --port 8002 --reload
"""

from backend.app.main import create_app

# Create the FastAPI application instance
app = create_app()

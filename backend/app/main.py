"""
FastAPI application factory for the MediStore Multi-Agent RAG backend (v2).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path

from backend.app.api.routes import router as api_router
from backend.config import UPLOADS_DIR, ensure_upload_dirs


def create_app() -> FastAPI:
    ensure_upload_dirs()

    app = FastAPI(
        title="MediStore AI — Multi-Agent RAG API v2",
        description=(
            "Multi-Agent RAG API supporting medical document upload, "
            "PDF/image understanding, and citation-aware Q&A.\n\n"
            "**Agent pipeline**: Orchestrator → Researcher (MCP) → "
            "Reasoning → Analyst (Gemini) → Guardrail"
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── API Routes ─────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    return app

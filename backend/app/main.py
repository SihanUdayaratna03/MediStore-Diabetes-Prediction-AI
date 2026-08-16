"""
FastAPI application factory for the MediStore Multi-Agent RAG backend.

Creates the FastAPI app, registers middleware, and mounts API routes.
Imported by backend/main.py for the uvicorn entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from backend.app.api.routes import router as api_router


def create_app() -> FastAPI:
    """
    Constructs and configures the FastAPI application instance.

    Returns:
        A fully configured FastAPI app ready to serve.
    """
    app = FastAPI(
        title="MediStore AI — Multi-Agent RAG API",
        description=(
            "Multi-Agent RAG API for the MediStore Diabetes Prediction System.\n"
            "Powered by LangGraph, Google Gemini 1.5 Flash, and ChromaDB.\n\n"
            "**Agent pipeline**: Orchestrator → Researcher (MCP) → Analyst (Gemini)"
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────────────────────────
    # Allow the React dev server (Vite default: 5173) and production origins.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server
            "http://localhost:3000",   # Alternative React port
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── GZip compression for large AI responses ───────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── API Routes ────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    return app

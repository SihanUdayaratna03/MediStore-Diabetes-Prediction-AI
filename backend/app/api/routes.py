"""
FastAPI route definitions for the Multi-Agent RAG system.

Endpoints:
  POST /api/v1/chat     — Main RAG chat endpoint (orchestrator → researcher → analyst)
  GET  /api/v1/health   — Health check for the RAG backend
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.graph import rag_graph

router = APIRouter()


# ── Pydantic Models ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query:           str           = Field(..., min_length=1, max_length=2000,
                                          description="The user's question or clinical query.")
    patient_context: Optional[str] = Field(
        None,
        description=(
            "Pre-formatted patient prediction context string. "
            "Pass the patient data returned from the /predict endpoint here."
        ),
    )


class ChatResponse(BaseModel):
    response:    str
    steps_taken: list[str]
    error:       Optional[str] = None


# ── Endpoints ───────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, tags=["RAG"])
async def chat_endpoint(request: ChatRequest):
    """
    Main Multi-Agent RAG endpoint.

    Invokes the full LangGraph pipeline:
      orchestrator → researcher (MCP/ChromaDB) → analyst (Gemini) → response

    The optional ``patient_context`` field lets the frontend pass structured
    prediction data so the analyst can ground its response in the patient's
    actual biomarkers.
    """
    try:
        result = await rag_graph.ainvoke({
            "user_query":      request.query,
            "patient_context": request.patient_context or "",
            "retrieved_docs":  None,
            "final_response":  None,
            "error":           None,
            "steps_taken":     [],
        })

        return ChatResponse(
            response    = result.get("final_response", "No response generated."),
            steps_taken = result.get("steps_taken", []),
            error       = result.get("error"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent pipeline failed: {str(e)}",
        )


@router.get("/health", tags=["System"])
async def health_check():
    """Quick health check — confirms the RAG service is running."""
    return {
        "status":  "ok",
        "service": "MediStore RAG API",
        "version": "1.0.0",
    }

"""
FastAPI route definitions for the Multi-Agent RAG system (v2).

Endpoints:
  POST   /api/v1/chat              — Standard RAG chat (original, unchanged behavior)
  POST   /api/v1/upload            — Upload medical PDF or image
  POST   /api/v1/doc-chat          — Chat about an uploaded document
  GET    /api/v1/session/{id}      — Get session/document info
  DELETE /api/v1/session/{id}      — Delete a session and clean up files
  GET    /api/v1/health            — Health check
"""

import uuid
import shutil
import aiofiles
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from backend.app.graph import rag_graph
from backend.rag.document_processor import process_upload
from backend.rag.chunker import chunk_document
from backend.rag.vector_store import SessionVectorStore
from backend.rag.session_store import session_store
from backend.config import UPLOADS_DIR, SESSION_CHROMA_DIR, ensure_upload_dirs

router = APIRouter()

# Ensure directories exist
ensure_upload_dirs()

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}
MAX_FILE_SIZE_MB   = 25

# ── Pydantic Models ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query:           str           = Field(..., min_length=1, max_length=2000)
    patient_context: Optional[str] = Field(None)


class DocChatRequest(BaseModel):
    session_id:           str           = Field(..., description="Session ID from /upload")
    query:                str           = Field(..., min_length=1, max_length=2000)
    conversation_history: List[dict]    = Field(default_factory=list)
    patient_context:      Optional[str] = Field(None)


class CitationRef(BaseModel):
    chunk_index:  int
    page_number:  int | str
    filename:     str
    text_snippet: str
    similarity:   float
    chunk_id:     str


class ChatResponse(BaseModel):
    response:    str
    steps_taken: list[str]
    error:       Optional[str] = None


class DocChatResponse(BaseModel):
    response:    str
    steps_taken: list[str]
    citations:   list[CitationRef] = []
    error:       Optional[str] = None


class UploadResponse(BaseModel):
    session_id:        str
    filename:          str
    doc_type:          str
    total_pages:       int
    chunk_count:       int
    preview_text:      str
    extraction_method: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, tags=["RAG Chat"])
async def chat_endpoint(request: ChatRequest):
    """Standard Multi-Agent RAG chat (no document context)."""
    try:
        result = await rag_graph.ainvoke({
            "user_query":           request.query,
            "patient_context":      request.patient_context or "",
            "session_id":           None,
            "doc_mode":             False,
            "doc_context":          None,
            "citations":            [],
            "conversation_history": [],
            "retrieved_docs":       None,
            "reasoning_trace":      None,
            "final_response":       None,
            "error":                None,
            "steps_taken":          [],
        })
        return ChatResponse(
            response    = result.get("final_response", "No response generated."),
            steps_taken = result.get("steps_taken", []),
            error       = result.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {str(e)}")


@router.post("/upload", response_model=UploadResponse, tags=["Document"])
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a medical PDF or image for question-answering.

    Returns a session_id that must be passed to /doc-chat for follow-up questions.
    The session is valid for 24 hours.
    """
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. "
                   f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Generate a pre-session ID for the upload directory
    temp_session_id = str(uuid.uuid4())
    upload_dir      = UPLOADS_DIR / temp_session_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path       = upload_dir / file.filename

    # Save uploaded file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                shutil.rmtree(upload_dir, ignore_errors=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
                )
            await f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")

    # Extract text from the document
    try:
        doc_content = process_upload(file_path, file.filename)
    except ValueError as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    # Chunk the document
    chunks = chunk_document(doc_content, session_id=temp_session_id)

    # Build session vector store
    chroma_path = SESSION_CHROMA_DIR / temp_session_id
    chroma_path.mkdir(parents=True, exist_ok=True)
    try:
        vec_store = SessionVectorStore(
            session_id  = temp_session_id,
            chroma_path = str(chroma_path),
        )
        vec_store.add_chunks(chunks)
    except Exception as e:
        shutil.rmtree(upload_dir, ignore_errors=True)
        shutil.rmtree(chroma_path, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Vector store creation failed: {str(e)}")

    # Register session
    session_id = session_store.create_session(
        filename     = file.filename,
        doc_type     = doc_content.doc_type,
        total_pages  = doc_content.total_pages,
        preview_text = doc_content.preview_text,
        chunk_count  = len(chunks),
        file_path    = file_path,
        chroma_path  = chroma_path,
    )

    # Rename the upload dir to the real session_id
    new_upload_dir = UPLOADS_DIR / session_id
    upload_dir.rename(new_upload_dir)

    return UploadResponse(
        session_id        = session_id,
        filename          = file.filename,
        doc_type          = doc_content.doc_type,
        total_pages       = doc_content.total_pages,
        chunk_count       = len(chunks),
        preview_text      = doc_content.preview_text,
        extraction_method = doc_content.extraction_method,
    )


@router.post("/doc-chat", response_model=DocChatResponse, tags=["Document"])
async def doc_chat_endpoint(request: DocChatRequest):
    """
    Ask a question about an uploaded document.

    Pass the session_id from /upload and the conversation_history for memory.
    """
    # Validate session
    session_info = session_store.get(request.session_id)
    if not session_info:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-upload your document."
        )

    try:
        result = await rag_graph.ainvoke({
            "user_query":           request.query,
            "patient_context":      request.patient_context or "",
            "session_id":           request.session_id,
            "doc_mode":             True,
            "doc_context":          None,
            "citations":            [],
            "conversation_history": request.conversation_history,
            "retrieved_docs":       None,
            "reasoning_trace":      None,
            "final_response":       None,
            "error":                None,
            "steps_taken":          [],
        })

        # Retrieve citations from vector store
        citations = []
        try:
            chroma_path = str(SESSION_CHROMA_DIR / request.session_id)
            vec_store   = SessionVectorStore(
                session_id  = request.session_id,
                chroma_path = chroma_path,
            )
            _, citations = vec_store.format_for_agent(request.query, n_results=5)
        except Exception:
            pass   # citations are optional — don't fail the response

        return DocChatResponse(
            response    = result.get("final_response", "No response generated."),
            steps_taken = result.get("steps_taken", []),
            citations   = [CitationRef(**c) for c in citations],
            error       = result.get("error"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document chat failed: {str(e)}")


@router.get("/session/{session_id}", tags=["Document"])
async def get_session(session_id: str):
    """Get information about an uploaded document session."""
    session_info = session_store.get(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return session_info.to_dict()


@router.delete("/session/{session_id}", tags=["Document"])
async def delete_session(session_id: str):
    """Delete a document session and clean up all associated files."""
    session_info = session_store.get(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Clean up files
    upload_dir  = UPLOADS_DIR / session_id
    chroma_path = SESSION_CHROMA_DIR / session_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)
    if chroma_path.exists():
        shutil.rmtree(chroma_path, ignore_errors=True)

    session_store.delete(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.get("/health", tags=["System"])
async def health_check():
    """Health check — confirms the RAG service is running."""
    return {
        "status":   "ok",
        "service":  "MediStore RAG API",
        "version":  "2.0.0",
        "features": ["chat", "document-upload", "multimodal-ocr", "citation-tracking"],
    }

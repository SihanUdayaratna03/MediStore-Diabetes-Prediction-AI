"""
session_store.py
================
In-memory session registry for uploaded document sessions.

Each session entry records:
  - session_id
  - original filename and document type
  - total pages and chunk count
  - preview text (first ~300 chars)
  - file and chroma paths for cleanup
  - creation timestamp (for TTL enforcement)

Sessions expire after SESSION_TTL_HOURS (default: 24h).
"""

import uuid
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Dict


# ── Configuration ──────────────────────────────────────────────────────────────
SESSION_TTL_HOURS = 24


# ── Session entry ──────────────────────────────────────────────────────────────

@dataclass
class SessionInfo:
    """All metadata associated with an uploaded document session."""
    session_id:   str
    filename:     str
    doc_type:     str           # "pdf" | "image"
    total_pages:  int
    chunk_count:  int
    preview_text: str
    file_path:    Path
    chroma_path:  Path
    created_at:   datetime = field(default_factory=datetime.utcnow)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(hours=SESSION_TTL_HOURS)

    def to_dict(self) -> dict:
        return {
            "session_id":   self.session_id,
            "filename":     self.filename,
            "doc_type":     self.doc_type,
            "total_pages":  self.total_pages,
            "chunk_count":  self.chunk_count,
            "preview_text": self.preview_text,
            "created_at":   self.created_at.isoformat(),
            "expires_at":   (self.created_at + timedelta(hours=SESSION_TTL_HOURS)).isoformat(),
        }


# ── Session store ──────────────────────────────────────────────────────────────

class SessionStore:
    """
    Thread-safe in-memory store for document upload sessions.
    Auto-expires sessions older than SESSION_TTL_HOURS.
    """

    def __init__(self) -> None:
        self._store: Dict[str, SessionInfo] = {}
        self._lock  = threading.Lock()

    def create_session(
        self,
        filename:     str,
        doc_type:     str,
        total_pages:  int,
        preview_text: str,
        chunk_count:  int,
        file_path:    Path,
        chroma_path:  Path,
    ) -> str:
        """Register a new session and return its session_id."""
        session_id = str(uuid.uuid4())
        info = SessionInfo(
            session_id   = session_id,
            filename     = filename,
            doc_type     = doc_type,
            total_pages  = total_pages,
            chunk_count  = chunk_count,
            preview_text = preview_text,
            file_path    = file_path,
            chroma_path  = chroma_path,
        )
        with self._lock:
            self._store[session_id] = info
        return session_id

    def get(self, session_id: str) -> Optional[SessionInfo]:
        """Return session info, or None if not found / expired."""
        with self._lock:
            info = self._store.get(session_id)
            if info is None:
                return None
            if info.is_expired():
                del self._store[session_id]
                return None
            return info

    def delete(self, session_id: str) -> bool:
        """Remove a session from the store. Returns True if it existed."""
        with self._lock:
            return self._store.pop(session_id, None) is not None

    def purge_expired(self) -> int:
        """Remove all expired sessions. Returns count of purged sessions."""
        with self._lock:
            expired = [sid for sid, info in self._store.items() if info.is_expired()]
            for sid in expired:
                del self._store[sid]
        return len(expired)


# ── Singleton ──────────────────────────────────────────────────────────────────
# Import and use directly:
#   from backend.rag.session_store import session_store
session_store = SessionStore()

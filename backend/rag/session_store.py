"""
session_store.py
================
In-memory session registry for uploaded document sessions.

Each session tracks:
  - session_id: UUID string
  - filename: original upload filename
  - doc_type: 'pdf' | 'image'
  - total_pages: int
  - preview_text: str
  - chunk_count: int
  - created_at: datetime
  - file_path: Path to the saved file
  - chroma_path: Path to the session's ChromaDB directory

Limitation: In-memory only — sessions are lost on server restart.
For production, replace with Redis or a persistent DB.
"""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class SessionInfo:
    session_id: str
    filename: str
    doc_type: str          # 'pdf' | 'image'
    total_pages: int
    preview_text: str
    chunk_count: int
    file_path: Path
    chroma_path: Path
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_expired(self, ttl_hours: int = 24) -> bool:
        return datetime.utcnow() > self.created_at + timedelta(hours=ttl_hours)

    def to_dict(self) -> dict:
        return {
            "session_id":   self.session_id,
            "filename":     self.filename,
            "doc_type":     self.doc_type,
            "total_pages":  self.total_pages,
            "preview_text": self.preview_text,
            "chunk_count":  self.chunk_count,
            "created_at":   self.created_at.isoformat(),
        }


class SessionStore:
    """Singleton in-memory session store."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._sessions: Dict[str, SessionInfo] = {}
        return cls._instance

    def create_session(
        self,
        filename: str,
        doc_type: str,
        total_pages: int,
        preview_text: str,
        chunk_count: int,
        file_path: Path,
        chroma_path: Path,
    ) -> str:
        """Creates a new session and returns the session_id."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SessionInfo(
            session_id=session_id,
            filename=filename,
            doc_type=doc_type,
            total_pages=total_pages,
            preview_text=preview_text,
            chunk_count=chunk_count,
            file_path=file_path,
            chroma_path=chroma_path,
        )
        return session_id

    def get(self, session_id: str) -> Optional[SessionInfo]:
        """Returns session info or None if not found/expired."""
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            self.delete(session_id)
            return None
        return session

    def delete(self, session_id: str) -> bool:
        """Removes a session from memory (does NOT clean up files)."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def list_sessions(self) -> list:
        return [s.to_dict() for s in self._sessions.values() if not s.is_expired()]


# Singleton instance
session_store = SessionStore()


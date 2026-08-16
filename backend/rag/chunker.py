"""
chunker.py
==========
Splits extracted document text into overlapping chunks for vector indexing.

Each chunk carries metadata: session_id, page_number, chunk_index, and
a text snippet for citation display.
"""

import re
from dataclasses import dataclass, field
from typing import List

from backend.rag.document_processor import DocumentContent


# ── Chunk dataclass ────────────────────────────────────────────────────────────

@dataclass
class DocumentChunk:
    """A single text chunk from an uploaded document."""
    chunk_id:     str
    session_id:   str
    page_number:  int | str
    chunk_index:  int
    text:         str
    text_snippet: str        # first 150 chars for citation display


# ── Chunking logic ─────────────────────────────────────────────────────────────

def chunk_document(
    doc: DocumentContent,
    session_id: str,
    chunk_size:  int = 800,
    overlap:     int = 150,
) -> List[DocumentChunk]:
    """
    Split document text into overlapping chunks, preserving page boundaries.

    Args:
        doc:        DocumentContent from process_upload().
        session_id: UUID of the current upload session.
        chunk_size: Maximum characters per chunk.
        overlap:    Characters of overlap between consecutive chunks.

    Returns:
        List[DocumentChunk] ready to be embedded and stored.
    """
    chunks: List[DocumentChunk] = []
    chunk_index = 0

    if doc.page_map:
        # Page-aware chunking — iterate page by page
        for page_num, page_text in doc.page_map.items():
            page_chunks = _split_text(page_text, chunk_size, overlap)
            for text in page_chunks:
                text = text.strip()
                if not text:
                    continue
                chunks.append(DocumentChunk(
                    chunk_id     = f"{session_id}_p{page_num}_c{chunk_index}",
                    session_id   = session_id,
                    page_number  = page_num,
                    chunk_index  = chunk_index,
                    text         = text,
                    text_snippet = text[:150],
                ))
                chunk_index += 1
    else:
        # Fallback: chunk the full text without page info
        raw_chunks = _split_text(doc.text, chunk_size, overlap)
        for text in raw_chunks:
            text = text.strip()
            if not text:
                continue
            chunks.append(DocumentChunk(
                chunk_id     = f"{session_id}_c{chunk_index}",
                session_id   = session_id,
                page_number  = "unknown",
                chunk_index  = chunk_index,
                text         = text,
                text_snippet = text[:150],
            ))
            chunk_index += 1

    return chunks


def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Sliding-window split that tries to break on sentence boundaries.
    """
    if not text.strip():
        return []

    # Prefer splitting at sentence ends
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks   = []
    current  = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current = (current + " " + sentence).strip()
        else:
            if current:
                chunks.append(current)
            # Start new chunk with overlap from previous
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = (overlap_text + " " + sentence).strip()

    if current:
        chunks.append(current)

    return chunks

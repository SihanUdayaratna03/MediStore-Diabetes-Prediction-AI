"""
chunker.py
===========
Medical-aware text chunker.

Splits PageContent objects into overlapping chunks and attaches rich
metadata so the vector store can return precise citations:
  - session_id
  - doc_id (filename hash)
  - page_number
  - chunk_index
  - char_start / char_end
  - doc_type
"""

import hashlib
from typing import List
from dataclasses import dataclass
from backend.rag.document_processor import DocumentContent, PageContent


@dataclass
class DocumentChunk:
    chunk_id: str          # unique: "{doc_id}_{page}_{chunk_index}"
    text: str
    session_id: str
    doc_id: str            # MD5 of filename
    filename: str
    page_number: int
    chunk_index: int       # within the page
    total_chunks_on_page: int
    char_start: int
    char_end: int
    doc_type: str          # 'pdf' | 'image'
    extraction_method: str

    @property
    def metadata_dict(self) -> dict:
        """ChromaDB-compatible metadata (all values must be str/int/float/bool)."""
        return {
            "session_id":            self.session_id,
            "doc_id":                self.doc_id,
            "filename":              self.filename,
            "page_number":           self.page_number,
            "chunk_index":           self.chunk_index,
            "total_chunks_on_page":  self.total_chunks_on_page,
            "char_start":            self.char_start,
            "char_end":              self.char_end,
            "doc_type":              self.doc_type,
            "extraction_method":     self.extraction_method,
        }


def chunk_document(
    doc_content: DocumentContent,
    session_id: str,
    chunk_size: int = 400,      # words per chunk
    chunk_overlap: int = 80,    # word overlap between adjacent chunks
) -> List[DocumentChunk]:
    """
    Converts a DocumentContent into a flat list of DocumentChunks.
    
    Chunking strategy:
    - Each page is chunked independently so page boundaries are preserved.
    - Overlapping ensures context is not lost at chunk boundaries.
    - The chunk_id encodes page + position for precise citation.
    """
    doc_id = hashlib.md5(doc_content.filename.encode()).hexdigest()[:12]
    all_chunks: List[DocumentChunk] = []

    for page in doc_content.pages:
        page_text = page.combined_text
        page_chunks_text = _split_into_word_chunks(page_text, chunk_size, chunk_overlap)

        # Track character positions for citation highlight support
        char_cursor = 0
        for chunk_idx, chunk_text in enumerate(page_chunks_text):
            char_start = page_text.find(chunk_text[:50], char_cursor)
            if char_start == -1:
                char_start = char_cursor
            char_end = char_start + len(chunk_text)
            char_cursor = max(char_cursor, char_start + len(chunk_text) - len(chunk_text) // 5)

            chunk_id = f"{doc_id}_p{page.page_number}_c{chunk_idx}"

            all_chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                session_id=session_id,
                doc_id=doc_id,
                filename=doc_content.filename,
                page_number=page.page_number,
                chunk_index=chunk_idx,
                total_chunks_on_page=len(page_chunks_text),
                char_start=char_start,
                char_end=char_end,
                doc_type=doc_content.doc_type,
                extraction_method=doc_content.extraction_method,
            ))

    return all_chunks


def _split_into_word_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> List[str]:
    """Split text by word count with overlap."""
    if not text.strip():
        return []
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - chunk_overlap
    return chunks

"""
vector_store.py
===============
ChromaDB wrappers for the RAG pipeline.

Two classes are provided:

  MedicalVectorStore  — Singleton for the shared medical-guidelines knowledge
                        base (pre-ingested, read-heavy, lives in CHROMA_DB_DIR).

  SessionVectorStore  — Per-upload collection for a single user session.
                        Created on document upload, queried during chat,
                        and isolated from every other session.
"""

import chromadb
from chromadb.utils import embedding_functions

from backend.config import CHROMA_DB_DIR

DB_PATH = str(CHROMA_DB_DIR)

# Shared embedding function used by both store classes
_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def _get_embedding_fn():
    """Returns a SentenceTransformer embedding function (cached by chromadb)."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=_EMBEDDING_MODEL
    )


# ---------------------------------------------------------------------------
# MedicalVectorStore — shared guidelines knowledge base
# ---------------------------------------------------------------------------

class MedicalVectorStore:
    """Singleton-style ChromaDB wrapper with sentence-transformer embeddings.

    Wraps the pre-ingested 'medical_guidelines' collection that lives in the
    shared CHROMA_DB_DIR.  Agents call format_for_agent() to pull relevant
    context before generating a response.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return
        self._initialised = True

        embedding_fn = _get_embedding_fn()
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="medical_guidelines",
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        """
        Semantic search over the medical-guidelines collection.

        Returns a list of dicts with 'document', 'metadata', and 'similarity'.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                output.append({
                    "document":   doc,
                    "metadata":   meta,
                    "similarity": round(1 - dist, 4),  # cosine distance → similarity
                })
        return output

    def format_for_agent(self, query: str, n_results: int = 3) -> str:
        """
        Returns retrieved guideline docs as a formatted string for LLM consumption.
        """
        results = self.search(query, n_results)
        if not results:
            return "No relevant medical guidelines found for this query."

        lines = ["**Retrieved Medical Guidelines:**\n"]
        for i, r in enumerate(results, 1):
            source     = r["metadata"].get("source", "unknown")
            similarity = r["similarity"]
            doc        = r["document"]
            lines.append(f"[{i}] Source: {source} (relevance: {similarity:.2%})")
            lines.append(f"    {doc}\n")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# SessionVectorStore — per-upload isolated collection
# ---------------------------------------------------------------------------

class SessionVectorStore:
    """
    Per-session ChromaDB vector store for uploaded documents.

    Each upload gets its own ChromaDB directory and collection.
    This ensures complete isolation between user sessions.

    Lifecycle:
      1. Created by the upload API endpoint after document processing.
      2. Populated once via add_chunks() with all DocumentChunk objects.
      3. Queried repeatedly via search() / format_for_agent() during chat.
      4. Discarded when the session expires (SessionStore TTL = 24 h).
    """

    def __init__(self, session_id: str, chroma_path: str):
        embedding_fn = _get_embedding_fn()
        self.session_id = session_id
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=f"session_{session_id[:8]}",   # short prefix for readability
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def add_chunks(self, chunks: list) -> None:
        """
        Ingest a list of DocumentChunk objects into this session's collection.
        Called once after document upload + chunking.
        """
        if not chunks:
            return
        self.collection.add(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[c.metadata_dict for c in chunks],
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """
        Semantic search within this session's document.

        Returns list of dicts with 'text', 'metadata', and 'similarity'.
        n_results is automatically clamped to the collection size so
        ChromaDB never raises an 'n_results > count' error.
        """
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count),
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                output.append({
                    "text":       doc,
                    "metadata":   meta,
                    "similarity": round(1 - dist, 4),
                })
        return output

    def format_for_agent(
        self, query: str, n_results: int = 5
    ) -> tuple[str, list[dict]]:
        """
        Returns (formatted_string_for_LLM, raw_citations_list).

        The formatted string is injected directly into the agent's prompt.
        The citations list is JSON-serializable and forwarded to the frontend
        so the UI can render source references alongside the AI response.
        """
        results = self.search(query, n_results)
        if not results:
            return "No relevant content found in the uploaded document.", []

        filename = results[0]["metadata"].get("filename", "uploaded document")
        lines = [f"**Retrieved from uploaded document '{filename}':**\n"]
        citations = []

        for i, r in enumerate(results, 1):
            meta = r["metadata"]
            page = meta.get("page_number", "?")
            sim  = r["similarity"]
            text = r["text"]

            lines.append(f"[Chunk {i}] Page {page} (relevance: {sim:.1%})")
            lines.append(f"  {text}\n")

            citations.append({
                "chunk_index":  i,
                "page_number":  page,
                "filename":     meta.get("filename", ""),
                "text_snippet": text[:200] + "..." if len(text) > 200 else text,
                "similarity":   sim,
                "chunk_id":     meta.get("chunk_id", ""),
            })

        return "\n".join(lines), citations

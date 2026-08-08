"""
Reusable ChromaDB wrapper for the RAG pipeline.
Supports semantic search with configurable embedding model.
"""

import chromadb
from chromadb.utils import embedding_functions


from backend.config import CHROMA_DB_DIR

DB_PATH = str(CHROMA_DB_DIR)


class MedicalVectorStore:
    """Singleton-style ChromaDB wrapper with sentence-transformer embeddings."""

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

        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="medical_guidelines",
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        """
        Returns a list of dicts with 'document' and 'metadata' keys.
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
                    "document": doc,
                    "metadata": meta,
                    "similarity": round(1 - dist, 4),  # Convert cosine distance → similarity
                })
        return output

    def format_for_agent(self, query: str, n_results: int = 3) -> str:
        """
        Returns retrieved docs as a formatted string for LLM consumption.
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

    

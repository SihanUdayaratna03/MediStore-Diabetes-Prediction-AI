import os
import uuid
from pathlib import Path
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions

# Paths 
ROOT     = Path(__file__).resolve().parents[2]
RAW_DOCS = Path(__file__).resolve().parent / "raw_docs"
DB_PATH  = str(ROOT / "data" / "chroma_db")


# Chunking
def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 80
) -> List[str]:
    """
    Splits text into overlapping chunks. Overlapping ensures context is not
    lost at chunk boundaries — critical for medical knowledge retrieval.
    """
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks


# Ingestion
def ingest_documents() -> None:
    print("🚀 Starting medical knowledge ingestion pipeline...")

    # Initialise ChromaDB with sentence-transformer embeddings
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"   # Fast + accurate; 384-dim vectors
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    # Delete existing collection to avoid duplicates on re-run
    try:
        client.delete_collection(name="medical_guidelines")
        print("⚠️  Deleted existing 'medical_guidelines' collection for fresh ingest.")
    except Exception:
        pass

    collection = client.create_collection(
        name="medical_guidelines",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}   # Cosine similarity for text
    )

    # Process each .txt file
    total_chunks = 0
    doc_files = list(RAW_DOCS.glob("*.txt"))

    if not doc_files:
        print(f"❌ No .txt files found in {RAW_DOCS}")
        print("   Add .txt medical guidelines files and re-run.")
        return

    for doc_path in doc_files:
        print(f"📄 Processing: {doc_path.name}")
        text   = doc_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        ids       = [str(uuid.uuid4()) for _ in chunks]
        documents = chunks
        metadatas = [
            {
                "source":   doc_path.name,
                "doc_type": "medical_guideline",
                "chunk_id": i,
            }
            for i in range(len(chunks))
        ]

        # Add in batches of 100 to stay within ChromaDB limits
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            collection.add(
                ids       = ids[i:i + batch_size],
                documents = documents[i:i + batch_size],
                metadatas = metadatas[i:i + batch_size],
            )

        total_chunks += len(chunks)
        print(f"   ✅ {len(chunks)} chunks ingested from {doc_path.name}")

    print(f"\n🎉 Ingestion complete! {total_chunks} total chunks across {len(doc_files)} files.")
    print(f"   ChromaDB stored at: {DB_PATH}")


if __name__ == "__main__":
    ingest_documents()





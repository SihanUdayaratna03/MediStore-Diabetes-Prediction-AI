"""
Quick seed-ingest: writes a handful of hard-coded guideline snippets into
ChromaDB. Useful for smoke-testing the RAG pipeline without the full corpus.

For the real corpus (backend/data_ingestion/raw_docs/*.txt with chunking and
sentence-transformer embeddings), use `ingest.py` instead.

Run from the project root:
    python -m backend.data_ingestion.ingest_seed_docs
"""

import chromadb
from dotenv import load_dotenv

from backend.config import CHROMA_DB_DIR

load_dotenv()


def populate_chromadb():
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_or_create_collection(name="medical_guidelines")

    documents = [
        "Standard treatment for Type 2 Diabetes includes Metformin and lifestyle modifications.",
        "A BMI over 30 combined with fasting glucose above 126 mg/dL strongly indicates diabetes risk.",
        "Patients with diabetic retinopathy should manage blood pressure strictly under 130/80 mmHg."
    ]

    ids = ["doc_1", "doc_2", "doc_3"]
    metadatas = [
        {"source": "ADA Guidelines"},
        {"source": "Clinical Study A"},
        {"source": "Ophthalmology Review"}
    ]

    print("Ingesting documents into ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully ingested {len(documents)} documents. DB is ready.")
    print(f"ChromaDB stored at: {CHROMA_DB_DIR}")


if __name__ == "__main__":
    populate_chromadb()

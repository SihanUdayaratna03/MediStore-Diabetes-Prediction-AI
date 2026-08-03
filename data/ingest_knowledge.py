import os
import chromadb
from dotenv import load_dotenv

load_dotenv()


def populate_chromadb():
    client = chromadb.PersistentClient(path="./chroma_db")
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


if __name__ == "__main__":
    populate_chromadb()

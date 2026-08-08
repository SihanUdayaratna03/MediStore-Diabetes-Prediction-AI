"""
Knowledge RAG MCP Server
=========================
Exposes a `semantic_search` tool that agents can call via MCP stdio protocol.
Backed by ChromaDB with sentence-transformer embeddings.
""" 

import asyncio
import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# setup
app     = Server("knowledge-rag-server")
ROOT    = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "data" / "chroma_db")
# Load embedding function (same model used during ingestion!)
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_client     = chromadb.PersistentClient(path=DB_PATH)
_collection = _client.get_or_create_collection(
    name="medical_guidelines",
    embedding_function=_embedding_fn,
    metadata={"hnsw:space": "cosine"},
)

# Tool definitions 
TOOLS = [
    types.Tool(
        name="semantic_search",
        description=(
            "Search the medical knowledge base for diabetes guidelines, "
            "treatments, risk factors, and clinical facts. "
            "Returns the top-N most semantically relevant passages."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Medical question or topic to search for.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default: 3.",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    ),
    types.Tool(
        name="get_collection_stats",
        description="Returns statistics about the knowledge base (number of documents, etc.).",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]

# Handlers
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return TOOLS
@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "semantic_search":
        query      = arguments.get("query", "")
        n_results  = int(arguments.get("num_results", 3))
        if not query.strip():
            return [types.TextContent(type="text", text="Error: query cannot be empty.")]
        results = _collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        lines = [f"Search Results for: '{query}'\n"]
        if results["documents"] and results["documents"][0]:
            for i, (doc, meta, dist) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ),
                1,
            ):
                source     = meta.get("source", "unknown")
                similarity = round(1 - dist, 4)
                lines.append(f"\n[Result {i}] Source: {source} | Relevance: {similarity:.1%}")
                lines.append(f"{doc}")
        else:
            lines.append("No relevant documents found.")
        return [types.TextContent(type="text", text="\n".join(lines))]
    elif name == "get_collection_stats":
        count = _collection.count()
        return [
            types.TextContent(
                type="text",
                text=f"Knowledge Base Stats:\n- Total chunks: {count}\n- Collection: medical_guidelines",
            )
        ]
    raise ValueError(f"Unknown tool: {name}")
    
# Entry point
async def main():
    print("🟢 Knowledge MCP Server starting...", file=sys.stderr, flush=True)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )
if __name__ == "__main__":
    asyncio.run(main())




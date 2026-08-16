"""
Researcher Agent (LangGraph Node)
===================================
Retrieves relevant content by calling MCP servers.

When doc_mode=True:
  1. Calls the Document MCP server with the session_id to search the uploaded doc.
  2. Falls back to the Knowledge MCP server for general medical context.

When doc_mode=False:
  - Only calls the Knowledge MCP server (existing behavior).
"""

import sys
from pathlib import Path
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from backend.app.agents.state import AgentState

PYTHON               = sys.executable
ROOT                 = Path(__file__).resolve().parents[3]
KNOWLEDGE_MCP_SERVER = str(ROOT / "mcp_servers" / "knowledge_mcp" / "server.py")
DOCUMENT_MCP_SERVER  = str(ROOT / "mcp_servers" / "document_mcp" / "server.py")


async def _call_knowledge_mcp(query: str, num_results: int = 3) -> str:
    """Search the static medical knowledge base."""
    try:
        server_params = StdioServerParameters(command=PYTHON, args=[KNOWLEDGE_MCP_SERVER])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "semantic_search",
                    {"query": query, "num_results": num_results},
                )
                return result.content[0].text if result.content else "No guidelines found."
    except Exception as e:
        return f"Knowledge retrieval error: {str(e)}"


async def _call_document_mcp(session_id: str, query: str, num_results: int = 5) -> tuple[str, list]:
    """Search the uploaded document's session collection."""
    try:
        server_params = StdioServerParameters(command=PYTHON, args=[DOCUMENT_MCP_SERVER])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "session_search",
                    {"session_id": session_id, "query": query, "num_results": num_results},
                )
                text = result.content[0].text if result.content else "No document content found."
                return text, []   # citations handled by analyst node
    except Exception as e:
        return f"Document retrieval error: {str(e)}", []


async def researcher_node(state: AgentState) -> AgentState:
    """
    LangGraph node: retrieves relevant content from appropriate sources.
    """
    query            = state.get("user_query", "")
    patient_context  = state.get("patient_context", "")
    session_id       = state.get("session_id")
    doc_mode         = state.get("doc_mode", False)

    steps = state.get("steps_taken", [])
    steps.append("researcher_node")

    # Build search query (enrich with patient context if available)
    search_query = query
    if patient_context:
        search_query = f"{query}\n\nPatient context: {patient_context}"

    doc_context   = None
    retrieved_docs = ""

    if doc_mode and session_id:
        # Primary: search the uploaded document
        doc_retrieved, _ = await _call_document_mcp(session_id, search_query, num_results=5)
        doc_context = doc_retrieved

        # Secondary: also search general knowledge for broader medical context
        knowledge_retrieved = await _call_knowledge_mcp(query, num_results=2)
        retrieved_docs = knowledge_retrieved
    else:
        # Standard mode: only knowledge base
        retrieved_docs = await _call_knowledge_mcp(search_query, num_results=3)

    return {
        **state,
        "retrieved_docs": retrieved_docs,
        "doc_context":    doc_context,
        "steps_taken":    steps,
    }

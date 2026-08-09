"""
Researcher Agent (LangGraph Node)
===================================
Calls the Knowledge MCP server to retrieve relevant medical guidelines
for the user's query. Writes results to AgentState['retrieved_docs'].
"""

import sys
from pathlib import Path
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from backend.app.agents.state import AgentState

PYTHON               = sys.executable
ROOT                 = Path(__file__).resolve().parents[3]
KNOWLEDGE_MCP_SERVER = str(ROOT / "mcp_servers" / "knowledge_mcp" / "server.py")


async def researcher_node(state: AgentState) -> AgentState:
    """
    LangGraph node: retrieves relevant medical documents.
    Called by the orchestrator as the first step.
    """
    query = state.get("user_query", "")

    # Build a search query from both the user question and patient context
    patient_context = state.get("patient_context", "")
    if patient_context:
        search_query = f"{query}\n\nPatient context: {patient_context}"
    else:
        search_query = query

    try:
        server_params = StdioServerParameters(
            command=PYTHON,
            args=[KNOWLEDGE_MCP_SERVER],
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "semantic_search",
                    {"query": search_query, "num_results": 3},
                )
                retrieved = (
                    result.content[0].text
                    if result.content
                    else "No relevant documents found."
                )
    except Exception as e:
        retrieved = f"Retrieval error: {str(e)}"

    steps = state.get("steps_taken", [])
    steps.append("researcher_node")

    return {
        **state,
        "retrieved_docs": retrieved,
        "steps_taken":    steps,
    }



"""
LangGraph Multi-Agent Orchestration Graph
==========================================

Graph topology:
  [START]
     │
     ▼
  orchestrator ──(empty query)──► [END]
     │
     ▼  (valid query)
  researcher
     │
     ▼
  analyst
     │
     ▼
  [END]

Usage:
    from backend.app.graph import rag_graph
    result = await rag_graph.ainvoke(initial_state)
"""

from langgraph.graph import StateGraph, END

from backend.app.agents.state        import AgentState
from backend.app.agents.orchestrator import orchestrator_node, route_after_orchestrator
from backend.app.agents.researcher   import researcher_node
from backend.app.agents.analyst      import analyst_node


def build_rag_graph() -> StateGraph:
    """
    Constructs and compiles the Multi-Agent RAG StateGraph.

    Returns:
        A compiled LangGraph graph ready for ainvoke().
    """
    graph = StateGraph(AgentState)

    # ── Register nodes ──────────────────────────────────────────────────────────
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("researcher",   researcher_node)
    graph.add_node("analyst",      analyst_node)

    # ── Entry point ─────────────────────────────────────────────────────────────
    graph.set_entry_point("orchestrator")

    # ── Conditional edge: orchestrator decides next step ─────────────────────────
    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {
            "researcher": "researcher",
            "END":        END,
        },
    )

    # ── Linear edges ─────────────────────────────────────────────────────────────
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst",    END)

    return graph.compile()


# ── Singleton compiled graph ─────────────────────────────────────────────────────
# Import and use directly anywhere in the backend:
#   from backend.app.graph import rag_graph
rag_graph = build_rag_graph()

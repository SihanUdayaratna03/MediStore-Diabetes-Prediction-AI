"""
LangGraph Multi-Agent Orchestration Graph (Enhanced)
======================================================

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
  reasoning
     │
     ▼
  analyst
     │
     ▼
  guardrail
     │
     ▼
  [END]
"""

from langgraph.graph import StateGraph, END

from backend.app.agents.state        import AgentState
from backend.app.agents.orchestrator import orchestrator_node, route_after_orchestrator
from backend.app.agents.researcher   import researcher_node
from backend.app.agents.reasoning    import reasoning_node
from backend.app.agents.analyst      import analyst_node
from backend.app.agents.guardrail    import guardrail_node


def build_rag_graph() -> StateGraph:
    """Constructs and compiles the 5-node Multi-Agent RAG StateGraph."""
    graph = StateGraph(AgentState)

    # ── Register nodes ──────────────────────────────────────────────────────────
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("researcher",   researcher_node)
    graph.add_node("reasoning",    reasoning_node)
    graph.add_node("analyst",      analyst_node)
    graph.add_node("guardrail",    guardrail_node)

    # ── Entry point ─────────────────────────────────────────────────────────────
    graph.set_entry_point("orchestrator")

    # ── Conditional edge: orchestrator decides next step ─────────────────────────
    graph.add_conditional_edges(
        "orchestrator",
        route_after_orchestrator,
        {"researcher": "researcher", "END": END},
    )

    # ── Linear pipeline ───────────────────────────────────────────────────────────
    graph.add_edge("researcher", "reasoning")
    graph.add_edge("reasoning",  "analyst")
    graph.add_edge("analyst",    "guardrail")
    graph.add_edge("guardrail",  END)

    return graph.compile()


# Singleton compiled graph
rag_graph = build_rag_graph()

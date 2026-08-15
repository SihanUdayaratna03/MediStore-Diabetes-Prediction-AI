"""
Orchestrator Agent (LangGraph Node)
=====================================
Validates and pre-processes the user query, then acts as a conditional
router — forwarding to the researcher pipeline or short-circuiting if
the query is empty/invalid.
"""

from backend.app.agents.state import AgentState


def orchestrator_node(state: AgentState) -> AgentState:
    """
    LangGraph node: validates the user query and initialises the pipeline.
    This node is synchronous (pure Python — no I/O).

    On empty query → sets final_response to short-circuit the graph.
    On valid query → passes state unchanged to the researcher.
    """
    query = state.get("user_query", "").strip()

    steps = state.get("steps_taken", [])
    steps.append("orchestrator_node")

    if not query:
        return {
            **state,
            "user_query":     query,
            "final_response": "Please provide a question or patient data to analyse.",
            "steps_taken":    steps,
        }

    return {
        **state,
        "user_query":  query,
        "steps_taken": steps,
    }


def route_after_orchestrator(state: AgentState) -> str:
    """
    Conditional routing function used by LangGraph's add_conditional_edges.

    Returns:
        "END"        — if we already have a final_response (empty query case)
        "researcher" — if we need to retrieve docs and run the full pipeline
    """
    if state.get("final_response"):
        return "END"
    return "researcher"

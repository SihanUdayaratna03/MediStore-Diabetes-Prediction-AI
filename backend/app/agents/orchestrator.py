"""
Orchestrator Agent (LangGraph Node)
=====================================
Validates the user query, detects document mode (when session_id is present),
and routes to the appropriate pipeline.

Routing logic:
  - Empty query              → END (short-circuit with error message)
  - session_id present       → "researcher" with doc_mode=True
  - No session, medical query → "researcher" with doc_mode=False
"""

from backend.app.agents.state import AgentState


def orchestrator_node(state: AgentState) -> AgentState:
    """
    LangGraph node: validates the user query and sets doc_mode flag.
    Synchronous (no I/O).
    """
    query      = state.get("user_query", "").strip()
    session_id = state.get("session_id")

    steps = state.get("steps_taken", [])
    steps.append("orchestrator_node")

    if not query:
        return {
            **state,
            "user_query":     query,
            "final_response": "Please provide a question to analyse.",
            "steps_taken":    steps,
        }

    # If a document session is active, set doc_mode
    doc_mode = bool(session_id and session_id.strip())

    return {
        **state,
        "user_query":  query,
        "doc_mode":    doc_mode,
        "steps_taken": steps,
    }


def route_after_orchestrator(state: AgentState) -> str:
    """
    Routing function for LangGraph conditional edges.

    Returns:
        "END"        → already has final_response (empty query case)
        "researcher" → normal or document-mode pipeline
    """
    if state.get("final_response"):
        return "END"
    return "researcher"

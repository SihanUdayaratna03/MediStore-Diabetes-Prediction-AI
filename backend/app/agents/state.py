"""
Shared state that flows through the entire LangGraph pipeline.
Every agent node reads from and writes to this TypedDict.
"""

from typing import TypedDict, Optional, List


class CitationRef(TypedDict):
    """A single citation reference returned alongside the final response."""
    chunk_index:  int
    page_number:  int | str
    filename:     str
    text_snippet: str
    similarity:   float
    chunk_id:     str


class AgentState(TypedDict):
    """The state passed between all agents in the graph."""

    # ── Input fields ──────────────────────────────────────────────────────────
    user_query:       str
    patient_context:  str

    # ── Document fields ───────────────────────────────────────────────────────
    session_id:       Optional[str]      # set when a document has been uploaded
    doc_mode:         bool               # True → prioritise document retrieval
    doc_context:      Optional[str]      # formatted doc content for analyst
    citations:        List[CitationRef]  # citation references to return to frontend

    # ── Conversation memory ───────────────────────────────────────────────────
    conversation_history: List[dict]     # [{role: 'user'|'assistant', content: str}]

    # ── Intermediate fields ───────────────────────────────────────────────────
    retrieved_docs:          Optional[str]
    clinical_interpretation: Optional[str]
    reasoning_trace:         Optional[str]  # from reasoning_node

    # ── Output fields ─────────────────────────────────────────────────────────
    final_response: Optional[str]

    # ── Metadata ──────────────────────────────────────────────────────────────
    error:       Optional[str]
    steps_taken: List[str]

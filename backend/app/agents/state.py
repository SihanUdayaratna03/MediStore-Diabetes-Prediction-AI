"""
Shared state that flows through the entire LangGraph pipeline.
Every agent node reads from and writes to this TypedDict.
"""

from typing import TypedDict, Optional, List
from langgraph.graph import MessagesState


class AgentState(TypedDict):
    """The state passed between all agents in the graph."""

    # Input fields
    user_query: str                    
    patient_context: str              

    # Intermediate fields 
    retrieved_docs: Optional[str]     
    clinical_interpretation: Optional[str]  

    # Output fields 
    final_response: Optional[str]    

    # etadata 
    error: Optional[str]               
    steps_taken: List[str]            

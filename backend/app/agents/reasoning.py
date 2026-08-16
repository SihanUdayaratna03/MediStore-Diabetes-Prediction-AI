"""
Reasoning Agent (LangGraph Node)
==================================
Performs multi-step reasoning over retrieved document content.

When doc_mode=True:
  - Identifies the most relevant evidence from the document.
  - Maps evidence to the user's specific question.
  - Generates a structured reasoning trace.
  - Extracts citation references (page numbers, text snippets).

When doc_mode=False:
  - Lightweight reasoning step over retrieved guidelines.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from backend.app.agents.state import AgentState
from backend.rag.prompts import REASONING_AGENT_PROMPT

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=REASONING_AGENT_PROMPT,
)


async def reasoning_node(state: AgentState) -> AgentState:
    """
    LangGraph node: performs chain-of-thought reasoning over retrieved content.
    """
    user_query   = state.get("user_query", "")
    doc_context  = state.get("doc_context", "")
    retrieved    = state.get("retrieved_docs", "")
    doc_mode     = state.get("doc_mode", False)

    steps = state.get("steps_taken", [])
    steps.append("reasoning_node")

    if doc_mode and doc_context:
        prompt = f"""
User Question: {user_query}

Content from Uploaded Document:
{doc_context}

Supplementary Medical Guidelines:
{retrieved}

Perform step-by-step reasoning:
1. Identify the exact information in the document that answers the question.
2. Note any relevant medical values, diagnoses, or recommendations mentioned.
3. Cross-reference with medical guidelines where applicable.
4. Summarize the key evidence in 3-5 bullet points.
5. Identify any critical findings that need emphasis (e.g., abnormal values, urgent recommendations).
6. Note the specific pages/sections where each piece of evidence was found.

Format your response as a structured reasoning trace.
"""
    else:
        prompt = f"""
User Question: {user_query}

Retrieved Medical Guidelines:
{retrieved}

Briefly reason through the guidelines:
1. Identify the most relevant sections.
2. Note key medical facts that apply to this question.
3. Summarize in 2-3 bullet points.
"""

    try:
        response = _model.generate_content(prompt)
        reasoning_trace = response.text
    except Exception as e:
        reasoning_trace = f"Reasoning step skipped: {str(e)}"

    return {
        **state,
        "reasoning_trace": reasoning_trace,
        "steps_taken":     steps,
    }

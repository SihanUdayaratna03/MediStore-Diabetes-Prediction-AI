"""
Analyst Agent (LangGraph Node)
================================
Synthesises document content + reasoning trace + guidelines into
a structured, citation-aware final response using Gemini.

When doc_mode=True:
  - Primary source: uploaded document (doc_context)
  - Secondary: medical guidelines (retrieved_docs)
  - Generates answer with explicit document citations

When doc_mode=False:
  - Standard behavior: guidelines + patient context
"""

import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai

from backend.app.agents.state import AgentState
from backend.rag.prompts import ANALYST_AGENT_PROMPT, DOC_ANALYST_PROMPT

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=ANALYST_AGENT_PROMPT,
)

_doc_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=DOC_ANALYST_PROMPT,
)


async def analyst_node(state: AgentState) -> AgentState:
    """LangGraph node: generates the final structured response."""
    patient_context = state.get("patient_context", "No patient data provided.")
    retrieved_docs  = state.get("retrieved_docs", "No general guidelines retrieved.")
    doc_context     = state.get("doc_context")
    user_query      = state.get("user_query", "")
    reasoning_trace = state.get("reasoning_trace", "")
    doc_mode        = state.get("doc_mode", False)
    conversation_history = state.get("conversation_history", [])

    steps = state.get("steps_taken", [])
    steps.append("analyst_node")

    # Build conversation context string
    conv_context = ""
    if conversation_history:
        recent = conversation_history[-6:]  # last 3 turns
        conv_context = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in recent
        )

    citations = []

    if doc_mode and doc_context:
        prompt = f"""
User Question: {user_query}

Conversation History:
{conv_context or "No previous conversation."}

Content Retrieved from Uploaded Document:
{doc_context}

Reasoning Trace:
{reasoning_trace}

Supplementary Medical Guidelines:
{retrieved_docs}

Please provide a structured answer that:
1. Directly answers the user's question based on the uploaded document content.
2. Cites specific pages or sections (e.g., "According to page 3 of your report...").
3. Highlights any critical medical values, diagnoses, or recommendations found.
4. Cross-references with general medical guidelines where relevant.
5. Flags any findings that require urgent medical attention.
6. Recommends consulting a qualified healthcare professional for final decisions.

When referencing the document, always mention the page number.
Format the response in clear sections with headers.
"""
        model_to_use = _doc_model
    else:
        prompt = f"""
User Question: {user_query}

Conversation History:
{conv_context or "No previous conversation."}

Patient Context:
{patient_context}

Retrieved Medical Guidelines:
{retrieved_docs}

Reasoning Trace:
{reasoning_trace}

Please provide a structured clinical analysis that:
1. Directly answers the user's question.
2. Interprets the patient's data against the guidelines.
3. Identifies key risk factors.
4. Provides actionable recommendations.
5. Reminds the patient to consult a qualified healthcare professional.
"""
        model_to_use = _model

    try:
        response       = model_to_use.generate_content(prompt)
        final_response = response.text
        error          = None
    except Exception as e:
        final_response = "I was unable to generate an analysis at this time. Please try again."
        error          = str(e)

    return {
        **state,
        "final_response": final_response,
        "citations":      citations,
        "steps_taken":    steps,
        "error":          error,
    }

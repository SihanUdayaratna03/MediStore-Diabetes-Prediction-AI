"""
Analyst Agent (LangGraph Node)
================================
Takes patient context + retrieved medical guidelines and generates
a clear, empathetic clinical analysis using Gemini.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from backend.app.agents.state import AgentState
from backend.rag.prompts import ANALYST_AGENT_PROMPT

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=ANALYST_AGENT_PROMPT,
)


async def analyst_node(state: AgentState) -> AgentState:
    """
    LangGraph node: synthesises retrieved docs + patient context into
    a structured clinical analysis.
    """
    patient_context = state.get("patient_context", "No patient data provided.")
    retrieved_docs  = state.get("retrieved_docs", "No documents retrieved.")
    user_query      = state.get("user_query", "")

    prompt = f"""
User Question: {user_query}

Patient Context:
{patient_context}

Retrieved Medical Guidelines:
{retrieved_docs}

Please provide a clear, structured clinical analysis that:
1. Directly answers the user's question
2. Interprets the patient's data against the guidelines
3. Identifies key risk factors
4. Provides actionable recommendations
5. Reminds the patient to consult a qualified healthcare professional
"""

    try:
        response       = _model.generate_content(prompt)
        final_response = response.text
        error          = None
    except Exception as e:
        final_response = "I was unable to generate an analysis at this time. Please try again."
        error          = str(e)

    steps = state.get("steps_taken", [])
    steps.append("analyst_node")

    return {
        **state,
        "final_response": final_response,
        "steps_taken":    steps,
        "error":          error,
    }

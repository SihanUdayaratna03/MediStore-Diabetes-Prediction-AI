# TODO: Implement the Guardrail Agent (LangGraph node).
# Last node before returning a response.
# Responsibilities:
#   - Check if the response is medically safe
#   - Verify the query is within medical scope
#   - Append a professional consultation disclaimer if missing
#   - Replace with a safe fallback if the response is truly dangerous

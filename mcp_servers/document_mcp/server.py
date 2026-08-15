# TODO: Implement the Document RAG MCP server.
# Exposes two tools via the MCP stdio protocol:
#
#   session_search  — semantic search within an uploaded document's ChromaDB collection.
#                     Accepts: session_id, query, num_results
#                     Returns: page-cited passages from data/session_chroma/{session_id}/
#
#   get_session_info — returns metadata about the uploaded document session.
#                      Accepts: session_id
#
# Run standalone: python mcp_servers/document_mcp/server.py
# Called by: backend/app/agents/researcher.py via MCP stdio client

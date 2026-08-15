/**
 * docApi.js
 * TODO: Implement HTTP client for document upload and doc-chat endpoints.
 *
 * Functions to implement:
 *   uploadDocument(file)                                  → POST /api/v1/upload
 *   sendDocChatMessage(sessionId, query, history)         → POST /api/v1/doc-chat
 *   getSessionInfo(sessionId)                             → GET  /api/v1/session/{id}
 *   deleteSession(sessionId)                              → DELETE /api/v1/session/{id}
 *
 * Base URL: import.meta.env.VITE_RAG_API_URL ?? 'http://localhost:8002'
 * Timeout: 120000ms (2 min — OCR + LLM can be slow)
 */

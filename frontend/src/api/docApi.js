/**
 * docApi.js
 * =========
 * HTTP client for the document upload and doc-chat endpoints.
 *
 * Endpoints used:
 *   POST /api/v1/upload       — multipart file upload
 *   POST /api/v1/doc-chat     — JSON chat with session_id
 *   GET  /api/v1/session/{id} — session info
 *   DELETE /api/v1/session/{id} — clean up session
 */

import axios from 'axios'

const RAG_BASE_URL = import.meta.env.VITE_RAG_API_URL ?? 'http://localhost:8002'

const docClient = axios.create({
  baseURL: RAG_BASE_URL,
  timeout: 120000,  // 2 min — LLM + OCR can be slow
})

/**
 * Upload a medical PDF or image file.
 * @param {File} file - The file object from the input element
 * @returns {Promise<UploadResponse>}
 */
export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await docClient.post('/api/v1/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
  return res.data
}

/**
 * Send a question about an uploaded document.
 * @param {string} sessionId          - From uploadDocument()
 * @param {string} query              - User's question
 * @param {Array}  conversationHistory - [{role, content}] pairs
 * @returns {Promise<DocChatResponse>}
 */
export async function sendDocChatMessage(sessionId, query, conversationHistory = []) {
  const res = await docClient.post('/api/v1/doc-chat', {
    session_id:           sessionId,
    query,
    conversation_history: conversationHistory,
  })
  return res.data
}

/**
 * Get information about an active document session.
 */
export async function getSessionInfo(sessionId) {
  const res = await docClient.get(`/api/v1/session/${sessionId}`)
  return res.data
}

/**
 * Delete a session and clean up server-side files.
 */
export async function deleteSession(sessionId) {
  const res = await docClient.delete(`/api/v1/session/${sessionId}`)
  return res.data
}

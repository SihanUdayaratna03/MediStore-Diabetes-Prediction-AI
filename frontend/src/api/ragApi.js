/**
 * ragApi.js
 * =========
 * All HTTP calls to the MediStore Multi-Agent RAG backend (port 8002).
 *
 * The RAG_BASE_URL can be overridden via a Vite env var so the app works
 * in both local dev and deployed environments without code changes.
 *
 * Usage:
 *   import { sendChatMessage } from './api/ragApi'
 *   const data = await sendChatMessage("What are my risk factors?", patientCtx)
 */

import axios from 'axios'

// Default: localhost:8002 (RAG server), overridable via .env
const RAG_BASE_URL = import.meta.env.VITE_RAG_API_URL ?? 'http://localhost:8002'

const ragClient = axios.create({
  baseURL: RAG_BASE_URL,
  timeout: 60000,  // 60s — LLM + MCP calls can be slow
  headers: { 'Content-Type': 'application/json' },
})

/**
 * Sends a chat message to the Multi-Agent RAG pipeline.
 *
 * @param {string} query           - The user's question
 * @param {string} patientContext  - Optional pre-formatted patient data string
 * @returns {Promise<{response: string, steps_taken: string[], error: string|null}>}
 */
export async function sendChatMessage(query, patientContext = '') {
  const res = await ragClient.post('/api/v1/chat', {
    query,
    patient_context: patientContext || null,
  })
  return res.data
}

/**
 * Health check for the RAG backend.
 * @returns {Promise<{status: string, service: string, version: string}>}
 */
export async function checkRagHealth() {
  const res = await ragClient.get('/api/v1/health')
  return res.data
}

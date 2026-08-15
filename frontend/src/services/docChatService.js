/**
 * docChatService.js
 * TODO: Implement the React hook for the DocChat component.
 *
 * Hook: useDocChatService(sessionId)
 *
 * Manages:
 *   - messages[]              message history (user + assistant with citations)
 *   - isLoading               loading state while awaiting the RAG pipeline
 *   - conversationHistory[]   [{role, content}] pairs sent to the backend for memory
 *   - sendMessage(userText)   appends user msg, calls sendDocChatMessage(), appends AI reply
 *   - clearChat()             resets messages and conversationHistory
 *
 * Returns: { messages, isLoading, sendMessage, clearChat }
 */

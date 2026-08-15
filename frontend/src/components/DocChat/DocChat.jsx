/**
 * DocChat.jsx
 * TODO: Implement the full-panel document Q&A chat interface.
 *
 * Props:
 *   sessionData  — UploadResponse | null
 *   isReady      — boolean (true once document is uploaded and indexed)
 *   onReset()    — called when user wants to upload a new document
 *
 * Features:
 *   - Header with filename display
 *   - Message bubbles (user / assistant) using useDocChatService()
 *   - Citation toggle badge on each assistant message ("📎 N sources cited")
 *   - Expandable CitationPanel per message
 *   - Agent steps trace badges
 *   - Typing indicator (3-dot animation)
 *   - Suggested starter questions (shown when ready but no messages yet)
 *   - Textarea input + send button (disabled when !isReady)
 *   - Medical disclaimer footer
 *   - Clear conversation button
 */

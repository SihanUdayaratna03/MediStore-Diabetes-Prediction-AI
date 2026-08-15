/**
 * useDocSession.js
 * TODO: Implement session state management hook.
 *
 * Hook: useDocSession()
 *
 * Manages:
 *   - sessionData      UploadResponse from the backend (session_id, filename, etc.)
 *   - uploadState      'idle' | 'uploading' | 'ready' | 'error'
 *   - uploadError      string | null
 *   - uploadProgress   0–100
 *   - handleUpload(file)   calls uploadDocument(), updates state
 *   - handleReset()        resets all state back to 'idle'
 *
 * Returns: { sessionData, uploadState, uploadError, uploadProgress, handleUpload, handleReset }
 */

/**
 * DocUpload.jsx
 * TODO: Implement the drag-and-drop medical document upload component.
 *
 * Props:
 *   onUpload(file)  — called with the validated File object when user clicks "Analyse"
 *   error           — string | null — external error from parent (upload failures)
 *
 * Features:
 *   - Drag-and-drop zone with visual feedback (isDragging state)
 *   - File type validation: PDF, JPG, PNG, WEBP, TIFF (max 25MB)
 *   - Preview of selected file name + size
 *   - List of supported document types (doctor reports, lab results, etc.)
 *   - "Analyse This Document" submit button
 */

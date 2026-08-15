/**
 * DocIntelligence.jsx
 * TODO: Implement the full Document Intelligence screen.
 *
 * Props:
 *   onBack()  — navigate back to the mode-select screen
 *
 * Layout (two-column on desktop, stacked on mobile):
 *   ┌─────────────────────────────────────────────────────┐
 *   │  Header: back button + title + session badge        │
 *   ├──────────────────────┬──────────────────────────────┤
 *   │  Left Panel          │  Right Panel                 │
 *   │  - DocUpload (idle)  │  - DocChat                   │
 *   │  - Upload progress   │  (disabled until ready)      │
 *   │  - DocViewer (ready) │                              │
 *   └──────────────────────┴──────────────────────────────┘
 *
 * Upload state machine: 'idle' → 'uploading' → 'ready' | 'error'
 * Uses useDocSession() hook for state management.
 */

import { Activity, ArrowLeft } from 'lucide-react'

/**
 * Persistent brand bar across the two predictor dashboards. Gives the app a
 * fixed identity anchor and a consistent place for the back action, instead of
 * a lone floating button.
 */
export default function TopBar({ moduleName, accent = 'sky', onBack, backLabel = 'Predictor Selection' }) {
  const colour = accent === 'violet' ? 'var(--violet-300)' : 'var(--sky-300)'

  return (
    <header className="ms-topbar">
      <div className="ms-brand">
        <span className="ms-brand__mark" aria-hidden="true">
          <Activity size={18} color="#e0f2fe" />
        </span>
        <span>
          MediStore AI
          {moduleName && (
            <>
              <span aria-hidden="true" style={{ color: 'var(--text-dim)', margin: '0 0.5rem', fontWeight: 400 }}>/</span>
              <span style={{ color: colour, fontWeight: 600 }}>{moduleName}</span>
            </>
          )}
          <span className="ms-brand__sub" style={{ display: 'block', marginTop: 2 }}>
            Clinical Diagnostic System
          </span>
        </span>
      </div>

      {onBack && (
        <button type="button" className="ms-btn" onClick={onBack}>
          <ArrowLeft size={16} aria-hidden="true" /> {backLabel}
        </button>
      )}
    </header>
  )
}

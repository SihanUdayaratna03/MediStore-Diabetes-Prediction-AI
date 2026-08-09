import { useState } from 'react'
import { SlidersHorizontal, ChevronDown } from 'lucide-react'

/**
 * The patient-input rail. On desktop it is a sticky glass pane; below 860px it
 * collapses behind a toggle so the dashboard — the part a clinician actually
 * reads — is what greets them on a phone.
 */
export default function Sidebar({ title = 'Patient Data', accent = 'sky', children }) {
  const [collapsed, setCollapsed] = useState(false)
  const colour = accent === 'violet' ? 'var(--violet-300)' : 'var(--sky-300)'

  return (
    <aside
      className="sidebar"
      data-collapsed={collapsed}
      aria-label="Patient data entry"
    >
      <button
        type="button"
        className="ms-sidebar-toggle"
        aria-expanded={!collapsed}
        onClick={() => setCollapsed((v) => !v)}
      >
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.55rem' }}>
          <SlidersHorizontal size={16} color={colour} aria-hidden="true" />
          {title}
        </span>
        <ChevronDown
          size={16}
          color={colour}
          aria-hidden="true"
          style={{
            transform: collapsed ? 'rotate(0deg)' : 'rotate(180deg)',
            transition: 'transform var(--dur-base) var(--ease-out)',
          }}
        />
      </button>

      <div className="ms-sidebar-body">{children}</div>
    </aside>
  )
}

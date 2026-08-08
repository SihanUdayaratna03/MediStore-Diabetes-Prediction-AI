import { useState } from 'react'
import { AlertTriangle, ShieldCheck } from 'lucide-react'
import { useGrowIn } from '../../hooks/useGrowIn'

/**
 * Risk factors weighed against protective factors.
 *
 * Form choice — the data has polarity (working against the patient vs for
 * them), so this is a diverging bar off a neutral centre line, not two
 * separate counts. Side-of-axis carries the sign, which means colour is a
 * redundant encoding here rather than the only one; icons and labels back it
 * up again. Colours are the validated diverging pair (ΔE 9.6 deutan).
 */
export default function FactorBalance({ risks, goods }) {
  const [hover, setHover] = useState(null)

  const riskCount = risks.length
  const goodCount = goods.length
  const max = Math.max(riskCount, goodCount, 1)

  // Severity breakdown — how much of the risk load is critical vs moderate.
  const critical = risks.filter((r) => r.level === 'r').length
  const moderate = riskCount - critical

  const grown = useGrowIn([riskCount, goodCount])

  const rows = [
    {
      key: 'critical',
      label: 'Critical risk factors',
      side: 'left',
      count: critical,
      colour: 'var(--status-critical)',
      fill: 'linear-gradient(270deg, #b91c1c, #ef4444)',
    },
    {
      key: 'moderate',
      label: 'Moderate risk factors',
      side: 'left',
      count: moderate,
      colour: 'var(--status-warn)',
      fill: 'linear-gradient(270deg, #a16207, #eab308)',
    },
    {
      key: 'protective',
      label: 'Protective indicators',
      side: 'right',
      count: goodCount,
      colour: 'var(--status-good)',
      fill: 'linear-gradient(90deg, #047857, #10b981)',
    },
  ]

  return (
    <div className="ms-chart" style={{ position: 'relative' }}>
      <div style={{ display: 'grid', gap: '0.5rem' }}>
        {rows.map((row) => {
          const pct = grown ? (row.count / max) * 100 : 0
          return (
            <div
              className="ms-balance"
              key={row.key}
              onPointerEnter={() => setHover(row.key)}
              onPointerLeave={() => setHover(null)}
            >
              {/* Left arm — risk */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.6rem', minWidth: 0 }}>
                {row.side === 'left' && (
                  <>
                    <span style={{
                      fontSize: '0.78rem', color: 'var(--text-muted)',
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                    }}>
                      {row.label}
                    </span>
                    <span
                      className="ms-balance__bar"
                      style={{ width: `${pct}%`, minWidth: row.count ? 8 : 0, background: row.fill, borderRadius: '6px 2px 2px 6px' }}
                    />
                  </>
                )}
              </div>

              {/* Neutral midpoint */}
              <span className="ms-balance__mid" aria-hidden="true" />

              {/* Right arm — protective */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', minWidth: 0 }}>
                {row.side === 'right' && (
                  <>
                    <span
                      className="ms-balance__bar"
                      style={{ width: `${pct}%`, minWidth: row.count ? 8 : 0, background: row.fill, borderRadius: '2px 6px 6px 2px' }}
                    />
                    <span style={{
                      fontSize: '0.78rem', color: 'var(--text-muted)',
                      whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                    }}>
                      {row.label}
                    </span>
                  </>
                )}
              </div>

              {hover === row.key && (
                <span className="ms-tooltip" style={{ left: '50%', top: 0 }}>
                  <span className="ms-tooltip__title">{row.label}</span>
                  <span className="ms-tooltip__meta">
                    {row.count} of {riskCount + goodCount} total signals
                  </span>
                </span>
              )}
            </div>
          )
        })}
      </div>

      <div className="ms-legend">
        <span className="ms-legend__item">
          <AlertTriangle size={13} color="var(--status-critical)" aria-hidden="true" />
          Working against the patient ({riskCount})
        </span>
        <span className="ms-legend__item">
          <ShieldCheck size={13} color="var(--status-good)" aria-hidden="true" />
          Working for the patient ({goodCount})
        </span>
      </div>
    </div>
  )
}

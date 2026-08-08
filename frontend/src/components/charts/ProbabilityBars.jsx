import { useState } from 'react'
import { CheckCircle2, AlertOctagon } from 'lucide-react'
import CountUp from '../ui/CountUp'
import { useGrowIn } from '../../hooks/useGrowIn'

/**
 * The two class probabilities as a paired bar comparison.
 *
 * Form choice — two magnitudes on a shared 0–100 scale, compared against a
 * decision threshold. One axis, one scale, direct labels on both rows (there
 * are only two, so labelling every one is not clutter), plus a legend, so
 * identity never rests on colour. A table view is always one click away.
 */
export default function ProbabilityBars({
  negative,            // { label, value }
  positive,            // { label, value }
  positiveColour,
  threshold = 50,
}) {
  const [showTable, setShowTable] = useState(false)
  const [hover, setHover] = useState(null)
  const grown = useGrowIn([negative.value, positive.value])

  const rows = [
    {
      ...negative,
      key: 'negative',
      colour: 'var(--status-good)',
      fill: 'linear-gradient(90deg, #047857, #10b981)',
      Icon: CheckCircle2,
    },
    {
      ...positive,
      key: 'positive',
      colour: positiveColour,
      fill: `linear-gradient(90deg, ${positiveColour}, ${positiveColour}cc)`,
      Icon: AlertOctagon,
    },
  ]

  return (
    <div className="ms-chart">
      {rows.map((row) => {
        const width = grown ? Math.max(0, Math.min(row.value, 100)) : 0
        return (
          <div className="ms-bar-row" key={row.key}>
            <div className="ms-bar-head">
              <span className="ms-bar-head__name">
                <row.Icon size={14} color={row.colour} aria-hidden="true" />
                {row.label}
              </span>
              <span className="ms-bar-head__value" style={{ color: row.colour }}>
                <CountUp value={row.value} decimals={1} suffix="%" />
              </span>
            </div>

            <div
              className="ms-bar-track"
              onPointerEnter={() => setHover(row.key)}
              onPointerLeave={() => setHover(null)}
              style={{ position: 'relative' }}
            >
              <div
                className="ms-bar-fill"
                style={{ width: `${width}%`, background: row.fill }}
              />
              {/* Decision threshold marker, drawn above the fill */}
              <span
                className="ms-bar-threshold"
                style={{ left: `${threshold}%` }}
                aria-hidden="true"
              />
              {hover === row.key && (
                <span className="ms-tooltip" style={{ left: `${Math.min(Math.max(row.value, 12), 88)}%` }}>
                  <span className="ms-tooltip__title">{row.label}</span>
                  <span className="ms-tooltip__meta">
                    {row.value.toFixed(1)}% · threshold {threshold}%
                  </span>
                </span>
              )}
            </div>
          </div>
        )
      })}

      <div className="ms-legend">
        {rows.map((row) => (
          <span className="ms-legend__item" key={row.key}>
            <span className="ms-legend__swatch" style={{ background: row.colour }} />
            {row.label}
          </span>
        ))}
        <span className="ms-legend__item">
          <span
            className="ms-legend__swatch"
            style={{ background: 'rgba(226,232,240,0.55)', width: 3, borderRadius: 1 }}
          />
          {threshold}% decision threshold
        </span>
      </div>

      <button
        type="button"
        className="ms-table-toggle"
        aria-expanded={showTable}
        onClick={() => setShowTable((v) => !v)}
      >
        {showTable ? 'Hide data table' : 'View as data table'}
      </button>

      {showTable && (
        <table className="ms-table">
          <caption className="ms-sr-only">Predicted class probabilities</caption>
          <thead>
            <tr><th scope="col">Class</th><th scope="col">Probability</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <th scope="row" style={{ fontWeight: 500 }}>{row.label}</th>
                <td>{row.value.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

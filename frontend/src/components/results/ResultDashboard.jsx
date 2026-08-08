import {
  ShieldCheck, ShieldAlert, AlertTriangle, AlertOctagon,
  CheckCircle2, Info, Scale, Brain, Activity,
} from 'lucide-react'
import RiskGauge from '../charts/RiskGauge'
import ProbabilityBars from '../charts/ProbabilityBars'
import FactorBalance from '../charts/FactorBalance'
import ShapViewer from '../charts/ShapViewer'
import Reveal from '../ui/Reveal'
import Tilt3D from '../ui/Tilt3D'

/* Severity presentation. A status colour never travels alone — each level
   carries its own icon and its own word, so the meaning survives greyscale,
   colour-vision deficiency and forced-colours mode alike. */
const SEVERITY = {
  r: { colour: 'var(--status-critical)', Icon: AlertOctagon,  tag: 'Critical' },
  y: { colour: 'var(--status-warn)',     Icon: AlertTriangle, tag: 'Moderate' },
  g: { colour: 'var(--status-good)',     Icon: CheckCircle2,  tag: 'Protective' },
}

function FactorList({ items, emptyText, emptyLevel }) {
  if (!items.length) {
    const fallback = SEVERITY[emptyLevel]
    return (
      <div className="factor-item" style={{ '--factor-color': fallback.colour }}>
        <span className="factor-item__icon"><fallback.Icon size={16} aria-hidden="true" /></span>
        <span>{emptyText}</span>
      </div>
    )
  }

  return (
    /* ms-stagger drives the entrance from CSS animation-delay. An .ms-reveal
       here would be inert — it mounts already visible, so there is no state
       change for its transition to run against. */
    <ul className="ms-stagger" style={{ listStyle: 'none', margin: 0, padding: 0 }}>
      {items.map((item, i) => {
        const sev = SEVERITY[item.level] ?? SEVERITY.y
        return (
          <li
            key={item.text}
            className="factor-item"
            style={{ '--factor-color': sev.colour, '--i': i }}
          >
            <span className="factor-item__icon"><sev.Icon size={16} aria-hidden="true" /></span>
            <span>
              <span className="factor-item__tag">{sev.tag}</span>
              <br />
              {item.text}
            </span>
          </li>
        )
      })}
    </ul>
  )
}

/**
 * The full result view, shared by the v2 diabetes model and the v3
 * complication model. Both return the same prediction shape, so both get the
 * same polished dashboard — only the labels, accent and copy differ.
 */
export default function ResultDashboard({
  result,
  risks,
  goods,
  recommendations,
  accent,                    // 'sky' | 'violet'
  assessmentLabel,
  highRiskText,
  lowRiskText,
  negativeLabel,
  positiveLabel,
  gaugeCaption,
  shapDescription,
  disclaimer,
}) {
  const isHigh = result.prediction === 1
  const statusColour = isHigh ? 'var(--status-critical)' : 'var(--status-good)'
  const accentHex = accent === 'violet' ? '#8b5cf6' : '#0284c7'
  const positiveColour = isHigh ? '#ef4444' : accentHex

  return (
    <div className="dashboard-grid">
      {/* Screen-reader announcement of the headline call, on arrival. */}
      <p className="ms-sr-only" role="status" aria-live="polite">
        {assessmentLabel}: {isHigh ? highRiskText : lowRiskText}.
        {' '}{positiveLabel} {result.probability_positive.toFixed(1)} percent.
      </p>

      {/* ── Headline banner ─────────────────────────────────────────────── */}
      <div className={`result-banner ${isHigh ? 'high-risk' : 'low-risk'}`}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.1rem' }}>
          <span className="result-banner__icon" style={{ color: statusColour }}>
            {isHigh
              ? <ShieldAlert size={30} aria-hidden="true" />
              : <ShieldCheck size={30} aria-hidden="true" />}
          </span>
          <span>
            <span className="result-banner__label">{assessmentLabel}</span>
            <br />
            {isHigh ? highRiskText : lowRiskText}
          </span>
        </div>
        <div style={{ fontVariantNumeric: 'tabular-nums' }}>
          {result.probability_positive.toFixed(1)}%
        </div>
      </div>

      {/* ── Gauge + probability bars ────────────────────────────────────── */}
      <Reveal>
        <Tilt3D className="glass-panel" max={4}>
          <h3 className="ms-panel-title">
            <Activity size={17} color={accentHex} aria-hidden="true" />
            Probability Breakdown
          </h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(min(240px, 100%), 1fr))',
            gap: 'var(--sp-5)',
            alignItems: 'center',
          }}>
            <div style={{ display: 'grid', placeItems: 'center' }}>
              <RiskGauge
                value={result.probability_positive}
                label={isHigh ? highRiskText : lowRiskText}
                accent={statusColour}
                caption={gaugeCaption}
              />
            </div>

            <div>
              <ProbabilityBars
                negative={{ label: negativeLabel, value: result.probability_negative }}
                positive={{ label: positiveLabel, value: result.probability_positive }}
                positiveColour={positiveColour}
              />
            </div>
          </div>
        </Tilt3D>
      </Reveal>

      {/* ── Factor balance ──────────────────────────────────────────────── */}
      <Reveal delay={60}>
        <div className="glass-panel">
          <h3 className="ms-panel-title">
            <Scale size={17} color={accentHex} aria-hidden="true" />
            Clinical Signal Balance
          </h3>
          <p className="ms-panel-sub">
            Every signal detected in this patient's data, weighed against the
            neutral centre line. Bars extending left work against the patient;
            bars extending right work in their favour.
          </p>
          <FactorBalance risks={risks} goods={goods} />
        </div>
      </Reveal>

      {/* ── Factor detail ───────────────────────────────────────────────── */}
      <div className="ms-grid-2">
        <Reveal>
          <Tilt3D className="glass-panel" max={4} style={{ height: '100%' }}>
            <h3 className="ms-panel-title">
              <AlertTriangle size={17} color="var(--status-critical)" aria-hidden="true" />
              Risk Factors
              <span
                className="ms-panel-title__count"
                style={{
                  background: 'rgba(239,68,68,0.16)',
                  color: 'var(--status-critical-soft)',
                  border: '1px solid rgba(239,68,68,0.3)',
                }}
              >
                {risks.length}
              </span>
            </h3>
            <FactorList
              items={risks}
              emptyText="No significant risk factors identified"
              emptyLevel="g"
            />
          </Tilt3D>
        </Reveal>

        <Reveal delay={80}>
          <Tilt3D className="glass-panel" max={4} style={{ height: '100%' }}>
            <h3 className="ms-panel-title">
              <CheckCircle2 size={17} color="var(--status-good)" aria-hidden="true" />
              Positive Indicators
              <span
                className="ms-panel-title__count"
                style={{
                  background: 'rgba(5,150,105,0.16)',
                  color: 'var(--status-good-soft)',
                  border: '1px solid rgba(5,150,105,0.32)',
                }}
              >
                {goods.length}
              </span>
            </h3>
            <FactorList
              items={goods}
              emptyText="No strong positive indicators detected"
              emptyLevel="r"
            />
          </Tilt3D>
        </Reveal>
      </div>

      {/* ── Recommendations ─────────────────────────────────────────────── */}
      <Reveal>
        <div className="glass-panel">
          <h3 className="ms-panel-title">
            <Info size={17} color={accentHex} aria-hidden="true" />
            Clinical Recommendations
          </h3>
          <div className="ms-rec-grid ms-stagger">
            {recommendations.map((rec, i) => (
              <div className="ms-rec" key={rec.text} style={{ '--i': i }}>
                <span className="ms-rec__icon" aria-hidden="true">{rec.icon}</span>
                <span>{rec.text}</span>
              </div>
            ))}
          </div>
        </div>
      </Reveal>

      {/* ── SHAP ────────────────────────────────────────────────────────── */}
      <Reveal>
        <div className="glass-panel">
          <h3 className="ms-panel-title">
            <Brain size={17} color={accentHex} aria-hidden="true" />
            Explainable AI · SHAP Attribution
          </h3>
          <p className="ms-panel-sub">{shapDescription}</p>
          <ShapViewer src={result.shap_image_base64} />
        </div>
      </Reveal>

      <Reveal>
        <p className="ms-disclaimer">
          ⚠️ <strong>Medical Disclaimer</strong> — {disclaimer}
        </p>
      </Reveal>
    </div>
  )
}

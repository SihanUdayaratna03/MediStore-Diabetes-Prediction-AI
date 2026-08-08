import { Activity, ArrowRight, ShieldCheck, Brain, Sparkles } from 'lucide-react'
import CountUp from '../components/ui/CountUp'
import Reveal from '../components/ui/Reveal'

const PROOF = [
  { value: 101766, decimals: 0, label: 'Training records', format: (n) => n.toLocaleString() },
  { value: 60, decimals: 0, suffix: '+', label: 'Clinical features' },
  { value: 2, decimals: 0, label: 'Validated models' },
]

/**
 * The front door. Same message and same brand as before — restaged with a
 * gradient wordmark, staggered entrance, floating trust badges and a haloed
 * primary action.
 */
export default function Landing({ onStart }) {
  return (
    <div className="landing-screen">
      <main className="landing-content" id="main">
        <div style={{ maxWidth: 940, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

          <Reveal>
            <span className="ms-pill ms-float">
              <Activity size={14} color="var(--sky-400)" aria-hidden="true" />
              Clinical Diagnostic System
            </span>
          </Reveal>

          <Reveal delay={90}>
            <h1 className="ms-hero__title" style={{ marginTop: 'var(--sp-5)' }}>
              Welcome to MediStore AI
            </h1>
          </Reveal>

          <Reveal delay={170}>
            <p className="ms-hero__lede">
              Empowering healthcare professionals with state-of-the-art Explainable AI
              to predict diabetes risk and complication risk with clinical precision.
            </p>
          </Reveal>

          <Reveal delay={250}>
            <button
              type="button"
              className="ms-btn ms-btn--primary ms-btn--lg ms-btn--halo"
              onClick={onStart}
            >
              Get Started <ArrowRight size={20} aria-hidden="true" />
            </button>
          </Reveal>

          <Reveal delay={330}>
            <div className="ms-hero__proof">
              {PROOF.map((item) => (
                <div className="ms-hero__proof-item" key={item.label}>
                  <div className="ms-hero__proof-value">
                    {item.format
                      ? item.format(item.value)
                      : <CountUp value={item.value} decimals={item.decimals} suffix={item.suffix ?? ''} />}
                  </div>
                  <div className="ms-hero__proof-label">{item.label}</div>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal delay={410}>
            <div style={{
              display: 'flex', gap: 'var(--sp-4)', flexWrap: 'wrap',
              justifyContent: 'center', marginTop: 'var(--sp-6)',
            }}>
              {[
                [ShieldCheck, 'SHAP-explained predictions'],
                [Brain, 'Ensemble & SVM models'],
                [Sparkles, 'Clinically framed output'],
              ].map(([Icon, text]) => (
                <span
                  key={text}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                    fontSize: '0.82rem', color: 'var(--text-dim)',
                  }}
                >
                  <Icon size={15} color="var(--sky-400)" aria-hidden="true" />
                  {text}
                </span>
              ))}
            </div>
          </Reveal>

        </div>
      </main>
    </div>
  )
}

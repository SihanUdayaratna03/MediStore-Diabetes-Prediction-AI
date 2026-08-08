import { useEffect, useState } from 'react'
import { useReducedMotion } from '../../hooks/useReducedMotion'

const STEPS = [
  'Validating patient inputs…',
  'Scaling features to the training distribution…',
  'Running model inference…',
  'Computing SHAP attributions…',
  'Composing the clinical report…',
]

/**
 * Shown while a prediction is in flight. A skeleton in the shape of the real
 * result (rather than a lone spinner) keeps the layout stable when the data
 * lands, and the rotating status line tells the clinician what is actually
 * happening instead of making them guess.
 */
export default function AnalysingState({ accent = 'sky' }) {
  const reduced = useReducedMotion()
  const [step, setStep] = useState(0)
  const colour = accent === 'violet' ? 'var(--violet-300)' : 'var(--sky-300)'

  useEffect(() => {
    if (reduced) return
    // Advance but never loop back — the last line holds until the result lands.
    const id = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 900)
    return () => clearInterval(id)
  }, [reduced])

  return (
    <div className="ms-analysing" role="status" aria-live="polite">
      <p className="ms-analysing__status" style={{ color: colour }}>
        <span className="spinner" aria-hidden="true" />
        {STEPS[step]}
      </p>
      <div className="ms-skeleton ms-analysing__banner" />
      <div className="ms-skeleton ms-analysing__panel" />
      <div className="ms-analysing__row">
        <div className="ms-skeleton ms-analysing__half" />
        <div className="ms-skeleton ms-analysing__half" />
      </div>
    </div>
  )
}

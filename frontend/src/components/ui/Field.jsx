import { useId } from 'react'

/**
 * Form primitives.
 *
 * The originals used bare <label> elements with no `htmlFor`, so clicking a
 * label did nothing and screen readers announced the inputs unnamed. These
 * wrappers generate an id and wire the association properly — the visual
 * result is unchanged, the semantics are not.
 */

export function Field({ label, value, children, hint }) {
  const id = useId()
  return (
    <div className="input-group">
      <label className="input-label" htmlFor={id}>
        <span>{label}</span>
        {value !== undefined && <span className="ms-value">{value}</span>}
      </label>
      {children(id)}
      {hint && (
        <p style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: '0.3rem', lineHeight: 1.5 }}>
          {hint}
        </p>
      )}
    </div>
  )
}

/** Slider whose track paints a filled portion via the --fill custom property. */
export function RangeField({ label, name, min, max, step = 1, value, onChange, unit = '' }) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <Field label={label} value={`${value}${unit}`}>
      {(id) => (
        <input
          id={id}
          type="range"
          className="input-field range"
          name={name}
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={onChange}
          style={{ '--fill': `${Math.max(0, Math.min(pct, 100))}%` }}
        />
      )}
    </Field>
  )
}

export function NumberField({ label, name, value, onChange, min, max, step, unit }) {
  return (
    <Field label={unit ? `${label} (${unit})` : label}>
      {(id) => (
        <input
          id={id}
          type="number"
          className="input-field"
          name={name}
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={onChange}
        />
      )}
    </Field>
  )
}

export function SelectField({ label, name, value, onChange, options }) {
  return (
    <Field label={label}>
      {(id) => (
        <select id={id} className="input-field" name={name} value={value} onChange={onChange}>
          {options.map(([val, text]) => (
            <option key={val} value={val}>{text}</option>
          ))}
        </select>
      )}
    </Field>
  )
}

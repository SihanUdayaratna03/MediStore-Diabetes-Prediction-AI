import CountUp from '../ui/CountUp'
import { useGrowIn } from '../../hooks/useGrowIn'

/**
 * The headline figure: one probability, shown as a hero number inside a radial
 * magnitude arc.
 *
 * Form choice — a single value with a natural 0–100 domain is a hero number,
 * not a chart. The arc is a magnitude cue around it, so there is no legend and
 * no axis. The colour is a *status* colour and never travels alone: `label`
 * renders as text beneath it and the caller pairs it with an icon.
 */
export default function RiskGauge({
  value,                 // 0–100
  label,                 // e.g. "High Risk"
  accent,                // status colour
  caption = 'Risk score',
  threshold = 50,
  size = 210,
}) {
  const grown = useGrowIn([value])
  const progress = grown ? value : 0

  const stroke = 14
  const radius = (size - stroke * 2) / 2
  const cx = size / 2
  const cy = size / 2

  // A 270° arc, opened at the bottom — the standard clinical dial read.
  const SWEEP = 270
  const START = 135
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * (SWEEP / 360)

  const clamped = Math.max(0, Math.min(progress, 100))
  const offset = arcLength * (1 - clamped / 100)

  // Tick position for the 50% decision threshold.
  const tickAngle = ((START + (threshold / 100) * SWEEP) * Math.PI) / 180
  const tickInner = radius - stroke / 2 - 3
  const tickOuter = radius + stroke / 2 + 3

  return (
    <figure className="ms-gauge" style={{ width: size, height: size, margin: 0 }}>
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        role="img"
        aria-label={`${label}. ${value.toFixed(1)} percent ${caption.toLowerCase()}.`}
      >
        <g transform={`rotate(${START} ${cx} ${cy})`}>
          <circle
            className="ms-gauge__track"
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
          />
          <circle
            className="ms-gauge__value"
            cx={cx}
            cy={cy}
            r={radius}
            fill="none"
            stroke={accent}
            color={accent}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
            strokeDashoffset={offset}
          />
        </g>

        {/* Decision threshold — the line that separates the two clinical calls */}
        <line
          x1={cx + Math.cos(tickAngle) * tickInner}
          y1={cy + Math.sin(tickAngle) * tickInner}
          x2={cx + Math.cos(tickAngle) * tickOuter}
          y2={cy + Math.sin(tickAngle) * tickOuter}
          stroke="rgba(226,232,240,0.55)"
          strokeWidth="2"
          strokeLinecap="round"
        />
      </svg>

      <figcaption className="ms-gauge__center">
        <div className="ms-gauge__number" style={{ color: accent }}>
          <CountUp value={value} decimals={1} suffix="%" />
        </div>
        <div className="ms-gauge__caption">{caption}</div>
      </figcaption>
    </figure>
  )
}

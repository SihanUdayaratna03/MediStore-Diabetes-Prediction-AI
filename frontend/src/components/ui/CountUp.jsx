import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from '../../hooks/useReducedMotion'

/**
 * Counts from 0 to `value` on mount and re-animates whenever `value` changes.
 * Skips straight to the final number under reduced motion — the information is
 * the number, not the animation, so it must never be withheld.
 */
export default function CountUp({
  value,
  decimals = 0,
  duration = 1100,
  suffix = '',
  prefix = '',
  className,
  style,
}) {
  const reduced = useReducedMotion()
  const [display, setDisplay] = useState(reduced ? value : 0)
  const frameRef = useRef(0)
  const guardRef = useRef(0)

  useEffect(() => {
    if (reduced || !Number.isFinite(value)) {
      setDisplay(Number.isFinite(value) ? value : 0)
      return
    }

    const start = performance.now()
    const from = 0

    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1)
      // easeOutExpo — fast off the line, settles softly on the real figure.
      const eased = t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
      setDisplay(from + (value - from) * eased)
      if (t < 1) frameRef.current = requestAnimationFrame(tick)
    }

    frameRef.current = requestAnimationFrame(tick)

    // Browsers pause requestAnimationFrame in a background tab. Without this
    // guard, a result that arrives while the tab is hidden would animate to
    // nowhere and sit at 0 forever — showing a clinician the wrong number.
    // The timer keeps running regardless, so the true value always lands.
    guardRef.current = setTimeout(() => setDisplay(value), duration + 120)

    return () => {
      cancelAnimationFrame(frameRef.current)
      clearTimeout(guardRef.current)
    }
  }, [value, duration, reduced])

  return (
    <span className={className} style={style}>
      {prefix}{display.toFixed(decimals)}{suffix}
    </span>
  )
}

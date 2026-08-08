import { useEffect, useState } from 'react'
import { useReducedMotion } from './useReducedMotion'

/**
 * Returns false for one tick after `deps` change, then true — giving a CSS
 * transition a 0 → value edge to animate from.
 *
 * Deliberately a setTimeout and not a requestAnimationFrame: browsers pause
 * rAF entirely in a background tab, so a chart whose data arrived while the
 * user was on another tab would stay collapsed at zero forever. Timers are
 * only throttled, never stopped, so the final state always lands.
 *
 * Under reduced motion it is true immediately — no growth, just the value.
 */
export function useGrowIn(deps = []) {
  const reduced = useReducedMotion()
  const [grown, setGrown] = useState(reduced)

  useEffect(() => {
    if (reduced) { setGrown(true); return }
    setGrown(false)
    const id = setTimeout(() => setGrown(true), 30)
    return () => clearTimeout(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reduced, ...deps])

  return grown
}

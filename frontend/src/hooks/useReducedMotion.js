import { useEffect, useState } from 'react'

/**
 * Tracks the OS "reduce motion" preference and keeps up if the user flips it
 * mid-session. Components use this to skip work entirely (e.g. never start the
 * canvas RAF loop) rather than merely animating to a zero-length duration.
 */
export function useReducedMotion() {
  const [reduced, setReduced] = useState(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return false
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  })

  useEffect(() => {
    if (!window.matchMedia) return
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const onChange = (e) => setReduced(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  return reduced
}

/** True when the pointer is a real mouse — tilt and gloss are mouse-only. */
export function useFinePointer() {
  const [fine, setFine] = useState(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return true
    return window.matchMedia('(hover: hover) and (pointer: fine)').matches
  })

  useEffect(() => {
    if (!window.matchMedia) return
    const mq = window.matchMedia('(hover: hover) and (pointer: fine)')
    const onChange = (e) => setFine(e.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  return fine
}

import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from '../../hooks/useReducedMotion'

const EXIT_MS = 260

/**
 * Cross-fades between screens with a slight z-depth push, so navigating feels
 * like moving through the interface rather than swapping a div.
 *
 * The outgoing screen is held on screen for one short exit animation, then the
 * incoming one mounts. `screenKey` is what identifies a screen change.
 */
export default function ScreenTransition({ screenKey, children }) {
  const reduced = useReducedMotion()
  const [rendered, setRendered] = useState({ key: screenKey, node: children })
  const [phase, setPhase] = useState('idle')
  const pending = useRef(null)
  const timer = useRef(0)

  useEffect(() => {
    // Same screen re-rendering (e.g. new result data) — pass it straight through.
    if (screenKey === rendered.key) {
      setRendered({ key: screenKey, node: children })
      return
    }

    if (reduced) {
      setRendered({ key: screenKey, node: children })
      window.scrollTo({ top: 0, behavior: 'auto' })
      return
    }

    pending.current = { key: screenKey, node: children }
    setPhase('exiting')

    clearTimeout(timer.current)
    timer.current = setTimeout(() => {
      if (pending.current) setRendered(pending.current)
      setPhase('idle')
      window.scrollTo({ top: 0, behavior: 'auto' })
    }, EXIT_MS)

    return () => clearTimeout(timer.current)
  }, [screenKey, children, rendered.key, reduced])

  return (
    <div className="ms-screen" data-phase={phase} key={rendered.key}>
      {rendered.node}
    </div>
  )
}

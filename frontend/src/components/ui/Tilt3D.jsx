import { useCallback, useRef } from 'react'
import { useFinePointer, useReducedMotion } from '../../hooks/useReducedMotion'

/**
 * Pointer-driven 3D tilt with a cursor-tracked gloss highlight.
 *
 * The rotation is written to CSS custom properties on the node rather than to
 * React state, so a pointermove never triggers a render — the whole effect
 * costs one style write per frame and stays on the compositor.
 *
 * Degrades to a plain container when the pointer is coarse (touch) or the user
 * has asked for reduced motion.
 */
export default function Tilt3D({
  as: Tag = 'div',
  max = 7,
  perspective = 1000,
  gloss = true,
  className = '',
  children,
  ...rest
}) {
  const ref = useRef(null)
  const raf = useRef(0)
  const fine = useFinePointer()
  const reduced = useReducedMotion()
  const enabled = fine && !reduced

  const handleMove = useCallback((e) => {
    if (!enabled) return
    const node = ref.current
    if (!node) return

    cancelAnimationFrame(raf.current)
    const { clientX, clientY } = e

    raf.current = requestAnimationFrame(() => {
      const rect = node.getBoundingClientRect()
      if (!rect.width || !rect.height) return

      const px = (clientX - rect.left) / rect.width   // 0..1
      const py = (clientY - rect.top) / rect.height   // 0..1

      node.style.setProperty('--tilt-y', `${(px - 0.5) * 2 * max}deg`)
      node.style.setProperty('--tilt-x', `${(0.5 - py) * 2 * max}deg`)
      node.style.setProperty('--gloss-x', `${px * 100}%`)
      node.style.setProperty('--gloss-y', `${py * 100}%`)
    })
  }, [enabled, max])

  const handleEnter = useCallback(() => {
    if (!enabled) return
    ref.current?.setAttribute('data-active', 'true')
  }, [enabled])

  const handleLeave = useCallback(() => {
    cancelAnimationFrame(raf.current)
    const node = ref.current
    if (!node) return
    node.setAttribute('data-active', 'false')
    node.style.setProperty('--tilt-x', '0deg')
    node.style.setProperty('--tilt-y', '0deg')
  }, [])

  return (
    <Tag
      ref={ref}
      className={`ms-tilt ${className}`.trim()}
      data-active="false"
      style={{ '--tilt-perspective': `${perspective}px` }}
      onPointerMove={handleMove}
      onPointerEnter={handleEnter}
      onPointerLeave={handleLeave}
      onBlur={handleLeave}
      {...rest}
    >
      {children}
      {gloss && enabled && <span className="ms-tilt__gloss" aria-hidden="true" />}
    </Tag>
  )
}

/** A child that floats above the card face when the parent is tilted. */
export function TiltLayer({ depth = 20, className = '', children, ...rest }) {
  return (
    <div
      className={`ms-tilt__layer ${className}`.trim()}
      style={{ '--depth': `${depth}px` }}
      {...rest}
    >
      {children}
    </div>
  )
}

import { useEffect, useRef } from 'react'
import { useReducedMotion } from '../../hooks/useReducedMotion'

/**
 * The ambient layer behind the whole app: drifting colour orbs (CSS), a faint
 * clinical grid (CSS), and a canvas particle constellation that reacts to the
 * pointer with a gentle parallax.
 *
 * Performance notes — this runs on every screen, so it is deliberately cheap:
 *   • particle count scales with viewport area and is hard-capped
 *   • devicePixelRatio is clamped to 2 (a 3x phone would otherwise draw 9x)
 *   • the RAF loop stops entirely when the tab is hidden
 *   • nothing here re-renders React; the loop owns the canvas directly
 *   • with `prefers-reduced-motion` the loop never starts — one static frame
 */
export default function AuroraField() {
  const canvasRef = useRef(null)
  const reduced = useReducedMotion()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d', { alpha: true })
    if (!ctx) return

    let width = 0
    let height = 0
    let dpr = 1
    let particles = []
    let frame = 0
    let running = true

    // Pointer position drives a slow parallax offset, eased toward the target
    // so the field glides rather than snapping.
    const pointer = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5 }

    const PALETTE = [
      [56, 189, 248],   // sky
      [167, 139, 250],  // violet
      [125, 211, 252],  // light sky
    ]

    const setup = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = Math.floor(width * dpr)
      canvas.height = Math.floor(height * dpr)
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      const density = (width * height) / 19000
      const count = Math.max(24, Math.min(Math.round(density), 90))

      particles = Array.from({ length: count }, () => {
        const colour = PALETTE[Math.floor(Math.random() * PALETTE.length)]
        return {
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          r: Math.random() * 1.7 + 0.7,
          // Depth 0..1 — drives size, alpha and parallax strength together, so
          // near particles feel genuinely closer than far ones.
          depth: Math.random(),
          colour,
          phase: Math.random() * Math.PI * 2,
        }
      })
    }

    const drawFrame = (animate) => {
      ctx.clearRect(0, 0, width, height)

      if (animate) {
        pointer.x += (pointer.tx - pointer.x) * 0.045
        pointer.y += (pointer.ty - pointer.y) * 0.045
      }

      const px = (pointer.x - 0.5) * 42
      const py = (pointer.y - 0.5) * 42

      // Link nearby particles — the "neural mesh" read. O(n²) is fine at n ≤ 90.
      const linkDist = Math.min(width, height) * 0.16
      for (let i = 0; i < particles.length; i++) {
        const a = particles[i]
        const ax = a.x + px * a.depth
        const ay = a.y + py * a.depth

        for (let j = i + 1; j < particles.length; j++) {
          const b = particles[j]
          const bx = b.x + px * b.depth
          const by = b.y + py * b.depth
          const dx = ax - bx
          const dy = ay - by
          const dist = Math.hypot(dx, dy)
          if (dist > linkDist) continue

          const strength = (1 - dist / linkDist) * 0.28
          ctx.strokeStyle = `rgba(125, 211, 252, ${strength.toFixed(3)})`
          ctx.lineWidth = 0.7
          ctx.beginPath()
          ctx.moveTo(ax, ay)
          ctx.lineTo(bx, by)
          ctx.stroke()
        }
      }

      for (const p of particles) {
        if (animate) {
          p.x += p.vx
          p.y += p.vy
          p.phase += 0.012

          if (p.x < -30) p.x = width + 30
          if (p.x > width + 30) p.x = -30
          if (p.y < -30) p.y = height + 30
          if (p.y > height + 30) p.y = -30
        }

        const x = p.x + px * p.depth
        const y = p.y + py * p.depth
        const twinkle = animate ? 0.55 + Math.sin(p.phase) * 0.25 : 0.6
        const radius = p.r * (0.55 + p.depth * 0.8)
        const [r, g, b] = p.colour

        const glow = ctx.createRadialGradient(x, y, 0, x, y, radius * 5)
        glow.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${(twinkle * 0.5).toFixed(3)})`)
        glow.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`)
        ctx.fillStyle = glow
        ctx.beginPath()
        ctx.arc(x, y, radius * 5, 0, Math.PI * 2)
        ctx.fill()

        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${twinkle.toFixed(3)})`
        ctx.beginPath()
        ctx.arc(x, y, radius, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    const loop = () => {
      if (!running) return
      drawFrame(true)
      frame = requestAnimationFrame(loop)
    }

    const onPointerMove = (e) => {
      pointer.tx = e.clientX / width
      pointer.ty = e.clientY / height
    }

    // Pause off-screen: a hidden tab should cost nothing.
    const onVisibility = () => {
      if (document.hidden) {
        running = false
        cancelAnimationFrame(frame)
      } else if (!reduced) {
        running = true
        frame = requestAnimationFrame(loop)
      }
    }

    let resizeTimer
    const onResize = () => {
      clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => {
        setup()
        if (reduced) drawFrame(false)
      }, 160)
    }

    setup()

    if (reduced) {
      drawFrame(false)
    } else {
      window.addEventListener('pointermove', onPointerMove, { passive: true })
      frame = requestAnimationFrame(loop)
    }

    window.addEventListener('resize', onResize)
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      running = false
      cancelAnimationFrame(frame)
      clearTimeout(resizeTimer)
      window.removeEventListener('pointermove', onPointerMove)
      window.removeEventListener('resize', onResize)
      document.removeEventListener('visibilitychange', onVisibility)
    }
  }, [reduced])

  return (
    <div className="ms-field" aria-hidden="true">
      <div className="ms-orb ms-orb--sky" />
      <div className="ms-orb ms-orb--violet" />
      <div className="ms-orb ms-orb--teal" />
      <div className="ms-field__grid" />
      <canvas ref={canvasRef} className="ms-field__canvas" />
    </div>
  )
}

import { useEffect, useRef, useState } from 'react'

/**
 * Reveals its children the first time they scroll into view.
 *
 * One IntersectionObserver per element, disconnected as soon as it fires —
 * nothing keeps observing after the reveal, so a long dashboard doesn't
 * accumulate live observers.
 */
export default function Reveal({ delay = 0, className = '', children, ...rest }) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    // No IntersectionObserver (or SSR) — show immediately rather than hide.
    if (typeof IntersectionObserver === 'undefined') {
      setVisible(true)
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return
        setVisible(true)
        observer.disconnect()
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      className={`ms-reveal ${className}`.trim()}
      data-visible={visible}
      style={{ '--reveal-delay': `${delay}ms` }}
      {...rest}
    >
      {children}
    </div>
  )
}

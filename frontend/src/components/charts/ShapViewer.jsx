import { useEffect, useRef, useState } from 'react'
import { Maximize2, X, ImageOff } from 'lucide-react'

/**
 * Displays the SHAP explanation plot returned by the model server, with a
 * click-to-zoom lightbox.
 *
 * The plot arrives as a base64 PNG on a white matplotlib canvas. Rather than
 * dropping a white rectangle into a dark UI, the image is inverted and
 * hue-rotated in CSS (see .ms-shap img) — which preserves the red/blue SHAP
 * semantics while letting it sit inside the theme. The lightbox uses a native
 * <dialog>, so focus trapping and Escape-to-close come from the platform.
 */
export default function ShapViewer({ src, alt = 'SHAP feature attribution plot' }) {
  const [open, setOpen] = useState(false)
  const [failed, setFailed] = useState(false)
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    const onClose = () => setOpen(false)
    dialog.addEventListener('close', onClose)
    return () => dialog.removeEventListener('close', onClose)
  }, [])

  if (!src || failed) {
    return (
      <div className="ms-shap" style={{ flexDirection: 'column', gap: '0.6rem', color: 'var(--status-critical-soft)' }}>
        <ImageOff size={26} aria-hidden="true" />
        <span style={{ fontSize: '0.85rem' }}>SHAP explanation could not be generated.</span>
      </div>
    )
  }

  return (
    <>
      {/* The control sits above the plot rather than floating over it — a
          waterfall puts its base-value label in the top-right corner, and an
          overlaid button covered exactly that number. */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 'var(--sp-2)' }}>
        <button
          type="button"
          className="ms-btn"
          onClick={() => setOpen(true)}
          style={{ padding: '0.4rem 0.75rem', fontSize: '0.78rem' }}
        >
          <Maximize2 size={14} aria-hidden="true" /> Enlarge
        </button>
      </div>

      <div className="ms-shap">
        <img
          src={src}
          alt={alt}
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
          onClick={() => setOpen(true)}
        />
      </div>

      <dialog ref={dialogRef} className="ms-lightbox" aria-label="SHAP explanation, enlarged">
        <button
          type="button"
          className="ms-btn ms-lightbox__close"
          onClick={() => setOpen(false)}
          autoFocus
        >
          <X size={16} aria-hidden="true" /> Close
        </button>
        {open && <img src={src} alt={alt} />}
      </dialog>
    </>
  )
}

import { Suspense, lazy, useCallback, useState } from 'react'
import AuroraField from './components/background/AuroraField'
import ScreenTransition from './components/ui/ScreenTransition'
import Landing from './screens/Landing'
import ModeSelect from './screens/ModeSelect'
import DiabetesPredictor from './screens/DiabetesPredictor'
import DocIntelligence from './screens/DocIntelligence'
import './App.css'

// The v3 module is the heavier of the two (52 fields, a large option map), and
// most sessions never open it — so it is split out and fetched on demand.
const ComplicationPredictor = lazy(() => import('./screens/ComplicationPredictor'))

function ScreenFallback() {
  return (
    <div className="landing-screen">
      <div className="landing-content">
        <span className="spinner" aria-hidden="true" />
        <p style={{ marginTop: 'var(--sp-4)', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
          Loading module…
        </p>
      </div>
    </div>
  )
}

/**
 * Screen router. The app has five screens and no URL routing, so navigation is
 * plain state — wrapped in ScreenTransition to give each change a real
 * enter/exit rather than an instant swap.
 */
export default function App() {
  // 'landing' | 'mode-select' | 'v2' | 'v3' | 'doc-intelligence'
  const [screen, setScreen] = useState('landing')

  const goSelect = useCallback(() => setScreen('mode-select'), [])
  const goLanding = useCallback(() => setScreen('landing'), [])

  let view
  if (screen === 'landing') {
    view = <Landing onStart={goSelect} />
  } else if (screen === 'mode-select') {
    view = <ModeSelect onSelect={setScreen} onBack={goLanding} />
  } else if (screen === 'v2') {
    view = <DiabetesPredictor onBack={goSelect} />
  } else if (screen === 'doc-intelligence') {
    view = <DocIntelligence onBack={goSelect} />
  } else {
    view = (
      <Suspense fallback={<ScreenFallback />}>
        <ComplicationPredictor onBack={goSelect} />
      </Suspense>
    )
  }

  return (
    <>
      <a className="ms-skip-link" href="#main">Skip to main content</a>
      <AuroraField />
      <ScreenTransition screenKey={screen}>{view}</ScreenTransition>
    </>
  )
}

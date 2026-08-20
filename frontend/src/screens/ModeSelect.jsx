import { Droplet, Brain, FileText, MapPin, ArrowRight, ArrowLeft, Zap } from 'lucide-react'
import Tilt3D, { TiltLayer } from '../components/ui/Tilt3D'
import Reveal from '../components/ui/Reveal'

const MODULES = [
  {
    id: 'v2',
    accent: 'sky',
    Icon: Droplet,
    iconColour: '#38bdf8',
    name: 'Diabetes Risk Predictor',
    version: 'v2 · SVM Model',
    description:
      "Predicts diabetes presence from 8 Pima biomarkers — glucose, BMI, age, insulin, "
      + 'blood pressure, skin thickness, pregnancies, and genetic predisposition.',
    tags: ['8 Biomarkers', 'SVM + SHAP', 'Pima Dataset', '~85% Accuracy'],
    badge: null,
  },
  {
    id: 'v3',
    accent: 'violet',
    Icon: Brain,
    iconColour: '#a78bfa',
    name: 'Complication Risk Predictor',
    version: 'v3 · XGB + LGBM + RF Ensemble',
    description:
      'Predicts early hospital readmission risk (a proxy for poor glycaemic control and '
      + 'complications) from 52 clinical features across 101,766 UCI hospital records.',
    tags: ['52 Features', 'XGB+LGBM+RF', 'UCI-130 Dataset', 'Readmission Risk'],
    badge: 'New',
  },
  {
    id: 'doc-intelligence',
    accent: 'emerald',
    Icon: FileText,
    iconColour: '#34d399',
    name: 'Document Intelligence',
    version: 'RAG · Gemini Vision + OCR',
    description:
      'Upload a medical PDF, doctor\'s report, or image and ask questions about '
      + 'its contents. Powered by Gemini Vision, OCR, and Multi-Agent RAG.',
    tags: ['PDF Upload', 'Image OCR', 'Multi-Agent RAG', 'Citation Tracking'],
    badge: 'New',
  },
  {
    id: 'care-locator',
    accent: 'sky',
    Icon: MapPin,
    iconColour: '#38bdf8',
    name: 'Care & Supply Locator',
    version: 'Google Maps · Real-Time Network',
    description:
      'Interactive Google Map connecting patients to endocrinologists, diagnostic labs, '
      + 'and 24/7 pharmacies stocked with insulin, CGMs, and testing strips.',
    tags: ['Google Maps API', 'Endocrinology', '24/7 Pharmacies', 'Insulin Cold-Chain'],
    badge: 'Live',
  },
]

/**
 * Module picker. The two cards are the app's showpiece 3D moment — they tilt
 * toward the cursor, catch a gloss highlight, and lift their icon and title
 * off the card face for real parallax depth.
 */
export default function ModeSelect({ onSelect, onBack }) {
  return (
    <div className="landing-screen">
      <main className="landing-content" id="main">

        <Reveal>
          <span className="ms-pill">
            <Zap size={13} color="var(--sky-400)" aria-hidden="true" />
            Select a Prediction Module
          </span>
        </Reveal>

        <Reveal delay={80}>
          <h2 className="ms-hero__title" style={{ fontSize: 'clamp(2rem, 5vw, 2.9rem)', margin: 'var(--sp-4) 0 var(--sp-3)' }}>
            Choose Your Predictor
          </h2>
        </Reveal>

        <Reveal delay={150}>
          <p className="ms-hero__lede" style={{ marginBottom: 'var(--sp-6)' }}>
            MediStore AI offers two clinically validated models. Select the one that
            matches your patient's assessment needs.
          </p>
        </Reveal>

        <div className="ms-mode-grid">
          {MODULES.map((mod, i) => (
            <Reveal delay={200 + i * 100} key={mod.id}>
              <Tilt3D
                as="button"
                type="button"
                max={8}
                perspective={1200}
                className={`mode-card mode-card--${mod.accent}`}
                onClick={() => onSelect(mod.id)}
                aria-label={`${mod.name}, ${mod.version}. Open predictor.`}
              >
                <span className="mode-card__orb" aria-hidden="true" />
                {mod.badge && <span className="mode-card__badge">{mod.badge}</span>}

                <TiltLayer depth={38}>
                  <span className="mode-card__icon">
                    <mod.Icon size={24} color={mod.iconColour} aria-hidden="true" />
                  </span>
                </TiltLayer>

                <TiltLayer depth={22}>
                  <span className="mode-card__name" style={{ display: 'block' }}>{mod.name}</span>
                  <span className="mode-card__version" style={{ display: 'block' }}>{mod.version}</span>
                </TiltLayer>

                <TiltLayer depth={10}>
                  <span className="mode-card__desc" style={{ display: 'block' }}>{mod.description}</span>
                  <span className="mode-card__tags">
                    {mod.tags.map((tag) => (
                      <span className={`ms-tag ms-tag--${mod.accent}`} key={tag}>{tag}</span>
                    ))}
                  </span>
                  <span className="mode-card__cta">
                    Open Predictor <ArrowRight size={16} aria-hidden="true" />
                  </span>
                </TiltLayer>
              </Tilt3D>
            </Reveal>
          ))}
        </div>

        <Reveal delay={420}>
          <button
            type="button"
            className="ms-btn ms-btn--ghost"
            onClick={onBack}
            style={{ marginTop: 'var(--sp-6)' }}
          >
            <ArrowLeft size={14} aria-hidden="true" /> Back to Home
          </button>
        </Reveal>

      </main>
    </div>
  )
}

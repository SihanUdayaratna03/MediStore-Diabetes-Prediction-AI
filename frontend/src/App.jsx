import { useState } from 'react'
import axios from 'axios'
import {
  Activity, Stethoscope, Droplet, Heart, User,
  ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle,
  Info, ArrowRight, ArrowLeft, Brain, Zap,
} from 'lucide-react'
import ComplicationPredictor from './ComplicationPredictor'
import './App.css'

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  // 'landing' | 'mode-select' | 'v2' | 'v3'
  const [screen, setScreen] = useState('landing')

  const [formData, setFormData] = useState({
    pregnancies: 0,
    glucose: 120,
    blood_pressure: 70,
    skin_thickness: 20,
    insulin: 80,
    bmi: 25.0,
    dpf: 0.5,
    age: 30,
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('http://localhost:8000/predict', formData)
      setResult(res.data)
    } catch (err) {
      setError('Failed to connect to the prediction server. Ensure FastAPI is running on port 8000.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getFactors = () => {
    const risks = [], goods = []
    const { glucose, bmi, age, blood_pressure: bp, dpf, insulin } = formData

    if (glucose > 125) risks.push({ level: 'r', text: 'High plasma glucose (>125 mg/dL) — key diabetes marker' })
    else if (glucose < 100) goods.push({ level: 'g', text: 'Normal fasting glucose — within healthy range' })

    if (bmi > 30) risks.push({ level: 'r', text: 'Obesity — BMI >30 significantly raises diabetes risk' })
    else if (bmi >= 18.5 && bmi <= 24.9) goods.push({ level: 'g', text: 'Healthy BMI (18.5–24.9) — reduces metabolic risk' })
    else if (bmi >= 25) risks.push({ level: 'y', text: 'Overweight — BMI between 25–30, borderline risk' })

    if (age > 45) risks.push({ level: 'y', text: 'Age >45 — diabetes prevalence increases with age' })
    else if (age < 35) goods.push({ level: 'g', text: 'Younger age — lower baseline diabetes risk' })

    if (bp > 80) risks.push({ level: 'r', text: 'Elevated diastolic BP (>80 mm Hg) — metabolic risk factor' })
    else if (bp >= 60 && bp <= 80) goods.push({ level: 'g', text: 'Diastolic blood pressure within normal range' })

    if (dpf > 0.8) risks.push({ level: 'r', text: 'High genetic predisposition (DPF >0.8)' })
    else if (dpf > 0.5) risks.push({ level: 'y', text: 'Moderate genetic predisposition (DPF >0.5)' })
    else goods.push({ level: 'g', text: 'Low genetic predisposition (DPF ≤0.5)' })

    if (insulin > 200) risks.push({ level: 'y', text: 'Elevated insulin — possible insulin resistance' })

    return { risks, goods }
  }

  const { risks, goods } = getFactors()

  const recommendations = result?.prediction === 1 ? [
    { icon: '🏥', text: 'Consult a healthcare professional or endocrinologist as soon as possible' },
    { icon: '🧪', text: 'Request a full diabetes panel: HbA1c, fasting plasma glucose, oral glucose tolerance test' },
    { icon: '📊', text: 'Begin self-monitoring of blood glucose — aim for pre-meal readings below 7 mmol/L' },
    { icon: '🥗', text: 'Reduce dietary refined sugars and processed carbohydrates; increase fibre intake' },
    { icon: '🏃', text: 'Start structured physical activity — 150 min/week moderate aerobic exercise' },
    { icon: '💊', text: 'Discuss pharmacological management options with your doctor' },
  ] : [
    { icon: '📅', text: 'Schedule annual blood glucose and HbA1c screening tests' },
    { icon: '🥗', text: 'Maintain a balanced diet — Mediterranean or low-GI dietary patterns recommended' },
    { icon: '🏃', text: 'Stay physically active — at least 150 minutes of moderate exercise per week' },
    { icon: '⚖️', text: 'Maintain a healthy weight; even 5–7% weight reduction lowers diabetes risk' },
    { icon: '💧', text: 'Stay well-hydrated — aim for 2–3 litres of water daily' },
    { icon: '😴', text: 'Prioritise 7–9 hours of quality sleep — poor sleep increases insulin resistance' },
  ]

  // ── LANDING ──────────────────────────────────────────────────────────────────
  if (screen === 'landing') {
    return (
      <div className="landing-screen fade-in-up">
        <div className="landing-content">
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            padding: '2rem', textAlign: 'center', maxWidth: '900px',
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              marginBottom: '1.5rem', padding: '0.5rem 1rem',
              background: 'rgba(0,0,0,0.4)', borderRadius: '99px',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'white', fontSize: '0.85rem', fontWeight: 'bold',
              textTransform: 'uppercase', letterSpacing: '0.1em', backdropFilter: 'blur(4px)',
            }}>
              <Activity size={16} color="var(--accent)" /> Clinical Diagnostic System
            </div>

            <h1 style={{
              fontSize: '4.5rem', fontFamily: 'Space Grotesk', marginBottom: '1.5rem',
              fontWeight: 800, textShadow: '0 4px 20px rgba(0,0,0,0.6)', color: 'white',
            }}>
              Welcome to MediStore AI
            </h1>

            <p style={{
              fontSize: '1.2rem', color: 'rgba(255,255,255,0.9)', marginBottom: '3rem',
              maxWidth: '600px', lineHeight: '1.6', textShadow: '0 2px 10px rgba(0,0,0,0.5)',
            }}>
              Empowering healthcare professionals with state-of-the-art Explainable AI to predict
              diabetes risk and complication risk with clinical precision.
            </p>

            <button
              onClick={() => setScreen('mode-select')}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                padding: '1.2rem 3rem', fontSize: '1.1rem', fontWeight: 700,
                fontFamily: 'Space Grotesk',
                background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                color: 'white', border: 'none', borderRadius: '99px',
                cursor: 'pointer', transition: 'all 0.3s ease',
                boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
              }}
              onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 15px 35px rgba(0,0,0,0.6)' }}
              onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 10px 25px rgba(0,0,0,0.4)' }}
            >
              Get Started <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ── MODE SELECT ──────────────────────────────────────────────────────────────
  if (screen === 'mode-select') {
    return (
      <div className="landing-screen fade-in-up">
        <div className="landing-content">
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
              marginBottom: '1.2rem', padding: '0.45rem 1rem',
              background: 'rgba(0,0,0,0.4)', borderRadius: '99px',
              border: '1px solid rgba(255,255,255,0.2)',
              color: 'rgba(255,255,255,0.85)', fontSize: '0.78rem', fontWeight: 700,
              textTransform: 'uppercase', letterSpacing: '0.1em', backdropFilter: 'blur(4px)',
            }}>
              <Zap size={13} color="var(--accent)" /> Select a Prediction Module
            </div>
            <h2 style={{
              fontFamily: 'Space Grotesk', fontSize: '2.8rem', fontWeight: 800,
              color: 'white', marginBottom: '0.75rem', textShadow: '0 4px 20px rgba(0,0,0,0.6)',
            }}>
              Choose Your Predictor
            </h2>
            <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '1rem', maxWidth: '520px', lineHeight: 1.6 }}>
              MediStore AI offers two clinically validated models. Select the one that
              matches your patient's assessment needs.
            </p>
          </div>

          {/* Mode cards */}
          <div style={{ display: 'flex', gap: '1.5rem', maxWidth: '820px', width: '100%', flexWrap: 'wrap', justifyContent: 'center' }}>

            {/* V2 Card */}
            <button
              onClick={() => setScreen('v2')}
              className="mode-card"
              style={{
                flex: '1 1 340px', maxWidth: 380,
                background: 'rgba(15,23,42,0.75)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(56,189,248,0.35)', borderRadius: '20px',
                padding: '2rem 1.8rem', cursor: 'pointer', textAlign: 'left',
                transition: 'all 0.25s ease', position: 'relative', overflow: 'hidden',
              }}
              onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-6px)'; e.currentTarget.style.borderColor = 'rgba(56,189,248,0.75)'; e.currentTarget.style.boxShadow = '0 20px 50px rgba(2,132,199,0.25)' }}
              onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = 'rgba(56,189,248,0.35)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              {/* Glow orb */}
              <div style={{
                position: 'absolute', top: -40, right: -40,
                width: 120, height: 120, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(56,189,248,0.2) 0%, transparent 70%)',
                pointerEvents: 'none',
              }} />
              {/* Icon */}
              <div style={{
                width: 52, height: 52, borderRadius: '14px', marginBottom: '1.2rem',
                background: 'linear-gradient(135deg, rgba(2,132,199,0.35), rgba(56,189,248,0.15))',
                border: '1px solid rgba(56,189,248,0.4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Droplet size={24} color="#38bdf8" />
              </div>
              <div style={{ fontFamily: 'Space Grotesk', fontSize: '1.25rem', fontWeight: 700, color: 'white', marginBottom: '0.4rem' }}>
                Diabetes Risk Predictor
              </div>
              <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
                v2 · SVM Model
              </div>
              <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.65)', lineHeight: 1.6, marginBottom: '1.5rem' }}>
                Predicts diabetes presence from 8 Pima biomarkers — glucose, BMI, age, insulin,
                blood pressure, skin thickness, pregnancies, and genetic predisposition.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1.5rem' }}>
                {['8 Biomarkers', 'SVM + SHAP', 'Pima Dataset', '~85% Accuracy'].map(t => (
                  <span key={t} style={{
                    background: 'rgba(56,189,248,0.1)', border: '1px solid rgba(56,189,248,0.25)',
                    borderRadius: '99px', padding: '0.2rem 0.7rem',
                    fontSize: '0.72rem', color: '#7dd3fc', fontWeight: 600,
                  }}>{t}</span>
                ))}
              </div>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                color: '#38bdf8', fontFamily: 'Space Grotesk', fontWeight: 600, fontSize: '0.88rem',
              }}>
                Open Predictor <ArrowRight size={16} />
              </div>
            </button>

            {/* V3 Card */}
            <button
              onClick={() => setScreen('v3')}
              className="mode-card"
              style={{
                flex: '1 1 340px', maxWidth: 380,
                background: 'rgba(15,23,42,0.75)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(139,92,246,0.35)', borderRadius: '20px',
                padding: '2rem 1.8rem', cursor: 'pointer', textAlign: 'left',
                transition: 'all 0.25s ease', position: 'relative', overflow: 'hidden',
              }}
              onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-6px)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.75)'; e.currentTarget.style.boxShadow = '0 20px 50px rgba(109,40,217,0.25)' }}
              onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = 'rgba(139,92,246,0.35)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              {/* Glow orb */}
              <div style={{
                position: 'absolute', top: -40, right: -40,
                width: 120, height: 120, borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)',
                pointerEvents: 'none',
              }} />
              {/* NEW badge */}
              <div style={{
                position: 'absolute', top: 16, right: 16,
                background: 'linear-gradient(135deg, #7c3aed, #a855f7)',
                color: 'white', fontSize: '0.65rem', fontWeight: 800,
                letterSpacing: '0.1em', textTransform: 'uppercase',
                padding: '0.2rem 0.6rem', borderRadius: '99px',
              }}>NEW</div>
              {/* Icon */}
              <div style={{
                width: 52, height: 52, borderRadius: '14px', marginBottom: '1.2rem',
                background: 'linear-gradient(135deg, rgba(109,40,217,0.35), rgba(139,92,246,0.15))',
                border: '1px solid rgba(139,92,246,0.4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Brain size={24} color="#a78bfa" />
              </div>
              <div style={{ fontFamily: 'Space Grotesk', fontSize: '1.25rem', fontWeight: 700, color: 'white', marginBottom: '0.4rem' }}>
                Complication Risk Predictor
              </div>
              <div style={{ fontSize: '0.75rem', color: '#a78bfa', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '1rem' }}>
                v3 · XGB + LGBM + RF Ensemble
              </div>
              <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.65)', lineHeight: 1.6, marginBottom: '1.5rem' }}>
                Predicts early hospital readmission risk (a proxy for poor glycaemic control and
                complications) from 52 clinical features across 101,766 UCI hospital records.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '1.5rem' }}>
                {['52 Features', 'XGB+LGBM+RF', 'UCI-130 Dataset', 'Readmission Risk'].map(t => (
                  <span key={t} style={{
                    background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.25)',
                    borderRadius: '99px', padding: '0.2rem 0.7rem',
                    fontSize: '0.72rem', color: '#c4b5fd', fontWeight: 600,
                  }}>{t}</span>
                ))}
              </div>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                color: '#a78bfa', fontFamily: 'Space Grotesk', fontWeight: 600, fontSize: '0.88rem',
              }}>
                Open Predictor <ArrowRight size={16} />
              </div>
            </button>
          </div>

          {/* Back link */}
          <button
            onClick={() => setScreen('landing')}
            style={{
              marginTop: '2rem', display: 'flex', alignItems: 'center', gap: '0.4rem',
              background: 'none', border: 'none', color: 'rgba(255,255,255,0.5)',
              cursor: 'pointer', fontSize: '0.85rem', fontFamily: 'Inter', transition: 'color 0.2s',
            }}
            onMouseOver={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.9)' }}
            onMouseOut={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.5)' }}
          >
            <ArrowLeft size={14} /> Back to Home
          </button>
        </div>
      </div>
    )
  }

  // ── V3 DASHBOARD — delegate to ComplicationPredictor ─────────────────────────
  if (screen === 'v3') {
    return <ComplicationPredictor onBack={() => setScreen('mode-select')} />
  }

  // ── V2 DASHBOARD (existing) ──────────────────────────────────────────────────
  return (
    <div className="app-container fade-in-up">
      {/* Sidebar Form */}
      <aside className="sidebar">
        <h2 className="form-section-title"><User size={14} /> Demographics</h2>
        <div className="input-group">
          <label className="input-label">Age (Years) <span>{formData.age}</span></label>
          <input type="range" className="input-field range" name="age" min="1" max="120" value={formData.age} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">Pregnancies <span>{formData.pregnancies}</span></label>
          <input type="number" className="input-field" name="pregnancies" min="0" max="20" value={formData.pregnancies} onChange={handleInputChange} />
        </div>

        <h2 className="form-section-title"><Droplet size={14} /> Biomarkers</h2>
        <div className="input-group">
          <label className="input-label">Glucose (mg/dL)</label>
          <input type="number" className="input-field" name="glucose" value={formData.glucose} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">Insulin (mu U/ml)</label>
          <input type="number" className="input-field" name="insulin" value={formData.insulin} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">Skin Thickness (mm)</label>
          <input type="number" className="input-field" name="skin_thickness" value={formData.skin_thickness} onChange={handleInputChange} />
        </div>

        <h2 className="form-section-title"><Heart size={14} /> Vitals & Indices</h2>
        <div className="input-group">
          <label className="input-label">Blood Pressure (mm Hg)</label>
          <input type="number" className="input-field" name="blood_pressure" value={formData.blood_pressure} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">BMI</label>
          <input type="number" step="0.1" className="input-field" name="bmi" value={formData.bmi} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">Diabetes Pedigree</label>
          <input type="number" step="0.01" className="input-field" name="dpf" value={formData.dpf} onChange={handleInputChange} />
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="submit-btn"
          style={{ background: 'rgba(2,132,199,0.8)', border: '1px solid rgba(56,189,248,0.3)', backdropFilter: 'blur(10px)' }}
        >
          {loading ? <div className="spinner" /> : <><Stethoscope size={18} /> Analyze Patient Risk</>}
        </button>

        {error && <div style={{ color: '#fca5a5', fontSize: '0.8rem', marginTop: '1rem' }}>{error}</div>}
      </aside>

      <div className="content-wrapper">
        <header className="header" style={{ background: 'transparent', borderBottom: 'none' }}>
          <button
            onClick={() => { setResult(null); setScreen('mode-select') }}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(10px)',
              color: 'white', border: '1px solid rgba(255,255,255,0.2)',
              padding: '0.6rem 1.2rem', borderRadius: '8px',
              cursor: 'pointer', transition: 'all 0.2s',
              fontFamily: 'Space Grotesk', fontWeight: 500,
              boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            }}
            onMouseOver={e => { e.currentTarget.style.background = 'rgba(0,0,0,0.6)'; e.currentTarget.style.transform = 'translateY(-1px)' }}
            onMouseOut={e => { e.currentTarget.style.background = 'rgba(0,0,0,0.4)'; e.currentTarget.style.transform = 'translateY(0)' }}
          >
            <ArrowLeft size={16} /> Back to Predictor Selection
          </button>
        </header>

        <main className="dashboard-area">
          {!result && !loading && (
            <div className="glass-panel fade-in-up" style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              height: '100%', minHeight: '600px', textAlign: 'center',
            }}>
              <div>
                <Activity size={56} color="var(--accent)" style={{ marginBottom: '1.5rem' }} />
                <h2 style={{ fontFamily: 'Space Grotesk', fontSize: '2.5rem', marginBottom: '1rem', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
                  Clinical Intelligence Dashboard
                </h2>
                <p style={{ fontSize: '1.1rem', color: 'rgba(255,255,255,0.8)', maxWidth: '500px' }}>
                  Enter patient data in the sidebar and click Analyze Patient Risk to view the SVM predictions.
                </p>
              </div>
            </div>
          )}

          {result && (
            <div className="dashboard-grid fade-in-up">

              {/* Banner */}
              <div className={`result-banner ${result.prediction === 1 ? 'high-risk' : 'low-risk'}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {result.prediction === 1 ? <ShieldAlert size={36} /> : <ShieldCheck size={36} />}
                  <div>
                    <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.9 }}>
                      Clinical Assessment
                    </div>
                    {result.prediction === 1 ? 'HIGH RISK - Diabetic' : 'LOW RISK - Non-Diabetic'}
                  </div>
                </div>
                <div>{result.probability_positive.toFixed(1)}% Score</div>
              </div>

              {/* Probability bars */}
              <div className="glass-panel prob-panel">
                <div style={{ marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontWeight: 500 }}>
                    <span>Non-Diabetic Probability</span>
                    <span style={{ color: result.probability_negative > 50 ? '#6ee7b7' : '#cbd5e1' }}>
                      {result.probability_negative.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ width: `${result.probability_negative}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #34d399)', transition: 'width 1s ease-out' }} />
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontWeight: 500 }}>
                    <span>Diabetic Probability</span>
                    <span style={{ color: result.probability_positive > 50 ? '#fca5a5' : '#cbd5e1' }}>
                      {result.probability_positive.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{
                      width: `${result.probability_positive}%`, height: '100%',
                      background: result.probability_positive > 50
                        ? 'linear-gradient(90deg, #dc2626, #ef4444)'
                        : 'linear-gradient(90deg, #f59e0b, #fbbf24)',
                      transition: 'width 1s ease-out',
                    }} />
                  </div>
                </div>
              </div>

              {/* Factors */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div className="glass-panel">
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.1rem' }}>
                    <AlertTriangle size={18} color="#ef4444" /> Risk Factors
                    <span style={{ marginLeft: 'auto', background: 'rgba(239,68,68,0.2)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.3)' }}>
                      {risks.length}
                    </span>
                  </h3>
                  {risks.length > 0 ? risks.map((r, i) => (
                    <div key={i} className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', flexShrink: 0, background: r.level === 'r' ? '#ef4444' : '#f59e0b', boxShadow: `0 0 10px ${r.level === 'r' ? '#ef4444' : '#f59e0b'}` }} />
                      <span>{r.text}</span>
                    </div>
                  )) : (
                    <div className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} />
                      <span>No significant risk factors identified</span>
                    </div>
                  )}
                </div>
                <div className="glass-panel">
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.1rem' }}>
                    <CheckCircle size={18} color="#10b981" /> Positive Indicators
                    <span style={{ marginLeft: 'auto', background: 'rgba(16,185,129,0.2)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', color: '#6ee7b7', border: '1px solid rgba(16,185,129,0.3)' }}>
                      {goods.length}
                    </span>
                  </h3>
                  {goods.length > 0 ? goods.map((g, i) => (
                    <div key={i} className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', flexShrink: 0, background: '#10b981', boxShadow: '0 0 10px #10b981' }} />
                      <span>{g.text}</span>
                    </div>
                  )) : (
                    <div className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} />
                      <span>No strong positive indicators detected</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Recommendations */}
              <div className="glass-panel">
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.1rem' }}>
                  <Info size={18} color="var(--accent)" /> Clinical Recommendations
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  {recommendations.map((rec, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(0,0,0,0.35)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ fontSize: '1.5rem', background: 'rgba(255,255,255,0.1)', width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px', flexShrink: 0, border: '1px solid rgba(255,255,255,0.1)' }}>
                        {rec.icon}
                      </div>
                      <div style={{ color: result.prediction === 1 ? '#fca5a5' : '#a7f3d0', fontSize: '0.9rem', lineHeight: 1.5 }}>
                        {rec.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* SHAP */}
              <div className="glass-panel">
                <h3 style={{ fontFamily: 'Space Grotesk', marginBottom: '0.5rem' }}>🧠 Explainable AI (SHAP)</h3>
                <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.8)', marginBottom: '1.5rem' }}>
                  This panel shows exactly how each biomarker influenced the AI's decision. Features pushing right (red) increase diabetes risk, while features pushing left (blue) lower it.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  {result.shap_image_base64
                    ? <img src={result.shap_image_base64} alt="SHAP Explanation" style={{ maxWidth: '100%', borderRadius: '8px' }} />
                    : <div style={{ color: '#fca5a5' }}>SHAP explanation could not be generated.</div>
                  }
                </div>
              </div>

              {/* Disclaimer */}
              <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.6)', textAlign: 'center', border: '1px solid rgba(255,255,255,0.1)' }}>
                ⚠️ <strong>Medical Disclaimer</strong> — This tool is for educational purposes only. It does <em>not</em> constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

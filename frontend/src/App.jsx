<<<<<<< Updated upstream
import { useState } from 'react'
import axios from 'axios'
import { Activity, Stethoscope, Droplet, Heart, User, ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle, Info, ArrowRight, ArrowLeft } from 'lucide-react'
import './App.css'

function App() {
  const [showDashboard, setShowDashboard] = useState(false)
  const [formData, setFormData] = useState({
    pregnancies: 0,
    glucose: 120,
    blood_pressure: 70,
    skin_thickness: 20,
    insulin: 80,
    bmi: 25.0,
    dpf: 0.5,
    age: 30
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
      setError("Failed to connect to the prediction server. Ensure FastAPI is running on port 8000.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Calculate Risk / Positive factors based on formData
  const getFactors = () => {
    const risks = []
    const goods = []
    const { glucose, bmi, age, blood_pressure: bp, dpf, insulin } = formData

    if (glucose > 125) risks.push({ level: 'r', text: "High plasma glucose (>125 mg/dL) — key diabetes marker" })
    else if (glucose < 100) goods.push({ level: 'g', text: "Normal fasting glucose — within healthy range" })
    
    if (bmi > 30) risks.push({ level: 'r', text: "Obesity — BMI >30 significantly raises diabetes risk" })
    else if (bmi >= 18.5 && bmi <= 24.9) goods.push({ level: 'g', text: "Healthy BMI (18.5–24.9) — reduces metabolic risk" })
    else if (bmi >= 25) risks.push({ level: 'y', text: "Overweight — BMI between 25–30, borderline risk" })
    
    if (age > 45) risks.push({ level: 'y', text: "Age >45 — diabetes prevalence increases with age" })
    else if (age < 35) goods.push({ level: 'g', text: "Younger age — lower baseline diabetes risk" })
    
    if (bp > 80) risks.push({ level: 'r', text: "Elevated diastolic BP (>80 mm Hg) — metabolic risk factor" })
    else if (bp >= 60 && bp <= 80) goods.push({ level: 'g', text: "Diastolic blood pressure within normal range" })
    
    if (dpf > 0.8) risks.push({ level: 'r', text: "High genetic predisposition (DPF >0.8)" })
    else if (dpf > 0.5) risks.push({ level: 'y', text: "Moderate genetic predisposition (DPF >0.5)" })
    else goods.push({ level: 'g', text: "Low genetic predisposition (DPF ≤0.5)" })
    
    if (insulin > 200) risks.push({ level: 'y', text: "Elevated insulin — possible insulin resistance" })

    return { risks, goods }
  }

  const { risks, goods } = getFactors()

  const recommendations = result?.prediction === 1 ? [
    { icon: "🏥", text: "Consult a healthcare professional or endocrinologist as soon as possible" },
    { icon: "🧪", text: "Request a full diabetes panel: HbA1c, fasting plasma glucose, oral glucose tolerance test" },
    { icon: "📊", text: "Begin self-monitoring of blood glucose — aim for pre-meal readings below 7 mmol/L" },
    { icon: "🥗", text: "Reduce dietary refined sugars and processed carbohydrates; increase fibre intake" },
    { icon: "🏃", text: "Start structured physical activity — 150 min/week moderate aerobic exercise" },
    { icon: "💊", text: "Discuss pharmacological management options with your doctor" }
  ] : [
    { icon: "📅", text: "Schedule annual blood glucose and HbA1c screening tests" },
    { icon: "🥗", text: "Maintain a balanced diet — Mediterranean or low-GI dietary patterns recommended" },
    { icon: "🏃", text: "Stay physically active — at least 150 minutes of moderate exercise per week" },
    { icon: "⚖️", text: "Maintain a healthy weight; even 5–7% weight reduction lowers diabetes risk" },
    { icon: "💧", text: "Stay well-hydrated — aim for 2–3 litres of water daily" },
    { icon: "😴", text: "Prioritise 7–9 hours of quality sleep — poor sleep increases insulin resistance" }
  ]

  if (!showDashboard) {
    return (
      <div className="landing-screen fade-in-up">
        <div className="landing-content">
          <div className="hero-transparent-card" style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', 
            padding: '2rem', textAlign: 'center', maxWidth: '900px'
          }}>
            <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', padding: '0.5rem 1rem', background: 'rgba(0, 0, 0, 0.4)', borderRadius: '99px', border: '1px solid rgba(255, 255, 255, 0.2)', color: 'white', fontSize: '0.85rem', fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '0.1em', backdropFilter: 'blur(4px)'}}>
              <Activity size={16} color="var(--accent)"/> Clinical Diagnostic System
            </div>
            
            <h1 style={{fontSize: '4.5rem', fontFamily: 'Space Grotesk', marginBottom: '1.5rem', fontWeight: '800', textShadow: '0 4px 20px rgba(0,0,0,0.6)', color: 'white'}}>
              Welcome to MediStore AI
            </h1>
            
            <p style={{fontSize: '1.2rem', color: 'rgba(255,255,255,0.9)', marginBottom: '3rem', maxWidth: '600px', lineHeight: '1.6', textShadow: '0 2px 10px rgba(0,0,0,0.5)'}}>
              Empowering healthcare professionals with state-of-the-art Explainable AI to predict diabetes risk with clinical precision.
            </p>
            
            <button className="get-started-btn" onClick={() => setShowDashboard(true)} style={{display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1.2rem 3rem', fontSize: '1.1rem', fontWeight: '700', fontFamily: 'Space Grotesk', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', border: 'none', borderRadius: '99px', cursor: 'pointer', transition: 'all 0.3s ease', boxShadow: '0 10px 25px rgba(0, 0, 0, 0.4)'}}
              onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.6)' }}
              onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.4)' }}
            >
              Get Started <ArrowRight size={20} />
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container fade-in-up">
      {/* Sidebar Form */}
      <aside className="sidebar">
        <h2 className="form-section-title"><User size={14}/> Demographics</h2>
        <div className="input-group">
          <label className="input-label">Age (Years) <span>{formData.age}</span></label>
          <input type="range" className="input-field range" name="age" min="1" max="120" value={formData.age} onChange={handleInputChange} />
        </div>
        <div className="input-group">
          <label className="input-label">Pregnancies <span>{formData.pregnancies}</span></label>
          <input type="number" className="input-field" name="pregnancies" min="0" max="20" value={formData.pregnancies} onChange={handleInputChange} />
        </div>

        <h2 className="form-section-title"><Droplet size={14}/> Biomarkers</h2>
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

        <h2 className="form-section-title"><Heart size={14}/> Vitals & Indices</h2>
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

        <button onClick={handleSubmit} disabled={loading} className="submit-btn" style={{background: 'rgba(2,132,199,0.8)', border: '1px solid rgba(56,189,248,0.3)', backdropFilter: 'blur(10px)'}}>
          {loading ? <div className="spinner"></div> : <><Stethoscope size={18}/> Analyze Patient Risk</>}
        </button>
        
        {error && <div className="error-msg" style={{color:'#fca5a5', fontSize:'0.8rem', marginTop:'1rem'}}>{error}</div>}
      </aside>

      <div className="content-wrapper">
        <header className="header" style={{background: 'transparent', borderBottom: 'none'}}>
          <button onClick={() => setShowDashboard(false)} style={{display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(10px)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', padding: '0.6rem 1.2rem', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'Space Grotesk', fontWeight: '500', boxShadow: '0 4px 15px rgba(0,0,0,0.2)'}}
            onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(0,0,0,0.6)'; e.currentTarget.style.transform = 'translateY(-1px)' }}
            onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(0,0,0,0.4)'; e.currentTarget.style.transform = 'translateY(0)' }}
          >
            <ArrowLeft size={16} /> Back to Landing Page
          </button>
        </header>

        <main className="dashboard-area">
          {!result && !loading && (
             <div className="glass-panel fade-in-up" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-main)', minHeight: '600px', textAlign: 'center'}}>
               <div>
                 <Activity size={56} color="var(--accent)" style={{marginBottom: '1.5rem'}}/>
                 <h2 style={{fontFamily: 'Space Grotesk', fontSize: '2.5rem', marginBottom: '1rem', textShadow: '0 2px 10px rgba(0,0,0,0.5)'}}>Clinical Intelligence Dashboard</h2>
                 <p style={{fontSize: '1.1rem', color: 'rgba(255,255,255,0.8)', maxWidth: '500px'}}>Enter patient data in the sidebar and click Analyze Patient Risk to view the XGBoost predictions.</p>
               </div>
             </div>
          )}

          {result && (
            <div className="dashboard-grid fade-in-up">
              
              {/* Banner */}
              <div className={`result-banner ${result.prediction === 1 ? 'high-risk' : 'low-risk'}`}>
                <div className="banner-content" style={{display:'flex', alignItems:'center', gap:'1rem'}}>
                  {result.prediction === 1 ? <ShieldAlert size={36}/> : <ShieldCheck size={36}/>}
                  <div>
                    <div className="banner-subtitle" style={{fontSize:'0.85rem', textTransform:'uppercase', letterSpacing:'0.1em', opacity: 0.9}}>Clinical Assessment</div>
                    {result.prediction === 1 ? 'HIGH RISK - Diabetic' : 'LOW RISK - Non-Diabetic'}
                  </div>
                </div>
                <div className="banner-score">
                  {result.probability_positive.toFixed(1)}% Score
                </div>
              </div>

              {/* Progress Bars */}
              <div className="glass-panel prob-panel">
                <div className="prob-item" style={{marginBottom: '1.5rem'}}>
                  <div className="prob-label" style={{display:'flex', justifyContent:'space-between', marginBottom:'0.5rem', fontWeight:500}}>
                    <span style={{color:'var(--text-main)'}}>Non-Diabetic Probability</span>
                    <span style={{color: result.probability_negative > 50 ? '#6ee7b7' : '#cbd5e1'}}>{result.probability_negative.toFixed(1)}%</span>
                  </div>
                  <div className="bar-track" style={{width:'100%', height:'8px', background:'rgba(0,0,0,0.3)', borderRadius:'4px', overflow:'hidden', border: '1px solid rgba(255,255,255,0.1)'}}>
                    <div className="bar-fill" style={{ width: `${result.probability_negative}%`, height:'100%', background: 'linear-gradient(90deg, #10b981, #34d399)', transition:'width 1s ease-out' }}></div>
                  </div>
                </div>
                <div className="prob-item">
                  <div className="prob-label" style={{display:'flex', justifyContent:'space-between', marginBottom:'0.5rem', fontWeight:500}}>
                    <span style={{color:'var(--text-main)'}}>Diabetic Probability</span>
                    <span style={{color: result.probability_positive > 50 ? '#fca5a5' : '#cbd5e1'}}>{result.probability_positive.toFixed(1)}%</span>
                  </div>
                  <div className="bar-track" style={{width:'100%', height:'8px', background:'rgba(0,0,0,0.3)', borderRadius:'4px', overflow:'hidden', border: '1px solid rgba(255,255,255,0.1)'}}>
                    <div className="bar-fill" style={{ width: `${result.probability_positive}%`, height:'100%', background: result.probability_positive > 50 ? 'linear-gradient(90deg, #dc2626, #ef4444)' : 'linear-gradient(90deg, #f59e0b, #fbbf24)', transition:'width 1s ease-out' }}></div>
                  </div>
                </div>
              </div>

              {/* Factors */}
              <div className="factors-row" style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem'}}>
                <div className="glass-panel">
                  <h3 className="panel-title" style={{display:'flex', alignItems:'center', gap:'0.5rem', marginBottom:'1.5rem', fontFamily:'Space Grotesk', fontSize:'1.1rem'}}>
                    <AlertTriangle size={18} color="#ef4444"/> Risk Factors 
                    <span className="badge badge-red" style={{marginLeft:'auto', background:'rgba(239,68,68,0.2)', padding:'2px 8px', borderRadius:'12px', fontSize:'0.75rem', color:'#fca5a5', border: '1px solid rgba(239,68,68,0.3)'}}>{risks.length}</span>
                  </h3>
                  <div className="factors-list">
                    {risks.length > 0 ? risks.map((r, i) => (
                      <div key={i} className={`factor-item ${r.level}`}>
                        <div className={`dot dot-${r.level}`} style={{width:'10px', height:'10px', borderRadius:'50%', flexShrink:0, background: r.level==='r'?'#ef4444':'#f59e0b', boxShadow: `0 0 10px ${r.level==='r'?'#ef4444':'#f59e0b'}`}}></div>
                        <span>{r.text}</span>
                      </div>
                    )) : (
                      <div className="factor-item g"><div className="dot dot-g" style={{width:'10px', height:'10px', borderRadius:'50%', background:'#10b981'}}></div><span>No significant risk factors identified</span></div>
                    )}
                  </div>
                </div>
                <div className="glass-panel">
                  <h3 className="panel-title" style={{display:'flex', alignItems:'center', gap:'0.5rem', marginBottom:'1.5rem', fontFamily:'Space Grotesk', fontSize:'1.1rem'}}>
                    <CheckCircle size={18} color="#10b981"/> Positive Indicators 
                    <span className="badge badge-green" style={{marginLeft:'auto', background:'rgba(16,185,129,0.2)', padding:'2px 8px', borderRadius:'12px', fontSize:'0.75rem', color:'#6ee7b7', border: '1px solid rgba(16,185,129,0.3)'}}>{goods.length}</span>
                  </h3>
                  <div className="factors-list">
                    {goods.length > 0 ? goods.map((g, i) => (
                      <div key={i} className={`factor-item ${g.level}`}>
                        <div className={`dot dot-${g.level}`} style={{width:'10px', height:'10px', borderRadius:'50%', flexShrink:0, background: g.level==='r'?'#ef4444':g.level==='y'?'#f59e0b':'#10b981', boxShadow: `0 0 10px ${g.level==='r'?'#ef4444':g.level==='y'?'#f59e0b':'#10b981'}`}}></div>
                        <span>{g.text}</span>
                      </div>
                    )) : (
                      <div className="factor-item r"><div className="dot dot-r" style={{width:'10px', height:'10px', borderRadius:'50%', background:'#ef4444'}}></div><span>No strong positive indicators detected</span></div>
                    )}
                  </div>
                </div>
              </div>

              {/* Clinical Recommendations */}
              <div className="glass-panel">
                <h3 className="panel-title" style={{display:'flex', alignItems:'center', gap:'0.5rem', marginBottom:'1.5rem', fontFamily:'Space Grotesk', fontSize:'1.1rem'}}>
                  <Info size={18} color="var(--accent)"/> Clinical Recommendations
                </h3>
                <div className="recs-grid" style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem'}}>
                  {recommendations.map((rec, i) => (
                    <div key={i} className="rec-card" style={{display:'flex', alignItems:'center', gap:'1rem', background:'rgba(0,0,0,0.35)', padding:'1rem', borderRadius:'12px', border:'1px solid rgba(255,255,255,0.05)'}}>
                      <div className="rec-icon" style={{fontSize:'1.5rem', background:'rgba(255,255,255,0.1)', width:'40px', height:'40px', display:'flex', alignItems:'center', justifyContent:'center', borderRadius:'8px', flexShrink:0, border: '1px solid rgba(255,255,255,0.1)'}}>{rec.icon}</div>
                      <div className="rec-text" style={{color: result.prediction === 1 ? '#fca5a5' : '#a7f3d0', fontSize:'0.9rem', lineHeight:'1.5'}}>{rec.text}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Explainable AI */}
              <div className="glass-panel">
                <h3 className="panel-title" style={{fontFamily:'Space Grotesk', marginBottom:'0.5rem'}}>🧠 Explainable AI (SHAP)</h3>
                <p className="panel-desc" style={{fontSize:'0.9rem', color:'rgba(255,255,255,0.8)', marginBottom:'1.5rem'}}>This panel shows exactly how each biomarker influenced the AI's decision. Features pushing right (red) increase diabetes risk, while features pushing left (blue) lower it.</p>
                <div className="shap-container" style={{display:'flex', justifyContent:'center', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)'}}>
                  {result.shap_image_base64 ? (
                    <img src={result.shap_image_base64} alt="SHAP Explanation" className="shap-img" style={{maxWidth:'100%', borderRadius:'8px'}} />
                  ) : (
                    <div className="error-msg">SHAP explanation could not be generated.</div>
                  )}
                </div>
              </div>

              {/* Disclaimer */}
              <div className="disclaimer" style={{padding:'1rem', background:'rgba(0,0,0,0.4)', borderRadius:'8px', fontSize:'0.8rem', color:'rgba(255,255,255,0.6)', textAlign:'center', border: '1px solid rgba(255,255,255,0.1)'}}>
                ⚠️ <strong>Medical Disclaimer</strong> — This tool is for educational purposes only. It does <em>not</em> constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.
              </div>

            </div>
          )}
        </main>
=======
import { Suspense, lazy, useCallback, useState } from 'react'
import AuroraField from './components/background/AuroraField'
import ScreenTransition from './components/ui/ScreenTransition'
import Landing from './screens/Landing'
import ModeSelect from './screens/ModeSelect'
import DiabetesPredictor from './screens/DiabetesPredictor'
import './App.css'

// The v3 module is the heavier of the two (52 fields, a large option map), and
// most sessions never open it — so it is split out and fetched on demand.
const ComplicationPredictor = lazy(() => import('./ComplicationPredictor'))

function ScreenFallback() {
  return (
    <div className="landing-screen">
      <div className="landing-content">
        <span className="spinner" aria-hidden="true" />
        <p style={{ marginTop: 'var(--sp-4)', color: 'var(--text-dim)', fontSize: '0.9rem' }}>
          Loading module…
        </p>
>>>>>>> Stashed changes
      </div>
    </div>
  )
}

/**
 * Screen router. The app has four screens and no URL routing, so navigation is
 * plain state — wrapped in ScreenTransition to give each change a real
 * enter/exit rather than an instant swap.
 */
export default function App() {
  // 'landing' | 'mode-select' | 'v2' | 'v3'
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

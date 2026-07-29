import { useState } from 'react'
import axios from 'axios'
import {
  Activity, Stethoscope, User, Heart, Pill, FlaskConical,
  ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle,
  Info, ArrowLeft, Building2, ClipboardList, ChevronDown,
} from 'lucide-react'

// ─── Helpers ──────────────────────────────────────────────────────────────────
const MedSelect = ({ name, value, onChange }) => (
  <select className="input-field" name={name} value={value} onChange={onChange}>
    <option value={0}>No</option>
    <option value={1}>Steady</option>
    <option value={2}>Up</option>
    <option value={-1}>Down</option>
  </select>
)

const ICD9_LABELS = {
  0: 'Unknown / Other',         1: 'Infectious & Parasitic',
  2: 'Neoplasms (Cancer)',      3: 'Endocrine / Diabetes',
  4: 'Blood Diseases',          5: 'Mental Disorders',
  6: 'Nervous System',          7: 'Circulatory System',
  8: 'Respiratory',             9: 'Digestive',
  10: 'Genitourinary',          11: 'Pregnancy / Childbirth',
  12: 'Skin Diseases',          13: 'Musculoskeletal',
  14: 'Congenital Anomalies',   15: 'Perinatal Conditions',
  16: 'Symptoms / Ill-defined', 17: 'Injury / Poisoning',
}

const ADMISSION_TYPE = {
  1: 'Emergency', 2: 'Urgent', 3: 'Elective',
  4: 'Newborn',   5: 'Not Available', 7: 'Trauma Center',
}

const ADMISSION_SOURCE = {
  1: 'Physician / Clinic Referral', 2: 'HMO Referral',
  3: 'Transfer from Hospital',      7: 'Emergency Room',
  9: 'Not Available',
}

const DISCHARGE_DISP = {
  1: 'Discharged to Home',
  2: 'Discharged to Short-term Hospital',
  3: 'Discharged to SNF',
  6: 'Discharged to Home Health',
  7: 'Left AMA',
  11: 'Not Available',
}

const AGE_OPTIONS = [
  { label: '[0–10)',   value: 5  }, { label: '[10–20)', value: 15 },
  { label: '[20–30)', value: 25  }, { label: '[30–40)', value: 35 },
  { label: '[40–50)', value: 45  }, { label: '[50–60)', value: 55 },
  { label: '[60–70)', value: 65  }, { label: '[70–80)', value: 75 },
  { label: '[80–90)', value: 85  }, { label: '[90–100)', value: 95 },
]

// ─── Defaults ─────────────────────────────────────────────────────────────────
// These are the modal / median values from the UCI-130 training set.
// They are always sent to the model — the user only needs to override
// the "essential" fields shown upfront.
const DEFAULT_FORM = {
  // Essential — always shown
  gender: 1, age: 55,
  admission_type_id: 1, admission_source_id: 7, time_in_hospital: 3,
  num_lab_procedures: 40, num_medications: 15,
  number_diagnoses: 9, diag_1: 3,
  max_glu_serum: 0, a1cresult: 0,
  metformin: 0, insulin: 1,
  change: 0, diabetesmed: 1,
  race_Asian: 0, race_Caucasian: 1, race_Hispanic: 0, race_Other: 0,

  // Advanced — hidden by default, sensible defaults applied
  discharge_disposition_id: 1,
  num_procedures: 1,
  diag_2: 3, diag_3: 7,
  number_outpatient: 0, number_emergency: 0, number_inpatient: 0,
  repaglinide: 0, nateglinide: 0, chlorpropamide: 0,
  glimepiride: 0, acetohexamide: 0, glipizide: 0, glyburide: 0,
  tolbutamide: 0, pioglitazone: 0, rosiglitazone: 0, acarbose: 0,
  miglitol: 0, troglitazone: 0, tolazamide: 0,
  glyburide_metformin: 0, glipizide_metformin: 0,
  glimepiride_pioglitazone: 0, metformin_rosiglitazone: 0,
  metformin_pioglitazone: 0,
}

// ─── Sub-component: collapsible Advanced section ───────────────────────────────
function AdvancedSection({ form, onChange, onRace, currentRace }) {
  const [open, setOpen] = useState(false)

  return (
    <div style={{ marginTop: '0.5rem' }}>
      {/* Toggle button */}
      <button
        type="button"
        onClick={() => setOpen(p => !p)}
        style={{
          width: '100%',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: open
            ? 'rgba(139,92,246,0.12)'
            : 'rgba(139,92,246,0.06)',
          border: '1px solid rgba(139,92,246,0.3)',
          borderRadius: '10px',
          padding: '0.75rem 1rem',
          cursor: 'pointer',
          transition: 'all 0.2s',
          marginBottom: open ? '1rem' : '0',
        }}
        onMouseOver={e => { e.currentTarget.style.background = 'rgba(139,92,246,0.18)' }}
        onMouseOut={e => { e.currentTarget.style.background = open ? 'rgba(139,92,246,0.12)' : 'rgba(139,92,246,0.06)' }}
      >
        <span style={{
          fontFamily: 'Space Grotesk', fontSize: '0.78rem', fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '0.09em', color: '#c4b5fd',
          display: 'flex', alignItems: 'center', gap: '0.5rem',
        }}>
          <span style={{
            width: 18, height: 18, borderRadius: '50%',
            background: 'rgba(139,92,246,0.25)', border: '1px solid rgba(139,92,246,0.5)',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.7rem', fontWeight: 800, color: '#a78bfa',
          }}>
            {open ? '−' : '+'}
          </span>
          Advanced Fields
        </span>
        <span style={{ fontSize: '0.7rem', color: 'rgba(196,181,253,0.6)', fontFamily: 'Inter' }}>
          {open ? 'Click to collapse' : '29 optional fields'}
        </span>
        <ChevronDown
          size={16}
          color="#a78bfa"
          style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.25s ease', flexShrink: 0 }}
        />
      </button>

      {/* Collapsible content */}
      <div style={{
        overflow: 'hidden',
        maxHeight: open ? '9999px' : '0',
        opacity: open ? 1 : 0,
        transition: 'opacity 0.3s ease',
      }}>
        <div style={{
          background: 'rgba(139,92,246,0.04)',
          border: '1px solid rgba(139,92,246,0.18)',
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '0.5rem',
        }}>
          <p style={{
            fontSize: '0.72rem', color: 'rgba(255,255,255,0.45)',
            marginBottom: '1.2rem', lineHeight: 1.55, fontStyle: 'italic',
          }}>
            These fields are pre-filled with typical values from the UCI-130 dataset.
            Override them only when you have specific patient data available.
          </p>

          {/* Discharge */}
          <h2 className="form-section-title" style={{ marginTop: 0 }}>
            <Building2 size={12} /> Discharge
          </h2>
          <div className="input-group">
            <label className="input-label">Discharge Disposition</label>
            <select className="input-field" name="discharge_disposition_id"
              value={form.discharge_disposition_id} onChange={onChange}>
              {Object.entries(DISCHARGE_DISP).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>

          {/* Prior Utilisation */}
          <h2 className="form-section-title"><ClipboardList size={12} /> Prior Utilisation</h2>
          <div className="input-group">
            <label className="input-label">Outpatient Visits (prior year)</label>
            <input type="number" className="input-field" name="number_outpatient"
              min={0} max={42} value={form.number_outpatient} onChange={onChange} />
          </div>
          <div className="input-group">
            <label className="input-label">Emergency Visits (prior year)</label>
            <input type="number" className="input-field" name="number_emergency"
              min={0} max={76} value={form.number_emergency} onChange={onChange} />
          </div>
          <div className="input-group">
            <label className="input-label">Inpatient Visits (prior year)</label>
            <input type="number" className="input-field" name="number_inpatient"
              min={0} max={21} value={form.number_inpatient} onChange={onChange} />
          </div>

          {/* Additional Diagnoses */}
          <h2 className="form-section-title"><ClipboardList size={12} /> Additional Diagnoses</h2>
          <div className="input-group">
            <label className="input-label">Procedures Performed</label>
            <input type="number" className="input-field" name="num_procedures"
              min={0} max={6} value={form.num_procedures} onChange={onChange} />
          </div>
          <div className="input-group">
            <label className="input-label">Secondary Diagnosis (ICD-9)</label>
            <select className="input-field" name="diag_2" value={form.diag_2} onChange={onChange}>
              {Object.entries(ICD9_LABELS).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Tertiary Diagnosis (ICD-9)</label>
            <select className="input-field" name="diag_3" value={form.diag_3} onChange={onChange}>
              {Object.entries(ICD9_LABELS).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>

          {/* Other Medications */}
          <h2 className="form-section-title"><Pill size={12} /> Other Medications</h2>
          <p style={{ fontSize: '0.72rem', color: 'rgba(255,255,255,0.4)', marginBottom: '0.85rem', lineHeight: 1.5 }}>
            Dosage status: No / Steady / Up / Down
          </p>
          {[
            ['glipizide',              'Glipizide'],
            ['glyburide',              'Glyburide'],
            ['glimepiride',            'Glimepiride'],
            ['pioglitazone',           'Pioglitazone'],
            ['rosiglitazone',          'Rosiglitazone'],
            ['repaglinide',            'Repaglinide'],
            ['nateglinide',            'Nateglinide'],
            ['chlorpropamide',         'Chlorpropamide'],
            ['acarbose',               'Acarbose'],
            ['tolbutamide',            'Tolbutamide'],
            ['miglitol',               'Miglitol'],
            ['acetohexamide',          'Acetohexamide'],
            ['tolazamide',             'Tolazamide'],
            ['troglitazone',           'Troglitazone'],
            ['glyburide_metformin',    'Glyburide–Metformin'],
            ['glipizide_metformin',    'Glipizide–Metformin'],
            ['glimepiride_pioglitazone','Glimepiride–Pioglitazone'],
            ['metformin_rosiglitazone','Metformin–Rosiglitazone'],
            ['metformin_pioglitazone', 'Metformin–Pioglitazone'],
          ].map(([name, label]) => (
            <div className="input-group" key={name}>
              <label className="input-label">{label}</label>
              <MedSelect name={name} value={form[name]} onChange={onChange} />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function ComplicationPredictor({ onBack }) {
  const [form, setForm] = useState(DEFAULT_FORM)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: parseFloat(value) }))
  }

  const handleRace = (race) => {
    setForm(prev => ({
      ...prev,
      race_Asian:     race === 'Asian'     ? 1 : 0,
      race_Caucasian: race === 'Caucasian'  ? 1 : 0,
      race_Hispanic:  race === 'Hispanic'   ? 1 : 0,
      race_Other:     race === 'Other'      ? 1 : 0,
    }))
  }

  const currentRace = () => {
    if (form.race_Asian)     return 'Asian'
    if (form.race_Caucasian) return 'Caucasian'
    if (form.race_Hispanic)  return 'Hispanic'
    if (form.race_Other)     return 'Other'
    return 'AfricanAmerican'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const payload = {
        ...form,
        gender:                    parseInt(form.gender),
        age:                       parseInt(form.age),
        admission_type_id:         parseInt(form.admission_type_id),
        discharge_disposition_id:  parseInt(form.discharge_disposition_id),
        admission_source_id:       parseInt(form.admission_source_id),
        time_in_hospital:          parseInt(form.time_in_hospital),
        num_lab_procedures:        parseInt(form.num_lab_procedures),
        num_procedures:            parseInt(form.num_procedures),
        num_medications:           parseInt(form.num_medications),
        number_outpatient:         parseInt(form.number_outpatient),
        number_emergency:          parseInt(form.number_emergency),
        number_inpatient:          parseInt(form.number_inpatient),
        diag_1:                    parseInt(form.diag_1),
        diag_2:                    parseInt(form.diag_2),
        diag_3:                    parseInt(form.diag_3),
        number_diagnoses:          parseInt(form.number_diagnoses),
      }
      const res = await axios.post('http://localhost:8001/predict_v3', payload)
      setResult(res.data)
    } catch (err) {
      setError('Failed to connect to the complication risk server. Ensure server_v3.py is running on port 8001.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // ── Factor analysis ──────────────────────────────────────────────────────────
  const getFactors = () => {
    const risks = [], goods = []
    const { a1cresult, max_glu_serum, number_inpatient, time_in_hospital,
            number_emergency, age, number_diagnoses, diabetesmed, change } = form

    if (a1cresult >= 3)       risks.push({ level: 'r', text: 'A1c result >8% — severely uncontrolled glycaemia' })
    else if (a1cresult === 2) risks.push({ level: 'y', text: 'A1c result >7% — moderately elevated, intervention needed' })
    else if (a1cresult === 1) goods.push({ level: 'g', text: 'A1c within normal range — good glycaemic control' })

    if (max_glu_serum >= 3)       risks.push({ level: 'r', text: 'Max glucose serum >300 mg/dL — critical hyperglycaemia' })
    else if (max_glu_serum === 2) risks.push({ level: 'y', text: 'Max glucose serum >200 mg/dL — elevated blood glucose' })
    else if (max_glu_serum === 1) goods.push({ level: 'g', text: 'Serum glucose within normal range' })

    if (number_inpatient >= 2)      risks.push({ level: 'r', text: `${number_inpatient} prior inpatient visits — high care dependency` })
    else if (number_inpatient === 1) risks.push({ level: 'y', text: '1 prior inpatient visit — moderate readmission risk' })
    else                            goods.push({ level: 'g', text: 'No prior inpatient visits — lower readmission baseline' })

    if (number_emergency >= 2)      risks.push({ level: 'r', text: `${number_emergency} emergency visits — unstable management` })
    else if (number_emergency === 1) risks.push({ level: 'y', text: '1 emergency visit — borderline instability signal' })

    if (time_in_hospital > 7)  risks.push({ level: 'y', text: `Extended hospital stay (${time_in_hospital} days) — complex case` })
    else                       goods.push({ level: 'g', text: `Short hospital stay (${time_in_hospital} days) — manageable case` })

    if (age >= 75)      risks.push({ level: 'r', text: 'Age ≥75 — elevated physiological frailty and complication risk' })
    else if (age >= 55) risks.push({ level: 'y', text: 'Age ≥55 — moderate age-related diabetes complication risk' })
    else                goods.push({ level: 'g', text: 'Younger age — lower baseline complication risk' })

    if (number_diagnoses >= 8)      risks.push({ level: 'r', text: `${number_diagnoses} co-diagnoses — high comorbidity burden` })
    else if (number_diagnoses >= 5) risks.push({ level: 'y', text: `${number_diagnoses} co-diagnoses — moderate comorbidity load` })
    else                            goods.push({ level: 'g', text: `Low comorbidity count (${number_diagnoses}) — simpler clinical picture` })

    if (diabetesmed === 1)  goods.push({ level: 'g', text: 'Prescribed diabetes medication — active pharmacological management' })
    else                    risks.push({ level: 'y', text: 'No diabetes medication — possible under-management' })

    if (change === 1) risks.push({ level: 'y', text: 'Medication regimen changed — may indicate instability' })
    else              goods.push({ level: 'g', text: 'Stable medication regimen — consistent treatment' })

    return { risks, goods }
  }

  const { risks, goods } = getFactors()

  const HIGH_RISK_RECS = [
    { icon: '🏥', text: 'Immediate follow-up with diabetologist or endocrinologist — do not delay' },
    { icon: '📊', text: 'Establish intensive glucose monitoring protocol — target HbA1c below 7%' },
    { icon: '💊', text: 'Review and optimise current pharmacological regimen with the clinical team' },
    { icon: '🧪', text: 'Order full metabolic panel: renal function, lipids, liver enzymes, HbA1c' },
    { icon: '🥗', text: 'Refer to a clinical dietitian for personalised medical nutrition therapy' },
    { icon: '📋', text: 'Develop a structured discharge plan with a 7-day post-discharge follow-up' },
  ]

  const LOW_RISK_RECS = [
    { icon: '📅', text: 'Schedule quarterly HbA1c monitoring and annual comprehensive metabolic panel' },
    { icon: '🏃', text: 'Maintain structured physical activity — 150 min/week moderate aerobic exercise' },
    { icon: '🥗', text: 'Adhere to a balanced, low-GI diet; limit refined carbohydrates and processed foods' },
    { icon: '💊', text: 'Continue current medication regimen and reinforce adherence with patient education' },
    { icon: '⚖️', text: 'Monitor weight trajectory; target BMI 18.5–24.9 to reduce complication risk' },
    { icon: '😴', text: 'Ensure 7–9 hours of quality sleep — poor sleep significantly worsens glycaemic control' },
  ]

  const recommendations = result?.prediction === 1 ? HIGH_RISK_RECS : LOW_RISK_RECS

  return (
    <div className="app-container fade-in-up">

      {/* ══════════════════════════════════════════════════════════════════════
          SIDEBAR
      ══════════════════════════════════════════════════════════════════════ */}
      <aside className="sidebar">

        {/* Version badge */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          marginBottom: '1.5rem', padding: '0.5rem 1rem',
          background: 'rgba(139,92,246,0.15)', borderRadius: '99px',
          border: '1px solid rgba(139,92,246,0.35)',
          color: '#c4b5fd', fontSize: '0.75rem', fontWeight: 700,
          textTransform: 'uppercase', letterSpacing: '0.08em',
        }}>
          <Activity size={13} /> Complication Risk · v3
        </div>

        <form onSubmit={handleSubmit}>

          {/* ── ESSENTIAL FIELDS ──────────────────────────────────────────── */}

          {/* Demographics */}
          <h2 className="form-section-title"><User size={13} /> Demographics</h2>

          <div className="input-group">
            <label className="input-label">Gender</label>
            <select className="input-field" name="gender" value={form.gender} onChange={handleChange}>
              <option value={1}>Male</option>
              <option value={0}>Female</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Age Bracket</label>
            <select className="input-field" name="age" value={form.age} onChange={handleChange}>
              {AGE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Race / Ethnicity</label>
            <select
              className="input-field"
              value={currentRace()}
              onChange={e => handleRace(e.target.value)}
            >
              <option value="AfricanAmerican">African American</option>
              <option value="Asian">Asian</option>
              <option value="Caucasian">Caucasian</option>
              <option value="Hispanic">Hispanic</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Hospital Visit */}
          <h2 className="form-section-title"><Building2 size={13} /> Hospital Visit</h2>

          <div className="input-group">
            <label className="input-label">Admission Type</label>
            <select className="input-field" name="admission_type_id"
              value={form.admission_type_id} onChange={handleChange}>
              {Object.entries(ADMISSION_TYPE).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Admission Source</label>
            <select className="input-field" name="admission_source_id"
              value={form.admission_source_id} onChange={handleChange}>
              {Object.entries(ADMISSION_SOURCE).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">
              Days in Hospital <span>{form.time_in_hospital}</span>
            </label>
            <input type="range" className="input-field range"
              name="time_in_hospital" min={1} max={14}
              value={form.time_in_hospital} onChange={handleChange} />
          </div>

          {/* Clinical */}
          <h2 className="form-section-title"><ClipboardList size={13} /> Clinical</h2>

          <div className="input-group">
            <label className="input-label">
              Lab Procedures <span>{form.num_lab_procedures}</span>
            </label>
            <input type="range" className="input-field range"
              name="num_lab_procedures" min={1} max={132}
              value={form.num_lab_procedures} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label className="input-label">Number of Medications</label>
            <input type="number" className="input-field" name="num_medications"
              min={1} max={81} value={form.num_medications} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label className="input-label">Number of Diagnoses</label>
            <input type="number" className="input-field" name="number_diagnoses"
              min={1} max={16} value={form.number_diagnoses} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label className="input-label">Primary Diagnosis (ICD-9)</label>
            <select className="input-field" name="diag_1" value={form.diag_1} onChange={handleChange}>
              {Object.entries(ICD9_LABELS).map(([k, v]) =>
                <option key={k} value={k}>{v}</option>)}
            </select>
          </div>

          {/* Lab Results */}
          <h2 className="form-section-title"><FlaskConical size={13} /> Lab Results</h2>

          <div className="input-group">
            <label className="input-label">A1c Result</label>
            <select className="input-field" name="a1cresult" value={form.a1cresult} onChange={handleChange}>
              <option value={0}>Not Tested</option>
              <option value={1}>Normal</option>
              <option value={2}>&gt;7%</option>
              <option value={3}>&gt;8%</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Max Glucose Serum</label>
            <select className="input-field" name="max_glu_serum" value={form.max_glu_serum} onChange={handleChange}>
              <option value={0}>Not Tested</option>
              <option value={1}>Normal</option>
              <option value={2}>&gt;200 mg/dL</option>
              <option value={3}>&gt;300 mg/dL</option>
            </select>
          </div>

          {/* Key Medications */}
          <h2 className="form-section-title"><Pill size={13} /> Key Medications</h2>
          <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '0.9rem', lineHeight: 1.5 }}>
            Dosage status: No / Steady / Up / Down
          </p>

          <div className="input-group">
            <label className="input-label">Metformin</label>
            <MedSelect name="metformin" value={form.metformin} onChange={handleChange} />
          </div>

          <div className="input-group">
            <label className="input-label">Insulin</label>
            <MedSelect name="insulin" value={form.insulin} onChange={handleChange} />
          </div>

          {/* Management Flags */}
          <h2 className="form-section-title"><Heart size={13} /> Management</h2>

          <div className="input-group">
            <label className="input-label">Medication Change</label>
            <select className="input-field" name="change" value={form.change} onChange={handleChange}>
              <option value={0}>No Change</option>
              <option value={1}>Changed</option>
            </select>
          </div>

          <div className="input-group">
            <label className="input-label">Diabetes Medication Prescribed</label>
            <select className="input-field" name="diabetesmed" value={form.diabetesmed} onChange={handleChange}>
              <option value={1}>Yes</option>
              <option value={0}>No</option>
            </select>
          </div>

          {/* ── ADVANCED FIELDS (collapsible) ──────────────────────────────── */}
          <AdvancedSection
            form={form}
            onChange={handleChange}
            onRace={handleRace}
            currentRace={currentRace()}
          />

        </form>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="submit-btn"
          style={{
            background: 'linear-gradient(135deg, rgba(139,92,246,0.85), rgba(109,40,217,0.85))',
            border: '1px solid rgba(167,139,250,0.4)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 20px rgba(139,92,246,0.35)',
          }}
        >
          {loading
            ? <div className="spinner" />
            : <><Stethoscope size={18} /> Assess Complication Risk</>
          }
        </button>

        {error && (
          <div style={{ color: '#fca5a5', fontSize: '0.78rem', marginTop: '1rem', lineHeight: 1.5 }}>
            {error}
          </div>
        )}
      </aside>

      {/* ══════════════════════════════════════════════════════════════════════
          CONTENT AREA
      ══════════════════════════════════════════════════════════════════════ */}
      <div className="content-wrapper">
        <header className="header" style={{ background: 'transparent', borderBottom: 'none' }}>
          <button
            onClick={onBack}
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

          {/* Idle state */}
          {!result && !loading && (
            <div className="glass-panel fade-in-up" style={{
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              minHeight: '600px', textAlign: 'center',
            }}>
              <div>
                <div style={{
                  width: 80, height: 80, borderRadius: '50%', margin: '0 auto 1.5rem',
                  background: 'linear-gradient(135deg, rgba(139,92,246,0.25), rgba(109,40,217,0.15))',
                  border: '1px solid rgba(139,92,246,0.4)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Activity size={36} color="#a78bfa" />
                </div>
                <h2 style={{
                  fontFamily: 'Space Grotesk', fontSize: '2.2rem',
                  marginBottom: '1rem', color: 'var(--text-main)',
                }}>
                  Complication Risk Dashboard
                </h2>
                <p style={{ fontSize: '1rem', color: 'rgba(255,255,255,0.7)', maxWidth: '480px', lineHeight: 1.6 }}>
                  Fill in the essential patient details in the sidebar and click
                  <strong style={{ color: '#a78bfa' }}> Assess Complication Risk</strong>.
                  Optional fields are pre-filled with typical values and can be overridden
                  in the <strong style={{ color: '#c4b5fd' }}>Advanced Fields</strong> section.
                </p>
                {/* Model stats */}
                <div style={{
                  display: 'flex', gap: '1rem', justifyContent: 'center',
                  marginTop: '2rem', flexWrap: 'wrap',
                }}>
                  {[
                    ['XGB+LGBM+RF', 'Ensemble'],
                    ['101,766',     'Training Records'],
                    ['52',          'Features'],
                    ['UCI-130',     'Dataset'],
                  ].map(([val, lbl]) => (
                    <div key={lbl} style={{
                      background: 'rgba(139,92,246,0.1)',
                      border: '1px solid rgba(139,92,246,0.25)',
                      borderRadius: '12px', padding: '0.75rem 1.2rem', textAlign: 'center',
                    }}>
                      <div style={{ fontFamily: 'Space Grotesk', fontSize: '1rem', fontWeight: 700, color: '#c4b5fd' }}>{val}</div>
                      <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: '0.15rem' }}>{lbl}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="dashboard-grid fade-in-up">

              {/* Banner */}
              <div className={`result-banner ${result.prediction === 1 ? 'high-risk' : 'low-risk'}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {result.prediction === 1 ? <ShieldAlert size={36} /> : <ShieldCheck size={36} />}
                  <div>
                    <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.85 }}>
                      Complication Risk Assessment
                    </div>
                    {result.prediction === 1
                      ? 'HIGH RISK — Early Readmission Likely'
                      : 'LOW RISK — Stable / Well-Managed'}
                  </div>
                </div>
                <div style={{ fontFamily: 'Space Grotesk', fontWeight: 700 }}>
                  {result.probability_positive.toFixed(1)}% Score
                </div>
              </div>

              {/* Probability Bars */}
              <div className="glass-panel">
                <div style={{ marginBottom: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontWeight: 500 }}>
                    <span style={{ color: 'var(--text-main)' }}>Stable / Low-Risk Probability</span>
                    <span style={{ color: result.probability_negative > 50 ? '#6ee7b7' : 'var(--text-muted)' }}>
                      {result.probability_negative.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ width: `${result.probability_negative}%`, height: '100%', background: 'linear-gradient(90deg,#10b981,#34d399)', transition: 'width 1s ease-out' }} />
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontWeight: 500 }}>
                    <span style={{ color: 'var(--text-main)' }}>Early Readmission Probability</span>
                    <span style={{ color: result.probability_positive > 50 ? '#fca5a5' : 'var(--text-muted)' }}>
                      {result.probability_positive.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(0,0,0,0.3)', borderRadius: '4px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{
                      width: `${result.probability_positive}%`, height: '100%',
                      background: result.probability_positive > 50
                        ? 'linear-gradient(90deg,#dc2626,#ef4444)'
                        : 'linear-gradient(90deg,#a78bfa,#8b5cf6)',
                      transition: 'width 1s ease-out',
                    }} />
                  </div>
                </div>
              </div>

              {/* Risk & Positive Factors */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                <div className="glass-panel">
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.05rem' }}>
                    <AlertTriangle size={17} color="#ef4444" /> Risk Factors
                    <span style={{ marginLeft: 'auto', background: 'rgba(239,68,68,0.2)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.3)' }}>
                      {risks.length}
                    </span>
                  </h3>
                  {risks.length > 0 ? risks.map((r, i) => (
                    <div key={i} className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', flexShrink: 0, background: r.level === 'r' ? '#ef4444' : '#f59e0b', boxShadow: `0 0 8px ${r.level === 'r' ? '#ef4444' : '#f59e0b'}` }} />
                      <span>{r.text}</span>
                    </div>
                  )) : (
                    <div className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }} />
                      <span>No significant risk factors identified</span>
                    </div>
                  )}
                </div>

                <div className="glass-panel">
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.05rem' }}>
                    <CheckCircle size={17} color="#10b981" /> Positive Indicators
                    <span style={{ marginLeft: 'auto', background: 'rgba(16,185,129,0.2)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', color: '#6ee7b7', border: '1px solid rgba(16,185,129,0.3)' }}>
                      {goods.length}
                    </span>
                  </h3>
                  {goods.length > 0 ? goods.map((g, i) => (
                    <div key={i} className="factor-item">
                      <div style={{ width: 10, height: 10, borderRadius: '50%', flexShrink: 0, background: '#10b981', boxShadow: '0 0 8px #10b981' }} />
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
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontFamily: 'Space Grotesk', fontSize: '1.05rem' }}>
                  <Info size={17} color="var(--accent)" /> Clinical Recommendations
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  {recommendations.map((rec, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', background: 'rgba(0,0,0,0.35)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
                      <div style={{ fontSize: '1.4rem', background: 'rgba(255,255,255,0.08)', width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px', flexShrink: 0, border: '1px solid rgba(255,255,255,0.1)' }}>
                        {rec.icon}
                      </div>
                      <span style={{ color: result.prediction === 1 ? '#fca5a5' : '#a7f3d0', fontSize: '0.88rem', lineHeight: 1.55 }}>
                        {rec.text}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* SHAP */}
              <div className="glass-panel">
                <h3 style={{ fontFamily: 'Space Grotesk', marginBottom: '0.5rem', fontSize: '1.05rem' }}>
                  🧠 Explainable AI (SHAP)
                </h3>
                <p style={{ fontSize: '0.88rem', color: 'rgba(255,255,255,0.75)', marginBottom: '1.5rem', lineHeight: 1.5 }}>
                  Which clinical features drove this readmission risk prediction.
                  Features pushing <strong style={{ color: '#f87171' }}>right (red)</strong> increase risk;
                  features pushing <strong style={{ color: '#93c5fd' }}>left (blue)</strong> lower it.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  {result.shap_image_base64
                    ? <img src={result.shap_image_base64} alt="SHAP Explanation" style={{ maxWidth: '100%', borderRadius: '8px' }} />
                    : <div style={{ color: '#fca5a5' }}>SHAP explanation could not be generated.</div>
                  }
                </div>
              </div>

              {/* Disclaimer */}
              <div style={{ padding: '1rem', background: 'rgba(0,0,0,0.4)', borderRadius: '8px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.55)', textAlign: 'center', border: '1px solid rgba(255,255,255,0.1)' }}>
                ⚠️ <strong>Medical Disclaimer</strong> — This tool is for educational and research purposes only.
                Predictions are based on historical hospital data and do <em>not</em> constitute clinical advice,
                diagnosis, or treatment. Always consult a qualified healthcare professional.
              </div>

            </div>
          )}
        </main>
      </div>
    </div>
  )
}

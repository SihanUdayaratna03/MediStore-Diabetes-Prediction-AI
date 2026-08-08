/**
 * Single place where the frontend talks to the two FastAPI backends.
 *
 * Base URLs come from Vite env vars so the app can point at a deployed API
 * without code changes; the defaults match the local dev ports used by
 * docker-compose and scripts/start.ps1.
 */
import axios from 'axios'

export const V2_BASE_URL = import.meta.env.VITE_API_V2_URL ?? 'http://localhost:8000'
export const V3_BASE_URL = import.meta.env.VITE_API_V3_URL ?? 'http://localhost:8001'

const v2 = axios.create({ baseURL: V2_BASE_URL })
const v3 = axios.create({ baseURL: V3_BASE_URL })

/**
 * v2 model — diabetes risk from 8 PIMA biomarkers.
 * @returns {Promise<{prediction:number, probability_positive:number,
 *                    probability_negative:number, shap_image_base64:string}>}
 */
export async function predictDiabetesRisk(payload) {
  const res = await v2.post('/predict', payload)
  return res.data
}

/**
 * v3 model — complication / early-readmission risk from UCI-130 features.
 * @returns {Promise<{prediction:number, probability_positive:number,
 *                    probability_negative:number, shap_image_base64:string}>}
 */
export async function predictComplicationRisk(payload) {
  const res = await v3.post('/predict_v3', payload)
  return res.data
}

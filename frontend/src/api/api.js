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

/**
 * Fetches nearby clinics, specialists, pharmacies, and supply hubs.
 * @param {Object} options
 * @param {number} [options.lat=6.9271]
 * @param {number} [options.lng=79.8612]
 * @param {string} [options.category='all'] ('all' | 'endocrinologist' | 'pharmacy' | 'laboratory' | 'podiatry' | 'emergency')
 * @param {string} [options.riskLevel='all'] ('all' | 'high_risk' | 'low_risk')
 */
export async function searchNearbyPlaces({ lat = 6.9271, lng = 79.8612, category = 'all', riskLevel = 'all' } = {}) {
  try {
    const res = await v2.get('/api/places/nearby', {
      params: { lat, lng, category, risk_level: riskLevel }
    })
    return res.data.facilities
  } catch (err) {
    console.error('Failed to fetch nearby places:', err)
    throw err
  }
}

/**
 * Searches for any pharmacy, hospital, clinic or diagnostic lab by name.
 * @param {Object} options
 * @param {string} options.query
 * @param {number} [options.lat=6.9271]
 * @param {number} [options.lng=79.8612]
 * @param {number} [options.radius=15000]
 */
export async function searchPlacesByName({ query, lat = 6.9271, lng = 79.8612, radius = 15000 }) {
  try {
    const res = await v2.get('/api/places/search', {
      params: { query, lat, lng, radius }
    })
    return res.data.facilities
  } catch (err) {
    console.error('Failed to search places by name:', err)
    throw err
  }
}

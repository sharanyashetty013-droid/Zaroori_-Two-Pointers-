// Real backend only. In dev it talks to the local API; in a production build
// set VITE_API_URL to the deployed backend address.
export const BASE =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')

// Kept so older imports (Login.jsx) keep working. Demo mode is gone.
export const DEMO = false

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

let ashaKey = null
export function setKey(key) {
  ashaKey = key
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(BASE + path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(ashaKey ? { 'X-Asha-Key': ashaKey } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new ApiError(0, 'No connection')
  }
  if (!res.ok) throw new ApiError(res.status, 'Request failed')
  try {
    return await res.json()
  } catch {
    throw new ApiError(-1, 'Bad response')
  }
}

const post = (path, body) =>
  request(path, { method: 'POST', body: JSON.stringify(body) })

// Login check: returns { code, district, login_required }
export const getMe = () => request('/asha/me')

export const getHospitals = (district) =>
  request('/hospitals?district=' + encodeURIComponent(district))

// [{ id, text, options: [{ value, label }] }] in the chosen language
export const getQuestions = (lang) =>
  request('/questions?lang=' + encodeURIComponent(lang))

// -> { session_id }. The district comes from the ASHA's own account.
export const startSession = (lang, hospitalId) =>
  post('/sessions', {
    lang,
    ...(hospitalId != null ? { hospital_id: hospitalId } : {}),
  })

// answers: { [questionId]: optionValue } -> full result (headline, AI questions, hospitals, alert)
export const submitAnswers = (sid, answers) =>
  post(`/sessions/${sid}/answers`, { answers })

export const getResult = (sid, lang) =>
  request(`/sessions/${sid}/result?lang=${encodeURIComponent(lang)}`)

// Direct link to the PDF slip
export const slipUrl = (sid, lang) =>
  `${BASE}/sessions/${sid}/slip.pdf?lang=${encodeURIComponent(lang)}`

// Sends the alert for a session (the woman has already said yes on screen)
export const postAlert = (sessionId) =>
  post('/alerts', { session_id: sessionId, consent: true })

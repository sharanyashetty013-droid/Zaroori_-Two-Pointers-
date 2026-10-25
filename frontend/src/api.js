const BASE = import.meta.env.VITE_API_URL

// Demo mode: only while developing (npm run dev) with no real address,
// or when VITE_API_URL=demo. A production build never turns it on by itself.
export const DEMO = BASE === 'demo' || (!BASE && import.meta.env.DEV)

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

// ---- Demo mode ----
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

export async function getMe() {
  if (DEMO) {
    await wait(400)
    if ((ashaKey || '').trim().toLowerCase() !== 'asha-demo')
      throw new ApiError(401, 'Wrong key')
    return { asha_code: 'DEMO-001', district: 'Demo District' }
  }
  return request('/asha/me')
}

export async function getHospitals(district) {
  if (DEMO) {
    await wait(300)
    return [
      { id: 'h1', name: 'DEMO Hospital A' },
      { id: 'h2', name: 'DEMO Hospital B' },
      { id: 'h3', name: 'DEMO Hospital C' },
    ]
  }
  return request('/hospitals?district=' + encodeURIComponent(district))
}
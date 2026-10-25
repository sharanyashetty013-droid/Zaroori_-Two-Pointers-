import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { setKey, getMe, DEMO } from '../api'
import '../login.css'

function Background() {
  return (
    <>
      <div className="lg-orbs">
        <div className="lg-orb o1" />
        <div className="lg-orb o2" />
        <div className="lg-orb o3" />
      </div>
      <div className="lg-sphere" />
      <div className="lg-grain" />
    </>
  )
}

function Top() {
  return (
    <div className="lg-left">
      <div className="lg-logo">
        <div className="lg-logo-chip">?</div>
        <div className="lg-word">Zaroori<span>?</span></div>
      </div>
      <div className="lg-chips">
        <div className="lg-chip left">A</div>
        <div className="lg-chip mid">अ</div>
        <div className="lg-chip right">ಕ</div>
      </div>
      <div className="lg-badge-wrap">
        <span className="lg-badge">Rural women's healthcare</span>
      </div>
      <h1 className="lg-title">
        Ask <span className="hl">Once More</span><br />
        Before A Big Decision
      </h1>
    </div>
  )
}

function EyeIcon({ off }) {
  return off ? (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}

export default function Login() {
  const { asha, login } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('choose') // 'choose' | 'haskey' | 'nokey'
  const [value, setValue] = useState('')
  const [show, setShow] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState(null)

  useEffect(() => {
    document.body.classList.remove('login-bg')
    document.body.classList.add('glass-bg')
    if (asha) navigate('/language', { replace: true })
    return () => document.body.classList.remove('glass-bg')
  }, [])

  async function check() {
    setError('')
    setLoading(true)
    setKey(value.trim())
    try {
      const me = await getMe()
      console.log('ME RESPONSE (remove later):', me)
      setProfile({
        key: value.trim(),
        code: me.asha_code ?? me.code ?? me.id ?? '',
        district: me.district ?? me.district_name ?? '',
      })
    } catch (e) {
      console.log('LOGIN ERROR (remove later):', e, 'API URL:', import.meta.env.VITE_API_URL)
      setKey(null)
      if (e.status === 401)
        setError('Wrong ASHA key entered. Please check it and try again. If it keeps failing, the key may be switched off. Ask your coordinator.')
      else if (e.status === 403)
        setError('This key is for a different district. Ask your coordinator.')
      else if (e.status === 429)
        setError('Too many tries. Please wait or contact your coordinator.')
      else if (e.status === 0)
        setError('No connection. Please check your internet and try again.')
      else if (e.status === -1)
        setError('Cannot reach the server properly. Please try again later.')
      else
        setError(`Something went wrong (code ${e.status}). Please try again.`)
    }
    setLoading(false)
  }

  let body

  if (profile) {
    body = (
      <>
        <div className="lg-glass">
          <h2>Welcome</h2>
          <p>ASHA code: <strong>{profile.code}</strong></p>
          <p>District: <strong>{profile.district}</strong></p>
        </div>
        <button
          className="lg-btn"
          onClick={() => {
            login(profile)
            navigate('/language')
          }}
        >
          Continue
        </button>
      </>
    )
  } else if (mode === 'choose') {
    body = (
      <>
        <p className="lg-sub">Log in to start a case with a woman, safely and privately.</p>
        <button className="lg-btn" onClick={() => setMode('haskey')}>
          I have an ASHA key
        </button>
        <button className="lg-btn ghost" onClick={() => setMode('nokey')}>
          I don't have an ASHA key
        </button>
        <button className="lg-back" onClick={() => navigate('/officials')}>
          I'm a health official →
        </button>
      </>
    )
  } else if (mode === 'nokey') {
    body = (
      <>
        <div className="lg-glass">
          <h2>No ASHA key?</h2>
          <p>
            Every ASHA gets her own key from her coordinator or the district
            health office. Please ask them for one. Without a key, a case
            cannot be started.
          </p>
          <p>Never use someone else's key.</p>
        </div>
        <button className="lg-btn" onClick={() => setMode('haskey')}>
          I have a key now
        </button>
        <button className="lg-btn ghost" onClick={() => setMode('choose')}>
          Back
        </button>
      </>
    )
  } else {
    body = (
      <>
        <div className="lg-glass">
          <label htmlFor="key">ASHA key</label>
          <div className="lg-field">
            <input
              id="key"
              className="lg-input"
              type={show ? 'text' : 'password'}
              autoComplete="off"
              value={value}
              onChange={(e) => {
                setValue(e.target.value)
                setError('')
              }}
            />
            <button
              type="button"
              className="lg-eye"
              onClick={() => setShow(!show)}
              aria-label={show ? 'Hide key' : 'Show key'}
            >
              <EyeIcon off={show} />
            </button>
          </div>
          {error && <p className="lg-error">{error}</p>}
          {DEMO && <p className="lg-demo">Demo mode: use the key ASHA-DEMO</p>}
        </div>
        <button className="lg-btn" disabled={!value.trim() || loading} onClick={check}>
          {loading ? 'Checking…' : 'Continue'}
        </button>
        <button className="lg-back" onClick={() => setMode('choose')}>
          ← Back
        </button>
      </>
    )
  }

  return (
    <>
      <Background />
      <div className="lg-page">
        <Top />
        <div className="lg-right">
          {body}
          <p className="lg-note">🔒 No names, phone numbers or Aadhaar are stored.</p>
        </div>
      </div>
    </>
  )
}
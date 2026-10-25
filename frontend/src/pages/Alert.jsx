import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { ALERT, HELPLINES } from '../data/alert'
import { speak } from '../speak'

export default function Alert() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { lang } = useLanguage()
  const [consent, setConsent] = useState(null) // null | 'yes' | 'no'
  const answers = state?.answers

  const spoken = [
    ALERT.headline[lang],
    ALERT.body[lang],
    ALERT.rightsTitle[lang],
    ...ALERT.rights.map((r) => r[lang]),
    ALERT.consentTitle[lang],
  ].join('. ')

  useEffect(() => {
    if (!answers) {
      navigate('/')
      return
    }
    document.body.classList.add('alert-bg')
    speak(spoken, lang)
    return () => {
      document.body.classList.remove('alert-bg')
      window.speechSynthesis.cancel()
    }
  }, [])

  function answerConsent(value) {
    setConsent(value)
    if (value === 'yes') {
      // TODO (feature/connect-backend): send an anonymous case to the backend here.
      // Send only answers + hospital + district. NEVER a name or phone number.
      console.log('Case to send (no name):', answers)
    }
  }

  if (!answers) return null

  return (
    <div>
      <div className="alert-card">
        <h1>{ALERT.headline[lang]}</h1>
        <p>{ALERT.body[lang]}</p>
        <button className="btn-big" onClick={() => speak(spoken, lang)}>
          🔊 {ALERT.listen[lang]}
        </button>
      </div>

      <div className="alert-card">
        <h2>{ALERT.rightsTitle[lang]}</h2>
        <ul className="rights-list">
          {ALERT.rights.map((r, i) => (
            <li key={i}>{r[lang]}</li>
          ))}
        </ul>
      </div>

      <div className="alert-card">
        <h2>📞 {ALERT.helpTitle[lang]}</h2>
        {HELPLINES.map((h) => (
          <a key={h.number} className="btn-big call" href={`tel:${h.number}`}>
            <span className="call-label">{h.label[lang]}</span>
            <span>{h.number}</span>
          </a>
        ))}
      </div>

      <div className="alert-card">
        <h2>{ALERT.consentTitle[lang]}</h2>
        <p>{ALERT.consentNote[lang]}</p>
        {consent === null && (
          <>
            <button className="btn-big" onClick={() => answerConsent('yes')}>
              {ALERT.yes[lang]}
            </button>
            <button className="btn-big btn-outline" onClick={() => answerConsent('no')}>
              {ALERT.no[lang]}
            </button>
          </>
        )}
        {consent === 'yes' && <p className="done">✅ {ALERT.sent[lang]}</p>}
        {consent === 'no' && <p className="done">{ALERT.declined[lang]}</p>}
      </div>

      <button
        className="btn-big btn-outline"
        onClick={() => navigate('/result', { state: { answers } })}
      >
        {ALERT.plan[lang]}
      </button>
    </div>
  )
}
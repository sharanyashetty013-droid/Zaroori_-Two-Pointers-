import { useEffect, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { ALERT_TEXT, HELPLINES, spokenDigits } from '../data/alertText'
import { postAlert } from '../api'
import { speak } from '../speak'

const LANGS = [
  { code: 'en', label: 'EN' },
  { code: 'hi', label: 'हि' },
  { code: 'kn', label: 'ಕ' },
]

function Icon({ d }) {
  return (
    <svg className="rd-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  )
}

export default function Alert() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { lang, setLang } = useLanguage()
  const a = ALERT_TEXT[lang]
  const answers = state?.answers
  const hospitalId = state?.hospitalId ?? null
  const slipCode = state?.slipCode ?? ''

  const [view, setView] = useState('rights') // rights | consent | done
  const [sending, setSending] = useState(false)
  const [failed, setFailed] = useState(false)
  const [sentCode, setSentCode] = useState('')

  useEffect(() => {
    document.body.classList.add('rd-bg')
    return () => {
      document.body.classList.remove('rd-bg')
      window.speechSynthesis?.cancel()
    }
  }, [])

  if (!answers) return <Navigate to="/language" replace />

  const rights = [a.r1, a.r2, a.r3, a.r4]
  const spokenRights = [
    a.headline,
    a.body,
    a.rightsTitle,
    ...rights,
    a.helpTitle,
    ...HELPLINES.map((h) => a[h.key] + ': ' + spokenDigits(h.number, lang)),
  ].join('. ')

  async function send() {
    if (sending) return
    setSending(true)
    setFailed(false)
    try {
      const res = await postAlert(slipCode)
      setSentCode(res?.slip_code ?? slipCode)
      setView('done')
    } catch {
      setFailed(true)
    } finally {
      setSending(false)
    }
  }

  function quickExit() {
    window.location.replace('/neutral')
  }

  const listenBtn = (text) => (
    <button className="rd-listen" onClick={() => speak(text, lang)}>
      <Icon d="M11 5L6 9H3v6h3l5 4zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
      {a.listen}
    </button>
  )

  return (
    <div className="rd-page">
      <div className="rd-top">
        <div className="rd-langs">
          {LANGS.map((l) => (
            <button key={l.code} className={lang === l.code ? 'on' : ''} onClick={() => setLang(l.code)}>
              {l.label}
            </button>
          ))}
        </div>
        <button className="rd-exit" onClick={quickExit}>
          <Icon d="M18 6L6 18M6 6l12 12" />
          Exit
        </button>
      </div>

      {view === 'rights' && (
        <div className="rd-grid">
          <div className="rd-left">
            <h1 className="rd-title">{a.headline}</h1>
            <p className="rd-lead">{a.body}</p>
            {listenBtn(spokenRights)}

            <div className="rd-box rd-rights">
              <h2>{a.rightsTitle}</h2>
              <ul className="rd-list">
                {rights.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rd-right">
            <div className="rd-box rd-help">
              <h2>{a.helpTitle}</h2>
              {HELPLINES.map((h) => (
                <a key={h.number} className="rd-call" href={'tel:' + h.number}>
                  <span>
                    <Icon d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" />
                    {a[h.key]}
                  </span>
                  <strong>{h.number}</strong>
                </a>
              ))}
            </div>

            <div className="rd-note">
              <strong>ASHA</strong>
              <p>{a.guideRights}</p>
            </div>

            <div className="rd-actions">
              <button className="rd-btn ghost" onClick={() => setView('consent')}>
                {a.toConsent}
              </button>
              <button
                className="rd-link"
                onClick={() => navigate('/result', { state: { answers, hospitalId, slipCode } })}
              >
                &#8592; {a.backResult}
              </button>
            </div>
          </div>
        </div>
      )}

      {view === 'consent' && (
        <div className="rd-grid">
          <div className="rd-left">
            <h1 className="rd-title">{a.consentTitle}</h1>
            <p className="rd-lead">{a.consentQ}</p>
            {listenBtn(a.consentQ)}
            <div className="rd-note">
              <strong>ASHA</strong>
              <p>{a.guideConsent}</p>
            </div>
          </div>

          <div className="rd-right rd-center">
            {failed && <div className="rd-fail">{a.failed}</div>}
            <div className="rd-choices">
              <button className="rd-choice" disabled={sending} onClick={send}>
                {sending ? a.sending : failed ? a.retry : a.yes}
              </button>
              <button className="rd-choice" disabled={sending} onClick={() => setView('rights')}>
                {a.no}
              </button>
            </div>
          </div>
        </div>
      )}

      {view === 'done' && (
        <div className="rd-done">
          <h1 className="rd-title">{a.sentTitle}</h1>
          <p className="rd-lead">{a.sentBody}</p>
          <div className="rd-box">
            <div className="rd-code-label">{a.codeLabel}</div>
            <div className="rd-code">{sentCode}</div>
            <p>{a.codeNote}</p>
          </div>
          <button className="rd-btn" onClick={() => navigate('/language', { replace: true })}>
            {a.finish}
          </button>
        </div>
      )}
    </div>
  )
}
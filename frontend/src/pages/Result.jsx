import { useEffect, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { RESULT_TEXT } from '../data/resultText'
import { getResult, slipUrl } from '../api'
import { speak, stopSpeaking } from '../speak'
import Shell from '../components/Shell'

// The AI may return plain strings or objects; show either.
const asText = (x) => (typeof x === 'string' ? x : x?.text ?? x?.question ?? '')

export default function Result() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { lang } = useLanguage()
  const r = RESULT_TEXT[lang]
  const [res, setRes] = useState(state?.result ?? null)
  const sid = state?.result?.session_id

  // Reload the result in the new language when the language button is used
  useEffect(() => {
    if (!sid) return
    let off = false
    getResult(sid, lang)
      .then((x) => !off && setRes(x))
      .catch(() => {})
    return () => {
      off = true
    }
  }, [sid, lang])

  useEffect(() => () => stopSpeaking(), [])

  if (!res) return <Navigate to="/language" replace />

  const asks = (res.doctor_questions ?? []).map(asText).filter(Boolean)
  const hospitals = res.hospitals ?? []
  const slipCode = res.session_id.slice(0, 8).toUpperCase()
  const spoken = [
    res.headline,
    res.note,
    ...(asks.length ? [r.askTitle, ...asks] : []),
    ...(hospitals.length ? [r.visitTitle, ...hospitals.map((h) => h.name)] : []),
    r.notDiagnosis,
  ].join('. ')

  return (
    <Shell title={res.headline} step="result" guide={r.guide}>
      <div className="sh-card">
        <p>{res.note}</p>
        <button className="sh-listen" onClick={() => speak(spoken, lang, `/tts/result/${res.session_id}?lang=${lang}`)}>
          <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 5L6 9H3v6h3l5 4zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
          </svg>
          {r.listenAll}
        </button>
      </div>

      {asks.length > 0 && (
        <div className="sh-card">
          <h2>{r.askTitle}</h2>
          <ol className="sh-list">
            {asks.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ol>
        </div>
      )}

      {hospitals.length > 0 && (
        <div className="sh-card">
          <h2>{r.visitTitle}</h2>
          <ul className="sh-list">
            {hospitals.map((h) => (
              <li key={h.id}>{h.name}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="sh-slip">
        <div className="sh-slip-title">{r.slipTitle}</div>
        <div className="sh-slip-label">{r.slipCode}</div>
        <div className="sh-slip-code">{slipCode}</div>
        <hr />
        <p>{r.slipNote}</p>
        <p>{r.notDiagnosis}</p>
      </div>

      <div className="sh-stack">
        {res.completed && (
          <button className="sh-btn" onClick={() => window.open(slipUrl(res.session_id, lang), '_blank')}>
            {r.slipDownload}
          </button>
        )}

        {res.coercion && (
          <button
            className="sh-btn ghost"
            onClick={() =>
              navigate('/alert', {
                state: {
                  answers: state?.answers ?? {},
                  hospitalId: state?.hospitalId ?? null,
                  slipCode,
                  sessionId: res.session_id,
                },
              })
            }
          >
            {r.helpBtn}
          </button>
        )}

        <button className="sh-btn ghost" onClick={() => navigate('/language', { replace: true })}>
          {r.finish}
        </button>
      </div>
    </Shell>
  )
}

import { useEffect, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { RESULT_TEXT } from '../data/resultText'
import { speak } from '../speak'
import Shell from '../components/Shell'

export default function Result() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const { lang } = useLanguage()
  const r = RESULT_TEXT[lang]
  const answers = state?.answers
  const hospitalId = state?.hospitalId ?? null

  // Demo only: the real slip code will come from the backend.
  const [slipCode] = useState(
       () => state?.slipCode ?? 'ZR-' + Math.random().toString(36).slice(2, 6).toUpperCase()
  )

  const asks = [r.ask1, r.ask2, r.ask3, r.ask4, r.ask5]
  const spoken = [r.headline, r.body, r.askTitle, ...asks, r.visitTitle, r.hospA, r.hospB, r.notDiagnosis].join('. ')

  useEffect(() => () => window.speechSynthesis?.cancel(), [])

  if (!answers) return <Navigate to="/language" replace />

  return (
    <Shell title={r.headline} step="result" guide={r.guide}>
      <div className="sh-card">
        <p>{r.body}</p>
        <button className="sh-listen" onClick={() => speak(spoken, lang)}>
          <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 5L6 9H3v6h3l5 4zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
          </svg>
          {r.listenAll}
        </button>
      </div>

      <div className="sh-card">
        <h2>{r.askTitle}</h2>
        <ol className="sh-list">
          {asks.map((a, i) => (
            <li key={i}>{a}</li>
          ))}
        </ol>
      </div>

      <div className="sh-card">
        <h2>{r.visitTitle}</h2>
        <ul className="sh-list">
          <li>{r.hospA}</li>
          <li>{r.hospB}</li>
        </ul>
      </div>

      <div className="sh-slip">
        <div className="sh-slip-title">{r.slipTitle}</div>
        <div className="sh-slip-label">{r.slipCode}</div>
        <div className="sh-slip-code">{slipCode}</div>
        <hr />
        <p>{r.slipNote}</p>
        <p>{r.notDiagnosis}</p>
      </div>

      <div className="sh-stack">
        {/* Demo: prints the slip. Later this will download GET /sessions/{id}/slip.pdf */}
        <button className="sh-btn" onClick={() => window.print()}>
          {r.slipDownload}
        </button>

        {answers.pressure === 'yes' && (
          <button
            className="sh-btn ghost"
           onClick={() => navigate('/alert', { state: { answers, hospitalId, slipCode } })}
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
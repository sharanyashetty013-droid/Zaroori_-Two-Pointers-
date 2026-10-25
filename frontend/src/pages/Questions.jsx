import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../LanguageContext'
import { useT } from '../i18n'
import { UI } from '../data/questions'
import { getQuestions, startSession, submitAnswers } from '../api'
import { speak } from '../speak'
import Shell from '../components/Shell'

const MESSAGES = {
  load: 'Could not load the questions. Check the connection and try again.',
  login: 'Your ASHA login has expired. Please log in again.',
  limit: 'Daily case limit reached for this ASHA key. Ask your coordinator.',
  send: 'Could not save the answers. Please tap your last answer again.',
}

export default function Questions() {
  const { lang } = useLanguage()
  const t = useT()
  const navigate = useNavigate()
  const { state } = useLocation()
  const hospitalId = state?.hospitalId ?? null
  const [questions, setQuestions] = useState(null)
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const session = useRef(null) // one session per visit to this page

  useEffect(() => {
    let off = false
    setQuestions(null)
    setError('')
    getQuestions(lang)
      .then((qs) => !off && setQuestions(qs))
      .catch(() => !off && setError('load'))
    return () => {
      off = true
    }
  }, [lang])

  const q = questions?.[index]

  useEffect(() => {
    if (!q) return
    speak(q.text + '. ' + q.options.map((o) => o.label).join('. ') + '.', lang)
    return () => window.speechSynthesis?.cancel()
  }, [q, lang])

  function getSessionId() {
    if (!session.current) {
      const n = Number(hospitalId)
      const hid = hospitalId !== null && hospitalId !== '' && Number.isFinite(n) ? n : null
      session.current = startSession(lang, hid)
        .then((r) => r.session_id)
        .catch((e) => {
          session.current = null
          throw e
        })
    }
    return session.current
  }

  async function finish(all) {
    setBusy(true)
    setError('')
    try {
      const sid = await getSessionId()
      const result = await submitAnswers(sid, all)
      navigate('/result', { state: { result, answers: all, hospitalId } })
    } catch (e) {
      setError(e.status === 401 ? 'login' : e.status === 429 ? 'limit' : 'send')
    }
    setBusy(false)
  }

  function choose(value) {
    if (busy) return
    const next = { ...answers, [q.id]: value }
    setAnswers(next)
    if (index < questions.length - 1) setIndex(index + 1)
    else finish(next)
  }

  function goBack() {
    if (index > 0) setIndex(index - 1)
    else navigate('/hospital')
  }

  if (!q) {
    return (
      <Shell title="…" step="questions">
        <div className="sh-card">
          <p>{error ? MESSAGES.load : '…'}</p>
        </div>
        <button className="sh-btn ghost" onClick={() => navigate('/hospital')}>
          &#8592; {UI.back[lang]}
        </button>
      </Shell>
    )
  }

  const spoken = q.text + '. ' + q.options.map((o) => o.label).join('. ') + '.'
  const g = t('guideQ_' + q.id)
  const guide = g && !String(g).startsWith('guideQ_') ? g : undefined

  return (
    <Shell title={q.text} step="questions" guide={guide}>
      <div className="sh-card">
        <div className="sh-mob-meta">
          {t('question')} {index + 1} / {questions.length}
        </div>
        <div className="sh-mob-bar" aria-hidden="true">
          {questions.map((x, i) => (
            <div key={x.id} className={'sh-seg' + (i < index ? ' done' : '') + (i === index ? ' on' : '')} />
          ))}
        </div>
        <button className="sh-listen" onClick={() => speak(spoken, lang)}>
          <svg className="sh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M11 5L6 9H3v6h3l5 4zM15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13" />
          </svg>
          {UI.listen[lang]}
        </button>
      </div>

      {error && (
        <div className="sh-card">
          <p>{MESSAGES[error]}</p>
        </div>
      )}

      <div className="sh-rows">
        {q.options.map((o) => (
          <button
            key={o.value}
            disabled={busy}
            className={'sh-row' + (answers[q.id] === o.value ? ' sel' : '')}
            onClick={() => choose(o.value)}
          >
            <span>{o.label}</span>
          </button>
        ))}
      </div>

      <button className="sh-btn ghost" onClick={goBack}>
        &#8592; {UI.back[lang]}
      </button>
    </Shell>
  )
}
